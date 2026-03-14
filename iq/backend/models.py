"""
Database Models - SQLAlchemy models for IQ Analyzer
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel

Base = declarative_base()

# SQLAlchemy Models
class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    iq_option_user_id = Column(String(100), nullable=True)
    iq_option_token = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with trades
    trades = relationship("Trade", back_populates="user")

class Trade(Base):
    """Trade model for storing IQ Option trading history"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    iq_trade_id = Column(String(100), unique=True, index=True, nullable=False)
    asset = Column(String(50), nullable=False)
    direction = Column(String(10), nullable=False)  # "call" or "put"
    amount = Column(Float, nullable=False)
    stake = Column(Float, nullable=False)
    payout = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    result = Column(String(20), nullable=False)  # "win", "lose", "draw"
    open_time = Column(DateTime, nullable=False)
    close_time = Column(DateTime, nullable=False)
    expiry_time = Column(DateTime, nullable=False)
    strike_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with user
    user = relationship("User", back_populates="trades")

# Pydantic Models for API
class UserBase(BaseModel):
    """Base user model"""
    email: str
    iq_option_user_id: Optional[str] = None

class UserCreate(UserBase):
    """User creation model"""
    pass

class UserResponse(UserBase):
    """User response model"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str

class LoginResponse(BaseModel):
    """Login response model"""
    success: bool
    user: Optional[UserResponse] = None
    token: Optional[str] = None
    message: str
    trades_loaded: int = 0

class TradeBase(BaseModel):
    """Base trade model"""
    asset: str
    direction: str  # "call" or "put"
    amount: float
    stake: float
    payout: float
    profit: float
    result: str  # "win", "lose", "draw"
    open_time: datetime
    close_time: datetime
    expiry_time: datetime
    strike_price: float
    close_price: float

class TradeCreate(TradeBase):
    """Trade creation model"""
    user_id: int
    iq_trade_id: str

class TradeResponse(TradeBase):
    """Trade response model"""
    id: int
    user_id: int
    iq_trade_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    """Analytics response model"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit: float
    total_stake: float
    total_payout: float
    average_profit: float
    best_asset: str
    best_timeframe: str
    profit_by_asset: dict
    profit_by_direction: dict
