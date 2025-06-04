# scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

def setup_scheduler(send_weather_func, post_time):
    hour, minute = map(int, post_time.split(":"))
    scheduler.add_job(send_weather_func, 'cron', hour=hour, minute=minute)
    scheduler.start()
