from datetime import datetime, timezone
from uuid import UUID as UUIDType
from uuid import uuid4

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3))
    customer_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True))
    product_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True))
    quantity: Mapped[int] = mapped_column(Integer)
