# Alpaca ROC Trading Bot - Modernized Edition

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Alpaca-py 0.43.2](https://img.shields.io/badge/alpaca--py-0.43.2-green.svg)](https://pypi.org/project/alpaca-py/)
[![Paper Trading](https://img.shields.io/badge/paper%20trading-enabled-brightgreen.svg)]()

**A modernized high-frequency stock scalping bot using the Alpaca API and ROC (Rate of Change) strategy.**

## 🚀 What's New (Nov 2025)

This is a fully modernized version of the original Alpaca ROC Trading Bot with:

- ✅ **Updated to alpaca-py SDK** (deprecated alpaca-trade-api replaced)
- ✅ **Environment-based configuration** (secure .env file)
- ✅ **Comprehensive logging system** (file + console output)
- ✅ **Paper trading by default** (safe testing environment)
- ✅ **Modern Python 3.8+ support** (latest dependencies)
- ✅ **Better error handling** (automatic recovery)
- ✅ **Setup validation script** (verify configuration)
- ✅ **Complete documentation** (setup guide + migration notes)

## 📋 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Free [Alpaca account](https://alpaca.markets/) (paper trading)
- 5 minutes for setup

### 2. Installation

```bash
# Clone or navigate to the repository
cd Alpaca-ROC-Trading-Bot

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Create your configuration files
cp .env.example .env
cp Tickers.txt.example Tickers.txt

# Edit .env with your Alpaca API credentials
# Get them from: https://app.alpaca.markets/paper/dashboard/overview
```

Edit `.env`:
```bash
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
PAPER_TRADING=true  # Keep this as 'true' for testing!
```

Edit `Tickers.txt` with stocks to watch:
```
AAPL MSFT GOOGL AMZN TSLA
```

### 4. Validate Setup

```bash
# Run the validation script
python validate_setup.py
```

You should see:
```
🎉 All checks passed! You're ready to run the bot.
```

### 5. Run the Bot

```bash
# Start in paper trading mode (no real money)
python main_modernized.py
```

## 📊 Trading Strategy

### ROC (Rate of Change) Scalping

1. **Monitor** multiple stocks in real-time
2. **Calculate** Rate of Change for ask prices
3. **Identify** stocks with highest positive momentum
4. **Validate** Ask Price > Last Traded Price (bullish signal)
5. **Enter** with 100% capital allocation
6. **Exit** at 2% profit target
7. **Repeat** continuously during market hours

### Key Features

- **First Trade**: Waits until 10:00 AM EST, uses 30-min window
- **Subsequent Trades**: 1-minute timeframe for rapid scalping
- **No Stop Loss**: Only profit target (consider adding one!)
- **All-In Strategy**: Uses 100% of available cash per trade

## 📁 Project Structure

```
Alpaca-ROC-Trading-Bot/
├── main_modernized.py        # ⭐ NEW: Use this bot (alpaca-py)
├── validate_setup.py          # ⭐ NEW: Validate your setup
├── main.py                    # Original bot (deprecated API)
├── requirements.txt           # ⭐ UPDATED: Modern dependencies
├── .env.example              # ⭐ NEW: Configuration template
├── .gitignore                # ⭐ NEW: Protects credentials
├── Tickers.txt.example       # ⭐ NEW: Ticker list template
├── SETUP_GUIDE.md            # ⭐ NEW: Detailed setup instructions
├── MODERNIZATION_NOTES.md    # ⭐ NEW: Technical migration details
├── README_MODERNIZED.md      # ⭐ NEW: This file
├── README.md                  # Original documentation
└── AUTH/                      # Original auth directory
    ├── auth.txt               # Original credentials (still works)
    └── Tickers.txt            # Original ticker list (still works)
```

## 🔧 Configuration Options

All settings in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `ALPACA_API_KEY` | Your Alpaca API Key ID | Required |
| `ALPACA_SECRET_KEY` | Your Alpaca Secret Key | Required |
| `PAPER_TRADING` | Use paper trading mode | `true` |
| `PROFIT_TARGET_PERCENT` | Exit profit percentage | `2.0` |
| `MIN_CASH_BALANCE` | Minimum cash to keep | `10.0` |
| `EMAIL_ENABLED` | Send email alerts | `false` |
| `EMAIL_SENDER` | Gmail for sending | - |
| `EMAIL_PASSWORD` | Gmail app password | - |
| `EMAIL_RECEIVER` | Email to receive alerts | - |

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup walkthrough
- **[MODERNIZATION_NOTES.md](MODERNIZATION_NOTES.md)** - Technical details of changes
- **[README.md](README.md)** - Original documentation

## 🛡️ Safety Features

1. **Paper Trading Default** - No real money at risk
2. **Validation Script** - Checks setup before running
3. **Comprehensive Logging** - Complete audit trail
4. **Credential Protection** - .env not committed to git
5. **PDT Protection** - Auto-stops if flagged
6. **Confirmation Prompt** - Double-check for live trading

## ⚠️ Important Warnings

- **No Stop Loss**: Unlimited downside risk per trade
- **100% Allocation**: Extremely aggressive capital management
- **Pattern Day Trader Rule**: Need $25k+ for live trading
- **High Frequency**: Can accumulate losses quickly
- **Educational Purpose**: Not financial advice
- **Test Thoroughly**: Use paper trading for weeks first

## 🧪 Testing Recommendations

1. ✅ Run in paper trading for **at least 1 week**
2. ✅ Monitor `trading_bot.log` daily
3. ✅ Review trade history in `Orders.csv`
4. ✅ Test during different market conditions
5. ✅ Verify email alerts work (if enabled)
6. ⚠️ Only consider live trading after thorough testing

## 📈 Monitoring

### Check Logs
```bash
# Watch logs in real-time
tail -f trading_bot.log
```

### View Trades
```bash
# See trade history
cat Orders.csv
```

### Alpaca Dashboard
- Paper: https://app.alpaca.markets/paper/dashboard
- Live: https://app.alpaca.markets/live/dashboard

## 🔄 Migrating from Old Bot

If you're upgrading from the original bot:

1. **Backup your data:**
   ```bash
   cp Orders.csv Orders_backup.csv
   cp FirstTrade.csv FirstTrade_backup.csv
   ```

2. **Install new dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create configuration:**
   ```bash
   cp .env.example .env
   # Add your credentials
   ```

4. **Run validation:**
   ```bash
   python validate_setup.py
   ```

5. **Start modernized bot:**
   ```bash
   python main_modernized.py
   ```

See [MODERNIZATION_NOTES.md](MODERNIZATION_NOTES.md) for detailed migration info.

## 🐛 Troubleshooting

### Common Issues

**"Missing Alpaca API credentials!"**
- Create `.env` from `.env.example`
- Add your API keys from Alpaca dashboard

**"No module named 'alpaca'"**
- Run: `pip install -r requirements.txt`

**"No data available for ticker"**
- Market might be closed
- Try more liquid stocks (AAPL, MSFT, GOOGL)

**"Pattern day trading flag detected!"**
- Use paper trading (no PDT restrictions)
- Live accounts need $25k+ balance

For more help, see [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting)

## 🤝 Contributing

Improvements welcome! Areas for enhancement:

- Add stop-loss functionality
- Implement position sizing
- Support multiple positions
- Add backtesting capability
- Create web dashboard
- Support crypto trading

## 📜 License

Open source - use at your own risk. Not financial advice.

## 🔗 Resources

- **Alpaca**: https://alpaca.markets/
- **Alpaca Docs**: https://docs.alpaca.markets/
- **Alpaca-py GitHub**: https://github.com/alpacahq/alpaca-py
- **Alpaca Community**: https://forum.alpaca.markets/

## 📞 Support

- Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Review [MODERNIZATION_NOTES.md](MODERNIZATION_NOTES.md)
- Visit Alpaca Community Forum
- Run `python validate_setup.py`

---

**Version:** 2.0 (Modernized)
**Last Updated:** November 2025
**SDK:** alpaca-py 0.43.2
**Original:** [tejaslinge/Alpaca-ROC-Trading-Bot](https://github.com/tejaslinge/Alpaca-ROC-Trading-Bot)

---

## ⚖️ Disclaimer

This bot is for educational purposes only. Trading stocks involves significant risk of loss. Past performance does not guarantee future results. The authors are not responsible for any financial losses incurred. Always do your own research and consider consulting with a financial advisor before trading.
