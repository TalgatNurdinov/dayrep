import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
import os

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

# Function to escape Markdown V2 special characters
def escape_markdown_v2(text):
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text

# Function to fetch daily market snapshot from CoinGecko API
def fetch_daily_snapshot():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        market_cap = data['data']['total_market_cap']['usd']
        volume = data['data']['total_volume']['usd']
        btc_dominance = data['data']['market_cap_percentage']['btc']
        sentiment = "Neutral (Fear & Greed: 50)"  # Mock sentiment data
        return escape_markdown_v2(f"\U0001F4F0 *Market Snapshot*\n\n" \
               f"• Total Market Cap: ${market_cap:,.2f}\n" \
               f"• 24h Volume: ${volume:,.2f}\n" \
               f"• BTC Dominance: {btc_dominance:.2f}%\n" \
               f"• Sentiment: {sentiment}")
    else:
        return "Failed to fetch market data. Please try again later."

# Function to fetch winners and losers from CoinGecko API
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
        winners = [f"{coin['name']} (+{coin['price_change_percentage_24h']:.2f}%)" for coin in data[:5]]

        params['order'] = 'percent_change_24h_asc'
        response = requests.get(url, params=params)
        data = response.json()
        losers = [f"{coin['name']} ({coin['price_change_percentage_24h']:.2f}%)" for coin in data[:5]]

        return escape_markdown_v2(
            "\U0001F4C8 *Winners & Losers*\n\n" \
            "*Winners:*\n" \
            + "\n".join([f"• {winner}" for winner in winners]) + "\n\n" \
            "*Losers:*\n" \
            + "\n".join([f"• {loser}" for loser in losers])
        )
    else:
        return "Failed to fetch winners and losers."

# Function to fetch news from CoinGecko API
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
            f"{item['project']['name']}: {escape_markdown_v2(item['description'])}"
            for item in data['status_updates'][:5]
        ]
        return escape_markdown_v2(
            "\U0001F4E2 *News That Matters*\n\n" \
            + "\n".join([f"• {item}" for item in news_items])
        )
    else:
        return "Failed to fetch news. Please try again later."

# Command: Daily report
async def daily(update: Update, context: CallbackContext) -> None:
    snapshot = fetch_daily_snapshot()
    winners_losers = fetch_winners_losers()
    news = fetch_news()
    report = f"{snapshot}\n\n{winners_losers}\n\n{news}"
    await update.message.reply_markdown_v2(report)

# Command: Weekly report
async def weekly(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Weekly trends are currently unavailable.")

# Command: Start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        escape_markdown_v2(
            f"Hello, {user.mention_markdown_v2()}\! \n"
            f"I'm Dayrep, your daily crypto market report bot\. \n"
            "Use /daily to get today's market snapshot or /weekly for weekly trends\."
        )
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
