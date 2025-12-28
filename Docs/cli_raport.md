# 📊 CLI – Raporty (Contract Costs Automation)

Ten dokument opisuje **raporty dostępne w CLI**, sposób ich uruchamiania,
opcje grupowania oraz formaty wyjścia.

---

## ▶️ Uruchamianie raportów

Raporty dostępne są przez główną komendę:

```bash
contract-costs report <type> [options]
```

lub (zalecane):

```bash
uv run python -m contract_costs.cli.main report <type> [options]
```

---

## 📦 Dostępne raporty

---

## 💰 `report costs`

### Opis
Raport kosztów kontraktu oparty o:
- **faktury**
- **pozycje faktur**
- **leaf cost nodes**
- **typy kosztów**

Raport **zawsze grupowany jest per kontrakt**.

---

### Podstawowe użycie

```bash
contract-costs report costs <CONTRACT_CODE | UUID>
```

Przykład:
```bash
contract-costs report costs TAUR
```

---

## 🧩 Grupowanie danych

Domyślnie:
```text
group-by = cost_node
```

Możliwe wartości `--group-by` (wielokrotne):

| Wartość CLI | Znaczenie |
|------------|----------|
| cost_node  | Węzeł kosztów (leaf) |
| cost_type  | Typ kosztu (materiał, robocizna itd.) |
| invoice    | Numer faktury |
| invoice_date | Data faktury |

### Przykłady

#### Koszty per node:
```bash
contract-costs report costs TAUR --group-by cost_node
```

#### Koszty per node + typ kosztu:
```bash
contract-costs report costs TAUR --group-by cost_node cost_type
```

#### Koszty per faktura:
```bash
contract-costs report costs TAUR --group-by invoice
```

---

## 📤 Format wyjścia

### STDOUT (domyślnie)

```bash
contract-costs report costs TAUR
```

Wyświetla tabelę w konsoli.

---

### Excel

```bash
contract-costs report costs TAUR --output excel
```

Plik zapisywany jest do:
```
work_dir/reports/contract_costs_<CONTRACT_CODE>.xlsx
```

---

## 📊 Kolumny raportu (przykładowe)

| Kolumna | Opis |
|-------|------|
| contract_code | Kod kontraktu |
| cost_node_code | Kod węzła kosztu |
| cost_node_name | Nazwa węzła |
| cost_node_budget | Budżet węzła |
| cost_type_code | Typ kosztu |
| net_amount | Koszt netto |
| vat_amount | VAT |
| gross_amount | Brutto |
| non_tax_amount | Koszty nieopodatkowane |
| quantity | Ilość |
| unit | Jednostka |

> ⚠ Raport zawiera **tylko leaf cost nodes**

---

## 🔍 Ograniczenia (aktualne)

✔ tylko aktywne kontrakty  
✔ tylko przypisane pozycje faktur  
✔ tylko leaf cost nodes  
❌ brak filtrów po dacie (planowane)  
❌ brak filtrowania po fakturze (planowane)  

---

## 🚧 Planowane rozszerzenia

- `--invoice <nr>`
- `--date-from / --date-to`
- raport porównania **budżet vs wykonanie**
- snapshot kosztów w czasie
- CSV / PDF

---

## ✅ Status

✔ stabilny  
✔ używany produkcyjnie  
✔ Excel-ready  

