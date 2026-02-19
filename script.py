import json
import aiofiles
import os
import asyncio

DATA_FILE = "tft_data.json"

# Struktura początkowa, jeśli plik nie istnieje
DEFAULT_DATA = {
    "tracked_players": []
}


async def init_pool():
    """Sprawdza czy plik istnieje, jak nie to go tworzy."""
    if not os.path.exists(DATA_FILE):
        print(f"⚠️ [JSON] Tworzenie nowego pliku bazy: {DATA_FILE}")
        async with aiofiles.open(DATA_FILE, mode='w') as f:
            await f.write(json.dumps(DEFAULT_DATA, indent=4))
    else:
        print(f"✅ [JSON] Baza danych znaleziona: {DATA_FILE}")


async def load_data():
    """Wczytuje dane z pliku."""
    try:
        async with aiofiles.open(DATA_FILE, mode='r') as f:
            content = await f.read()
            return json.loads(content)
    except Exception as e:
        print(f"❌ Błąd odczytu JSON: {e}")
        return DEFAULT_DATA


async def save_data(data):
    """Zapisuje dane do pliku."""
    try:
        async with aiofiles.open(DATA_FILE, mode='w') as f:
            await f.write(json.dumps(data, indent=4))
    except Exception as e:
        print(f"❌ Błąd zapisu JSON: {e}")


# --- FUNKCJE DLA BOTA ---

async def get_tracked_players():
    """Zwraca listę graczy do pętli sprawdzającej mecze."""
    data = await load_data()
    # Formatujemy tak, żeby pasował do Twojego bota (lista słowników)
    return data.get("tracked_players", [])


async def add_player(puuid, name, region, channel_id, summoner_id):
    """Dodaje nowego gracza."""
    data = await load_data()
    players = data["tracked_players"]

    # Sprawdź czy już istnieje
    if any(p['puuid'] == puuid for p in players):
        return False  # Gracz już jest

    new_player = {
        "puuid": puuid,
        "name": name,  # Zmieniłem klucz na 'name' dla wygody, w SQL było summoner_name
        "region": region,
        "last_match_id": "",
        "ch": int(channel_id),  # Skracam nazwę klucza dla wygody
        "summoner_id": summoner_id
    }

    players.append(new_player)
    await save_data(data)
    return True


async def update_last_match(puuid, match_id):
    """Aktualizuje ostatni mecz gracza."""
    data = await load_data()
    changed = False
    for p in data["tracked_players"]:
        if p['puuid'] == puuid:
            p['last_match_id'] = match_id
            changed = True
            break

    if changed:
        await save_data(data)