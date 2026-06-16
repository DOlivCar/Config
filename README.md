# Config_DSAA

Loading de configurações para projetos Python.
 O `ConfigLoader` lê automaticamente todos os ficheiros de configuração presentes na pasta `config/` e expõe os seus valores como atributos da instância.

---

## Formatos suportados

| Extensão | Formato | Exemplo |
|---|---|---|
| `*.env` | `KEY=VALUE` (python-dotenv) | `exemplo.env` |
| `*.yaml` / `*.yml` | Mapeamento YAML | `config_exemplo.yaml` |
| `*.json` | Objeto JSON | `config_exemplo.json`, `save_paths_exemplo.json` |

---

## Estrutura da pasta `config/`

```
config/
├── exemplo.env              # variáveis de ambiente
├── config_exemplo.yaml      # configurações gerais
├── config_exemplo.json      # caminhos de entrada
└── save_paths_exemplo.json  # caminhos de saída
```

---


---

## Múltiplos ficheiros do mesmo formato

O `ConfigLoader` carrega **todos** os ficheiros da pasta `config/` automaticamente, independentemente do número ou nome. Podem coexistir vários `.env`, `.json`, `.yaml`, etc.

### Exemplo — separar configurações de app e de base de dados

```
config/
├── exemplo.env       # APP_NAME, DEBUG, API_KEY, TIMEOUT
├── database.env      # DB_HOST, DB_PORT, DB_NAME, DB_USER
├── config_exemplo.json   # input_paths
└── database.json     # db_settings
```

`config/database.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=admin
```

`config/database.json`:
```json
{
  "db_settings": {
    "pool_size": 5,
    "timeout": 30,
    "retry_attempts": 3
  }
}
```

Após instanciar o `ConfigLoader`, todos os atributos ficam disponíveis na mesma instância.

> **Atenção a conflitos de chaves:** se dois ficheiros definirem a mesma chave de topo, o ficheiro carregado por último sobrescreve o anterior. A ordem de carregamento depende do sistema de ficheiros e não é garantidamente alfabética. Para evitar conflitos, use chaves de topo únicas por ficheiro.

## Instanciar o ConfigLoader

```python
from src.config import ConfigLoader

cfg = ConfigLoader()
```

Por defeito, o `ConfigLoader` aponta para a pasta `config/` na raiz do projeto (detetada automaticamente via `pyproject.toml`). 
É possível configurar uma pasta alternativa:

```python
from pathlib import Path
from src.config import ConfigLoader

cfg = ConfigLoader(config_dir=Path("outro/caminho/config"))
```

---

## Aceder aos atributos

Cada chave de topo dos ficheiros de configuração torna-se um atributo da instância.

### Variáveis `.env`

Ficheiro `config/exemplo.env`:
```env
APP_NAME=ConfigLoader Test
DEBUG=true
API_KEY=abc123
TIMEOUT=30
```

Acesso:
```python
print(cfg.APP_NAME)   # "ConfigLoader Test"
print(cfg.DEBUG)      # "true"
print(cfg.API_KEY)    # "abc123"
print(cfg.TIMEOUT)    # "30"
```

> **Nota:** os valores `.env` são sempre carregados como `str`.

---

### Ficheiros YAML

Ficheiro `config/config_exemplo.yaml`:
```yaml
app_version: 1.0.0
environment: development
log_level: INFO
```

Acesso:
```python
print(cfg.app_version)   # "1.0.0"
print(cfg.environment)   # "development"
print(cfg.log_level)     # "INFO"
```

---

### Ficheiros JSON

Ficheiro `config/config_exemplo.json`:
```json
{
    "input_paths": {
        "csv_path": "output/csv",
        "json_path": "json_path",
        "md_path": "output/md"
    }
}
```

Acesso:
```python
print(cfg.input_paths["csv_path"])   # "output/csv"
print(cfg.input_paths["md_path"])    # "output/md"
```

Ficheiro `config/save_paths_exemplo.json`:
```json
{
    "save_paths": {
        "csv": "output/csv",
        "json": "output/json",
        "md": "output/markdown"
    }
}
```

Acesso:
```python
print(cfg.save_paths["csv"])    # "output/csv"
print(cfg.save_paths["json"])   # "output/json"
print(cfg.save_paths["md"])     # "output/markdown"
```

---

### Ir buscar os atributos com o método `get()` 
```python
timeout = cfg.get("TIMEOUT", 60)          # retorna "30" ou 60 se a chave não existir
nivel   = cfg.get("log_level", "WARNING") # retorna "INFO"
```

---

## Guardar ficheiros com o método `save()`

O método `save()` escreve dados para a pasta configurada em `save_paths`.

```python
# CSV — lista de dicionários
cfg.save(
    data=[{"nome": "Alice", "score": 92}],
    filename="resultados",
    output_format="csv"
)

# JSON — qualquer objeto serializável
cfg.save(
    data={"versão": "1.0.0", "debug": True},
    filename="metadata",
    output_format="json"
)

# Markdown — string
cfg.save(
    data="# Relatório\n\nConteúdo gerado automaticamente.",
    filename="relatorio",
    output_format="md"
)
```

Os ficheiros são escritos nos diretórios definidos em `save_paths` (relativos à raiz do projeto).

---

## Sincronização de dependências

```bash
uv sync
```

## Executar exemplo

```bash
uv run main.py
```
