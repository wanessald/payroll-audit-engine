# TASK-TESTE-01 | Validar índice parcial worker_benefits
#   → inserir VT ativo para contrato X
#   → tentar inserir segundo VT ativo para mesmo contrato X
#   → banco deve rejeitar com UniqueViolation
#   → expirar o primeiro VT (preencher valid_until)
#   → inserir novo VT ativo → deve ser permitido