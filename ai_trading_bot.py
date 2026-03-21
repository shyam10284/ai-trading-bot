import ccxt
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# --- CONFIGURATION ---
SYMBOL = 'BTC/USDT'
TIMEFRAME = '5m' 
TELEGRAM_BOT_TOKEN = '8624719861:AAHYU02Kp7fb-UDU1HP9L2XeaWYEbaIre4s' 
TELEGRAM_CHAT_ID = '7076515356'   

# Using KuCoin to avoid regional blocks
exchange = ccxt.kucoin()

def send_telegram_signal(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send message: {e}")

def fetch_data():
    """Fetches a larger dataset so the AI has enough history to learn from."""
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=500)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def create_features_and_train_ai(df):
    """
    THE AI BRAIN: 
    1. Creates mathematical features for the AI to study.
    2. Trains a Random Forest model on the historical data.
    3. Predicts what the current market is about to do.
    """
    # 1. Feature Engineering (Giving the AI clues)
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['SMA_30'] = df['close'].rolling(window=30).mean()
    df['Volatility'] = df['close'].rolling(window=10).std()
    df['Price_Change'] = df['close'].pct_change()
    
    # 2. The Target (What we want to predict: 1 if the NEXT candle goes up, 0 if down)
    df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)

    # Clean up empty data
    df = df.dropna()

    # 3. Split data into "Features" (X) and "Answers" (y)
    features = ['SMA_10', 'SMA_30', 'Volatility', 'Price_Change', 'volume']
    X = df[features]
    y = df['Target']

    # 4. Train the AI Model! (Using the last 490 candles to learn)
    # We leave out the very last row because we don't know the future yet!
    X_train = X.iloc[:-1] 
    y_train = y.iloc[:-1]
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 5. Make a prediction for right NOW
    current_market_state = X.iloc[[-1]]
    prediction = model.predict(current_market_state)[0]
    
    # Get the AI's confidence level (probability)
    probability = model.predict_proba(current_market_state)[0][1]

    return prediction, probability, df.iloc[-1]['close']

def run_bot():
    print("Starting Machine Learning Trading Bot...")
    while True:
        try:
            df = fetch_data()
            prediction, probability, entry_price = create_features_and_train_ai(df)
            
            # If AI predicts "Up" (1) AND is highly confident (>65%)
            if prediction == 1 and probability > 0.65:
                stop_loss = entry_price * 0.995 
                target_1 = entry_price * 1.01   
                target_2 = entry_price * 1.02   
                signal_time = datetime.now().strftime("%I:%M:%S %p")

                message = (
                    f"🤖 *AI Bot Observation* 🤖\n"
                    f"Asset: {SYMBOL}\n"
                    f"AI Confidence: `{probability * 100:.1f}%`\n"
                    f"Entry Price: `${entry_price:.2f}`\n\n"
                    f"🛑 *Ref SL:* `${stop_loss:.2f}`\n"
                    f"✅ *Ref Lvl 1:* `${target_1:.2f}`\n"
                    f"🚀 *Ref Lvl 2:* `${target_2:.2f}`\n\n"
                    f"⏱ Time: {signal_time}"
                )
                send_telegram_signal(message)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Signal sent! AI Confidence: {probability*100:.1f}%")
                
                # Sleep longer after a signal so it doesn't spam
                time.sleep(1800) 
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No strong AI signal. Current Bullish Probability: {probability*100:.1f}%")
            
            time.sleep(300) # Check again in 5 minutes
            
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()