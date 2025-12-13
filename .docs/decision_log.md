# Log de Decisoes do Projeto

Este arquivo documenta as principais decisoes de arquitetura e funcionalidades implementadas neste projeto, incluindo o que foi feito e por que.

---

### 2025-11-30: Alinhamento de Documentacao e Testes de Roteamento

- **O que foi feito:**
  1. `README.md` atualizado com lista completa de agentes, comandos `/agente` e `/limpar`, persistencia do historico (`conversation_context.json`) e nota de que `tools` e conceitual.
  2. `.docs/copilot-instructions.md` reescrito para refletir o uso de `system_prompt`/`tools`, comandos e fluxo do `Orchestrator`.
  3. Adicionado `tests/test_orchestrator.py` com casos para `_extract_text_from_response` e `choose_agent_for_message`, cobrindo cenarios comuns e fallback.
- **Por que foi feito:** Para alinhar a documentacao ao estado atual do codigo e criar uma base minima de testes que previna regresoes em roteamento e extracao de texto.

---

### 2025-11-30: Templates MCP e ajustes de ferramentas

- **O que foi feito:**
  1. Adicionado `.docs/mcp-servers.example.toml` com blocos de configuracao para MCP (postgres, azure, github).
  2. Atualizado `README.md` e `.docs/copilot-instructions.md` para referenciar MCP, `MCP_SERVERS_FILE` e listar quais agentes usam cada ferramenta (`mcp:postgres`, `mcp:azure`, `mcp:github`).
  3. Ajustados `tools` dos agentes: `devops` agora inclui `mcp:github` e `arquitetura_cloud` usa `mcp:azure`.
  4. `orchestrator.py` agora carrega um TOML de MCP e avisa quando ferramentas declaradas nao estao configuradas.
- **Por que foi feito:** Para preparar o orquestrador para usar servidores MCP reais, deixando claro como configurar ferramentas para postgres, azure e github.

---

### 2025-11-30: Orquestrador agnostico de provedor LLM com estrategia custo/beneficio

- **O que foi feito:**
  1. Criado `llm_client.py` com adaptadores para OpenAI, Gemini e Claude, com selecao de modelo por `LLM_PROVIDER` e estrategia `LLM_STRATEGY=quality|balance|cost`, incluindo overrides de modelo.
  2. `orchestrator.py` agora usa `LLMClient` generico, injeta aviso de MCP e evita enviar modelos OpenAI para outros provedores.
  3. Adicionados testes para o resolutor de modelos (`tests/test_llm_client.py`) e adaptados testes do orquestrador para usar LLM fake.
  4. Documentacao atualizada (`README.md`, `.docs/copilot-instructions.md`) com novas envs e fluxo multi-provedor; adicionada `mcp-servers.local.toml` com defaults seguros.
- **Por que foi feito:** Para permitir escolher o melhor provedor e modelo de acordo com custo/beneficio sem alterar a logica do orquestrador, mantendo compatibilidade com configuracoes existentes.

### 2025-11-30: Refatoracao para Modulo de Agentes e Criacao do Agent.Arquitetura

- **O que foi feito:**
  1. Foi criada uma pasta `agents/` para modularizar as definicoes dos agentes.
  2. O primeiro agente especializado, `agents/agent_arquitetura.py`, foi criado com um prompt de sistema robusto e uma funcao de fabrica (`create_agent`).
  3. O `orchestrator.py` foi refatorado para carregar dinamicamente os agentes a partir deste novo modulo, em vez de te-los definidos localmente. O dicionario `AGENTS` agora e populado chamando as funcoes de fabrica de cada agente.
  4. O agente "arquiteto" generico foi substituido pelo novo `Agent.Arquitetura`.
- **Por que foi feito:** Para desacoplar a logica do orquestrador da definicao dos agentes. Esta abordagem torna o projeto mais organizado, escalavel e facil de manter. Adicionar ou modificar agentes agora pode ser feito em seus proprios arquivos, sem alterar o nucleo do orquestrador.

---

### 2025-11-29: Criacao do Log de Decisoes

- **O que foi feito:** Foi criado este arquivo (`.docs/decision_log.md`) para servir como um registro central das decisoes de desenvolvimento.
- **Por que foi feito:** Para manter um historico claro da evolucao do projeto, facilitando o entendimento do contexto e das razoes por tras das mudancas para todos os desenvolvedores e assistentes de IA. O assistente de IA deve ler este arquivo antes de sugerir mudancas e atualiza-lo apos cada implementacao significativa.

---

### 2025-11-28: Implementacao do Contexto de Conversa Persistente

- **O que foi feito:** Um arquivo (`conversation_context.json`) foi criado para salvar o historico das interacoes do usuario com os agentes. O orquestrador agora carrega esse historico ao iniciar e o atualiza apos cada resposta. Um comando `/limpar` foi adicionado para resetar o contexto.
- **Por que foi feito:** Para dar aos agentes uma "memoria" de longo prazo. Isso permite que a conversa continue de onde parou, mesmo que o programa seja fechado e reaberto, garantindo que o contexto e as decisoes tomadas durante a interacao nao sejam perdidos.

---

### 2025-11-27: Adicao de Selecao Manual de Agentes (Slash Commands)

- **O que foi feito:** A logica do `interactive_loop` em `orchestrator.py` foi modificada para reconhecer comandos iniciados com `/` (ex: `/dba`, `/devops`).
- **Por que foi feito:** Para dar ao usuario controle direto sobre qual agente deve tratar uma solicitacao especifica, contornando o roteamento automatico baseado em palavras-chave quando necessario. Isso aumenta a flexibilidade e a precisao do sistema.
