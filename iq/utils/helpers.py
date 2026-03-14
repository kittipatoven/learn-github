"""
Helper Functions - Utility functions for the application
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Any, Union, Optional
import re


def format_currency(amount: float, currency: str = "$", decimal_places: int = 2) -> str:
    """
    Format amount as currency
    
    Args:
        amount: Amount to format
        currency: Currency symbol
        decimal_places: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    if pd.isna(amount) or amount is None:
        return f"{currency}0.00"
    
    return f"{currency}{abs(amount):.{decimal_places}f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format value as percentage
    
    Args:
        value: Value to format (as decimal, e.g., 0.25 for 25%)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if pd.isna(value) or value is None:
        return "0.00%"
    
    return f"{value * 100:.{decimal_places}f}%"


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        if pd.isna(value) or value is None or value == "":
            return default
        
        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = re.sub(r'[$,\s]', '', value)
            return float(cleaned)
        
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Int value or default
    """
    try:
        if pd.isna(value) or value is None or value == "":
            return default
        
        return int(float(value))
    except (ValueError, TypeError):
        return default


def parse_datetime(value: Any, formats: Optional[list] = None) -> Optional[datetime]:
    """
    Parse datetime from various formats
    
    Args:
        value: Value to parse
        formats: List of datetime formats to try
        
    Returns:
        Datetime object or None
    """
    if pd.isna(value) or value is None:
        return None
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        default_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%d/%m/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y'
        ]
        
        formats_to_try = formats or default_formats
        
        for fmt in formats_to_try:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        # Try parsing as Unix timestamp
        try:
            return datetime.fromtimestamp(float(value))
        except ValueError:
            pass
    
    return None


def calculate_drawdown(equity_curve: list) -> tuple:
    """
    Calculate drawdown from equity curve
    
    Args:
        equity_curve: List of equity values
        
    Returns:
        Tuple of (max_drawdown, drawdown_periods)
    """
    if not equity_curve:
        return 0.0, []
    
    equity_array = np.array(equity_curve)
    peak = np.maximum.accumulate(equity_array)
    drawdown = (peak - equity_array) / peak * 100
    max_drawdown = np.max(drawdown)
    
    # Find drawdown periods
    drawdown_periods = []
    in_drawdown = False
    start_idx = 0
    
    for i, dd in enumerate(drawdown):
        if dd > 0 and not in_drawdown:
            start_idx = i
            in_drawdown = True
        elif dd == 0 and in_drawdown:
            drawdown_periods.append((start_idx, i))
            in_drawdown = False
    
    return max_drawdown, drawdown_periods


def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: List of returns
        risk_free_rate: Risk-free rate (annual)
        
    Returns:
        Sharpe ratio
    """
    if len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate / 252  # Daily risk-free rate
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    return np.mean(excess_returns) / np.std(excess_returns)


def calculate_sortino_ratio(returns: list, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sortino ratio
    
    Args:
        returns: List of returns
        risk_free_rate: Risk-free rate (annual)
        
    Returns:
        Sortino ratio
    """
    if len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate / 252
    
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0:
        return float('inf')
    
    downside_deviation = np.std(downside_returns)
    
    if downside_deviation == 0:
        return 0.0
    
    return np.mean(excess_returns) / downside_deviation


def calculate_calmar_ratio(net_profit: float, max_drawdown: float) -> float:
    """
    Calculate Calmar ratio
    
    Args:
        net_profit: Net profit
        max_drawdown: Maximum drawdown (as percentage)
        
    Returns:
        Calmar ratio
    """
    if max_drawdown == 0:
        return float('inf') if net_profit > 0 else 0.0
    
    return net_profit / abs(max_drawdown)


def normalize_score(score: float, min_val: float = 0, max_val: float = 100) -> float:
    """
    Normalize score to specified range
    
    Args:
        score: Score to normalize
        min_val: Minimum value in range
        max_val: Maximum value in range
        
    Returns:
        Normalized score
    """
    return max(min_val, min(max_val, score))


def calculate_win_rate(trades: list) -> float:
    """
    Calculate win rate from trades
    
    Args:
        trades: List of trades with result field
        
    Returns:
        Win rate (0-1)
    """
    if not trades:
        return 0.0
    
    winning_trades = sum(1 for trade in trades if getattr(trade, 'result', 'LOSS') == 'WIN')
    return winning_trades / len(trades)


def calculate_profit_factor(trades: list) -> float:
    """
    Calculate profit factor from trades
    
    Args:
        trades: List of trades with profit field
        
    Returns:
        Profit factor
    """
    if not trades:
        return 0.0
    
    profits = [getattr(trade, 'profit', 0) for trade in trades]
    gross_profit = sum(p for p in profits if p > 0)
    gross_loss = abs(sum(p for p in profits if p < 0))
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss


def get_time_period_description(start_date: datetime, end_date: datetime) -> str:
    """
    Get human-readable description of time period
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Description string
    """
    if not start_date or not end_date:
        return "Unknown period"
    
    days = (end_date - start_date).days
    
    if days < 1:
        return "Same day"
    elif days == 1:
        return "1 day"
    elif days < 7:
        return f"{days} days"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''}"
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''}"
    else:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''}"


def validate_trade_data(trade_data: dict) -> tuple:
    """
    Validate trade data dictionary
    
    Args:
        trade_data: Trade data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['id', 'timestamp', 'asset', 'trade_type', 'amount', 'result', 'profit']
    
    for field in required_fields:
        if field not in trade_data or trade_data[field] is None:
            return False, f"Missing required field: {field}"
    
    # Validate data types
    try:
        # Check numeric fields
        numeric_fields = ['amount', 'profit']
        for field in numeric_fields:
            float(trade_data[field])
        
        # Check timestamp
        parse_datetime(trade_data['timestamp'])
        
    except (ValueError, TypeError) as e:
        return False, f"Invalid data type: {str(e)}"
    
    return True, ""


def clean_asset_name(asset: str) -> str:
    """
    Clean and standardize asset name
    
    Args:
        asset: Asset name to clean
        
    Returns:
        Cleaned asset name
    """
    if not asset:
        return ""
    
    # Remove extra spaces and convert to uppercase
    cleaned = asset.strip().upper()
    
    # Replace common separators with /
    cleaned = re.sub(r'[._-]', '/', cleaned)
    
    return cleaned


def generate_trade_id() -> str:
    """
    Generate unique trade ID
    
    Returns:
        Unique trade ID
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    import random
    random_suffix = f"{random.randint(1000, 9999)}"
    return f"TRADE_{timestamp}_{random_suffix}"


def calculate_position_size(account_balance: float, risk_percent: float, stop_loss_pips: float) -> float:
    """
    Calculate position size based on risk management
    
    Args:
        account_balance: Account balance
        risk_percent: Risk percentage (e.g., 1.0 for 1%)
        stop_loss_pips: Stop loss in pips
        
    Returns:
        Position size
    """
    risk_amount = account_balance * (risk_percent / 100)
    position_size = risk_amount / stop_loss_pips if stop_loss_pips > 0 else 0
    return position_size


def format_time_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
