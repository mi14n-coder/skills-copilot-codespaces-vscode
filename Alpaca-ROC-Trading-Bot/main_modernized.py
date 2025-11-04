"""
Alpaca ROC Trading Bot - Modernized Version
Updated for alpaca-py SDK (Nov 2025)
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from pytz import timezone
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Modern Alpaca SDK imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockTradesRequest, StockQuotesRequest
from alpaca.data.timeframe import TimeFrame

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
PAPER_TRADING = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
PROFIT_TARGET = float(os.getenv('PROFIT_TARGET_PERCENT', '2.0'))
MIN_CASH = float(os.getenv('MIN_CASH_BALANCE', '10.0'))

# Initialize Alpaca clients
trading_client = TradingClient(
    api_key=ALPACA_API_KEY,
    secret_key=ALPACA_SECRET_KEY,
    paper=PAPER_TRADING
)

data_client = StockHistoricalDataClient(
    api_key=ALPACA_API_KEY,
    secret_key=ALPACA_SECRET_KEY
)

# Load tickers
def load_tickers():
    """Load ticker symbols from Tickers.txt or AUTH/Tickers.txt"""
    ticker_paths = ['Tickers.txt', 'AUTH/Tickers.txt']
    for path in ticker_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                tickers = f.read().upper().split()
                logger.info(f"Loaded {len(tickers)} tickers from {path}")
                return tickers

    logger.warning("No Tickers.txt found, using default tickers")
    return ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

TICKERS = load_tickers()

# Create tick_data directory if it doesn't exist
Path('tick_data').mkdir(exist_ok=True)


def get_minute_data(tickers):
    """Fetch 1-minute market data for given tickers"""
    ny_tz = timezone('America/New_York')
    end_time = datetime.now(ny_tz)
    start_time = end_time - timedelta(minutes=2)

    for ticker in tickers:
        try:
            # Get trades data
            trades_request = StockTradesRequest(
                symbol_or_symbols=ticker,
                start=start_time,
                end=end_time,
                limit=10000
            )
            trades = data_client.get_stock_trades(trades_request)

            # Get quotes data
            quotes_request = StockQuotesRequest(
                symbol_or_symbols=ticker,
                start=start_time,
                end=end_time,
                limit=10000
            )
            quotes = data_client.get_stock_quotes(quotes_request)

            # Convert to DataFrames
            if ticker in trades.data:
                prices_df = trades.df.reset_index()[['timestamp', 'price']]
                prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                prices_df = prices_df.drop_duplicates(subset='timestamp', keep='first')
                prices_df.set_index('timestamp', inplace=True)
            else:
                prices_df = pd.DataFrame(columns=['price'])

            if ticker in quotes.data:
                quotes_df = quotes.df.reset_index()[['timestamp', 'ask_price']]
                quotes_df['timestamp'] = pd.to_datetime(quotes_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                quotes_df = quotes_df.drop_duplicates(subset='timestamp', keep='first')
                quotes_df.set_index('timestamp', inplace=True)
            else:
                quotes_df = pd.DataFrame(columns=['ask_price'])

            # Merge and save
            if not prices_df.empty and not quotes_df.empty:
                df = pd.merge(prices_df, quotes_df, left_index=True, right_index=True, how='inner')
                df.to_csv(f'tick_data/{ticker}.csv')
                logger.debug(f"Saved minute data for {ticker}")
            else:
                logger.warning(f"No data available for {ticker}")

        except Exception as e:
            logger.error(f"Error fetching minute data for {ticker}: {e}")


def get_past30_data(tickers):
    """Fetch 30-minute historical data for first trade"""
    ny_tz = timezone('America/New_York')
    now = datetime.now(ny_tz)

    for ticker in tickers:
        try:
            # Get trades from 30 mins ago
            trades_request_1 = StockTradesRequest(
                symbol_or_symbols=ticker,
                start=now - timedelta(minutes=30),
                end=now - timedelta(minutes=28, seconds=30),
                limit=10000
            )
            trades_1 = data_client.get_stock_trades(trades_request_1)

            # Get recent trades
            trades_request_2 = StockTradesRequest(
                symbol_or_symbols=ticker,
                start=now - timedelta(minutes=1, seconds=30),
                end=now,
                limit=10000
            )
            trades_2 = data_client.get_stock_trades(trades_request_2)

            # Get quotes from 30 mins ago
            quotes_request_1 = StockQuotesRequest(
                symbol_or_symbols=ticker,
                start=now - timedelta(minutes=30),
                end=now - timedelta(minutes=28, seconds=30),
                limit=10000
            )
            quotes_1 = data_client.get_stock_quotes(quotes_request_1)

            # Get recent quotes
            quotes_request_2 = StockQuotesRequest(
                symbol_or_symbols=ticker,
                start=now - timedelta(minutes=1, seconds=30),
                end=now,
                limit=10000
            )
            quotes_2 = data_client.get_stock_quotes(quotes_request_2)

            # Process and merge data
            prices_list = []
            if ticker in trades_1.data:
                df1 = trades_1.df.reset_index()[['timestamp', 'price']]
                prices_list.append(df1)
            if ticker in trades_2.data:
                df2 = trades_2.df.reset_index()[['timestamp', 'price']]
                prices_list.append(df2)

            quotes_list = []
            if ticker in quotes_1.data:
                df1 = quotes_1.df.reset_index()[['timestamp', 'ask_price']]
                quotes_list.append(df1)
            if ticker in quotes_2.data:
                df2 = quotes_2.df.reset_index()[['timestamp', 'ask_price']]
                quotes_list.append(df2)

            if prices_list and quotes_list:
                prices_df = pd.concat(prices_list)
                prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                prices_df = prices_df.drop_duplicates(subset='timestamp', keep='first')
                prices_df.set_index('timestamp', inplace=True)

                quotes_df = pd.concat(quotes_list)
                quotes_df['timestamp'] = pd.to_datetime(quotes_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                quotes_df = quotes_df.drop_duplicates(subset='timestamp', keep='first')
                quotes_df.set_index('timestamp', inplace=True)

                df = pd.merge(prices_df, quotes_df, left_index=True, right_index=True, how='inner')
                df.to_csv(f'tick_data/{ticker}.csv')
                logger.debug(f"Saved 30-min data for {ticker}")
            else:
                logger.warning(f"Insufficient data for {ticker}")

        except Exception as e:
            logger.error(f"Error fetching 30-min data for {ticker}: {e}")


def ROC(ask, timeframe):
    """Calculate Rate of Change"""
    if len(ask) < 2:
        return 0

    if timeframe == 30:
        rocs = (ask.iloc[-1] - ask.iloc[0]) / ask.iloc[0]
    else:
        rocs = (ask.iloc[-1] - ask.iloc[-2]) / ask.iloc[-2]

    return rocs * 1000


def return_ROC_list(tickers, timeframe):
    """Returns list of ROCs for all tickers"""
    ROC_tickers = []

    for ticker in tickers:
        try:
            df = pd.read_csv(f'tick_data/{ticker}.csv')
            df.set_index('timestamp', inplace=True)
            df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d %H:%M')
            roc = ROC(df['ask_price'], timeframe)
            ROC_tickers.append(roc)
        except Exception as e:
            logger.error(f"Error calculating ROC for {ticker}: {e}")
            ROC_tickers.append(-999999)  # Very low value to avoid selection

    return ROC_tickers


def compare_ask_ltp(tickers, timeframe):
    """Compare ASK price vs Last Traded Price to find buy candidate"""
    if len(tickers) == 0:
        return None

    ROCs = return_ROC_list(tickers, timeframe)
    max_ROC = max(ROCs)

    if max_ROC <= 0:
        logger.info("All ROCs are <= 0")
        return 0

    max_ROC_index = ROCs.index(max_ROC)

    # Iterate through tickers sorted by ROC
    for _ in range(len(tickers)):
        try:
            buy_stock_init = tickers[max_ROC_index]
            df = pd.read_csv(f'tick_data/{buy_stock_init}.csv')
            df.set_index('timestamp', inplace=True)
            df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d %H:%M')

            # Check if ask_price > price for last 2 data points
            buy_condition = []
            for i in range(max(0, len(df) - 2), len(df)):
                if i < len(df):
                    buy_condition.append(df.iloc[i]['ask_price'] > df.iloc[i]['price'])

            if buy_condition and buy_condition[-1]:
                logger.info(f"Buy signal for {buy_stock_init} (ROC: {max_ROC:.4f})")
                return buy_stock_init
            else:
                # Remove this ticker and try next
                tickers.pop(max_ROC_index)
                ROCs.pop(max_ROC_index)

                if len(tickers) == 0:
                    logger.info("All Ask prices < LTP")
                    return -1

                max_ROC = max(ROCs)
                max_ROC_index = ROCs.index(max_ROC)

        except Exception as e:
            logger.error(f"Error in compare_ask_ltp for {buy_stock_init}: {e}")
            tickers.pop(max_ROC_index)
            ROCs.pop(max_ROC_index)

            if len(tickers) == 0:
                return -1

            max_ROC = max(ROCs)
            max_ROC_index = ROCs.index(max_ROC)

    return None


def algo(tickers):
    """Main algorithm to determine which stock to buy"""
    timeframe = 1 if os.path.isfile('FirstTrade.csv') else 30
    stock = compare_ask_ltp(tickers.copy(), timeframe)
    return stock


def buy(stock_to_buy: str):
    """Place a buy order"""
    try:
        account = trading_client.get_account()
        cash_balance = float(account.cash)

        # Get latest trade price
        latest_trade_request = StockTradesRequest(
            symbol_or_symbols=stock_to_buy,
            limit=1
        )
        latest_trade = data_client.get_stock_latest_trade({stock_to_buy: latest_trade_request})
        price_stock = latest_trade[stock_to_buy].price

        # Calculate position size
        target_position_size = int(cash_balance / price_stock)

        if target_position_size < 1:
            logger.warning(f"Insufficient funds to buy {stock_to_buy}")
            return None

        # Place market order
        order_data = MarketOrderRequest(
            symbol=stock_to_buy,
            qty=target_position_size,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )

        order = trading_client.submit_order(order_data)

        mail_content = f'''ALERT

BUY Order Placed for {stock_to_buy}: {target_position_size} Shares at ${price_stock:.2f}'''

        logger.info(f"BUY: {stock_to_buy} x{target_position_size} @ ${price_stock:.2f}")

        # Log to CSV
        ny_tz = timezone('America/New_York')
        order_data = {
            'Time': datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S"),
            'Ticker': stock_to_buy,
            'Type': 'buy',
            'Price': price_stock,
            'Quantity': target_position_size,
            'Total': target_position_size * price_stock,
            'Acc Balance': cash_balance
        }

        if os.path.isfile('Orders.csv'):
            df = pd.read_csv('Orders.csv', index_col=0)
            df = pd.concat([df, pd.DataFrame([order_data])], ignore_index=True)
        else:
            df = pd.DataFrame([order_data])

        df.to_csv('Orders.csv')

        return mail_content

    except Exception as e:
        logger.error(f"Error placing buy order for {stock_to_buy}: {e}")
        return None


def sell(current_stock):
    """Sell current position"""
    try:
        position = trading_client.get_open_position(current_stock)
        quantity = float(position.qty)

        # Get latest price
        latest_trade_request = StockTradesRequest(
            symbol_or_symbols=current_stock,
            limit=1
        )
        latest_trade = data_client.get_stock_latest_trade({current_stock: latest_trade_request})
        sell_price = latest_trade[current_stock].price

        # Cancel pending orders and close position
        trading_client.cancel_orders()
        trading_client.close_position(current_stock)

        mail_content = f'''ALERT

SELL Order Placed for {current_stock}: {quantity} Shares at ${sell_price:.2f}'''

        logger.info(f"SELL: {current_stock} x{quantity} @ ${sell_price:.2f}")

        # Log to CSV
        ny_tz = timezone('America/New_York')
        account = trading_client.get_account()

        order_data = {
            'Time': datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S"),
            'Ticker': current_stock,
            'Type': 'sell',
            'Price': sell_price,
            'Quantity': quantity,
            'Total': quantity * sell_price,
            'Acc Balance': float(account.cash)
        }

        df = pd.read_csv('Orders.csv', index_col=0)
        df = pd.concat([df, pd.DataFrame([order_data])], ignore_index=True)
        df.to_csv('Orders.csv')

        return mail_content

    except Exception as e:
        logger.error(f"Error selling {current_stock}: {e}")
        return 0


def check_rets(current_stock):
    """Check returns and sell if profit target is met"""
    try:
        position = trading_client.get_open_position(current_stock)
        returns = float(position.unrealized_plpc) * 100

        logger.debug(f"{current_stock} current return: {returns:.2f}%")

        if returns >= PROFIT_TARGET:
            logger.info(f"Profit target met for {current_stock}: {returns:.2f}%")
            return sell(current_stock)

        return 0

    except Exception as e:
        logger.error(f"Error checking returns for {current_stock}: {e}")
        return 0


def mail_alert(mail_content, sleep_time):
    """Send email notification"""
    if not EMAIL_ENABLED or not mail_content:
        return

    try:
        message = MIMEMultipart()
        message['From'] = 'Trading Bot'
        message['To'] = EMAIL_RECEIVER
        message['Subject'] = 'Alpaca Trading Bot Alert'

        message.attach(MIMEText(mail_content, 'plain'))

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(EMAIL_SENDER, EMAIL_PASSWORD)

        text = message.as_string()
        session.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, text)
        session.quit()

        logger.info("Email alert sent")
        time.sleep(sleep_time)

    except Exception as e:
        logger.error(f"Error sending email: {e}")


def main():
    """Main trading loop"""
    logger.info("=" * 60)
    logger.info("Alpaca ROC Trading Bot - Modernized Version")
    logger.info(f"Mode: {'PAPER TRADING' if PAPER_TRADING else 'LIVE TRADING'}")
    logger.info(f"Watching {len(TICKERS)} tickers")
    logger.info("=" * 60)

    try:
        clock = trading_client.get_clock()

        if clock.is_open:
            mail_content = f'The bot started running on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S UTC")}'
            mail_alert(mail_content, 0)

        while True:
            try:
                # Check if PDT flag is set
                account = trading_client.get_account()
                if account.pattern_day_trader:
                    logger.warning("Pattern day trading flag detected! Stopping bot.")
                    mail_alert('Pattern day trading notification, bot is stopping now', 0)
                    break

                clock = trading_client.get_clock()

                if not clock.is_open:
                    logger.info("Market is closed, waiting...")
                    time.sleep(300)
                    continue

                tickers = TICKERS.copy()

                # First trade logic
                if not os.path.isfile('FirstTrade.csv'):
                    ny_tz = timezone('America/New_York')
                    current_time = datetime.now(ny_tz).strftime('%H:%M:%S')

                    if current_time < '10:00:00':
                        # Calculate time until 10:00 AM
                        time_diff = datetime.strptime('10:00:00', '%H:%M:%S') - datetime.strptime(current_time, '%H:%M:%S')
                        sleep_seconds = time_diff.total_seconds() - 20

                        if sleep_seconds > 0:
                            logger.info(f"Waiting until 10:00 AM EST (sleeping {sleep_seconds:.0f}s)")
                            time.sleep(sleep_seconds)

                    logger.info("Fetching 30-min data for first trade...")
                    get_past30_data(tickers)
                    stock_to_buy = algo(tickers)

                    if stock_to_buy == 0 or stock_to_buy == -1:
                        logger.info("No suitable stock found for first trade")
                        time.sleep(60)
                        continue

                    mail_content = buy(stock_to_buy)
                    if mail_content:
                        mail_alert(mail_content, 5)
                        # Mark first trade complete
                        df = pd.DataFrame({'First Stock': [stock_to_buy]})
                        df.to_csv('FirstTrade.csv')

                    continue

                # Regular trading logic
                account = trading_client.get_account()
                cash_balance = float(account.cash)

                if cash_balance > MIN_CASH:
                    # We have cash, look for buy opportunity
                    get_minute_data(tickers)
                    stock_to_buy = algo(tickers)

                    if stock_to_buy == 0:
                        logger.debug("All ROCs <= 0, waiting...")
                        time.sleep(2)
                        continue
                    elif stock_to_buy == -1:
                        logger.debug("All Ask < LTP, waiting...")
                        time.sleep(2)
                        continue
                    elif not stock_to_buy:
                        time.sleep(2)
                        continue

                    # Check if we already hold this stock
                    positions = trading_client.get_all_positions()
                    current_symbols = [pos.symbol for pos in positions]

                    if stock_to_buy in current_symbols:
                        position = trading_client.get_open_position(stock_to_buy)
                        latest_trade_request = StockTradesRequest(
                            symbol_or_symbols=stock_to_buy,
                            limit=1
                        )
                        latest_trade = data_client.get_stock_latest_trade({stock_to_buy: latest_trade_request})
                        current_price = latest_trade[stock_to_buy].price

                        if current_price > float(position.avg_entry_price):
                            logger.info(f"Already holding {stock_to_buy} at lower price, skipping")
                            time.sleep(2)
                            continue

                    # Cancel any partially filled orders
                    try:
                        orders = trading_client.get_orders()
                        for order in orders:
                            if order.status == 'partially_filled':
                                trading_client.cancel_orders()
                                break
                    except:
                        pass

                    mail_content = buy(stock_to_buy)
                    if mail_content:
                        mail_alert(mail_content, 5)

                else:
                    # No cash, check if we should sell any positions
                    positions = trading_client.get_all_positions()

                    for position in positions:
                        mail_content = check_rets(position.symbol)
                        if mail_content and mail_content != 0:
                            mail_alert(mail_content, 0)

                    time.sleep(3)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)
                continue

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        clock = trading_client.get_clock()
        if not clock.is_open:
            mail_content = f'The bot stopped running on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S UTC")}'
            mail_alert(mail_content, 0)

        logger.info("Bot shutdown complete")


if __name__ == '__main__':
    # Validate configuration
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        logger.error("Missing Alpaca API credentials! Please set them in .env file")
        exit(1)

    if PAPER_TRADING:
        logger.warning("Running in PAPER TRADING mode - no real money at risk")
    else:
        response = input("WARNING: Running in LIVE TRADING mode! Type 'YES' to confirm: ")
        if response != 'YES':
            logger.info("Live trading not confirmed. Exiting.")
            exit(0)

    main()
