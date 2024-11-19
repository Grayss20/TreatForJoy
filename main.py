import logging
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.models.models import Base
from app.utils.db import engine
from app.routes import web_app  # Импортируем маршруты веб-приложения
from bot import bot, dp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import Update

# Загрузка переменных окружения из .env
load_dotenv()

# Настройки
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_PATH = "/webhook"
PORT = int(os.getenv("PORT", 8000))

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройка FastAPI приложения
app = FastAPI()


# Mount static files globally
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Подключение маршрутов веб-приложения
app.include_router(web_app.router, prefix="/webapp")


# Инициализация базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully.")


async def check_webhook_status():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL + WEBHOOK_PATH:
        await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
        logger.info("Webhook set successfully!")
    else:
        logger.info("Webhook already set, no action needed.")


# Настройка вебхука при запуске приложения
@app.on_event("startup")
async def on_startup():
    logger.info("Checking and setting webhook...")
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL + WEBHOOK_PATH:
        await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
        logger.info("Webhook set successfully!")
    else:
        logger.info("Webhook already set, no action needed.")

    await init_db()

    # Планировщик для периодической проверки вебхука
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_webhook_status, "interval", minutes=3)
    scheduler.start()
    logger.info("Scheduler started for periodic webhook checks.")


# Удаление вебхука при завершении работы приложения
@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Deleting webhook...")
    await bot.delete_webhook()
    await engine.dispose()


# Эндпоинт для получения обновлений от Telegram
@app.post(WEBHOOK_PATH)
async def telegram_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}


# Маршрут для проверки состояния приложения
@app.get("/")
async def read_root():
    return {"message": "Telegram bot is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
