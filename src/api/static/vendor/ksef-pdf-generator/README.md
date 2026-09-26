# ksef-pdf-generator (MF / CIRFMF)

Oficjalna biblioteka Ministerstwa Finansów do wizualizacji PDF faktur KSeF
(FA(1), FA(2), FA(3), FA_RR, PEF) i UPO – ta sama, której używa aplikacja KSeF.

- Źródło: https://github.com/CIRFMF/ksef-pdf-generator
- Wersja: tag `1.1.40`, commit `f59fc4e2addcf42c74b1674e7c1d534085bc3a84`
- Licencja: MIT (plik `LICENSE`)
- Plik: `ksef-fe-invoice-converter.umd.js` = `dist/ksef-fe-invoice-converter.umd.cjs`
  (samowystarczalny – pdfmake, czcionki i tłumaczenia w środku, bez sieci).
  Globalnie: `window["ksef-fe-invoice-converter"].generateInvoice(file, additionalData, "blob")`.

Biblioteka nie jest publikowana w npm, więc budujemy ją sami (Node tylko w
jednorazowym kontenerze):

```sh
docker run --rm -v "$PWD:/out" node:22-slim sh -c '
  apt-get update -qq && apt-get install -y -qq git &&
  git clone -q https://github.com/CIRFMF/ksef-pdf-generator.git /repo && cd /repo &&
  git checkout -q <TAG> && npm ci && npm run build &&
  cp dist/ksef-fe-invoice-converter.umd.cjs /out/ksef-fe-invoice-converter.umd.js'
```

Po podmianie pliku zaktualizuj wersję i commit powyżej.
