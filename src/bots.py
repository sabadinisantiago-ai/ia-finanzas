"""
Trading Bots Module
Implements 3 different trading strategies competing against each other
"""

import random
import os
from abc import ABC, abstractmethod
import pandas as pd
import pandas_ta as ta


class TradingBot(ABC):
    """
    Abstract base class for trading bots.
    
    All trading strategies must inherit from this class and implement
    the decide() method.
    """
    
    def __init__(self, name):
        """
        Initialize trading bot.
        
        Args:
            name (str): Bot name
        """
        self.name = name
    
    @abstractmethod
    def decide(self, current_price, historical_data):
        """
        Make trading decision based on current market conditions.
        
        Args:
            current_price (float): Current BTC price
            historical_data (list): Historical OHLCV data
        
        Returns:
            str: Decision - "BUY", "SELL", or "HOLD"
        """
        pass
    
    def __str__(self):
        return f"{self.name} Trading Bot"


class AgentClaude(TradingBot):
    """
    AI-Powered Trading Bot using Anthropic's Claude API.
    
    Analyzes market sentiment from news and makes decisions using AI.
    Falls back to random decisions when API key is not configured.
    """
    
    def __init__(self):
        super().__init__("AgentClaude")
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
    
    def decide(self, current_price, historical_data):
        """
        Make AI-powered trading decision.
        
        Uses Claude API to analyze market conditions and news sentiment.
        Falls back to random decisions if API key not available.
        """
        if not self.api_key:
            print(f"⚠️ {self.name}: No API key found, using random decision")
            return random.choice(["BUY", "SELL", "HOLD"])
        
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.api_key)
            
            # Prepare market context
            price_change = 0
            if len(historical_data) >= 2:
                old_price = historical_data[-2][4]  # Close price
                price_change = ((current_price - old_price) / old_price) * 100
            
            prompt = f"""You are a cryptocurrency trading expert. Analyze the current market conditions and provide a trading decision.

Current BTC Price: ${current_price:,.2f}
Recent Price Change: {price_change:+.2f}%

Based on this information, should I BUY, SELL, or HOLD Bitcoin?
Respond with ONLY one word: BUY, SELL, or HOLD."""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            
            decision = message.content[0].text.strip().upper()
            
            # Validate decision
            if decision not in ["BUY", "SELL", "HOLD"]:
                print(f"⚠️ {self.name}: Invalid AI response '{decision}', defaulting to HOLD")
                decision = "HOLD"
            
            print(f"🤖 {self.name}: AI Decision = {decision}")
            return decision
            
        except Exception as e:
            print(f"❌ {self.name}: API Error - {e}. Using random decision.")
            return random.choice(["BUY", "SELL", "HOLD"])


class RoboQuant(TradingBot):
    """
    Technical Analysis Bot using RSI (Relative Strength Index).
    
    Strategy:
    - BUY when RSI < 30 (oversold)
    - SELL when RSI > 70 (overbought)
    - HOLD otherwise
    """
    
    def __init__(self):
        super().__init__("RoboQuant")
    
    def decide(self, current_price, historical_data):
        """
        Make decision based on RSI indicator.
        
        Calculates 14-period RSI and applies mean-reversion strategy.
        """
        if not historical_data or len(historical_data) < 14:
            print(f"⚠️ {self.name}: Insufficient data for RSI calculation, HOLD")
            return "HOLD"
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(historical_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Calculate RSI using pandas-ta
            df['rsi'] = ta.rsi(df['close'], length=14)
            
            # Get latest RSI
            current_rsi = df['rsi'].iloc[-1]
            
            if pd.isna(current_rsi):
                print(f"⚠️ {self.name}: RSI calculation failed, HOLD")
                return "HOLD"
            
            # Trading logic
            if current_rsi < 30:
                decision = "BUY"
                print(f"📉 {self.name}: RSI = {current_rsi:.2f} (Oversold) → {decision}")
            elif current_rsi > 70:
                decision = "SELL"
                print(f"📈 {self.name}: RSI = {current_rsi:.2f} (Overbought) → {decision}")
            else:
                decision = "HOLD"
                print(f"➡️ {self.name}: RSI = {current_rsi:.2f} (Neutral) → {decision}")
            
            return decision
            
        except Exception as e:
            print(f"❌ {self.name}: Error calculating RSI - {e}")
            return "HOLD"


class WhaleHunter(TradingBot):
    """
    Whale Tracking Bot - Simulates copying large transactions.
    
    Currently uses random decisions with a "luck" factor.
    
    FUTURE ENHANCEMENT:
    - Integrate with Etherscan API to track large BTC transfers
    - Monitor whale wallets and copy their moves
    - Analyze on-chain metrics for institutional activity
    """
    
    def __init__(self):
        super().__init__("WhaleHunter")
        self.luck_factor = random.uniform(0.4, 0.6)  # Simulated success rate
    
    def decide(self, current_price, historical_data):
        """
        Make decision based on simulated whale activity.
        
        TODO: Replace with real whale tracking using Etherscan API
        Example endpoint: https://api.etherscan.io/api?module=account&action=txlist&address=WHALE_ADDRESS
        
        For now, uses weighted random decisions to simulate whale-following strategy.
        """
        # Simulate whale detection with luck factor
        whale_detected = random.random() < self.luck_factor
        
        if whale_detected:
            # Simulate whale action
            whale_action = random.choice(["BUY", "BUY", "SELL"])  # Whales buy more often
            print(f"🐋 {self.name}: Whale detected! Copying action → {whale_action}")
            return whale_action
        else:
            print(f"🔍 {self.name}: No whale activity detected → HOLD")
            return "HOLD"
        
        # TODO: Implement real whale tracking
        # 1. Fetch large transactions from Etherscan
        # 2. Analyze transaction patterns
        # 3. Identify accumulation/distribution phases
        # 4. Make informed decisions based on whale behavior


def create_bots():
    """
    Factory function to create all trading bots.
    
    Returns:
        dict: Dictionary of bot instances {name: bot_instance}
    """
    return {
        'AgentClaude': AgentClaude(),
        'RoboQuant': RoboQuant(),
        'WhaleHunter': WhaleHunter()
    }
