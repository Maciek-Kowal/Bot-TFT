# 📊 Bot Analityczny i Tracker TFT (Discord)

## 📌 O projekcie
Projekt to zaawansowany bot na platformę Discord, stworzony do śledzenia i analizowania danych z meczów **Teamfight Tactics (TFT)** w czasie rzeczywistym. Narzędzie integruje się z **Riot Games API**, pobierając historię meczów, a następnie wykorzystuje bibliotekę **Pillow (PIL)** do dynamicznego generowania profesjonalnych podsumowań graficznych. Bot automatycznie renderuje składy, przedmioty oraz statystyki gracza bezpośrednio na serwerze.

## 🚀 Kluczowe Funkcje
* **Śledzenie w Czasie Rzeczywistym:** Wykorzystanie zadań w tle (`tasks.loop`) do monitorowania kont graczy i automatycznego powiadamiania o nowych meczach.
* **Dynamiczne Generowanie Obrazów:** Własny silnik graficzny oparty na `Pillow`, który tworzy:
    * Sześciokątne ikony cech (traits) z teksturami proceduralnymi.
    * Ramki bohaterów kodowane kolorystycznie według kosztu (rarity).
    * Wizualizację gwiazdek (tier) oraz nakładki nałożonych przedmiotów.
* **Architektura Asynchroniczna:** Budowa oparta na `aiohttp` oraz `discord.py` zapewnia płynną obsługę wielu zapytań jednocześnie bez blokowania bota.
* **Inspekcja Profili:** Komendy debugujące pozwalające na zrzut surowych danych JSON do celów głębokiej analizy danych.

## 🛠️ Technologie
* **Język:** Python 3.10+
* **Integracja API:** aiohttp, Riot Games API (EUN1/EUW1)
* **Wizualizacja:** Pillow (PIL) – zaawansowane operacje na obrazach i rysowanie UI.
* **Interfejs:** Discord.py (Slash Commands).
* **Dane:** JSON, biblioteki pomocnicze (Pandas/Requests).

## ⚙️ Konfiguracja
Bot wykorzystuje zmienne środowiskowe dla zachowania bezpieczeństwa kluczy:
* `DISCORD_TOKEN`: Token autoryzacyjny bota Discord.
* [cite_start]`RIOT_API_KEY`: Klucz API od Riot Games.  [cite: 22-114]
* [cite_start]`GUILD_ID`: ID serwera do synchronizacji komend.  [cite: 26-29, 517-530]

## 📦 Instalacja i Uruchomienie
1. Sklonuj repozytorium.
2. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```
3. Ustaw zmienne środowiskowe (tokeny).

4. Uruchom bota:
 ```bash
   python main.py
 ```