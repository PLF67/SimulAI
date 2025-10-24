"""Seed initial data for the game"""
import json

# Initial stock data
INITIAL_STOCKS = [
    # AI Sector
    {"ticker": "AICORE", "company_name": "AI Core Technologies", "sector": "AI", "subsector": "Machine Learning", "initial_price": 150.0, "volatility": 0.25, "description": "Leading AI chip manufacturer"},
    {"ticker": "NEUNET", "company_name": "NeuralNet Systems", "sector": "AI", "subsector": "Deep Learning", "initial_price": 85.0, "volatility": 0.30, "description": "Advanced neural network platforms"},
    {"ticker": "COGAI", "company_name": "Cognitive AI Solutions", "sector": "AI", "subsector": "NLP", "initial_price": 120.0, "volatility": 0.28, "description": "Natural language processing leader"},

    # Quantum Computing
    {"ticker": "QBIT", "company_name": "Quantum Bit Corp", "sector": "Quantum", "subsector": "Quantum Hardware", "initial_price": 200.0, "volatility": 0.35, "description": "Quantum computer manufacturer"},
    {"ticker": "QSEC", "company_name": "Quantum Security", "sector": "Quantum", "subsector": "Quantum Cryptography", "initial_price": 95.0, "volatility": 0.32, "description": "Quantum encryption solutions"},
    {"ticker": "QSIM", "company_name": "Quantum Simulations Ltd", "sector": "Quantum", "subsector": "Quantum Software", "initial_price": 110.0, "volatility": 0.30, "description": "Quantum simulation software"},

    # Finance
    {"ticker": "FINTEK", "company_name": "FinTech Global", "sector": "Finance", "subsector": "Digital Banking", "initial_price": 75.0, "volatility": 0.18, "description": "Digital banking platform"},
    {"ticker": "BLKCH", "company_name": "Blockchain Finance", "sector": "Finance", "subsector": "Blockchain", "initial_price": 65.0, "volatility": 0.40, "description": "Blockchain financial services"},
    {"ticker": "PAYPRO", "company_name": "PaymentPro Inc", "sector": "Finance", "subsector": "Payments", "initial_price": 90.0, "volatility": 0.20, "description": "Global payment processing"},

    # Pharmaceuticals
    {"ticker": "BIOTECH", "company_name": "BioTech Innovations", "sector": "Pharma", "subsector": "Biotech", "initial_price": 180.0, "volatility": 0.22, "description": "Biotechnology research and development"},
    {"ticker": "GENEDIT", "company_name": "Gene Editors Corp", "sector": "Pharma", "subsector": "Gene Therapy", "initial_price": 140.0, "volatility": 0.28, "description": "CRISPR gene editing technology"},
    {"ticker": "VAXX", "company_name": "VaxGen Pharma", "sector": "Pharma", "subsector": "Vaccines", "initial_price": 105.0, "volatility": 0.20, "description": "Vaccine development and manufacturing"},

    # Energy
    {"ticker": "SOLAR", "company_name": "Solar Power Systems", "sector": "Energy", "subsector": "Renewable", "initial_price": 70.0, "volatility": 0.25, "description": "Solar energy solutions"},
    {"ticker": "FUSION", "company_name": "Fusion Energy Ltd", "sector": "Energy", "subsector": "Nuclear Fusion", "initial_price": 130.0, "volatility": 0.35, "description": "Nuclear fusion research"},
    {"ticker": "BATT", "company_name": "Battery Tech Corp", "sector": "Energy", "subsector": "Energy Storage", "initial_price": 95.0, "volatility": 0.22, "description": "Advanced battery technology"},

    # Telecommunications
    {"ticker": "5GNET", "company_name": "5G Networks Global", "sector": "Telecom", "subsector": "5G", "initial_price": 80.0, "volatility": 0.20, "description": "5G network infrastructure"},
    {"ticker": "SATCOM", "company_name": "Satellite Communications", "sector": "Telecom", "subsector": "Satellite", "initial_price": 115.0, "volatility": 0.24, "description": "Satellite internet services"},

    # Robotics
    {"ticker": "ROBO", "company_name": "Robotics Industries", "sector": "Robotics", "subsector": "Industrial", "initial_price": 125.0, "volatility": 0.26, "description": "Industrial automation robots"},
    {"ticker": "AUTOCAR", "company_name": "Autonomous Vehicles Inc", "sector": "Robotics", "subsector": "Autonomous Vehicles", "initial_price": 145.0, "volatility": 0.30, "description": "Self-driving car technology"},
]

