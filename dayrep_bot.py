import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from datetime import datetime, timedelta

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token from BotFather
TOKEN = "YOUR_BOT_TOKEN"

# Function to fetch daily market snapshot from CoinGecko API
def fetch_daily_snapshot():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        market_cap = data['data']['total_market_cap']['usd']
        volume = data['data']['total_volume']['usd']
        dominance = data['data']['market_cap_percentage']['btc']
        return f"\U0001F4C8 *Market Snapshot*\n\n" \
               f"Total Market Cap: ${market_cap:,.2f}\n" \
               f"24h Volume: ${volume:,.2f}\n" \
               f"BTC Dominance: {dominance:.2f}%"
    else:
        return "Failed to fetch market data. Please try again later."

# Function to fetch weekly market trends (mock implementation)
def fetch_weekly_trends():
    # Placeholder for weekly data
    return ("\U0001F4CA *Weekly Market Trends*\n\n" \
            "- BTC: +5.2%\n" \
            "- ETH: +7.1%\n" \
            "- Total Market Cap Growth: +4.8%\n")

# Command: Start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        f"Hello, {user.mention_markdown_v2()}\! \n"
        f"I'm Dayrep, your daily crypto market report bot\. \n"
        "Use /daily to get today's market snapshot or /weekly for weekly trends\."
    )

# Command: Daily report
def daily(update: Update, context: CallbackContext) -> None:
    report = fetch_daily_snapshot()
    update.message.reply_markdown_v2(report, parse_mode='Markdown')

# Command: Weekly report
def weekly(update: Update, context: CallbackContext) -> None:
    report = fetch_weekly_trends()
    update.message.reply_markdown_v2(report, parse_mode='Markdown')

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Main function
def main():
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("daily", daily))
    dispatcher.add_handler(CommandHandler("weekly", weekly))

    # Log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
