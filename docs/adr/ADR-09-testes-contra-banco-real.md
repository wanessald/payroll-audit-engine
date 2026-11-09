ADR-09: Testes de banco usam um banco separado e a migration real

Resumo em linguagem simples:
Os testes rodam num banco só deles (payroll_audit_test), montado pela
mesma migration que vai para produção. Assim testamos o banco de verdade
sem risco para os dados de desenvolvimento.

Contexto: As regras de integridade (índices parciais, exclusion
constraint, chaves estrangeiras) vivem no PostgreSQL. Só dá
para prová-las contra um PostgreSQL real.

Decisão:

1. Banco separado: payroll_audit_test, no mesmo container.
2. Esquema criado com alembic upgrade head (opção B), não com create_all().
3. O nome do banco é trocado por variável de ambiente no tests/conftest.py,
   antes de qualquer import do app.
4. Trava de segurança: uma fixture de sessão aborta o Pytest se o engine
   não apontar para um banco terminado em "\_test".

Alternativas:
A. create_all(): simples, mas não executa a migration (nem o
CREATE EXTENSION btree_gist). Descartada.

Hipótese a validar:
Com create_all(), a tabela aliquot_rates falharia por falta do btree_gist.
Ainda não observado; não é necessário para a decisão.

Decisão em aberto:
Como isolar os testes entre si (rollback ao fim de cada teste ou
limpar as tabelas).

Limitações:

- Mais lento que create_all().
- A trava confere só o NOME do banco (sufixo "\_test").

Consequências:

- testa o mesmo caminho da produção
- dados de desenvolvimento protegidos

* exige o container do PostgreSQL no ar para rodar os testes

Referências:
Pytest — conftest.py → https://docs.pytest.org/en/stable/reference/fixtures.html
Alembic — API de comandos → https://alembic.sqlalchemy.org/en/latest/api/commands.html
