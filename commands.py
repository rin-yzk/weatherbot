import discord
from discord import app_commands
import json
from geopy.geocoders import Nominatim

CONFIG_FILE = "config.json"
geolocator = Nominatim(user_agent="weather_bot")

class WeatherCommands(discord.Client):
    def __init__(self, *, intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        register_commands(self)
        await self.tree.sync()

@app_commands.command(name="settime", description="投稿時刻をHH:MM形式で設定します")
@app_commands.describe(time="例: 07:10")
async def set_time(interaction: discord.Interaction, time: str):
    try:
        hour, minute = map(int, time.split(":"))
        assert 0 <= hour < 24 and 0 <= minute < 60
    except:
        await interaction.response.send_message("⚠️ 時刻の形式が正しくありません。例: 07:10", ephemeral=True)
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    config["post_time"] = time  # BOTのメッセージ投稿がおかしくなったらここを確認
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    await interaction.response.send_message(f"✅ 投稿時刻を {time} に更新しました！", ephemeral=True)

@app_commands.command(name="addlocation", description="都市名から場所を追加します")
@app_commands.describe(city="都市名（例: Tokyo, Shizuoka など）")
async def add_location(interaction: discord.Interaction, city: str):
    location = geolocator.geocode(city)
    if not location:
        await interaction.response.send_message(f"⚠️ 「{city}」の場所が見つかりませんでした。", ephemeral=True)
        return
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    config["locations"].append({
        "name": city,
        "latitude": location.latitude,
        "longitude": location.longitude
    })
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    await interaction.response.send_message(f"✅ 「{city}」を追加しました！ 緯度: {location.latitude} 経度: {location.longitude}", ephemeral=True)

def register_commands(bot: WeatherCommands):
    bot.tree.add_command(set_time)
    bot.tree.add_command(add_location)
    bot.tree.add_command(location_all)
    bot.tree.add_command(remove_location)

@app_commands.command(name="location-all", description="追加された全ての場所を表示します")
async def location_all(interaction: discord.Interaction):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    locations = config.get("locations", [])
    if not locations:
        await interaction.response.send_message("🏙️ 追加された場所はまだありません。", ephemeral=True)
        return

    msg = "🌍 追加された場所一覧:\n"
    for loc in locations:
        msg += f"- {loc['name']} (緯度: {loc['latitude']:.4f}, 経度: {loc['longitude']:.4f})\n"

    await interaction.response.send_message(msg, ephemeral=True)

@app_commands.command(name="removelocation", description="追加済みの都市名を削除します")
@app_commands.describe(city="削除する都市名（例: Tokyo, Shizuoka など）")
async def remove_location(interaction: discord.Interaction, city: str):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    original_count = len(config["locations"])
    # 大文字小文字を無視して比較して削除
    config["locations"] = [
        loc for loc in config["locations"] if loc["name"].lower() != city.lower()
    ]

    removed_count = original_count - len(config["locations"])
    if removed_count == 0:
        await interaction.response.send_message(f"⚠️ 「{city}」は登録されていませんでした。", ephemeral=True)
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        await interaction.response.send_message(f"🗑️ 「{city}」を削除しました！", ephemeral=True)

