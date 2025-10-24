from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

# Game schemas
class GameCreate(BaseModel):
    name: str
    total_quarters: int = 12

class GameResponse(BaseModel):
    id: int
    name: str
    status: str
    current_quarter: int
    total_quarters: int
    created_at: datetime

    class Config:
        from_attributes = True

# Player schemas
class PlayerCreate(BaseModel):
    name: str
    email: EmailStr
    game_id: int

class PlayerResponse(BaseModel):
    id: int
    name: str
    email: str
    current_cash: float
    total_portfolio_value: float
    is_active: bool

    class Config:
        from_attributes = True

class PlayerRanking(BaseModel):
    player_id: int
    player_name: str
    total_value: float
    rank: int
    cash: float
    holdings_value: float

# Stock schemas
class StockCreate(BaseModel):
    ticker: str
    company_name: str
    sector: str
    subsector: Optional[str] = None
    initial_price: float
    description: Optional[str] = None
    volatility: float = 0.15

class StockResponse(BaseModel):
    id: int
    ticker: str
    company_name: str
    sector: str
    subsector: Optional[str]
    current_price: float
    description: Optional[str]

    class Config:
        from_attributes = True

class StockWithChange(StockResponse):
    price_change_percent: float
    price_change_value: float

# Portfolio schemas
class HoldingResponse(BaseModel):
    stock_ticker: str
    company_name: str
    quantity: int
    average_buy_price: float
    current_price: float
    total_value: float
    profit_loss: float
    profit_loss_percent: float

class PortfolioResponse(BaseModel):
    player_id: int
    cash: float
    holdings: List[HoldingResponse]
    total_holdings_value: float
    total_portfolio_value: float

# Transaction schemas
class TransactionCreate(BaseModel):
    player_id: int
    stock_id: int
    transaction_type: str  # buy or sell
    quantity: int

class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    stock_ticker: str
    quantity: int
    price: float
    total_amount: float
    quarter: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Event schemas
class EventTemplateCreate(BaseModel):
    title: str
    description: str
    event_type: str
    affected_sectors: List[str]
    impact_multipliers: Dict[str, float]
    causality_tags: List[str]
    probability: float = 0.5

class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    event_type: str
    affected_sectors: List[str]
    quarter_triggered: int
    triggered_at: datetime

    class Config:
        from_attributes = True

# News schemas
class NewsItemResponse(BaseModel):
    id: int
    title: str
    content: str
    news_type: str
    related_sectors: List[str]
    sentiment: str
    quarter: int
    created_at: datetime

    class Config:
        from_attributes = True

# Game control schemas
class QuarterAdvance(BaseModel):
    game_id: int
    trigger_events: bool = True

class EventTrigger(BaseModel):
    game_id: int
    event_template_id: Optional[int] = None

# Dashboard schemas
class GameState(BaseModel):
    game: GameResponse
    current_quarter: int
    player_rankings: List[PlayerRanking]
    recent_events: List[EventResponse]
    recent_news: List[NewsItemResponse]
    top_gaining_stocks: List[StockWithChange]
    top_losing_stocks: List[StockWithChange]

class SectorPerformance(BaseModel):
    sector: str
    average_change: float
    stock_count: int
