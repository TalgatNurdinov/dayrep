import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
import os  # Импортируем os для работы с переменными окружения

# Получаем токен из переменной окружения
TOKEN = os.getenv("YOUR_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)



# Function to fetch daily market snapshot from CoinGecko API
def fetch_daily_snapshot():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        market_cap = data['data']['total_market_cap']['usd']
        volume = data['data']['total_volume']['usd']
        dominance = data['data']['market_cap_percentage']['btc']
        return f"📈 *Market Snapshot*\n\n" \
               f"Total Market Cap: ${market_cap:,.2f}\n" \
               f"24h Volume: ${volume:,.2f}\n" \
               f"BTC Dominance: {dominance:.2f}%"
    else:
        return "Failed to fetch market data. Please try again later."

# Function to fetch weekly market trends (mock implementation)
def fetch_weekly_trends():
    # Placeholder for weekly data
    return ("📊 *Weekly Market Trends*\n\n"
            "- BTC: +5.2%\n"
            "- ETH: +7.1%\n"
            "- Total Market Cap Growth: +4.8%\n")

# Command: Start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        f"Hello, {user.mention_markdown_v2()}\\! \\n"
        f"I'm Dayrep, your daily crypto market report bot\\. \\n"
        "Use /daily to get today's market snapshot or /weekly for weekly trends\\."
    )

# Command: Daily report
async def daily(update: Update, context: CallbackContext) -> None:
    report = fetch_daily_snapshot()
    await update.message.reply_markdown_v2(report)

# Command: Weekly report
async def weekly(update: Update, context: CallbackContext) -> None:
    report = fetch_weekly_trends()
    await update.message.reply_markdown_v2(report)

# Main function
def main():
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
