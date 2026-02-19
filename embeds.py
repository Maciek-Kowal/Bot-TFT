import aiohttp
import asyncio
import urllib.parse
import json
import sys

# ==========================================
RIOT_API_KEY = "RGAPI-d14bd451-243e-428e-8d51-9ecc82628406"
TARGET_NAME = "BlackMati"
TARGET_TAG = "NoWay"


# ==========================================

async def get_id_from_live_game():
    headers = {"X-Riot-Token": RIOT_API_KEY.strip()}
    print(f"🔴 SKANOWANIE AKTYWNEJ GRY DLA: {TARGET_NAME}#{TARGET_TAG}")

    async with aiohttp.ClientSession() as session:
        # 1. PUUID
        url_acc = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(TARGET_NAME)}/{urllib.parse.quote(TARGET_TAG)}"
        async with session.get(url_acc, headers=headers) as r:
            if r.status != 200:
                print(f"❌ Błąd konta: {r.status}")
                return
            data = await r.json()
            puuid = data['puuid']
            print(f"✅ PUUID: {puuid}")

        # 2. SPECTATOR V5 (EUNE)
        # To zapytanie omija zepsute profile i historię. Pyta wprost serwer gry.
        url_spec = f"https://eun1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"

        async with session.get(url_spec, headers=headers) as r:
            if r.status == 404:
                print("\n❌ GRACZ NIE JEST W GRZE.")
                print("   Aby zdobyć ID, ten gracz musi wejść do meczu (ekran ładowania).")
                print("   Jak wejdzie - uruchom ten skrypt ponownie.")
                return
            elif r.status != 200:
                print(f"\n❌ Błąd Spectatora: {r.status}")
                return

            print("\n✅ POŁĄCZONO Z MECZEM NA ŻYWO!")
            game_data = await r.json()

            # Szukamy ID w danych na żywo
            for p in game_data['participants']:
                if p['puuid'] == puuid:
                    real_id = p.get('summonerId')

                    if real_id:
                        print("\n" + "=" * 50)
                        print("🎉 ZNALAZŁEM ID! TO JEST TO!")
                        print("=" * 50)
                        print(f"{real_id}")
                        print("=" * 50)

                        # Test czy to ID działa w rangach
                        print("🧪 Sprawdzam czy to ID pokazuje rangę...")
                        url_rank = f"https://eun1.api.riotgames.com/tft/league/v1/entries/by-summoner/{real_id}"
                        async with session.get(url_rank, headers=headers) as rr:
                            if rr.status == 200:
                                print("✅ TAK! Rangi są dostępne.")
                                print(f"👉 WPISZ W BOCIE: /force_id {TARGET_NAME}#{TARGET_TAG} {real_id}")
                            else:
                                print(f"⚠️ ID jest poprawne, ale endpoint rang zwrócił {rr.status}.")
                    else:
                        print("❌ Nawet Spectator ukrył ID. To konto jest niemożliwe do śledzenia.")
                    return


if __name__ == "__main__":
    if "RGAPI" not in RIOT_API_KEY:
        print("❌ Uzupełnij klucz!")
    else:
        asyncio.run(get_id_from_live_game())