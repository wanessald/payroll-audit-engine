ADR-07: Modelagem de alíquotas — aliquot_rates e prevenção de sobreposição de faixas

Resumo:
A tabela guarda faixas de salário com suas alíquotas. Duas faixas nunca
podem cobrir o mesmo salário na mesma época, senão o sistema não saberia
qual alíquota usar. Por isso o banco recusa faixas sobrepostas, o que
protege contra erro de digitação no seed e contra inserção direta.
Fronteira: o número de cima de cada faixa está incluído, o de baixo não.
Exemplos: R$ 1.621,00 é faixa 1; R$ 2.902,84 é faixa 2.

Contexto: INSS, IRRF e FGTS são calculados por tabelas de faixas salariais
que mudam por decreto. INSS e IRRF são progressivos (várias faixas);
FGTS tem uma única alíquota fixa. As tabelas precisam preservar
histórico por competência (ADR-01, padrão SCD2 do ADR-05/06).

Requisito de negócio:
Para um mesmo rate_type, jurisdição e data de competência, cada salário
pertence a exatamente uma faixa. Duas faixas cobrindo o mesmo salário
é dado inválido, não uma situação a ser desempatada.

Decisão: Tabela única aliquot_rates, uma linha por faixa:
id
rate_type → 'INSS' | 'IRRF' | 'FGTS'
salary_from → Numeric — início da faixa
salary_until → Numeric nullable — fim da faixa (NULL = sem teto)
rate → Numeric — alíquota da faixa
deduction_amount → Numeric — parcela a deduzir em R$
(IRRF; INSS se usar o método da dedução; 0 quando não se aplica)
valid_from → Date
valid_until → Date nullable (NULL = vigente)
jurisdiction → String(5), default 'BR' (ADR-01)
created_at → DateTime(timezone=True)

FGTS é representado como uma única faixa sem teto:
salary_from = 0 | salary_until = NULL | rate = 0.08 | deduction = 0
NULL como "sem limite" em vez de número sentinela: qualquer teto numérico
pode ser ultrapassado e deixaria um salário sem regra aplicável.

Prevenção de sobreposição: EXCLUSION CONSTRAINT no PostgreSQL, combinando
rate_type, jurisdiction, intervalo de salário (numrange) e intervalo de
vigência (daterange) com o operador de sobreposição.
O intervalo de vigência faz parte da constraint para que faixas de anos
diferentes, com o mesmo intervalo de salário, não conflitem (histórico SCD2).

Alternativas consideradas:
B. Validação apenas na camada de serviço ao inserir a tabela.

- mais simples de entender e testar

* o banco aceitaria sobreposição em inserção direta ou erro no seed
  Escolha:
  A. Uma única barreira cobre erro de seed e inserção direta
  (regra crítica no banco, conforme cheat sheet banco vs. aplicação).

Convenção de fronteira (decidida):
Intervalo aberto à esquerda e fechado à direita: (salary_from, salary_until].
Reflete o texto da tabela oficial: "até R$ X" inclui X; a faixa seguinte
começa logo acima de X.
Fronteiras contíguas: salary_from da faixa N = salary_until da faixa N-1.
Evidência: tabela INSS 2026 em fontes secundárias; conferir em gov.br/inss
antes do seed.
Caso de borda para teste: salário exatamente igual à fronteira
(ex: R$ 1.621,00 pertence à faixa 1).

Hipóteses a validar:

1. A extensão btree_gist está disponível na imagem postgres:16 do Docker.
2. A constraint rejeita faixas sobrepostas da mesma vigência e aceita
   faixas iguais em vigências diferentes.
   Validação pendente: TASK-TESTE-03, teste de integração que insere duas
   faixas sobrepostas e verifica a rejeição, e depois insere a mesma faixa
   em outro ano e verifica a aceitação.

Validação (05/11/2026, PostgreSQL 16, teste manual via psql no banco real):
Hipótese 1: btree_gist disponível e instalada pela migration → CONFIRMADA
Hipótese 2: a constraint recusa faixas sobrepostas na mesma vigência
e aceita a mesma faixa em outra vigência → CONFIRMADA - (0, 1621.00] e (1621.00, 2902.84] na mesma vigência: aceitas
(fronteira compartilhada não é sobreposição) - (0, 1518.00] com vigência de 2025: aceita - (1500.00, 3000.00] em 2026: recusada (ex_aliquot_rates_no_overlap)
Limite da evidência: teste manual, não reproduzível. O teste automatizado
em Pytest (TASK-TESTE-03) continua pendente.
Lacunas (salário sem faixa) não foram testadas e continuam sendo
limitação conhecida.

Limitações conhecidas:

- Exclusion constraint impede sobreposição, mas NÃO impede lacunas
  (um salário sem nenhuma faixa). Lacunas precisam ser verificadas
  no seed e/ou na camada de serviço.
- Específica do PostgreSQL e exige a extensão btree_gist, que precisa de
  permissão de criação de extensão (pode ser restrita em bancos gerenciados).
- Mais complexa que um índice único: maior custo de entendimento e manutenção.

Consequências:

- sobreposição de faixas é impossível por qualquer caminho de escrita
- mesma estrutura serve INSS, IRRF e FGTS
- histórico de tabelas por competência preservado (SCD2)

* lacunas exigem validação adicional
* dependência de extensão do PostgreSQL

Referências:
PostgreSQL — Exclusion constraints →
https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION
PostgreSQL — Range types →
https://www.postgresql.org/docs/current/rangetypes.html
PostgreSQL — btree_gist →
https://www.postgresql.org/docs/current/btree-gist.html
