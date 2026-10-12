import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=True)
    profile_picture: Mapped[str] = mapped_column(String(500), nullable=True)
    google_access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=True)
    google_refresh_token_encrypted: Mapped[str] = mapped_column(Text, nullable=True)
    google_token_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_scan_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
