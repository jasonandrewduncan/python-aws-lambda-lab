# Python AWS Lambda Data Pipeline Lab

A small Lambda-oriented Python lab that ingests CSV, JSON, and JSONL source data into PostgreSQL staging tables, transforms the data into a curated `daily_sales_summary`, and explores a simple sales forecast in Jupyter.

## What it demonstrates

- Python data ingestion and transformation
- SQL-based aggregation in PostgreSQL
- Multiple source types: CSV, JSON, JSONL
- Structured and semi-structured data handling
- Lambda-ready handler structure
- Docker-based local database setup
- Basic forecasting with actuals, rolling average, and polynomial trend

## Project structure

```text
python-aws-lambda-lab/
  .devcontainer/
    devcontainer.json
    docker-compose.yml
  requirements.txt
  .env.example
  README.md
  sql/
    init.sql
    reset_data.sql
  src/
    db.py
    ingest_lambda.py
    load_from_staging_lambda.py
    load_summary_lambda.py
  data/
    sample_orders.csv
    sample_events.json
    sample_logs.jsonl
    daily_sales_summary_seed.csv
  notebooks/
    sales_forecast.ipynb
```

## Setup

### 1. Start PostgreSQL

```bash
docker compose -f .devcontainer/docker-compose.yml up -d
```

### Initialize the database with a SQL client

Use either:

- VS Code with `SQLTools` and `SQLTools PostgreSQL/Cockroach Driver`
- another PostgreSQL client such as DBeaver

Connect to the database with these settings:

- host: `postgres` when you are inside the dev container, otherwise `localhost`
- port: `5432`
- database: `lambda_lab`
- user: `lambda_lab`
- password: `lambda_lab`

For first-time setup, run:

1. `sql/init.sql`

That creates the database tables.

Later, after you have loaded staging data, run:

1. `python src/load_from_staging_lambda.py`
2. `python src/load_summary_lambda.py`

For interactive test reruns, you can reset table data first with:

1. `sql/reset_data.sql`

### Alternative: open in a dev container

The project includes a `.devcontainer` setup that starts the Python workspace container and the PostgreSQL service on the same Docker Compose network.

Inside the dev container, the database host is `postgres` instead of `localhost`, so the app can connect to the Compose service directly without any extra local setup.

#### SSH / GitHub access from inside the dev container (WSL)

The devcontainer uses SSH agent forwarding so you can `git push` to GitHub without copying your private key into the container. It reads `SSH_AUTH_SOCK` from your WSL environment at container-start time.

**Prerequisite — WSL must have ssh-agent running before you open the devcontainer in VS Code.**

Add this to your WSL `~/.bashrc` (or `~/.zshrc`) so the agent starts automatically:

```bash
# Start ssh-agent once per WSL session
if [ -z "$SSH_AUTH_SOCK" ]; then
  eval "$(ssh-agent -s)" > /dev/null
fi
ssh-add -l &>/dev/null || ssh-add ~/.ssh/id_ed25519
```

Replace `id_ed25519` with your actual key filename (`id_rsa`, etc.) if different. After editing the file, run `source ~/.bashrc` (or open a new WSL terminal), then rebuild/reopen the devcontainer. You can verify it's working inside the container with:

```bash
ssh -T git@github.com
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Copy `.env.example` to `.env` or export the values manually.

## Run the pipeline

### Ingest raw files into staging

```bash
python src/ingest_lambda.py
```

### Load staging into curated orders

```bash
python src/load_from_staging_lambda.py
```

### Build daily summary from orders

```bash
python src/load_summary_lambda.py
```

## Explore the forecast

Launch Jupyter and open the notebook:

```bash
jupyter notebook
```

Open:

```text
notebooks/sales_forecast.ipynb
```

## Tables created

- `staging_orders`
- `staging_events`
- `staging_logs`
- `orders`
- `daily_sales_summary`

## Notes

- `sample_orders.csv` is the only source used to build `orders` and `daily_sales_summary`.
- `sample_events.json` and `sample_logs.jsonl` are still loaded into staging so you can talk about integrating multiple source types.
- The notebook intentionally keeps forecasting simple:
  - actuals
  - 7-day rolling average
  - 2nd-degree polynomial forecast

## Possible cleanup/improvements later

- Add validation/reject tables
- Add indexes based on query plans
- Add idempotent upserts with stronger de-duplication rules
- Split local file ingestion from true S3-triggered Lambda events

## What's next / What's missing

- CI/CD builds in Github Actions
- Tests/Linting
- AWS/Terraform infrastructure and deployment
- CloudWatch monitoring and IAM/ARN-based security
