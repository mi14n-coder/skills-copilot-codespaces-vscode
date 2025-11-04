# Alpaca ROC Trading Bot - Setup Guide (Modernized)

## Overview

This is a modernized version of the Alpaca ROC Trading Bot, updated to use the latest `alpaca-py` SDK (v0.43.2) and modern Python best practices.

### What's New in the Modernized Version

- ✅ Updated to `alpaca-py` SDK (alpaca-trade-api is deprecated)
- ✅ Environment variable configuration with `.env` file
- ✅ Comprehensive logging to file and console
- ✅ Better error handling and recovery
- ✅ Paper trading mode by default (safe testing)
- ✅ Modern Python dependencies (Python 3.8+)
- ✅ Improved code structure and documentation
- ✅ Secure credential storage

## Prerequisites

- **Python 3.8 or higher**
- **Alpaca Account** (Free Paper Trading Account is sufficient)
- **$25,000+ for live trading** (Pattern Day Trader rule) or use Paper Trading for testing

## Installation Steps

### 1. Get Alpaca API Credentials

1. Go to [Alpaca](https://alpaca.markets/) and create a free account
2. Navigate to your dashboard: https://app.alpaca.markets/paper/dashboard/overview
3. Go to "API Keys" section (usually in the right sidebar or under settings)
4. Click "Generate New Key" or view existing keys
5. Copy both the **API Key ID** and **Secret Key**
6. Keep these credentials secure!

**Important:** Use Paper Trading keys for testing (they're free and risk-free)

### 2. Clone and Setup

```bash
# Navigate to the bot directory
cd Alpaca-ROC-Trading-Bot

# Install dependencies
pip install -r requirements.txt

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure the Bot

#### Create your `.env` file:

```bash
cp .env.example .env
```

#### Edit `.env` with your credentials:

```bash
# Required: Your Alpaca API credentials
ALPACA_API_KEY=PKxxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Trading mode (ALWAYS start with paper trading!)
PAPER_TRADING=true

# Optional: Email notifications
EMAIL_ENABLED=false
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECEIVER=receiver@gmail.com

# Trading parameters
PROFIT_TARGET_PERCENT=2.0
MIN_CASH_BALANCE=10.0
```

#### Create your ticker list:

```bash
cp Tickers.txt.example Tickers.txt
```

Edit `Tickers.txt` to include the stocks you want to trade:

```
AAPL MSFT GOOGL AMZN TSLA META NVDA
```

**Pro tip:** Start with 5-10 liquid stocks for best results.

### 4. Test Your Setup

Run the modernized bot:

```bash
python main_modernized.py
```

You should see:

```
============================================================
Alpaca ROC Trading Bot - Modernized Version
Mode: PAPER TRADING
Watching 7 tickers
============================================================
```

## Understanding the Trading Strategy

### ROC (Rate of Change) Scalping Strategy

1. **Calculate ROC** for all watched stocks based on ask price
2. **Sort by highest ROC** (stocks with fastest price increase)
3. **Validation**: Check if Ask Price > Last Traded Price (bullish signal)
4. **Buy**: Use 100% of available cash on the selected stock
5. **Sell**: Exit at 2% profit (configurable)
6. **Repeat**: Continuous scanning and trading

### Important Behavior

- **First Trade**: Waits until 10:00 AM EST, uses 30-minute data window
- **Subsequent Trades**: Uses 1-minute data window for rapid scalping
- **Capital Allocation**: All-in strategy (100% cash per trade)
- **No Stop Loss**: Only profit target (risk consideration!)

## File Structure

```
Alpaca-ROC-Trading-Bot/
├── main_modernized.py      # New modernized bot (USE THIS)
├── main.py                  # Original bot (deprecated API)
├── requirements.txt         # Updated dependencies
├── .env                     # Your credentials (create from .env.example)
├── .env.example            # Template for configuration
├── .gitignore              # Protects sensitive files
├── Tickers.txt             # Your stock symbols (create from example)
├── Tickers.txt.example     # Template ticker list
├── trading_bot.log         # Bot activity log (auto-created)
├── Orders.csv              # Trade history (auto-created)
├── FirstTrade.csv          # First trade marker (auto-created)
├── tick_data/              # Market data cache (auto-created)
└── SETUP_GUIDE.md          # This file
```

## Running the Bot

### Paper Trading (Recommended for Testing)

```bash
# Make sure PAPER_TRADING=true in .env
python main_modernized.py
```

**No real money at risk!** Perfect for testing and learning.

### Live Trading (CAUTION!)

```bash
# Set PAPER_TRADING=false in .env
# Use your LIVE trading API keys
python main_modernized.py

# You'll be prompted to confirm:
WARNING: Running in LIVE TRADING mode! Type 'YES' to confirm:
```

⚠️ **WARNING:** Live trading uses real money and requires $25k+ to avoid PDT restrictions!

## Configuration Options

### `.env` Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALPACA_API_KEY` | Your Alpaca API Key ID | Required |
| `ALPACA_SECRET_KEY` | Your Alpaca Secret Key | Required |
| `PAPER_TRADING` | Use paper trading mode | `true` |
| `EMAIL_ENABLED` | Send email notifications | `false` |
| `EMAIL_SENDER` | Gmail address for sending | - |
| `EMAIL_PASSWORD` | Gmail app password | - |
| `EMAIL_RECEIVER` | Email to receive alerts | - |
| `PROFIT_TARGET_PERCENT` | Exit profit target | `2.0` |
| `MIN_CASH_BALANCE` | Minimum cash to maintain | `10.0` |

### Email Notifications Setup (Optional)

To enable email alerts:

1. Use a Gmail account
2. Enable 2-factor authentication
3. Create an [App Password](https://myaccount.google.com/apppasswords)
4. Use the app password (not your regular password)
5. Set `EMAIL_ENABLED=true` in `.env`

## Monitoring the Bot

### Check Logs

```bash
# Watch logs in real-time
tail -f trading_bot.log
```

### View Trade History

```bash
# Open Orders.csv in a spreadsheet
cat Orders.csv
```

### Alpaca Dashboard

Monitor your positions and orders at:
- Paper Trading: https://app.alpaca.markets/paper/dashboard
- Live Trading: https://app.alpaca.markets/live/dashboard

## Troubleshooting

### "Missing Alpaca API credentials!"

- Make sure `.env` file exists
- Check that `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` are set
- Verify no extra spaces in the `.env` file

### "No data available for ticker"

- Some stocks may have low trading volume
- Market might be closed
- Try more liquid stocks (AAPL, MSFT, etc.)

### "Pattern day trading flag detected!"

- Your account has been flagged for PDT
- Paper trading accounts don't have this restriction
- Live accounts need $25k+ to avoid PDT

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### API Rate Limits

- Alpaca has rate limits on API calls
- The bot includes automatic error handling and retries
- Consider reducing the number of tickers if you hit limits

## Safety Features

1. **Paper Trading Default**: Safe testing environment
2. **Pattern Day Trader Protection**: Auto-stops if PDT flag is detected
3. **Logging**: Complete audit trail of all actions
4. **Credential Security**: `.env` file not committed to git
5. **Error Recovery**: Automatic retry on transient errors
6. **Confirmation Prompt**: Double-check before live trading

## Performance Considerations

### Recommended Settings

- **Tickers**: 5-10 liquid stocks (high volume)
- **Account Size**: $5,000+ for paper testing, $25,000+ for live
- **Profit Target**: 2% is aggressive, consider 1.5-3% based on volatility
- **Market Hours**: Most effective during high volume periods (10 AM - 3 PM EST)

### Risk Warnings

⚠️ **This bot is for educational purposes**
- No stop-loss mechanism (unlimited downside risk per trade)
- 100% capital allocation is extremely aggressive
- Past performance doesn't guarantee future results
- High-frequency trading can incur significant losses
- Always test thoroughly in paper trading first

## Differences from Original Bot

### What Changed?

| Feature | Original | Modernized |
|---------|----------|------------|
| SDK | `alpaca-trade-api` (deprecated) | `alpaca-py` (current) |
| Config | JSON file | `.env` file |
| Logging | Print statements | Full logging system |
| Error Handling | Basic try/catch | Comprehensive recovery |
| Security | Exposed credentials | Environment variables |
| Dependencies | 2022 versions | 2025 versions |

### Backward Compatibility

The modernized bot creates the same output files (`Orders.csv`, `FirstTrade.csv`) so you can switch between versions if needed.

## Next Steps

1. ✅ Test in paper trading for at least 1 week
2. ✅ Monitor the log files daily
3. ✅ Analyze your trade history in Orders.csv
4. ✅ Adjust profit target and ticker list based on results
5. ✅ Consider adding stop-loss protection (code modification needed)
6. ⚠️ Only switch to live trading after thorough paper testing

## Getting Help

- **Alpaca Documentation**: https://docs.alpaca.markets/
- **Alpaca Community Forum**: https://forum.alpaca.markets/
- **Alpaca-py GitHub**: https://github.com/alpacahq/alpaca-py

## License

This is a modernized version of the original open-source bot. Use at your own risk.

---

**Last Updated:** November 2025
**Bot Version:** 2.0 (Modernized)
**SDK:** alpaca-py 0.43.2
