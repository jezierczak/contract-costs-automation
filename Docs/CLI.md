
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

## 🌍 Środowisko uruchomieniowe (APP_ENV)

Domyślnie aplikacja uruchamia się w **trybie testowym** (`APP_ENV=test`).  
Tryb testowy:
- używa testowej bazy danych
- używa katalogu `.test_work_dir`
- jest bezpieczny do eksperymentów i importów

### 🔁 Przełączenie na tryb produkcyjny

Aby jawnie uruchomić aplikację w trybie **produkcyjnym**, należy ustawić zmienną środowiskową:

**PowerShell (Windows):**
```powershell
$env:APP_ENV="prod"
```

**Linux / macOS (bash / zsh):**
```bash
export APP_ENV=prod
```

Po ustawieniu `APP_ENV=prod`:
- używana jest produkcyjna baza danych
- używany jest katalog `work_dir`
- CLI wymaga potwierdzenia uruchomienia w trybie PROD

⚠️ **Tryb produkcyjny wymaga jawnego potwierdzenia w CLI**

---

## 📌 Dostępne komendy

---

## 🏗️ `init`

### Opis
Inicjalizuje infrastrukturę aplikacji (workdir).

Tworzy:
- katalog roboczy
- katalogi inputów
- katalogi faktur
- katalogi raportów
- katalogi logów

### Komenda
```bash
contract-costs init
```

---

## 🏢 `add company`

### Opis
Dodaje nową firmę do systemu.

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

## 🧮 `add cost-type`

### Opis
Dodaje nowy typ kosztu do globalnego słownika.

### Komenda
```bash
contract-costs add cost-type
```

---

## 📤 `showexcel contract`

### Opis
Generuje plik Excel do tworzenia lub edycji struktury kosztowej kontraktu.

### Warianty
```bash
contract-costs showexcel contract
contract-costs showexcel contract <CONTRACT_CODE | UUID>
```

---

## 📥 `applyexcel contract`

### Opis
Importuje strukturę kontraktu z Excela.

### Warianty
```bash
contract-costs applyexcel contract new
contract-costs applyexcel contract <CONTRACT_CODE | UUID>
```

---

## 📤 `showexcel invoices`

### Opis
Generuje Excel do przypisywania kosztów faktur (NEW, IN_PROGRESS).

### Komenda
```bash
contract-costs showexcel invoices
```

---

## 📥 `applyexcel invoices`

### Opis
Zatwierdza przypisania kosztów faktur z Excela.

### Komenda
```bash
contract-costs applyexcel invoices
```

---

## 📊 `report costs`

### Opis
Generuje raport kosztów dla kontraktu.

### Komenda
```bash
contract-costs report costs <CONTRACT_CODE | UUID>
```

### Grupowanie
```bash
--group-by cost_node cost_type invoice invoice_date
```

### Output
```bash
--output stdout
--output excel
```

---

## 👀 `run`

### Opis
Uruchamia watcher faktur PDF.

### Komenda
```bash
contract-costs run
```

---

## ✅ Status

✔ CLI operacyjne  
✔ Excel jako UI  
✔ Watcher faktur  
✔ MySQL  
✔ Raporty kosztowe  

