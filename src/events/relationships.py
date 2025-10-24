"""
Causal relationship models for event correlation.

Defines different types of causal relationships between events and their properties.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CausalityType(str, Enum):
    """
    Types of causal relationships between events.

    Each type represents a different kind of causation that can exist
    in the business simulation.
    """

    # Direct causality: A directly causes B with high certainty
    DIRECT = "direct"

    # Indirect causality: A causes B through intermediary events
    INDIRECT = "indirect"

    # Contributory: A contributes to B but doesn't fully cause it
    CONTRIBUTORY = "contributory"

    # Conditional: A causes B only under certain conditions
    CONDITIONAL = "conditional"

    # Probabilistic: A increases probability of B occurring
    PROBABILISTIC = "probabilistic"

    # Preventive: A prevents B from occurring
    PREVENTIVE = "preventive"

    # Catalytic: A accelerates or amplifies B
    CATALYTIC = "catalytic"

    # Suppressive: A reduces the likelihood or impact of B
    SUPPRESSIVE = "suppressive"

    # Correlational: A and B occur together but causality unclear
    CORRELATIONAL = "correlational"


class RelationshipStrength(str, Enum):
    """Strength of a causal relationship."""

    VERY_STRONG = "very_strong"    # 0.8-1.0
    STRONG = "strong"              # 0.6-0.8
    MODERATE = "moderate"          # 0.4-0.6
    WEAK = "weak"                  # 0.2-0.4
    VERY_WEAK = "very_weak"        # 0.0-0.2

    @classmethod
    def from_score(cls, score: float) -> "RelationshipStrength":
        """Convert a numeric score to a strength category."""
        if score >= 0.8:
            return cls.VERY_STRONG
        elif score >= 0.6:
            return cls.STRONG
        elif score >= 0.4:
            return cls.MODERATE
        elif score >= 0.2:
            return cls.WEAK
        else:
            return cls.VERY_WEAK


class CausalRelationship(BaseModel):
    """
    Represents a causal relationship between two events.

    Captures the nature, strength, and confidence of how one event
    influences another.
    """

    cause_event_id: str = Field(..., description="ID of the causing event")
    effect_event_id: str = Field(..., description="ID of the effect event")

    causality_type: CausalityType = Field(..., description="Type of causal relationship")
    strength: RelationshipStrength = Field(..., description="Strength of the relationship")

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this causal relationship (0-1)"
    )

    time_lag_minutes: Optional[float] = Field(
        None,
        description="Time between cause and effect in minutes"
    )

    # Conditional factors
    conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Conditions required for this causality to hold"
    )

    # Quantitative impact
    impact_magnitude: Optional[float] = Field(
        None,
        description="Quantitative measure of impact (domain-specific)"
    )

    impact_direction: Optional[int] = Field(
        None,
        ge=-1,
        le=1,
        description="Direction of impact: 1 (positive), -1 (negative), 0 (neutral)"
    )

    # Metadata
    discovered_at: datetime = Field(
        default_factory=datetime.now,
        description="When this relationship was identified"
    )

    discovery_method: str = Field(
        default="manual",
        description="How this relationship was discovered (e.g., 'rule', 'pattern', 'ml')"
    )

    notes: Optional[str] = Field(None, description="Additional notes about the relationship")

    # Domain-specific attributes
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional domain-specific relationship attributes"
    )

    class Config:
        frozen = False
        json_schema_extra = {
            "example": {
                "cause_event_id": "evt-001",
                "effect_event_id": "evt-002",
                "causality_type": "direct",
                "strength": "strong",
                "confidence_score": 0.85,
                "time_lag_minutes": 30,
                "impact_magnitude": 0.15,
                "impact_direction": 1,
                "discovery_method": "rule"
            }
        }

    def is_significant(self, min_confidence: float = 0.5) -> bool:
        """
        Determine if this relationship is statistically significant.

        Args:
            min_confidence: Minimum confidence threshold

        Returns:
            True if confidence meets threshold and strength is at least weak
        """
        return (
            self.confidence_score >= min_confidence
            and self.strength != RelationshipStrength.VERY_WEAK
        )

    def get_causal_weight(self) -> float:
        """
        Calculate a composite weight for this causal relationship.

        Combines strength and confidence into a single metric.

        Returns:
            Weight value between 0 and 1
        """
        strength_weights = {
            RelationshipStrength.VERY_STRONG: 1.0,
            RelationshipStrength.STRONG: 0.75,
            RelationshipStrength.MODERATE: 0.5,
            RelationshipStrength.WEAK: 0.25,
            RelationshipStrength.VERY_WEAK: 0.1,
        }

        return strength_weights[self.strength] * self.confidence_score

    def __repr__(self) -> str:
        return (
            f"CausalRelationship(cause={self.cause_event_id[:8]}..., "
            f"effect={self.effect_event_id[:8]}..., "
            f"type={self.causality_type.value}, "
            f"strength={self.strength.value}, "
            f"confidence={self.confidence_score:.2f})"
        )
