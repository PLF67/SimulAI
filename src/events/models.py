"""
Core event models for the correlation engine.

Provides rich event representation with metadata, temporal information,
and context for sophisticated causal analysis.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Categories of events in the business simulation."""

    # Market Events
    MARKET_SHIFT = "market_shift"
    DEMAND_CHANGE = "demand_change"
    SUPPLY_CHANGE = "supply_change"
    PRICE_CHANGE = "price_change"
    COMPETITOR_ACTION = "competitor_action"

    # Customer Events
    CUSTOMER_ACQUISITION = "customer_acquisition"
    CUSTOMER_CHURN = "customer_churn"
    CUSTOMER_COMPLAINT = "customer_complaint"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    PURCHASE = "purchase"

    # Operational Events
    PRODUCTION_CHANGE = "production_change"
    INVENTORY_CHANGE = "inventory_change"
    QUALITY_ISSUE = "quality_issue"
    SUPPLY_CHAIN_DISRUPTION = "supply_chain_disruption"
    CAPACITY_CHANGE = "capacity_change"

    # Financial Events
    REVENUE_CHANGE = "revenue_change"
    COST_CHANGE = "cost_change"
    INVESTMENT = "investment"
    CASH_FLOW_CHANGE = "cash_flow_change"

    # Strategic Events
    PRODUCT_LAUNCH = "product_launch"
    MARKETING_CAMPAIGN = "marketing_campaign"
    PARTNERSHIP = "partnership"
    EXPANSION = "expansion"
    RESTRUCTURING = "restructuring"

    # External Events
    REGULATORY_CHANGE = "regulatory_change"
    ECONOMIC_SHIFT = "economic_shift"
    TECHNOLOGICAL_CHANGE = "technological_change"
    NATURAL_DISASTER = "natural_disaster"
    SOCIAL_TREND = "social_trend"


class EventSeverity(str, Enum):
    """Severity/impact level of an event."""

    CRITICAL = "critical"      # Major impact, requires immediate attention
    HIGH = "high"              # Significant impact
    MEDIUM = "medium"          # Moderate impact
    LOW = "low"                # Minor impact
    NEGLIGIBLE = "negligible"  # Minimal impact


class EventContext(BaseModel):
    """
    Contextual information about an event.

    Provides additional metadata that helps in correlation and causality analysis.
    """

    domain: str = Field(..., description="Business domain (e.g., 'sales', 'operations')")
    source: str = Field(..., description="Source system or actor generating the event")
    location: Optional[str] = Field(None, description="Geographic location if relevant")
    department: Optional[str] = Field(None, description="Department involved")
    stakeholders: List[str] = Field(default_factory=list, description="Affected stakeholders")
    tags: Set[str] = Field(default_factory=set, description="Searchable tags")

    class Config:
        frozen = False


class Event(BaseModel):
    """
    Core event model with rich metadata for correlation analysis.

    Events represent discrete occurrences in the business simulation that can
    have causal relationships with other events.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the event occurred")
    event_type: EventType = Field(..., description="Type/category of the event")
    severity: EventSeverity = Field(default=EventSeverity.MEDIUM, description="Impact level")

    title: str = Field(..., description="Short descriptive title")
    description: str = Field(..., description="Detailed description of the event")

    context: EventContext = Field(..., description="Contextual metadata")

    # Quantitative attributes
    magnitude: float = Field(default=1.0, ge=0.0, description="Quantitative impact magnitude")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in event occurrence")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Event duration if applicable")

    # Causal tracking
    triggered_by: List[str] = Field(default_factory=list, description="IDs of events that caused this")
    triggers: List[str] = Field(default_factory=list, description="IDs of events this caused")

    # Custom attributes
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific attributes")

    # Temporal relationships
    expected_effects_window_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Expected time window for causal effects"
    )

    class Config:
        frozen = False
        json_schema_extra = {
            "example": {
                "event_type": "price_change",
                "severity": "high",
                "title": "Product price reduction",
                "description": "Reduced price by 15% to match competitor",
                "context": {
                    "domain": "pricing",
                    "source": "pricing_system",
                    "department": "sales",
                    "stakeholders": ["sales_team", "customers"],
                    "tags": ["pricing", "competition"]
                },
                "magnitude": 0.15,
                "confidence": 1.0,
                "attributes": {
                    "old_price": 100.0,
                    "new_price": 85.0,
                    "product_id": "PROD-001"
                }
            }
        }

    def add_cause(self, event_id: str) -> None:
        """Add an event that caused this one."""
        if event_id not in self.triggered_by:
            self.triggered_by.append(event_id)

    def add_effect(self, event_id: str) -> None:
        """Add an event that this one caused."""
        if event_id not in self.triggers:
            self.triggers.append(event_id)

    def matches_pattern(self, pattern: Dict[str, Any]) -> bool:
        """
        Check if event matches a pattern specification.

        Args:
            pattern: Dictionary with field:value pairs to match

        Returns:
            True if all pattern fields match
        """
        for field, value in pattern.items():
            if field == "event_type":
                if self.event_type != value:
                    return False
            elif field == "severity":
                if self.severity != value:
                    return False
            elif field == "domain":
                if self.context.domain != value:
                    return False
            elif field == "tags":
                if isinstance(value, (list, set)):
                    if not any(tag in self.context.tags for tag in value):
                        return False
            elif field in self.attributes:
                if self.attributes[field] != value:
                    return False
        return True

    def time_since(self, other_event: "Event") -> float:
        """
        Calculate time difference from another event in minutes.

        Args:
            other_event: Event to compare against

        Returns:
            Minutes between events (positive if this event is later)
        """
        delta = self.timestamp - other_event.timestamp
        return delta.total_seconds() / 60.0

    def __repr__(self) -> str:
        return (
            f"Event(id='{self.id[:8]}...', type={self.event_type.value}, "
            f"severity={self.severity.value}, title='{self.title}')"
        )
