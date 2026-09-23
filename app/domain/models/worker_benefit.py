from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkerBenefit(Base):
    __tablename__ = "worker_benefits"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    clt_contract_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("clt_contracts.id"),
        nullable=False,
    )

    benefit_type: Mapped[str] = mapped_column(String(50), nullable=False)

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False,
    )

    # VT: desconto máximo de 6% do salário base (0.06) — CLT art. 4º-A
    # a regra específica do VT é validada na camada de serviço
    # esta constraint garante apenas que nenhum desconto ultrapassa 100%
    discount_rate: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=4),
        nullable=False,
        default=Decimal("0.0"),
    )

    valid_from: Mapped[date] = mapped_column(Date, nullable=False)

    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)

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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_worker_benefits_amount_positive",
        ),
        CheckConstraint(
            "discount_rate >= 0 AND discount_rate <= 1",
            name="ck_worker_benefits_discount_rate_range",
        ),
        CheckConstraint(
            "valid_until IS NULL OR valid_until >= valid_from",
            name="ck_worker_benefits_valid_period",
        ),

        Index(
            "uq_worker_benefits_active_type",
            "clt_contract_id",
            "benefit_type",
            unique=True,
            postgresql_where="valid_until IS NULL",
        ),
    )