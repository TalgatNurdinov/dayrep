import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
import os
import time
from html import escape
from functools import lru_cache

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("BOT_TOKEN")  # Переименовано для Render.com
WEBHOOK_URL = "https://dayrep-bot.onrender.com"
PORT = int(os.getenv("PORT", 8443))
CACHE_TTL = 300  # 5 минут

# Форматирование чисел для больших значений
def format_number(num: float) -> str:
    if num >= 1e12:
        return f"{num/1e12:.2f}T"
    elif num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif num >= 1e6:
        return f"{num/1e6:.2f}M"
    return f"{num:,.2f}"

# Кэшированные запросы к API
@lru_cache(maxsize=32, ttl=CACHE_TTL)
def fetch_coingecko_data(endpoint: str, params: dict = None):
    try:
        url = f"https://api.coingecko.com/api/v3/{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"CoinGecko API Error: {e}")
        return None

# Получение данных о рынке
def fetch_daily_snapshot() -> str:
    data = fetch_coingecko_data("global")
    if not data:
        return "❌ Failed to fetch market data"

    stats = data['data']
    return (
        f"📈 <b>Market Snapshot</b>\n\n"
        f"• Total Market Cap: ${format_number(stats['total_market_cap']['usd'])}\n"
        f"• 24h Volume: ${format_number(stats['total_volume']['usd'])}\n"
        f"• BTC Dominance: {stats['market_cap_percentage']['btc']:.2f}%\n"
        f"• Active Cryptos: {stats['active_cryptocurrencies']:,}"
    )

# Получение данных о победителях и проигравших
def fetch_winners_losers() -> str:
    params = {
        'vs_currency': 'usd',
        'per_page': 5,
        'price_change_percentage': '24h'
    }
    
    # Winners
    winners_data = fetch_coingecko_data("coins/markets", {**params, 'order': 'gecko_desc'})
    time.sleep(1)  # Задержка для API
    
    # Losers
    losers_data = fetch_coingecko_data("coins/markets", {**params, 'order': 'gecko_asc'})
    
    if not winners_data or not losers_data:
        return "❌ Failed to fetch market movers"
    
    winners = [escape(f"{coin['name']} (+{coin['price_change_percentage_24h']:.2f}%)") 
              for coin in winners_data[:3]]
    losers = [escape(f"{coin['name']} ({coin['price_change_percentage_24h']:.2f}%)") 
             for coin in losers_data[:3]]
    
    return (
        "📊 <b>Top Movers</b>\n\n"
        "<b>🚀 Winners:</b>\n" + "\n".join([f"• {w}" for w in winners]) + "\n\n"
        "<b>📉 Losers:</b>\n" + "\n".join([f"• {l}" for l in losers])
    )

# Новости
def fetch_news() -> str:
    data = fetch_coingecko_data("status_updates", {'per_page': 3})
    if not data or 'status_updates' not in data:
        return "❌ Failed to fetch news"
    
    news_items = []
    for item in data['status_updates'][:3]:
        project = item.get('project', {}).get('name', 'Unknown')
        description = escape(item.get('description', 'No description'))[:100]
        news_items.append(f"• <b>{project}</b>: {description}...")
    
    return "🗞️ <b>Latest News</b>\n\n" + "\n".join(news_items)

# Команды бота
async def daily(update: Update, context: CallbackContext) -> None:
    try:
        report = "\n\n".join([fetch_daily_snapshot(), fetch_winners_losers(), fetch_news()])
        await update.message.reply_text(report, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"/daily error: {str(e)}")
        await update.message.reply_text("⚠️ Error generating report. Please try later.")

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    name = user.full_name or user.first_name or "Anonymous"
    await update.message.reply_text(
        f"👋 Welcome, <b>{escape(name)}</b>!\n"
        "I'm Dayrep - your crypto market analyst.\n\n"
        "Commands:\n"
        "/daily - Market snapshot\n"
        "/weekly - Weekly trends (coming soon)",
        parse_mode=ParseMode.HTML
    )

async def weekly(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("📆 Weekly report feature is in development!")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))

    # Webhook конфигурация для Render
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        url_path='',
        cert=None
    )

if __name__ == '__main__':
    main()