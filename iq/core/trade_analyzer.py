"""
Trade Analyzer Module - Comprehensive trade analysis and statistics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
from collections import defaultdict

from core.data_models import Trade, AnalysisResult, TradeType, TradeResult, DataFrameConverter
from core.metrics_calculator import MetricsCalculator


class TradeAnalyzer:
    """Comprehensive trade analysis and statistics calculator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_calculator = MetricsCalculator()
    
    def analyze_trades(self, 
                      trades: List[Trade],
                      date_range: Optional[Tuple[datetime, datetime]] = None) -> AnalysisResult:
        """
        Perform comprehensive analysis of trade data
        
        Args:
            trades: List of trades to analyze
            date_range: Optional date range filter
            
        Returns:
            AnalysisResult object with comprehensive statistics
        """
        self.logger.info(f"Starting analysis of {len(trades)} trades")
        
        if not trades:
            return self._create_empty_result()
        
        # Convert to DataFrame for easier analysis
        df = DataFrameConverter.trades_to_dataframe(trades)
        
        # Apply date filter if provided
        if date_range:
            start_date, end_date = date_range
            df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
        
        if df.empty:
            return self._create_empty_result()
        
        # Calculate basic statistics
        basic_stats = self._calculate_basic_stats(df)
        
        # Calculate time-based analysis
        time_analysis = self._analyze_time_patterns(df)
        
        # Calculate asset-based analysis
        asset_analysis = self._analyze_asset_performance(df)
        
        # Calculate equity curve and drawdown
        equity_analysis = self._calculate_equity_analysis(df)
        
        # Find best and worst trades
        best_trade, worst_trade = self._find_extreme_trades(df)
        
        # Compile comprehensive result
        result = AnalysisResult(
            total_trades=len(df),
            winning_trades=basic_stats['winning_trades'],
            losing_trades=basic_stats['losing_trades'],
            win_rate=basic_stats['win_rate'],
            total_profit=basic_stats['total_profit'],
            total_loss=basic_stats['total_loss'],
            net_profit=basic_stats['net_profit'],
            average_profit=basic_stats['average_profit'],
            average_loss=basic_stats['average_loss'],
            profit_factor=basic_stats['profit_factor'],
            max_drawdown=equity_analysis['max_drawdown'],
            max_consecutive_wins=basic_stats['max_consecutive_wins'],
            max_consecutive_losses=basic_stats['max_consecutive_losses'],
            best_trade=best_trade,
            worst_trade=worst_trade,
            best_hour=time_analysis['best_hour'],
            worst_hour=time_analysis['worst_hour'],
            best_asset=asset_analysis['best_asset'],
            worst_asset=asset_analysis['worst_asset'],
            equity_curve=equity_analysis['equity_curve'],
            trades_by_hour=time_analysis['trades_by_hour'],
            trades_by_asset=asset_analysis['trades_by_asset'],
            trades_by_weekday=time_analysis['trades_by_weekday'],
            date_range=(df['timestamp'].min(), df['timestamp'].max()),
            analysis_timestamp=datetime.now()
        )
        
        self.logger.info(f"Analysis complete. Win rate: {result.win_rate:.2%}, Net profit: {result.net_profit:.2f}")
        return result
    
    def analyze_date_range(self, 
                          trades: List[Trade],
                          start_date: datetime,
                          end_date: datetime) -> Dict[str, Any]:
        """
        Analyze trades within a specific date range with enhanced metrics
        
        Args:
            trades: List of trades to analyze
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with comprehensive date range analysis
        """
        self.logger.info(f"Analyzing date range: {start_date} to {end_date}")
        
        # Filter trades by date range
        filtered_trades = [
            trade for trade in trades 
            if start_date <= trade.timestamp <= end_date
        ]
        
        if not filtered_trades:
            return self._create_empty_date_range_result(start_date, end_date)
        
        # Perform full analysis
        analysis = self.analyze_trades(filtered_trades, (start_date, end_date))
        
        # Additional date range specific metrics
        df = DataFrameConverter.trades_to_dataframe(filtered_trades)
        
        date_range_metrics = {
            'period_summary': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_days': (end_date - start_date).days + 1,
                'trading_days': df['timestamp'].dt.date.nunique(),
                'total_trades': len(filtered_trades),
                'avg_trades_per_day': len(filtered_trades) / max(1, df['timestamp'].dt.date.nunique())
            },
            'performance_metrics': {
                'net_profit': analysis.net_profit,
                'win_rate': analysis.win_rate,
                'profit_factor': analysis.profit_factor,
                'max_drawdown': analysis.max_drawdown,
                'total_return': analysis.net_profit / max(1, abs(analysis.total_loss)),
                'sharpe_ratio': self._calculate_sharpe_ratio(df),
                'sortino_ratio': self._calculate_sortino_ratio(df),
                'calmar_ratio': self._calculate_calmar_ratio(analysis.net_profit, analysis.max_drawdown)
            },
            'trading_patterns': {
                'best_hour': analysis.best_hour,
                'worst_hour': analysis.worst_hour,
                'best_weekday': self._find_best_weekday(df),
                'best_asset': analysis.best_asset,
                'worst_asset': analysis.worst_asset,
                'most_traded_asset': df['asset'].value_counts().index[0],
                'best_trade_type': self._find_best_trade_type(df)
            },
            'risk_analysis': {
                'max_consecutive_wins': analysis.max_consecutive_wins,
                'max_consecutive_losses': analysis.max_consecutive_losses,
                'average_win': analysis.average_profit,
                'average_loss': analysis.average_loss,
                'largest_win': analysis.best_trade.profit,
                'largest_loss': analysis.worst_trade.profit,
                'risk_reward_ratio': abs(analysis.average_profit / analysis.average_loss) if analysis.average_loss != 0 else 0,
                'var_95': self._calculate_var(df, 0.95),
                'cvar_95': self._calculate_cvar(df, 0.95)
            },
            'equity_analysis': {
                'equity_curve': analysis.equity_curve,
                'max_drawdown': analysis.max_drawdown,
                'drawdown_periods': self._identify_drawdown_periods(analysis.equity_curve),
                'recovery_times': self._calculate_recovery_times(analysis.equity_curve),
                'volatility': self._calculate_equity_volatility(analysis.equity_curve)
            },
            'detailed_stats': {
                'total_profit': analysis.total_profit,
                'total_loss': analysis.total_loss,
                'winning_trades': analysis.winning_trades,
                'losing_trades': analysis.losing_trades,
                'average_profit': analysis.average_profit,
                'average_loss': analysis.average_loss,
                'median_profit': df[df['profit'] > 0]['profit'].median() if len(df[df['profit'] > 0]) > 0 else 0,
                'median_loss': df[df['profit'] < 0]['profit'].median() if len(df[df['profit'] < 0]) > 0 else 0
            }
        }
        
        return date_range_metrics
    
    def _calculate_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic trading statistics"""
        winning_trades = len(df[df['result'] == 'WIN'])
        losing_trades = len(df[df['result'] == 'LOSS'])
        total_trades = len(df)
        
        wins = df[df['result'] == 'WIN']['profit']
        losses = df[df['result'] == 'LOSS']['profit']
        
        total_profit = wins.sum() if len(wins) > 0 else 0
        total_loss = abs(losses.sum()) if len(losses) > 0 else 0
        net_profit = total_profit - total_loss
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        average_profit = wins.mean() if len(wins) > 0 else 0
        average_loss = losses.mean() if len(losses) > 0 else 0
        
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Calculate consecutive wins/losses
        consecutive = self._calculate_consecutive_runs(df)
        
        return {
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'net_profit': net_profit,
            'average_profit': average_profit,
            'average_loss': average_loss,
            'profit_factor': profit_factor,
            'max_consecutive_wins': consecutive['max_wins'],
            'max_consecutive_losses': consecutive['max_losses']
        }
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trading patterns by time"""
        # Hourly analysis
        hourly_stats = df.groupby('hour').agg({
            'profit': ['sum', 'count', 'mean'],
            'result': lambda x: (x == 'WIN').mean()
        }).round(2)
        
        hourly_stats.columns = ['total_profit', 'trade_count', 'avg_profit', 'win_rate']
        
        # Find best and worst hours
        best_hour = hourly_stats['total_profit'].idxmax()
        worst_hour = hourly_stats['total_profit'].idxmin()
        
        # Weekday analysis
        weekday_stats = df.groupby('weekday').agg({
            'profit': ['sum', 'count', 'mean'],
            'result': lambda x: (x == 'WIN').mean()
        }).round(2)
        
        weekday_stats.columns = ['total_profit', 'trade_count', 'avg_profit', 'win_rate']
        
        return {
            'best_hour': int(best_hour),
            'worst_hour': int(worst_hour),
            'trades_by_hour': hourly_stats.to_dict('index'),
            'trades_by_weekday': weekday_stats.to_dict('index')
        }
    
    def _analyze_asset_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by asset"""
        asset_stats = df.groupby('asset').agg({
            'profit': ['sum', 'count', 'mean'],
            'result': lambda x: (x == 'WIN').mean()
        }).round(2)
        
        asset_stats.columns = ['total_profit', 'trade_count', 'avg_profit', 'win_rate']
        
        # Find best and worst assets
        best_asset = asset_stats['total_profit'].idxmax()
        worst_asset = asset_stats['total_profit'].idxmin()
        
        return {
            'best_asset': best_asset,
            'worst_asset': worst_asset,
            'trades_by_asset': asset_stats.to_dict('index')
        }
    
    def _calculate_equity_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate equity curve and drawdown analysis"""
        # Sort by timestamp
        df_sorted = df.sort_values('timestamp')
        
        # Calculate cumulative profit
        equity_curve = df_sorted['profit'].cumsum().tolist()
        
        # Calculate drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak * 100
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        
        return {
            'equity_curve': equity_curve,
            'max_drawdown': max_drawdown
        }
    
    def _find_extreme_trades(self, df: pd.DataFrame) -> Tuple[Trade, Trade]:
        """Find best and worst trades"""
        best_trade_data = df.loc[df['profit'].idxmax()]
        worst_trade_data = df.loc[df['profit'].idxmin()]
        
        best_trade = DataFrameConverter.dataframe_to_trades(
            pd.DataFrame([best_trade_data])
        )[0]
        
        worst_trade = DataFrameConverter.dataframe_to_trades(
            pd.DataFrame([worst_trade_data])
        )[0]
        
        return best_trade, worst_trade
    
    def _calculate_consecutive_runs(self, df: pd.DataFrame) -> Dict[str, int]:
        """Calculate consecutive wins and losses"""
        df_sorted = df.sort_values('timestamp')
        results = df_sorted['result'].tolist()
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for result in results:
            if result == 'WIN':
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            elif result == 'LOSS':
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        return {
            'max_wins': max_wins,
            'max_losses': max_losses
        }
    
    def _calculate_sharpe_ratio(self, df: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        returns = df['profit'].values
        if len(returns) < 2:
            return 0
        
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0
    
    def _calculate_sortino_ratio(self, df: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        returns = df['profit'].values
        if len(returns) < 2:
            return 0
        
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_deviation = np.std(downside_returns)
        return np.mean(excess_returns) / downside_deviation if downside_deviation != 0 else 0
    
    def _calculate_calmar_ratio(self, net_profit: float, max_drawdown: float) -> float:
        """Calculate Calmar ratio"""
        if max_drawdown == 0:
            return float('inf') if net_profit > 0 else 0
        
        return net_profit / abs(max_drawdown)
    
    def _find_best_weekday(self, df: pd.DataFrame) -> int:
        """Find best performing weekday"""
        weekday_performance = df.groupby('weekday')['profit'].sum()
        return int(weekday_performance.idxmax())
    
    def _find_best_trade_type(self, df: pd.DataFrame) -> str:
        """Find best performing trade type"""
        type_performance = df.groupby('trade_type')['profit'].sum()
        return type_performance.idxmax()
    
    def _calculate_var(self, df: pd.DataFrame, confidence_level: float) -> float:
        """Calculate Value at Risk (VaR)"""
        returns = df['profit'].values
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def _calculate_cvar(self, df: pd.DataFrame, confidence_level: float) -> float:
        """Calculate Conditional Value at Risk (CVaR)"""
        returns = df['profit'].values
        var = self._calculate_var(df, confidence_level)
        return returns[returns <= var].mean()
    
    def _identify_drawdown_periods(self, equity_curve: List[float]) -> List[Dict[str, Any]]:
        """Identify drawdown periods"""
        if len(equity_curve) < 2:
            return []
        
        peak = equity_curve[0]
        drawdowns = []
        current_dd_start = None
        
        for i, value in enumerate(equity_curve):
            if value > peak:
                peak = value
                if current_dd_start is not None:
                    drawdowns.append({
                        'start': current_dd_start,
                        'end': i - 1,
                        'depth': (peak - value) / peak * 100,
                        'duration': i - current_dd_start
                    })
                    current_dd_start = None
            elif value < peak:
                if current_dd_start is None:
                    current_dd_start = i
        
        return drawdowns
    
    def _calculate_recovery_times(self, equity_curve: List[float]) -> List[float]:
        """Calculate recovery times from drawdowns"""
        if len(equity_curve) < 2:
            return []
        
        peak = equity_curve[0]
        recovery_times = []
        in_drawdown = False
        drawdown_start = 0
        
        for i, value in enumerate(equity_curve):
            if value > peak:
                peak = value
                if in_drawdown:
                    recovery_times.append(i - drawdown_start)
                    in_drawdown = False
            elif value < peak:
                if not in_drawdown:
                    drawdown_start = i
                    in_drawdown = True
        
        return recovery_times
    
    def _calculate_equity_volatility(self, equity_curve: List[float]) -> float:
        """Calculate equity curve volatility"""
        if len(equity_curve) < 2:
            return 0
        
        returns = np.diff(equity_curve) / equity_curve[:-1]
        return np.std(returns) * np.sqrt(252)  # Annualized volatility
    
    def _create_empty_result(self) -> AnalysisResult:
        """Create empty analysis result"""
        empty_trade = Trade(
            id="",
            timestamp=datetime.now(),
            asset="",
            trade_type=TradeType.CALL,
            amount=0,
            payout=0,
            result=TradeResult.LOSS,
            profit=0
        )
        
        return AnalysisResult(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            total_profit=0,
            total_loss=0,
            net_profit=0,
            average_profit=0,
            average_loss=0,
            profit_factor=0,
            max_drawdown=0,
            max_consecutive_wins=0,
            max_consecutive_losses=0,
            best_trade=empty_trade,
            worst_trade=empty_trade,
            best_hour=0,
            worst_hour=0,
            best_asset="",
            worst_asset="",
            equity_curve=[],
            trades_by_hour={},
            trades_by_asset={},
            trades_by_weekday={},
            date_range=(datetime.now(), datetime.now()),
            analysis_timestamp=datetime.now()
        )
    
    def _create_empty_date_range_result(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Create empty date range analysis result"""
        return {
            'period_summary': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_days': (end_date - start_date).days + 1,
                'trading_days': 0,
                'total_trades': 0,
                'avg_trades_per_day': 0
            },
            'performance_metrics': {
                'net_profit': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'total_return': 0,
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'calmar_ratio': 0
            },
            'trading_patterns': {
                'best_hour': 0,
                'worst_hour': 0,
                'best_weekday': 0,
                'best_asset': "",
                'worst_asset': "",
                'most_traded_asset': "",
                'best_trade_type': ""
            },
            'risk_analysis': {
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0,
                'average_win': 0,
                'average_loss': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'risk_reward_ratio': 0,
                'var_95': 0,
                'cvar_95': 0
            },
            'equity_analysis': {
                'equity_curve': [],
                'max_drawdown': 0,
                'drawdown_periods': [],
                'recovery_times': [],
                'volatility': 0
            },
            'detailed_stats': {
                'total_profit': 0,
                'total_loss': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'average_profit': 0,
                'average_loss': 0,
                'median_profit': 0,
                'median_loss': 0
            }
        }
