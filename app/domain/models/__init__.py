# Importar todos os modelos aqui registra todas as tabelas em Base.metadata.
# O Alembic só enxerga as tabelas que foram importadas.
from app.domain.models.employer import Employer
from app.domain.models.worker import Worker
from app.domain.models.clt_contract import CLTContract
from app.domain.models.worker_benefit import WorkerBenefit
from app.domain.models.leave_type_rule import LeaveTypeRule
from app.domain.models.worker_leave import WorkerLeave
from app.domain.models.aliquot_rate import AliquotRate
from app.domain.models.leave_type import LeaveType

__all__ = [
    "Employer",
    "Worker",
    "CLTContract",
    "WorkerBenefit",
    "LeaveTypeRule",
    "WorkerLeave",
    "AliquotRate",
    "LeaveType"
]