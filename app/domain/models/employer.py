import uuid6
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Employer(Base):
    __tablename__ = "employers"

    # identificador interno — nunca exposto na API
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # identificador externo — exposto na API e nos relatórios de auditoria
    public_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid6.uuid7()),
    )

    cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[str] = mapped_column(String(255), nullable=True)

    # metadados de rastreabilidade
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