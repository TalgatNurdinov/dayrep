import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Переменные окружения
TOKEN = os.getenv("YOUR_BOT_TOKEN")  # Токен бота
PORT = int(os.environ.get("PORT", 8443))  # Порт для Webhook
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_URL')}"  # URL твоего сервиса Render

# Функции бота
async def start(update: Update, context: CallbackContext) -> None:
    """Приветственное сообщение."""
    await update.message.reply_text("Привет! Я ваш Telegram-бот для криптоотчётов.")

async def daily(update: Update, context: CallbackContext) -> None:
    """Ежедневный отчёт."""
    await update.message.reply_text("Ежедневный отчёт пока пуст.")

async def weekly(update: Update, context: CallbackContext) -> None:
    """Еженедельный отчёт."""
    await update.message.reply_text("Еженедельный отчёт пока пуст.")

# Основная функция
def main():
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))

    # Настройка Webhook
    application.run_webhook(
        listen="0.0.0.0",  # Слушаем на всех интерфейсах
        port=PORT,  # Указываем порт
        webhook_url=WEBHOOK_URL  # Полный URL Webhook
    )

if __name__ == "__main__":
    main()
