"""Event system with causality engine"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.database import GameEvent, EventTemplate, Game, Stock
from backend.services.portfolio_manager import PortfolioManager
from typing import List, Dict, Optional
from datetime import datetime
import random

class CausalityEngine:
    """
    Engine for understanding implicit connections between events and sectors.
    Uses causality tags to determine secondary and tertiary effects.
    """

    # Define causality relationships
    CAUSALITY_MAP = {
        "AI": {
            "strengthens": ["Robotics", "Pharma", "Finance", "Telecom"],
            "competes_with": [],
            "dependent_on": ["Energy", "Quantum"]
        },
        "Quantum": {
            "strengthens": ["AI", "Finance", "Pharma", "Energy"],
            "competes_with": [],
            "dependent_on": ["Energy"]
        },
        "Finance": {
            "strengthens": ["AI", "Quantum"],
            "competes_with": [],
            "dependent_on": ["Telecom", "AI"]
        },
        "Pharma": {
            "strengthens": [],
            "competes_with": [],
            "dependent_on": ["AI", "Quantum"]
        },
        "Energy": {
            "strengthens": ["Robotics", "AI", "Telecom"],
            "competes_with": [],
            "dependent_on": []
        },
        "Telecom": {
            "strengthens": ["AI", "Robotics", "Finance"],
            "competes_with": [],
            "dependent_on": ["Energy"]
        },
        "Robotics": {
            "strengthens": ["Pharma"],
            "competes_with": [],
            "dependent_on": ["AI", "Energy", "Telecom"]
        }
    }

    # Event type implications
    EVENT_TYPE_EFFECTS = {
        "breakthrough": {
            "direct": 1.0,  # Strengthened sectors get this multiplier
            "strengthens": 0.3,  # Sectors that benefit indirectly
            "dependent": 0.2  # Sectors that depend on affected sector
        },
        "crisis": {
            "direct": 1.0,  # Weakened sectors get this multiplier
            "strengthens": -0.2,  # Sectors that were strengthened are now weaker
            "dependent": -0.3  # Dependent sectors suffer more
        },
        "regulation": {
            "direct": 1.0,
            "strengthens": -0.1,
            "dependent": -0.15
        }
    }

    def calculate_secondary_effects(
        self,
        primary_sectors: List[str],
        impact_multipliers: Dict[str, float],
        event_type: str
    ) -> Dict[str, float]:
        """
        Calculate secondary and tertiary effects based on causality.
        Returns a complete map of sector -> final_multiplier
        """
        final_multipliers = impact_multipliers.copy()
        effect_config = self.EVENT_TYPE_EFFECTS.get(event_type, {"direct": 1.0, "strengthens": 0, "dependent": 0})

        for sector in primary_sectors:
            if sector not in self.CAUSALITY_MAP:
                continue

            primary_impact = impact_multipliers.get(sector, 1.0)
            impact_direction = 1 if primary_impact > 1.0 else -1 if primary_impact < 1.0 else 0

            relations = self.CAUSALITY_MAP[sector]

            # Apply effects to sectors that are strengthened by this sector
            for strengthened_sector in relations["strengthens"]:
                if strengthened_sector not in final_multipliers:
                    effect = 1.0 + (impact_direction * effect_config["strengthens"])
                    final_multipliers[strengthened_sector] = effect

            # Apply effects to sectors that depend on this sector
            for dependent_sector in relations["dependent_on"]:
                if dependent_sector not in final_multipliers:
                    effect = 1.0 + (impact_direction * effect_config["dependent"])
                    final_multipliers[dependent_sector] = effect

        return final_multipliers


class EventSystem:
    """Manages game events and their effects"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.causality_engine = CausalityEngine()
        self.portfolio_manager = PortfolioManager(db)

    async def trigger_random_event(self, game_id: int) -> Optional[GameEvent]:
        """Trigger a random event from templates based on probability"""
        result = await self.db.execute(select(EventTemplate))
        templates = result.scalars().all()

        if not templates:
            return None

        # Weight by probability
        total_prob = sum(t.probability for t in templates)
        rand = random.uniform(0, total_prob)

        cumulative = 0
        selected_template = None
        for template in templates:
            cumulative += template.probability
            if rand <= cumulative:
                selected_template = template
                break

        if not selected_template:
            selected_template = templates[-1]

        return await self.trigger_event(game_id, selected_template.id)

    async def trigger_event(self, game_id: int, event_template_id: int) -> Optional[GameEvent]:
        """Trigger a specific event and apply its effects"""
        # Get event template
        result = await self.db.execute(
            select(EventTemplate).where(EventTemplate.id == event_template_id)
        )
        template = result.scalar_one_or_none()
        if not template:
            return None

        # Get game
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if not game:
            return None

        # Calculate secondary effects using causality engine
        all_impact_multipliers = self.causality_engine.calculate_secondary_effects(
            template.affected_sectors,
            template.impact_multipliers,
            template.event_type
        )

        # Create game event
        game_event = GameEvent(
            game_id=game_id,
            title=template.title,
            description=template.description,
            event_type=template.event_type,
            affected_sectors=template.affected_sectors,
            impact_multipliers=all_impact_multipliers,
            quarter_triggered=game.current_quarter
        )
        self.db.add(game_event)
        await self.db.commit()
        await self.db.refresh(game_event)

        # Apply market effects
        await self.apply_event_effects(game_event, game_id, game.current_quarter)

        return game_event

    async def apply_event_effects(self, event: GameEvent, game_id: int, quarter: int):
        """Apply the market effects of an event"""
        impact_multipliers = event.impact_multipliers

        # Apply to each affected sector
        for sector, multiplier in impact_multipliers.items():
            await self.portfolio_manager.apply_sector_change(sector, multiplier, game_id, quarter)

    async def get_recent_events(self, game_id: int, limit: int = 10) -> List[GameEvent]:
        """Get recent events for a game"""
        result = await self.db.execute(
            select(GameEvent)
            .where(GameEvent.game_id == game_id)
            .order_by(GameEvent.triggered_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def seed_event_templates(self):
        """Seed the database with event templates"""
        from backend.database.seed_data import EVENT_TEMPLATES

        for event_data in EVENT_TEMPLATES:
            # Check if already exists
            result = await self.db.execute(
                select(EventTemplate).where(EventTemplate.title == event_data["title"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                continue

            event_template = EventTemplate(**event_data)
            self.db.add(event_template)

        await self.db.commit()
