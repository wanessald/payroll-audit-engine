ADR-06: Modelagem de benefícios e direitos CLT — tabela worker_benefits

Contexto: Empregados CLT têm direito a benefícios variados: vale transporte,
vale alimentação, vale refeição, plano de saúde, auxílio
home office, entre outros.
Modelar cada benefício como coluna booleana em clt_contracts
exige migration a cada novo tipo de benefício, não captura
valores nem vigência, e não suporta histórico de alterações.

Decisão: Criar tabela worker_benefits separada de clt_contracts.
Cada benefício é um registro com tipo, valor, percentual de
desconto do empregado e período de vigência.
Adicionar um novo tipo de benefício = inserir linhas,
não alterar estrutura da tabela.

Campos:
id
clt_contract_id → FK para clt_contracts
benefit_type → 'VALE_TRANSPORTE' | 'VALE_ALIMENTACAO'
'VALE_REFEICAO' | 'PLANO_SAUDE'
'AUXILIO_HOME_OFFICE' | ...
amount → Decimal — valor mensal do benefício
discount_rate → Decimal — percentual descontado do empregado: 0.0 a 1.0
constraint: 0 <= discount_rate <= 1 (banco)
regra específica do VT: máximo 6% do salário base (0.06)
validada na camada de serviço — não como constraint
genérica, pois outros benefícios podem ter
discount_rate diferente
valid_from → Date — início da vigência do benefício
valid_until → Date nullable — fim da vigência (null = vigente)
jurisdiction → String(5), default 'BR' — preparado para
internacionalização (ADR-01)
created_at → DateTime(timezone=True)
updated_at → DateTime(timezone=True)

Constraints obrigatórias:
amount > 0
0 <= discount_rate <= 1
valid_until >= valid_from quando valid_until não é NULL

Security e Privacy by Design:

- benefit_type como enum controlado — sem inserção de tipos
  arbitrários que bypassem regras de cálculo
- valores de benefício são dados salariais sensíveis —
  acesso restrito por role (RH vê tudo, gestor vê seu time,
  empregado vê apenas os próprios dados)
- toda criação ou alteração de benefício registrada na audit_trail
  com before/after state — nunca sobrescrita silenciosa
- log de acesso a dados de remuneração registrado na audit_trail
- discount_rate com constraint de intervalo — impede desconto
  superior a 100% do valor do benefício

Decisões técnicas complementares:

1. Unicidade de benefício ativo: índice parcial PostgreSQL
   CREATE UNIQUE INDEX uq_worker_benefits_active_type
   ON worker_benefits (clt_contract_id, benefit_type)
   WHERE valid_until IS NULL
   Garante: no máximo um registro ativo por tipo por contrato
   Preserva: histórico de registros expirados (valid_until preenchido)

2. Concorrência: UniqueViolation capturado na camada de serviço
   e traduzido para mensagem de negócio — erro de banco não
   vaza para o cliente da API

3. Reajuste de valor (padrão SCD2):
   UPDATE no registro atual (preenche valid_until) +
   INSERT do novo registro (novo valor com valid_from)
   ambos na mesma transação — atomicidade obrigatória

Hipótese a validar:
O índice parcial previne inserção de dois benefícios do mesmo tipo
ativos simultaneamente para o mesmo contrato.
Validação pendente: TASK-TESTE-01 — teste de integração que tenta
inserir dois VTs ativos para o mesmo contrato e verifica rejeição
com UniqueViolation.

Consequências:

- novos tipos de benefício não exigem migration de estrutura
- histórico de vigência preservado — auditável por competência
- valores e descontos rastreáveis por período
- preparado para múltiplas jurisdições (ADR-01)

* consulta de benefícios ativos exige filtro por valid_from/valid_until
* cálculo de folha precisa agregar benefícios ativos na competência

Limitação conhecida:
O índice parcial `WHERE valid_until IS NULL` é específico do PostgreSQL.
MySQL e SQLite não suportam índices parciais com essa sintaxe.
Portabilidade para outros bancos exige revisão desta constraint.
Decisão aceitável dado que PostgreSQL é o banco definido (ADR-01).

Referências:
CLT art. 4º-A — vale transporte →
https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm
Lei 7.418/85 — vale transporte →
https://www.planalto.gov.br/ccivil_03/leis/l7418.htm
