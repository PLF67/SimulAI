"""
Business scenario generator.

Creates realistic business simulation scenarios with interconnected events.
"""

from datetime import datetime, timedelta
from typing import List
import random

from ..events.models import Event, EventType, EventSeverity, EventContext


class BusinessScenarioGenerator:
    """
    Generates realistic business scenarios with causal event chains.

    Creates pre-configured scenarios that demonstrate complex business
    dynamics and event correlations.
    """

    def __init__(self, start_time: datetime = None):
        """
        Initialize scenario generator.

        Args:
            start_time: Starting timestamp for scenarios (default: now)
        """
        self.start_time = start_time or datetime.now()

    def generate_competitive_market_scenario(self) -> List[Event]:
        """
        Generate a competitive market scenario.

        Simulates a market disruption caused by competitor actions,
        leading to pricing changes, demand shifts, and operational responses.

        Returns:
            List of events forming a realistic causal chain
        """
        events = []
        t = self.start_time

        # 1. Competitor launches aggressive pricing campaign
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.COMPETITOR_ACTION,
                severity=EventSeverity.HIGH,
                title="Competitor launches 20% price reduction campaign",
                description="Main competitor announced aggressive pricing strategy to gain market share",
                context=EventContext(
                    domain="market",
                    source="market_intelligence",
                    department="strategy",
                    stakeholders=["sales", "marketing", "pricing"],
                    tags={"competition", "pricing", "threat"},
                ),
                magnitude=0.2,
                attributes={
                    "competitor": "CompanyX",
                    "action_type": "price_reduction",
                    "price_change_pct": -20,
                },
            )
        )

        # 2. Market shift detected (4 hours later)
        t += timedelta(hours=4)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.MARKET_SHIFT,
                severity=EventSeverity.MEDIUM,
                title="Market dynamics shift toward price sensitivity",
                description="Customer behavior showing increased price sensitivity",
                context=EventContext(
                    domain="market",
                    source="analytics",
                    department="strategy",
                    stakeholders=["leadership", "sales"],
                    tags={"market_analysis", "customer_behavior"},
                ),
                magnitude=0.15,
                attributes={"shift_type": "price_sensitive"},
            )
        )

        # 3. Our demand decreases (6 hours after competitor action)
        t += timedelta(hours=2)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.DEMAND_CHANGE,
                severity=EventSeverity.HIGH,
                title="15% drop in product demand",
                description="Significant decrease in customer demand for our main product line",
                context=EventContext(
                    domain="sales",
                    source="sales_system",
                    department="sales",
                    stakeholders=["sales", "operations", "leadership"],
                    tags={"demand", "sales", "alert"},
                ),
                magnitude=0.15,
                attributes={"direction": "decrease", "change_pct": -15},
            )
        )

        # 4. Emergency pricing decision (1 day later)
        t += timedelta(days=1)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.PRICE_CHANGE,
                severity=EventSeverity.HIGH,
                title="Price reduction to 15% to match market",
                description="Strategic decision to reduce prices to remain competitive",
                context=EventContext(
                    domain="pricing",
                    source="pricing_system",
                    department="sales",
                    stakeholders=["sales", "finance", "leadership"],
                    tags={"pricing", "strategy", "response"},
                ),
                magnitude=0.15,
                attributes={
                    "direction": "decrease",
                    "price_change_pct": -15,
                    "reason": "competitive_response",
                },
            )
        )

        # 5. Marketing campaign launched (3 hours later)
        t += timedelta(hours=3)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.MARKETING_CAMPAIGN,
                severity=EventSeverity.MEDIUM,
                title="Emergency marketing campaign: 'Best Value Guarantee'",
                description="Launched targeted campaign to highlight value proposition",
                context=EventContext(
                    domain="marketing",
                    source="marketing_system",
                    department="marketing",
                    stakeholders=["marketing", "sales"],
                    tags={"campaign", "competitive_response"},
                ),
                magnitude=0.5,
                attributes={
                    "budget": 50000,
                    "duration_days": 14,
                    "channels": ["digital", "social", "email"],
                },
            )
        )

        # 6. Demand starts recovering (8 hours after price change)
        t += timedelta(hours=8)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.DEMAND_CHANGE,
                severity=EventSeverity.MEDIUM,
                title="Demand recovery: 10% increase",
                description="Customer demand showing positive response to pricing adjustment",
                context=EventContext(
                    domain="sales",
                    source="sales_system",
                    department="sales",
                    stakeholders=["sales", "leadership"],
                    tags={"demand", "recovery"},
                ),
                magnitude=0.1,
                attributes={"direction": "increase", "change_pct": 10},
            )
        )

        # 7. Increased purchases (2 days later)
        t += timedelta(days=2)
        for i in range(5):  # Multiple purchase events
            events.append(
                Event(
                    timestamp=t + timedelta(hours=i * 2),
                    event_type=EventType.PURCHASE,
                    severity=EventSeverity.LOW,
                    title=f"Bulk purchase order #{1001 + i}",
                    description=f"Customer purchase following price adjustment",
                    context=EventContext(
                        domain="sales",
                        source="order_system",
                        department="sales",
                        stakeholders=["sales"],
                        tags={"purchase", "revenue"},
                    ),
                    magnitude=random.uniform(5000, 15000),
                    attributes={"amount": random.uniform(5000, 15000)},
                )
            )

        # 8. Revenue impact (shortly after purchases)
        t += timedelta(hours=12)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.REVENUE_CHANGE,
                severity=EventSeverity.MEDIUM,
                title="Revenue increase: 8% above forecast",
                description="Positive revenue impact from strategic response",
                context=EventContext(
                    domain="finance",
                    source="finance_system",
                    department="finance",
                    stakeholders=["finance", "leadership"],
                    tags={"revenue", "performance"},
                ),
                magnitude=0.08,
                attributes={"direction": "increase", "change_pct": 8},
            )
        )

        return events

    def generate_supply_chain_crisis_scenario(self) -> List[Event]:
        """
        Generate a supply chain crisis scenario.

        Simulates a supply chain disruption and resulting operational challenges.

        Returns:
            List of events forming a supply chain crisis
        """
        events = []
        t = self.start_time

        # 1. Natural disaster
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.NATURAL_DISASTER,
                severity=EventSeverity.CRITICAL,
                title="Hurricane disrupts supplier facilities",
                description="Category 4 hurricane hit main supplier region",
                context=EventContext(
                    domain="external",
                    source="news_feed",
                    location="Southeast Region",
                    stakeholders=["operations", "procurement", "leadership"],
                    tags={"disaster", "supplier", "critical"},
                ),
                magnitude=1.0,
                attributes={"disaster_type": "hurricane", "affected_region": "southeast"},
            )
        )

        # 2. Supply chain disruption (8 hours later)
        t += timedelta(hours=8)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.SUPPLY_CHAIN_DISRUPTION,
                severity=EventSeverity.CRITICAL,
                title="Major supplier offline for 2-3 weeks",
                description="Primary component supplier cannot fulfill orders",
                context=EventContext(
                    domain="supply_chain",
                    source="supplier_management",
                    department="operations",
                    stakeholders=["operations", "production", "leadership"],
                    tags={"disruption", "critical", "supplier"},
                ),
                magnitude=0.8,
                attributes={
                    "supplier_id": "SUP-001",
                    "expected_duration_days": 18,
                    "components_affected": ["comp_a", "comp_b"],
                },
            )
        )

        # 3. Inventory drops (12 hours later)
        t += timedelta(hours=12)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.INVENTORY_CHANGE,
                severity=EventSeverity.HIGH,
                title="Critical inventory shortage: 60% below safety stock",
                description="Inventory levels dropping rapidly due to supply shortage",
                context=EventContext(
                    domain="operations",
                    source="inventory_system",
                    department="operations",
                    stakeholders=["operations", "production"],
                    tags={"inventory", "shortage", "alert"},
                ),
                magnitude=0.6,
                attributes={"direction": "decrease", "below_safety_stock_pct": 60},
            )
        )

        # 4. Production affected (1 day later)
        t += timedelta(days=1)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.PRODUCTION_CHANGE,
                severity=EventSeverity.HIGH,
                title="Production reduced to 40% capacity",
                description="Manufacturing output limited by component shortage",
                context=EventContext(
                    domain="operations",
                    source="production_system",
                    department="production",
                    stakeholders=["production", "operations", "leadership"],
                    tags={"production", "capacity", "crisis"},
                ),
                magnitude=0.6,
                attributes={"direction": "decrease", "capacity_pct": 40},
            )
        )

        # 5. Customer complaints start (2 days later)
        t += timedelta(days=2)
        for i in range(3):
            events.append(
                Event(
                    timestamp=t + timedelta(hours=i * 6),
                    event_type=EventType.CUSTOMER_COMPLAINT,
                    severity=EventSeverity.MEDIUM,
                    title=f"Delivery delay complaint #{2001 + i}",
                    description="Customer complaint about order fulfillment delays",
                    context=EventContext(
                        domain="customer_service",
                        source="crm_system",
                        department="customer_service",
                        stakeholders=["customer_service", "sales"],
                        tags={"complaint", "delivery", "satisfaction"},
                    ),
                    magnitude=0.3,
                    attributes={"complaint_type": "delivery_delay"},
                )
            )

        # 6. Emergency investment in alternative supplier (3 days later)
        t += timedelta(days=3)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.INVESTMENT,
                severity=EventSeverity.HIGH,
                title="Emergency investment: $500K for alternative suppliers",
                description="Fast-track onboarding of backup suppliers",
                context=EventContext(
                    domain="finance",
                    source="finance_system",
                    department="procurement",
                    stakeholders=["procurement", "finance", "leadership"],
                    tags={"investment", "supplier", "emergency"},
                ),
                magnitude=0.5,
                attributes={"amount": 500000, "purpose": "alternative_supplier"},
            )
        )

        # 7. Cost increase (1 day after investment)
        t += timedelta(days=1)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.COST_CHANGE,
                severity=EventSeverity.HIGH,
                title="Operating costs up 25% due to premium suppliers",
                description="Increased costs from emergency supplier arrangements",
                context=EventContext(
                    domain="finance",
                    source="finance_system",
                    department="finance",
                    stakeholders=["finance", "leadership"],
                    tags={"costs", "operations"},
                ),
                magnitude=0.25,
                attributes={"direction": "increase", "change_pct": 25},
            )
        )

        # 8. Gradual recovery (5 days later)
        t += timedelta(days=5)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.PRODUCTION_CHANGE,
                severity=EventSeverity.MEDIUM,
                title="Production capacity restored to 75%",
                description="Alternative suppliers enabling production recovery",
                context=EventContext(
                    domain="operations",
                    source="production_system",
                    department="production",
                    stakeholders=["production", "operations"],
                    tags={"production", "recovery"},
                ),
                magnitude=0.35,
                attributes={"direction": "increase", "capacity_pct": 75},
            )
        )

        return events

    def generate_product_launch_scenario(self) -> List[Event]:
        """
        Generate a successful product launch scenario.

        Simulates a new product launch with marketing, demand generation,
        and operational response.

        Returns:
            List of events for a product launch
        """
        events = []
        t = self.start_time

        # 1. Product launch announcement
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.PRODUCT_LAUNCH,
                severity=EventSeverity.HIGH,
                title="Launch: NextGen Smart Widget v2.0",
                description="Officially launched next generation product with AI features",
                context=EventContext(
                    domain="product",
                    source="product_management",
                    department="product",
                    stakeholders=["product", "marketing", "sales", "leadership"],
                    tags={"launch", "product", "innovation"},
                ),
                magnitude=0.8,
                attributes={
                    "product_id": "PROD-200",
                    "product_name": "NextGen Smart Widget v2.0",
                    "features": ["AI", "cloud_integration", "mobile_app"],
                },
            )
        )

        # 2. Marketing campaign (2 hours later)
        t += timedelta(hours=2)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.MARKETING_CAMPAIGN,
                severity=EventSeverity.HIGH,
                title="Product launch campaign: 'The Future Is Here'",
                description="Multi-channel campaign for new product launch",
                context=EventContext(
                    domain="marketing",
                    source="marketing_system",
                    department="marketing",
                    stakeholders=["marketing", "sales"],
                    tags={"campaign", "launch", "digital"},
                ),
                magnitude=0.9,
                attributes={
                    "budget": 200000,
                    "duration_days": 30,
                    "channels": ["digital", "social", "pr", "events"],
                },
            )
        )

        # 3. Social trend alignment (1 day later)
        t += timedelta(days=1)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.SOCIAL_TREND,
                severity=EventSeverity.MEDIUM,
                title="Viral social media trend: #SmartLiving2025",
                description="Product aligns with trending consumer interest in smart technology",
                context=EventContext(
                    domain="market",
                    source="social_listening",
                    stakeholders=["marketing"],
                    tags={"social", "trend", "viral"},
                ),
                magnitude=0.6,
                attributes={"trend_type": "technology", "reach": "high"},
            )
        )

        # 4. Customer acquisition spike (2 days after launch)
        t += timedelta(days=2)
        for i in range(4):
            events.append(
                Event(
                    timestamp=t + timedelta(hours=i * 4),
                    event_type=EventType.CUSTOMER_ACQUISITION,
                    severity=EventSeverity.MEDIUM,
                    title=f"New customer cohort {i + 1}: 150 signups",
                    description="New customers acquired through launch campaign",
                    context=EventContext(
                        domain="sales",
                        source="crm_system",
                        department="sales",
                        stakeholders=["sales", "marketing"],
                        tags={"acquisition", "growth"},
                    ),
                    magnitude=150,
                    attributes={"count": 150, "source": "launch_campaign"},
                )
            )

        # 5. Demand increase (3 days after launch)
        t += timedelta(days=3)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.DEMAND_CHANGE,
                severity=EventSeverity.HIGH,
                title="Product demand exceeds forecast by 40%",
                description="Overwhelming positive market response to new product",
                context=EventContext(
                    domain="sales",
                    source="analytics",
                    department="sales",
                    stakeholders=["sales", "operations", "product"],
                    tags={"demand", "success", "forecast"},
                ),
                magnitude=0.4,
                attributes={"direction": "increase", "change_pct": 40},
            )
        )

        # 6. Production ramp-up (1 day later)
        t += timedelta(days=1)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.PRODUCTION_CHANGE,
                severity=EventSeverity.MEDIUM,
                title="Production increased to 150% of plan",
                description="Manufacturing scaled up to meet demand",
                context=EventContext(
                    domain="operations",
                    source="production_system",
                    department="production",
                    stakeholders=["production", "operations"],
                    tags={"production", "scale_up"},
                ),
                magnitude=0.5,
                attributes={"direction": "increase", "capacity_pct": 150},
            )
        )

        # 7. Revenue increase (2 days later)
        t += timedelta(days=2)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.REVENUE_CHANGE,
                severity=EventSeverity.HIGH,
                title="Monthly revenue up 35% from new product",
                description="Significant revenue contribution from successful launch",
                context=EventContext(
                    domain="finance",
                    source="finance_system",
                    department="finance",
                    stakeholders=["finance", "leadership"],
                    tags={"revenue", "success", "growth"},
                ),
                magnitude=0.35,
                attributes={"direction": "increase", "change_pct": 35},
            )
        )

        # 8. Partnership opportunity (1 week after launch)
        t += timedelta(weeks=1)
        events.append(
            Event(
                timestamp=t,
                event_type=EventType.PARTNERSHIP,
                severity=EventSeverity.MEDIUM,
                title="Strategic partnership with TechCorp for distribution",
                description="Major retailer partnership secured due to product success",
                context=EventContext(
                    domain="strategy",
                    source="business_development",
                    department="strategy",
                    stakeholders=["strategy", "sales", "leadership"],
                    tags={"partnership", "distribution", "growth"},
                ),
                magnitude=0.7,
                attributes={"partner": "TechCorp", "type": "distribution"},
            )
        )

        return events

    def generate_all_scenarios(self) -> Dict[str, List[Event]]:
        """
        Generate all predefined scenarios.

        Returns:
            Dictionary mapping scenario name to event list
        """
        return {
            "competitive_market": self.generate_competitive_market_scenario(),
            "supply_chain_crisis": self.generate_supply_chain_crisis_scenario(),
            "product_launch": self.generate_product_launch_scenario(),
        }
