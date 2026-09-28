from app.core.database import Base
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime, timezone

class LeaveTypeRule(Base):
    __tablename__ = "leave_type_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    leave_type: Mapped[str] = mapped_column(String(50), nullable=False)

    affects_salary: Mapped[bool] = mapped_column(Boolean, nullable=False)
    affects_fgts: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # True = afastamento sempre tem data de fim conhecida (ex: férias)
    # False = data de fim indeterminada (ex: auxílio-doença INSS)
    has_fixed_end_date: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # SCD2 — ADR-05
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)

# internacionalização — ADR-01
jurisdiction: Mapped[str] = mapped_column(
    String(5),
    nullable=False,
    default="BR",
)

created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda: datetime.now(timezone.utc),
)

__tablename__ = (
    # regra ativa só pode existir uma por leave_type (ADR-05)
    CheckConstraint(
        "valid_until IS NULL OR valid_until >= valid_from",
        name="ck_leave_type_rules_valid_period",
    ),
    # índice parcial — unicidade de regra ativa por tipo
    # limitação: específico do PostgreSQL (ADR-05)
    Index(
        "uq_leave_type_rules_active",
        "leave_type",
        "jurisdiction",
        unique=True,
        postgresql_where="valid_until IS NULL",
    ),
)