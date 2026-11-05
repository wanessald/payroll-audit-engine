from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LeaveType(Base):
    __tablename__ = "leave_types"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # nome estável do tipo, ex: 'FERIAS'. Cada tipo aparece uma só vez (ADR-08)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    description: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )