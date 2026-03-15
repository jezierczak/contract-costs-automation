Contract Costs – Product Roadmap
Overview

Contract Costs to system zarządzania kosztami kontraktów, dokumentami finansowymi oraz analizą finansową firm.
System integruje:

zarządzanie kontraktami

rozliczanie kosztów

obsługę dokumentów i faktur

analizę finansową firm

automatyczne przypisywanie dokumentów

integrację z AI (OCR + matching)

Docelowo system będzie działał jako SaaS z obsługą wielu organizacji i użytkowników.

Core Modules
Contracts
Contract list improvements

filtrowanie kontraktów według statusu:

active

planned

cancelled

finished

możliwe dodatkowe filtry:

kontrahent

data rozpoczęcia / zakończenia

typ kontraktu

Contract details improvements

przy każdej linii drzewa kosztów dodać przycisk faktury

pokazanie listy faktur dla danego zakresu

obecny modal z podziałem:

material

robocizna

kliknięcie w typ kosztu w modalu → lista faktur z tego zakresu

Contract tree creation from cost estimate

Możliwość utworzenia drzewa kontraktu z pliku kosztorysu.

Proces:

upload kosztorysu (PDF / DOC / XLS)

wysłanie pliku do LLM

LLM generuje strukturę JSON

system tworzy drzewo kontraktu

Dodatkowo:

kosztorys zapisywany jako document powiązany z kontraktem

Counterparties
Counterparty list improvements
Auto cleanup

Worker usuwający kontrahentów bez powiązań:

brak kontraktów

brak faktur

brak rekordów

List improvements

Dodatkowa kolumna:

liczba faktur

Sortowanie:

liczba faktur

nazwa

ostatnia faktura

Own companies

Firmy własne pozostają w tabeli kontrahentów, ponieważ są używane w pickerach.

Counterparty details
Invoice list filters

Filtrowanie faktur:

numer faktury

zakres kwot

kontrakt

Agreements (Umowy)

Moduł zarządzania umowami z kontrahentami.

Funkcje:

lista umów kontrahenta

podgląd umowy

tworzenie umowy

edycja umowy

Architektura:

struktura identyczna jak kontrakt

osobny serwis

minimalne zmiany widoków

Documents
Document list improvements

Obecne filtry:

ready

failed

inne statusy

Nowe filtry:

rok

miesiąc

Document assignment improvements

Możliwość:

odpięcia dokumentu

ponownego przypisania dokumentu

Auto document assignment improvements

Obecne dopasowanie:

numer dokumentu

NIP sprzedawcy

Nowe dopasowanie:

NIP sprzedawcy

kwota całkowita

tolerancja kwoty

Cel:
obsługa przypadków:

faktura zaliczkowa

korekty

zmiana numeru faktury

Manual document assignment improvements

Zmiany:

wykorzystanie tego samego algorytmu matchingu co auto assignment

zamiast dropdowna → modal wyboru rekordu

Records (Invoices)
Main records dashboard

Obecne widoki:

rekordy do przypisania

rekordy do wysłania do księgowej

niezapłacone koszty

niezapłacone przychody

Nowe widoki:

Sent to accounting

Lista rekordów wysłanych do księgowej.

Filtry:

firma

kontrahent

kontrakt

zakres dat

kwoty

Global records view

Widok wszystkich rekordów z pełnym filtrowaniem.

Records requiring attention

Rekordy wymagające interwencji:

brak kontraktu

brak kontrahenta

błędy przetwarzania

Payments
Partial payments support

Zmiana modelu rekordu.

Nowa kolumna:

paid_amount

Nowy modal płatności:

data płatności

kwota

opcja "zapłacono w całości"

Obsługa:

płatności częściowe

dopłaty

Record Form Improvements
Counterparty creation from modal

Możliwość utworzenia kontrahenta z modala wyboru buyer/seller.

Flow:

select → create → auto-select

Node selection modal

Dla:

nodów kontraktu

typów kosztów

Modal z możliwością tworzenia nowych elementów.

Bulk assignment for invoice lines

Masowe przypisywanie:

kontraktu

noda

value type

Opcja:

apply to all
Automatic numbering improvements

Zamiast wpisywania:

ZUS_<Y>_<m>

dropdown wyboru typu numeracji.

Przykłady:

ZUS_2026_03
KSIĘGOWA_2026_03
LEASING_2026_03
Agreements assignment

Logika:

jeśli kontrahent nie ma umów → brak pola

jedna umowa → auto przypisanie

wiele umów → wybór

Node umowy:
ten sam modal co kontrakty.

Invoice Details View
More counterparty data

Wyświetlanie pełnych danych:

nazwa

NIP

adres

konto bankowe

Łatwe kopiowanie danych.

Copy values

Możliwość kopiowania:

netto

VAT

brutto

suma faktury

Invoice Lines Validation

Podsumowanie pozycji faktury:

suma netto

suma VAT

suma brutto

Porównanie z dokumentem źródłowym.

Own Companies Finance
Financial dashboard

Widok wyników finansowych:

rok

miesiące

historia

Kliknięcie → modal z podziałem kosztów.

Invoice drill down

Kliknięcie typu kosztu → lista faktur.

Invoice list filters

klient

NIP

tytuł faktury

kontrakt

Own company management

Przeniesienie tworzenia firmy z kontrahentów do dashboardu.

Modal:

dane firmy

edycja

Current financial state

Sekcja:

nadchodzące płatności

zaległe płatności

koszty bieżącego miesiąca

Recurring payments

Obsługa:

ZUS

księgowość

kredyty

leasing

Parametry:

częstotliwość

data generowania

termin płatności

kwota

zmienna / stała

Dictionaries

Obecny:

value_types

Możliwe rozszerzenia:

payment_methods

units

Users
User invitations

Core istnieje, brak widoków.

Funkcje:

zapraszanie użytkowników

akceptacja zaproszeń

User profile

Panel użytkownika:

zmiana nazwy wyświetlanej

zmiana hasła

metadane

User activity

Pole:

last_activity
Sessions

Zamiast fixed 12h:

sesja zależna od aktywności.

Authorization

Wstępny model:

Owner

Admin

User

Możliwe rozszerzenie:

uprawnienia per moduł.

AI Features

OCR dokumentów

automatyczne przypisywanie faktur

dopasowanie rekordów

import kosztorysów

SaaS & Deployment
Subscription model

Proponowane plany:

Free / Trial

Basic

Pro

Enterprise

Feature gating

Kontrola dostępu do funkcji:

liczba dokumentów

liczba kontraktów

funkcje AI

liczba użytkowników

Deployment

przygotowanie obrazu Docker

konfiguracja serwera

release systemu

Long-term Features
Global dashboard

Dashboard całego systemu:

koszty

kontrakty

faktury

aktywność

Podsumowanie

System obejmuje główne obszary:

Contracts

Counterparties

Agreements

Documents

Records

Finance

Users

AI processing

SaaS monetization