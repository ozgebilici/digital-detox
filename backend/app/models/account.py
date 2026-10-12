import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_name: Mapped[str] = mapped_column(String(100), nullable=False)
    platform_domain: Mapped[str] = mapped_column(String(100), nullable=False)
    platform_category: Mapped[str] = mapped_column(String(50), nullable=False)
    account_email: Mapped[str] = mapped_column(String(255), nullable=True)
    email_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
