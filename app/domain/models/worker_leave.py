from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkerLeave(Base):
    __tablename__ = "worker_leaves"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # quem se afastou
    clt_contract_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("clt_contracts.id"),
        nullable=False,
    )

    # qual tipo de afastamento — FK para leave_type_rules.leave_type
    # affects_salary e affects_fgts são consultados em leave_type_rules
    # no momento do processamento — não ficam aqui (ADR-05)
    leave_type: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("leave_type_rules.leave_type"),
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    # NULL = data de fim indeterminada (ex: auxílio-doença INSS)
    # preenchido = afastamento com prazo conhecido (ex: férias)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        # banco garante integridade de datas
        # sobreposição de períodos prevenida na camada de serviço (ADR-05)
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_worker_leaves_valid_period",
        ),
    )