# Event templates with causality
EVENT_TEMPLATES = [
    {
        "title": "Major AI Breakthrough in Natural Language Understanding",
        "description": "Researchers announce a revolutionary AI model that achieves human-level language comprehension.",
        "event_type": "breakthrough",
        "affected_sectors": ["AI", "Telecom", "Finance"],
        "impact_multipliers": {"AI": 1.15, "Telecom": 1.05, "Finance": 1.03},
        "causality_tags": ["AI", "technology", "automation"],
        "probability": 0.3
    },
    {
        "title": "New AI Regulation Framework Announced",
        "description": "Governments introduce strict regulations on AI development and deployment.",
        "event_type": "regulation",
        "affected_sectors": ["AI", "Finance", "Pharma"],
        "impact_multipliers": {"AI": 0.85, "Finance": 0.95, "Pharma": 0.98},
        "causality_tags": ["AI", "regulation", "policy"],
        "probability": 0.4
    },
    {
        "title": "Quantum Computing Achieves Practical Supremacy",
        "description": "First quantum computer solves real-world problem faster than any classical computer.",
        "event_type": "breakthrough",
        "affected_sectors": ["Quantum", "AI", "Finance", "Pharma"],
        "impact_multipliers": {"Quantum": 1.25, "AI": 1.08, "Finance": 1.05, "Pharma": 1.06},
        "causality_tags": ["quantum", "computing", "cryptography"],
        "probability": 0.25
    },
    {
        "title": "Cybersecurity Crisis: Major Encryption Vulnerability",
        "description": "Critical vulnerability discovered in widely-used encryption protocols.",
        "event_type": "crisis",
        "affected_sectors": ["Finance", "Quantum", "Telecom"],
        "impact_multipliers": {"Finance": 0.80, "Quantum": 1.20, "Telecom": 0.90},
        "causality_tags": ["security", "cryptography", "crisis"],
        "probability": 0.2
    },
    {
        "title": "Breakthrough in Gene Therapy",
        "description": "New gene editing technique shows promise in curing genetic diseases.",
        "event_type": "breakthrough",
        "affected_sectors": ["Pharma", "AI"],
        "impact_multipliers": {"Pharma": 1.18, "AI": 1.04},
        "causality_tags": ["biotech", "medical", "innovation"],
        "probability": 0.35
    },
    {
        "title": "Global Pandemic Alert",
        "description": "New infectious disease outbreak raises concerns worldwide.",
        "event_type": "crisis",
        "affected_sectors": ["Pharma", "Telecom", "Finance"],
        "impact_multipliers": {"Pharma": 1.25, "Telecom": 1.10, "Finance": 0.85},
        "causality_tags": ["health", "crisis", "pandemic"],
        "probability": 0.15
    },
    {
        "title": "Renewable Energy Cost Breakthrough",
        "description": "Solar power becomes cheaper than fossil fuels across all markets.",
        "event_type": "breakthrough",
        "affected_sectors": ["Energy", "Finance"],
        "impact_multipliers": {"Energy": 1.20, "Finance": 1.05},
        "causality_tags": ["energy", "sustainability", "innovation"],
        "probability": 0.3
    },
    {
        "title": "Fusion Energy Milestone Achieved",
        "description": "First sustained net-positive fusion reaction achieved in laboratory.",
        "event_type": "breakthrough",
        "affected_sectors": ["Energy", "Quantum"],
        "impact_multipliers": {"Energy": 1.30, "Quantum": 1.08},
        "causality_tags": ["energy", "fusion", "innovation"],
        "probability": 0.2
    },
    {
        "title": "Global Economic Recession",
        "description": "Major economies enter recession, affecting global markets.",
        "event_type": "crisis",
        "affected_sectors": ["Finance", "Telecom", "Energy", "Robotics"],
        "impact_multipliers": {"Finance": 0.75, "Telecom": 0.90, "Energy": 0.85, "Robotics": 0.88},
        "causality_tags": ["economy", "crisis", "recession"],
        "probability": 0.25
    },
    {
        "title": "Autonomous Vehicle Approval",
        "description": "Regulators approve fully autonomous vehicles for public roads.",
        "event_type": "regulation",
        "affected_sectors": ["Robotics", "AI", "Telecom"],
        "impact_multipliers": {"Robotics": 1.20, "AI": 1.12, "Telecom": 1.08},
        "causality_tags": ["autonomous", "regulation", "transportation"],
        "probability": 0.3
    },
    {
        "title": "Satellite Internet Constellation Completed",
        "description": "Global satellite internet network provides worldwide coverage.",
        "event_type": "breakthrough",
        "affected_sectors": ["Telecom", "Robotics"],
        "impact_multipliers": {"Telecom": 1.15, "Robotics": 1.05},
        "causality_tags": ["telecom", "satellite", "connectivity"],
        "probability": 0.35
    },
    {
        "title": "Data Privacy Scandal",
        "description": "Major tech companies face scrutiny over data handling practices.",
        "event_type": "crisis",
        "affected_sectors": ["AI", "Telecom", "Finance"],
        "impact_multipliers": {"AI": 0.88, "Telecom": 0.85, "Finance": 0.92},
        "causality_tags": ["privacy", "regulation", "data"],
        "probability": 0.3
    },
    {
        "title": "Quantum Cryptography Standard Adopted",
        "description": "Industry adopts quantum-resistant encryption as new standard.",
        "event_type": "regulation",
        "affected_sectors": ["Quantum", "Finance", "Telecom"],
        "impact_multipliers": {"Quantum": 1.18, "Finance": 1.06, "Telecom": 1.04},
        "causality_tags": ["quantum", "security", "standard"],
        "probability": 0.25
    },
    {
        "title": "AI-Powered Drug Discovery Success",
        "description": "AI system discovers effective treatment for major disease.",
        "event_type": "breakthrough",
        "affected_sectors": ["AI", "Pharma"],
        "impact_multipliers": {"AI": 1.10, "Pharma": 1.15},
        "causality_tags": ["AI", "pharma", "medical"],
        "probability": 0.3
    },
    {
        "title": "Energy Storage Revolution",
        "description": "New battery technology increases capacity by 10x at lower cost.",
        "event_type": "breakthrough",
        "affected_sectors": ["Energy", "Robotics"],
        "impact_multipliers": {"Energy": 1.25, "Robotics": 1.10},
        "causality_tags": ["energy", "battery", "innovation"],
        "probability": 0.25
    }
]
