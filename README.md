# 🧮 Contract Costs Automation

Production-grade backend system for **contract-level cost control**, designed around real-world construction workflows.

The system tracks costs using **hierarchical cost trees**, aggregates financial data from invoices, and produces **deterministic historical snapshots** that can be audited, compared, and exported to Excel.

This is **not an ERP**.  
It is a focused domain system that reflects how construction costs are actually controlled in practice.

---

## 🎯 Problem Statement

In real construction projects:

- costs are controlled **per contract**, not per invoice
- invoices often contain **multiple cost positions**
- costs must be assigned to **specific elements of a cost estimate**
- budgets exist **before** invoices arrive
- Excel is still the primary operational interface

This system bridges the gap between **formal accounting documents** and **practical, budget-aware cost control**.

---

## ✨ Key Features

### 📁 Contract-centric cost control

- Each contract has its own **hierarchical cost structure**
- Arbitrary depth (tree of cost nodes)
- Leaf nodes represent assignable cost positions

### 🧱 Hierarchical cost nodes

- Reflect real cost estimate structures
- Budgets defined per node
- Automatic aggregation from child nodes

### 🧾 Invoice processing

- One invoice → many invoice lines
- Invoice lines assigned to cost nodes
- Designed for Excel-based workflows
- OCR / AI ingestion supported (optional extensions)

### 📸 Historical snapshots (core feature)

- Snapshot = **deterministic financial state of a contract on a given date**
- Snapshots are:
  - idempotent
  - reproducible
  - auditable
- Aggregation flow:

```text
invoice_lines
→ value_snapshots
→ cost_node_snapshots
→ contract_snapshot
```

---

### 📊 Financial aggregation

Each snapshot aggregates:

- NET
- VAT
- GROSS
- NON_DEDUCTIBLE
- REVENUE (based on ValueType.direction)

Derived metrics:

- **SPEND = NET + NON_DEDUCTIBLE**
- **RESULT = DONE − SPEND**

---

### 📄 Excel & CLI reporting

- Identical data model for:
  - CLI output
  - Excel exports
- Cost tree rendered with ASCII indentation
- Budget vs actual vs result
- Designed for auditors, controllers, and investors

---

## 🧠 Core Domain Concepts

| Concept              | Description                          |
|----------------------|--------------------------------------|
| Contract             | Main cost container                  |
| ContractNode         | Hierarchical cost structure (tree)   |
| Invoice              | Financial document                   |
| InvoiceLine          | Single cost position                 |
| ValueType            | COST / REVENUE / INTERNAL            |
| Snapshot             | Historical contract state (per date) |
| ContractNodeSnapshot | Aggregated node values               |
| ValueSnapshot        | Aggregated financial values          |

---

## 🧭 Architecture Principles

- Domain-first design
- Explicit aggregation pipeline
- Deterministic snapshots
- Storage-agnostic core
- CLI and Excel as adapters, not business logic

---

## 🖥️ CLI Usage

Run CLI via:

```bash
uv run python -m contract_costs.cli.main <command>
```

Snapshot-related commands:

```bash
add snapshot <contract>
show snapshots
show snapshot <id|prefix>
show snapshot <id|prefix> --excel
```

Snapshot IDs can be referenced using **unique UUID prefixes** (e.g. first 8 characters).

---

## 📈 Reporting

All reports are snapshot-based.

- CLI renders a hierarchical cost tree
- Excel exports preserve:
  - tree structure
  - indentation
  - formatting
  - financial consistency

Columns include:

- CODE
- BUDGET
- PROG
- DONE
- NET
- NON-DEDUCT
- SPEND
- RESULT
- REV
- NAME

---

## 🧪 Environments

Default environment: **test**

To enable production mode:

```powershell
$env:APP_ENV="prod"
```

Production mode requires explicit confirmation to prevent accidental data modification.

---

## 🚧 Project Status

🟢 **Production use**

Current focus:

- snapshot UX
- Excel exports
- query & aggregation performance
- snapshot comparison & diff (planned)

---

## 💡 Purpose

This project exists as:

- a real-world production system
- a domain-driven backend portfolio
- a pragmatic alternative to ERP-level complexity

---

## 📜 License

MIT
