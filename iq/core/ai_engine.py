"""
AI Engine - Advanced pair scoring and analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass

from data_models import Trade, PairScore, MarketData, NewsItem


@dataclass
class ScoringWeights:
    """Weights for different scoring factors"""
    trend_weight: float = 0.25
    volatility_weight: float = 0.20
    momentum_weight: float = 0.15
    historical_winrate_weight: float = 0.20
    session_weight: float = 0.10
    news_weight: float = 0.10


class AIEngine:
    """Advanced AI engine for pair scoring and analysis"""
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        self.logger = logging.getLogger(__name__)
        self.weights = weights or ScoringWeights()
        self.confidence_threshold = 0.6
        
    def analyze_best_pairs(self, 
                          market_data: Dict[str, MarketData],
                          historical_trades: List[Trade],
                          news_data: Optional[List[NewsItem]] = None) -> List[PairScore]:
        """
        Analyze and rank trading pairs using advanced AI scoring
        
        Args:
            market_data: Dictionary of market data by pair
            historical_trades: List of historical trades
            news_data: Optional news data for sentiment analysis
            
        Returns:
            List of PairScore objects ranked by overall score
        """
        self.logger.info("Starting AI pair analysis...")
        
        # Prepare historical data
        trades_df = self._prepare_trades_dataframe(historical_trades)
        
        # Calculate scores for each pair
        pair_scores = []
        for pair, data in market_data.items():
            try:
                score = self._calculate_pair_score(pair, data, trades_df, news_data)
                pair_scores.append(score)
            except Exception as e:
                self.logger.warning(f"Error calculating score for {pair}: {str(e)}")
                continue
        
        # Sort by overall score and assign ranks
        pair_scores.sort(key=lambda x: x.overall_score, reverse=True)
        for i, score in enumerate(pair_scores):
            score.rank = i + 1
            score.recommendation = self._get_recommendation(score)
        
        self.logger.info(f"AI analysis complete. Analyzed {len(pair_scores)} pairs")
        return pair_scores
    
    def _calculate_pair_score(self, 
                              pair: str, 
                              market_data: MarketData,
                              trades_df: pd.DataFrame,
                              news_data: Optional[List[NewsItem]] = None) -> PairScore:
        """Calculate comprehensive score for a single pair"""
        
        # Calculate individual scores
        trend_score = self._calculate_trend_score(market_data)
        volatility_score = self._calculate_volatility_score(market_data, trades_df)
        momentum_score = self._calculate_momentum_score(market_data)
        historical_score = self._calculate_historical_winrate(pair, trades_df)
        session_score = self._calculate_session_score(pair, market_data)
        news_score = self._calculate_news_impact(pair, news_data)
        
        # Calculate weighted overall score
        overall_score = (
            trend_score * self.weights.trend_weight +
            volatility_score * self.weights.volatility_weight +
            momentum_score * self.weights.momentum_weight +
            historical_score * self.weights.historical_winrate_weight +
            session_score * self.weights.session_weight +
            news_score * self.weights.news_weight
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            trend_score, volatility_score, momentum_score, 
            historical_score, trades_df, pair
        )
        
        # Prepare scoring details
        scoring_details = {
            'trend_analysis': {
                'score': trend_score,
                'direction': market_data.trend_direction,
                'strength': market_data.momentum
            },
            'volatility_analysis': {
                'score': volatility_score,
                'current_volatility': market_data.volatility,
                'normalized_volatility': self._normalize_volatility(market_data.volatility)
            },
            'momentum_analysis': {
                'score': momentum_score,
                'momentum_value': market_data.momentum,
                'momentum_trend': self._classify_momentum(market_data.momentum)
            },
            'historical_performance': {
                'score': historical_score,
                'winrate': self._get_pair_winrate(pair, trades_df),
                'total_trades': self._get_pair_trade_count(pair, trades_df)
            },
            'session_analysis': {
                'score': session_score,
                'current_session': self._get_current_session(),
                'optimal_sessions': self._get_optimal_sessions(pair, trades_df)
            },
            'news_analysis': {
                'score': news_score,
                'sentiment': self._get_news_sentiment(pair, news_data),
                'recent_news_count': self._get_news_count(pair, news_data)
            }
        }
        
        return PairScore(
            pair=pair,
            overall_score=round(overall_score, 2),
            trend_score=round(trend_score, 2),
            volatility_score=round(volatility_score, 2),
            momentum_score=round(momentum_score, 2),
            historical_winrate=round(historical_score, 2),
            session_score=round(session_score, 2),
            news_impact=round(news_score, 2),
            confidence=round(confidence, 2),
            rank=0,  # Will be assigned later
            recommendation="",  # Will be assigned later
            scoring_details=scoring_details,
            timestamp=datetime.now()
        )
    
    def _calculate_trend_score(self, market_data: MarketData) -> float:
        """Calculate trend score based on market data"""
        trend_direction = market_data.trend_direction.upper()
        momentum = abs(market_data.momentum)
        
        # Base score from trend direction
        if trend_direction == 'UP':
            base_score = 70
        elif trend_direction == 'DOWN':
            base_score = 60
        else:  # SIDEWAYS
            base_score = 40
        
        # Adjust based on momentum strength
        momentum_bonus = min(momentum * 10, 30)  # Max 30 points bonus
        
        return min(base_score + momentum_bonus, 100)
    
    def _calculate_volatility_score(self, market_data: MarketData, trades_df: pd.DataFrame) -> float:
        """Calculate normalized volatility score"""
        current_volatility = market_data.volatility
        
        # Get historical volatility for this pair if available
        if not trades_df.empty:
            pair_trades = trades_df[trades_df['asset'] == market_data.symbol]
            if not pair_trades.empty:
                # Calculate historical volatility proxy
                historical_vol = pair_trades['profit'].std() if len(pair_trades) > 1 else current_volatility
                normalized_vol = current_volatility / max(historical_vol, 0.001)
            else:
                normalized_vol = current_volatility
        else:
            normalized_vol = current_volatility
        
        # Normalize to 0-100 scale (optimal range: 0.5-2.0)
        if normalized_vol < 0.5:
            return 40  # Too low volatility
        elif normalized_vol > 2.0:
            return 50  # Too high volatility
        else:
            # Optimal range gets higher scores
            return 80 - abs(normalized_vol - 1.0) * 30
    
    def _calculate_momentum_score(self, market_data: MarketData) -> float:
        """Calculate momentum score"""
        momentum = market_data.momentum
        
        # Normalize momentum to 0-100 scale
        if abs(momentum) < 0.1:
            return 30  # Low momentum
        elif abs(momentum) < 0.5:
            return 60  # Moderate momentum
        else:
            return 85  # High momentum
    
    def _calculate_historical_winrate(self, pair: str, trades_df: pd.DataFrame) -> float:
        """Calculate historical winrate score for a pair"""
        if trades_df.empty:
            return 50  # Neutral score if no data
        
        pair_trades = trades_df[trades_df['asset'] == pair]
        if pair_trades.empty:
            return 50  # Neutral score for new pairs
        
        winrate = (pair_trades['result'] == 'WIN').mean()
        
        # Convert winrate to score (0-100 scale)
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
    
    def _calculate_session_score(self, pair: str, market_data: MarketData) -> float:
        """Calculate session-based score"""
        current_hour = datetime.now().hour
        
        # Define optimal trading sessions for different pairs
        session_optimization = {
            'EUR/USD': [(8, 16), (13, 17)],  # London + NY overlap
            'GBP/USD': [(8, 16), (13, 17)],
            'USD/JPY': [(0, 8), (13, 17)],   # Tokyo + NY
            'AUD/USD': [(0, 8)],             # Sydney/Tokyo
            'USD/CAD': [(13, 17)],           # NY session
        }
        
        optimal_sessions = session_optimization.get(pair, [(8, 16)])
        
        # Check if current time is in optimal session
        for start, end in optimal_sessions:
            if start <= current_hour <= end:
                return 90
        
        # Partial score for nearby hours
        for start, end in optimal_sessions:
            if abs(current_hour - start) <= 2 or abs(current_hour - end) <= 2:
                return 60
        
        return 30  # Low score for suboptimal times
    
    def _calculate_news_impact(self, pair: str, news_data: Optional[List[NewsItem]] = None) -> float:
        """Calculate news impact score"""
        if not news_data:
            return 50  # Neutral score
        
        recent_news = [
            news for news in news_data 
            if pair in news.related_pairs and 
            (datetime.now() - news.timestamp).hours <= 24
        ]
        
        if not recent_news:
            return 50  # No recent news
        
        # Calculate sentiment score
        total_sentiment = sum(news.sentiment for news in recent_news)
        avg_sentiment = total_sentiment / len(recent_news)
        
        # Convert sentiment (-1 to 1) to score (0-100)
        sentiment_score = (avg_sentiment + 1) * 50
        
        # Adjust for news impact level
        high_impact_count = sum(1 for news in recent_news if news.impact == 'HIGH')
        if high_impact_count > 0:
            sentiment_score *= 0.7  # Reduce score for high-impact news (higher risk)
        
        return max(0, min(100, sentiment_score))
    
    def _calculate_confidence(self, 
                             trend_score: float,
                             volatility_score: float,
                             momentum_score: float,
                             historical_score: float,
                             trades_df: pd.DataFrame,
                             pair: str) -> float:
        """Calculate confidence score for the prediction"""
        
        # Base confidence from score consistency
        scores = [trend_score, volatility_score, momentum_score, historical_score]
        score_std = np.std(scores)
        consistency_score = max(0, 100 - score_std * 2)
        
        # Data volume confidence
        pair_trades = trades_df[trades_df['asset'] == pair]
        if len(pair_trades) >= 100:
            data_confidence = 90
        elif len(pair_trades) >= 50:
            data_confidence = 75
        elif len(pair_trades) >= 20:
            data_confidence = 60
        else:
            data_confidence = 40
        
        # Overall confidence is weighted average
        overall_confidence = (consistency_score * 0.6 + data_confidence * 0.4)
        
        return round(overall_confidence, 2)
    
    def _get_recommendation(self, score: PairScore) -> str:
        """Generate trading recommendation based on score"""
        if score.overall_score >= 80 and score.confidence >= 70:
            return "STRONG BUY"
        elif score.overall_score >= 70 and score.confidence >= 60:
            return "BUY"
        elif score.overall_score >= 60 and score.confidence >= 50:
            return "CONSIDER"
        elif score.overall_score <= 40:
            return "AVOID"
        else:
            return "HOLD"
    
    def _prepare_trades_dataframe(self, trades: List[Trade]) -> pd.DataFrame:
        """Prepare trades DataFrame for analysis"""
        if not trades:
            return pd.DataFrame()
        
        data = [trade.to_dict() for trade in trades]
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['weekday'] = df['timestamp'].dt.dayofweek
        
        return df
    
    def _normalize_volatility(self, volatility: float) -> float:
        """Normalize volatility value"""
        # Assuming typical volatility range of 0.1 to 2.0
        return min(max(volatility / 1.0, 0.1), 2.0)
    
    def _classify_momentum(self, momentum: float) -> str:
        """Classify momentum strength"""
        if abs(momentum) < 0.1:
            return "WEAK"
        elif abs(momentum) < 0.5:
            return "MODERATE"
        else:
            return "STRONG"
    
    def _get_pair_winrate(self, pair: str, trades_df: pd.DataFrame) -> float:
        """Get historical winrate for a pair"""
        if trades_df.empty:
            return 0.5
        
        pair_trades = trades_df[trades_df['asset'] == pair]
        if pair_trades.empty:
            return 0.5
        
        return (pair_trades['result'] == 'WIN').mean()
    
    def _get_pair_trade_count(self, pair: str, trades_df: pd.DataFrame) -> int:
        """Get number of trades for a pair"""
        if trades_df.empty:
            return 0
        
        return len(trades_df[trades_df['asset'] == pair])
    
    def _get_current_session(self) -> str:
        """Get current trading session"""
        hour = datetime.now().hour
        
        if 0 <= hour < 8:
            return "ASIAN"
        elif 8 <= hour < 13:
            return "LONDON"
        elif 13 <= hour < 17:
            return "NEW_YORK"
        else:
            return "OFF_HOURS"
    
    def _get_optimal_sessions(self, pair: str, trades_df: pd.DataFrame) -> List[str]:
        """Get optimal trading sessions for a pair based on historical performance"""
        if trades_df.empty:
            return ["LONDON", "NEW_YORK"]
        
        pair_trades = trades_df[trades_df['asset'] == pair]
        if pair_trades.empty:
            return ["LONDON", "NEW_YORK"]
        
        # Calculate winrate by hour
        hourly_performance = pair_trades.groupby('hour').apply(
            lambda x: (x['result'] == 'WIN').mean()
        )
        
        # Find best performing hours
        best_hours = hourly_performance.nlargest(3).index.tolist()
        
        # Convert hours to sessions
        sessions = []
        for hour in best_hours:
            if 0 <= hour < 8:
                sessions.append("ASIAN")
            elif 8 <= hour < 13:
                sessions.append("LONDON")
            elif 13 <= hour < 17:
                sessions.append("NEW_YORK")
        
        return list(set(sessions))
    
    def _get_news_sentiment(self, pair: str, news_data: Optional[List[NewsItem]] = None) -> float:
        """Get average news sentiment for a pair"""
        if not news_data:
            return 0.0
        
        pair_news = [
            news for news in news_data 
            if pair in news.related_pairs and 
            (datetime.now() - news.timestamp).hours <= 24
        ]
        
        if not pair_news:
            return 0.0
        
        return sum(news.sentiment for news in pair_news) / len(pair_news)
    
    def _get_news_count(self, pair: str, news_data: Optional[List[NewsItem]] = None) -> int:
        """Get count of recent news for a pair"""
        if not news_data:
            return 0
        
        return len([
            news for news in news_data 
            if pair in news.related_pairs and 
            (datetime.now() - news.timestamp).hours <= 24
        ])
    
    def update_weights(self, new_weights: ScoringWeights):
        """Update scoring weights"""
        self.weights = new_weights
        self.logger.info("Updated AI scoring weights")
    
    def get_detailed_analysis(self, score: PairScore) -> Dict[str, Any]:
        """Get detailed analysis for a pair score"""
        return {
            'pair': score.pair,
            'overall_assessment': {
                'score': score.overall_score,
                'rank': score.rank,
                'recommendation': score.recommendation,
                'confidence': score.confidence
            },
            'detailed_scores': score.scoring_details,
            'strengths': self._identify_strengths(score),
            'weaknesses': self._identify_weaknesses(score),
            'risk_factors': self._identify_risk_factors(score)
        }
    
    def _identify_strengths(self, score: PairScore) -> List[str]:
        """Identify strengths for a pair"""
        strengths = []
        
        if score.trend_score >= 70:
            strengths.append("Strong trend direction")
        if score.volatility_score >= 70:
            strengths.append("Optimal volatility levels")
        if score.momentum_score >= 70:
            strengths.append("High momentum")
        if score.historical_winrate >= 70:
            strengths.append("Strong historical performance")
        if score.session_score >= 70:
            strengths.append("Optimal trading session")
        if score.news_impact >= 60:
            strengths.append("Positive news sentiment")
        
        return strengths
    
    def _identify_weaknesses(self, score: PairScore) -> List[str]:
        """Identify weaknesses for a pair"""
        weaknesses = []
        
        if score.trend_score <= 40:
            weaknesses.append("Weak or unclear trend")
        if score.volatility_score <= 40:
            weaknesses.append("Unfavorable volatility")
        if score.momentum_score <= 40:
            weaknesses.append("Low momentum")
        if score.historical_winrate <= 40:
            weaknesses.append("Poor historical performance")
        if score.session_score <= 40:
            weaknesses.append("Suboptimal trading session")
        if score.news_impact <= 40:
            weaknesses.append("Negative news sentiment")
        
        return weaknesses
    
    def _identify_risk_factors(self, score: PairScore) -> List[str]:
        """Identify risk factors for a pair"""
        risks = []
        
        if score.confidence < 50:
            risks.append("Low confidence in prediction")
        
        if score.scoring_details['volatility_analysis']['current_volatility'] > 2.0:
            risks.append("High volatility - increased risk")
        
        if score.scoring_details['news_analysis']['recent_news_count'] > 5:
            risks.append("High news activity - potential volatility")
        
        if score.scoring_details['historical_performance']['total_trades'] < 20:
            risks.append("Limited historical data")
        
        return risks
