"""Game management service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.database import Game, Player, Stock
from backend.services.portfolio_manager import PortfolioManager
from backend.services.event_system import EventSystem
from backend.services.ai_news_generator import AINewsGenerator
from typing import Optional
from datetime import datetime
import random


class GameManager:
    """Manages overall game flow and state"""

    def __init__(self, db: AsyncSession, ai_api_key: Optional[str] = None, ai_provider: str = "anthropic"):
        self.db = db
        self.portfolio_manager = PortfolioManager(db)
        self.event_system = EventSystem(db)
        self.news_generator = AINewsGenerator(db, ai_api_key, ai_provider)

    async def create_game(self, name: str, total_quarters: int = 12) -> Game:
        """Create a new game"""
        game = Game(
            name=name,
            status="setup",
            total_quarters=total_quarters
        )
        self.db.add(game)
        await self.db.commit()
        await self.db.refresh(game)
        return game

    async def add_player(self, game_id: int, name: str, email: str, initial_cash: float) -> Player:
        """Add a player to a game"""
        player = Player(
            game_id=game_id,
            name=name,
            email=email,
            initial_cash=initial_cash,
            current_cash=initial_cash,
            total_portfolio_value=initial_cash
        )
        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)
        return player

    async def start_game(self, game_id: int) -> bool:
        """Start a game"""
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if not game:
            return False

        game.status = "active"
        game.started_at = datetime.utcnow()
        game.current_quarter = 1
        await self.db.commit()
        return True

    async def advance_quarter(self, game_id: int, trigger_events: bool = True) -> bool:
        """Advance to the next quarter"""
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if not game or game.status != "active":
            return False

        # Apply random market fluctuation
        await self.portfolio_manager.apply_random_market_fluctuation(game_id, game.current_quarter)

        # Trigger random events
        if trigger_events:
            # 60% chance of an event each quarter
            if random.random() < 0.6:
                event = await self.event_system.trigger_random_event(game_id)
                if event:
                    # Generate news from the event
                    await self.news_generator.generate_news_from_event(game_id, event)

            # Generate some sector news (1-3 news items)
            num_news = random.randint(1, 3)
            result = await self.db.execute(select(Stock))
            stocks = result.scalars().all()
            sectors = list(set(stock.sector for stock in stocks))

            for _ in range(num_news):
                sector = random.choice(sectors)
                await self.news_generator.generate_sector_news(game_id, sector, game.current_quarter)

        # Update all portfolio values
        await self.portfolio_manager.update_all_portfolio_values(game_id)

        # Advance quarter
        game.current_quarter += 1

        # Check if game is over
        if game.current_quarter > game.total_quarters:
            game.status = "completed"
            game.ended_at = datetime.utcnow()

        await self.db.commit()
        return True

    async def pause_game(self, game_id: int) -> bool:
        """Pause a game"""
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if not game:
            return False

        game.status = "paused"
        await self.db.commit()
        return True

    async def resume_game(self, game_id: int) -> bool:
        """Resume a paused game"""
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if not game:
            return False

        game.status = "active"
        await self.db.commit()
        return True

    async def end_game(self, game_id: int) -> bool:
        """End a game"""
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if not game:
            return False

        game.status = "completed"
        game.ended_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def seed_stocks(self):
        """Seed the database with initial stocks"""
        from backend.database.seed_data import INITIAL_STOCKS

        for stock_data in INITIAL_STOCKS:
            # Check if already exists
            result = await self.db.execute(
                select(Stock).where(Stock.ticker == stock_data["ticker"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                continue

            stock = Stock(
                ticker=stock_data["ticker"],
                company_name=stock_data["company_name"],
                sector=stock_data["sector"],
                subsector=stock_data.get("subsector"),
                initial_price=stock_data["initial_price"],
                current_price=stock_data["initial_price"],
                description=stock_data.get("description"),
                volatility=stock_data.get("volatility", 0.15)
            )
            self.db.add(stock)

        await self.db.commit()
