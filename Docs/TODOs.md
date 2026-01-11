# 📌 PROJECT CHECKPOINTS & TODO

## 0. ARCHITECTURE (GLOBAL)
- [ ] Utrzymać warstwę: model / repository / service(query) / DTO / adapters
- [ ] Wszystkie CLI i Excel opierać wyłącznie o query + DTO
- [ ] Brak logiki biznesowej w CLI
- [ ] Prepare / Apply jako standardowy workflow

---

## 1. COMPANIES (ITERATION 1)
- [ ] Ujednolicić CompanyQueryService
- [ ] Wspólny CompanyQuery (own / inactive / search)
- [ ] `show companies` wyłącznie przez query service
- [ ] `show companies --search <phrase>`
- [ ] Prepare companies (Excel)
- [ ] Apply companies (Excel)
- [ ] Dropdown `active` w Excel
- [ ] Deactivate zamiast delete
- [ ] DTO jako jedyny output
- [ ] Walidacje przy apply (NIP, type, duplicates)

---

## 2. COST TYPES
- [ ] Edit cost-type
- [ ] Deactivate cost-type (active=false)
- [ ] Block hard delete
- [ ] Show cost-types (jeśli brak)

---

## 3. CONTRACTS
- [ ] Edit contract metadata (CLI)
- [ ] Quick status change (planned / active / cancelled / finished)
- [ ] Edit single cost-node (CLI)
- [ ] Improve prepare contract Excel (UX)
- [ ] Export contract tree to Excel (read-only)
- [ ] Ujednolicić show / prepare / apply pattern
- [ ] DTO dla contracts i cost nodes

---

## 4. COST NODES
- [ ] Cost nodes zawsze kontekstowe względem contract
- [ ] Walidacja: cost_node należy do contract
- [ ] Prepare bez globalnej listy cost nodes
- [ ] Apply z walidacją kontraktu

---

## 5. INVOICES (CORE)
- [ ] Dodać scan filename (tylko nazwa pliku)
- [ ] Jawny invoice kind (COST / REVENUE / FOREIGN / UNKNOWN)
- [ ] Resolver invoice (number + seller identity)
- [ ] Zmienić logikę OWN NOT FOUND (OCR vs Excel)
- [ ] Obsługa faktur przychodowych (REVENUE)
- [ ] Tags na invoices (set[str])
- [ ] Formalny enum workflow statusów
- [ ] Walidacja przejść statusów
- [ ] Processed invoices readonly (z wyjątkami)
- [ ] Prepare / apply for accountant
- [ ] Reopen invoice workflow
- [ ] Prepare unpaid / apply paid

---

## 6. INVOICE QUERY & LISTING
- [ ] Jeden InvoiceQueryService
- [ ] Jeden obiekt InvoiceQuery (filters)
- [ ] Ujednolicić seller summary z main query
- [ ] Listowanie po own company
- [ ] Listowanie po miesiącu
- [ ] CLI i Excel z tych samych DTO
- [ ] Show invoice resolve → lista jeśli nieunikalne

---

## 7. REPORTS
- [ ] Ujednolicić wejściowe query do raportów
- [ ] Rozdzielić query / transform / render
- [ ] Grupowanie: cost_node / cost_type / invoice
- [ ] Eksport Excel (wiele arkuszy – opcjonalnie)
- [ ] Przygotować miejsce pod snapshoty
- [ ] % wykonania (po snapshotach)

---

## 8. BACKLOG / LATER
- [ ] Snapshot model
- [ ] Revenue reports
- [ ] API layer
- [ ] Web UI
- [ ] Permissions / roles
