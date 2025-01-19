import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
import os

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
TOKEN = os.getenv("YOUR_BOT_TOKEN")

# Функция для экранирования символов
def escape_markdown(text):
    return text.replace("-", "\\-").replace(".", "\\.").replace("_", "\\_")

# Функция для получения ежедневного отчёта
def fetch_daily_snapshot():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        market_cap = data['data']['total_market_cap']['usd']
        volume = data['data']['total_volume']['usd']
        dominance = data['data']['market_cap_percentage']['btc']
        # Экранируем данные
        return escape_markdown(
            f"📈 *Market Snapshot*\n\n"
            f"Total Market Cap: ${market_cap:,.2f}\n"
            f"24h Volume: ${volume:,.2f}\n"
            f"BTC Dominance: {dominance:.2f}%"
        )
    else:
        return "Failed to fetch market data. Please try again later."

# Функция для еженедельного отчёта
def fetch_weekly_trends():
    return escape_markdown(
        "📊 *Weekly Market Trends*\n\n"
        "- BTC: +5.2%\n"
        "- ETH: +7.1%\n"
        "- Total Market Cap Growth: +4.8%\n"
    )

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        f"Hello, {user.mention_markdown_v2()}\\! \\n"
        f"I'm Dayrep, your daily crypto market report bot\\. \\n"
        "Use /daily to get today's market snapshot or /weekly for weekly trends\\."
    )

# Команда /daily
async def daily(update: Update, context: CallbackContext) -> None:
    report = fetch_daily_snapshot()
    await update.message.reply_markdown_v2(report)

# Команда /weekly
async def weekly(update: Update, context: CallbackContext) -> None:
    report = fetch_weekly_trends()
    await update.message.reply_markdown_v2(report)

# Основная функция
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))

    application.run_polling()

if __name__ == "__main__":
    main()
