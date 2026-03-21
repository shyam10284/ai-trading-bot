import ccxt
import pandas as pd
import requests
import time
from datetime import datetime

# --- CONFIGURATION ---
SYMBOL = 'BTC/USDT'
TIMEFRAME = '5m' # 5-minute chart like in your image
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'

# Initialize exchange (using Binance as an example for free data)
exchange = ccxt.binance()

def send_telegram_signal(message):
    """Sends the signal to your Telegram phone app."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
        print("Signal sent to Telegram!")
    except Exception as e:
        print(f"Failed to send message: {e}")

def fetch_data():
    """Fetches the latest candlestick data."""
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def ai_strategy_logic(df):
    """
    THIS IS WHERE YOUR AI GOES. 
    For now, we use a simple Moving Average Crossover to generate a signal.
    """
    # Calculate simple moving averages
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['SMA_30'] = df['close'].rolling(window=30).mean()

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    # Check for a "Buy" signal (Fast MA crosses above Slow MA)
    if previous['SMA_10'] < previous['SMA_30'] and latest['SMA_10'] > latest['SMA_30']:
        entry_price = latest['close']
        
        # Calculate levels just like the screenshot
        stop_loss = entry_price * 0.995 # 0.5% below entry
        target_1 = entry_price * 1.01   # 1% above entry
        target_2 = entry_price * 1.02   # 2% above entry
        
        signal_time = datetime.now().strftime("%I:%M:%S %p")

        # Format the message to look like your group promo/chart
        message = (
            f"🚨 *AI Buy Observation* 🚨\n"
            f"Asset: {SYMBOL}\n"
            f"Price: `${entry_price:.2f}`\n\n"
            f"🛑 *Ref SL:* `${stop_loss:.2f}`\n"
            f"✅ *Ref Lvl 1:* `${target_1:.2f}`\n"
            f"🚀 *Ref Lvl 2:* `${target_2:.2f}`\n\n"
            f"⏱ Time: {signal_time}"
        )
        send_telegram_signal(message)
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No signal right now. Market is chopping.")

def run_bot():
    print("Starting AI Trading Bot...")
    while True:
        try:
            df = fetch_data()
            ai_strategy_logic(df)
            
            # Wait 5 minutes before checking the next candle
            time.sleep(300) 
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()