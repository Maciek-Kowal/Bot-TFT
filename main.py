import discord
from discord import app_commands
from discord.ext import commands, tasks
import script as database
import aiohttp
import urllib.parse
import asyncio
import json
import os
import re
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO, StringIO

# ==========================================
# KONFIGURACJA
# ==========================================

RIOT_API_KEY = os.environ.get("RIOT_API_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

try:
    GUILD_ID = int(os.environ.get("GUILD_ID", 0))
except:
    GUILD_ID = 0

PLATFORM_URL = "https://eun1.api.riotgames.com"
ROUTING_URL = "https://europe.api.riotgames.com"

DATA_ROOTS = [
    "https://raw.communitydragon.org/latest/game/assets",
    "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets"
]

# ==========================================
# SŁOWNIKI I MAPOWANIA
# ==========================================

BILGEWATER_FILENAME_MAP = {
    "TFT16_Item_Bilgewater_DeadmansDagger": "tt16_item_bilgewater_deadmansdagger",
    "TFT16_Item_Bilgewater_BilgeratCutlass": "tft16_item_bilgewater_bilgeratcutlass",
    "TFT16_Item_Bilgewater_Cutlass": "tft16_item_bilgewater_bilgeratcutlass",
    "TFT16_Item_Bilgewater_BlackmarketExplosives": "tft16_item_bilgewater_blackmarketexplosives",
    "TFT16_Item_Bilgewater_DreadwayCannon": "tft16_item_bilgewater_dreadwaycannon",
    "TFT16_Item_Bilgewater_FreebootersFrock": "tft16_item_bilgewater_freebootersfrock",
    "TFT16_Item_Bilgewater_Barknuckles": "tft16_item_bilgewater_freebootersfrock",
    "TFT16_Item_Bilgewater_HauntedSpyglass": "tft16_item_bilgewater_hauntedspyglass",
    "TFT16_Item_Bilgewater_Spyglass": "tft16_item_bilgewater_hauntedspyglass",
    "TFT16_Item_Bilgewater_JollyRoger": "tft16_item_bilgewater_jollyroger",
    "TFT16_Item_Bilgewater_LuckyEyepatch": "tft16_item_luckydubloon",
    "TFT16_Item_PileOfCitrus": "tft16_item_pileofcitrus"
}

EMBLEM_MAPPING = {
    "TFT16_Item_ArcanistEmblemItem": "tft16_emblem_arcanist",
    "TFT16_Item_BilgewaterEmblemItem": "tft16_emblem_bilgewater",
    "TFT16_Item_BruiserEmblemItem": "tft16_emblem_bruiser",
    "TFT16_Item_DefenderEmblemItem": "tft16_emblem_defender",
    "TFT16_Item_DemaciaEmblemItem": "tft16_emblem_demacia",
    "TFT16_Item_DisruptorEmblemItem": "tft16_emblem_disruptor",
    "TFT16_Item_FreljordEmblemItem": "tft16_emblem_freljord",
    "TFT16_Item_GunslingerEmblemItem": "tft16_emblem_gunslinger",
    "TFT16_Item_InvokerEmblemItem": "tft16_emblem_invoker",
    "TFT16_Item_IoniaEmblemItem": "tft16_emblem_ionia",
    "TFT16_Item_IxtalEmblemItem": "tft16_emblem_ixtal",
    "TFT16_Item_JuggernautEmblemItem": "tft16_emblem_juggernaut",
    "TFT16_Item_LongshotEmblemItem": "tft16_emblem_longshot",
    "TFT16_Item_NoxusEmblemItem": "tft16_emblem_noxus",
    "TFT16_Item_PiltoverEmblemItem": "tft16_emblem_piltover",
    "TFT16_Item_QuickstrikerEmblemItem": "tft16_emblem_quickstriker",
    "TFT16_Item_SlayerEmblemItem": "tft16_emblem_slayer",
    "TFT16_Item_VanquisherEmblemItem": "tft16_emblem_vanquisher",
    "TFT16_Item_VoidEmblemItem": "tft16_emblem_void",
    "TFT16_Item_WardenEmblemItem": "tft16_emblem_warden",
    "TFT16_Item_YordleEmblemItem": "tft16_emblem_yordle",
    "TFT16_Item_ZaunEmblemItem": "tft16_emblem_zaun",
    "TFT16_Item_ArcanistEmblem": "tft16_emblem_arcanist",
    "TFT16_Item_BilgewaterEmblem": "tft16_emblem_bilgewater",
    "TFT16_Item_BruiserEmblem": "tft16_emblem_bruiser",
    "TFT16_Item_DefenderEmblem": "tft16_emblem_defender",
    "TFT16_Item_DemaciaEmblem": "tft16_emblem_demacia",
    "TFT16_Item_DisruptorEmblem": "tft16_emblem_disruptor",
    "TFT16_Item_FreljordEmblem": "tft16_emblem_freljord",
    "TFT16_Item_GunslingerEmblem": "tft16_emblem_gunslinger",
    "TFT16_Item_InvokerEmblem": "tft16_emblem_invoker",
    "TFT16_Item_IoniaEmblem": "tft16_emblem_ionia",
    "TFT16_Item_IxtalEmblem": "tft16_emblem_ixtal",
    "TFT16_Item_JuggernautEmblem": "tft16_emblem_juggernaut",
    "TFT16_Item_LongshotEmblem": "tft16_emblem_longshot",
    "TFT16_Item_NoxusEmblem": "tft16_emblem_noxus",
    "TFT16_Item_PiltoverEmblem": "tft16_emblem_piltover",
    "TFT16_Item_QuickstrikerEmblem": "tft16_emblem_quickstriker",
    "TFT16_Item_SlayerEmblem": "tft16_emblem_slayer",
    "TFT16_Item_VanquisherEmblem": "tft16_emblem_vanquisher",
    "TFT16_Item_VoidEmblem": "tft16_emblem_void",
    "TFT16_Item_WardenEmblem": "tft16_emblem_warden",
    "TFT16_Item_YordleEmblem": "tft16_emblem_yordle",
    "TFT16_Item_ZaunEmblem": "tft16_emblem_zaun"
}

ITEM_EXCEPTIONS = {
    "tft_item_artifact_navoriflickerblades": "tft_item_artifact_navoriflickerplade.tft_tft14_5.png",
    "tft_item_navoriflickerblades": "tft_item_artifact_navoriflickerplade.tft_tft14_5.png",
    "tft_item_statikkshiv": "tft_item_voidstaff.tft_tft14_5.png",
    "tft_item_runaanshurricane": "tft_item_krakenslayer.tft_tft14_5.png",
    "tft_item_redemption": "tft_item_spiritvisagerr.tft_tft14_5.png",
}

ITEM_SUFFIXES = [".tft_set13.png", ".tft_set16.png", ".tft_tft14_5.png", ".tft_set15.png", ".png"]

QUEUE_TYPES = {
    1090: "Normal", 1100: "Ranked", 1130: "Hyper Roll", 1160: "Double Up",
    1170: "Fortune's Favor", 110: "Ranked (TFT)"
}

PLACE_COLORS = {
    1: (255, 215, 0), 2: (46, 204, 113), 3: (46, 204, 113), 4: (46, 204, 113),
    5: (149, 165, 166), 6: (149, 165, 166), 7: (149, 165, 166), 8: (231, 76, 60)
}

# --- KOLORY RAMEK (POPRAWIONE) ---
COST_COLORS = {
    0: (128, 128, 128),
    1: (128, 128, 128),  # 1 Cost (Szary)
    2: (21, 142, 21),  # 2 Cost (Zielony)
    3: (26, 116, 226),  # 3 Cost (Niebieski)
    4: (180, 0, 180),  # 4 Cost (FIOLETOWY)
    5: (255, 215, 0),  # 5 Cost (ZŁOTY)
    6: (255, 215, 0),
    8: (255, 215, 0)
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.session = None


# ==========================================
# FUNKCJE POMOCNICZE
# ==========================================

async def riot_request(url):
    if not RIOT_API_KEY:
        print("❌ BŁĄD: Brak RIOT_API_KEY!")
        return None
    h = {"X-Riot-Token": RIOT_API_KEY}
    for _ in range(3):
        try:
            async with bot.session.get(url, headers=h) as r:
                if r.status == 200: return await r.json()
                if r.status == 429:
                    await asyncio.sleep(int(r.headers.get("Retry-After", 1)) + 1)
                    continue
                return None
        except:
            return None
    return None


def get_tft_stage(last_round):
    if last_round <= 3: return f"1-{last_round}"
    adj = last_round - 3
    stage = ((adj - 1) // 7) + 2
    round_in_stage = ((adj - 1) % 7) + 1
    return f"{stage}-{round_in_stage}"


def normalize_trait_name(text):
    # Prosta normalizacja: usuwamy TFT16_ i wszystkie znaki specjalne
    clean = re.sub(r'^(TFT\d+_|Set\d+_)', '', text, flags=re.IGNORECASE)
    clean = clean.lower()
    return re.sub(r'[^a-z0-9]', '', clean)


# --- GRAFIKA ---

def create_prismatic_texture(size):
    img = Image.new('RGB', (size, size))
    pixels = img.load()
    for x in range(size):
        for y in range(size):
            r = int(225 + 30 * math.sin(x / 8.0 + y / 10.0))
            g = int(235 + 20 * math.sin(x / 10.0 - y / 12.0))
            b = int(240 + 15 * math.sin(-x / 12.0 + y / 8.0))
            pixels[x, y] = (min(255, r), min(255, g), min(255, b))
    return img


def create_hexagon_image(size, color_or_texture):
    mask = Image.new('L', (size, size), 0)
    draw_mask = ImageDraw.Draw(mask)
    center, radius = (size / 2, size / 2), size / 2 - 2
    pts = [(center[0] + radius * math.cos(math.radians(60 * i + 30)),
            center[1] + radius * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    draw_mask.polygon(pts, fill=255)

    if isinstance(color_or_texture, Image.Image):
        fill = color_or_texture.resize((size, size))
    else:
        fill = Image.new('RGBA', (size, size), color_or_texture)

    res = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    res.paste(fill, (0, 0), mask)
    ImageDraw.Draw(res).polygon(pts, outline=(20, 20, 20), width=3)
    return res


def recolor_icon_black(img):
    if img.mode != 'RGBA': img = img.convert('RGBA')
    a = img.split()[3]
    return Image.merge('RGBA',
                       (Image.new('L', img.size, 0), Image.new('L', img.size, 0), Image.new('L', img.size, 0), a))


async def fetch_image(urls, size=None):
    for url in urls:
        try:
            async with bot.session.get(url) as resp:
                if resp.status == 200:
                    img = Image.open(BytesIO(await resp.read())).convert("RGBA")
                    if size: img = img.resize(size)
                    return img
        except:
            continue
    return None


def draw_stars(draw, x, y, count, size=12):
    gap = 3
    total_width = (count * size) + ((count - 1) * gap)
    start_x = x + (80 - total_width) // 2
    for i in range(count):
        draw.ellipse([start_x + i * (size + gap), y, start_x + i * (size + gap) + size, y + size], fill=(255, 215, 0),
                     outline=(0, 0, 0))


# ==========================================
# GŁÓWNA LOGIKA GENEROWANIA OBRAZKA
# ==========================================

async def generate_full_summary(placement, augments, traits, units, companion_data):
    HEX_SIZE, ICON_SIZE, TRAIT_SPACING = 75, 45, 85

    LOCAL_TRAIT_COLORS = {
        0: (40, 40, 40),
        1: (165, 113, 100),
        2: (176, 195, 217),
        3: (255, 100, 20),
        4: (255, 215, 0)
    }

    # 1. MINI LEGENDA
    companion_img = None
    if companion_data:
        try:
            species = companion_data.get('species', 'Avatar')
            name_clean = species.lower()
            if name_clean.startswith("pet"):
                name_clean = name_clean[3:]
            if name_clean == "councillor": name_clean = "tacticiancouncillor"

            base_loot = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/loot/companions/{name_clean}"
            urls = []

            if "chibi" in name_clean:
                chibi_core_name = name_clean.replace('chibi', '', 1)
                urls.append(f"{base_loot}/loot_{name_clean}_base_classic_tier1.chibi_{chibi_core_name}_base.png")

            urls.append(f"{base_loot}/loot_{name_clean}_base_classic_tier3.png")
            urls.append(f"{base_loot}/loot_{name_clean}_base_base_tier1.ll_{name_clean}_base.png")
            urls.append(f"{base_loot}/loot_{name_clean}_base_base_tier1.png")
            urls.append(f"{base_loot}/loot_{name_clean}_base_tier1.png")
            urls.append(f"{base_loot}/loot_{name_clean}_base_classic_tier1.png")

            companion_img = await fetch_image(urls, (130, 130))
        except Exception as e:
            print(f"Błąd przy pobieraniu legendy: {e}")
            companion_img = None

    # 2. CECHY
    trait_imgs = []
    for t in sorted(traits, key=lambda t: (t['style'], t['num_units']), reverse=True):
        if t['style'] > 0:
            norm = normalize_trait_name(t['name'])
            urls = []

            # === FIX: Tylko dla Bilgewater dodajemy wersję "9_" ===
            if norm == "bilgewater":
                for root in DATA_ROOTS:
                    urls.append(f"{root}/ux/traiticons/trait_icon_9_bilgewater.png")

            # Dla wszystkich (w tym Bilgewater jako fallback, i reszty jak Shadow Isles)
            for root in DATA_ROOTS:
                urls.extend([
                    f"{root}/ux/traiticons/trait_icon_16_{norm}.tft_set16.png",
                    f"{root}/ux/traiticons/trait_icon_16_{norm}.png",
                    f"{root}/ux/traiticons/trait_icon_{norm}.png",
                    f"{root}/maps/tft/icons/traits/trait_icon_{norm}.png"
                ])

            mask = await fetch_image(urls, (ICON_SIZE, ICON_SIZE))
            if mask:
                if t['style'] >= 5:
                    bg = create_prismatic_texture(HEX_SIZE)
                else:
                    bg = LOCAL_TRAIT_COLORS.get(t['style'], (50, 50, 50))

                hex_badge = create_hexagon_image(HEX_SIZE, bg)
                black_icon = recolor_icon_black(mask)
                hex_badge.paste(black_icon, ((HEX_SIZE - ICON_SIZE) // 2, (HEX_SIZE - ICON_SIZE) // 2), black_icon)
                trait_imgs.append(hex_badge)

    # 3. JEDNOSTKI I PRZEDMIOTY (Z POPRAWKĄ RAMEK I BEZ +1)
    unit_imgs = []
    for u in sorted(units, key=lambda u: (u['tier'], u['rarity']), reverse=True):
        raw_id = u['character_id'].lower()
        clean_name = re.sub(r'^(tft\d+_|set\d+_|skin\d+_)', '', raw_id)
        target_name = f"tft16_{clean_name}"
        urls = []
        for root in DATA_ROOTS:
            urls.extend([
                f"{root}/characters/{target_name}/hud/{target_name}_square.tft_set16.png",
                f"{root}/characters/{target_name}/hud/{target_name}_square.png",
                f"{root}/characters/{clean_name}/hud/{clean_name}_square.png"
            ])
        base_img = await fetch_image(urls, (80, 80))
        if base_img:
            # FIX: Usuwamy +1
            cost = u['rarity'] if u['rarity'] < 8 else 5

            final = Image.new('RGBA', (84, 130), (0, 0, 0, 0))
            frame = Image.new('RGBA', (84, 90), COST_COLORS.get(cost, (128, 128, 128)))
            frame.paste(base_img, (2, 2))
            final.paste(frame, (0, 35))
            d = ImageDraw.Draw(final)
            d.rectangle([0, 110, 84, 130], fill=(10, 10, 10))
            draw_stars(d, 2, 115, u['tier'])

            items = u.get('itemNames', [])
            item_size = 24
            items_width = len(items) * item_size
            item_start_x = (84 - items_width) // 2

            for idx, item_raw in enumerate(items):
                full_name_lower = item_raw.lower()
                i_urls = []
                mapped_filename = BILGEWATER_FILENAME_MAP.get(item_raw)
                if not mapped_filename:
                    for api_key, file_val in BILGEWATER_FILENAME_MAP.items():
                        if api_key.lower() == full_name_lower:
                            mapped_filename = file_val
                            break
                if mapped_filename:
                    url = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/maps/particles/tft/item_icons/tft16/{mapped_filename}.tft_set16.png"
                    i_urls.append(url)
                elif "emblem" in full_name_lower:
                    mapped_name = EMBLEM_MAPPING.get(item_raw)
                    if not mapped_name:
                        mapped_name = item_raw.lower().replace("_item_", "_").replace("emblemitem", "emblem")
                    if mapped_name:
                        url = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/maps/particles/tft/item_icons/traits/spatula/set16/{mapped_name}.tft_set16.png"
                        i_urls.append(url)
                if not i_urls:
                    if full_name_lower in ITEM_EXCEPTIONS:
                        specific_file = ITEM_EXCEPTIONS[full_name_lower]
                        for root in DATA_ROOTS:
                            i_urls.append(f"{root}/maps/tft/icons/items/hexcore/{specific_file}")
                            i_urls.append(f"{root}/maps/tft/icons/items/{specific_file}")
                    else:
                        for root in DATA_ROOTS:
                            base_i = f"{root}/maps/tft/icons/items"
                            hex_i = f"{root}/maps/tft/icons/items/hexcore"
                            emblem_i = f"{root}/maps/tft/icons/items/emblems"
                            for s in ITEM_SUFFIXES:
                                i_urls.append(f"{hex_i}/{full_name_lower}{s}")
                                i_urls.append(f"{base_i}/{full_name_lower}{s}")
                                i_urls.append(f"{emblem_i}/{full_name_lower}{s}")

                item_icon = await fetch_image(i_urls, (item_size, item_size))
                if item_icon:
                    final.paste(item_icon, (item_start_x + idx * item_size, 5), item_icon)

            unit_imgs.append(final)

    # 4. SKŁADANIE (FONT)
    width = 900
    total_height = 130 + (HEX_SIZE + 20 if trait_imgs else 0) + 150 + 20
    canvas = Image.new('RGBA', (width, total_height), (30, 33, 36))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([30, 20, 130, 100], radius=15, fill=PLACE_COLORS.get(placement, (100, 100, 100)))

    try:
        if os.path.exists("font.ttf"):
            font = ImageFont.truetype("font.ttf", 70)
        else:
            font = ImageFont.truetype("arial.ttf", 70)
    except:
        font = ImageFont.load_default()

    txt = f"#{placement}"
    bbox = font.getbbox(txt)
    draw.text((30 + (100 - (bbox[2] - bbox[0])) // 2, 25), txt, font=font, fill=(255, 255, 255), stroke_width=3,
              stroke_fill=(0, 0, 0))

    if companion_img:
        canvas.paste(companion_img, (width - 140, 10), companion_img)

    curr_y = 130
    if trait_imgs:
        sx = (width - len(trait_imgs[:10]) * TRAIT_SPACING) // 2
        for i, img in enumerate(trait_imgs[:10]):
            canvas.paste(img, (sx + i * TRAIT_SPACING, curr_y), img)
        curr_y += HEX_SIZE + 20

    if unit_imgs:
        units_to_draw = unit_imgs[:10]
        sx = (width - (len(units_to_draw) * 90)) // 2
        if sx < 0: sx = 0
        for i, img in enumerate(units_to_draw):
            canvas.paste(img, (sx + i * 90, curr_y), img)

    buf = BytesIO()
    canvas.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename="summary.png")


async def create_full_report(name, match_data, puuid):
    info = match_data['info']
    p = next((x for x in info['participants'] if x['puuid'] == puuid), None)
    if not p: return None, None
    embed = discord.Embed(
        title=f"{QUEUE_TYPES.get(info['queueId'], 'TFT')} | {name}",
        color=discord.Color.from_rgb(*PLACE_COLORS.get(p['placement'], (100, 100, 100)))
    )
    embed.description = f"⏱️ {int(info['game_length'] / 60)} min • Poziom {p['level']}"
    embed.add_field(
        name="📊 Statystyki",
        value=f"💰 **Złoto:** {p.get('gold_left', 0)}\n"
              f"💀 **Eliminacje:** {p.get('players_eliminated', 0)}\n"
              f"⚔️ **Dmg:** {p.get('total_damage_to_players', 0)}\n"
              f"🔄 **Etap:** {get_tft_stage(p.get('last_round', 0))}"
    )
    file = await generate_full_summary(p['placement'], [], p['traits'], p['units'], p.get('companion'))
    if file: embed.set_image(url="attachment://summary.png")
    return embed, file


@bot.event
async def on_ready():
    print(f'🔥 Bot gotowy: {bot.user}')
    if GUILD_ID == 0:
        print("❌ OSTRZEŻENIE: Nie ustawiono GUILD_ID. Komendy nie zostaną wgrane automatycznie.")
        return
    try:
        my_guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=my_guild)
        synced = await bot.tree.sync(guild=my_guild)
        print(f"✅ Zsynchronizowano {len(synced)} komend z serwerem ID: {GUILD_ID}")
    except Exception as e:
        print(f"❌ Błąd synchronizacji: {e}")


@bot.tree.command(name="track", description="Dodaj gracza do śledzenia (np. Nick#TAG)")
async def track(interaction: discord.Interaction, riot_id: str, region: str = "EUN1"):
    await interaction.response.defer()
    try:
        if "#" not in riot_id:
            await interaction.followup.send("❌ Błędny format! Użyj: `Nick#TAG`")
            return
        name, tag = riot_id.split("#")
        acc_url = f"{ROUTING_URL}/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(name)}/{urllib.parse.quote(tag)}"
        acc = await riot_request(acc_url)
        if not acc:
            await interaction.followup.send(f"❌ Nie znaleziono konta: **{riot_id}**")
            return
        success = await database.add_player(
            puuid=acc['puuid'],
            name=acc['gameName'],
            region=region,
            channel_id=interaction.channel_id,
            summoner_id=""
        )
        if success:
            await interaction.followup.send(f"✅ Dodano gracza **{acc['gameName']}#{acc['tagLine']}**!")
        else:
            await interaction.followup.send(f"⚠️ Gracz **{acc['gameName']}** jest już na liście.")
    except Exception as e:
        await interaction.followup.send(f"❌ Wystąpił błąd: {str(e)}")


@bot.tree.command(name="inspect", description="Dane JSON (Debug)")
async def inspect(interaction: discord.Interaction, riot_id: str):
    await interaction.response.defer()
    try:
        n, t = riot_id.split("#", 1)
        acc = await riot_request(f"{ROUTING_URL}/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(n)}/{t}")
        if not acc:
            await interaction.followup.send("Nie znaleziono konta.")
            return
        m = await riot_request(f"{ROUTING_URL}/tft/match/v1/matches/by-puuid/{acc['puuid']}/ids?count=1")
        if not m:
            await interaction.followup.send("Brak meczów.")
            return
        md = await riot_request(f"{ROUTING_URL}/tft/match/v1/matches/{m[0]}")
        p = next((x for x in md['info']['participants'] if x['puuid'] == acc['puuid']), None)
        await interaction.followup.send(
            file=discord.File(StringIO(json.dumps(p, indent=4)), filename=f"debug_{n}.json"))
    except Exception as e:
        await interaction.followup.send(f"Wystąpił błąd: {e}")


@bot.tree.command(name="test", description="Pokaż ostatni mecz gracza")
async def test(interaction: discord.Interaction, riot_id: str):
    await interaction.response.defer()
    try:
        n, t = riot_id.split("#", 1)
        acc = await riot_request(f"{ROUTING_URL}/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(n)}/{t}")
        if not acc:
            await interaction.followup.send("Nie znaleziono konta.")
            return
        md = await riot_request(f"{ROUTING_URL}/tft/match/v1/matches/by-puuid/{acc['puuid']}/ids?count=1")
        if not md:
            await interaction.followup.send("Brak meczów.")
            return
        match = await riot_request(f"{ROUTING_URL}/tft/match/v1/matches/{md[0]}")
        embed, file = await create_full_report(riot_id, match, acc['puuid'])
        await interaction.followup.send(embed=embed, file=file)
    except Exception as e:
        await interaction.followup.send(f"Wystąpił błąd: {e}")


@tasks.loop(minutes=2)
async def check_matches_task():
    try:
        players = await database.get_tracked_players()
    except Exception as e:
        print(f"❌ Błąd odczytu bazy JSON: {e}")
        return
    if not players: return

    for p in players:
        try:
            puuid = p['puuid']
            name = p['name']
            last_match = p['last_match_id']
            channel_id = int(p['ch'])

            m = await riot_request(f"{ROUTING_URL}/tft/match/v1/matches/by-puuid/{puuid}/ids?count=1")
            if m and m[0] != last_match:
                print(f"🔎 Znaleziono nowy mecz dla {name}!")
                det = await riot_request(f"{ROUTING_URL}/tft/match/v1/matches/{m[0]}")
                emb, f = await create_full_report(name, det, puuid)
                ch = bot.get_channel(channel_id)
                if ch and emb:
                    await ch.send(embed=emb, file=f)
                await database.update_last_match(puuid, m[0])
        except Exception as e:
            print(f"⚠️ Błąd przy sprawdzaniu gracza {p.get('name', 'Unknown')}: {e}")


@bot.event
async def setup_hook():
    bot.session = aiohttp.ClientSession()
    try:
        await database.init_pool()
        check_matches_task.start()
        print("✅ Baza JSON załadowana i pętla sprawdzania uruchomiona.")
    except Exception as e:
        print(f"❌ Błąd inicjalizacji: {e}")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ BŁĄD KRYTYCZNY: Brak DISCORD_TOKEN w zmiennych środowiskowych!")
    else:
        bot.run(DISCORD_TOKEN)