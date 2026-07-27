ADR-01: Jurisdição base — Brasil (CLT / eSocial), com arquitetura preparada
para internacionalização
Contexto: O sistema tem duplo propósito — portfólio e uso real futuro.
O domínio financeiro escolhido é folha de pagamento.
Cobrir múltiplas jurisdições simultaneamente seria desproporcional
para a fase inicial.
Decisão: Implementar regras brasileiras como jurisdição base: - Cálculos de INSS, IRRF e FGTS conforme CLT e tabelas vigentes - Eventos de folha compatíveis com leiaute eSocial - Retenções conforme EFD-Reinf - Reconhecimento de provisões (férias, 13º) conforme NBC TG 26
Arquitetura preparada para internacionalização desde o início: - Tabelas de alíquotas com coluna `jurisdiction` ('BR', 'US', 'PT'...) - Colunas `valid_from` / `valid_until` para versionamento de regras - Regras de cálculo isoladas em `domain/rules/` parametrizável
Regras internacionais (IAS 19, ISO 20022) não implementadas na fase inicial.
Referências:

- CLT → https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm
- eSocial → https://www.gov.br/esocial
- NBC TG 26 → https://www.cfc.org.br
- IAS 19 (expansão futura) → https://www.ifrs.org/issued-standards/list-of-standards/ias-19-employee-benefits/
  Consequências:

* Fixtures de teste podem usar XMLs e valores reais de eSocial
* Tabelas de alíquotas nunca hardcoded — sempre consultadas por vigência
* Adicionar nova jurisdição = inserir linhas no banco, não alterar código

- Validação de compliance exige consulta à tabela vigente na competência
