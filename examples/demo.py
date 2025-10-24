"""
Demonstration of the Event Correlation Engine.

This script demonstrates the key features of the correlation engine
using realistic business scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.correlation.engine import CorrelationEngine
from src.correlation.analysis import CorrelationAnalyzer
from src.business.rules import create_business_rules
from src.business.scenarios import BusinessScenarioGenerator


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_event_summary(events: list) -> None:
    """Print a summary of events."""
    print(f"\nGenerated {len(events)} events:")
    for i, event in enumerate(events[:10], 1):  # Show first 10
        print(f"  {i}. [{event.timestamp.strftime('%Y-%m-%d %H:%M')}] "
              f"{event.event_type.value}: {event.title}")
    if len(events) > 10:
        print(f"  ... and {len(events) - 10} more")


def demo_competitive_market_scenario():
    """Demonstrate competitive market scenario."""
    print_section("DEMO 1: Competitive Market Scenario")

    # Initialize engine
    engine = CorrelationEngine(
        time_window_minutes=10080,  # 1 week
        min_confidence=0.5,
        auto_discover=True
    )

    # Load business rules
    print("\nLoading business causal rules...")
    rules = create_business_rules()
    for rule in rules:
        engine.add_rule(rule)
    print(f"✓ Loaded {len(rules)} causal rules")

    # Generate scenario
    print("\nGenerating competitive market scenario...")
    generator = BusinessScenarioGenerator()
    events = generator.generate_competitive_market_scenario()
    print_event_summary(events)

    # Process events
    print("\nProcessing events and discovering relationships...")
    engine.add_events(events)

    # Show statistics
    stats = engine.get_statistics()
    print(f"\n✓ Processed {stats['total_events']} events")
    print(f"✓ Discovered {stats['total_relationships']} causal relationships")
    print(f"✓ Applied {stats['rules_applied']} rules")

    # Analyze causal chains
    print("\n" + "-" * 70)
    print("Causal Chain Analysis")
    print("-" * 70)

    # Find the initial competitor action
    initial_event = events[0]
    print(f"\nStarting from: {initial_event.title}")

    # Get effects chain
    effects = engine.get_effects(initial_event.id)
    if effects:
        print("\nDirect effects of competitor action:")
        for effect_event, relationship in effects:
            print(f"  → {effect_event.title}")
            print(f"     Type: {relationship.causality_type.value}")
            print(f"     Confidence: {relationship.confidence_score:.2f}")
            print(f"     Time lag: {relationship.time_lag_minutes:.0f} minutes")

    # Show full causal chain
    print("\nFull causal chain (forward):")
    chain = engine.get_causal_chain(initial_event.id, direction="forward", max_depth=10)
    for i, event in enumerate(chain, 1):
        indent = "  " * (i - 1)
        print(f"{indent}{i}. {event.title}")

    # Pattern detection
    print("\n" + "-" * 70)
    print("Pattern Detection")
    print("-" * 70)
    patterns = engine.detect_patterns()
    for pattern_type, pattern_list in patterns.items():
        if pattern_list:
            print(f"\n{pattern_type.upper()} ({len(pattern_list)} found):")
            for pattern in pattern_list[:3]:  # Show first 3
                print(f"  • {pattern.description}")
                print(f"    Occurrences: {pattern.occurrence_count}, "
                      f"Confidence: {pattern.confidence:.2f}")


def demo_supply_chain_crisis():
    """Demonstrate supply chain crisis scenario."""
    print_section("DEMO 2: Supply Chain Crisis Scenario")

    # Initialize engine
    engine = CorrelationEngine(
        time_window_minutes=20160,  # 2 weeks
        min_confidence=0.5,
        auto_discover=True
    )

    # Load rules
    print("\nLoading business causal rules...")
    rules = create_business_rules()
    for rule in rules:
        engine.add_rule(rule)
    print(f"✓ Loaded {len(rules)} causal rules")

    # Generate scenario
    print("\nGenerating supply chain crisis scenario...")
    generator = BusinessScenarioGenerator()
    events = generator.generate_supply_chain_crisis_scenario()
    print_event_summary(events)

    # Process events
    print("\nProcessing events...")
    engine.add_events(events)

    stats = engine.get_statistics()
    print(f"\n✓ Processed {stats['total_events']} events")
    print(f"✓ Discovered {stats['total_relationships']} causal relationships")

    # Analysis
    print("\n" + "-" * 70)
    print("Correlation Analysis")
    print("-" * 70)

    analyzer = CorrelationAnalyzer(engine)

    # Most influential events
    print("\nMost Influential Events:")
    influential = analyzer.get_most_influential_events(5)
    for event, effect_count in influential:
        print(f"  • {event.title}")
        print(f"    Severity: {event.severity.value}, Effects: {effect_count}")

    # Causality type distribution
    print("\nCausality Type Distribution:")
    causality_dist = analyzer.get_causality_type_distribution()
    for causality_type, count in causality_dist.items():
        print(f"  {causality_type.value}: {count}")

    # Event type interactions
    print("\nEvent Type Interactions:")
    interactions = analyzer.get_event_type_interactions()
    for (cause_type, effect_type), count in list(interactions.items())[:5]:
        print(f"  {cause_type.value} → {effect_type.value}: {count}")


def demo_product_launch():
    """Demonstrate product launch scenario."""
    print_section("DEMO 3: Product Launch Scenario")

    # Initialize engine
    engine = CorrelationEngine(
        time_window_minutes=43200,  # 30 days
        min_confidence=0.4,
        auto_discover=True
    )

    # Load rules
    print("\nLoading business causal rules...")
    rules = create_business_rules()
    for rule in rules:
        engine.add_rule(rule)
    print(f"✓ Loaded {len(rules)} causal rules")

    # Generate scenario
    print("\nGenerating product launch scenario...")
    generator = BusinessScenarioGenerator()
    events = generator.generate_product_launch_scenario()
    print_event_summary(events)

    # Process events
    print("\nProcessing events...")
    engine.add_events(events)

    stats = engine.get_statistics()
    print(f"\n✓ Processed {stats['total_events']} events")
    print(f"✓ Discovered {stats['total_relationships']} causal relationships")

    # Generate comprehensive report
    print("\n")
    analyzer = CorrelationAnalyzer(engine)
    report = analyzer.generate_summary_report()
    print(report)

    # Critical paths
    print("\n" + "-" * 70)
    print("Critical Causal Paths")
    print("-" * 70)

    paths = analyzer.find_critical_paths(min_length=3)
    if paths:
        print(f"\nFound {len(paths)} causal paths:")
        for i, path in enumerate(paths[:3], 1):  # Show top 3
            print(f"\nPath {i} ({len(path)} events):")
            for j, event in enumerate(path, 1):
                print(f"  {j}. {event.title}")


def demo_pattern_detection():
    """Demonstrate pattern detection across scenarios."""
    print_section("DEMO 4: Pattern Detection Across Scenarios")

    # Initialize engine
    engine = CorrelationEngine(
        time_window_minutes=43200,  # 30 days
        min_confidence=0.3,
        auto_discover=True
    )

    # Load rules
    rules = create_business_rules()
    for rule in rules:
        engine.add_rule(rule)

    # Generate all scenarios
    print("\nGenerating multiple scenarios...")
    generator = BusinessScenarioGenerator()
    all_scenarios = generator.generate_all_scenarios()

    # Process all events
    total_events = 0
    for scenario_name, events in all_scenarios.items():
        print(f"  • {scenario_name}: {len(events)} events")
        engine.add_events(events)
        total_events += len(events)

    print(f"\n✓ Total events processed: {total_events}")

    # Detect patterns
    print("\n" + "-" * 70)
    print("Pattern Detection Results")
    print("-" * 70)

    patterns = engine.detect_patterns()

    for pattern_type, pattern_list in patterns.items():
        print(f"\n{pattern_type.upper()}: {len(pattern_list)} patterns")
        for pattern in pattern_list:
            print(f"\n  {pattern.description}")
            print(f"    Events: {[et.value for et in pattern.event_types]}")
            print(f"    Occurrences: {pattern.occurrence_count}")
            print(f"    Confidence: {pattern.confidence:.2f}")
            if pattern.typical_duration_minutes:
                print(f"    Typical duration: {pattern.typical_duration_minutes:.0f} minutes")

    # Final statistics
    stats = engine.get_statistics()
    print("\n" + "=" * 70)
    print("Overall Statistics")
    print("=" * 70)
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "    SimulAI Event Correlation Engine - Demonstration".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        # Run demos
        demo_competitive_market_scenario()
        input("\n\nPress Enter to continue to next demo...")

        demo_supply_chain_crisis()
        input("\n\nPress Enter to continue to next demo...")

        demo_product_launch()
        input("\n\nPress Enter to continue to next demo...")

        demo_pattern_detection()

        print("\n" + "=" * 70)
        print("  Demonstration Complete!")
        print("=" * 70)
        print("\nThank you for exploring the SimulAI Event Correlation Engine.")
        print("For more information, see the documentation in docs/README.md\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
