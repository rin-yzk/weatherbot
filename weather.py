import aiohttp

async def get_weather(latitude, longitude):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&current=temperature_2m,weathercode&timezone=Asia%2FTokyo"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            data = await response.json()
            current = data.get("current", {})
            temperature = current.get("temperature_2m")
            weathercode = current.get("weathercode")
            return {
                "temperature": temperature,
                "weathercode": weathercode
            }

# Open-Meteo の weathercode を日本語に変換する関数
def weather_code_to_text(code):
    mapping = {
        0: "晴れ",
        1: "主に晴れ",
        2: "曇りがち",
        3: "曇り",
        45: "霧",
        48: "霧（霧雨あり）",
        51: "弱い霧雨",
        53: "中程度の霧雨",
        55: "強い霧雨",
        61: "弱い雨",
        63: "中程度の雨",
        65: "強い雨",
        71: "弱い雪",
        73: "中程度の雪",
        75: "強い雪",
        95: "雷雨",
        96: "雷雨（雹あり）",
        99: "激しい雷雨（雹あり）"
    }
    return mapping.get(code, "不明な天気")
