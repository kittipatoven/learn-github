"""
Real IQ Option API Service - Using official iqoptionapi library
"""

from iqoptionapi.stable_api import IQ_Option
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class IQOptionAPI:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.iq_client: Optional[IQ_Option] = None
        self.is_connected = False
        self.email: Optional[str] = None
        self.user_id: Optional[str] = None

    def connect(self, email: str, password: str, account_type: str = "PRACTICE") -> Dict[str, Any]:
        """
        Connect to IQ Option API
        
        Args:
            email: User email
            password: User password
            account_type: Account type ("PRACTICE" or "REAL")
            
        Returns:
            Dict with connection result
        """
        try:
            self.logger.info(f"Connecting to IQ Option with email: {email}")
            self.logger.info(f"Using account type: {account_type}")

            self.iq_client = IQ_Option(email, password)

            check, reason = self.iq_client.connect()

            if check:

                self.is_connected = True
                self.email = email

                # Set account type dynamically
                self.logger.info(f"Setting account type to {account_type}...")
                self.iq_client.change_balance(account_type)
                self.logger.info(f"Account type set to {account_type}")

                # Allow websocket connection to stabilize
                self.logger.info("Waiting for connection to stabilize...")
                time.sleep(2)

                try:

                    profile = self.iq_client.get_profile_ansyc()

                    self.user_id = profile.get("id", "")

                    self.logger.info(
                        f"Successfully connected to IQ Option as {email}")

                    return {
                        "success": True,
                        "message": "Connected successfully",
                        "user_id": self.user_id,
                        "client": self.iq_client,  # ✅ RETURN THE CLIENT
                        "profile": profile
                    }

                except Exception:

                    return {
                        "success": True,
                        "message": "Connected successfully",
                        "user_id": "",
                        "client": self.iq_client,  # ✅ RETURN THE CLIENT
                    }

            else:

                return {
                    "success": False,
                    "message": reason
                }

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    def get_trade_history(self, limit: int = 1000, trade_type: str = "binary-option") -> Dict[str, Any]:

        if not self.is_connected or not self.iq_client:

            return {
                "success": False,
                "message": "Not connected"
            }

        try:

            self.logger.info(f"Retrieving {trade_type} trade history (limit: {limit})")

            end = int(time.time())

            start = end - (60 * 60 * 24 * 30)

            offset = 0

            # Use dynamic trade type parameter
            raw = self.iq_client.get_position_history_v2(
                trade_type,      # instrument_type (dynamic)
                offset,           # offset
                limit,            # limit  
                start,            # start
                end               # end
            )

            # DEBUG: Log the raw response structure
            self.logger.info(f"Raw response type: {type(raw)}")
            self.logger.info(f"Raw response: {raw}")

            if raw is None:

                return {
                    "success": True,
                    "trades": [],
                    "count": 0
                }

            # Handle different response formats
            positions_data = None
            
            if isinstance(raw, tuple):
                # Response is a tuple, extract data part
                if len(raw) == 2:
                    # Format: (success, data) or (data, error)
                    if isinstance(raw[0], bool):
                        # (success, data) format
                        if raw[0]:  # success is True
                            positions_data = raw[1]
                            self.logger.info("API call successful")
                        else:
                            error_msg = raw[1] if raw[1] else "Unknown API error"
                            return {
                                "success": False,
                                "message": f"API Error: {error_msg}"
                            }
                    else:
                        # (data, error) format - use first element
                        positions_data = raw[0]
                        self.logger.info("Using first tuple element as data")
                elif len(raw) == 1:
                    # Single element tuple
                    positions_data = raw[0]
                    self.logger.info("Using single tuple element as data")
                else:
                    return {
                        "success": False,
                        "message": f"Unexpected tuple format: {raw}"
                    }
            elif isinstance(raw, dict):
                # Response is already a dictionary
                positions_data = raw
                self.logger.info("Response is already a dictionary")
            else:
                return {
                    "success": False,
                    "message": f"Unexpected response type: {type(raw)}"
                }

            if not positions_data:
                return {
                    "success": True,
                    "trades": [],
                    "count": 0
                }

            # Extract positions from the data
            positions = positions_data.get("positions", [])
            
            if not positions:
                return {
                    "success": True,
                    "trades": [],
                    "count": 0,
                    "message": "No positions found"
                }

            trades = []

            for trade in positions:

                try:

                    profit = float(trade.get("close_profit", 0))

                    amount = float(trade.get("invest", 0))

                    trades.append({

                        "iq_trade_id": trade.get("id"),

                        "asset": trade.get("active"),

                        "direction": trade.get("direction"),

                        "amount": amount,

                        "profit": profit,

                        "result": "win" if profit > 0 else "lose",

                        "open_time": self._parse_timestamp(
                            trade.get("open_time")
                        ),

                        "close_time": self._parse_timestamp(
                            trade.get("close_time")
                        ),

                        "expiry_time": self._parse_timestamp(
                            trade.get("close_time")
                        )

                    })

                except Exception as e:

                    self.logger.warning(f"Trade parse error {e}")

            return {

                "success": True,
                "trades": trades,
                "count": len(trades)

            }

        except Exception as e:

            self.logger.error(f"Trade history error {e}")

            return {
                "success": False,
                "message": str(e)
            }

    def get_balance(self):

        if not self.is_connected:

            return {
                "success": False,
                "message": "Not connected"
            }

        try:

            balance = self.iq_client.get_balance()

            return {
                "success": True,
                "balance": balance
            }

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    def get_profile(self):

        if not self.is_connected:

            return {
                "success": False,
                "message": "Not connected"
            }

        try:

            profile = self.iq_client.get_profile_ansyc()

            return {
                "success": True,
                "profile": profile
            }

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    def disconnect(self):

        try:

            if self.iq_client:

                self.iq_client.disconnect()

            self.is_connected = False
            self.email = None
            self.user_id = None
            self.iq_client = None

            return {
                "success": True
            }

        except Exception as e:

            return {
                "success": False,
                "message": str(e)
            }

    def _parse_timestamp(self, timestamp):

        if not timestamp:

            return None

        try:

            return datetime.fromtimestamp(int(timestamp))

        except Exception:

            return None

    def is_authenticated(self):

        return self.is_connected and self.iq_client is not None
    
    def change_balance_type(self, balance_type: str = "PRACTICE"):
        """
        Change account balance type
        
        Args:
            balance_type: "PRACTICE" or "REAL"
            
        Returns:
            Dict with success status
        """
        if not self.is_connected or not self.iq_client:
            return {
                "success": False,
                "message": "Not connected"
            }
        
        try:
            balance_type = balance_type.upper()
            if balance_type not in ["PRACTICE", "REAL"]:
                return {
                    "success": False,
                    "message": "Balance type must be 'PRACTICE' or 'REAL'"
                }
            
            self.logger.info(f"Changing balance type to {balance_type}...")
            self.iq_client.change_balance(balance_type)
            self.logger.info(f"Balance type changed to {balance_type}")
            
            return {
                "success": True,
                "message": f"Balance type set to {balance_type}"
            }
            
        except Exception as e:
            self.logger.error(f"Error changing balance type: {e}")
            return {
                "success": False,
                "message": str(e)
            }