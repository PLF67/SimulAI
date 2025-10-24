"""AI-powered news generation system"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.database import NewsItem, Game, Stock, GameEvent
from typing import List, Optional
from datetime import datetime
import random

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AINewsGenerator:
    """Generates realistic news items using AI"""

    def __init__(self, db: AsyncSession, api_key: Optional[str] = None, provider: str = "anthropic"):
        self.db = db
        self.provider = provider
        self.api_key = api_key

        if provider == "anthropic" and ANTHROPIC_AVAILABLE and api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        elif provider == "openai" and OPENAI_AVAILABLE and api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None

    async def generate_news_from_event(self, game_id: int, event: GameEvent) -> NewsItem:
        """Generate a news article based on a game event"""
        if self.client:
            content = await self._generate_ai_news(event)
        else:
            content = self._generate_template_news(event)

        # Determine sentiment
        sentiment = "positive" if any(v > 1.0 for v in event.impact_multipliers.values()) else "negative"

        news_item = NewsItem(
            game_id=game_id,
            title=event.title,
            content=content,
            news_type="event",
            related_sectors=event.affected_sectors,
            sentiment=sentiment,
            quarter=event.quarter_triggered
        )

        self.db.add(news_item)
        await self.db.commit()
        await self.db.refresh(news_item)

        return news_item

    async def generate_sector_news(self, game_id: int, sector: str, quarter: int) -> NewsItem:
        """Generate general news about a sector's progress"""
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()

        news_types = ["innovation", "setback", "societal"]
        news_type = random.choice(news_types)

        if self.client:
            content = await self._generate_ai_sector_news(sector, news_type, quarter)
            title = content.split('\n')[0] if '\n' in content else content[:100]
        else:
            title, content = self._generate_template_sector_news(sector, news_type)

        sentiment = "positive" if news_type == "innovation" else "negative" if news_type == "setback" else "neutral"

        news_item = NewsItem(
            game_id=game_id,
            title=title,
            content=content,
            news_type=news_type,
            related_sectors=[sector],
            sentiment=sentiment,
            quarter=quarter
        )

        self.db.add(news_item)
        await self.db.commit()
        await self.db.refresh(news_item)

        return news_item

    async def _generate_ai_news(self, event: GameEvent) -> str:
        """Generate news using AI"""
        prompt = f"""Write a realistic news article (2-3 paragraphs) about the following event:

Title: {event.title}
Description: {event.description}
Event Type: {event.event_type}
Affected Sectors: {', '.join(event.affected_sectors)}

Write in a professional journalistic style, as if this is appearing in a financial news publication.
Include quotes from fictional industry experts and discuss market implications."""

        try:
            if self.provider == "anthropic":
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_news(event)

    async def _generate_ai_sector_news(self, sector: str, news_type: str, quarter: int) -> str:
        """Generate sector news using AI"""
        if news_type == "innovation":
            prompt_type = "a breakthrough or advancement"
        elif news_type == "setback":
            prompt_type = "a challenge or setback"
        else:
            prompt_type = "a societal or market development"

        prompt = f"""Write a realistic news article (2-3 paragraphs) about {prompt_type} in the {sector} sector.

This is for quarter {quarter} of a business simulation game.
Write in a professional journalistic style.
Include specific details and fictional company names.
Discuss implications for investors and the industry."""

        try:
            if self.provider == "anthropic":
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"AI generation failed: {e}")
            title, content = self._generate_template_sector_news(sector, news_type)
            return f"{title}\n\n{content}"

    def _generate_template_news(self, event: GameEvent) -> str:
        """Generate news using templates (fallback when AI is not available)"""
        templates = {
            "breakthrough": [
                "Industry analysts are calling this a game-changing development. The breakthrough is expected to accelerate innovation across multiple sectors and create new market opportunities. Investors are responding with enthusiasm as companies position themselves to capitalize on this advancement.",
                "This represents a significant milestone in technological progress. Experts predict widespread adoption within the next few years, potentially disrupting traditional business models. Market watchers are closely monitoring how companies adapt to this new landscape."
            ],
            "crisis": [
                "The situation has sent shockwaves through the industry, with companies scrambling to assess the impact. Analysts warn of potential long-term consequences for market stability. Regulatory bodies are being called upon to address the emerging challenges.",
                "This development has raised serious concerns among investors and industry stakeholders. Companies are implementing emergency protocols and reviewing their risk management strategies. The full extent of the impact remains to be seen."
            ],
            "regulation": [
                "The new regulatory framework will require significant adjustments from industry players. While some see this as a necessary step for market maturity, others worry about compliance costs and competitive implications. Companies are already planning their adaptation strategies.",
                "Regulatory experts note that this change reflects growing awareness of industry challenges. The implementation timeline will be crucial for affected companies. Market analysts expect a period of adjustment as businesses align with new requirements."
            ]
        }

        template_list = templates.get(event.event_type, templates["breakthrough"])
        return random.choice(template_list)

    def _generate_template_sector_news(self, sector: str, news_type: str) -> tuple:
        """Generate sector news using templates"""
        templates = {
            "innovation": {
                "AI": ("AI Research Lab Announces Major Efficiency Gains",
                       "Researchers have developed a new algorithm that significantly reduces computational requirements while improving accuracy. The breakthrough could make advanced AI more accessible to smaller companies. Industry experts predict this will accelerate AI adoption across various sectors."),
                "Quantum": ("Quantum Computing Reaches New Stability Milestone",
                           "Scientists have achieved unprecedented quantum coherence times, bringing practical quantum computing closer to reality. The advance addresses one of the field's most significant challenges. Major technology companies are expected to increase their quantum computing investments."),
                "Finance": ("New FinTech Platform Disrupts Payment Processing",
                           "A startup has launched an innovative payment system that reduces transaction costs by 40%. Early adopters report significant efficiency improvements. Traditional financial institutions are monitoring the development closely."),
                "Pharma": ("Novel Drug Delivery System Shows Promise",
                          "Pharmaceutical researchers have developed a targeted delivery mechanism that could revolutionize treatment effectiveness. Clinical trials show encouraging results with reduced side effects. The technology could be applied to various therapeutic areas."),
                "Energy": ("Solar Panel Efficiency Reaches Record High",
                          "New materials science breakthrough enables solar panels to convert more sunlight to electricity than ever before. Manufacturing costs remain competitive with traditional panels. Energy analysts predict accelerated adoption of solar technology."),
            }
        }

        if sector in templates.get(news_type, {}):
            return templates[news_type][sector]
        else:
            return (f"{sector} Sector Update",
                   f"The {sector} sector continues to evolve with new developments. Industry participants are adapting to changing market conditions. Analysts remain cautiously optimistic about future prospects.")

    async def get_recent_news(self, game_id: int, limit: int = 10) -> List[NewsItem]:
        """Get recent news for a game"""
        result = await self.db.execute(
            select(NewsItem)
            .where(NewsItem.game_id == game_id)
            .order_by(NewsItem.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
