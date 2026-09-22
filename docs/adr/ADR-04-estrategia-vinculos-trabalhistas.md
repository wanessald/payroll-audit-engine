ADR-04: Estratégia de modelagem de vínculos trabalhistas
Contexto: O sistema precisa suportar múltiplos tipos de vínculo
(CLT, PJ, Freelancer, Temporário) com regras de cálculo
distintas. Cada tipo tem campos e obrigações fiscais próprias.
Decisão: Herança de tabela — modelo base `workers` com
tabelas especializadas por tipo de vínculo.
Implementação incremental:
Sprint 1 → workers + clt_contracts (único tipo implementado)
Sprints seguintes → pj_contracts, freelancer_contracts
conforme casos de uso reais surgirem.
Consequências:

- Sem retrabalho de estrutura ao adicionar novos tipos de vínculo
- Cada tabela especializada tem exatamente os campos que precisa
- Regras de cálculo isoladas por tipo — sem condicionais espalhadas

* Maior complexidade inicial de modelagem
* JOINs entre workers e clt_contracts em toda consulta de folha CLT
  Referência: SQLAlchemy joined table inheritance →
  https://docs.sqlalchemy.org/en/20/orm/inheritance.html#joined-table-inheritance
