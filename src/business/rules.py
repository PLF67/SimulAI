"""
Business-specific causal rules.

Defines realistic causal relationships for business simulation scenarios.
"""

from typing import List

from ..correlation.rules import CausalRule
from ..events.models import Event, EventType
from ..events.relationships import CausalityType, RelationshipStrength


def create_business_rules() -> List[CausalRule]:
    """
    Create a comprehensive set of business causal rules.

    Returns:
        List of causal rules modeling realistic business relationships
    """
    rules = []

    # =========================================================================
    # PRICING AND DEMAND RULES
    # =========================================================================

    rules.append(
        CausalRule(
            name="price_reduction_increases_demand",
            description="Price reductions typically increase product demand",
            cause_pattern={"event_type": EventType.PRICE_CHANGE},
            effect_pattern={"event_type": EventType.DEMAND_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.85,
            min_time_lag_minutes=30,
            max_time_lag_minutes=480,  # 8 hours
            condition_func=lambda cause, effect: (
                cause.attributes.get("direction") == "decrease"
                and effect.attributes.get("direction") == "increase"
            ),
            impact_calculator=lambda cause, effect: (
                cause.attributes.get("price_change_pct", 0) * 1.5
            ),
            tags=["pricing", "demand"],
            priority=10,
        )
    )

    rules.append(
        CausalRule(
            name="price_increase_decreases_demand",
            description="Price increases typically decrease demand (elastic goods)",
            cause_pattern={"event_type": EventType.PRICE_CHANGE},
            effect_pattern={"event_type": EventType.DEMAND_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.MODERATE,
            base_confidence=0.7,
            min_time_lag_minutes=30,
            max_time_lag_minutes=480,
            condition_func=lambda cause, effect: (
                cause.attributes.get("direction") == "increase"
                and effect.attributes.get("direction") == "decrease"
            ),
            tags=["pricing", "demand"],
            priority=10,
        )
    )

    # =========================================================================
    # COMPETITION RULES
    # =========================================================================

    rules.append(
        CausalRule(
            name="competitor_price_cut_forces_response",
            description="Competitor price reduction forces our price adjustment",
            cause_pattern={"event_type": EventType.COMPETITOR_ACTION},
            effect_pattern={"event_type": EventType.PRICE_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.8,
            min_time_lag_minutes=60,
            max_time_lag_minutes=2880,  # 2 days
            condition_func=lambda cause, effect: (
                "price" in cause.attributes.get("action_type", "").lower()
            ),
            tags=["competition", "pricing"],
            priority=9,
        )
    )

    rules.append(
        CausalRule(
            name="competitor_action_causes_market_shift",
            description="Major competitor actions shift market dynamics",
            cause_pattern={"event_type": EventType.COMPETITOR_ACTION},
            effect_pattern={"event_type": EventType.MARKET_SHIFT},
            causality_type=CausalityType.CONTRIBUTORY,
            base_strength=RelationshipStrength.MODERATE,
            base_confidence=0.65,
            min_time_lag_minutes=120,
            max_time_lag_minutes=4320,  # 3 days
            tags=["competition", "market"],
            priority=7,
        )
    )

    # =========================================================================
    # CUSTOMER BEHAVIOR RULES
    # =========================================================================

    rules.append(
        CausalRule(
            name="demand_increase_drives_purchases",
            description="Increased demand leads to more purchases",
            cause_pattern={"event_type": EventType.DEMAND_CHANGE},
            effect_pattern={"event_type": EventType.PURCHASE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.VERY_STRONG,
            base_confidence=0.9,
            min_time_lag_minutes=10,
            max_time_lag_minutes=1440,  # 1 day
            condition_func=lambda cause, effect: (
                cause.attributes.get("direction") == "increase"
            ),
            tags=["demand", "sales"],
            priority=10,
        )
    )

    rules.append(
        CausalRule(
            name="customer_complaint_causes_churn",
            description="Unresolved complaints lead to customer churn",
            cause_pattern={"event_type": EventType.CUSTOMER_COMPLAINT},
            effect_pattern={"event_type": EventType.CUSTOMER_CHURN},
            causality_type=CausalityType.PROBABILISTIC,
            base_strength=RelationshipStrength.MODERATE,
            base_confidence=0.6,
            min_time_lag_minutes=1440,  # 1 day
            max_time_lag_minutes=10080,  # 1 week
            condition_func=lambda cause, effect: (
                cause.severity.value in ["high", "critical"]
            ),
            tags=["customer_service", "retention"],
            priority=8,
        )
    )

    rules.append(
        CausalRule(
            name="quality_issue_causes_complaints",
            description="Quality issues trigger customer complaints",
            cause_pattern={"event_type": EventType.QUALITY_ISSUE},
            effect_pattern={"event_type": EventType.CUSTOMER_COMPLAINT},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.85,
            min_time_lag_minutes=30,
            max_time_lag_minutes=2880,  # 2 days
            tags=["quality", "customer_service"],
            priority=9,
        )
    )

    rules.append(
        CausalRule(
            name="marketing_campaign_drives_acquisition",
            description="Marketing campaigns lead to customer acquisition",
            cause_pattern={"event_type": EventType.MARKETING_CAMPAIGN},
            effect_pattern={"event_type": EventType.CUSTOMER_ACQUISITION},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.75,
            min_time_lag_minutes=60,
            max_time_lag_minutes=4320,  # 3 days
            impact_calculator=lambda cause, effect: (
                cause.attributes.get("budget", 0) / 10000  # ROI estimate
            ),
            tags=["marketing", "growth"],
            priority=8,
        )
    )

    # =========================================================================
    # OPERATIONAL RULES
    # =========================================================================

    rules.append(
        CausalRule(
            name="inventory_shortage_from_demand_spike",
            description="Demand spikes cause inventory shortages",
            cause_pattern={"event_type": EventType.DEMAND_CHANGE},
            effect_pattern={"event_type": EventType.INVENTORY_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.8,
            min_time_lag_minutes=30,
            max_time_lag_minutes=720,  # 12 hours
            condition_func=lambda cause, effect: (
                cause.attributes.get("direction") == "increase"
                and effect.attributes.get("direction") == "decrease"
            ),
            tags=["inventory", "operations"],
            priority=9,
        )
    )

    rules.append(
        CausalRule(
            name="supply_disruption_causes_inventory_drop",
            description="Supply chain disruptions reduce inventory levels",
            cause_pattern={"event_type": EventType.SUPPLY_CHAIN_DISRUPTION},
            effect_pattern={"event_type": EventType.INVENTORY_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.VERY_STRONG,
            base_confidence=0.95,
            min_time_lag_minutes=60,
            max_time_lag_minutes=1440,  # 1 day
            condition_func=lambda cause, effect: (
                effect.attributes.get("direction") == "decrease"
            ),
            tags=["supply_chain", "inventory"],
            priority=10,
        )
    )

    rules.append(
        CausalRule(
            name="inventory_shortage_triggers_production_increase",
            description="Low inventory triggers production ramp-up",
            cause_pattern={"event_type": EventType.INVENTORY_CHANGE},
            effect_pattern={"event_type": EventType.PRODUCTION_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.85,
            min_time_lag_minutes=120,
            max_time_lag_minutes=2880,  # 2 days
            condition_func=lambda cause, effect: (
                cause.attributes.get("direction") == "decrease"
                and effect.attributes.get("direction") == "increase"
            ),
            tags=["inventory", "production"],
            priority=8,
        )
    )

    rules.append(
        CausalRule(
            name="production_increase_raises_costs",
            description="Increased production raises operational costs",
            cause_pattern={"event_type": EventType.PRODUCTION_CHANGE},
            effect_pattern={"event_type": EventType.COST_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.9,
            min_time_lag_minutes=30,
            max_time_lag_minutes=480,  # 8 hours
            condition_func=lambda cause, effect: (
                cause.attributes.get("direction") == "increase"
                and effect.attributes.get("direction") == "increase"
            ),
            tags=["production", "costs"],
            priority=8,
        )
    )

    # =========================================================================
    # FINANCIAL RULES
    # =========================================================================

    rules.append(
        CausalRule(
            name="purchases_increase_revenue",
            description="Customer purchases directly increase revenue",
            cause_pattern={"event_type": EventType.PURCHASE},
            effect_pattern={"event_type": EventType.REVENUE_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.VERY_STRONG,
            base_confidence=1.0,
            min_time_lag_minutes=1,
            max_time_lag_minutes=60,
            condition_func=lambda cause, effect: (
                effect.attributes.get("direction") == "increase"
            ),
            impact_calculator=lambda cause, effect: (
                cause.attributes.get("amount", 0)
            ),
            tags=["sales", "revenue"],
            priority=10,
        )
    )

    rules.append(
        CausalRule(
            name="cost_increase_reduces_cash_flow",
            description="Rising costs reduce cash flow",
            cause_pattern={"event_type": EventType.COST_CHANGE},
            effect_pattern={"event_type": EventType.CASH_FLOW_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.VERY_STRONG,
            base_confidence=0.95,
            min_time_lag_minutes=30,
            max_time_lag_minutes=1440,  # 1 day
            condition_func=lambda cause, effect: (
                cause.attributes.get("direction") == "increase"
                and effect.attributes.get("direction") == "decrease"
            ),
            tags=["costs", "finance"],
            priority=9,
        )
    )

    rules.append(
        CausalRule(
            name="investment_enables_expansion",
            description="Strategic investments enable business expansion",
            cause_pattern={"event_type": EventType.INVESTMENT},
            effect_pattern={"event_type": EventType.EXPANSION},
            causality_type=CausalityType.CONDITIONAL,
            base_strength=RelationshipStrength.MODERATE,
            base_confidence=0.7,
            min_time_lag_minutes=1440,  # 1 day
            max_time_lag_minutes=43200,  # 30 days
            condition_func=lambda cause, effect: (
                cause.attributes.get("amount", 0) > 100000
            ),
            tags=["investment", "growth"],
            priority=7,
        )
    )

    # =========================================================================
    # STRATEGIC RULES
    # =========================================================================

    rules.append(
        CausalRule(
            name="product_launch_drives_marketing",
            description="New product launches trigger marketing campaigns",
            cause_pattern={"event_type": EventType.PRODUCT_LAUNCH},
            effect_pattern={"event_type": EventType.MARKETING_CAMPAIGN},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.9,
            min_time_lag_minutes=60,
            max_time_lag_minutes=1440,  # 1 day
            tags=["product", "marketing"],
            priority=8,
        )
    )

    rules.append(
        CausalRule(
            name="product_launch_increases_demand",
            description="Successful product launches increase market demand",
            cause_pattern={"event_type": EventType.PRODUCT_LAUNCH},
            effect_pattern={"event_type": EventType.DEMAND_CHANGE},
            causality_type=CausalityType.PROBABILISTIC,
            base_strength=RelationshipStrength.MODERATE,
            base_confidence=0.65,
            min_time_lag_minutes=1440,  # 1 day
            max_time_lag_minutes=10080,  # 1 week
            condition_func=lambda cause, effect: (
                effect.attributes.get("direction") == "increase"
            ),
            tags=["product", "demand"],
            priority=7,
        )
    )

    rules.append(
        CausalRule(
            name="partnership_drives_market_expansion",
            description="Strategic partnerships enable market expansion",
            cause_pattern={"event_type": EventType.PARTNERSHIP},
            effect_pattern={"event_type": EventType.EXPANSION},
            causality_type=CausalityType.CONTRIBUTORY,
            base_strength=RelationshipStrength.MODERATE,
            base_confidence=0.7,
            min_time_lag_minutes=2880,  # 2 days
            max_time_lag_minutes=43200,  # 30 days
            tags=["partnership", "growth"],
            priority=7,
        )
    )

    # =========================================================================
    # EXTERNAL FACTORS RULES
    # =========================================================================

    rules.append(
        CausalRule(
            name="regulatory_change_requires_restructuring",
            description="Major regulatory changes force business restructuring",
            cause_pattern={"event_type": EventType.REGULATORY_CHANGE},
            effect_pattern={"event_type": EventType.RESTRUCTURING},
            causality_type=CausalityType.CONDITIONAL,
            base_strength=RelationshipStrength.MODERATE,
            base_confidence=0.6,
            min_time_lag_minutes=1440,  # 1 day
            max_time_lag_minutes=43200,  # 30 days
            condition_func=lambda cause, effect: (
                cause.severity.value in ["high", "critical"]
            ),
            tags=["regulatory", "operations"],
            priority=7,
        )
    )

    rules.append(
        CausalRule(
            name="economic_shift_affects_demand",
            description="Economic changes impact consumer demand",
            cause_pattern={"event_type": EventType.ECONOMIC_SHIFT},
            effect_pattern={"event_type": EventType.DEMAND_CHANGE},
            causality_type=CausalityType.CONTRIBUTORY,
            base_strength=RelationshipStrength.MODERATE,
            base_confidence=0.7,
            min_time_lag_minutes=1440,  # 1 day
            max_time_lag_minutes=20160,  # 2 weeks
            tags=["economy", "demand"],
            priority=7,
        )
    )

    rules.append(
        CausalRule(
            name="tech_change_enables_product_launch",
            description="Technological advances enable new product development",
            cause_pattern={"event_type": EventType.TECHNOLOGICAL_CHANGE},
            effect_pattern={"event_type": EventType.PRODUCT_LAUNCH},
            causality_type=CausalityType.CATALYTIC,
            base_strength=RelationshipStrength.MODERATE,
            base_confidence=0.6,
            min_time_lag_minutes=10080,  # 1 week
            max_time_lag_minutes=86400,  # 60 days
            tags=["technology", "product"],
            priority=6,
        )
    )

    rules.append(
        CausalRule(
            name="natural_disaster_disrupts_supply_chain",
            description="Natural disasters cause supply chain disruptions",
            cause_pattern={"event_type": EventType.NATURAL_DISASTER},
            effect_pattern={"event_type": EventType.SUPPLY_CHAIN_DISRUPTION},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.VERY_STRONG,
            base_confidence=0.95,
            min_time_lag_minutes=30,
            max_time_lag_minutes=2880,  # 2 days
            tags=["disaster", "supply_chain"],
            priority=10,
        )
    )

    rules.append(
        CausalRule(
            name="social_trend_influences_demand",
            description="Social trends shift consumer preferences and demand",
            cause_pattern={"event_type": EventType.SOCIAL_TREND},
            effect_pattern={"event_type": EventType.DEMAND_CHANGE},
            causality_type=CausalityType.CONTRIBUTORY,
            base_strength=RelationshipStrength.WEAK,
            base_confidence=0.5,
            min_time_lag_minutes=2880,  # 2 days
            max_time_lag_minutes=43200,  # 30 days
            tags=["social", "demand"],
            priority=5,
        )
    )

    # =========================================================================
    # CASCADING EFFECTS
    # =========================================================================

    rules.append(
        CausalRule(
            name="churn_reduces_revenue",
            description="Customer churn directly reduces revenue",
            cause_pattern={"event_type": EventType.CUSTOMER_CHURN},
            effect_pattern={"event_type": EventType.REVENUE_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.VERY_STRONG,
            base_confidence=0.95,
            min_time_lag_minutes=30,
            max_time_lag_minutes=1440,  # 1 day
            condition_func=lambda cause, effect: (
                effect.attributes.get("direction") == "decrease"
            ),
            tags=["retention", "revenue"],
            priority=9,
        )
    )

    rules.append(
        CausalRule(
            name="capacity_increase_enables_production",
            description="Capacity expansion enables production increases",
            cause_pattern={"event_type": EventType.CAPACITY_CHANGE},
            effect_pattern={"event_type": EventType.PRODUCTION_CHANGE},
            causality_type=CausalityType.CATALYTIC,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.8,
            min_time_lag_minutes=480,  # 8 hours
            max_time_lag_minutes=4320,  # 3 days
            condition_func=lambda cause, effect: (
                cause.attributes.get("direction") == "increase"
                and effect.attributes.get("direction") == "increase"
            ),
            tags=["capacity", "production"],
            priority=7,
        )
    )

    return rules
