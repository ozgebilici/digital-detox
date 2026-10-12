from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid

from app.models.user import User
from app.models.account import Account
from app.utils.dependencies import get_db, get_current_user
from app.services.analyzer import analyze_user_emails

router = APIRouter(prefix="/api/scan", tags=["Scanning"])

@router.post("/start")
async def start_scan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.google_access_token_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google hesabı bağlı değil veya oturum kapatılmış."
        )
    try:
        scanned_count, detected_count = await analyze_user_emails(current_user, db)
        return {
            "status": "success",
            "message": "Tarama başarıyla tamamlandı.",
            "scanned_emails_count": scanned_count,
            "detected_accounts_count": detected_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"E-postalar taranırken hata oluştu: {str(e)}"
        )

@router.get("/accounts")
async def get_detected_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Account)
        .where(Account.user_id == current_user.id)
        .order_by(Account.confidence_score.desc(), Account.platform_name.asc())
    )
    accounts = result.scalars().all()
    return accounts

@router.delete("/accounts/{id}")
async def delete_account(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Account).where(Account.id == id, Account.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=404, detail="Hesap bulunamadı.")
        
    await db.delete(account)
    await db.commit()
    return {"status": "success", "message": "Hesap başarıyla listeden kaldırıldı."}
