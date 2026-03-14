"""
Trade Parser Module - Parse and validate IQ Option trade data
"""

import pandas as pd
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from core.data_models import Trade, TradeResult, TradeType


class TradeParser:
    """Parse and validate IQ Option trade data from various sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_fields = {
            'id', 'timestamp', 'asset', 'trade_type', 
            'amount', 'payout', 'result', 'profit'
        }
    
    def parse_from_file(self, file_path: Union[str, Path]) -> List[Trade]:
        """
        Parse trades from file (JSON, CSV, or Excel)
        
        Args:
            file_path: Path to trade data file
            
        Returns:
            List of Trade objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Trade file not found: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.json':
                return self._parse_json(file_path)
            elif file_path.suffix.lower() == '.csv':
                return self._parse_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                return self._parse_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        except Exception as e:
            self.logger.error(f"Error parsing file {file_path}: {str(e)}")
            raise
    
    def parse_from_dataframe(self, df: pd.DataFrame) -> List[Trade]:
        """
        Parse trades from pandas DataFrame
        
        Args:
            df: DataFrame containing trade data
            
        Returns:
            List of Trade objects
        """
        try:
            # Validate required columns
            missing_cols = self.required_fields - set(df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            trades = []
            for _, row in df.iterrows():
                trade = self._create_trade_from_row(row.to_dict())
                if trade:
                    trades.append(trade)
            
            self.logger.info(f"Successfully parsed {len(trades)} trades from DataFrame")
            return trades
            
        except Exception as e:
            self.logger.error(f"Error parsing DataFrame: {str(e)}")
            raise
    
    def parse_from_dict(self, data: List[Dict[str, Any]]) -> List[Trade]:
        """
        Parse trades from list of dictionaries
        
        Args:
            data: List of trade dictionaries
            
        Returns:
            List of Trade objects
        """
        trades = []
        for trade_data in data:
            try:
                trade = self._create_trade_from_dict(trade_data)
                if trade:
                    trades.append(trade)
            except Exception as e:
                self.logger.warning(f"Skipping invalid trade: {str(e)}")
                continue
        
        self.logger.info(f"Successfully parsed {len(trades)} trades from dictionary data")
        return trades
    
    def _parse_json(self, file_path: Path) -> List[Trade]:
        """Parse trades from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'trades' in data:
            data = data['trades']
        
        if not isinstance(data, list):
            raise ValueError("JSON file must contain a list of trades")
        
        return self.parse_from_dict(data)
    
    def _parse_csv(self, file_path: Path) -> List[Trade]:
        """Parse trades from CSV file"""
        df = pd.read_csv(file_path)
        return self.parse_from_dataframe(df)
    
    def _parse_excel(self, file_path: Path) -> List[Trade]:
        """Parse trades from Excel file"""
        df = pd.read_excel(file_path)
        return self.parse_from_dataframe(df)
    
    def _create_trade_from_row(self, row: Dict[str, Any]) -> Optional[Trade]:
        """Create Trade object from DataFrame row"""
        try:
            # Handle timestamp conversion
            timestamp = self._parse_timestamp(row.get('timestamp'))
            
            # Parse trade type
            trade_type = self._parse_trade_type(row.get('trade_type'))
            
            # Parse result
            result = self._parse_result(row.get('result'))
            
            return Trade(
                id=str(row.get('id', '')),
                timestamp=timestamp,
                asset=str(row.get('asset', '')).upper(),
                trade_type=trade_type,
                amount=float(row.get('amount', 0)),
                payout=float(row.get('payout', 0)),
                result=result,
                profit=float(row.get('profit', 0)),
                duration=row.get('duration'),
                open_price=row.get('open_price'),
                close_price=row.get('close_price'),
                strike_price=row.get('strike_price')
            )
        except Exception as e:
            self.logger.warning(f"Error creating trade from row: {str(e)}")
            return None
    
    def _create_trade_from_dict(self, data: Dict[str, Any]) -> Trade:
        """Create Trade object from dictionary"""
        return Trade(
            id=str(data.get('id', '')),
            timestamp=self._parse_timestamp(data.get('timestamp')),
            asset=str(data.get('asset', '')).upper(),
            trade_type=self._parse_trade_type(data.get('trade_type')),
            amount=float(data.get('amount', 0)),
            payout=float(data.get('payout', 0)),
            result=self._parse_result(data.get('result')),
            profit=float(data.get('profit', 0)),
            duration=data.get('duration'),
            open_price=data.get('open_price'),
            close_price=data.get('close_price'),
            strike_price=data.get('strike_price')
        )
    
    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """Parse timestamp from various formats"""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            # Try different timestamp formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%d/%m/%Y %H:%M:%S',
                '%m/%d/%Y %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
            
            # Try parsing as Unix timestamp
            try:
                return datetime.fromtimestamp(float(timestamp))
            except ValueError:
                pass
            
            raise ValueError(f"Unable to parse timestamp: {timestamp}")
        elif isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp)
        else:
            raise ValueError(f"Unsupported timestamp format: {type(timestamp)}")
    
    def _parse_trade_type(self, trade_type: Any) -> TradeType:
        """Parse trade type from various formats"""
        if isinstance(trade_type, TradeType):
            return trade_type
        elif isinstance(trade_type, str):
            trade_type_upper = trade_type.upper()
            if trade_type_upper in ['CALL', 'BUY', 'UP']:
                return TradeType.CALL
            elif trade_type_upper in ['PUT', 'SELL', 'DOWN']:
                return TradeType.PUT
            else:
                raise ValueError(f"Unknown trade type: {trade_type}")
        else:
            raise ValueError(f"Unsupported trade type format: {type(trade_type)}")
    
    def _parse_result(self, result: Any) -> TradeResult:
        """Parse trade result from various formats"""
        if isinstance(result, TradeResult):
            return result
        elif isinstance(result, str):
            result_upper = result.upper()
            if result_upper in ['WIN', 'WON', 'PROFIT']:
                return TradeResult.WIN
            elif result_upper in ['LOSS', 'LOST', 'LOSE']:
                return TradeResult.LOSS
            elif result_upper in ['DRAW', 'TIE', 'PUSH']:
                return TradeResult.DRAW
            else:
                raise ValueError(f"Unknown result: {result}")
        elif isinstance(result, (int, float)):
            if result > 0:
                return TradeResult.WIN
            elif result < 0:
                return TradeResult.LOSS
            else:
                return TradeResult.DRAW
        else:
            raise ValueError(f"Unsupported result format: {type(result)}")
    
    def validate_trades(self, trades: List[Trade]) -> List[Trade]:
        """
        Validate and clean trade data
        
        Args:
            trades: List of trades to validate
            
        Returns:
            List of valid trades
        """
        valid_trades = []
        errors = []
        
        for i, trade in enumerate(trades):
            try:
                # Basic validation
                if not trade.id:
                    errors.append(f"Trade {i}: Missing ID")
                    continue
                
                if not trade.asset:
                    errors.append(f"Trade {i}: Missing asset")
                    continue
                
                if trade.amount <= 0:
                    errors.append(f"Trade {i}: Invalid amount: {trade.amount}")
                    continue
                
                if trade.payout <= 0:
                    errors.append(f"Trade {i}: Invalid payout: {trade.payout}")
                    continue
                
                # Check for duplicate IDs
                if any(t.id == trade.id for t in valid_trades):
                    errors.append(f"Trade {i}: Duplicate ID: {trade.id}")
                    continue
                
                valid_trades.append(trade)
                
            except Exception as e:
                errors.append(f"Trade {i}: Validation error: {str(e)}")
        
        if errors:
            self.logger.warning(f"Found {len(errors)} validation errors:")
            for error in errors[:10]:  # Log first 10 errors
                self.logger.warning(f"  - {error}")
            if len(errors) > 10:
                self.logger.warning(f"  ... and {len(errors) - 10} more errors")
        
        self.logger.info(f"Validation complete: {len(valid_trades)}/{len(trades)} trades valid")
        return valid_trades
    
    def get_trade_statistics(self, trades: List[Trade]) -> Dict[str, Any]:
        """
        Get basic statistics about trade data
        
        Args:
            trades: List of trades
            
        Returns:
            Dictionary with basic statistics
        """
        if not trades:
            return {}
        
        df = pd.DataFrame([trade.to_dict() for trade in trades])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        stats = {
            'total_trades': len(trades),
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat()
            },
            'unique_assets': df['asset'].nunique(),
            'assets': df['asset'].unique().tolist(),
            'trade_types': df['trade_type'].value_counts().to_dict(),
            'results': df['result'].value_counts().to_dict(),
            'total_amount': df['amount'].sum(),
            'total_profit': df['profit'].sum(),
            'average_profit': df['profit'].mean()
        }
        
        return stats
