"""Main FastAPI application"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.connection import get_db, init_db, close_db
from backend.models import schemas
from backend.models.database import Game, Player, Stock, Holding, GameEvent, NewsItem, EventTemplate
from backend.services.game_manager import GameManager
from backend.services.portfolio_manager import PortfolioManager
from backend.services.event_system import EventSystem
from backend.services.ai_news_generator import AINewsGenerator
from config.settings import settings
from typing import List
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await init_db()
    async for db in get_db():
        game_manager = GameManager(db, settings.anthropic_api_key, settings.ai_provider)
        await game_manager.seed_stocks()
        event_system = EventSystem(db)
        await event_system.seed_event_templates()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="SimulAI Business Game API",
    description="Backend API for the SimulAI business simulation game",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Game Management Endpoints
# ============================================================================

@app.post("/games", response_model=schemas.GameResponse)
async def create_game(game: schemas.GameCreate, db: AsyncSession = Depends(get_db)):
    """Create a new game"""
    game_manager = GameManager(db, settings.anthropic_api_key, settings.ai_provider)
    new_game = await game_manager.create_game(game.name, game.total_quarters)
    return new_game

@app.get("/games", response_model=List[schemas.GameResponse])
async def list_games(db: AsyncSession = Depends(get_db)):
    """List all games"""
    result = await db.execute(select(Game))
    games = result.scalars().all()
    return games

@app.get("/games/{game_id}", response_model=schemas.GameResponse)
async def get_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """Get game details"""
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@app.post("/games/{game_id}/start")
async def start_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """Start a game"""
    game_manager = GameManager(db, settings.anthropic_api_key, settings.ai_provider)
    success = await game_manager.start_game(game_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot start game")
    return {"message": "Game started"}

@app.post("/games/{game_id}/advance-quarter")
async def advance_quarter(game_id: int, trigger_events: bool = True, db: AsyncSession = Depends(get_db)):
    """Advance to next quarter"""
    game_manager = GameManager(db, settings.anthropic_api_key, settings.ai_provider)
    success = await game_manager.advance_quarter(game_id, trigger_events)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot advance quarter")
    return {"message": "Quarter advanced"}

@app.post("/games/{game_id}/pause")
async def pause_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """Pause a game"""
    game_manager = GameManager(db, settings.anthropic_api_key, settings.ai_provider)
    success = await game_manager.pause_game(game_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot pause game")
    return {"message": "Game paused"}

@app.post("/games/{game_id}/resume")
async def resume_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """Resume a game"""
    game_manager = GameManager(db, settings.anthropic_api_key, settings.ai_provider)
    success = await game_manager.resume_game(game_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot resume game")
    return {"message": "Game resumed"}

@app.post("/games/{game_id}/end")
async def end_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """End a game"""
    game_manager = GameManager(db, settings.anthropic_api_key, settings.ai_provider)
    success = await game_manager.end_game(game_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot end game")
    return {"message": "Game ended"}

# ============================================================================
# Player Management Endpoints
# ============================================================================

@app.post("/players", response_model=schemas.PlayerResponse)
async def create_player(player: schemas.PlayerCreate, db: AsyncSession = Depends(get_db)):
    """Create a new player"""
    game_manager = GameManager(db, settings.anthropic_api_key, settings.ai_provider)
    new_player = await game_manager.add_player(
        player.game_id,
        player.name,
        player.email,
        settings.initial_player_money
    )
    return new_player

@app.get("/games/{game_id}/players", response_model=List[schemas.PlayerResponse])
async def list_players(game_id: int, db: AsyncSession = Depends(get_db)):
    """List all players in a game"""
    result = await db.execute(select(Player).where(Player.game_id == game_id))
    players = result.scalars().all()
    return players

@app.get("/players/{player_id}", response_model=schemas.PlayerResponse)
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
    """Get player details"""
    result = await db.execute(select(Player).where(Player.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.get("/games/{game_id}/rankings", response_model=List[schemas.PlayerRanking])
async def get_rankings(game_id: int, db: AsyncSession = Depends(get_db)):
    """Get player rankings"""
    portfolio_manager = PortfolioManager(db)
    rankings = await portfolio_manager.get_player_rankings(game_id)
    return rankings

# ============================================================================
# Stock Endpoints
# ============================================================================

@app.get("/stocks", response_model=List[schemas.StockResponse])
async def list_stocks(db: AsyncSession = Depends(get_db)):
    """List all stocks"""
    result = await db.execute(select(Stock))
    stocks = result.scalars().all()
    return stocks

@app.get("/stocks/{stock_id}", response_model=schemas.StockResponse)
async def get_stock(stock_id: int, db: AsyncSession = Depends(get_db)):
    """Get stock details"""
    result = await db.execute(select(Stock).where(Stock.id == stock_id))
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

# ============================================================================
# Portfolio & Trading Endpoints
# ============================================================================

@app.get("/players/{player_id}/portfolio")
async def get_portfolio(player_id: int, db: AsyncSession = Depends(get_db)):
    """Get player's portfolio"""
    result = await db.execute(select(Player).where(Player.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Get holdings
    holdings_result = await db.execute(
        select(Holding, Stock).join(Stock).where(Holding.player_id == player_id)
    )
    holdings_data = holdings_result.all()

    holdings = []
    total_holdings_value = 0
    for holding, stock in holdings_data:
        total_value = holding.quantity * stock.current_price
        profit_loss = total_value - (holding.quantity * holding.average_buy_price)
        profit_loss_percent = (profit_loss / (holding.quantity * holding.average_buy_price)) * 100 if holding.quantity > 0 else 0

        holdings.append({
            "stock_ticker": stock.ticker,
            "company_name": stock.company_name,
            "quantity": holding.quantity,
            "average_buy_price": holding.average_buy_price,
            "current_price": stock.current_price,
            "total_value": total_value,
            "profit_loss": profit_loss,
            "profit_loss_percent": profit_loss_percent
        })
        total_holdings_value += total_value

    return {
        "player_id": player_id,
        "cash": player.current_cash,
        "holdings": holdings,
        "total_holdings_value": total_holdings_value,
        "total_portfolio_value": player.current_cash + total_holdings_value
    }

@app.post("/trades/buy")
async def buy_stock(trade: schemas.TransactionCreate, db: AsyncSession = Depends(get_db)):
    """Buy stock"""
    # Get player to find game_id
    result = await db.execute(select(Player).where(Player.id == trade.player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    portfolio_manager = PortfolioManager(db)
    success, message = await portfolio_manager.buy_stock(
        trade.player_id,
        trade.stock_id,
        trade.quantity,
        player.game_id
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@app.post("/trades/sell")
async def sell_stock(trade: schemas.TransactionCreate, db: AsyncSession = Depends(get_db)):
    """Sell stock"""
    # Get player to find game_id
    result = await db.execute(select(Player).where(Player.id == trade.player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    portfolio_manager = PortfolioManager(db)
    success, message = await portfolio_manager.sell_stock(
        trade.player_id,
        trade.stock_id,
        trade.quantity,
        player.game_id
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

# ============================================================================
# Event Endpoints
# ============================================================================

@app.get("/games/{game_id}/events", response_model=List[schemas.EventResponse])
async def get_events(game_id: int, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get game events"""
    event_system = EventSystem(db)
    events = await event_system.get_recent_events(game_id, limit)
    return events

@app.get("/event-templates")
async def list_event_templates(db: AsyncSession = Depends(get_db)):
    """List all event templates"""
    result = await db.execute(select(EventTemplate))
    templates = result.scalars().all()
    return templates

@app.post("/games/{game_id}/trigger-event")
async def trigger_event(game_id: int, event_template_id: int, db: AsyncSession = Depends(get_db)):
    """Manually trigger an event"""
    event_system = EventSystem(db)
    event = await event_system.trigger_event(game_id, event_template_id)
    if not event:
        raise HTTPException(status_code=400, detail="Failed to trigger event")

    # Generate news
    news_generator = AINewsGenerator(db, settings.anthropic_api_key, settings.ai_provider)
    await news_generator.generate_news_from_event(game_id, event)

    return {"message": "Event triggered", "event": event}

# ============================================================================
# News Endpoints
# ============================================================================

@app.get("/games/{game_id}/news", response_model=List[schemas.NewsItemResponse])
async def get_news(game_id: int, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get game news"""
    news_generator = AINewsGenerator(db, settings.anthropic_api_key, settings.ai_provider)
    news = await news_generator.get_recent_news(game_id, limit)
    return news

# ============================================================================
# Dashboard Endpoints
# ============================================================================

@app.get("/games/{game_id}/dashboard")
async def get_dashboard(game_id: int, db: AsyncSession = Depends(get_db)):
    """Get complete game dashboard data"""
    # Get game
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Get rankings
    portfolio_manager = PortfolioManager(db)
    rankings = await portfolio_manager.get_player_rankings(game_id)

    # Get recent events
    event_system = EventSystem(db)
    events = await event_system.get_recent_events(game_id, 5)

    # Get recent news
    news_generator = AINewsGenerator(db, settings.anthropic_api_key, settings.ai_provider)
    news = await news_generator.get_recent_news(game_id, 5)

    # Get stock performance
    result = await db.execute(select(Stock))
    stocks = result.scalars().all()

    stock_changes = []
    for stock in stocks:
        change_percent = ((stock.current_price - stock.initial_price) / stock.initial_price) * 100
        stock_changes.append({
            "id": stock.id,
            "ticker": stock.ticker,
            "company_name": stock.company_name,
            "sector": stock.sector,
            "subsector": stock.subsector,
            "current_price": stock.current_price,
            "description": stock.description,
            "price_change_percent": change_percent,
            "price_change_value": stock.current_price - stock.initial_price
        })

    stock_changes.sort(key=lambda x: x["price_change_percent"], reverse=True)

    return {
        "game": game,
        "current_quarter": game.current_quarter,
        "player_rankings": rankings,
        "recent_events": events,
        "recent_news": news,
        "top_gaining_stocks": stock_changes[:5],
        "top_losing_stocks": stock_changes[-5:][::-1]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SimulAI Business Game API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
