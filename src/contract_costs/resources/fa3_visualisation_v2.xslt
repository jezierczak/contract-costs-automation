<xsl:stylesheet
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:k="http://crd.gov.pl/wzor/2025/06/25/13775/"


>


<xsl:output method="html" indent="yes" encoding="UTF-8"/>

<!-- ===================== -->
<!-- 🔹 PAYMENT METHOD -->
<!-- ===================== -->
<xsl:template name="paymentMethod">
    <xsl:param name="code"/>

    <xsl:choose>
        <xsl:when test="$code = '1'">Gotówka</xsl:when>
        <xsl:when test="$code = '2'">Karta</xsl:when>
        <xsl:when test="$code = '3'">Bon</xsl:when>
        <xsl:when test="$code = '4'">Czek</xsl:when>
        <xsl:when test="$code = '5'">Kredyt</xsl:when>
        <xsl:when test="$code = '6'">Przelew</xsl:when>
        <xsl:when test="$code = '7'">BLIK</xsl:when>
        <xsl:otherwise>Inna</xsl:otherwise>
    </xsl:choose>
</xsl:template>

<!-- ===================== -->
<!-- 🔹 IBAN FORMAT -->
<!-- ===================== -->
<xsl:template name="formatIBAN">
    <xsl:param name="iban"/>

    <xsl:variable name="clean" select="translate($iban, ' ', '')"/>

    <xsl:value-of select="substring($clean,1,2)"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="substring($clean,3,4)"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="substring($clean,7,4)"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="substring($clean,11,4)"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="substring($clean,15,4)"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="substring($clean,19,4)"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="substring($clean,23)"/>
</xsl:template>

    <xsl:template name="paymentQR">
    <xsl:param name="iban"/>
    <xsl:param name="amount"/>
    <xsl:param name="recipient"/>
    <xsl:param name="title"/>

    <xsl:variable name="cleanIban" select="translate($iban, ' ', '')"/>

<xsl:variable name="data" select="concat(
    'SPD*1.0*ACC:', $cleanIban,
    '*AM:', $amount,
    '*CC:PLN*RN:', translate($recipient, 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ ', 'acelnoszzACELNOSZZ'),
    '*T:', translate($title, ' ', '')
)"/>

   <img>
    <xsl:attribute name="src">
        <xsl:value-of select="concat(
            'https://chart.googleapis.com/chart?chs=200x200&amp;cht=qr&amp;chl=',
            $data
        )"/>
    </xsl:attribute>
</img>
</xsl:template>

<!-- ===================== -->
<!-- 🔹 MAIN -->
<!-- ===================== -->
<xsl:template match="/">

<html>
<head>
<meta charset="UTF-8"/>

<style>
body {
    font-family: Arial, sans-serif;
    font-size: 12px;
    margin: 20px;
    color: #000;
}

h1 {
    font-size: 20px;
    margin-bottom: 10px;
}

.section {
    margin-bottom: 20px;
}

.row {
    display: flex;
    justify-content: space-between;
}

.col {
    width: 48%;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
}

th, td {
    border: 1px solid #999;
    padding: 6px;
}

th {
    background: #f0f0f0;
    font-weight: bold;
}

.right {
    text-align: right;
}

@media print {
    body { margin: 0; }
}
    .section {
    page-break-inside: avoid;
}

table {
    page-break-inside: auto;
}

tr {
    page-break-inside: avoid;
}
</style>

</head>

<body>

<h1>FAKTURA</h1>

<!-- ===================== -->
<!-- HEADER -->
<!-- ===================== -->
<div class="section">
<b>Numer:</b> <xsl:value-of select="//k:Fa/k:P_2"/><br/>
<b>Data wystawienia:</b> <xsl:value-of select="//k:Fa/k:P_1"/><br/>
<b>Data sprzedaży:</b> <xsl:value-of select="//k:Fa/k:P_6"/>
</div>

<!-- ===================== -->
<!-- PODMIOTY -->
<!-- ===================== -->
<div class="section row">

<div class="col">
<b>Nabywca:</b><br/>
<xsl:value-of select="//k:Podmiot2/k:DaneIdentyfikacyjne/k:Nazwa"/><br/>
NIP: <xsl:value-of select="//k:Podmiot2/k:DaneIdentyfikacyjne/k:NIP"/><br/>
<xsl:value-of select="//k:Podmiot2/k:Adres/k:AdresL1"/><br/>
<xsl:value-of select="//k:Podmiot2/k:Adres/k:AdresL2"/>
</div>

<div class="col">
<b>Sprzedawca:</b><br/>
<xsl:value-of select="//k:Podmiot1/k:DaneIdentyfikacyjne/k:Nazwa"/><br/>
NIP: <xsl:value-of select="//k:Podmiot1/k:DaneIdentyfikacyjne/k:NIP"/><br/>
<xsl:value-of select="//k:Podmiot1/k:Adres/k:AdresL1"/><br/>
<xsl:value-of select="//k:Podmiot1/k:Adres/k:AdresL2"/>
</div>

