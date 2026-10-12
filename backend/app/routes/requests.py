from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.models.user import User
from app.models.account import Account
from app.models.request import Request, RequestStatus
from app.utils.dependencies import get_db, get_current_user
from app.services.gmail_service import send_gmail_email

router = APIRouter(prefix="/api/requests", tags=["Requests"])

class RequestCreatePayload(BaseModel):
    account_ids: List[uuid.UUID]

class StatusUpdatePayload(BaseModel):
    status: str
    notes: Optional[str] = None

def generate_email_body(user: User, platform_name: str, platform_domain: str) -> str:
    bugunun_tarihi = datetime.utcnow().strftime("%d.%m.%Y")
    return (
        f"Sayın {platform_name} Yetkilileri,\n\n"
        f"{platform_name} ({platform_domain}) platformunda kayıtlı olan hesabıma ait "
        f"tüm kişisel verilerimin KVKK Madde 11 ve GDPR Madde 17 kapsamında kalıcı "
        f"olarak silinmesini talep ediyorum.\n\n"
        f"Hesap bilgilerim:\n"
        f"- E-posta adresi: {user.email}\n"
        f"- Ad Soyad: {user.display_name}\n\n"
        f"Bu talep kapsamında aşağıdakilerin yapılmasını istiyorum:\n"
        f"1. Hesabımın kalıcı olarak kapatılması\n"
        f"2. Kişisel verilerimin tüm sistemlerden silinmesi\n"
        f"3. Üçüncü taraflarla paylaşılan verilerimin silinmesinin sağlanması\n"
        f"4. Silme işleminin tamamlandığına dair yazılı bildirim yapılması\n\n"
        f"Yasal düzenleme gereği 30 gün içinde yanıt bekliyorum.\n\n"
        f"Saygılarımla,\n"
        f"{user.display_name}\n"
        f"{user.email}\n"
        f"Tarih: {bugunun_tarihi}"
    )

@router.post("/")
async def create_requests(
    payload: RequestCreatePayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    created_requests = []
    
    for acc_id in payload.account_ids:
        result = await db.execute(
            select(Account).where(Account.id == acc_id, Account.user_id == current_user.id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            continue
            
        res_req = await db.execute(
            select(Request).where(Request.account_id == acc_id, Request.user_id == current_user.id)
        )
        existing_req = res_req.scalar_one_or_none()
        
        if existing_req:
            existing_req.email_subject = f"Kişisel Veri Silme Talebi - {current_user.email}"
            existing_req.email_body = generate_email_body(current_user, account.platform_name, account.platform_domain)
            created_requests.append(existing_req)
            continue
            
        dpo_email = f"privacy@{account.platform_domain}"
        deadline_date = datetime.utcnow() + timedelta(days=30)
        email_subject = f"Kişisel Veri Silme Talebi - {current_user.email}"
        email_body = generate_email_body(current_user, account.platform_name, account.platform_domain)
        
        new_req = Request(
            user_id=current_user.id,
            account_id=acc_id,
            status=RequestStatus.PENDING,
            deadline=deadline_date,
            email_subject=email_subject,
            email_body=email_body,
            platform_dpo_email=dpo_email,
            notes=""
        )
        
        db.add(new_req)
        created_requests.append(new_req)
        
    await db.commit()
    return created_requests

@router.get("/")
async def get_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Request, Account)
        .join(Account, Request.account_id == Account.id)
        .where(Request.user_id == current_user.id)
        .order_by(Request.created_at.desc())
    )
    
    rows = result.all()
    requests_data = []
    
    for request, account in rows:
        requests_data.append({
            "id": str(request.id),
            "user_id": str(request.user_id),
            "account_id": str(request.account_id),
            "platform_name": account.platform_name,
            "platform_domain": account.platform_domain,
            "platform_category": account.platform_category,
            "status": request.status.value,
            "sent_at": request.sent_at.isoformat() if request.sent_at else None,
            "deadline": request.deadline.isoformat() if request.deadline else None,
            "response_received_at": request.response_received_at.isoformat() if request.response_received_at else None,
            "email_subject": request.email_subject,
            "email_body": request.email_body,
            "platform_dpo_email": request.platform_dpo_email,
            "notes": request.notes,
            "created_at": request.created_at.isoformat(),
            "updated_at": request.updated_at.isoformat()
        })
        
    return requests_data

@router.put("/{id}/status")
async def update_request_status(
    id: uuid.UUID,
    payload: StatusUpdatePayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Request).where(Request.id == id, Request.user_id == current_user.id)
    )
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(status_code=404, detail="Talep bulunamadı.")
        
    try:
        new_status = RequestStatus(payload.status.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz durum değeri.")
        
    request.status = new_status
    if new_status == RequestStatus.SENT and not request.sent_at:
        request.sent_at = datetime.utcnow()
        request.deadline = datetime.utcnow() + timedelta(days=30)
    elif new_status == RequestStatus.COMPLETED or new_status == RequestStatus.REJECTED:
        request.response_received_at = datetime.utcnow()
        
    if payload.notes is not None:
        request.notes = payload.notes
        
    await db.commit()
    return request

@router.get("/{id}/email")
async def get_request_email(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Request).where(Request.id == id, Request.user_id == current_user.id)
    )
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(status_code=404, detail="Talep bulunamadı.")
        
    return {
        "subject": request.email_subject,
        "body": request.email_body,
        "dpo_email": request.platform_dpo_email
    }

class SendEmailPayload(BaseModel):
    dpo_email: str
    subject: str
    body: str

@router.post("/{id}/send")
async def send_request_email(
    id: uuid.UUID,
    payload: SendEmailPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gmail API üzerinden veri silme talebini gerçekten gönderir."""
    result = await db.execute(
        select(Request).where(Request.id == id, Request.user_id == current_user.id)
    )
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(status_code=404, detail="Talep bulunamadı.")
    
    if request.status not in [RequestStatus.PENDING]:
        raise HTTPException(status_code=400, detail="Bu talep zaten gönderilmiş.")
    
    try:
        await send_gmail_email(
            user=current_user,
            to_email=payload.dpo_email,
            subject=payload.subject,
            body=payload.body,
            db=db,          # ← token yenilenirse DB'ye kaydedilir
        )
    except RuntimeError as e:
        # Token yenileme başarısız — kullanıcıya net hata mesajı
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
    except Exception as e:
        print(f"Gmail send error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"E-posta gönderilemedi: {str(e)}",
        )
    # Başarıyla gönderildi — durumu güncelle
    request.status = RequestStatus.SENT
    request.sent_at = datetime.utcnow()
    request.deadline = datetime.utcnow() + timedelta(days=30)
    request.platform_dpo_email = payload.dpo_email  # Kullanıcı değiştirmiş olabilir
    await db.commit()
    
    return {"status": "sent", "message": "E-posta başarıyla gönderildi.", "sent_at": request.sent_at.isoformat()}
