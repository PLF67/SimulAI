# API Reference

Complete API reference for the SimulAI Event Correlation Engine.

## Core Classes

### Event

Represents a discrete business event with rich metadata.

```python
from src.events.models import Event, EventType, EventSeverity, EventContext

event = Event(
    timestamp=datetime.now(),        # When event occurred
    event_type=EventType.PRICE_CHANGE,  # Type of event
    severity=EventSeverity.HIGH,     # Impact level
    title="Price reduced",           # Short title
    description="Detailed description",  # Full description
    context=EventContext(...),       # Contextual metadata
    magnitude=0.15,                  # Quantitative impact
    confidence=1.0,                  # Confidence in occurrence (0-1)
    attributes={...}                 # Custom attributes
)
```

#### Key Methods

- `add_cause(event_id)`: Add a causing event
- `add_effect(event_id)`: Add an effect event
- `matches_pattern(pattern)`: Check if event matches a pattern
- `time_since(other_event)`: Calculate time difference in minutes

### EventContext

Contextual information about an event.

```python
context = EventContext(
    domain="sales",                  # Business domain
    source="sales_system",           # Source system
    location="North Region",         # Geographic location (optional)
    department="sales",              # Department involved (optional)
    stakeholders=["sales", "ops"],   # Affected stakeholders
    tags={"urgent", "customer"}      # Searchable tags
)
```

### CausalRelationship

Represents a causal relationship between two events.

```python
from src.events.relationships import CausalRelationship, CausalityType, RelationshipStrength

relationship = CausalRelationship(
    cause_event_id="evt-001",
    effect_event_id="evt-002",
    causality_type=CausalityType.DIRECT,
    strength=RelationshipStrength.STRONG,
    confidence_score=0.85,
    time_lag_minutes=30.0,
    conditions={...},                # Conditional factors
    impact_magnitude=0.15,           # Quantitative impact
    impact_direction=1,              # 1 (positive), -1 (negative), 0 (neutral)
)
```

#### Key Methods

- `is_significant(min_confidence)`: Check if relationship is statistically significant
- `get_causal_weight()`: Get composite weight combining strength and confidence

### CorrelationEngine

Main engine for event correlation and causal analysis.

```python
from src.correlation.engine import CorrelationEngine

engine = CorrelationEngine(
    time_window_minutes=1440,    # Time window for relationships (24 hours)
    min_confidence=0.5,          # Minimum confidence threshold
    auto_discover=True           # Automatically discover relationships
)
```

#### Key Methods

##### Event Management

```python
# Add single event
engine.add_event(event)

# Add multiple events
engine.add_events([event1, event2, event3])

# Get event by ID
event = engine.events[event_id]
```

##### Rule Management

```python
# Add causal rule
engine.add_rule(causal_rule)

# Access rule library
rules = engine.rule_library.rules
```

##### Relationship Discovery

```python
# Get causes of an event
causes = engine.get_causes(event_id)
# Returns: List[(Event, CausalRelationship)]

# Get effects of an event
effects = engine.get_effects(event_id)
# Returns: List[(Event, CausalRelationship)]

# Get full causal chain
chain = engine.get_causal_chain(
    event_id,
    direction="forward",  # or "backward"
    max_depth=10
)
# Returns: List[Event]
```

##### Manual Relationships

```python
relationship = engine.add_manual_relationship(
    cause_event_id="evt-001",
    effect_event_id="evt-002",
    causality_type=CausalityType.DIRECT,
    strength=RelationshipStrength.STRONG,
    confidence=0.8,
    notes="Custom business logic"
)
```

##### Pattern Detection

```python
# Detect all patterns
patterns = engine.detect_patterns()
# Returns: Dict[str, List[EventPattern]]
# Keys: "sequences", "co_occurrences", "cascades", "periodic"
```

##### Graph Building

```python
# Build NetworkX graph
graph = engine.build_event_graph()
# Returns: networkx.DiGraph or None
```

##### Statistics

