import os
import json
import re
from datetime import datetime
from sqlalchemy.future import select
from app.models.account import Account
from app.services.gmail_service import fetch_gmail_emails

# Load platforms.json
PLATFORMS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platforms.json")

def load_platforms():
    try:
        with open(PLATFORMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

platforms_db = load_platforms()

GMAIL_QUERY = (
    "subject:(welcome OR verify OR confirmed OR register OR account OR "
    "subscription OR hosgeldiniz OR kayit OR uyelik OR aktivasyon OR "
    "activate OR signup OR joined OR onayla OR dogrula OR merhaba OR "
    "aramiza OR hesabiniz OR sifreni)"
)

KEYWORDS = [
    "welcome", "verify", "confirmed", "activate", "account created", "registration",
    "subscription", "sign up", "signed up", "joined", "get started", "complete your",
    "confirm your", "new account", "activate your", "verify your",
    "hosgeldiniz", "kayit", "uyelik", "aktivasyon", "hesabiniz", "onayla",
    "dogrula", "aramiza katildiniz", "hesap olusturuldu", "merhaba"
]

EXCLUDED_DOMAINS = {
    "gmail.com", "googlemail.com", "google.com", "yahoo.com", "ymail.com",
    "outlook.com", "hotmail.com", "live.com", "msn.com", "icloud.com",
    "me.com", "mac.com", "aol.com", "zoho.com", "proton.me", "protonmail.com",
    "mail.com", "gmx.com", "gmx.net", "web.de", "yandex.com", "yandex.ru",
    "mail.ru", "list.ru", "bk.ru", "inbox.ru", "mynet.com", "windowslive.com"
}

def extract_domain(from_value: str) -> str:
    match = re.search(r'<([^>]+)>', from_value)
    email = match.group(1) if match else from_value
    
    if "@" in email:
        domain = email.split("@")[-1].strip().lower()
        parts = domain.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return domain
    return ""

async def analyze_user_emails(user, db):
    emails = await fetch_gmail_emails(user, query=GMAIL_QUERY, max_results=1000)
    
    scanned_count = len(emails)
    detected_accounts = {}
    
    for email in emails:
        subject = email.get("subject", "").lower()
        from_val = email.get("from", "")
        
        has_keyword = any(kw in subject for kw in KEYWORDS)
        if not has_keyword:
            continue
            
        domain = extract_domain(from_val)
        if not domain:
            continue
            
        platform_info = platforms_db.get(domain)
        if not platform_info and domain not in EXCLUDED_DOMAINS:
            main_part = domain.split(".")[0]
            platform_info = {
                "name": main_part.capitalize(),
                "category": "other"
            }
            
        if platform_info:
            if domain in detected_accounts:
                detected_accounts[domain]["email_count"] += 1
            else:
                match = re.search(r'[\w\.-]+@[\w\.-]+', from_val)
                account_email = match.group(0) if match else ""
                
                detected_accounts[domain] = {
                    "platform_name": platform_info["name"],
                    "platform_domain": domain,
                    "platform_category": platform_info["category"],
                    "account_email": account_email,
                    "email_count": 1,
                    "detected_at": datetime.utcnow()
                }

    saved_accounts = []
    for domain, data in detected_accounts.items():
        data["confidence_score"] = min(1.0, data["email_count"] / 3.0)
        
        result = await db.execute(
            select(Account).where(
                Account.user_id == user.id,
                Account.platform_domain == domain
            )
        )
        existing_acc = result.scalar_one_or_none()
        
        if existing_acc:
            existing_acc.email_count = data["email_count"]
            existing_acc.confidence_score = data["confidence_score"]
            existing_acc.account_email = data["account_email"] or existing_acc.account_email
            saved_accounts.append(existing_acc)
        else:
            new_acc = Account(
                user_id=user.id,
                platform_name=data["platform_name"],
                platform_domain=data["platform_domain"],
                platform_category=data["platform_category"],
                account_email=data["account_email"],
                email_count=data["email_count"],
                confidence_score=data["confidence_score"],
                is_confirmed=True,
                detected_at=data["detected_at"]
            )
            db.add(new_acc)
            saved_accounts.append(new_acc)
            
    user.last_scan_at = datetime.utcnow()
    await db.commit()
    
    return scanned_count, len(saved_accounts)
