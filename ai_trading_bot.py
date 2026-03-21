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
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN' # Paste your token
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'     # Paste your ID

exchange = ccxt.kucoin()

def send_telegram_signal(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send message: {e}")

def fetch_data():
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=500)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def create_features_and_train_ai(df):
    """
    THE UPGRADED AI BRAIN
    Now includes RSI and MACD for professional-grade pattern recognition.
    """
    # 1. Basic Features
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['SMA_30'] = df['close'].rolling(window=30).mean()
    df['Volatility'] = df['close'].rolling(window=10).std()
    df['Price_Change'] = df['close'].pct_change()
    
    # 2. Advanced Feature: RSI (Relative Strength Index)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 3. Advanced Feature: MACD (Moving Average Convergence Divergence)
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # The Target: 1 if NEXT candle goes up, 0 if down
    df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)

    # Clean up empty data created by rolling averages
    df = df.dropna()

    # Tell the AI to look at ALL our new indicators
    features = ['SMA_10', 'SMA_30', 'Volatility', 'Price_Change', 'volume', 'RSI', 'MACD', 'Signal_Line']
    X = df[features]
    y = df['Target']

    # Train the AI Model
    X_train = X.iloc[:-1] 
    y_train = y.iloc[:-1]
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Make a prediction
    current_market_state = X.iloc[[-1]]
    prediction = model.predict(current_market_state)[0]
    probability = model.predict_proba(current_market_state)[0][1]

    return prediction, probability, df.iloc[-1]['close']

def run_bot():
    print("Starting Level 2 Machine Learning Trading Bot...")
    while True:
        try:
            df = fetch_data()
            prediction, probability, entry_price = create_features_and_train_ai(df)
            
            # CHANGED: Lowered threshold to 60% so you get signals faster!
            if prediction == 1 and probability > 0.60:
                stop_loss = entry_price * 0.995 
                target_1 = entry_price * 1.01   
                target_2 = entry_price * 1.02   
                signal_time = datetime.now().strftime("%I:%M:%S %p")

                message = (
                    f" *AI Bot Observation* \n"
                    f"Asset: {SYMBOL}\n"
                    f"AI Confidence: `{probability * 100:.1f}%`\n"
                    f"Price: `${entry_price:.2f}`\n\n"
                    f" *Ref SL:* `${stop_loss:.2f}`\n"
                    f" *Ref Lvl 1:* `${target_1:.2f}`\n"
                    f" *Ref Lvl 2:* `${target_2:.2f}`\n\n"
                    f" Time: {signal_time}"
                )
                send_telegram_signal(message)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Signal sent! AI Confidence: {probability*100:.1f}%")
                
                time.sleep(1800) # Sleep for 30 mins after a signal
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting. Current Bullish Probability: {probability*100:.1f}%")
            
            time.sleep(300) # Check again in 5 minutes
            
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()