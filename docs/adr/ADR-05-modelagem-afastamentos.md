ADR-05: Modelagem de afastamentos e licenças — tabela worker_leaves

Contexto: Empregados CLT podem ter suspensões temporárias ou permanentes
do vínculo ativo: férias, afastamento por doença, licença
maternidade/paternidade, licença médica e aposentadoria.
Cada tipo tem impacto diferente sobre salário e FGTS.
Usar apenas termination_date não cobre suspensões temporárias —
o contrato permanece ativo mas a folha normal é suspensa.

Decisão: Criar tabela worker_leaves separada de clt_contracts.
termination_date permanece em clt_contracts apenas para
encerramento definitivo do vínculo.
worker_leaves registra todo evento de suspensão temporária
ou permanente com: tipo, período, impacto em salário e FGTS.
O gate de processamento da folha verifica os dois critérios: 1. termination_date IS NULL (contrato ativo) 2. nenhum worker_leave ativo com affects_salary = True
na competência sendo processada

Campos:
id
clt_contract_id → FK para clt_contracts
leave_type → 'FERIAS' | 'AFASTAMENTO_INSS' | 'LICENCA_MATERNIDADE'
'LICENCA_PATERNIDADE' | 'LICENCA_MEDICA' | 'APOSENTADORIA'
start_date → Date, início do afastamento
end_date → Date nullable, fim previsto (null = indeterminado)
affects_salary → Boolean, folha normal é suspensa?
affects_fgts → Boolean, FGTS continua sendo recolhido?
created_at → DateTime(timezone=True)

Security e Privacy by Design:

- leave_type como enum controlado — sem tipos arbitrários
- toda criação ou alteração de afastamento registrada na audit_trail
  com before/after state e identificação de quem operou
- dados de afastamento são sensíveis (saúde, maternidade) —
  acesso restrito por role; log de acesso registrado na audit_trail
- end_date >= start_date validado por constraint no banco

Consequências:

- gate de processamento cobre todos os cenários de suspensão
- histórico completo de afastamentos por empregado
- auditável — cada afastamento tem registro de criação e alteração

* consulta de elegibilidade de folha exige JOIN com worker_leaves
* complexidade de processamento aumenta para competências com
  afastamento parcial (ex: afastamento a partir do dia 15)

Referência:
CLT — afastamentos → https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm
Lei 8.213/91 — benefícios previdenciários → https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm
