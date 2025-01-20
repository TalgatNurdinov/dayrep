import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
import os
from html import escape

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token from BotFather
TOKEN = os.getenv("YOUR_BOT_TOKEN")
WEBHOOK_URL = "https://dayrep-bot.onrender.com"
PORT = int(os.getenv("PORT", 8443))

# Function to fetch daily market snapshot with HTML formatting
def fetch_daily_snapshot():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        market_cap = data['data']['total_market_cap']['usd']
        volume = data['data']['total_volume']['usd']
        btc_dominance = data['data']['market_cap_percentage']['btc']
        sentiment = "Neutral (Fear & Greed: 50)"  # Example data
        return (
            f"📈 <b>Market Snapshot</b><br><br>"
            f"• Total Market Cap: ${market_cap:,.2f}<br>"
            f"• 24h Volume: ${volume:,.2f}<br>"
            f"• BTC Dominance: {btc_dominance:.2f}%<br>"
            f"• Sentiment: {sentiment}"
        )
    else:
        return "Failed to fetch market data. Please try again later."

# Function to fetch winners and losers from CoinGecko API with HTML formatting
def fetch_winners_losers():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'percent_change_24h_desc',
        'per_page': 5,
        'page': 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        winners = [escape(f"{coin['name']} (+{coin['price_change_percentage_24h']:.2f}%)") for coin in data[:5]]

        params['order'] = 'percent_change_24h_asc'
        response = requests.get(url, params=params)
        data = response.json()
        losers = [escape(f"{coin['name']} ({coin['price_change_percentage_24h']:.2f}%)") for coin in data[:5]]

        return (
            "📊 <b>Winners & Losers</b><br><br>"
            "<b>Winners:</b><br>"
            + "<br>".join([f"• {winner}" for winner in winners]) + "<br><br>"
            "<b>Losers:</b><br>"
            + "<br>".join([f"• {loser}" for loser in losers])
        )
    else:
        return "Failed to fetch winners and losers."

# Function to fetch news from CoinGecko API with HTML formatting
def fetch_news():
    url = "https://api.coingecko.com/api/v3/status_updates"
    params = {
        'per_page': 5,  # Get the latest 5 news items
        'page': 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        news_items = [
            escape(f"{item['project']['name']}: {item['description']}")
            for item in data['status_updates'][:5]
        ]
        return (
            "🗞️ <b>News That Matters</b><br><br>"
            + "<br>".join([f"• {item}" for item in news_items])
        )
    else:
        return "Failed to fetch news. Please try again later."

# Command: Daily report with HTML formatting
async def daily(update: Update, context: CallbackContext) -> None:
    try:
        snapshot = fetch_daily_snapshot()
        winners_losers = fetch_winners_losers()
        news = fetch_news()
        report = f"{snapshot}<br><br>{winners_losers}<br><br>{news}"
        await update.message.reply_text(report, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in /daily: {e}")
        await update.message.reply_text("An error occurred while generating the report. Please try again later.")

# Command: Weekly report
async def weekly(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Weekly trends are currently unavailable.")

# Command: Start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hello, <b>{escape(user.full_name)}</b>!<br>"
        f"I'm Dayrep, your daily crypto market report bot.<br>"
        "Use /daily to get today's market snapshot or /weekly for weekly trends.",
        parse_mode='HTML'
    )

# Main function
def main():
    application = Application.builder().token(TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))

    # Run Webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == '__main__':
    main()
