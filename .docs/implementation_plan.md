# Plano de Implementacao (fase atual)

| Prioridade | Task | Descricao detalhada | Status |
|------------|------|---------------------|--------|
| Alta | MCP Server real | Revisar `server_mcp.py` para retornar a resposta real do orquestrador (texto, agente, modelo, usage) e erros estruturados; integrar tools MCP quando aplicavel. | Pendente |
| Alta | MCP Client robusto | Trocar `mcp/client.py` (subprocess) por SDK MCP com discovery e auth; suportar OAuth/creds; testes com fakes. | Pendente |
| Alta | Token Broker real | Integrar com broker (extensao VS Code/SecretStorage ou servico local) com refresh; melhorar mensagens de erro/retries no client. | Pendente |
| Media | Builder hardening | Validar JSON do Builder, slug seguro, persistir/recuperar `generated_*` no bootstrap; testes de criacao dinamica. | Pendente |
| Media | Cache inteligente | Escopo por repo/commit/arquivo; TTL; opcao NO_CACHE; estatisticas de hit/miss. | Pendente |
| Media | Observabilidade expandida | Logs estruturados com custo/usage; hooks para metricas/OTEL (opcional). | Pendente |
| Baixa | CLI/UX extra | Flags como `--plan-only`, `--agent`, escolha de mapa de modelos; mensagens de fallback melhores. | Pendente |
| Baixa | Docs/Playbooks | Setup por provedor, MCP real, broker real, troubleshooting; atualizar decision log. | Pendente |
