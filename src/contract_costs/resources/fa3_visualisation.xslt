<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:k="http://crd.gov.pl/wzor/2025/06/25/13775/"
>

<xsl:output method="html" indent="yes" encoding="UTF-8"/>

<xsl:template match="/">

<html>
<head>
<meta charset="UTF-8"/>

<style>
body {
    font-family: Arial, sans-serif;
    font-size: 12px;
}

h1 {
    font-size: 20px;
}

.section {
    margin-bottom: 20px;
}

table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    border: 1px solid #ccc;
    padding: 6px;
}

th {
    background: #f5f5f5;
}

.right {
    text-align: right;
}
</style>

</head>

<body>

<h1>Faktura</h1>

<div class="section">
<b>Numer:</b>
<xsl:value-of select="//k:Fa/k:P_2"/>
<br/>

<b>Data wystawienia:</b>
<xsl:value-of select="//k:Fa/k:P_1"/>
<br/>

<b>Data sprzedaży:</b>
<xsl:value-of select="//k:Fa/k:P_6"/>
</div>


<div class="section">

<h2>Sprzedawca</h2>

<xsl:value-of select="//k:Podmiot1/k:DaneIdentyfikacyjne/k:Nazwa"/>
<br/>

NIP:
<xsl:value-of select="//k:Podmiot1/k:DaneIdentyfikacyjne/k:NIP"/>
<br/>

<xsl:value-of select="//k:Podmiot1/k:Adres/k:AdresL1"/>
<br/>

<xsl:value-of select="//k:Podmiot1/k:Adres/k:AdresL2"/>

</div>


<div class="section">

<h2>Nabywca</h2>

<xsl:value-of select="//k:Podmiot2/k:DaneIdentyfikacyjne/k:Nazwa"/>
<br/>

NIP:
<xsl:value-of select="//k:Podmiot2/k:DaneIdentyfikacyjne/k:NIP"/>
<br/>

<xsl:value-of select="//k:Podmiot2/k:Adres/k:AdresL1"/>
<br/>

<xsl:value-of select="//k:Podmiot2/k:Adres/k:AdresL2"/>

</div>


<div class="section">

<h2>Pozycje</h2>

<table>

<tr>
<th>Lp</th>
<th>Nazwa</th>
<th>Ilość</th>
<th>Jednostka</th>
<th class="right">Netto</th>
<th>VAT</th>
</tr>

<xsl:for-each select="//k:FaWiersz">

<tr>

<td>
<xsl:value-of select="position()"/>
</td>

<td>
<xsl:value-of select="k:P_7"/>
</td>

<td>
<xsl:value-of select="k:P_8B"/>
</td>

<td>
<xsl:value-of select="k:P_8A"/>
</td>

<td class="right">
<xsl:value-of select="k:P_11"/>
</td>

<td>
<xsl:value-of select="k:P_12"/>
</td>

</tr>

</xsl:for-each>

</table>

</div>


<div class="section">

<h2>Podsumowanie</h2>

<table>

<tr>
<td>Netto</td>
<td class="right">
<xsl:value-of select="//k:Fa/k:P_13_1"/>
</td>
</tr>

<tr>
<td>VAT</td>
<td class="right">
<xsl:value-of select="//k:Fa/k:P_14_1"/>
</td>
</tr>

<tr>
<td><b>Brutto</b></td>
<td class="right">
<b>
<xsl:value-of select="//k:Fa/k:P_15"/>
</b>
</td>
</tr>

</table>

</div>

</body>
</html>

</xsl:template>

</xsl:stylesheet>