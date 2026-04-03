# Israel Semiconductor PE Database

A structured database of Israeli semiconductor companies, grants, patents, and
corporate filings — built to support private-equity deal sourcing and due
diligence.

---

## Stack

| Layer | Technology |
|---|---|
| Notebooks / compute | Google Colab (Python 3.10) |
| Database | Supabase (PostgreSQL 15, asyncpg) |
| ORM | SQLAlchemy 2 async |
| Validation | Pydantic v2 |
| Code storage | GitHub |
| Secrets | Colab Secrets panel |

---

## Project Structure

```
israel-semicon-db/
  src/
    db/            # models.py, session.py, base.py
    pipelines/     # iia_pipeline.py, registrar_scraper.py, patent_pipeline.py
    matching/      # entity_resolver.py
    api/           # main.py, routes/
  notebooks/       # one .ipynb per session (session_X_Y.ipynb)
  tests/           # test_*.py files
  scripts/         # utility scripts; output CSVs go in scripts/output/ (gitignored)
  requirements.txt
  .gitignore
  README.md
```

---

## Setup (new contributor)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/israel-semicon-db.git
cd israel-semicon-db
```

### 2. Scaffold folder structure (first time only)

```bash
bash scripts/init_repo.sh
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure secrets

In Google Colab, add the following keys via **Secrets** (the key icon in the
left sidebar):

| Secret key | Value |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_DB_URL` | `postgresql+asyncpg://postgres:<password>@<host>:5432/postgres` |
| `SUPABASE_KEY` | Supabase anon/public API key |

Access them in notebooks:

```python
from google.colab import userdata
SUPABASE_URL    = userdata.get('SUPABASE_URL')
SUPABASE_DB_URL = userdata.get('SUPABASE_DB_URL')
SUPABASE_KEY    = userdata.get('SUPABASE_KEY')
```

### 5. Apply nest_asyncio (required in every Colab session)

```python
import nest_asyncio
nest_asyncio.apply()
```

---

## Database Tables (Part 1)

| Table | Purpose |
|---|---|
| `companies` | Master entity list — UUID PK, Israeli company number, sub-sector |
| `iia_grants` | Israel Innovation Authority grant awards |
| `patents` | Patent filings linked to companies |
| `registrar_filings` | Israeli Companies Registrar corporate filings |
| `raw_staging` | Raw ingest buffer before entity resolution |

**Sub-sector taxonomy (exact values):**
`fabless` | `ip_licensing` | `eda` | `automotive` | `defense` |
`photonics` | `mixed_signal` | `rf_wireless`

---

## Data Sources

| Source | Description |
|---|---|
| Israel Innovation Authority (IIA) | R&D grants and approved budgets |
| Israel Patent Office / USPTO / EPO | Patent filings by Israeli entities |
| Israel Companies Registrar (Rasham HaChavarot) | Corporate registrations, officers, filings |
| TASE (Tel Aviv Stock Exchange) | Public company disclosures |
| LinkedIn / Crunchbase (manual) | Headcount, funding rounds |

---

## Naming Conventions

- All identifiers: `snake_case`
- Monetary fields: `_ils` suffix for ILS amounts, `_usd` for USD amounts
- Text fields: `name_en` = English canonical name, `name_he` = Hebrew legal name
- Primary key: `company_id` (UUID) | Legal identifier: `company_number`

---

## Session Log

| Session | Branch | Description |
|---|---|---|
| 0.1 | `claude/setup-semicon-db-env-JEH45` | Repo scaffold, requirements, gitignore, README |
