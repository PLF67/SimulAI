# SimulAI - Event Correlation Engine

A sophisticated event correlation engine with realistic causal relationships for business simulation games.

## Overview

SimulAI provides a powerful framework for modeling and analyzing complex causal relationships between business events. The engine automatically discovers relationships, detects patterns, and provides deep insights into how events influence each other in realistic business scenarios.

### Key Features

- **Rich Event Model**: Comprehensive event representation with metadata, temporal information, and context
- **Multiple Causality Types**: Direct, indirect, conditional, probabilistic, and more
- **Automatic Relationship Discovery**: Rule-based system automatically identifies causal relationships
- **Pattern Detection**: Identifies sequences, co-occurrences, cascades, and periodic patterns
- **Business Domain Models**: Pre-configured rules for realistic business scenarios
- **Graph-Based Analysis**: Network representation of event relationships
- **Confidence Scoring**: Probabilistic relationship strength assessment

## Architecture

### Core Components

1. **Event Models** (`src/events/`)
   - `Event`: Rich event representation with temporal and contextual data
   - `EventType`: Comprehensive event taxonomy (30+ business event types)
   - `EventContext`: Contextual metadata for events
   - `CausalRelationship`: Models causality between events

2. **Correlation Engine** (`src/correlation/`)
   - `CorrelationEngine`: Main engine for processing events and discovering relationships
   - `CausalRule`: Rule definitions for identifying causal patterns
   - `PatternDetector`: Detects temporal patterns and sequences
   - `CorrelationAnalyzer`: Statistical analysis and insights

3. **Business Domain** (`src/business/`)
   - Pre-configured causal rules for business scenarios
   - Scenario generators for common business situations
   - Realistic event chains and cascades

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd SimulAI

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.correlation.engine import CorrelationEngine
from src.events.models import Event, EventType, EventContext
from src.business.rules import create_business_rules

# Initialize engine
engine = CorrelationEngine(
    time_window_minutes=1440,  # 24 hours
    min_confidence=0.5,
    auto_discover=True
)

# Load business rules
rules = create_business_rules()
for rule in rules:
    engine.add_rule(rule)

# Add events
event1 = Event(
    event_type=EventType.PRICE_CHANGE,
    severity=EventSeverity.HIGH,
    title="Price reduced by 15%",
    description="Strategic price reduction to match competitor",
    context=EventContext(
        domain="pricing",
        source="pricing_system",
        department="sales",
        tags={"pricing", "competition"}
    ),
    attributes={"direction": "decrease", "price_change_pct": -15}
)

engine.add_event(event1)

# Engine automatically discovers relationships with other events
# Get causal effects
effects = engine.get_effects(event1.id)
for effect_event, relationship in effects:
    print(f"{event1.title} -> {effect_event.title}")
    print(f"  Type: {relationship.causality_type.value}")
    print(f"  Confidence: {relationship.confidence_score:.2f}")
```

### Using Pre-built Scenarios

```python
from src.business.scenarios import BusinessScenarioGenerator

# Generate realistic business scenario
generator = BusinessScenarioGenerator()
events = generator.generate_competitive_market_scenario()

# Process with engine
engine.add_events(events)

# Analyze results
stats = engine.get_statistics()
print(f"Discovered {stats['total_relationships']} causal relationships")
```

### Running the Demo

```bash
python examples/demo.py
```

The demo showcases:
- Competitive market scenario with competitor actions and responses
- Supply chain crisis with cascading operational impacts
- Product launch with marketing and demand generation
- Pattern detection across multiple scenarios

## Event Types

The engine supports 30+ event types across categories:

- **Market Events**: market_shift, demand_change, supply_change, price_change, competitor_action
- **Customer Events**: customer_acquisition, customer_churn, customer_complaint, purchase
- **Operational Events**: production_change, inventory_change, quality_issue, supply_chain_disruption
- **Financial Events**: revenue_change, cost_change, investment, cash_flow_change
- **Strategic Events**: product_launch, marketing_campaign, partnership, expansion
- **External Events**: regulatory_change, economic_shift, technological_change, natural_disaster

## Causality Types

The engine models various types of causal relationships:

- **Direct**: A directly causes B with high certainty
- **Indirect**: A causes B through intermediary events
- **Contributory**: A contributes to B but doesn't fully cause it
- **Conditional**: A causes B only under certain conditions
- **Probabilistic**: A increases probability of B occurring
- **Preventive**: A prevents B from occurring
- **Catalytic**: A accelerates or amplifies B
- **Suppressive**: A reduces the likelihood or impact of B
- **Correlational**: A and B occur together (causality unclear)

## Pattern Detection

The engine automatically detects:

- **Sequences**: Common event sequences (A → B → C)
- **Co-occurrences**: Events that frequently occur together
- **Cascades**: One event triggering chains of events
- **Periodic Patterns**: Events recurring at regular intervals

## Business Rules

The engine includes 30+ pre-configured business rules:

### Pricing and Demand
- Price reductions increase demand
- Price increases decrease demand (elastic goods)
- Competitor actions force price responses

### Customer Behavior
- Demand increases drive purchases
- Complaints can lead to churn
- Quality issues trigger complaints
- Marketing campaigns drive acquisition

### Operations
- Demand spikes cause inventory shortages
- Supply disruptions reduce inventory
- Low inventory triggers production increases
- Production increases raise costs

### Financial
- Purchases increase revenue
- Cost increases reduce cash flow
- Investments enable expansion

### Strategic
- Product launches drive marketing campaigns
- Partnerships enable market expansion
- Regulatory changes force restructuring

## Analysis and Insights

```python
from src.correlation.analysis import CorrelationAnalyzer