</div>

<!-- ===================== -->
<!-- POZYCJE -->
<!-- ===================== -->
<div class="section">

<table>

<tr>
<th>Lp</th>
<th>Nazwa</th>
<th>Ilość</th>
<th>Jedn.</th>
<th class="right">Cena netto</th>
<th class="right">Netto</th>
<th>VAT</th>
<th class="right">Brutto</th>
</tr>

<xsl:for-each select="//k:FaWiersz">

<xsl:variable name="qty" select="number(k:P_8B)"/>

<!-- NET -->
<xsl:variable name="net">
    <xsl:choose>
        <xsl:when test="string(k:P_11) != ''">
            <xsl:value-of select="number(k:P_11)"/>
        </xsl:when>
        <xsl:when test="string(k:P_11A) != ''">
            <xsl:value-of select="number(k:P_11A)"/>
        </xsl:when>
        <xsl:otherwise>0</xsl:otherwise>
    </xsl:choose>
</xsl:variable>

<!-- VAT -->
<xsl:variable name="vat">
    <xsl:choose>
        <xsl:when test="string(k:P_11Vat) != ''">
            <xsl:value-of select="number(k:P_11Vat)"/>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="$net * (number(k:P_12) div 100)"/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:variable>

<!-- BRUTTO -->
<xsl:variable name="gross" select="$net + $vat"/>

<!-- CENA JEDNOSTKOWA -->
<xsl:variable name="unitNet">
    <xsl:choose>
        <xsl:when test="$qty &gt; 0">
            <xsl:value-of select="$net div $qty"/>
        </xsl:when>
        <xsl:otherwise>0</xsl:otherwise>
    </xsl:choose>
</xsl:variable>

<tr>
<td><xsl:value-of select="position()"/></td>
<td><xsl:value-of select="k:P_7"/></td>
<td><xsl:value-of select="k:P_8B"/></td>
<td><xsl:value-of select="k:P_8A"/></td>

<td class="right">
<xsl:value-of select="format-number(number($unitNet), '0.00')"/>
</td>

<td class="right">
<xsl:value-of select="format-number(number($net), '0.00')"/>
</td>

<td><xsl:value-of select="k:P_12"/>%</td>

<td class="right">
<xsl:value-of select="format-number(number($gross), '0.00')"/>
</td>
</tr>

</xsl:for-each>

</table>

</div>

<!-- ===================== -->
<!-- PODSUMOWANIE -->
<!-- ===================== -->
<div class="section">

<h3>Podsumowanie</h3>

<table>

<tr>
<td>Netto</td>
<td class="right">
<xsl:value-of select="format-number(//k:Fa/k:P_13_1, '0.00')"/>
</td>
</tr>

<tr>
<td>VAT</td>
<td class="right">
<xsl:value-of select="format-number(//k:Fa/k:P_14_1, '0.00')"/>
</td>
</tr>

<tr>
<td><b>Brutto</b></td>
<td class="right">
<b><xsl:value-of select="format-number(//k:Fa/k:P_15, '0.00')"/></b>
</td>
</tr>

</table>

</div>

<!-- ===================== -->
<!-- PŁATNOŚĆ -->
<!-- ===================== -->
<div class="section">

<h3>Płatność</h3>

<table>

<tr>
<td>Kwota do zapłaty</td>
<td class="right">
<xsl:value-of select="//k:Rozliczenie/k:DoZaplaty"/>
</td>
</tr>

<tr>
<td>Termin</td>
<td class="right">
<xsl:value-of select="//k:Platnosc/k:TerminPlatnosci/k:Termin"/>
</td>
</tr>

<tr>
<td>Forma</td>
<td class="right">
<xsl:call-template name="paymentMethod">
    <xsl:with-param name="code" select="//k:Platnosc/k:FormaPlatnosci"/>
</xsl:call-template>
</td>
</tr>

<xsl:if test="//k:Platnosc/k:RachunekBankowy/k:NrRB">
<tr>
<td>Konto</td>
<td class="right">
<xsl:call-template name="formatIBAN">
    <xsl:with-param name="iban" select="//k:Platnosc/k:RachunekBankowy/k:NrRB"/>
</xsl:call-template>
</td>
</tr>
</xsl:if>

</table>
    <xsl:if test="//k:Platnosc/k:RachunekBankowy/k:NrRB">

<div style="margin-top:15px; text-align:center;">

<b>Zeskanuj aby zapłacić</b><br/>

<xsl:call-template name="paymentQR">
    <xsl:with-param name="iban" select="//k:Platnosc/k:RachunekBankowy/k:NrRB"/>
    <xsl:with-param name="amount" select="//k:Rozliczenie/k:DoZaplaty"/>
    <xsl:with-param name="recipient" select="//k:Podmiot1/k:DaneIdentyfikacyjne/k:Nazwa"/>
    <xsl:with-param name="title" select="//k:Fa/k:P_2"/>
</xsl:call-template>

</div>

</xsl:if>

</div>

</body>
</html>

</xsl:template>
</xsl:stylesheet>