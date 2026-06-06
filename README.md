# Config Manager CLI

Ferramenta de linha de comando para gerenciar arquivos de configuração.

## Descrição

CLI em Python para organizar, validar, transformar e gerenciar arquivos de configuração
de projetos (JSON, YAML, TOML, INI, .env, etc.).

### Funcionalidades previstas

- **Validação** de configs contra schemas
- **Conversão** entre formatos (YAML ↔ JSON ↔ TOML)
- **Merge** de configs por ambiente (dev, staging, prod)
- **Template** de configs com variáveis de ambiente
- **Diff** entre versões de configuração

## Requisitos

- Python 3.10+

## Instalação

```bash
# Criar virtualenv
python -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -e .
```

## Uso

```bash
# Mostrar ajuda
config-manager --help

# Validar arquivo de configuração
config-manager validate config.yaml --schema schema.json

# Converter entre formatos
config-manager convert config.yaml --to json

# Merge de configs por ambiente
config-manager merge base.yaml envs/dev.yaml

# Aplicar template com variáveis de ambiente
config-manager template config.tpl --env .env
```

## Estrutura do Projeto

```
├── README.md              # Este arquivo
├── QWEN.md                # Contexto para interações com o agente
├── pyproject.toml         # Configuração do projeto Python
├── requirements.txt       # Dependências (se aplicável)
├── .venv/                 # Virtual environment (ignorada)
└── src/
    └── config_manager/
        ├── __init__.py
        ├── cli.py         # Interface de linha de comando
        ├── validators/    # Validadores por formato
        ├── converters/    # Conversores entre formatos
        └── utils/         # Utilitários comuns
```

## Roadmap

- [x] Definir linguagem e stack (Python + Click/Typer)
- [x] Definir funcionalidade core (gerenciamento de configs)
- [ ] Criar estrutura de diretórios e `pyproject.toml`
- [ ] Implementar comando `validate`
- [ ] Implementar comando `convert`
- [ ] Implementar comando `merge`
- [ ] Implementar comando `template`
- [ ] Adicionar testes unitários
- [ ] Documentar uso avançado e plugins
