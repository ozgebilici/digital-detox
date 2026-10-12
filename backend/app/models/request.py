import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Request(Base):
    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, values_callable=lambda x: [e.value for e in x]),
        default=RequestStatus.PENDING,
        nullable=False,
        index=True
    )
    
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    response_received_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    email_subject: Mapped[str] = mapped_column(String(500), nullable=True)
    email_body: Mapped[str] = mapped_column(Text, nullable=True)
    platform_dpo_email: Mapped[str] = mapped_column(String(255), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    account = relationship("Account")
