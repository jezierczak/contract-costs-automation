# MySQL Isolated Tests (PowerShell)

## 1) Set env flag for isolated DB

```powershell
$env:TEST_DB_ISOLATED='1'
```

## 2) Run isolated MySQL contract tests

```powershell
uv run pytest -q tests/mysql_isolated -m mysql_isolated --run-mysql-isolated
```

## Optional: choose MySQL image

```powershell
$env:MYSQL_CONTRACT_IMAGE='mysql:8.4'
```

## Run full tests with HTML coverage

```powershell
uv run pytest --run-mysql-isolated --cov=src --cov-report=html
```
