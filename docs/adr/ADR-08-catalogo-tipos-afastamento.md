ADR-08: Catálogo de tipos de afastamento (leave_types) — revisão do ADR-05

Resumo em linguagem simples:
O afastamento do empregado precisa apontar para o TIPO de afastamento
(ex: férias), e não para uma versão da regra. A regra muda com o tempo e
é escolhida pela data de cada folha. Para o banco aceitar essa ligação,
criamos uma tabela só com os tipos, onde cada tipo aparece uma vez.

Contexto: No ADR-05, worker_leaves.leave_type apontava com chave estrangeira
para leave_type_rules.leave_type. Essa coluna se repete no
histórico (SCD2): a mesma FERIAS aparece em várias versões.

Evidência (teste no PostgreSQL 16, tabelas temporárias, 04/11/2026):
Chave estrangeira para coluna com unicidade só parcial (WHERE ativo)
foi recusada com o erro: "there is no unique constraint matching
given keys for referenced table".

Requisito de negócio:
A regra aplicada a uma folha depende da data de competência dela.
Um afastamento longo pode passar por mudança de lei, e cada mês usa a
regra vigente naquele mês.

Decisão: Criar a tabela leave_types (catálogo) e apontar para ela.
leave_types → id, code (único, ex: 'FERIAS'), description, created_at
leave_type_rules → troca o texto leave_type por leave_type_id
(chave estrangeira para leave_types.id)
o restante do ADR-05 continua valendo
worker_leaves → troca o texto leave_type por leave_type_id
(chave estrangeira para leave_types.id)
O índice parcial de unicidade da regra ativa passa a ser por
(leave_type_id, jurisdiction) WHERE valid_until IS NULL.
Seed: leave_types é populada primeiro, depois leave_type_rules.

Alternativas consideradas:
A. Apontar para leave_type_rules.id: prenderia o afastamento a uma
versão antiga da regra, mesmo após mudança de lei. Descartada.
C. Sem chave estrangeira, validando só no serviço: perde a garantia
do banco. Descartada.

Decisão em aberto:
O índice parcial impede duas regras ativas, mas não impede períodos
passados sobrepostos para o mesmo tipo e jurisdição. Como a regra é
buscada pela data, sobreposição deixaria a busca ambígua. Avaliar a
mesma exclusion constraint do ADR-07.

Limitações:

- Um tipo pode existir em leave_types sem regra para uma jurisdição
  ou data. Isso precisa ser verificado no serviço e no seed.
- Uma tabela a mais.

Hipótese a validar:
A chave estrangeira para leave_types.id é aceita pelo PostgreSQL
(esperado, id é chave primária). Será confirmado na primeira migration.

Consequências:

- chave estrangeira válida e tipo inexistente continua impossível
- cada folha usa a regra vigente na sua competência

* uma tabela a mais e um JOIN a mais na consulta da regra

Revisa: ADR-05 (apenas a chave estrangeira de worker_leaves).
