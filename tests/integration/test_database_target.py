from app.core.database import engine


def test_engine_aponta_para_o_banco_de_teste():
    assert engine.url.database == "payroll_audit_test"