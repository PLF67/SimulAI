"""
Core correlation engine for event analysis.

The main engine that processes events, discovers causal relationships,
and maintains the event correlation graph.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
import logging

from ..events.models import Event, EventType
from ..events.relationships import CausalRelationship, CausalityType, RelationshipStrength
from .rules import CausalRule, CausalRuleLibrary
from .patterns import PatternDetector, EventPattern

try:
    import networkx as nx
except ImportError:
    nx = None


logger = logging.getLogger(__name__)


class CorrelationEngine:
    """
    Main engine for event correlation and causal analysis.

    Manages events, discovers relationships, and provides analysis capabilities.
    """

    def __init__(
        self,
        time_window_minutes: float = 1440,  # 24 hours
        min_confidence: float = 0.5,
        auto_discover: bool = True,
    ):
        """
        Initialize the correlation engine.

        Args:
            time_window_minutes: Time window for considering causal relationships
            min_confidence: Minimum confidence threshold for relationships
            auto_discover: Automatically discover relationships when events are added
        """
        self.time_window_minutes = time_window_minutes
        self.min_confidence = min_confidence
        self.auto_discover = auto_discover

        # Event storage
        self.events: Dict[str, Event] = {}
        self.events_by_type: Dict[EventType, List[Event]] = defaultdict(list)
        self.events_by_timestamp: List[Event] = []

        # Relationship storage
        self.relationships: Dict[str, CausalRelationship] = {}
        self.relationships_by_cause: Dict[str, List[CausalRelationship]] = defaultdict(list)
        self.relationships_by_effect: Dict[str, List[CausalRelationship]] = defaultdict(list)

        # Rule library
        self.rule_library = CausalRuleLibrary()

        # Pattern detector
        self.pattern_detector = PatternDetector(
            min_support=0.1,
            min_confidence=min_confidence,
            max_time_window_minutes=time_window_minutes,
        )

        # Statistics
        self.stats = {
            "events_processed": 0,
            "relationships_discovered": 0,
            "rules_applied": 0,
            "patterns_detected": 0,
        }

    def add_event(self, event: Event) -> None:
        """
        Add an event to the engine.

        Args:
            event: Event to add
        """
        if event.id in self.events:
            logger.warning(f"Event {event.id} already exists, skipping")
            return

        # Store event
        self.events[event.id] = event
        self.events_by_type[event.event_type].append(event)
        self.events_by_timestamp.append(event)
        self.events_by_timestamp.sort(key=lambda e: e.timestamp)

        self.stats["events_processed"] += 1

        # Auto-discover relationships if enabled
        if self.auto_discover:
            self._discover_relationships_for_event(event)

    def add_events(self, events: List[Event]) -> None:
        """Add multiple events in batch."""
        for event in events:
            self.add_event(event)

    def add_rule(self, rule: CausalRule) -> None:
        """Add a causal rule to the engine."""
        self.rule_library.add_rule(rule)

    def _discover_relationships_for_event(self, event: Event) -> None:
        """
        Discover relationships for a newly added event.

        Checks if this event is caused by or causes other events.
        """
        # Check if this event is an effect of previous events
        time_cutoff = event.timestamp - timedelta(minutes=self.time_window_minutes)
        potential_causes = [
            e for e in self.events_by_timestamp if time_cutoff <= e.timestamp < event.timestamp
        ]

        for cause in potential_causes:
            self._check_causal_relationship(cause, event)

        # Check if this event causes later events
        time_cutoff = event.timestamp + timedelta(minutes=self.time_window_minutes)
        potential_effects = [
            e for e in self.events_by_timestamp if event.timestamp < e.timestamp <= time_cutoff
        ]

        for effect in potential_effects:
            self._check_causal_relationship(event, effect)

    def _check_causal_relationship(self, cause: Event, effect: Event) -> None:
        """
        Check if a causal relationship exists between two events.

        Args:
            cause: Potential causing event
            effect: Potential effect event
        """
        # Find matching rules
        matches = self.rule_library.find_matching_rules(cause, effect)

        for rule, relationship_details in matches:
            # Create relationship
            rel = CausalRelationship(
                cause_event_id=cause.id,
                effect_event_id=effect.id,
                **relationship_details,
            )

            # Store relationship if significant
            if rel.is_significant(self.min_confidence):
                self._add_relationship(rel)
                self.stats["rules_applied"] += 1

    def _add_relationship(self, relationship: CausalRelationship) -> None:
        """Add a causal relationship to the engine."""
        rel_id = f"{relationship.cause_event_id}->{relationship.effect_event_id}"

        if rel_id in self.relationships:
            # Update existing relationship if new one has higher confidence
            existing = self.relationships[rel_id]
            if relationship.confidence_score > existing.confidence_score:
                self.relationships[rel_id] = relationship
        else:
            self.relationships[rel_id] = relationship
            self.stats["relationships_discovered"] += 1

        # Update indices
        self.relationships_by_cause[relationship.cause_event_id].append(relationship)
        self.relationships_by_effect[relationship.effect_event_id].append(relationship)

        # Update event objects
        cause_event = self.events.get(relationship.cause_event_id)
        effect_event = self.events.get(relationship.effect_event_id)

        if cause_event:
            cause_event.add_effect(relationship.effect_event_id)
        if effect_event:
            effect_event.add_cause(relationship.cause_event_id)

    def add_manual_relationship(
        self,
        cause_event_id: str,
        effect_event_id: str,
        causality_type: CausalityType,
        strength: RelationshipStrength,
        confidence: float = 1.0,
        **kwargs: Any,
    ) -> Optional[CausalRelationship]:
        """
        Manually add a causal relationship.

        Args:
            cause_event_id: ID of causing event
            effect_event_id: ID of effect event
            causality_type: Type of causality
            strength: Strength of relationship
            confidence: Confidence score
            **kwargs: Additional relationship attributes

        Returns:
            Created relationship or None if events don't exist
        """
        if cause_event_id not in self.events or effect_event_id not in self.events:
            logger.error("One or both events not found")
            return None

        cause = self.events[cause_event_id]
        effect = self.events[effect_event_id]

        rel = CausalRelationship(
            cause_event_id=cause_event_id,
            effect_event_id=effect_event_id,
            causality_type=causality_type,
            strength=strength,
            confidence_score=confidence,
            time_lag_minutes=effect.time_since(cause),
            discovery_method="manual",
            **kwargs,
        )

        self._add_relationship(rel)
        return rel

    def get_causes(self, event_id: str) -> List[Tuple[Event, CausalRelationship]]:
        """
        Get all events that caused the specified event.

        Args:
            event_id: ID of the effect event

        Returns:
            List of (cause_event, relationship) tuples
        """
        relationships = self.relationships_by_effect.get(event_id, [])
        result = []

        for rel in relationships:
            cause = self.events.get(rel.cause_event_id)
            if cause:
                result.append((cause, rel))

        return result

    def get_effects(self, event_id: str) -> List[Tuple[Event, CausalRelationship]]:
        """
        Get all events caused by the specified event.

        Args:
            event_id: ID of the cause event

        Returns:
            List of (effect_event, relationship) tuples
        """
        relationships = self.relationships_by_cause.get(event_id, [])
        result = []

        for rel in relationships:
            effect = self.events.get(rel.effect_event_id)
            if effect:
                result.append((effect, rel))

        return result

    def get_causal_chain(
        self, event_id: str, direction: str = "forward", max_depth: int = 10
    ) -> List[Event]:
        """
        Get the causal chain from an event.

        Args:
            event_id: Starting event ID
            direction: "forward" for effects, "backward" for causes
            max_depth: Maximum chain depth

        Returns:
            List of events in the causal chain
        """
        if event_id not in self.events:
            return []

        visited = set()
        chain = []

        def traverse(curr_id: str, depth: int) -> None:
            if depth >= max_depth or curr_id in visited:
                return

            visited.add(curr_id)
            event = self.events.get(curr_id)
            if event:
                chain.append(event)

            if direction == "forward":
                for effect, _ in self.get_effects(curr_id):
                    traverse(effect.id, depth + 1)
            else:  # backward
                for cause, _ in self.get_causes(curr_id):
                    traverse(cause.id, depth + 1)

        traverse(event_id, 0)
        return chain

    def detect_patterns(self) -> Dict[str, List[EventPattern]]:
        """
        Detect patterns in the event stream.

        Returns:
            Dictionary of detected patterns by type
        """
        events_list = list(self.events.values())
        patterns = self.pattern_detector.analyze_all_patterns(events_list)

        total_patterns = sum(len(p) for p in patterns.values())
        self.stats["patterns_detected"] = total_patterns

        return patterns

    def build_event_graph(self) -> Optional[Any]:
        """
        Build a NetworkX graph of events and relationships.

        Returns:
            NetworkX DiGraph or None if networkx not available
        """
        if nx is None:
            logger.warning("NetworkX not available, cannot build graph")
            return None

        G = nx.DiGraph()

        # Add nodes (events)
        for event in self.events.values():
            G.add_node(
                event.id,
                event_type=event.event_type.value,
                timestamp=event.timestamp.isoformat(),
                title=event.title,
                severity=event.severity.value,
            )

        # Add edges (relationships)
        for rel in self.relationships.values():
            G.add_edge(
                rel.cause_event_id,
                rel.effect_event_id,
                causality_type=rel.causality_type.value,
                strength=rel.strength.value,
                confidence=rel.confidence_score,
                weight=rel.get_causal_weight(),
            )

        return G

    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            **self.stats,
            "total_events": len(self.events),
            "total_relationships": len(self.relationships),
            "rules_loaded": len(self.rule_library),
            "event_types": len(self.events_by_type),
        }

    def clear(self) -> None:
        """Clear all events and relationships."""
        self.events.clear()
        self.events_by_type.clear()
        self.events_by_timestamp.clear()
        self.relationships.clear()
        self.relationships_by_cause.clear()
        self.relationships_by_effect.clear()
        self.pattern_detector.detected_patterns.clear()

        self.stats = {
            "events_processed": 0,
            "relationships_discovered": 0,
            "rules_applied": 0,
            "patterns_detected": 0,
        }

    def __repr__(self) -> str:
        return (
            f"CorrelationEngine("
            f"{len(self.events)} events, "
            f"{len(self.relationships)} relationships, "
            f"{len(self.rule_library)} rules)"
        )
