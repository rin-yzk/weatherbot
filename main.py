import discord
import json
import asyncio
from commands import WeatherCommands
from datetime import datetime
import pytz
import aiohttp

# Discordトークン（本番では環境変数を推奨）
TOKEN = "YOUR-DISCORD-TOKEN"

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
bot = WeatherCommands(intents=intents)

# 天気コードを絵文字に変換（例）
WEATHER_EMOJIS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️", 51: "🌦️", 61: "🌧️",
    71: "🌨️", 95: "⛈️", 99: "🌩️"
}

async def fetch_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=weathercode,temperature_2m_max,temperature_2m_min"
        "&timezone=Asia%2FTokyo"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                code = data["daily"]["weathercode"][0]
                max_temp = data["daily"]["temperature_2m_max"][0]
                min_temp = data["daily"]["temperature_2m_min"][0]
                emoji = WEATHER_EMOJIS.get(code, "❓")
                return f"{emoji} 今日の天気: 最高 {max_temp}℃ / 最低 {min_temp}℃"
            else:
                return "⚠️ 天気情報の取得に失敗しました。"

async def post_weather():
    await bot.wait_until_ready()

    # 最新の設定を毎回読み込む
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    channel_id = config.get("channel_id")
    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"チャンネルID {channel_id} が見つかりません。")
        return

    message = ""
    for location in config.get("locations", []):
        name = location["name"]
        lat = location["latitude"]
        lon = location["longitude"]

        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            f"&timezone=Asia%2FTokyo"
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()

                    max_temp = data["daily"]["temperature_2m_max"][0]
                    min_temp = data["daily"]["temperature_2m_min"][0]
                    pop = data["daily"]["precipitation_probability_max"][0]

                    icon = "☀️"
                    if pop >= 80:
                        icon = "🌧️"
                    elif pop >= 50:
                        icon = "🌦️"
                    elif pop >= 30:
                        icon = "☁️"

                    message += f"📍 {name}\n{icon} 今日の天気: 最高 {max_temp}℃ / 最低 {min_temp}℃\n☔ 降水確率: {pop}%\n\n"
        except Exception as e:
            print(f"[{name}] 天気情報取得失敗: {e}")
            continue

    if message:
        await channel.send(message)

async def scheduler():
    while True:
        # 最新の設定を読み込み
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        now = datetime.now(pytz.timezone("Asia/Tokyo"))
        post_time = config.get("post_time", "07:10")
        post_hour, post_minute = map(int, post_time.split(":"))

        # デバッグログ（変更が反映されているかチェック）
        print(f"[scheduler] 現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[scheduler] 読み込んだ投稿時刻: {post_time}（{post_hour}:{post_minute}）")

        if now.hour == post_hour and now.minute == post_minute:
            print("[scheduler] 投稿時刻です。天気情報を送信します。")
            await post_weather()
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(10)

async def main():
    async with bot:
        await asyncio.gather(
            bot.start(TOKEN),
            scheduler()
        )

if __name__ == "__main__":
    asyncio.run(main())