analyzer = CorrelationAnalyzer(engine)

# Find most influential events
influential = analyzer.get_most_influential_events(top_n=10)

# Analyze causality type distribution
causality_dist = analyzer.get_causality_type_distribution()

# Find critical causal paths
paths = analyzer.find_critical_paths(min_length=3)

# Generate comprehensive report
report = analyzer.generate_summary_report()
print(report)
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Project Structure

```
SimulAI/
├── src/
│   ├── events/               # Event models and relationships
│   │   ├── models.py         # Event, EventType, EventContext
│   │   └── relationships.py  # CausalRelationship, CausalityType
│   ├── correlation/          # Correlation engine
│   │   ├── engine.py         # Main CorrelationEngine
│   │   ├── rules.py          # CausalRule, CausalRuleLibrary
│   │   ├── patterns.py       # PatternDetector
│   │   └── analysis.py       # CorrelationAnalyzer
│   └── business/             # Business domain models
│       ├── rules.py          # Business causal rules
│       └── scenarios.py      # Scenario generators
├── examples/
│   └── demo.py               # Comprehensive demonstration
├── tests/
│   └── test_correlation_engine.py
├── requirements.txt
└── README.md
```

## Advanced Features

### Custom Rules

Define your own causal rules:

```python
from src.correlation.rules import CausalRule
from src.events.relationships import CausalityType, RelationshipStrength

custom_rule = CausalRule(
    name="my_custom_rule",
    description="Custom business logic",
    cause_pattern={"event_type": EventType.MARKETING_CAMPAIGN},
    effect_pattern={"event_type": EventType.CUSTOMER_ACQUISITION},
    causality_type=CausalityType.DIRECT,
    base_strength=RelationshipStrength.STRONG,
    base_confidence=0.75,
    min_time_lag_minutes=60,
    max_time_lag_minutes=4320,
    condition_func=lambda cause, effect: (
        cause.attributes.get("budget", 0) > 50000
    ),
    priority=8
)

engine.add_rule(custom_rule)
```

### Graph Analysis

```python
# Build NetworkX graph
graph = engine.build_event_graph()

# Use NetworkX algorithms
import networkx as nx
centrality = nx.betweenness_centrality(graph)
communities = nx.community.greedy_modularity_communities(graph)
```

### Manual Relationships

```python
# Manually specify relationships
engine.add_manual_relationship(
    cause_event_id=event1.id,
    effect_event_id=event2.id,
    causality_type=CausalityType.CONDITIONAL,
    strength=RelationshipStrength.MODERATE,
    confidence=0.7,
    notes="Special business logic"
)
```

## Use Cases

- **Business Simulation Games**: Model realistic business dynamics
- **Training Simulations**: Teach cause-and-effect in business decisions
- **Scenario Planning**: Explore outcomes of different strategies
- **Risk Analysis**: Identify potential cascading effects
- **Decision Support**: Understand implications of business actions

## Contributing

Contributions are welcome! Areas for enhancement:

- Additional event types and business domains
- Machine learning-based pattern detection
- Real-time event streaming
- Interactive visualization dashboard
- More sophisticated probabilistic models

## License

[Specify your license]

## Authors

Created as part of the SimulAI business simulation game project.

## Acknowledgments

Built with:
- Python 3.x
- Pydantic for data validation
- NetworkX for graph analysis
- NumPy and Pandas for statistical analysis
