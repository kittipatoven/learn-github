"""
IQ Option API Service - Handle authentication and data retrieval from IQ Option
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

class IQOptionAPI:
    """IQ Option API client for authentication and data retrieval"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://iqoption.com/api"  # Update with actual IQ Option API URL
        self.session_token = None
        self.user_id = None
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "IQ-Analyzer-Pro/1.0"
        })
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with IQ Option API
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dictionary with authentication result
        """
        self.logger.info(f"Attempting login for user: {email}")
        
        login_url = urljoin(self.base_url, "login")
        
        login_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                login_url,
                json=login_data,
                timeout=30
            )
            
            self.logger.info(f"Login response status: {response.status_code}")
            self.logger.info(f"Login response text: {response.text[:500]}")  # Log first 500 chars
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.logger.info(f"Parsed JSON result: {result}")
                    
                    if result.get("success"):
                        self.session_token = result.get("token")
                        self.user_id = result.get("userId")
                        
                        # Update session headers with auth token
                        self.session.headers.update({
                            "Authorization": f"Bearer {self.session_token}"
                        })
                        
                        self.logger.info(f"Login successful for user: {email}")
                        return {
                            "success": True,
                            "token": self.session_token,
                            "user_id": self.user_id,
                            "message": "Login successful"
                        }
                    else:
                        error_msg = result.get("message", "Login failed")
                        self.logger.error(f"Login failed: {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "message": result.get("message", "Unknown error")
                        }
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error: {e}")
                    self.logger.error(f"Response text: {response.text}")
                    return {
                        "success": False,
                        "error": "JSON decode error",
                        "message": f"Invalid JSON response: {str(e)}"
                    }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"HTTP error: {error_msg}")
                return {
                    "success": False,
                    "error": "HTTP error",
                    "message": error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.logger.error(f"Request exception: {error_msg}")
            return {
                "success": False,
                "error": "Network error",
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"Unexpected error: {error_msg}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": error_msg
            }
    
    def get_trades(self, start_date: Optional[datetime] = None, 
                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Retrieve trades from IQ Option API
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with trades data
        """
        if not self.session_token:
            return {
                "success": False,
                "error": "Not authenticated",
                "message": "Please login first"
            }
        
        trades_url = urljoin(self.base_url, "trades")
        
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        try:
            response = self.session.get(
                trades_url,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                trades_data = response.json()
                self.logger.info(f"Retrieved {len(trades_data)} trades")
                return {
                    "success": True,
                    "trades": trades_data,
                    "count": len(trades_data)
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"Trades retrieval error: {error_msg}")
                return {
                    "success": False,
                    "error": "HTTP error",
                    "message": error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.logger.error(f"Trades retrieval error: {error_msg}")
            return {
                "success": False,
                "error": "Network error",
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"Trades retrieval error: {error_msg}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": error_msg
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information from IQ Option API
        
        Returns:
            Dictionary with account data
        """
        if not self.session_token:
            return {
                "success": False,
                "error": "Not authenticated",
                "message": "Please login first"
            }
        
        account_url = urljoin(self.base_url, "account")
        
        try:
            response = self.session.get(account_url, timeout=30)
            
            if response.status_code == 200:
                account_data = response.json()
                self.logger.info("Retrieved account information")
                return {
                    "success": True,
                    "account": account_data
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"Account info error: {error_msg}")
                return {
                    "success": False,
                    "error": "HTTP error",
                    "message": error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.logger.error(f"Account info error: {error_msg}")
            return {
                "success": False,
                "error": "Network error",
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"Account info error: {error_msg}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": error_msg
            }
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout from IQ Option API
        """
        try:
            # Clear session token
            self.session_token = None
            self.user_id = None
            
            # Remove authorization header
            if "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]
            
            self.logger.info("Logged out successfully")
            return {
                "success": True,
                "message": "Logged out successfully"
            }
            
        except Exception as e:
            error_msg = f"Logout error: {str(e)}"
            self.logger.error(f"Logout error: {error_msg}")
            return {
                "success": False,
                "error": "Logout error",
                "message": error_msg
            }
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.session_token is not None
    
    def get_headers(self) -> Dict[str, str]:
        """Get current request headers"""
        return self.session.headers.copy()
