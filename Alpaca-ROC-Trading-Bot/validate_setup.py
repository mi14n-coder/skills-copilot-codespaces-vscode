#!/usr/bin/env python3
"""
Setup Validation Script for Alpaca ROC Trading Bot
Run this to verify your configuration before starting the bot
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version {version.major}.{version.minor} is too old. Need 3.8+")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'alpaca',
        'pandas',
        'numpy',
        'dotenv',
        'pytz'
    ]

    missing = []
    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'alpaca':
                __import__('alpaca.trading')
                __import__('alpaca.data')
            else:
                __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not Path('.env').exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        print("   Then edit .env with your Alpaca credentials")
        return False

    print("✅ .env file exists")

    # Load and check variables
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = ['ALPACA_API_KEY', 'ALPACA_SECRET_KEY']
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value or value == 'your_api_key_here' or value == 'your_secret_key_here':
            print(f"❌ {var} not configured")
            missing_vars.append(var)
        else:
            print(f"✅ {var} configured ({value[:8]}...)")

    paper_trading = os.getenv('PAPER_TRADING', 'true')
    if paper_trading.lower() == 'true':
        print("✅ Paper trading mode enabled (SAFE)")
    else:
        print("⚠️  LIVE trading mode enabled (REAL MONEY!)")

    if missing_vars:
        print(f"\n⚠️  Configure these in .env: {', '.join(missing_vars)}")
        return False

    return True

def check_tickers_file():
    """Check if Tickers.txt exists"""
    paths = ['Tickers.txt', 'AUTH/Tickers.txt']

    for path in paths:
        if Path(path).exists():
            with open(path, 'r') as f:
                tickers = f.read().strip().split()
            print(f"✅ {path} exists with {len(tickers)} tickers: {' '.join(tickers[:5])}{'...' if len(tickers) > 5 else ''}")
            return True

    print("❌ Tickers.txt not found")
    print("   Run: cp Tickers.txt.example Tickers.txt")
    print("   Then edit Tickers.txt with your stock symbols")
    return False

def check_api_connection():
    """Try to connect to Alpaca API"""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        from alpaca.trading.client import TradingClient

        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        paper = os.getenv('PAPER_TRADING', 'true').lower() == 'true'

        if not api_key or not secret_key:
            print("⚠️  API credentials not configured, skipping connection test")
            return True

        if api_key == 'your_api_key_here':
            print("⚠️  Using placeholder credentials, skipping connection test")
            return True

        client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)
        account = client.get_account()

        print(f"✅ Connected to Alpaca API")
        print(f"   Account Status: {account.status}")
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")

        return True

    except Exception as e:
        print(f"❌ Failed to connect to Alpaca API: {e}")
        print("   Check your API credentials in .env")
        return False

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("Alpaca ROC Trading Bot - Setup Validation")
    print("=" * 60)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Tickers File", check_tickers_file),
        ("API Connection", check_api_connection),
    ]

    results = []

    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        print("-" * 60)
        result = check_func()
        results.append(result)
        print()

    print("=" * 60)
    print("Validation Summary")
    print("=" * 60)

    all_passed = all(results)

    for (name, _), result in zip(checks, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print()

    if all_passed:
        print("🎉 All checks passed! You're ready to run the bot.")
        print()
        print("Next steps:")
        print("1. Review your configuration in .env")
        print("2. Make sure PAPER_TRADING=true for testing")
        print("3. Run: python main_modernized.py")
        print()
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Create .env: cp .env.example .env")
        print("- Create Tickers.txt: cp Tickers.txt.example Tickers.txt")
        print("- Edit .env with your Alpaca API credentials")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
