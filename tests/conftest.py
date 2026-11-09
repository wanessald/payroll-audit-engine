import os

import pytest

# DEVE vir antes de qualquer import de app.*: o settings é lido uma única
# vez, no import. Variável de ambiente tem prioridade sobre o .env.
os.environ["POSTGRES_DB"] = "payroll_audit_test"

from app.core.database import engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def garantir_banco_de_teste():
    """Trava de segurança: nenhum teste roda fora de um banco de teste."""
    nome_do_banco = engine.url.database
    if not nome_do_banco.endswith("_test"):
        pytest.exit(
            f"Abortando: os testes apontam para '{nome_do_banco}', "
            "que não é um banco de teste.",
            returncode=1,
        )