# QWEN.md — Contexto do Projeto

## Visão Geral

**Config Manager CLI** — Ferramenta de linha de comando em Python para gerenciar arquivos de configuração.

O projeto permite validar, converter, fazer merge e aplicar templates em arquivos de configuração
nos formatos JSON, YAML, TOML, INI e .env.

## Tecnologias e Stack

| Item | Escolha |
|---|---|
| **Linguagem** | Python 3.10+ |
| **CLI Framework** | Typer (ou Click) |
| **Formatos** | JSON, YAML, TOML, INI, .env |
| **Testes** | pytest |
| **Linting** | ruff |
| **Build** | `pip install -e .` (pyproject.toml) |

## Estrutura do Projeto

```
Qwen/
├── README.md
├── QWEN.md
├── pyproject.toml
├── .venv/
└── src/config_manager/
    ├── __init__.py
    ├── cli.py
    ├── validators/
    ├── converters/
    └── utils/
```

## Comandos Principais

```bash
# Instalar em modo desenvolvimento
pip install -e .

# Executar
config-manager --help
config-manager validate config.yaml --schema schema.json
config-manager convert config.yaml --to json
config-manager merge base.yaml envs/dev.yaml
config-manager template config.tpl --env .env

# Testes
pytest

# Linting
ruff check src/
```

## Convenções de Desenvolvimento

- Código no diretório `src/` (layout de projeto moderno Python)
- Typer para definição de comandos CLI
- pytest para testes
- ruff para linting e formatação
- Tipos Python (type hints) obrigatórios

## Como Atualizar Este Arquivo

Atualizar quando:
- Novas bibliotecas ou formatos forem adicionados
- Comandos CLI mudarem
- Estrutura de diretórios for alterada
- Convenções de código forem definidas
