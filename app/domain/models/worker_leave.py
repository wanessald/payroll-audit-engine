from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey
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

    # qual tipo de afastamento, do catálogo (ADR-08)
    # a regra (affects_salary, affects_fgts) é buscada em leave_type_rules
    # pela data da folha, não fica guardada aqui
    leave_type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("leave_types.id"),
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


