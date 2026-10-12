from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import httpx
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

from app.config import settings
from app.models.user import User
from app.utils.security import encrypt_token, decrypt_token, create_access_token, create_refresh_token, decode_token
from app.utils.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class RefreshRequest(BaseModel):
    refresh_token: str

@router.get("/google")
def login_google():
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        "response_type=code&"
        "scope=openid%20email%20profile%20https://www.googleapis.com/auth/gmail.readonly%20https://www.googleapis.com/auth/gmail.send&"
        "access_type=offline&"
        "prompt=consent"
    )
    return RedirectResponse(url=auth_url, status_code=302)

@router.get("/callback")
async def google_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Google hata döndürdüyse frontend'e yönlendir
    if error or not code:
        error_msg = error or "authorization_code_missing"
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/?auth_error={error_msg}",
            status_code=302
        )

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            if token_response.status_code != 200:
                print(f"Token exchange failed: {token_response.text}")
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/?auth_error=token_exchange_failed",
                    status_code=302
                )

            tokens = token_response.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            expires_in = tokens.get("expires_in", 3600)

            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            userinfo_response = await client.get(userinfo_url, headers=headers)
            if userinfo_response.status_code != 200:
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/?auth_error=userinfo_failed",
                    status_code=302
                )

            user_info = userinfo_response.json()
            email = user_info.get("email")
            name = user_info.get("name", "")
            picture = user_info.get("picture", "")

        if not email:
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/?auth_error=no_email",
                status_code=302
            )

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        access_encrypted = encrypt_token(access_token)
        refresh_encrypted = encrypt_token(refresh_token) if refresh_token else None

        if user:
            user.display_name = name
            user.profile_picture = picture
            user.google_access_token_encrypted = access_encrypted
            if refresh_token:
                user.google_refresh_token_encrypted = refresh_encrypted
            user.google_token_expires_at = expires_at
        else:
            user = User(
                email=email,
                display_name=name,
                profile_picture=picture,
                google_access_token_encrypted=access_encrypted,
                google_refresh_token_encrypted=refresh_encrypted or "",
                google_token_expires_at=expires_at
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        user_id_str = str(user.id)
        sys_access_token = create_access_token({"sub": user_id_str})
        sys_refresh_token = create_refresh_token({"sub": user_id_str})

        redirect_url = f"{settings.FRONTEND_URL}/?access_token={sys_access_token}&refresh_token={sys_refresh_token}"
        return RedirectResponse(url=redirect_url, status_code=302)

    except Exception as e:
        print(f"OAuth callback error: {e}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/?auth_error=internal_error",
            status_code=302
        )

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "display_name": current_user.display_name,
        "profile_picture": current_user.profile_picture,
        "last_scan_at": current_user.last_scan_at.isoformat() if current_user.last_scan_at else None
    }

@router.post("/refresh")
async def refresh_session(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Geçersiz refresh token")
        
    user_id_str = decoded.get("sub")
    result = await db.execute(select(User).where(User.id == user_id_str))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
        
    new_access = create_access_token({"sub": str(user.id)})
    return {"access_token": new_access}

@router.post("/revoke")
async def revoke_session(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current_user.google_access_token_encrypted = ""
    current_user.google_refresh_token_encrypted = ""
    await db.commit()
    return {"status": "ok", "message": "Oturum başarıyla kapatıldı ve tokenlar silindi."}
