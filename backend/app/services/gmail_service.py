import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from fastapi.concurrency import run_in_threadpool

from app.utils.security import decrypt_token, encrypt_token
from app.config import settings

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def _build_credentials(user) -> Credentials:
    """Kullanıcının şifreli tokenlarını çözerek Credentials nesnesi oluşturur."""
    access_token = decrypt_token(user.google_access_token_encrypted)
    refresh_token = decrypt_token(user.google_refresh_token_encrypted)

    return Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=GMAIL_SCOPES,
    )


def _refresh_if_needed(creds: Credentials, user) -> tuple[Credentials, bool]:
    """
    Token süresi dolmuşsa yeniler.
    Yenilenip yenilenmediğini (bool) döner — DB'ye kaydetmek için.
    """
    refreshed = False

    # google_token_expires_at varsa ve süresi yaklaştıysa zorla yenile
    expires_at = getattr(user, "google_token_expires_at", None)
    token_near_expiry = (
        expires_at is not None
        and datetime.utcnow() >= expires_at - timedelta(minutes=5)
    )

    if token_near_expiry or (creds.expired and creds.refresh_token):
        try:
            creds.refresh(GoogleRequest())
            refreshed = True
        except Exception as e:
            raise RuntimeError(
                f"Google token yenilenemedi: {e}. Lütfen çıkış yapıp tekrar giriş yapın."
            )

    return creds, refreshed


def get_gmail_client(user):
    """
    Sadece okuma işlemleri için Gmail client döner (token DB'ye kaydedilmez).
    Yeni token'ı DB'ye kaydetmek için get_gmail_client_refreshed kullanın.
    """
    creds = _build_credentials(user)
    creds, _ = _refresh_if_needed(creds, user)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


async def get_gmail_client_refreshed(user, db):
    """
    Gmail client döner; token yenilendiyse güncel değerleri DB'ye kaydeder.
    send ve scan gibi kritik işlemlerde bunu kullanın.
    """
    creds = _build_credentials(user)
    creds, refreshed = _refresh_if_needed(creds, user)

    if refreshed:
        user.google_access_token_encrypted = encrypt_token(creds.token)
        if creds.refresh_token:
            user.google_refresh_token_encrypted = encrypt_token(creds.refresh_token)
        if creds.expiry:
            user.google_token_expires_at = creds.expiry
        await db.commit()

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    return service


# ---------------------------------------------------------------------------
# Mesaj Okuma
# ---------------------------------------------------------------------------

def fetch_messages_sync(service, query: str, max_results: int = 1000):
    messages_data = []
    try:
        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])

        for msg in messages:
            try:
                m_details = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg["id"],
                        format="metadata",
                        metadataHeaders=["From", "Subject", "Date"],
                    )
                    .execute()
                )

                headers = m_details.get("payload", {}).get("headers", [])
                header_dict = {h["name"].lower(): h["value"] for h in headers}

                messages_data.append(
                    {
                        "id": msg["id"],
                        "from": header_dict.get("from", ""),
                        "subject": header_dict.get("subject", ""),
                        "date": header_dict.get("date", ""),
                    }
                )
            except Exception:
                continue
    except Exception as e:
        print(f"Gmail fetch error: {e}")
    return messages_data


async def fetch_gmail_emails(user, query: str, max_results: int = 1000):
    service = get_gmail_client(user)
    return await run_in_threadpool(fetch_messages_sync, service, query, max_results)


# ---------------------------------------------------------------------------
# E-posta Gönderme
# ---------------------------------------------------------------------------

def send_email_sync(
    service, sender_email: str, to_email: str, subject: str, body: str
) -> dict:
    """Gmail API kullanarak düz metin e-posta gönderir."""
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain", "utf-8"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    result = (
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
    )
    return result


async def send_gmail_email(user, to_email: str, subject: str, body: str, db=None) -> dict:
    """
    Kullanıcının Gmail hesabından e-posta gönderir.
    db parametresi verilirse token yenilendiğinde DB'ye kaydeder.
    """
    if db is not None:
        service = await get_gmail_client_refreshed(user, db)
    else:
        service = get_gmail_client(user)

    return await run_in_threadpool(
        send_email_sync, service, user.email, to_email, subject, body
    )