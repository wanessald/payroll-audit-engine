ADR-05: Modelagem de afastamentos e licenças — worker_leaves e leave_type_rules

Status: parcialmente revisado pelo ADR-08. A chave estrangeira de
worker_leaves para leave_type_rules.leave_type foi substituída por
leave_type_id apontando para leave_types.

Contexto: Empregados CLT podem ter suspensões temporárias ou permanentes
do vínculo ativo: férias, afastamento por doença, licença
maternidade/paternidade, licença médica e aposentadoria.
Cada tipo tem impacto diferente sobre salário e FGTS.
Usar apenas termination_date não cobre suspensões temporárias —
o contrato permanece ativo mas a folha normal é suspensa.
affects_salary e affects_fgts variam por tipo de afastamento
e são definidos por lei — não pelo usuário que cadastra
o afastamento.

Decisão: Criar duas tabelas separadas:

leave_type_rules → tabela de regras por tipo de afastamento
define o comportamento de cada tipo:
impacto em salário, FGTS e previsibilidade
de data de fim. Populada via seed script
idempotente — não via API nem migration com dados.
Segue padrão SCD2: atualizações geram novo
registro com valid_from — nunca UPDATE no
registro existente.

worker_leaves → registra cada evento de afastamento do empregado
referencia leave_type_rules via leave_type
NÃO possui affects_salary nem affects_fgts —
esses valores são consultados em leave_type_rules
no momento do processamento da folha

termination_date permanece em clt_contracts apenas para
encerramento definitivo do vínculo.

O gate de processamento da folha verifica dois critérios: 1. termination_date IS NULL (contrato ativo) 2. nenhum worker_leave ativo com leave_type_rules.affects_salary
= True na competência sendo processada

Campos de leave_type_rules:
id
leave_type → String — identificador do tipo de afastamento
affects_salary → Boolean — folha normal é suspensa?
affects_fgts → Boolean — FGTS continua sendo recolhido?
has_fixed_end_date → Boolean — afastamento sempre tem data de fim?
valid_from → Date — início da vigência da regra
valid_until → Date nullable — fim da vigência (null = vigente)
jurisdiction → String(5), default 'BR' — ADR-01

Campos de worker_leaves:
id
clt_contract_id → FK para clt_contracts
leave_type → FK para leave_type_rules.leave_type
start_date → Date — início do afastamento
end_date → Date nullable — fim previsto
null = indeterminado (ex: auxílio-doença INSS)
created_at → DateTime(timezone=True)

Regras de negócio garantidas pela aplicação:

- sobreposição de afastamentos prevenida via query de verificação
  antes do INSERT (dois afastamentos não podem ter períodos
  sobrepostos para o mesmo contrato)
- precedência cronológica: afastamento iniciado durante férias
  só produz efeito após o término das férias

Regras garantidas pelo banco:

- end_date >= start_date quando end_date não é NULL (CHECK constraint)

Security e Privacy by Design:

- leave_type como FK controlada — sem tipos arbitrários
- dados de afastamento são sensíveis (saúde, maternidade) —
  acesso restrito por role; log de acesso na audit_trail
- toda criação ou alteração registrada na audit_trail com
  before/after state e identificação de quem operou

Seed script:

- leave_type_rules populada via seed script idempotente
- migration cria estrutura; seed popula dados iniciais
- seed verifica existência antes de inserir (sem duplicidade)
- referência: scripts/seed_leave_type_rules.py (a criar)

Valores iniciais do seed (jurisdição BR):
FERIAS | salary: True | fgts: True | fixed_end: True
AFASTAMENTO_INSS | salary: False | fgts: False | fixed_end: False
ACIDENTE_TRABALHO | salary: False | fgts: True | fixed_end: False
LICENCA_MATERNIDADE | salary: False | fgts: True | fixed_end: True
LICENCA_PATERNIDADE | salary: False | fgts: True | fixed_end: True
LICENCA_MEDICA | salary: False | fgts: False | fixed_end: True
APOSENTADORIA | salary: False | fgts: False | fixed_end: False
LICENCA_GALA | salary: False | fgts: True | fixed_end: True
LICENCA_NOJO | salary: False | fgts: True | fixed_end: True
MANDATO_SINDICAL | salary: False | fgts: True | fixed_end: False

Decisão técnica complementar:
Unicidade de regra ativa por tipo: índice parcial PostgreSQL
CREATE UNIQUE INDEX uq_leave_type_rules_active
ON leave_type_rules (leave_type)
WHERE valid_until IS NULL
Garante: no máximo uma regra ativa por leave_type
Atualização de regra: UPDATE (preenche valid_until) +
INSERT (nova regra com valid_from) na mesma transação (SCD2)

Hipótese a validar:
O índice parcial previne inserção de duas regras ativas do mesmo
leave_type simultaneamente.
Validação pendente: TASK-TESTE-02 — teste de integração que tenta
inserir dois registros de FERIAS com valid_until = NULL e verifica
rejeição com UniqueViolation.

Limitação conhecida:
Índice parcial específico do PostgreSQL — mesma limitação do ADR-06.
