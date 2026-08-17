ADR-03: Estratégia de identificadores
Contexto: O sistema precisa de performance em JOINs internos (trilha de
auditoria referencia múltiplas tabelas) e segurança na exposição
de IDs via API (IDs sequenciais permitem enumeração de registros).

Decisão: Abordagem híbrida em todas as tabelas

- id: BIGINT gerado pelo banco → chave primária interna, usado em FKs e JOINs, nunca exposto na API
- public_id: UUID v7 gerado na aplicação → exposto na API e nos relatórios de auditoria, único e não enumerável

Consequências:

- JOINs internos usam BIGINT — máxima performance
- API nunca expõe sequência interna — sem risco de enumeração
- UUID v7 é ordenável cronologicamente — consultas por tempo eficientes

* Cada tabela tem dois identificadores — complexidade ligeiramente maior
  Referência: RFC 9562 (UUID v7) → https://www.rfc-editor.org/rfc/rfc9562
