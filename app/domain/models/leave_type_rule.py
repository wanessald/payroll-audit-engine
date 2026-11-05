from datetime import date, datetime, timezone

from app.core.database import Base
from sqlalchemy import (BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, String)
from sqlalchemy.orm import Mapped, mapped_column

class LeaveTypeRule(Base):
    __tablename__ = "leave_type_rules"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # a qual tipo do catálogo esta regra pertence (ADR-08)
    leave_type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("leave_types.id"),
        nullable=False,
    )

    # impacto no processamento da folha — definido por lei, não pelo usuário
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

    __table_args__ = (
        # regra ativa só pode existir uma por leave_type (ADR-05)
        CheckConstraint(
            "valid_until IS NULL OR valid_until >= valid_from",
            name="ck_leave_type_rules_valid_period",
        ),
        # regra ativa por tipo e jurisdição (ADR-05 e ADR-08)
        # limitação: específico do PostgreSQL (ADR-05)
        Index(
            "uq_leave_type_rules_active",
            "leave_type_id",
            "jurisdiction",
            unique=True,
            postgresql_where="valid_until IS NULL",
        ),
)