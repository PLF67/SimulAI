"""
Causal rule definitions for the correlation engine.

Rules define known causal relationships and conditions under which
events cause other events in the business simulation.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..events.models import Event, EventType
from ..events.relationships import CausalityType, RelationshipStrength


@dataclass
class CausalRule:
    """
    Defines a rule for identifying causal relationships between events.

    Rules specify patterns that indicate one event type causes another,
    along with conditions and expected characteristics.
    """

    name: str
    description: str

    # Event patterns
    cause_pattern: Dict[str, Any]  # Pattern to match cause event
    effect_pattern: Dict[str, Any]  # Pattern to match effect event

    # Relationship characteristics
    causality_type: CausalityType
    base_strength: RelationshipStrength
    base_confidence: float  # 0-1

    # Temporal constraints
    min_time_lag_minutes: Optional[float] = None
    max_time_lag_minutes: Optional[float] = None

    # Conditions
    condition_func: Optional[Callable[[Event, Event], bool]] = None
    required_context: Dict[str, Any] = field(default_factory=dict)

    # Impact estimation
    impact_calculator: Optional[Callable[[Event, Event], float]] = None

    # Metadata
    tags: List[str] = field(default_factory=list)
    priority: int = 1  # Higher priority rules are evaluated first

    def matches_cause(self, event: Event) -> bool:
        """Check if an event matches the cause pattern."""
        return event.matches_pattern(self.cause_pattern)

    def matches_effect(self, event: Event) -> bool:
        """Check if an event matches the effect pattern."""
        return event.matches_pattern(self.effect_pattern)

    def is_temporal_match(self, cause: Event, effect: Event) -> bool:
        """Check if temporal constraints are satisfied."""
        time_diff = effect.time_since(cause)

        if time_diff < 0:  # Effect before cause
            return False

        if self.min_time_lag_minutes and time_diff < self.min_time_lag_minutes:
            return False

        if self.max_time_lag_minutes and time_diff > self.max_time_lag_minutes:
            return False

        return True

    def evaluate(self, cause: Event, effect: Event) -> Optional[Dict[str, Any]]:
        """
        Evaluate if this rule applies to a cause-effect pair.

        Args:
            cause: Potential causing event
            effect: Potential effect event

        Returns:
            Dictionary with relationship details if rule matches, None otherwise
        """
        # Check basic pattern matching
        if not self.matches_cause(cause):
            return None
        if not self.matches_effect(effect):
            return None

        # Check temporal constraints
        if not self.is_temporal_match(cause, effect):
            return None

        # Check custom conditions
        if self.condition_func and not self.condition_func(cause, effect):
            return None

        # Calculate impact if calculator provided
        impact = None
        if self.impact_calculator:
            impact = self.impact_calculator(cause, effect)

        # Build relationship details
        return {
            "causality_type": self.causality_type,
            "strength": self.base_strength,
            "confidence_score": self.base_confidence,
            "time_lag_minutes": effect.time_since(cause),
            "impact_magnitude": impact,
            "discovery_method": f"rule:{self.name}",
            "notes": self.description,
        }

    def __repr__(self) -> str:
        return f"CausalRule(name='{self.name}', type={self.causality_type.value})"


class CausalRuleLibrary:
    """
    Collection of causal rules with efficient lookup and matching.

    Organizes rules by event types for fast pattern matching.
    """

    def __init__(self):
        self.rules: List[CausalRule] = []
        self._rules_by_cause_type: Dict[EventType, List[CausalRule]] = {}
        self._rules_by_effect_type: Dict[EventType, List[CausalRule]] = {}

    def add_rule(self, rule: CausalRule) -> None:
        """Add a rule to the library."""
        self.rules.append(rule)
        self._index_rule(rule)

    def _index_rule(self, rule: CausalRule) -> None:
        """Index rule by event types for efficient lookup."""
        # Index by cause type if specified
        if "event_type" in rule.cause_pattern:
            cause_type = rule.cause_pattern["event_type"]
            if cause_type not in self._rules_by_cause_type:
                self._rules_by_cause_type[cause_type] = []
            self._rules_by_cause_type[cause_type].append(rule)

        # Index by effect type if specified
        if "event_type" in rule.effect_pattern:
            effect_type = rule.effect_pattern["event_type"]
            if effect_type not in self._rules_by_effect_type:
                self._rules_by_effect_type[effect_type] = []
            self._rules_by_effect_type[effect_type].append(rule)

    def get_rules_for_cause(self, cause: Event) -> List[CausalRule]:
        """Get all rules that might match this cause event."""
        # Start with rules indexed by this event type
        rules = self._rules_by_cause_type.get(cause.event_type, []).copy()

        # Add rules without specific cause type (check all)
        for rule in self.rules:
            if "event_type" not in rule.cause_pattern and rule not in rules:
                rules.append(rule)

        # Sort by priority
        rules.sort(key=lambda r: r.priority, reverse=True)
        return rules

    def get_rules_for_effect(self, effect: Event) -> List[CausalRule]:
        """Get all rules that might match this effect event."""
        rules = self._rules_by_effect_type.get(effect.event_type, []).copy()

        for rule in self.rules:
            if "event_type" not in rule.effect_pattern and rule not in rules:
                rules.append(rule)

        rules.sort(key=lambda r: r.priority, reverse=True)
        return rules

    def find_matching_rules(
        self, cause: Event, effect: Event
    ) -> List[tuple[CausalRule, Dict[str, Any]]]:
        """
        Find all rules that match a cause-effect pair.

        Args:
            cause: Potential causing event
            effect: Potential effect event

        Returns:
            List of (rule, relationship_details) tuples
        """
        matches = []
        rules = self.get_rules_for_cause(cause)

        for rule in rules:
            result = rule.evaluate(cause, effect)
            if result:
                matches.append((rule, result))

        return matches

    def __len__(self) -> int:
        return len(self.rules)

    def __repr__(self) -> str:
        return f"CausalRuleLibrary({len(self.rules)} rules)"
