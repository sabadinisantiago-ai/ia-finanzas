"""
Paper Trading Bot - Main Orchestration Script

Simulates a trading competition between 3 different strategies:
- AgentClaude: AI-powered sentiment analysis
- RoboQuant: Technical analysis (RSI)
- WhaleHunter: Whale tracking simulation

Runs automatically via GitHub Actions every 12 hours.
"""

from datetime import datetime
from src.wallet import VirtualWallet
from src.bots import create_bots
from src.utils import (
    get_btc_price,
    get_historical_prices,
    save_state,
    load_state,
    generate_chart
)


def main():
    """Main execution function."""
    
    print("=" * 60)
    print("🤖 PAPER TRADING BOT - Trading Competition")
    print("=" * 60)
    print(f"⏰ Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load previous state
    state = load_state()
    if not state:
        print("❌ Failed to load state. Exiting.")
        return
    
    # Fetch current market data
    print("\n📊 Fetching Market Data...")
    current_price = get_btc_price()
    
    if not current_price:
        print("❌ Failed to fetch BTC price. Exiting.")
        return
    
    historical_data = get_historical_prices(limit=100)
    
    # Create bots
    bots = create_bots()
    
    # Initialize wallets for each bot
    wallets = {}
    for bot_name, bot in bots.items():
        wallet = VirtualWallet()
        wallet.load_state(state['bots'][bot_name])
        wallets[bot_name] = wallet
    
    print("\n" + "=" * 60)
    print("💼 Current Portfolio Status")
    print("=" * 60)
    
    for bot_name, wallet in wallets.items():
        total_value = wallet.get_total_value({'BTC': current_price})
        print(f"{bot_name}: ${total_value:.2f}")
    
    # Execute trading logic for each bot
    print("\n" + "=" * 60)
    print("🎯 Executing Trading Decisions")
    print("=" * 60)
    
    for bot_name, bot in bots.items():
        print(f"\n--- {bot_name} ---")
        wallet = wallets[bot_name]
        
        # Get bot's decision
        decision = bot.decide(current_price, historical_data)
        
        # Execute decision
        if decision == "BUY":
            # Use 90% of available USD balance
            amount_to_invest = wallet.usd_balance * 0.9
            if amount_to_invest > 10:  # Minimum $10 trade
                wallet.buy('BTC', current_price, amount_to_invest)
            else:
                print(f"⚠️ Insufficient funds to buy (${wallet.usd_balance:.2f})")
        
        elif decision == "SELL":
            if 'BTC' in wallet.holdings and wallet.holdings['BTC'] > 0:
                wallet.sell('BTC', current_price)
            else:
                print(f"⚠️ No BTC to sell")
        
        else:  # HOLD
            print(f"⏸️ HOLD - No action taken")
        
        # Show updated balance
        total_value = wallet.get_total_value({'BTC': current_price})
        print(f"💰 New Balance: ${total_value:.2f}")
    
    # Save updated state
    print("\n" + "=" * 60)
    print("💾 Saving State")
    print("=" * 60)
    
    # Update state with new balances
    for bot_name, wallet in wallets.items():
        state['bots'][bot_name] = wallet.get_state()
    
    # Add to history
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'btc_price': current_price,
        'bots': {
            bot_name: wallets[bot_name].get_total_value({'BTC': current_price})
            for bot_name in bots.keys()
        }
    }
    
    state['history'].append(snapshot)
    
    # Save to file
    save_state(state)
    
    # Generate performance chart
    print("\n" + "=" * 60)
    print("📊 Generating Performance Chart")
    print("=" * 60)
    
    generate_chart(state['history'])
    
    # Final summary
    print("\n" + "=" * 60)
    print("📈 Final Summary")
    print("=" * 60)
    
    results = []
    for bot_name in bots.keys():
        total_value = wallets[bot_name].get_total_value({'BTC': current_price})
        profit_loss = total_value - 1000.0
        profit_loss_pct = (profit_loss / 1000.0) * 100
        results.append((bot_name, total_value, profit_loss, profit_loss_pct))
    
    # Sort by performance
    results.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (bot_name, total_value, profit_loss, profit_loss_pct) in enumerate(results, 1):
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        sign = "+" if profit_loss >= 0 else ""
        print(f"{emoji} {rank}. {bot_name}: ${total_value:.2f} ({sign}${profit_loss:.2f} / {sign}{profit_loss_pct:.2f}%)")
    
    print("\n" + "=" * 60)
    print("✅ Execution Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
