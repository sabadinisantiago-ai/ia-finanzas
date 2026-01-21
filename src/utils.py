"""
Utility Functions Module
Handles market data fetching, state persistence, and chart generation
"""

import json
import os
from datetime import datetime
import ccxt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def get_btc_price():
    """
    Fetch current BTC/USDT price from Binance.
    
    Returns:
        float: Current BTC price in USDT, or None if error
    """
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker('BTC/USDT')
        price = ticker['last']
        print(f"📊 Current BTC Price: ${price:,.2f}")
        return price
    except Exception as e:
        print(f"❌ Error fetching BTC price: {e}")
        return None


def get_historical_prices(symbol='BTC/USDT', timeframe='1h', limit=100):
    """
    Fetch historical OHLCV data for technical analysis.
    
    Args:
        symbol (str): Trading pair symbol
        timeframe (str): Candlestick timeframe (1m, 5m, 1h, 1d, etc.)
        limit (int): Number of candles to fetch
    
    Returns:
        list: List of OHLCV data [timestamp, open, high, low, close, volume]
    """
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        print(f"📈 Fetched {len(ohlcv)} historical candles for {symbol}")
        return ohlcv
    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        return []


def save_state(data, filename='data.json'):
    """
    Save trading state to JSON file.
    
    Args:
        data (dict): State data to save
        filename (str): Output filename
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 State saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving state: {e}")


def load_state(filename='data.json'):
    """
    Load trading state from JSON file.
    
    If file doesn't exist, returns initial state with $1000 per bot.
    
    Args:
        filename (str): Input filename
    
    Returns:
        dict: Loaded state or initial state
    """
    if not os.path.exists(filename):
        print(f"📝 No existing state found. Initializing with $1000 per bot.")
        return {
            'bots': {
                'AgentClaude': {'usd_balance': 1000.0, 'holdings': {}},
                'RoboQuant': {'usd_balance': 1000.0, 'holdings': {}},
                'WhaleHunter': {'usd_balance': 1000.0, 'holdings': {}}
            },
            'history': [],
            'start_date': datetime.now().isoformat()
        }
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        print(f"📂 State loaded from {filename}")
        return data
    except Exception as e:
        print(f"❌ Error loading state: {e}")
        return None


def generate_chart(history, output_file='status.png'):
    """
    Generate performance comparison chart with dark theme.
    
    Args:
        history (list): List of historical snapshots
        output_file (str): Output image filename
    """
    if not history or len(history) < 2:
        print("⚠️ Not enough history data to generate chart")
        return
    
    try:
        # Use dark background style
        plt.style.use('dark_background')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Extract data
        timestamps = [datetime.fromisoformat(h['timestamp']) for h in history]
        
        bots = ['AgentClaude', 'RoboQuant', 'WhaleHunter']
        colors = ['#00FFFF', '#FF00FF', '#00FF00']  # Cyan, Magenta, Lime Green
        
        # Plot each bot's performance
        for bot_name, color in zip(bots, colors):
            values = [h['bots'][bot_name] for h in history]
            ax.plot(timestamps, values, label=bot_name, color=color, linewidth=2.5, marker='o', markersize=4)
        
        # Formatting
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Portfolio Value (USD)', fontsize=12, fontweight='bold')
        ax.set_title('🤖 Paper Trading Bot Competition - Performance Comparison', 
                     fontsize=16, fontweight='bold', pad=20)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45, ha='right')
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Legend
        ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
        
        # Add starting line
        ax.axhline(y=1000, color='white', linestyle='--', alpha=0.5, linewidth=1, label='Starting Capital')
        
        # Tight layout
        plt.tight_layout()
        
        # Save
        plt.savefig(output_file, dpi=150, facecolor='#0a0a0a')
        print(f"📊 Chart saved to {output_file}")
        
        plt.close()
        
    except Exception as e:
        print(f"❌ Error generating chart: {e}")


def get_crypto_news():
    """
    Fetch recent cryptocurrency news (placeholder for future implementation).
    
    Returns:
        list: List of news articles
    """
    # TODO: Integrate with a news API (e.g., CryptoPanic, NewsAPI)
    # For now, return placeholder
    return [
        {"title": "Bitcoin reaches new milestone", "sentiment": "positive"},
        {"title": "Market shows volatility", "sentiment": "neutral"}
    ]
