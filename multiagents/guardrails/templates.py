CONTEXT_TEMPLATE = """# Contexto do Projeto

## Objetivo do produto
- Descreva o problema/impacto de negocio.

## Arquitetura
- Estilo, modulos, boundaries, tecnologias.

## Fluxos principais
- Happy path do sistema.

## Fluxos secundarios e excecoes
- Fluxos alternativos, erros esperados.

## Integracoes
- Sistemas externos, protocolos, contratos.

## Observabilidade / logs
- Padroes de log/metricas/tracing.

## Restricoes NFR
- Performance, disponibilidade, seguranca, privacidade, custo.

## Convencoes do repo
- Estrutura de pastas, ferramentas, padroes de commit/branch.
"""

DECISOES_TEMPLATE = """# Registro de Decisoes (ADR simplificado)

- Data:
- Decisao:
- Contexto:
- Alternativas:
- Consequencias:
"""

TASKLIST_TEMPLATE = """# Tasklist

## Dimensao 1 - Task List Global do Projeto
| Ordem | Titulo | Descricao | Prioridade | Criticidade | Dependencias | Status |
|-------|--------|-----------|------------|-------------|--------------|--------|

## Dimensao 2 - Execucao Atual (Ultimo Pedido do Usuario)
| Ordem | Titulo | Descricao | Status |
|-------|--------|-----------|--------|
"""
