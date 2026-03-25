# ai-trading-bot

⚠️ Disclaimer
This project is for educational purposes only. I am not a financial advisor. Cryptocurrency trading carries significant risk. Never trade with money you cannot afford to lose. The creator of this bot is not responsible for any financial losses incurred while using this software.

#  AI Crypto Trading Bot

A fully autonomous, Machine Learning-powered cryptocurrency trading bot that analyzes market data, generates buy/sell signals, and sends real-time alerts via Telegram. This bot is designed to run 24/7 in the cloud.

##  Features
* **Automated Market Analysis:** Fetches real-time price data using the KuCoin API (via `ccxt`).
* **Machine Learning Predictions:** Uses `scikit-learn` to analyze trends and generate intelligent trading signals.
* **Real-Time Telegram Alerts:** Instantly messages your phone with Buy/Sell recommendations.
* **Cloud-Native & Always On:** Wrapped in a Flask web server and deployed on Render, kept continuously awake using UptimeRobot.
* **Secure Setup:** Uses Environment Variables to keep API keys and Bot Tokens 100% hidden and secure.

##  Tech Stack
* **Language:** Python 3
* **Web Framework:** Flask
* **Data & ML:** Pandas, Scikit-Learn
* **Crypto API:** CCXT (KuCoin)
* **Cloud Hosting:** Render
* **Monitoring:** UptimeRobot

##  How to Run Locally

### 1. Prerequisites
You will need to create a few free accounts and get your API keys:
* A Telegram Bot Token (from BotFather)
* Your Telegram Chat ID
* KuCoin API Keys (optional depending on your exact script setup)

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone [https://github.com/](https://github.com/)[Your-GitHub-Username]/ai-trading-bot.git
cd ai-trading-bot
pip install -r requirements.txt

3. Environment Variables
Create a .env file in the root directory (or export them in your terminal) and add your secret keys:
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

4. Start the Bot
python ai_trading_bot.py

5.Cloud Deployment (Render)
This bot is configured to be deployed on Render.com as a Web Service.

Connect your GitHub repository to Render.

Set the Build Command to: pip install -r requirements.txt

Set the Start Command to: python ai_trading_bot.py

Add your Environment Variables in the Render dashboard.

Use UptimeRobot to ping the provided Render URL every 5 minutes to prevent the free server from sleeping.
