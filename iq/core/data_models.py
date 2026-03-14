"""
Data models and structures for IQ Analyzer Pro
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
import pandas as pd


class TradeResult(Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    DRAW = "DRAW"


class TradeType(Enum):
    CALL = "CALL"
    PUT = "PUT"


@dataclass
class Trade:
    """Individual trade data model"""
    id: str
    timestamp: datetime
    asset: str
    trade_type: TradeType
    amount: float
    payout: float
    result: TradeResult
    profit: float
    duration: Optional[int] = None  # in seconds
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    strike_price: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trade to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'asset': self.asset,
            'trade_type': self.trade_type.value,
            'amount': self.amount,
            'payout': self.payout,
            'result': self.result.value,
            'profit': self.profit,
            'duration': self.duration,
            'open_price': self.open_price,
            'close_price': self.close_price,
            'strike_price': self.strike_price
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trade':
        """Create trade from dictionary"""
        return cls(
            id=data['id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            asset=data['asset'],
            trade_type=TradeType(data['trade_type']),
            amount=float(data['amount']),
            payout=float(data['payout']),
            result=TradeResult(data['result']),
            profit=float(data['profit']),
            duration=data.get('duration'),
            open_price=data.get('open_price'),
            close_price=data.get('close_price'),
            strike_price=data.get('strike_price')
        )


@dataclass
class AnalysisResult:
    """Result of trade analysis"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit: float
    total_loss: float
    net_profit: float
    average_profit: float
    average_loss: float
    profit_factor: float
    max_drawdown: float
    max_consecutive_wins: int
    max_consecutive_losses: int
    best_trade: Trade
    worst_trade: Trade
    best_hour: int
    worst_hour: int
    best_asset: str
    worst_asset: str
    equity_curve: List[float]
    trades_by_hour: Dict[int, Dict[str, Any]]
    trades_by_asset: Dict[str, Dict[str, Any]]
    trades_by_weekday: Dict[int, Dict[str, Any]]
    date_range: tuple
    analysis_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary"""
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'total_profit': self.total_profit,
            'total_loss': self.total_loss,
            'net_profit': self.net_profit,
            'average_profit': self.average_profit,
            'average_loss': self.average_loss,
            'profit_factor': self.profit_factor,
            'max_drawdown': self.max_drawdown,
            'max_consecutive_wins': self.max_consecutive_wins,
            'max_consecutive_losses': self.max_consecutive_losses,
            'best_trade': self.best_trade.to_dict(),
            'worst_trade': self.worst_trade.to_dict(),
            'best_hour': self.best_hour,
            'worst_hour': self.worst_hour,
            'best_asset': self.best_asset,
            'worst_asset': self.worst_asset,
            'equity_curve': self.equity_curve,
            'trades_by_hour': self.trades_by_hour,
            'trades_by_asset': self.trades_by_asset,
            'trades_by_weekday': self.trades_by_weekday,
            'date_range': self.date_range,
            'analysis_timestamp': self.analysis_timestamp.isoformat()
        }


@dataclass
class PairScore:
    """AI scoring result for a trading pair"""
    pair: str
    overall_score: float
    trend_score: float
    volatility_score: float
    momentum_score: float
    historical_winrate: float
    session_score: float
    news_impact: float
    confidence: float
    rank: int
    recommendation: str
    scoring_details: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pair score to dictionary"""
        return {
            'pair': self.pair,
            'overall_score': self.overall_score,
            'trend_score': self.trend_score,
            'volatility_score': self.volatility_score,
            'momentum_score': self.momentum_score,
            'historical_winrate': self.historical_winrate,
            'session_score': self.session_score,
            'news_impact': self.news_impact,
            'confidence': self.confidence,
            'rank': self.rank,
            'recommendation': self.recommendation,
            'scoring_details': self.scoring_details,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class MarketData:
    """Market data for analysis"""
    symbol: str
    current_price: float
    bid: float
    ask: float
    volatility: float
    volume: float
    trend_direction: str  # UP, DOWN, SIDEWAYS
    momentum: float
    support_level: Optional[float]
    resistance_level: Optional[float]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'current_price': self.current_price,
            'bid': self.bid,
            'ask': self.ask,
            'volatility': self.volatility,
            'volume': self.volume,
            'trend_direction': self.trend_direction,
            'momentum': self.momentum,
            'support_level': self.support_level,
            'resistance_level': self.resistance_level,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class NewsItem:
    """News data for sentiment analysis"""
    title: str
    content: str
    source: str
    timestamp: datetime
    sentiment: float  # -1 to 1
    impact: str  # LOW, MEDIUM, HIGH
    related_pairs: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'sentiment': self.sentiment,
            'impact': self.impact,
            'related_pairs': self.related_pairs
        }


class DataFrameConverter:
    """Utility class for converting between data models and pandas DataFrames"""
    
    @staticmethod
    def trades_to_dataframe(trades: List[Trade]) -> pd.DataFrame:
        """Convert list of trades to pandas DataFrame"""
        if not trades:
            return pd.DataFrame()
        
        data = [trade.to_dict() for trade in trades]
        df = pd.DataFrame(data)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Add derived columns
        df['hour'] = df['timestamp'].dt.hour
        df['weekday'] = df['timestamp'].dt.dayofweek
        df['date'] = df['timestamp'].dt.date
        
        return df
    
    @staticmethod
    def dataframe_to_trades(df: pd.DataFrame) -> List[Trade]:
        """Convert pandas DataFrame to list of trades"""
        trades = []
        for _, row in df.iterrows():
            trade_dict = row.to_dict()
            trades.append(Trade.from_dict(trade_dict))
        return trades
    
    @staticmethod
    def pair_scores_to_dataframe(scores: List[PairScore]) -> pd.DataFrame:
        """Convert list of pair scores to pandas DataFrame"""
        if not scores:
            return pd.DataFrame()
        
        data = [score.to_dict() for score in scores]
        df = pd.DataFrame(data)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df.sort_values('overall_score', ascending=False)
