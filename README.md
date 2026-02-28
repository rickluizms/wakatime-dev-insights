# 🚀 Dev Insights — Backend

Backend do projeto **Dev Insights**, responsável por integrar com a [API do WakaTime](https://wakatime.com/developers), extrair dados de produtividade e persisti-los em um banco **PostgreSQL**. Expõe uma **API REST** via FastAPI para consulta dos dados armazenados.

---

## 📐 Arquitetura

O backend é composto por dois serviços independentes que rodam em containers separados:

```
┌─────────────────────────────────────────────────────┐
│                   Docker Compose                    │
│                                                     │
│  ┌─────────────────┐      ┌──────────────────────┐  │
│  │   Orchestrator   │      │     API (FastAPI)     │  │
│  │ (src/orchestrator│      │    (src/api/main.py   │  │
│  │  /orchestrator.py)      │                       │  │
│  │                  │      │  · Endpoints REST     │  │
│  │  · Agendamento   │      │  · Autenticação       │  │
│  │  · Extração      │      │  · CORS               │  │
│  │  · Backfill      │◄────►│                       │  │
│  └────────┬─────────┘      └───────────┬───────────┘  │
│           │                            │              │
│           ▼                            ▼              │
│  ┌──────────────────────────────────────────────────┐ │
│  │              PostgreSQL (DATABASE_URL)            │ │
│  └──────────────────────────────────────────────────┘ │
│           ▲                                           │
│           │                                           │
│  ┌────────┴─────────┐                                 │
│  │   WakaTime API   │                                 │
│  │  (api.wakatime.   │                                │
│  │      com)         │                                │
│  └──────────────────┘                                 │
└─────────────────────────────────────────────────────┘
```

| Serviço | Arquivo | Descrição |
|---|---|---|
| **Orchestrator** | `main.py` | Extrai dados da API do WakaTime diariamente (00:15) e persiste no PostgreSQL |
| **API** | `app.py` | Expõe os dados armazenados via endpoints REST protegidos por API Key |

---

## 📁 Estrutura de Arquivos

```
backend/
├── app.py                 # Ponto de entrada da API (Chama src/api/main.py)
├── main.py                # Ponto de entrada do Orquestrador (Chama src/orchestrator)
├── models.py              # Modelos Pydantic (tipagem dos dados da API)
├── src/
│   ├── api/               # API FastAPI modulada (routes, schemas, security, main)
│   └── orchestrator/      # Lógica de extração e gravação (orchestrator, repository, schema, config)
├── core/
│   ├── api.py             # Cliente HTTP para a API do WakaTime
│   └── db.py              # Módulo de conexão e operações com PostgreSQL
├── docs/
│   └── API_GUIDE.md       # Guia completo da API REST
├── Dockerfile             # Imagem Docker (Python 3.11 + uv)
├── docker-compose.yml     # Orquestração dos serviços (API + Worker)
├── pyproject.toml         # Dependências do projeto (gerenciadas com uv)
├── uv.lock                # Lockfile de dependências
├── .env.example           # Template de variáveis de ambiente
├── .python-version        # Versão do Python (3.10)
└── .gitignore
```

---

## ⚙️ Pré-requisitos

- **Python** 3.10+
- **uv** — gerenciador de pacotes ([instalação](https://docs.astral.sh/uv/getting-started/installation/))
- **PostgreSQL** acessível (local ou via Docker)
- **Token da API do WakaTime** — obtido em [wakatime.com/settings/api-key](https://wakatime.com/settings/api-key)

---

## 🛠️ Configuração

### 1. Clonar e acessar o projeto

```bash
git clone https://github.com/rickluizms/dev_insights.git
cd dev_insights/backend
```

### 2. Criar o arquivo `.env`

Copie o template e preencha as variáveis:

```bash
cp .env.example .env
```

```env
DB_PASSWORD=sua_senha_do_postgres
DATABASE_URL=postgresql://usuario:senha@host:5432/dev_insights
WAKATIME_API_TOKEN=seu_token_wakatime
API_KEY_READONLY=your_secure_api_key_here
RUN_SCHEDULED=true
```

| Variável | Descrição |
|---|---|
| `DB_PASSWORD` | Senha do banco PostgreSQL |
| `DATABASE_URL` | String de conexão completa do PostgreSQL |
| `WAKATIME_API_TOKEN` | Token de autenticação da API do WakaTime |
| `API_KEY_READONLY` | Chave de segurança para endpoints protegidos (readonly) |
| `PREVIOUS_DAYS` | Acréscimo de dias anteriores para as estatísticas totais |
| `PREVIOUS_HOURS` | Acréscimo de horas anteriores para as estatísticas totais |
| `SMTP_HOST` | Endereço do servidor SMTP (ex: smtp.gmail.com) |
| `SMTP_PORT` | Porta do SMTP (ex: 587) |
| `SMTP_USER` | Usuário de autenticação do envio de e-mails |
| `SMTP_PASS` | Senha ou App Password do SMTP |
| `SMTP_FROM` | Remetente dos e-mails |
| `DEVELOPER_NAME` | Nome do desenvolvedor |
| `DEVELOPER_MAIL` | E-mail de destino do desenvolvedor |
| `RUN_SCHEDULED` | `true` = executa em loop agendado · `false` = executa uma única vez |

### 3. Instalar dependências

```bash
uv sync
```

---

## 🚀 Execução

### Desenvolvimento Local

#### Orquestrador (extração de dados)

```bash
# Execução única (extrai dados do dia anterior)
uv run python main.py

# Execução agendada (roda diariamente às 00:15)
# Defina RUN_SCHEDULED=true no .env
uv run python main.py
```

#### API REST

```bash
uv run uvicorn app:app --host 0.0.0.0 --port 8091 --reload
```

A documentação interativa estará disponível em:
- **Swagger UI**: http://localhost:8091/docs
- **ReDoc**: http://localhost:8091/redoc

### Docker Compose (recomendado)

```bash
docker compose up -d --build
```

Isso inicia dois containers:

| Container | Porta | Função |
|---|---|---|
| `dev-insights-api` | `8091` | API REST |
| `dev-insights-orchestrator` | — | Worker de extração agendada |

```bash
# Verificar logs
docker compose logs -f

# Parar os serviços
docker compose down
```

---

## 🗄️ Banco de Dados

O schema é criado automaticamente na primeira execução do orquestrador. As tabelas são:

| Tabela | Descrição |
|---|---|
| `daily_summaries` | Resumo diário de atividade (tempo total, código humano vs IA) |
| `languages` | Linguagens utilizadas por dia |
| `projects` | Projetos trabalhados por dia |
| `editors` | Editores utilizados por dia |
| `operating_systems` | Sistemas operacionais por dia |
| `categories` | Categorias de atividade por dia |
| `machines` | Máquinas utilizadas por dia |
| `branches` | Branches trabalhadas por dia |
| `entities` | Arquivos editados por dia |

### Diagrama ER simplificado

```
daily_summaries (1) ──── (N) languages
                   ──── (N) projects
                   ──── (N) editors
                   ──── (N) operating_systems
                   ──── (N) categories
                   ──── (N) machines
                   ──── (N) branches
                   ──── (N) entities
```

> As tabelas secundárias se relacionam com `daily_summaries` pelo campo `summary_date` ↔ `date`.

---

## 📡 API REST

Todos os endpoints (exceto `/health`) são protegidos por **API Key** via header `X-API-Key`.

### Autenticação

```bash
curl -H "X-API-Key: your_secure_api_key_here" http://localhost:8000/summaries
```

### Endpoints disponíveis

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Health check (público) |
| `GET` | `/summaries` | Lista resumos diários |
| `GET` | `/summaries/{date}` | Resumo de uma data específica |
| `GET` | `/languages` | Dados de linguagens por dia |
| `GET` | `/languages/stats` | Estatísticas agregadas de linguagens |
| `GET` | `/projects` | Dados de projetos por dia |
| `GET` | `/projects/stats` | Estatísticas agregadas de projetos |
| `GET` | `/editors` | Dados de editores por dia |
| `GET` | `/stats` | Estatísticas gerais do período |

### Query Parameters comuns

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `start_date` | `string` | Data inicial (`YYYY-MM-DD`) |
| `end_date` | `string` | Data final (`YYYY-MM-DD`) |
| `limit` | `int` | Limite de resultados |

> Para a documentação completa da API, consulte [`docs/API_GUIDE.md`](docs/API_GUIDE.md).

---

## 📦 Dependências

| Pacote | Versão | Uso |
|---|---|---|
| `fastapi` | ≥ 0.128.0 | Framework da API REST |
| `uvicorn` | ≥ 0.40.0 | Servidor ASGI |
| `psycopg2-binary` | ≥ 2.9.11 | Driver PostgreSQL |
| `requests` | ≥ 2.32.5 | Cliente HTTP (WakaTime API) |
| `python-dotenv` | ≥ 1.2.1 | Carregamento de variáveis de ambiente |
| `schedule` | ≥ 1.2.2 | Agendamento de tarefas |

---

## 🔧 Módulos Internos

### `core/api.py` — Cliente WakaTime

Gerencia autenticação via HTTP Basic Auth e fornece métodos para consultar a API:

```python
with WakaTimeAPI(api_token="seu_token") as api:
    summary = api.get_summaries_for_date("2026-01-15")
    week = api.get_week_summaries()
    month = api.get_month_summaries()
```

### `core/db.py` — Módulo de Banco de Dados

Abstração para operações com PostgreSQL usando `psycopg2`:

```python
with Database() as db:
    db.insert("languages", {"summary_date": "2026-01-15", "name": "Python", "total_seconds": 3600})
    rows = db.fetch_all("SELECT * FROM languages WHERE summary_date = %s", ("2026-01-15",))
```

### `models.py` — Modelos de Dados

Modelos Pydantic para tipagem e validação dos dados da API do WakaTime:

- `DailySummary` — Resumo completo de um dia
- `WakaTimeSummariesResponse` — Response da API `/summaries`
- `TimeTotal`, `SimpleStat`, `ProjectStat`, `EntityStat`, `MachineStat` — Modelos auxiliares

---

## 📄 Licença

Este projeto é de uso pessoal. Consulte o repositório principal para informações de licença.
