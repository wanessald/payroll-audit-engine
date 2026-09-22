from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.worker import Worker


class CLTContract(Worker):
    __tablename__ = "clt_contracts"

    # FK para workers.id — chave da herança joined table
    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("workers.id"),
        primary_key=True,
    )

    position: Mapped[str] = mapped_column(String(255), nullable=False)

    admission_date: Mapped[date] = mapped_column(Date, nullable=False)

    # NULL = contrato ativo | preenchido = contrato encerrado
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    base_salary: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False,
    )


    __mapper_args__ = {
        "polymorphic_identity": "CLT",
    }