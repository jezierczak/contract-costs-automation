# 📘 CLI – Contract Costs Automation

Ten dokument opisuje wszystkie aktualnie dostępne komendy CLI systemu **Contract Costs Automation** oraz ich przeznaczenie.

---

## ▶️ Uruchamianie CLI

CLI uruchamiane jest przez moduł:

```bash
python -m contract_costs.cli.main <command>
```

lub (zalecane):

```bash
uv run python -m contract_costs.cli.main <command>
```

---

## 📌 Dostępne komendy

---

## 🏗️ `init`

### Opis
Inicjalizuje infrastrukturę aplikacji (workdir).

Tworzy wymagane katalogi:
- katalog roboczy
- katalogi inputów
- katalogi faktur
- katalogi raportów
- logi

### Komenda
```bash
contract-costs init
```

---

## 🏢 `add company`

### Opis
Dodaje nową firmę do systemu (Company).

Obsługiwane role:
- OWNER
- CLIENT
- SUPPLIER
- BUYER
- SELLER

### Komenda
```bash
contract-costs add company
```

---

## ✏️ `edit company`

### Opis
Edycja istniejącej firmy po numerze NIP.

Możliwe zmiany:
- nazwa
- adres
- opis
- konto bankowe
- rola
- status aktywności

### Komenda
```bash
contract-costs edit company
```

---

## 🧱 `add contract`

### Opis
Tworzy nowy kontrakt (metadane).

### Komenda
```bash
contract-costs add contract
```

---

## 🧮 `add cost_type`

### Opis
Dodaje nowy typ kosztu do globalnego słownika.

### Komenda
```bash
contract-costs add cost_type
```

---

## 📤 `showexcel contract`

### Opis
Generuje plik Excel do tworzenia lub edycji struktury kontraktu.

### Warianty

Nowy kontrakt:
```bash
contract-costs showexcel contract
```

Edycja istniejącego:
```bash
contract-costs showexcel contract <CONTRACT_CODE | UUID>
```

---

## 📥 `applyexcel contract`

### Opis
Importuje strukturę kontraktu z Excela.

### Warianty

Nowy kontrakt:
```bash
contract-costs applyexcel contract new
```

Edycja istniejącego:
```bash
contract-costs applyexcel contract <CONTRACT_CODE | UUID>
```

Po przetworzeniu plik Excel trafia do:
```
work_dir/inputs/contracts/processed/
```

---

## 👀 `run`

### Opis
Uruchamia watcher faktur.

Watcher:
- obserwuje katalog `work_dir/invoices/incoming`
- parsuje faktury PDF
- zapisuje dane do bazy
- przenosi pliki do katalogów OWNER lub `failed`

### Komenda
```bash
contract-costs run
```

---

## 🧭 Status

✔ CLI operacyjne  
✔ Excel jako główny interfejs edycji  
✔ Watcher faktur  
✔ MySQL jako storage  
