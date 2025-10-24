"""Portfolio management and valuation service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.database import Player, Stock, Holding, Transaction, Game, StockPrice
from typing import Dict, List, Tuple
from datetime import datetime
import random

class PortfolioManager:
    """Manages player portfolios and stock valuations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def buy_stock(self, player_id: int, stock_id: int, quantity: int, game_id: int) -> Tuple[bool, str]:
        """
        Execute a buy transaction
        Returns: (success: bool, message: str)
        """
        # Get player
        result = await self.db.execute(select(Player).where(Player.id == player_id))
        player = result.scalar_one_or_none()
        if not player:
            return False, "Player not found"

        # Get stock
        result = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        stock = result.scalar_one_or_none()
        if not stock:
            return False, "Stock not found"

        # Get game
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if not game:
            return False, "Game not found"

        # Calculate total cost
        total_cost = stock.current_price * quantity

        # Check if player has enough cash
        if player.current_cash < total_cost:
            return False, f"Insufficient funds. Need ${total_cost:.2f}, have ${player.current_cash:.2f}"

        # Update player cash
        player.current_cash -= total_cost

        # Get or create holding
        result = await self.db.execute(
            select(Holding).where(
                Holding.player_id == player_id,
                Holding.stock_id == stock_id
            )
        )
        holding = result.scalar_one_or_none()

        if holding:
            # Update existing holding
            total_shares = holding.quantity + quantity
            total_value = (holding.average_buy_price * holding.quantity) + total_cost
            holding.average_buy_price = total_value / total_shares
            holding.quantity = total_shares
            holding.last_updated = datetime.utcnow()
        else:
            # Create new holding
            holding = Holding(
                player_id=player_id,
                stock_id=stock_id,
                quantity=quantity,
                average_buy_price=stock.current_price
            )
            self.db.add(holding)

        # Create transaction record
        transaction = Transaction(
            player_id=player_id,
            stock_id=stock_id,
            game_id=game_id,
            transaction_type="buy",
            quantity=quantity,
            price=stock.current_price,
            total_amount=total_cost,
            quarter=game.current_quarter
        )
        self.db.add(transaction)

        await self.db.commit()
        return True, f"Successfully bought {quantity} shares of {stock.ticker} for ${total_cost:.2f}"

    async def sell_stock(self, player_id: int, stock_id: int, quantity: int, game_id: int) -> Tuple[bool, str]:
        """
        Execute a sell transaction
        Returns: (success: bool, message: str)
        """
        # Get holding
        result = await self.db.execute(
            select(Holding).where(
                Holding.player_id == player_id,
                Holding.stock_id == stock_id
            )
        )
        holding = result.scalar_one_or_none()
        if not holding:
            return False, "You don't own this stock"

        if holding.quantity < quantity:
            return False, f"Insufficient shares. You have {holding.quantity}, trying to sell {quantity}"

        # Get stock
        result = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        stock = result.scalar_one_or_none()

        # Get game
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()

        # Get player
        result = await self.db.execute(select(Player).where(Player.id == player_id))
        player = result.scalar_one_or_none()

        # Calculate total proceeds
        total_proceeds = stock.current_price * quantity

        # Update player cash
        player.current_cash += total_proceeds

        # Update holding
        holding.quantity -= quantity
        if holding.quantity == 0:
            await self.db.delete(holding)
        else:
            holding.last_updated = datetime.utcnow()

        # Create transaction record
        transaction = Transaction(
            player_id=player_id,
            stock_id=stock_id,
            game_id=game_id,
            transaction_type="sell",
            quantity=quantity,
            price=stock.current_price,
            total_amount=total_proceeds,
            quarter=game.current_quarter
        )
        self.db.add(transaction)

        await self.db.commit()
        return True, f"Successfully sold {quantity} shares of {stock.ticker} for ${total_proceeds:.2f}"

    async def get_portfolio_value(self, player_id: int) -> float:
        """Calculate total portfolio value for a player"""
        # Get player
        result = await self.db.execute(select(Player).where(Player.id == player_id))
        player = result.scalar_one_or_none()
        if not player:
            return 0.0

        # Get all holdings
        result = await self.db.execute(
            select(Holding, Stock).join(Stock).where(Holding.player_id == player_id)
        )
        holdings = result.all()

        # Calculate total value
        holdings_value = sum(holding.quantity * stock.current_price for holding, stock in holdings)
        total_value = player.current_cash + holdings_value

        # Update player's portfolio value
        player.total_portfolio_value = total_value
        await self.db.commit()

        return total_value

    async def update_all_portfolio_values(self, game_id: int):
        """Update portfolio values for all players in a game"""
        result = await self.db.execute(select(Player).where(Player.game_id == game_id))
        players = result.scalars().all()

        for player in players:
            await self.get_portfolio_value(player.id)

    async def apply_market_change(self, stock_id: int, multiplier: float, game_id: int, quarter: int):
        """Apply a price change to a stock"""
        result = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        stock = result.scalar_one_or_none()
        if not stock:
            return

        old_price = stock.current_price
        new_price = old_price * multiplier
        stock.current_price = new_price

        # Record price history
        price_record = StockPrice(
            stock_id=stock_id,
            game_id=game_id,
            quarter=quarter,
            price=new_price,
            change_percent=((new_price - old_price) / old_price) * 100
        )
        self.db.add(price_record)
        await self.db.commit()

    async def apply_sector_change(self, sector: str, multiplier: float, game_id: int, quarter: int):
        """Apply a price change to all stocks in a sector"""
        result = await self.db.execute(select(Stock).where(Stock.sector == sector))
        stocks = result.scalars().all()

        for stock in stocks:
            # Add some randomness to make it less uniform
            stock_multiplier = multiplier * random.uniform(0.95, 1.05)
            await self.apply_market_change(stock.id, stock_multiplier, game_id, quarter)

    async def apply_random_market_fluctuation(self, game_id: int, quarter: int):
        """Apply random market fluctuations to all stocks"""
        result = await self.db.execute(select(Stock))
        stocks = result.scalars().all()

        for stock in stocks:
            # Random fluctuation based on stock's volatility
            change = random.gauss(0, stock.volatility / 4)  # Quarterly volatility
            multiplier = 1 + change
            await self.apply_market_change(stock.id, multiplier, game_id, quarter)

    async def get_player_rankings(self, game_id: int) -> List[Dict]:
        """Get player rankings by portfolio value"""
        result = await self.db.execute(
            select(Player).where(Player.game_id == game_id).order_by(Player.total_portfolio_value.desc())
        )
        players = result.scalars().all()

        rankings = []
        for rank, player in enumerate(players, 1):
            # Calculate holdings value
            holdings_result = await self.db.execute(
                select(Holding, Stock).join(Stock).where(Holding.player_id == player.id)
            )
            holdings = holdings_result.all()
            holdings_value = sum(holding.quantity * stock.current_price for holding, stock in holdings)

            rankings.append({
                "rank": rank,
                "player_id": player.id,
                "player_name": player.name,
                "total_value": player.total_portfolio_value,
                "cash": player.current_cash,
                "holdings_value": holdings_value
            })

        return rankings
