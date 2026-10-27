# DevOps Capstone

[![Build Status](https://github.com/MrRohit2309/devops-capstone-project/actions/workflows/ci-build.yaml/badge.svg)](https://github.com/MrRohit2309/devops-capstone-project/actions/workflows/ci-build.yaml)

Customer Accounts is a small Flask REST microservice for creating, reading,
updating, and deleting customer accounts.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app service run --debug
```

The API is available under `/api/customers`; use `GET /health` for a health
check. Data is held in memory and is intended for the capstone demonstration.

## Test and lint

```bash
pytest
flake8 service tests
pylint service
```

## Container

```bash
docker build -t customer-accounts .
docker run --rm -p 8080:8080 customer-accounts
```