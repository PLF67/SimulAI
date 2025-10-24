"""
Tests for the correlation engine.

Run with: pytest tests/
"""

from datetime import datetime, timedelta
import pytest

from src.events.models import Event, EventType, EventSeverity, EventContext
from src.events.relationships import CausalityType, RelationshipStrength
from src.correlation.engine import CorrelationEngine
from src.correlation.rules import CausalRule
from src.business.rules import create_business_rules
from src.business.scenarios import BusinessScenarioGenerator


class TestEvent:
    """Test Event model."""

    def test_event_creation(self):
        """Test basic event creation."""
        event = Event(
            event_type=EventType.PRICE_CHANGE,
            severity=EventSeverity.HIGH,
            title="Price reduced",
            description="Price reduced by 10%",
            context=EventContext(
                domain="pricing",
                source="pricing_system",
            ),
        )

        assert event.id is not None
        assert event.event_type == EventType.PRICE_CHANGE
        assert event.severity == EventSeverity.HIGH
        assert event.confidence == 1.0

    def test_event_pattern_matching(self):
        """Test event pattern matching."""
        event = Event(
            event_type=EventType.PRICE_CHANGE,
            severity=EventSeverity.HIGH,
            title="Test",
            description="Test",
            context=EventContext(domain="pricing", source="test"),
            attributes={"direction": "decrease"},
        )

        assert event.matches_pattern({"event_type": EventType.PRICE_CHANGE})
        assert event.matches_pattern({"severity": EventSeverity.HIGH})
        assert event.matches_pattern({"domain": "pricing"})
        assert event.matches_pattern({"direction": "decrease"})
        assert not event.matches_pattern({"event_type": EventType.DEMAND_CHANGE})

    def test_time_since_calculation(self):
        """Test time difference calculation between events."""
        event1 = Event(
            timestamp=datetime(2025, 1, 1, 10, 0),
            event_type=EventType.PRICE_CHANGE,
            title="Test 1",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        event2 = Event(
            timestamp=datetime(2025, 1, 1, 11, 30),
            event_type=EventType.DEMAND_CHANGE,
            title="Test 2",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        assert event2.time_since(event1) == 90.0  # 90 minutes


class TestCausalRule:
    """Test CausalRule functionality."""

    def test_rule_matching(self):
        """Test rule pattern matching."""
        rule = CausalRule(
            name="test_rule",
            description="Test",
            cause_pattern={"event_type": EventType.PRICE_CHANGE},
            effect_pattern={"event_type": EventType.DEMAND_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.8,
        )

        cause = Event(
            event_type=EventType.PRICE_CHANGE,
            title="Price change",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        effect = Event(
            timestamp=cause.timestamp + timedelta(hours=1),
            event_type=EventType.DEMAND_CHANGE,
            title="Demand change",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        assert rule.matches_cause(cause)
        assert rule.matches_effect(effect)
        assert rule.is_temporal_match(cause, effect)

        result = rule.evaluate(cause, effect)
        assert result is not None
        assert result["causality_type"] == CausalityType.DIRECT
        assert result["confidence_score"] == 0.8


class TestCorrelationEngine:
    """Test CorrelationEngine functionality."""

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = CorrelationEngine()

        assert len(engine.events) == 0
        assert len(engine.relationships) == 0
        assert engine.min_confidence == 0.5

    def test_add_event(self):
        """Test adding events to engine."""
        engine = CorrelationEngine(auto_discover=False)

        event = Event(
            event_type=EventType.PRICE_CHANGE,
            title="Test",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        engine.add_event(event)

        assert len(engine.events) == 1
        assert event.id in engine.events
        assert engine.stats["events_processed"] == 1

    def test_relationship_discovery(self):
        """Test automatic relationship discovery."""
        engine = CorrelationEngine(auto_discover=True)

        # Add a simple rule
        rule = CausalRule(
            name="price_to_demand",
            description="Price changes affect demand",
            cause_pattern={"event_type": EventType.PRICE_CHANGE},
            effect_pattern={"event_type": EventType.DEMAND_CHANGE},
            causality_type=CausalityType.DIRECT,
            base_strength=RelationshipStrength.STRONG,
            base_confidence=0.8,
            max_time_lag_minutes=480,
        )
        engine.add_rule(rule)

        # Add events
        cause = Event(
            timestamp=datetime(2025, 1, 1, 10, 0),
            event_type=EventType.PRICE_CHANGE,
            title="Price reduced",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        effect = Event(
            timestamp=datetime(2025, 1, 1, 12, 0),
            event_type=EventType.DEMAND_CHANGE,
            title="Demand increased",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        engine.add_event(cause)
        engine.add_event(effect)

        # Should have discovered relationship
        assert len(engine.relationships) >= 1
        assert len(engine.get_effects(cause.id)) >= 1
        assert len(engine.get_causes(effect.id)) >= 1

    def test_causal_chain(self):
        """Test causal chain retrieval."""
        engine = CorrelationEngine(auto_discover=False)

        # Create chain: event1 -> event2 -> event3
        event1 = Event(
            timestamp=datetime(2025, 1, 1, 10, 0),
            event_type=EventType.PRICE_CHANGE,
            title="Event 1",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        event2 = Event(
            timestamp=datetime(2025, 1, 1, 11, 0),
            event_type=EventType.DEMAND_CHANGE,
            title="Event 2",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        event3 = Event(
            timestamp=datetime(2025, 1, 1, 12, 0),
            event_type=EventType.PURCHASE,
            title="Event 3",
            description="Test",
            context=EventContext(domain="test", source="test"),
        )

        engine.add_events([event1, event2, event3])

        # Manually add relationships
        engine.add_manual_relationship(
            event1.id,
            event2.id,
            CausalityType.DIRECT,
            RelationshipStrength.STRONG,
            0.9,
        )

        engine.add_manual_relationship(
            event2.id,
            event3.id,
            CausalityType.DIRECT,
            RelationshipStrength.STRONG,
            0.9,
        )

        # Get forward chain
        chain = engine.get_causal_chain(event1.id, direction="forward")

        assert len(chain) == 3
        assert chain[0].id == event1.id

    def test_statistics(self):
        """Test engine statistics."""
        engine = CorrelationEngine()

        stats = engine.get_statistics()

        assert "total_events" in stats
        assert "total_relationships" in stats
        assert "events_processed" in stats


class TestBusinessRules:
    """Test business-specific rules."""

    def test_create_business_rules(self):
        """Test business rule creation."""
        rules = create_business_rules()

        assert len(rules) > 0
        assert all(isinstance(rule, CausalRule) for rule in rules)

        # Check for key rules
        rule_names = [rule.name for rule in rules]
        assert "price_reduction_increases_demand" in rule_names
        assert "competitor_price_cut_forces_response" in rule_names
        assert "quality_issue_causes_complaints" in rule_names


class TestBusinessScenarios:
    """Test business scenario generation."""

    def test_competitive_market_scenario(self):
        """Test competitive market scenario generation."""
        generator = BusinessScenarioGenerator()
        events = generator.generate_competitive_market_scenario()

        assert len(events) > 0
        assert any(e.event_type == EventType.COMPETITOR_ACTION for e in events)
        assert any(e.event_type == EventType.PRICE_CHANGE for e in events)
        assert any(e.event_type == EventType.DEMAND_CHANGE for e in events)

    def test_supply_chain_crisis_scenario(self):
        """Test supply chain crisis scenario."""
        generator = BusinessScenarioGenerator()
        events = generator.generate_supply_chain_crisis_scenario()

        assert len(events) > 0
        assert any(e.event_type == EventType.SUPPLY_CHAIN_DISRUPTION for e in events)
        assert any(e.event_type == EventType.INVENTORY_CHANGE for e in events)

    def test_product_launch_scenario(self):
        """Test product launch scenario."""
        generator = BusinessScenarioGenerator()
        events = generator.generate_product_launch_scenario()

        assert len(events) > 0
        assert any(e.event_type == EventType.PRODUCT_LAUNCH for e in events)
        assert any(e.event_type == EventType.MARKETING_CAMPAIGN for e in events)

    def test_scenario_integration(self):
        """Test full scenario with correlation engine."""
        engine = CorrelationEngine(
            time_window_minutes=10080,
            auto_discover=True,
        )

        # Load rules
        rules = create_business_rules()
        for rule in rules:
            engine.add_rule(rule)

        # Generate and process scenario
        generator = BusinessScenarioGenerator()
        events = generator.generate_competitive_market_scenario()
        engine.add_events(events)

        # Verify processing
        assert len(engine.events) == len(events)
        assert len(engine.relationships) > 0

        # Verify relationships were discovered
        stats = engine.get_statistics()
        assert stats["total_events"] > 0
        assert stats["total_relationships"] > 0


class TestPatternDetection:
    """Test pattern detection functionality."""

    def test_sequence_detection(self):
        """Test sequence pattern detection."""
        from src.correlation.patterns import PatternDetector

        detector = PatternDetector()

        # Create sequential events
        events = []
        base_time = datetime(2025, 1, 1, 10, 0)

        for i in range(3):
            for j in range(3):
                events.append(
                    Event(
                        timestamp=base_time + timedelta(hours=i * 2 + j * 0.5),
                        event_type=[
                            EventType.PRICE_CHANGE,
                            EventType.DEMAND_CHANGE,
                            EventType.PURCHASE,
                        ][j],
                        title=f"Event {i}-{j}",
                        description="Test",
                        context=EventContext(domain="test", source="test"),
                    )
                )

        patterns = detector.detect_sequences(events, max_sequence_length=3)

        assert len(patterns) > 0

    def test_co_occurrence_detection(self):
        """Test co-occurrence pattern detection."""
        from src.correlation.patterns import PatternDetector

        detector = PatternDetector()

        # Create co-occurring events
        events = []
        base_time = datetime(2025, 1, 1, 10, 0)

        for i in range(5):
            # Price change and demand change occur together
            events.append(
                Event(
                    timestamp=base_time + timedelta(hours=i * 2),
                    event_type=EventType.PRICE_CHANGE,
                    title=f"Price {i}",
                    description="Test",
                    context=EventContext(domain="test", source="test"),
                )
            )
            events.append(
                Event(
                    timestamp=base_time + timedelta(hours=i * 2, minutes=10),
                    event_type=EventType.DEMAND_CHANGE,
                    title=f"Demand {i}",
                    description="Test",
                    context=EventContext(domain="test", source="test"),
                )
            )

        patterns = detector.detect_co_occurrences(events, time_window_minutes=60)

        assert len(patterns) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