```python
stats = engine.get_statistics()
# Returns: {
#   "events_processed": int,
#   "relationships_discovered": int,
#   "rules_applied": int,
#   "patterns_detected": int,
#   "total_events": int,
#   "total_relationships": int,
#   "rules_loaded": int,
#   "event_types": int
# }
```

##### Utility

```python
# Clear all data
engine.clear()
```

### CausalRule

Defines a rule for identifying causal relationships.

```python
from src.correlation.rules import CausalRule

rule = CausalRule(
    name="price_affects_demand",
    description="Price changes affect demand",
    cause_pattern={                      # Pattern to match cause
        "event_type": EventType.PRICE_CHANGE
    },
    effect_pattern={                     # Pattern to match effect
        "event_type": EventType.DEMAND_CHANGE
    },
    causality_type=CausalityType.DIRECT,
    base_strength=RelationshipStrength.STRONG,
    base_confidence=0.85,
    min_time_lag_minutes=30,             # Minimum time between events
    max_time_lag_minutes=480,            # Maximum time between events
    condition_func=lambda cause, effect: (  # Optional condition
        cause.attributes.get("direction") == "decrease"
    ),
    impact_calculator=lambda cause, effect: (  # Optional impact calculator
        cause.attributes.get("price_change_pct", 0) * 1.5
    ),
    tags=["pricing", "demand"],
    priority=10                          # Higher = evaluated first
)
```

#### Key Methods

```python
# Check if event matches cause pattern
is_cause = rule.matches_cause(event)

# Check if event matches effect pattern
is_effect = rule.matches_effect(event)

# Check temporal constraints
is_valid = rule.is_temporal_match(cause_event, effect_event)

# Evaluate rule on event pair
result = rule.evaluate(cause_event, effect_event)
# Returns: Dict with relationship details or None
```

### CausalRuleLibrary

Collection of causal rules with efficient lookup.

```python
from src.correlation.rules import CausalRuleLibrary

library = CausalRuleLibrary()

# Add rules
library.add_rule(rule1)
library.add_rule(rule2)

# Get rules for specific events
rules_for_cause = library.get_rules_for_cause(event)
rules_for_effect = library.get_rules_for_effect(event)

# Find matching rules for event pair
matches = library.find_matching_rules(cause_event, effect_event)
# Returns: List[(CausalRule, Dict)]
```

### PatternDetector

Detects patterns in event streams.

```python
from src.correlation.patterns import PatternDetector

detector = PatternDetector(
    min_support=0.1,                 # Minimum frequency
    min_confidence=0.5,              # Minimum confidence
    max_time_window_minutes=1440     # Maximum time window
)
```

#### Key Methods

```python
# Detect sequential patterns
sequences = detector.detect_sequences(
    events,
    max_sequence_length=5
)

# Detect co-occurrences
co_occurrences = detector.detect_co_occurrences(
    events,
    time_window_minutes=60
)

# Detect cascades
cascades = detector.detect_cascades(
    events,
    min_cascade_length=3
)

# Detect periodic patterns
periodic = detector.find_periodic_patterns(
    events,
    tolerance_minutes=30
)

# Analyze all patterns
all_patterns = detector.analyze_all_patterns(events)
# Returns: Dict[str, List[EventPattern]]
```

### EventPattern

Represents a detected pattern.

```python
from src.correlation.patterns import EventPattern

pattern = EventPattern(
    pattern_id="seq_001",
    pattern_type="sequence",             # Type of pattern
    description="Price -> Demand -> Purchase",
    event_types=[...],                   # Event types involved
    event_sequence=[...],                # IDs in order (optional)
    typical_duration_minutes=120.0,      # Typical duration (optional)
    typical_intervals_minutes=[...],     # Intervals (optional)
    occurrence_count=5,                  # How many times observed
    confidence=0.8,                      # Confidence score
    support=0.2,                         # Frequency in dataset
    first_seen=datetime(...),            # First occurrence (optional)
    last_seen=datetime(...),             # Last occurrence (optional)
)
```

