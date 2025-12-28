# 🧮 Contract Costs Automation

Backend system for contract-level cost control, designed around real-world construction and investment workflows.

The application automates invoice processing, manages hierarchical cost structures, and generates **budget-aware Excel reports** for precise cost tracking.

This is **not an ERP**.  
It is a focused domain system built to reflect how costs are actually controlled on construction projects.

---

## 🎯 Problem Statement

In real projects:

- costs are tracked **per contract**, not per invoice
- invoices often contain **multiple cost positions**
- costs must be assigned to **specific elements of the cost estimate**
- budgets exist **before** invoices arrive
- Excel is still the primary operational tool

This system bridges the gap between **formal accounting documents** and **practical cost control**.

---

## ✨ Key Features

### 📁 Contract-centric cost tracking
- Each contract has its own **hierarchical cost structure**
- Arbitrary depth (cost nodes can be nested freely)
- Leaf nodes represent assignable cost positions

### 🧱 Hierarchical cost nodes
- Reflect real cost estimate structures
- Budgets defined per node
- Automatic aggregation from child nodes

### 🧾 Invoice processing
- One invoice → many cost positions
- Manual assignment via Excel
- Automated ingestion pipeline ready (OCR / AI supported)

### 📊 Budget-aware reporting
- Planned vs actual costs
- Aggregation by:
  - contract
  - cost node
  - cost type
  - invoice
- Export to Excel or CLI output

### 📄 Excel as workflow interface
- Excel used intentionally as a **UI**, not as storage
- Clear separation between:
  - input Excel files
  - processed history
  - generated reports

---

## 🧠 Core Domain Concepts

| Concept | Description |
|------|------------|
| Contract | Main cost container |
| Cost Node | Hierarchical cost structure (tree) |
| Cost Type | Global cost classification |
| Invoice | Financial document |
| Invoice Line | Single cost position |
| Budget | Planned cost assigned to nodes |
| Report | Aggregated cost view |

---

## 🧭 Architecture Principles

- Domain-first design
- Explicit workflows
- Clean separation of concerns
- Storage-agnostic core
- Excel and CLI as adapters, not business logic

---

## 🖥️ CLI Usage

Run CLI via:

```bash
uv run python -m contract_costs.cli.main <command>
```

Main command groups:
- init
- add
- showexcel
- applyexcel
- run
- report

---

## 📈 Reporting

Reports are generated using Pandas and can be:
- displayed in CLI
- exported to Excel
- grouped dynamically

Example:

```bash
contract-costs report costs TAUR --group-by cost_node cost_type --output excel
```

---

## 🧪 Environments

Default environment: **test**

To enable production mode:

```powershell
$env:APP_ENV="prod"
```

Production requires explicit confirmation to prevent accidental data changes.

---

## 🚧 Project Status

🟡 Active development

Current focus:
- reporting & aggregation
- Excel workflows
- domain robustness

Planned:
- advanced filtering
- performance optimizations
- AI-assisted invoice parsing
- historical snapshots

---

## 💡 Purpose

This project was built as:
- a real-world backend system
- a clean domain-driven portfolio project
- a practical alternative to ERP-level complexity

---

## 📜 License

MIT
