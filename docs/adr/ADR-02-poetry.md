ADR-02: Gerenciador de dependências — Poetry
Contexto: O projeto exige reprodutibilidade de ambiente para fins de auditoria.
O mesmo conjunto de versões que calculou uma folha em produção precisa
ser reconstituível exatamente para revisão posterior.
A ferramenta precisa ser familiar ao desenvolvedor para não adicionar
fricção desnecessária ao aprendizado.
Decisão: Usar Poetry como gerenciador de dependências.
Motivações:

- Familiaridade: ferramenta já utilizada e conhecida pelo desenvolvedor
- Reprodutibilidade: poetry.lock registra versões exatas de todos os pacotes
  (diretos e transitivos), garantindo que qualquer clone do repositório
  instale exatamente o mesmo ambiente
- Lock file nativo: gerado e atualizado automaticamente a cada `poetry add`,
  sem necessidade de ferramentas adicionais como pip-tools
  Consequências:

* poetry.lock versionado no Git garante ambiente auditável e reproduzível
* pyproject.toml continua sendo o arquivo de declaração de dependências

- Poetry 2.x tem breaking changes em relação a versões anteriores —
  pyproject.toml precisa seguir o schema correto (sem `python` em [tool.poetry])
  Referência: https://python-poetry.org/docs/
