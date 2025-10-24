"""
Pattern detection for event sequences and correlations.

Identifies recurring patterns, sequences, and anomalies in event streams.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

from ..events.models import Event, EventType


@dataclass
class EventPattern:
    """
    Represents a detected pattern in event sequences.

    Patterns can be temporal sequences, co-occurrences, or other
    recurring structures in the event stream.
    """

    pattern_id: str
    pattern_type: str  # "sequence", "co_occurrence", "periodic", "cascade"
    description: str

    # Events involved
    event_types: List[EventType]
    event_sequence: Optional[List[str]] = None  # IDs in order if sequential

    # Temporal characteristics
    typical_duration_minutes: Optional[float] = None
    typical_intervals_minutes: List[float] = field(default_factory=list)

    # Statistical properties
    occurrence_count: int = 0
    confidence: float = 0.0
    support: float = 0.0  # Frequency in dataset

    # Metadata
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    attributes: Dict[str, any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"EventPattern(id='{self.pattern_id}', type={self.pattern_type}, "
            f"events={[et.value for et in self.event_types]}, "
            f"occurrences={self.occurrence_count})"
        )


class PatternDetector:
    """
    Detects patterns in event streams using various algorithms.

    Identifies sequences, co-occurrences, periodic patterns, and cascades.
    """

    def __init__(
        self,
        min_support: float = 0.1,
        min_confidence: float = 0.5,
        max_time_window_minutes: float = 1440,  # 24 hours
    ):
        """
        Initialize pattern detector.

        Args:
            min_support: Minimum frequency for pattern to be significant
            min_confidence: Minimum confidence for pattern relationships
            max_time_window_minutes: Maximum time window for pattern detection
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.max_time_window_minutes = max_time_window_minutes

        self.detected_patterns: Dict[str, EventPattern] = {}
        self._pattern_counter = 0

    def detect_sequences(
        self, events: List[Event], max_sequence_length: int = 5
    ) -> List[EventPattern]:
        """
        Detect sequential patterns in events.

        Finds common sequences of event types that occur in order.

        Args:
            events: List of events to analyze
            max_sequence_length: Maximum length of sequences to detect

        Returns:
            List of detected sequential patterns
        """
        if not events:
            return []

        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        # Find sequences
        sequences: Dict[Tuple[EventType, ...], List[List[Event]]] = defaultdict(list)

        for i, event in enumerate(sorted_events):
            # Try to extend existing sequences or start new ones
            for length in range(2, max_sequence_length + 1):
                if i < length - 1:
                    continue

                # Get sequence of events
                sequence_events = sorted_events[i - length + 1 : i + 1]

                # Check temporal constraint
                time_span = (
                    sequence_events[-1].timestamp - sequence_events[0].timestamp
                )
                if time_span.total_seconds() / 60 > self.max_time_window_minutes:
                    continue

                # Create sequence key
                sequence_key = tuple(e.event_type for e in sequence_events)
                sequences[sequence_key].append(sequence_events)

        # Convert to patterns
        patterns = []
        total_windows = len(sorted_events)

        for sequence_types, occurrences in sequences.items():
            support = len(occurrences) / total_windows if total_windows > 0 else 0

            if support >= self.min_support and len(occurrences) >= 2:
                # Calculate typical intervals
                intervals = []
                for occurrence in occurrences:
                    if len(occurrence) > 1:
                        for i in range(1, len(occurrence)):
                            delta = occurrence[i].timestamp - occurrence[i - 1].timestamp
                            intervals.append(delta.total_seconds() / 60)

                avg_duration = sum(intervals) / len(intervals) if intervals else None

                pattern = EventPattern(
                    pattern_id=f"seq_{self._pattern_counter}",
                    pattern_type="sequence",
                    description=f"Sequence: {' -> '.join(t.value for t in sequence_types)}",
                    event_types=list(sequence_types),
                    typical_duration_minutes=avg_duration,
                    occurrence_count=len(occurrences),
                    confidence=min(support * 2, 1.0),  # Heuristic
                    support=support,
                    first_seen=occurrences[0][0].timestamp,
                    last_seen=occurrences[-1][-1].timestamp,
                )

                patterns.append(pattern)
                self.detected_patterns[pattern.pattern_id] = pattern
                self._pattern_counter += 1

        return patterns

    def detect_co_occurrences(
        self, events: List[Event], time_window_minutes: float = 60
    ) -> List[EventPattern]:
        """
        Detect events that frequently occur together.

        Args:
            events: List of events to analyze
            time_window_minutes: Time window for co-occurrence

        Returns:
            List of co-occurrence patterns
        """
        if not events:
            return []

        sorted_events = sorted(events, key=lambda e: e.timestamp)

        # Find co-occurrences
        co_occurrences: Dict[Tuple[EventType, EventType], int] = defaultdict(int)
        event_counts: Dict[EventType, int] = defaultdict(int)

        for i, event1 in enumerate(sorted_events):
            event_counts[event1.event_type] += 1

            for event2 in sorted_events[i + 1 :]:
                # Check time window
                time_diff = (event2.timestamp - event1.timestamp).total_seconds() / 60
                if time_diff > time_window_minutes:
                    break

                if event1.event_type != event2.event_type:
                    pair = tuple(sorted([event1.event_type, event2.event_type]))
                    co_occurrences[pair] += 1

        # Convert to patterns
        patterns = []
        total_events = len(sorted_events)

        for (type1, type2), count in co_occurrences.items():
            support = count / total_events if total_events > 0 else 0

            if support >= self.min_support and count >= 2:
                # Calculate confidence
                conf1 = count / event_counts[type1] if event_counts[type1] > 0 else 0
                conf2 = count / event_counts[type2] if event_counts[type2] > 0 else 0
                confidence = max(conf1, conf2)

                if confidence >= self.min_confidence:
                    pattern = EventPattern(
                        pattern_id=f"cooc_{self._pattern_counter}",
                        pattern_type="co_occurrence",
                        description=f"Co-occurrence: {type1.value} with {type2.value}",
                        event_types=[type1, type2],
                        occurrence_count=count,
                        confidence=confidence,
                        support=support,
                        attributes={"time_window_minutes": time_window_minutes},
                    )

                    patterns.append(pattern)
                    self.detected_patterns[pattern.pattern_id] = pattern
                    self._pattern_counter += 1

        return patterns

    def detect_cascades(
        self, events: List[Event], min_cascade_length: int = 3
    ) -> List[EventPattern]:
        """
        Detect cascade patterns where one event triggers a chain of events.

        Args:
            events: List of events to analyze
            min_cascade_length: Minimum number of events in a cascade

        Returns:
            List of cascade patterns
        """
        cascades = []

        # Group events by their triggered_by relationships
        events_by_id = {e.id: e for e in events}
        cascades_found: List[List[Event]] = []

        for event in events:
            if not event.triggered_by:  # Root event
                cascade = self._build_cascade_chain(event, events_by_id)
                if len(cascade) >= min_cascade_length:
                    cascades_found.append(cascade)

        # Convert to patterns
        for cascade_events in cascades_found:
            event_types = [e.event_type for e in cascade_events]
            duration = (
                cascade_events[-1].timestamp - cascade_events[0].timestamp
            ).total_seconds() / 60

            pattern = EventPattern(
                pattern_id=f"casc_{self._pattern_counter}",
                pattern_type="cascade",
                description=f"Cascade: {len(cascade_events)} events",
                event_types=event_types,
                event_sequence=[e.id for e in cascade_events],
                typical_duration_minutes=duration,
                occurrence_count=1,
                confidence=0.8,
                support=len(cascade_events) / len(events) if events else 0,
                first_seen=cascade_events[0].timestamp,
                last_seen=cascade_events[-1].timestamp,
            )

            cascades.append(pattern)
            self.detected_patterns[pattern.pattern_id] = pattern
            self._pattern_counter += 1

        return cascades

    def _build_cascade_chain(
        self, root: Event, events_by_id: Dict[str, Event]
    ) -> List[Event]:
        """Recursively build a cascade chain from a root event."""
        chain = [root]

        for triggered_id in root.triggers:
            if triggered_id in events_by_id:
                triggered_event = events_by_id[triggered_id]
                child_chain = self._build_cascade_chain(triggered_event, events_by_id)
                chain.extend(child_chain)

        return chain

    def find_periodic_patterns(
        self, events: List[Event], tolerance_minutes: float = 30
    ) -> List[EventPattern]:
        """
        Detect periodic patterns (events that recur at regular intervals).

        Args:
            events: List of events to analyze
            tolerance_minutes: Tolerance for interval variation

        Returns:
            List of periodic patterns
        """
        patterns = []

        # Group by event type
        events_by_type: Dict[EventType, List[Event]] = defaultdict(list)
        for event in events:
            events_by_type[event.event_type].append(event)

        for event_type, type_events in events_by_type.items():
            if len(type_events) < 3:
                continue

            # Sort by timestamp
            sorted_events = sorted(type_events, key=lambda e: e.timestamp)

            # Calculate intervals
            intervals = []
            for i in range(1, len(sorted_events)):
                delta = sorted_events[i].timestamp - sorted_events[i - 1].timestamp
                intervals.append(delta.total_seconds() / 60)

            if not intervals:
                continue

            # Check if intervals are relatively consistent
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
            std_dev = variance**0.5

            # If standard deviation is within tolerance, it's periodic
            if std_dev <= tolerance_minutes:
                pattern = EventPattern(
                    pattern_id=f"per_{self._pattern_counter}",
                    pattern_type="periodic",
                    description=f"Periodic: {event_type.value} every ~{avg_interval:.0f} min",
                    event_types=[event_type],
                    typical_intervals_minutes=intervals,
                    occurrence_count=len(sorted_events),
                    confidence=1.0 - min(std_dev / avg_interval, 1.0),
                    support=len(sorted_events) / len(events) if events else 0,
                    first_seen=sorted_events[0].timestamp,
                    last_seen=sorted_events[-1].timestamp,
                    attributes={
                        "average_interval_minutes": avg_interval,
                        "std_dev_minutes": std_dev,
                    },
                )

                patterns.append(pattern)
                self.detected_patterns[pattern.pattern_id] = pattern
                self._pattern_counter += 1

        return patterns

    def analyze_all_patterns(self, events: List[Event]) -> Dict[str, List[EventPattern]]:
        """
        Run all pattern detection algorithms.

        Args:
            events: List of events to analyze

        Returns:
            Dictionary mapping pattern type to list of detected patterns
        """
        return {
            "sequences": self.detect_sequences(events),
            "co_occurrences": self.detect_co_occurrences(events),
            "cascades": self.detect_cascades(events),
            "periodic": self.find_periodic_patterns(events),
        }

    def __repr__(self) -> str:
        return f"PatternDetector({len(self.detected_patterns)} patterns detected)"
