# Config Manager CLI

![CI](https://github.com/RBarucco-jr/Qwen/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/github/RBarucco-jr/Qwen/branch/master/graph/badge.svg)

CLI em Python para organizar, validar, converter, mesclar e comparar arquivos de configuração.

Suporta **JSON, YAML, TOML, INI e .env**.

## Funcionalidades

| Comando | Descrição |
|---|---|
| `validate` | Valida configs contra JSON Schema ou verifica se são parseáveis |
| `convert` | Converte entre formatos (JSON ↔ YAML ↔ TOML) |
| `merge` | Deep merge de configs por ambiente (dev, staging, prod) |
| `template` | Substitui variáveis (`${VAR}`, `$VAR`, `{{VAR}}`) usando .env |
| `diff` | Mostra diferenças entre dois arquivos de configuração |

## Requisitos

- Python 3.10+

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

```bash
# Ajuda geral
config-manager --help

# Validar (basic — verifica se é parseável)
config-manager validate config.json

# Validar contra schema
config-manager validate config.json --schema schema.json

# Converter JSON → YAML
config-manager convert config.json --to yaml

# Converter YAML → JSON (salvar em arquivo)
config-manager convert config.yaml --to json --output output.json

# Merge base + override (deep merge)
config-manager merge base.yaml dev.yaml

# Template com .env
config-manager template config.tpl --env .env

# Diff entre dois configs
config-manager diff config.yaml dev.yaml
```

## Desenvolvimento

```bash
# Instalar em modo dev
pip install -e ".[dev]"

# Rodar testes
pytest

# Linting
ruff check src/

# Auto-fix linting
ruff check src/ --fix
```

## Estrutura do Projeto

```
├── pyproject.toml                     # Configuração do projeto
├── src/config_manager/
│   ├── cli.py                         # CLI (Typer)
│   ├── validators/
│   │   └── runner.py                  # Validação com jsonschema
│   ├── converters/
│   │   └── runner.py                  # Conversão entre formatos
│   └── utils/
│       ├── format_detector.py         # Detecção e carregamento
│       ├── merger.py                  # Deep merge
│       ├── templater.py               # Template com env vars
│       └── differ.py                  # Diff entre configs
└── tests/
    └── test_format_detector.py        # Testes de format detection
```

## Roadmap

- [x] Definir linguagem e stack (Python + Typer)
- [x] Estrutura de diretórios e `pyproject.toml`
- [x] Implementar `validate`
- [x] Implementar `convert`
- [x] Implementar `merge`
- [x] Implementar `template`
- [x] Implementar `diff`
- [x] Testes unitários (9 passing)
- [ ] Serialização para INI/.env
- [ ] Testes para merge, convert, template, diff
- [ ] Documentação de uso avançado e plugins

## Licença

MIT