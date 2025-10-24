from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Game(Base):
    """Game session model"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, index=True)
    status = Column(String(50), default="setup")  # setup, active, paused, completed
    current_quarter = Column(Integer, default=0)
    total_quarters = Column(Integer, default=12)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    players = relationship("Player", back_populates="game")
    events = relationship("GameEvent", back_populates="game")
    news_items = relationship("NewsItem", back_populates="game")

class Player(Base):
    """Player model"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    name = Column(String(100))
    email = Column(String(200), unique=True, index=True)
    initial_cash = Column(Float, default=100000.0)
    current_cash = Column(Float, default=100000.0)
    total_portfolio_value = Column(Float, default=100000.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    game = relationship("Game", back_populates="players")
    holdings = relationship("Holding", back_populates="player")
    transactions = relationship("Transaction", back_populates="player")

class Stock(Base):
    """Stock model"""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, index=True)
    company_name = Column(String(200))
    sector = Column(String(100))  # AI, Quantum, Finance, Pharma, etc.
    subsector = Column(String(100), nullable=True)
    initial_price = Column(Float)
    current_price = Column(Float)
    description = Column(Text, nullable=True)
    volatility = Column(Float, default=0.15)  # Base volatility
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    holdings = relationship("Holding", back_populates="stock")
    transactions = relationship("Transaction", back_populates="stock")
    price_history = relationship("StockPrice", back_populates="stock")

class Holding(Base):
    """Player stock holdings"""
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    quantity = Column(Integer, default=0)
    average_buy_price = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="holdings")
    stock = relationship("Stock", back_populates="holdings")

class Transaction(Base):
    """Transaction history"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    transaction_type = Column(String(10))  # buy, sell
    quantity = Column(Integer)
    price = Column(Float)
    total_amount = Column(Float)
    quarter = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="transactions")
    stock = relationship("Stock", back_populates="transactions")

class GameEvent(Base):
    """Game events that affect stock prices"""
    __tablename__ = "game_events"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    title = Column(String(200))
    description = Column(Text)
    event_type = Column(String(100))  # regulation, breakthrough, disaster, etc.
    affected_sectors = Column(JSON)  # List of affected sectors
    impact_multipliers = Column(JSON)  # Sector -> impact multiplier mapping
    quarter_triggered = Column(Integer)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    is_visible = Column(Boolean, default=True)  # Some events may be hidden

    # Relationships
    game = relationship("Game", back_populates="events")

class EventTemplate(Base):
    """Template for events that can be triggered"""
    __tablename__ = "event_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    event_type = Column(String(100))
    affected_sectors = Column(JSON)
    impact_multipliers = Column(JSON)
    causality_tags = Column(JSON)  # Tags for causality connections
    probability = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)

class NewsItem(Base):
    """AI-generated news items"""
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    title = Column(String(300))
    content = Column(Text)
    news_type = Column(String(100))  # innovation, setback, societal, market
    related_sectors = Column(JSON)
    sentiment = Column(String(50))  # positive, negative, neutral
    quarter = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    game = relationship("Game", back_populates="news_items")

class StockPrice(Base):
    """Historical stock prices"""
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    quarter = Column(Integer)
    price = Column(Float)
    change_percent = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    stock = relationship("Stock", back_populates="price_history")
