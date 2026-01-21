"""
Virtual Wallet Module
Manages virtual portfolio with realistic trading costs (fees and slippage)
"""


class VirtualWallet:
    """
    Virtual wallet for paper trading with realistic fee simulation.
    
    Attributes:
        usd_balance (float): Current USD balance
        holdings (dict): Dictionary of crypto holdings {symbol: amount}
        fee_rate (float): Trading fee percentage (default 0.1%)
        slippage_rate (float): Slippage percentage (default 0.05%)
    """
    
    def __init__(self, initial_usd=1000.0, fee_rate=0.001, slippage_rate=0.0005):
        """
        Initialize virtual wallet.
        
        Args:
            initial_usd (float): Starting USD balance
            fee_rate (float): Trading fee as decimal (0.001 = 0.1%)
            slippage_rate (float): Slippage as decimal (0.0005 = 0.05%)
        """
        self.usd_balance = initial_usd
        self.holdings = {}  # {symbol: amount}
        self.fee_rate = fee_rate
        self.slippage_rate = slippage_rate
    
    def buy(self, symbol, price, amount_usd):
        """
        Buy cryptocurrency with USD.
        
        Applies trading fee and slippage to simulate realistic costs.
        
        Args:
            symbol (str): Crypto symbol (e.g., 'BTC')
            price (float): Current price per unit
            amount_usd (float): Amount in USD to spend
        
        Returns:
            bool: True if purchase successful, False otherwise
        """
        if amount_usd <= 0:
            print(f"❌ Invalid amount: ${amount_usd}")
            return False
        
        if amount_usd > self.usd_balance:
            print(f"❌ Insufficient funds. Balance: ${self.usd_balance:.2f}, Requested: ${amount_usd:.2f}")
            return False
        
        # Calculate effective price with slippage (buying = higher price)
        effective_price = price * (1 + self.slippage_rate)
        
        # Calculate fee
        fee = amount_usd * self.fee_rate
        
        # Calculate amount of crypto to receive
        net_usd = amount_usd - fee
        crypto_amount = net_usd / effective_price
        
        # Update balances
        self.usd_balance -= amount_usd
        self.holdings[symbol] = self.holdings.get(symbol, 0) + crypto_amount
        
        print(f"✅ BUY: {crypto_amount:.8f} {symbol} @ ${effective_price:.2f} (Fee: ${fee:.2f})")
        return True
    
    def sell(self, symbol, price):
        """
        Sell all holdings of a cryptocurrency.
        
        Applies trading fee and slippage to simulate realistic costs.
        
        Args:
            symbol (str): Crypto symbol to sell
            price (float): Current price per unit
        
        Returns:
            bool: True if sale successful, False otherwise
        """
        if symbol not in self.holdings or self.holdings[symbol] <= 0:
            print(f"❌ No {symbol} holdings to sell")
            return False
        
        crypto_amount = self.holdings[symbol]
        
        # Calculate effective price with slippage (selling = lower price)
        effective_price = price * (1 - self.slippage_rate)
        
        # Calculate gross USD received
        gross_usd = crypto_amount * effective_price
        
        # Calculate fee
        fee = gross_usd * self.fee_rate
        
        # Calculate net USD received
        net_usd = gross_usd - fee
        
        # Update balances
        self.usd_balance += net_usd
        self.holdings[symbol] = 0
        
        print(f"✅ SELL: {crypto_amount:.8f} {symbol} @ ${effective_price:.2f} (Fee: ${fee:.2f})")
        return True
    
    def get_total_value(self, current_prices):
        """
        Calculate total portfolio value in USD.
        
        Args:
            current_prices (dict): Dictionary of current prices {symbol: price}
        
        Returns:
            float: Total portfolio value in USD
        """
        total = self.usd_balance
        
        for symbol, amount in self.holdings.items():
            if amount > 0 and symbol in current_prices:
                total += amount * current_prices[symbol]
        
        return total
    
    def get_state(self):
        """
        Get current wallet state for persistence.
        
        Returns:
            dict: Wallet state dictionary
        """
        return {
            'usd_balance': self.usd_balance,
            'holdings': self.holdings.copy()
        }
    
    def load_state(self, state):
        """
        Load wallet state from saved data.
        
        Args:
            state (dict): Saved wallet state
        """
        self.usd_balance = state.get('usd_balance', 1000.0)
        self.holdings = state.get('holdings', {})
    
    def __str__(self):
        """String representation of wallet."""
        holdings_str = ", ".join([f"{amount:.8f} {symbol}" for symbol, amount in self.holdings.items() if amount > 0])
        if not holdings_str:
            holdings_str = "None"
        return f"Wallet(USD: ${self.usd_balance:.2f}, Holdings: {holdings_str})"
