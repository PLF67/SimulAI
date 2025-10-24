"""
Analysis tools for event correlations.

Provides statistical analysis and insights about event correlations
and causal relationships.
"""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

from ..events.models import Event, EventType, EventSeverity
from ..events.relationships import CausalRelationship, CausalityType


class CorrelationAnalyzer:
    """
    Provides analysis and insights on event correlations.

    Computes statistics, identifies key events, and generates reports.
    """

    def __init__(self, engine: "CorrelationEngine"):
        """
        Initialize analyzer with a correlation engine.

        Args:
            engine: CorrelationEngine instance to analyze
        """
        self.engine = engine

    def get_most_influential_events(self, top_n: int = 10) -> List[Tuple[Event, int]]:
        """
        Find events that caused the most other events.

        Args:
            top_n: Number of top events to return

        Returns:
            List of (event, effect_count) tuples
        """
        event_effects = []

        for event in self.engine.events.values():
            effect_count = len(self.engine.get_effects(event.id))
            if effect_count > 0:
                event_effects.append((event, effect_count))

        event_effects.sort(key=lambda x: x[1], reverse=True)
        return event_effects[:top_n]

    def get_most_affected_events(self, top_n: int = 10) -> List[Tuple[Event, int]]:
        """
        Find events that were caused by the most other events.

        Args:
            top_n: Number of top events to return

        Returns:
            List of (event, cause_count) tuples
        """
        event_causes = []

        for event in self.engine.events.values():
            cause_count = len(self.engine.get_causes(event.id))
            if cause_count > 0:
                event_causes.append((event, cause_count))

        event_causes.sort(key=lambda x: x[1], reverse=True)
        return event_causes[:top_n]

    def get_causality_type_distribution(self) -> Dict[CausalityType, int]:
        """
        Get distribution of causality types.

        Returns:
            Dictionary mapping causality type to count
        """
        return Counter(rel.causality_type for rel in self.engine.relationships.values())

    def get_event_type_interactions(self) -> Dict[Tuple[EventType, EventType], int]:
        """
        Get most common event type interactions (cause -> effect).

        Returns:
            Dictionary mapping (cause_type, effect_type) to count
        """
        interactions = Counter()

        for rel in self.engine.relationships.values():
            cause = self.engine.events.get(rel.cause_event_id)
            effect = self.engine.events.get(rel.effect_event_id)

            if cause and effect:
                interactions[(cause.event_type, effect.event_type)] += 1

        return dict(interactions)

    def get_average_relationship_strength(self) -> Dict[str, float]:
        """
        Calculate average relationship strengths by causality type.

        Returns:
            Dictionary mapping causality type to average confidence score
        """
        strengths_by_type: Dict[CausalityType, List[float]] = defaultdict(list)

        for rel in self.engine.relationships.values():
            strengths_by_type[rel.causality_type].append(rel.confidence_score)

        averages = {}
        for causality_type, scores in strengths_by_type.items():
            averages[causality_type.value] = sum(scores) / len(scores) if scores else 0.0

        return averages

    def get_temporal_distribution(self, bucket_minutes: int = 60) -> Dict[str, int]:
        """
        Get temporal distribution of events.

        Args:
            bucket_minutes: Size of time buckets in minutes

        Returns:
            Dictionary mapping time bucket to event count
        """
        if not self.engine.events:
            return {}

        events = sorted(self.engine.events.values(), key=lambda e: e.timestamp)
        start_time = events[0].timestamp

        distribution = Counter()

        for event in events:
            minutes_since_start = (event.timestamp - start_time).total_seconds() / 60
            bucket = int(minutes_since_start // bucket_minutes)
            bucket_label = f"{bucket * bucket_minutes}-{(bucket + 1) * bucket_minutes} min"
            distribution[bucket_label] += 1

        return dict(distribution)

    def get_severity_impact_analysis(self) -> Dict[EventSeverity, Dict[str, float]]:
        """
        Analyze impact of events by severity level.

        Returns:
            Dictionary mapping severity to impact metrics
        """
        severity_metrics: Dict[EventSeverity, Dict[str, List[float]]] = defaultdict(
            lambda: {"effects": [], "confidence": []}
        )

        for event in self.engine.events.values():
            effects = self.engine.get_effects(event.id)
            severity_metrics[event.severity]["effects"].append(len(effects))

            # Average confidence of outgoing relationships
            if effects:
                avg_confidence = sum(rel.confidence_score for _, rel in effects) / len(effects)
                severity_metrics[event.severity]["confidence"].append(avg_confidence)

        # Compute averages
        result = {}
        for severity, metrics in severity_metrics.items():
            result[severity] = {
                "avg_effects": (
                    sum(metrics["effects"]) / len(metrics["effects"])
                    if metrics["effects"]
                    else 0.0
                ),
                "avg_confidence": (
                    sum(metrics["confidence"]) / len(metrics["confidence"])
                    if metrics["confidence"]
                    else 0.0
                ),
                "event_count": len(metrics["effects"]),
            }

        return result

    def find_critical_paths(self, min_length: int = 3) -> List[List[Event]]:
        """
        Find critical causal paths (long chains of high-confidence relationships).

        Args:
            min_length: Minimum path length

        Returns:
            List of event chains (paths)
        """
        paths = []

        # Start from events with no causes (root events)
        root_events = [
            e for e in self.engine.events.values() if not self.engine.get_causes(e.id)
        ]

        for root in root_events:
            self._explore_paths(root, [], paths, min_length)

        # Sort by average confidence
        def path_confidence(path: List[Event]) -> float:
            total_conf = 0.0
            count = 0
            for i in range(len(path) - 1):
                effects = self.engine.get_effects(path[i].id)
                for effect, rel in effects:
                    if effect.id == path[i + 1].id:
                        total_conf += rel.confidence_score
                        count += 1
            return total_conf / count if count > 0 else 0.0

        paths.sort(key=path_confidence, reverse=True)
        return paths

    def _explore_paths(
        self, current: Event, path: List[Event], all_paths: List[List[Event]], min_length: int
    ) -> None:
        """Recursively explore causal paths."""
        path = path + [current]

        effects = self.engine.get_effects(current.id)

        if not effects:
            # End of path
            if len(path) >= min_length:
                all_paths.append(path)
        else:
            # Continue exploring
            for effect_event, rel in effects:
                if rel.confidence_score >= self.engine.min_confidence:
                    if effect_event not in path:  # Avoid cycles
                        self._explore_paths(effect_event, path, all_paths, min_length)

            # Also save current path if long enough
            if len(path) >= min_length:
                all_paths.append(path)

    def generate_summary_report(self) -> str:
        """
        Generate a comprehensive summary report.

        Returns:
            Formatted text report
        """
        stats = self.engine.get_statistics()

        report = []
        report.append("=" * 60)
        report.append("EVENT CORRELATION ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")

        # Basic statistics
        report.append("BASIC STATISTICS")
        report.append("-" * 60)
        report.append(f"Total Events: {stats['total_events']}")
        report.append(f"Total Relationships: {stats['total_relationships']}")
        report.append(f"Rules Applied: {stats['rules_applied']}")
        report.append(f"Patterns Detected: {stats['patterns_detected']}")
        report.append("")

        # Most influential events
        report.append("MOST INFLUENTIAL EVENTS (Top 5)")
        report.append("-" * 60)
        for event, count in self.get_most_influential_events(5):
            report.append(f"  {event.title} ({event.event_type.value}): {count} effects")
        report.append("")

        # Causality type distribution
        report.append("CAUSALITY TYPE DISTRIBUTION")
        report.append("-" * 60)
        for causality_type, count in self.get_causality_type_distribution().items():
            report.append(f"  {causality_type.value}: {count}")
        report.append("")

        # Event type interactions
        report.append("TOP EVENT TYPE INTERACTIONS")
        report.append("-" * 60)
        interactions = self.get_event_type_interactions()
        sorted_interactions = sorted(interactions.items(), key=lambda x: x[1], reverse=True)[:5]
        for (cause_type, effect_type), count in sorted_interactions:
            report.append(f"  {cause_type.value} → {effect_type.value}: {count}")
        report.append("")

        # Average strengths
        report.append("AVERAGE RELATIONSHIP STRENGTH BY TYPE")
        report.append("-" * 60)
        for causality_type, avg in self.get_average_relationship_strength().items():
            report.append(f"  {causality_type}: {avg:.2f}")
        report.append("")

        report.append("=" * 60)

        return "\n".join(report)

    def __repr__(self) -> str:
        return f"CorrelationAnalyzer(engine={self.engine})"
