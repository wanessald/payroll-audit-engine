from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Numeric,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AliquotRate(Base):
    __tablename__ = "aliquot_rates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # qual imposto: 'INSS' | 'IRRF' | 'FGTS' (garantido por CheckConstraint)
    rate_type: Mapped[str] = mapped_column(String(10), nullable=False)

    # faixa salarial: (salary_from, salary_until]
    # o número de baixo NÃO está incluído, o de cima está (ADR-07)
    # salary_until NULL = sem teto (ex: FGTS)
    salary_from: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    salary_until: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # alíquota como decimal: 0.0750 = 7,5%
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)

    # parcela a deduzir em R$ (IRRF; INSS se usar o método da dedução)
    deduction_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    # SCD2: NULL em valid_until = tabela vigente (ADR-05)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)

    # internacionalização (ADR-01)
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
        # regras de UMA linha isolada
        CheckConstraint(
            "rate_type IN ('INSS', 'IRRF', 'FGTS')",
            name="ck_aliquot_rates_rate_type",
        ),
        CheckConstraint(
            "salary_from >= 0",
            name="ck_aliquot_rates_salary_from_non_negative",
        ),
        CheckConstraint(
            "salary_until IS NULL OR salary_until > salary_from",
            name="ck_aliquot_rates_salary_range",
        ),
        CheckConstraint(
            "rate >= 0 AND rate <= 1",
            name="ck_aliquot_rates_rate_range",
        ),
        CheckConstraint(
            "deduction_amount >= 0",
            name="ck_aliquot_rates_deduction_non_negative",
        ),
        CheckConstraint(
            "valid_until IS NULL OR valid_until >= valid_from",
            name="ck_aliquot_rates_valid_period",
        ),
        # regra ENTRE linhas: recusa faixas sobrepostas (ADR-07)
        # "=" significa igual; "&&" significa sobrepõe
        # limitação: específico do PostgreSQL, exige a extensão btree_gist
        ExcludeConstraint(
            ("rate_type", "="),
            ("jurisdiction", "="),
            (text("numrange(salary_from, salary_until, '(]')"), "&&"),
            (text("daterange(valid_from, valid_until, '[]')"), "&&"),
            using="gist",
            name="ex_aliquot_rates_no_overlap",
        ),
    )