### CorrelationAnalyzer

Provides analysis and insights on correlations.

```python
from src.correlation.analysis import CorrelationAnalyzer

analyzer = CorrelationAnalyzer(engine)
```

#### Key Methods

```python
# Most influential events (caused most other events)
influential = analyzer.get_most_influential_events(top_n=10)
# Returns: List[(Event, effect_count)]

# Most affected events (caused by most other events)
affected = analyzer.get_most_affected_events(top_n=10)
# Returns: List[(Event, cause_count)]

# Causality type distribution
causality_dist = analyzer.get_causality_type_distribution()
# Returns: Dict[CausalityType, int]

# Event type interactions
interactions = analyzer.get_event_type_interactions()
# Returns: Dict[(EventType, EventType), int]

# Average relationship strength by causality type
avg_strengths = analyzer.get_average_relationship_strength()
# Returns: Dict[str, float]

# Temporal distribution
temporal_dist = analyzer.get_temporal_distribution(bucket_minutes=60)
# Returns: Dict[str, int]

# Severity impact analysis
severity_impact = analyzer.get_severity_impact_analysis()
# Returns: Dict[EventSeverity, Dict[str, float]]

# Find critical paths
paths = analyzer.find_critical_paths(min_length=3)
# Returns: List[List[Event]]

# Generate comprehensive report
report = analyzer.generate_summary_report()
# Returns: str (formatted report)
```

### BusinessScenarioGenerator

Generates realistic business scenarios.

```python
from src.business.scenarios import BusinessScenarioGenerator

generator = BusinessScenarioGenerator(start_time=datetime.now())
```

#### Key Methods

```python
# Generate competitive market scenario
events = generator.generate_competitive_market_scenario()

# Generate supply chain crisis
events = generator.generate_supply_chain_crisis_scenario()

# Generate product launch
events = generator.generate_product_launch_scenario()

# Generate all scenarios
all_scenarios = generator.generate_all_scenarios()
# Returns: Dict[str, List[Event]]
```

## Enums

### EventType

```python
class EventType(str, Enum):
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
```

### EventSeverity

```python
class EventSeverity(str, Enum):
    CRITICAL = "critical"      # Major impact
    HIGH = "high"              # Significant impact
    MEDIUM = "medium"          # Moderate impact
    LOW = "low"                # Minor impact
    NEGLIGIBLE = "negligible"  # Minimal impact
```

### CausalityType

```python
class CausalityType(str, Enum):
    DIRECT = "direct"              # A directly causes B
    INDIRECT = "indirect"          # A causes B through intermediaries
    CONTRIBUTORY = "contributory"  # A contributes to B
    CONDITIONAL = "conditional"    # A causes B under conditions
    PROBABILISTIC = "probabilistic"  # A increases P(B)
    PREVENTIVE = "preventive"      # A prevents B
    CATALYTIC = "catalytic"        # A accelerates B
    SUPPRESSIVE = "suppressive"    # A reduces B
    CORRELATIONAL = "correlational"  # A and B correlate
```

### RelationshipStrength

```python
class RelationshipStrength(str, Enum):
    VERY_STRONG = "very_strong"    # 0.8-1.0
    STRONG = "strong"              # 0.6-0.8
    MODERATE = "moderate"          # 0.4-0.6
    WEAK = "weak"                  # 0.2-0.4
    VERY_WEAK = "very_weak"        # 0.0-0.2

    @classmethod
    def from_score(cls, score: float) -> "RelationshipStrength":
        """Convert numeric score to strength category."""
```

## Utility Functions

### Business Rules

```python
from src.business.rules import create_business_rules

# Get all pre-configured business rules
rules = create_business_rules()
# Returns: List[CausalRule]
```

## Examples

See `examples/demo.py` for comprehensive usage examples covering:
- Competitive market scenarios
- Supply chain crisis management
- Product launches
- Pattern detection
- Analysis and reporting
