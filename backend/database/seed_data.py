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
    # === AI SECTOR EVENTS ===
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
        "title": "AI Chip Shortage Crisis",
        "description": "Global supply chain disruption causes severe shortage of AI processors, delaying projects worldwide.",
        "event_type": "crisis",
        "affected_sectors": ["AI", "Robotics", "Telecom"],
        "impact_multipliers": {"AI": 0.78, "Robotics": 0.82, "Telecom": 0.92},
        "causality_tags": ["AI", "supply-chain", "hardware"],
        "probability": 0.25
    },
    {
        "title": "AI Safety Incident Raises Concerns",
        "description": "High-profile AI system malfunction causes significant disruption, triggering calls for stricter oversight.",
        "event_type": "crisis",
        "affected_sectors": ["AI", "Finance", "Robotics"],
        "impact_multipliers": {"AI": 0.82, "Finance": 0.93, "Robotics": 0.88},
        "causality_tags": ["AI", "safety", "regulation"],
        "probability": 0.2
    },
    {
        "title": "Open-Source AI Model Disrupts Market",
        "description": "Powerful open-source AI model release threatens proprietary AI company business models.",
        "event_type": "breakthrough",
        "affected_sectors": ["AI"],
        "impact_multipliers": {"AI": 0.90},
        "causality_tags": ["AI", "competition", "disruption"],
        "probability": 0.35
    },
    {
        "title": "AI Ethics Board Established Globally",
        "description": "International consortium creates unified AI ethics standards, affecting development practices.",
        "event_type": "regulation",
        "affected_sectors": ["AI", "Pharma", "Finance"],
        "impact_multipliers": {"AI": 0.92, "Pharma": 0.96, "Finance": 0.97},
        "causality_tags": ["AI", "ethics", "regulation"],
        "probability": 0.3
    },

    # === QUANTUM COMPUTING EVENTS ===
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
        "title": "Quantum Cryptography Standard Adopted",
        "description": "Industry adopts quantum-resistant encryption as new standard.",
        "event_type": "regulation",
        "affected_sectors": ["Quantum", "Finance", "Telecom"],
        "impact_multipliers": {"Quantum": 1.18, "Finance": 1.06, "Telecom": 1.04},
        "causality_tags": ["quantum", "security", "standard"],
        "probability": 0.25
    },
    {
        "title": "Quantum Computing Setback: Stability Issues",
        "description": "Leading quantum computing labs report unexpected decoherence problems, delaying commercialization.",
        "event_type": "crisis",
        "affected_sectors": ["Quantum", "AI"],
        "impact_multipliers": {"Quantum": 0.75, "AI": 0.95},
        "causality_tags": ["quantum", "technology", "setback"],
        "probability": 0.3
    },
    {
        "title": "Quantum Computing Patent War Erupts",
        "description": "Major tech companies engage in legal battles over fundamental quantum computing patents.",
        "event_type": "crisis",
        "affected_sectors": ["Quantum"],
        "impact_multipliers": {"Quantum": 0.88},
        "causality_tags": ["quantum", "legal", "competition"],
        "probability": 0.25
    },
    {
        "title": "Room-Temperature Quantum Processor Demonstrated",
        "description": "Breakthrough eliminates need for expensive cooling systems, making quantum computing more accessible.",
        "event_type": "breakthrough",
        "affected_sectors": ["Quantum", "AI", "Finance"],
        "impact_multipliers": {"Quantum": 1.35, "AI": 1.12, "Finance": 1.08},
        "causality_tags": ["quantum", "breakthrough", "accessibility"],
        "probability": 0.15
    },

    # === CYBERSECURITY & PRIVACY EVENTS ===
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
        "title": "Data Privacy Scandal",
        "description": "Major tech companies face scrutiny over data handling practices.",
        "event_type": "crisis",
        "affected_sectors": ["AI", "Telecom", "Finance"],
        "impact_multipliers": {"AI": 0.88, "Telecom": 0.85, "Finance": 0.92},
        "causality_tags": ["privacy", "regulation", "data"],
        "probability": 0.3
    },
    {
        "title": "Global Ransomware Attack Wave",
        "description": "Coordinated ransomware attacks hit critical infrastructure, driving demand for security solutions.",
        "event_type": "crisis",
        "affected_sectors": ["Finance", "Telecom", "Energy"],
        "impact_multipliers": {"Finance": 0.85, "Telecom": 0.88, "Energy": 0.82},
        "causality_tags": ["security", "crisis", "cyber"],
        "probability": 0.25
    },
    {
        "title": "Zero-Day Exploit Market Crackdown",
        "description": "International law enforcement shuts down major vulnerability trading platforms.",
        "event_type": "regulation",
        "affected_sectors": ["AI", "Finance", "Telecom"],
        "impact_multipliers": {"AI": 1.05, "Finance": 1.08, "Telecom": 1.06},
        "causality_tags": ["security", "regulation", "enforcement"],
        "probability": 0.2
    },

    # === PHARMACEUTICAL & BIOTECH EVENTS ===
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
        "title": "AI-Powered Drug Discovery Success",
        "description": "AI system discovers effective treatment for major disease.",
        "event_type": "breakthrough",
        "affected_sectors": ["AI", "Pharma"],
        "impact_multipliers": {"AI": 1.10, "Pharma": 1.15},
        "causality_tags": ["AI", "pharma", "medical"],
        "probability": 0.3
    },
    {
        "title": "Clinical Trial Failure Rocks Biotech Sector",
        "description": "Multiple high-profile drug candidates fail Phase 3 trials, causing investor concern.",
        "event_type": "crisis",
        "affected_sectors": ["Pharma"],
        "impact_multipliers": {"Pharma": 0.75},
        "causality_tags": ["pharma", "setback", "trials"],
        "probability": 0.3
    },
    {
        "title": "Personalized Medicine Platform Approved",
        "description": "Regulatory approval for AI-driven personalized treatment platform transforms healthcare delivery.",
        "event_type": "breakthrough",
        "affected_sectors": ["Pharma", "AI"],
        "impact_multipliers": {"Pharma": 1.20, "AI": 1.12},
        "causality_tags": ["pharma", "AI", "personalization"],
        "probability": 0.25
    },
    {
        "title": "Drug Pricing Regulation Enacted",
        "description": "New legislation caps pharmaceutical prices, impacting industry profit margins.",
        "event_type": "regulation",
        "affected_sectors": ["Pharma"],
        "impact_multipliers": {"Pharma": 0.80},
        "causality_tags": ["pharma", "regulation", "pricing"],
        "probability": 0.35
    },
    {
        "title": "Longevity Drug Shows Promising Results",
        "description": "Clinical trials demonstrate significant life extension in humans, creating massive market potential.",
        "event_type": "breakthrough",
        "affected_sectors": ["Pharma"],
        "impact_multipliers": {"Pharma": 1.30},
        "causality_tags": ["pharma", "longevity", "breakthrough"],
        "probability": 0.15
    },

    # === ENERGY SECTOR EVENTS ===
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
        "title": "Energy Storage Revolution",
        "description": "New battery technology increases capacity by 10x at lower cost.",
        "event_type": "breakthrough",
        "affected_sectors": ["Energy", "Robotics"],
        "impact_multipliers": {"Energy": 1.25, "Robotics": 1.10},
        "causality_tags": ["energy", "battery", "innovation"],
        "probability": 0.25
    },
    {
        "title": "Grid Failure Exposes Infrastructure Weaknesses",
        "description": "Major power grid collapse highlights vulnerability of aging energy infrastructure.",
        "event_type": "crisis",
        "affected_sectors": ["Energy", "Telecom", "AI"],
        "impact_multipliers": {"Energy": 0.82, "Telecom": 0.90, "AI": 0.93},
        "causality_tags": ["energy", "infrastructure", "crisis"],
        "probability": 0.25
    },
    {
        "title": "Carbon Tax Implementation",
        "description": "Major economies implement aggressive carbon pricing, accelerating renewable energy adoption.",
        "event_type": "regulation",
        "affected_sectors": ["Energy"],
        "impact_multipliers": {"Energy": 1.15},
        "causality_tags": ["energy", "regulation", "climate"],
        "probability": 0.35
    },
    {
        "title": "Rare Earth Minerals Supply Crisis",
        "description": "Geopolitical tensions disrupt supply of critical minerals for batteries and renewable energy.",
        "event_type": "crisis",
        "affected_sectors": ["Energy", "Robotics", "Telecom"],
        "impact_multipliers": {"Energy": 0.75, "Robotics": 0.80, "Telecom": 0.88},
        "causality_tags": ["energy", "supply-chain", "geopolitical"],
        "probability": 0.3
    },
    {
        "title": "Wireless Power Transmission Breakthrough",
        "description": "Efficient long-range wireless power transmission becomes commercially viable.",
        "event_type": "breakthrough",
        "affected_sectors": ["Energy", "Telecom", "Robotics"],
        "impact_multipliers": {"Energy": 1.22, "Telecom": 1.15, "Robotics": 1.10},
        "causality_tags": ["energy", "wireless", "innovation"],
        "probability": 0.2
    },

    # === TELECOMMUNICATIONS EVENTS ===
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
        "title": "6G Technology Standard Finalized",
        "description": "Next-generation wireless technology promises 100x faster speeds and near-zero latency.",
        "event_type": "breakthrough",
        "affected_sectors": ["Telecom", "AI", "Robotics"],
        "impact_multipliers": {"Telecom": 1.20, "AI": 1.08, "Robotics": 1.10},
        "causality_tags": ["telecom", "wireless", "standard"],
        "probability": 0.3
    },
    {
        "title": "Undersea Cable Damage Disrupts Global Internet",
        "description": "Multiple submarine cable cuts cause widespread internet outages and connectivity issues.",
        "event_type": "crisis",
        "affected_sectors": ["Telecom", "Finance", "AI"],
        "impact_multipliers": {"Telecom": 0.85, "Finance": 0.90, "AI": 0.92},
        "causality_tags": ["telecom", "infrastructure", "crisis"],
        "probability": 0.2
    },
    {
        "title": "Net Neutrality Regulations Overturned",
        "description": "New regulations allow ISPs to prioritize traffic, creating market opportunities and concerns.",
        "event_type": "regulation",
        "affected_sectors": ["Telecom", "Finance"],
        "impact_multipliers": {"Telecom": 1.12, "Finance": 1.04},
        "causality_tags": ["telecom", "regulation", "policy"],
        "probability": 0.25
    },
    {
        "title": "Quantum Internet Test Network Operational",
        "description": "First quantum communication network demonstrates unhackable data transmission.",
        "event_type": "breakthrough",
        "affected_sectors": ["Telecom", "Quantum", "Finance"],
        "impact_multipliers": {"Telecom": 1.18, "Quantum": 1.22, "Finance": 1.10},
        "causality_tags": ["telecom", "quantum", "security"],
        "probability": 0.2
    },

    # === ROBOTICS & AUTOMATION EVENTS ===
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
        "title": "Humanoid Robot Mass Production Begins",
        "description": "First general-purpose humanoid robots enter mass production for service industries.",
        "event_type": "breakthrough",
        "affected_sectors": ["Robotics", "AI"],
        "impact_multipliers": {"Robotics": 1.25, "AI": 1.10},
        "causality_tags": ["robotics", "automation", "production"],
        "probability": 0.25
    },
    {
        "title": "Autonomous Delivery Drone Accident",
        "description": "Fatal accident involving delivery drone triggers safety review and regulatory scrutiny.",
        "event_type": "crisis",
        "affected_sectors": ["Robotics", "AI"],
        "impact_multipliers": {"Robotics": 0.78, "AI": 0.88},
        "causality_tags": ["robotics", "safety", "regulation"],
        "probability": 0.25
    },
    {
        "title": "Warehouse Automation Adoption Surges",
        "description": "Labor shortages drive massive adoption of robotic warehouse systems across industries.",
        "event_type": "breakthrough",
        "affected_sectors": ["Robotics", "AI"],
        "impact_multipliers": {"Robotics": 1.18, "AI": 1.08},
        "causality_tags": ["robotics", "automation", "logistics"],
        "probability": 0.35
    },
    {
        "title": "Robot Rights Movement Gains Momentum",
        "description": "Ethical debates over AI consciousness and robot rights influence legislation.",
        "event_type": "regulation",
        "affected_sectors": ["Robotics", "AI"],
        "impact_multipliers": {"Robotics": 0.92, "AI": 0.94},
        "causality_tags": ["robotics", "ethics", "regulation"],
        "probability": 0.2
    },

    # === FINANCIAL SECTOR EVENTS ===
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
        "title": "Central Bank Digital Currency Launch",
        "description": "Major central banks launch official digital currencies, transforming payment systems.",
        "event_type": "breakthrough",
        "affected_sectors": ["Finance", "AI"],
        "impact_multipliers": {"Finance": 1.15, "AI": 1.06},
        "causality_tags": ["finance", "currency", "digital"],
        "probability": 0.3
    },
    {
        "title": "Cryptocurrency Market Collapse",
        "description": "Major cryptocurrency exchanges fail, causing massive losses and regulatory crackdown.",
        "event_type": "crisis",
        "affected_sectors": ["Finance", "AI"],
        "impact_multipliers": {"Finance": 0.82, "AI": 0.95},
        "causality_tags": ["finance", "crypto", "crisis"],
        "probability": 0.3
    },
    {
        "title": "AI-Driven Trading Algorithms Banned",
        "description": "Regulators restrict high-frequency algorithmic trading to prevent market manipulation.",
        "event_type": "regulation",
        "affected_sectors": ["Finance", "AI"],
        "impact_multipliers": {"Finance": 0.90, "AI": 0.88},
        "causality_tags": ["finance", "AI", "regulation"],
        "probability": 0.25
    },
    {
        "title": "Global Financial Transaction Tax Implemented",
        "description": "Coordinated international effort introduces small tax on all financial transactions.",
        "event_type": "regulation",
        "affected_sectors": ["Finance"],
        "impact_multipliers": {"Finance": 0.85},
        "causality_tags": ["finance", "taxation", "regulation"],
        "probability": 0.2
    },
    {
        "title": "Decentralized Finance Platform Hacked",
        "description": "Major DeFi protocol exploited for billions, raising security and regulatory concerns.",
        "event_type": "crisis",
        "affected_sectors": ["Finance", "AI"],
        "impact_multipliers": {"Finance": 0.78, "AI": 0.92},
        "causality_tags": ["finance", "security", "crypto"],
        "probability": 0.3
    },

    # === CROSS-SECTOR & GEOPOLITICAL EVENTS ===
    {
        "title": "Trade War Escalation",
        "description": "Major economic powers impose tariffs on technology goods, disrupting global supply chains.",
        "event_type": "crisis",
        "affected_sectors": ["AI", "Quantum", "Robotics", "Telecom"],
        "impact_multipliers": {"AI": 0.82, "Quantum": 0.80, "Robotics": 0.85, "Telecom": 0.88},
        "causality_tags": ["geopolitical", "trade", "crisis"],
        "probability": 0.3
    },
    {
        "title": "International Climate Agreement Strengthened",
        "description": "Enhanced global climate commitments drive massive investment in clean technology.",
        "event_type": "regulation",
        "affected_sectors": ["Energy", "Robotics", "AI"],
        "impact_multipliers": {"Energy": 1.20, "Robotics": 1.08, "AI": 1.05},
        "causality_tags": ["climate", "regulation", "sustainability"],
        "probability": 0.35
    },
    {
        "title": "Global Skills Gap Crisis",
        "description": "Severe shortage of technical talent threatens innovation across all tech sectors.",
        "event_type": "crisis",
        "affected_sectors": ["AI", "Quantum", "Robotics", "Pharma"],
        "impact_multipliers": {"AI": 0.88, "Quantum": 0.85, "Robotics": 0.90, "Pharma": 0.92},
        "causality_tags": ["labor", "education", "crisis"],
        "probability": 0.25
    },
    {
        "title": "Universal Basic Income Pilot Programs Expand",
        "description": "Multiple countries implement UBI in response to automation, affecting consumer behavior.",
        "event_type": "regulation",
        "affected_sectors": ["Robotics", "AI", "Finance"],
        "impact_multipliers": {"Robotics": 1.10, "AI": 1.08, "Finance": 1.12},
        "causality_tags": ["policy", "automation", "social"],
        "probability": 0.2
    },
    {
        "title": "Space Resource Mining Rights Established",
        "description": "International treaty defines property rights for asteroid mining, opening new markets.",
        "event_type": "regulation",
        "affected_sectors": ["Robotics", "Energy", "AI"],
        "impact_multipliers": {"Robotics": 1.15, "Energy": 1.12, "AI": 1.06},
        "causality_tags": ["space", "resources", "regulation"],
        "probability": 0.15
    },
    {
        "title": "Global Intellectual Property Reform",
        "description": "Major changes to patent law affect technology development and competition.",
        "event_type": "regulation",
        "affected_sectors": ["AI", "Quantum", "Pharma", "Robotics"],
        "impact_multipliers": {"AI": 0.95, "Quantum": 0.93, "Pharma": 0.90, "Robotics": 0.94},
        "causality_tags": ["IP", "regulation", "innovation"],
        "probability": 0.25
    },
    {
        "title": "Breakthrough in Room-Temperature Superconductors",
        "description": "Discovery enables lossless power transmission and revolutionary computing advances.",
        "event_type": "breakthrough",
        "affected_sectors": ["Energy", "Quantum", "AI", "Telecom"],
        "impact_multipliers": {"Energy": 1.35, "Quantum": 1.30, "AI": 1.20, "Telecom": 1.15},
        "causality_tags": ["materials", "physics", "breakthrough"],
        "probability": 0.1
    }
]
