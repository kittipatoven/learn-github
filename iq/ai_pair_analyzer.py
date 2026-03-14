"""
ai_pair_analyzer.py - Improved AI pair analyzer with enhanced features
Maintains backward compatibility while providing advanced functionality
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core.ai_engine import AIEngine, ScoringWeights
from core.data_models import MarketData, NewsItem
from utils.helpers import normalize_score
import pandas as pd
import numpy as np
from datetime import datetime


class LegacyAIPairAnalyzer:
    """
    Legacy compatibility wrapper for the original ai_pair_analyzer.py
    Maintains the same function signatures while using the improved AI engine
    """
    
    def __init__(self):
        self.ai_engine = AIEngine()
    
    def news_score(self, news):
        """
        Legacy news scoring function - maintains compatibility
        
        Args:
            news: News data (can be various formats)
            
        Returns:
            float: News score (0-100)
        """
        if isinstance(news, str):
            # Simple sentiment analysis for string input
            positive_words = ['good', 'great', 'excellent', 'positive', 'bullish', 'up']
            negative_words = ['bad', 'terrible', 'negative', 'bearish', 'down']
            
            news_lower = news.lower()
            positive_count = sum(1 for word in positive_words if word in news_lower)
            negative_count = sum(1 for word in negative_words if word in news_lower)
            
            total_words = positive_count + negative_count
            if total_words == 0:
                return 50  # Neutral
            
            score = (positive_count - negative_count) / total_words * 50 + 50
            return normalize_score(score, 0, 100)
        
        return 50  # Default neutral score
    
    def volatility_score(self, iq):
        """
        Legacy volatility scoring - maintains compatibility
        
        Args:
            iq: Market data or volatility value
            
        Returns:
            float: Volatility score (0-100)
        """
        if isinstance(iq, (int, float)):
            volatility = iq
        elif hasattr(iq, 'volatility'):
            volatility = iq.volatility
        else:
            volatility = 1.0  # Default
        
        # Normalize volatility (optimal range: 0.5-2.0)
        if volatility < 0.5:
            return 40
        elif volatility > 2.0:
            return 50
        else:
            return 80 - abs(volatility - 1.0) * 30
    
    def momentum_score(self, iq):
        """
        Legacy momentum scoring - maintains compatibility
        
        Args:
            iq: Market data or momentum value
            
        Returns:
            float: Momentum score (0-100)
        """
        if isinstance(iq, (int, float)):
            momentum = iq
        elif hasattr(iq, 'momentum'):
            momentum = iq.momentum
        else:
            momentum = 0.0  # Default
        
        abs_momentum = abs(momentum)
        
        if abs_momentum < 0.1:
            return 30
        elif abs_momentum < 0.5:
            return 60
        else:
            return 85
    
    def trend_score(self, iq):
        """
        Legacy trend scoring - maintains compatibility
        
        Args:
            iq: Market data or trend direction
            
        Returns:
            float: Trend score (0-100)
        """
        if isinstance(iq, str):
            trend = iq.upper()
        elif hasattr(iq, 'trend_direction'):
            trend = iq.trend_direction.upper()
        else:
            trend = 'SIDEWAYS'  # Default
        
        if trend == 'UP':
            return 75
        elif trend == 'DOWN':
            return 65
        else:
            return 40
    
    def winrate_score(self, trades):
        """
        Legacy winrate scoring - maintains compatibility
        
        Args:
            trades: Trade data or winrate value
            
        Returns:
            float: Winrate score (0-100)
        """
        if isinstance(trades, (int, float)):
            winrate = trades
        elif isinstance(trades, list) and len(trades) > 0:
            # Calculate winrate from trades list
            winning_trades = sum(1 for trade in trades 
                               if hasattr(trade, 'result') and trade.result.value == 'WIN')
            winrate = winning_trades / len(trades)
        elif isinstance(trades, pd.DataFrame):
            # Calculate winrate from DataFrame
            if 'result' in trades.columns:
                winrate = (trades['result'] == 'WIN').mean()
            else:
                winrate = 0.5
        else:
            winrate = 0.5  # Default
        
        # Convert winrate to score
        if winrate >= 0.7:
            return 95
        elif winrate >= 0.6:
            return 80
        elif winrate >= 0.5:
            return 65
        elif winrate >= 0.4:
            return 45
        else:
            return 25
    
    def session_score(self):
        """
        Legacy session scoring - maintains compatibility
        
        Returns:
            float: Session score (0-100)
        """
        from datetime import datetime
        hour = datetime.now().hour
        
        # Define optimal trading sessions
        if 8 <= hour <= 16:  # London session
            return 85
        elif 13 <= hour <= 17:  # NY session
            return 90
        elif 0 <= hour <= 8:  # Asian session
            return 70
        else:
            return 30
    
    def analyze_best_pairs(self, iq, trades, news=None):
        """
        Main analysis function - maintains backward compatibility
        
        Args:
            iq: Market data (can be dict, object, or various formats)
            trades: Trade data (list, DataFrame, etc.)
            news: Optional news data
            
        Returns:
            pandas.DataFrame: Ranked pairs with scores
        """
        # Convert inputs to proper format
        market_data = self._convert_market_data(iq)
        historical_trades = self._convert_trades(trades)
        news_data = self._convert_news(news)
        
        # Run analysis with improved AI engine
        results = self.ai_engine.analyze_best_pairs(market_data, historical_trades, news_data)
        
        # Convert results to DataFrame for compatibility
        from core.data_models import DataFrameConverter
        return DataFrameConverter.pair_scores_to_dataframe(results)
    
    def _convert_market_data(self, iq):
        """
        Convert various input formats to MarketData objects
        
        Args:
            iq: Market data in various formats
            
        Returns:
            dict: MarketData objects by pair
        """
        market_data = {}
        
        if isinstance(iq, dict):
            # Handle dictionary input
            for pair, data in iq.items():
                if isinstance(data, dict):
                    market_data[pair] = MarketData(
                        symbol=pair,
                        current_price=data.get('price', 1.0),
                        bid=data.get('bid', 1.0),
                        ask=data.get('ask', 1.0),
                        volatility=data.get('volatility', 1.0),
                        volume=data.get('volume', 1000000),
                        trend_direction=data.get('trend', 'SIDEWAYS'),
                        momentum=data.get('momentum', 0.0),
                        support_level=data.get('support'),
                        resistance_level=data.get('resistance'),
                        timestamp=datetime.now()
                    )
                else:
                    # Simple object with attributes
                    market_data[pair] = MarketData(
                        symbol=pair,
                        current_price=getattr(data, 'price', 1.0),
                        bid=getattr(data, 'bid', 1.0),
                        ask=getattr(data, 'ask', 1.0),
                        volatility=getattr(data, 'volatility', 1.0),
                        volume=getattr(data, 'volume', 1000000),
                        trend_direction=getattr(data, 'trend_direction', 'SIDEWAYS'),
                        momentum=getattr(data, 'momentum', 0.0),
                        support_level=getattr(data, 'support_level'),
                        resistance_level=getattr(data, 'resistance_level'),
                        timestamp=datetime.now()
                    )
        else:
            # Single object or default pairs
            pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD']
            
            for pair in pairs:
                market_data[pair] = MarketData(
                    symbol=pair,
                    current_price=1.0 + hash(pair) % 1000 / 10000,
                    bid=1.0 + hash(pair) % 1000 / 10000 - 0.0001,
                    ask=1.0 + hash(pair) % 1000 / 10000 + 0.0001,
                    volatility=0.5 + hash(pair) % 100 / 100,
                    volume=1000000 + hash(pair) % 500000,
                    trend_direction=['UP', 'DOWN', 'SIDEWAYS'][hash(pair) % 3],
                    momentum=(hash(pair) % 100 - 50) / 100,
                    support_level=1.0 + hash(pair) % 1000 / 10000 - 0.01,
                    resistance_level=1.0 + hash(pair) % 1000 / 10000 + 0.01,
                    timestamp=datetime.now()
                )
        
        return market_data
    
    def _convert_trades(self, trades):
        """
        Convert various trade formats to Trade objects
        
        Args:
            trades: Trade data in various formats
            
        Returns:
            list: Trade objects
        """
        if not trades:
            return []
        
        from core.trade_parser import TradeParser
        
        parser = TradeParser()
        
        if isinstance(trades, pd.DataFrame):
            return parser.dataframe_to_trades(trades)
        elif isinstance(trades, list):
            if all(isinstance(trade, str) for trade in trades):
                # List of strings - create dummy trades
                return []
            else:
                # Assume list of trade objects or dictionaries
                try:
                    return parser.parse_from_dict(trades)
                except:
                    return []
        else:
            return []
    
    def _convert_news(self, news):
        """
        Convert various news formats to NewsItem objects
        
        Args:
            news: News data in various formats
            
        Returns:
            list: NewsItem objects
        """
        if not news:
            return []
        
        news_data = []
        
        if isinstance(news, list):
            for item in news:
                if isinstance(item, str):
                    # Simple string news
                    news_data.append(NewsItem(
                        title=item[:50],
                        content=item,
                        source="Legacy",
                        timestamp=datetime.now(),
                        sentiment=0.0,
                        impact="MEDIUM",
                        related_pairs=[]
                    ))
                elif isinstance(item, dict):
                    # Dictionary news
                    news_data.append(NewsItem(
                        title=item.get('title', ''),
                        content=item.get('content', ''),
                        source=item.get('source', 'Legacy'),
                        timestamp=datetime.now(),
                        sentiment=item.get('sentiment', 0.0),
                        impact=item.get('impact', 'MEDIUM'),
                        related_pairs=item.get('related_pairs', [])
                    ))
        
        return news_data


# Global instance for compatibility
ai_analyzer = LegacyAIPairAnalyzer()


# Export functions for original compatibility
def news_score(news):
    """Legacy news score function"""
    return ai_analyzer.news_score(news)


def volatility_score(iq):
    """Legacy volatility score function"""
    return ai_analyzer.volatility_score(iq)


def momentum_score(iq):
    """Legacy momentum score function"""
    return ai_analyzer.momentum_score(iq)


def trend_score(iq):
    """Legacy trend score function"""
    return ai_analyzer.trend_score(iq)


def winrate_score(trades):
    """Legacy winrate score function"""
    return ai_analyzer.winrate_score(trades)


def session_score():
    """Legacy session score function"""
    return ai_analyzer.session_score()


def analyze_best_pairs(iq, trades, news=None):
    """Legacy main analysis function"""
    return ai_analyzer.analyze_best_pairs(iq, trades, news)


if __name__ == "__main__":
    # Example usage for testing
    sample_iq = {
        'EUR/USD': {'volatility': 1.2, 'trend': 'UP', 'momentum': 0.3},
        'GBP/USD': {'volatility': 1.5, 'trend': 'DOWN', 'momentum': -0.2}
    }
    
    sample_trades = []  # Empty for demo
    
    results = analyze_best_pairs(sample_iq, sample_trades)
    print("AI Analysis Results:")
    print(results)
