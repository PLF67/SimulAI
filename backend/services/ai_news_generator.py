"""AI-powered news generation system"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.database import NewsItem, Game, Stock, GameEvent
from typing import List, Optional
from datetime import datetime
import random

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AINewsGenerator:
    """Generates realistic news items using AI"""

    def __init__(self, db: AsyncSession, api_key: Optional[str] = None, provider: str = "anthropic"):
        self.db = db
        self.provider = provider
        self.api_key = api_key

        if provider == "anthropic" and ANTHROPIC_AVAILABLE and api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        elif provider == "openai" and OPENAI_AVAILABLE and api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None

    async def generate_news_from_event(self, game_id: int, event: GameEvent) -> NewsItem:
        """Generate a news article based on a game event"""
        if self.client:
            content = await self._generate_ai_news(event)
        else:
            content = self._generate_template_news(event)

        # Determine sentiment
        sentiment = "positive" if any(v > 1.0 for v in event.impact_multipliers.values()) else "negative"

        news_item = NewsItem(
            game_id=game_id,
            title=event.title,
            content=content,
            news_type="event",
            related_sectors=event.affected_sectors,
            sentiment=sentiment,
            quarter=event.quarter_triggered
        )

        self.db.add(news_item)
        await self.db.commit()
        await self.db.refresh(news_item)

        return news_item

    async def generate_sector_news(self, game_id: int, sector: str, quarter: int) -> NewsItem:
        """Generate general news about a sector's progress"""
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()

        news_types = ["innovation", "setback", "societal"]
        news_type = random.choice(news_types)

        if self.client:
            content = await self._generate_ai_sector_news(sector, news_type, quarter)
            title = content.split('\n')[0] if '\n' in content else content[:100]
        else:
            title, content = self._generate_template_sector_news(sector, news_type)

        sentiment = "positive" if news_type == "innovation" else "negative" if news_type == "setback" else "neutral"

        news_item = NewsItem(
            game_id=game_id,
            title=title,
            content=content,
            news_type=news_type,
            related_sectors=[sector],
            sentiment=sentiment,
            quarter=quarter
        )

        self.db.add(news_item)
        await self.db.commit()
        await self.db.refresh(news_item)

        return news_item

    async def _generate_ai_news(self, event: GameEvent) -> str:
        """Generate news using AI"""
        prompt = f"""Write a realistic news article (2-3 paragraphs) about the following event:

Title: {event.title}
Description: {event.description}
Event Type: {event.event_type}
Affected Sectors: {', '.join(event.affected_sectors)}

Write in a professional journalistic style, as if this is appearing in a financial news publication.
Include quotes from fictional industry experts and discuss market implications."""

        try:
            if self.provider == "anthropic":
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_news(event)

    async def _generate_ai_sector_news(self, sector: str, news_type: str, quarter: int) -> str:
        """Generate sector news using AI"""
        if news_type == "innovation":
            prompt_type = "a breakthrough or advancement"
        elif news_type == "setback":
            prompt_type = "a challenge or setback"
        else:
            prompt_type = "a societal or market development"

        prompt = f"""Write a realistic news article (2-3 paragraphs) about {prompt_type} in the {sector} sector.

This is for quarter {quarter} of a business simulation game.
Write in a professional journalistic style.
Include specific details and fictional company names.
Discuss implications for investors and the industry."""

        try:
            if self.provider == "anthropic":
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"AI generation failed: {e}")
            title, content = self._generate_template_sector_news(sector, news_type)
            return f"{title}\n\n{content}"

    def _generate_template_news(self, event: GameEvent) -> str:
        """Generate news using templates (fallback when AI is not available)"""
        templates = {
            "breakthrough": [
                "Industry analysts are calling this a game-changing development. The breakthrough is expected to accelerate innovation across multiple sectors and create new market opportunities. Leading investment firms have upgraded their sector ratings, with Morgan Stanley analyst Dr. Sarah Chen noting, 'This fundamentally changes the competitive landscape.' Venture capital funding in related areas has already increased 40% this quarter as investors rush to capitalize on the opportunity.",
                "This represents a significant milestone in technological progress that could reshape entire industries. Experts predict widespread adoption within 18-24 months, potentially disrupting traditional business models and creating an estimated $50 billion market opportunity. Fortune 500 companies are already forming strategic partnerships to integrate the new technology, while startups scramble to stake their claims in this emerging space.",
                "The announcement has triggered a wave of excitement across global markets, with sector indices surging in early trading. 'We haven't seen this level of fundamental innovation since the early days of the internet,' comments venture capitalist James Rodriguez of Sequoia Capital. Major corporations are reportedly accelerating their R&D timelines, with some announcing immediate pilot programs to test commercial viability.",
                "Market watchers are closely monitoring how companies adapt to this paradigm shift, which analysts estimate could generate returns of 200-300% for early movers. Goldman Sachs has issued a research note suggesting this could be 'the most significant technological advancement of the decade,' while cautioning that execution risks remain substantial for companies without deep technical expertise.",
                "This breakthrough comes at a critical juncture for the industry, which has been seeking new growth catalysts after years of incremental improvements. Early adopters are already reporting significant efficiency gains, with some claiming 10x performance improvements over legacy systems. However, experts warn that the transition period could be turbulent, with smaller players potentially struggling to compete as barriers to entry shift dramatically."
            ],
            "crisis": [
                "The situation has sent shockwaves through global markets, with sector indices down 15-25% in volatile trading as investors reassess risk profiles. Emergency board meetings are being convened across the industry, with several CEOs issuing statements attempting to calm investor fears. 'This is a wake-up call for the entire sector,' warns risk management consultant Michael Torres, 'and companies that don't respond decisively could face existential threats.'",
                "This development has raised serious concerns among institutional investors, triggering a broad sell-off as hedge funds reduce exposure to affected sectors. Rating agencies are reviewing credit ratings for major companies, while insurance premiums for related risks have already doubled. Legal experts anticipate a wave of shareholder lawsuits, with several class-action filings already in motion.",
                "Regulatory bodies are being called upon to address the emerging challenges, with congressional hearings scheduled for next month and multiple regulatory agencies launching investigations. The crisis has exposed systemic vulnerabilities that industry observers have long warned about, leading to calls for comprehensive oversight reform. 'We can't afford to be reactive anymore,' stated Senator Patricia Williams during a press conference.",
                "Companies are implementing emergency protocols and reviewing their risk management strategies as the full extent of the impact becomes clear. Some firms are halting related operations entirely while conducting internal audits, while others are rushing to reassure stakeholders that their systems are secure. The crisis has already cost an estimated $10 billion in market capitalization, with analysts predicting further losses if remediation efforts prove inadequate.",
                "Industry stakeholders are demanding immediate action as confidence erodes in previously trusted systems and processes. Consumer advocacy groups are calling for greater transparency and accountability, while some customers are already switching to alternative providers. The long-term reputational damage could take years to repair, fundamentally altering competitive dynamics across the sector.",
                "This incident highlights the interconnected nature of modern technological systems, where a failure in one area can cascade across multiple sectors. Supply chain disruptions are already being reported, with some companies warning of potential delays in product deliveries. Cybersecurity experts are urging organizations to review their defensive postures, noting that this crisis may embolden other threat actors."
            ],
            "regulation": [
                "The new regulatory framework will require significant adjustments from industry players, with compliance costs estimated at $2-5 million per organization over the next two years. Legal teams are scrambling to interpret the complex requirements, which span over 300 pages of technical specifications and operational mandates. 'This is the most comprehensive regulatory overhaul we've seen in two decades,' notes compliance attorney David Kim of Baker McKenzie.",
                "Regulatory experts note that this change reflects growing public concern about industry practices and the need for stronger consumer protections. The rules, which take effect in six months, will fundamentally alter how companies operate, requiring new reporting systems, enhanced security protocols, and regular third-party audits. Industry lobbying groups have criticized the timeline as 'unrealistic,' while consumer advocates claim the measures don't go far enough.",
                "Market analysts expect a period of significant adjustment as businesses align with new requirements, potentially creating competitive advantages for well-capitalized firms that can afford rapid compliance. Smaller companies may struggle with the burden, leading to industry consolidation as they seek acquisition partners with deeper resources. Some startups are already revising their business models to avoid triggering the most onerous provisions.",
                "Companies are already planning their adaptation strategies, with many hiring specialized consultants and establishing dedicated compliance divisions. Early adopters who voluntarily exceed regulatory minimums may gain reputational benefits and attract customers increasingly concerned about these issues. However, executives worry that the regulatory patchwork across different jurisdictions could create operational headaches for global firms.",
                "The implementation timeline will be crucial for affected companies, many of which are calling for phased rollouts and grace periods to avoid disrupting ongoing operations. Regulators have indicated some flexibility on enforcement during the initial transition period, but have made clear that full compliance will be expected within 12-18 months. Industry associations are developing best-practice guides to help members navigate the complex new landscape.",
                "While some see this as a necessary step for market maturity and long-term sustainability, others worry about unintended consequences and competitive implications. There are concerns that excessive regulation could stifle innovation and push activity to less-regulated jurisdictions, potentially undermining the policy objectives. The debate over regulatory scope and timing is expected to intensify as implementation details are finalized."
            ]
        }

        template_list = templates.get(event.event_type, templates["breakthrough"])
        return random.choice(template_list)

    def _generate_template_sector_news(self, sector: str, news_type: str) -> tuple:
        """Generate sector news using templates"""
        templates = {
            "innovation": {
                "AI": [
                    ("AI Research Lab Announces Major Efficiency Gains",
                     "Researchers at DeepMind Technologies have developed a revolutionary algorithm that reduces computational requirements by 75% while improving accuracy by 20%. The breakthrough leverages novel sparse attention mechanisms that could make advanced AI accessible to mid-sized companies previously priced out of the market. Industry experts predict this will accelerate AI adoption across healthcare, finance, and manufacturing sectors, with early trials showing promising results in medical diagnosis and fraud detection."),
                    ("Neural Architecture Search Breakthrough Automates AI Design",
                     "Scientists at MIT's Computer Science and AI Lab have created a system that automatically designs optimal neural networks for specific tasks, reducing development time from months to days. The AutoML platform has already generated architectures that outperform human-designed systems in image recognition and language translation. Venture capital firms are rushing to invest in companies leveraging the technology, with Series A funding for AI startups up 60% this quarter."),
                    ("Edge AI Chips Enable Real-Time Processing Without Cloud",
                     "Next-generation AI processors from NVIDIA and Apple can now run complex models directly on devices, eliminating latency and privacy concerns associated with cloud computing. The chips consume 10x less power while delivering performance previously requiring data center resources. Applications in autonomous vehicles, medical devices, and smart manufacturing are expected to proliferate rapidly, creating a projected $30 billion market by 2027."),
                    ("Multimodal AI Achieves Human-Level Understanding",
                     "OpenAI's latest model demonstrates unprecedented ability to reason across text, images, audio, and video simultaneously, enabling applications from automated content creation to advanced robotics. The system scored 95% on comprehensive reasoning benchmarks, compared to 78% for previous state-of-the-art models. Major enterprises are already piloting implementations for customer service, creative production, and data analysis workflows."),
                    ("Explainable AI Breakthrough Addresses Black Box Problem",
                     "Researchers have developed techniques that make deep learning decisions fully transparent and interpretable, addressing a major barrier to AI adoption in regulated industries like healthcare and finance. The methods maintain model performance while providing detailed rationales for each prediction. Regulatory bodies are already updating guidelines to accommodate the new transparency capabilities.")
                ],
                "Quantum": [
                    ("Quantum Computing Reaches New Stability Milestone",
                     "Scientists at IBM Research have achieved unprecedented quantum coherence times of over 1 millisecond, a 10x improvement that brings practical quantum computing significantly closer to reality. The advance addresses one of the field's most persistent challenges and enables execution of complex algorithms previously impossible. Major technology companies are accelerating their quantum roadmaps, with commercial applications in drug discovery and cryptography expected within 3-5 years."),
                    ("Error Correction Breakthrough Makes Quantum Computing Scalable",
                     "Physicists at Google Quantum AI have demonstrated error rates below the critical threshold needed for fault-tolerant quantum computing, solving a decades-old problem. The achievement uses a novel surface code architecture that can be scaled to millions of qubits. Financial institutions are already partnering with quantum computing providers to prepare for applications in portfolio optimization and risk analysis."),
                    ("Photonic Quantum Computer Operates at Room Temperature",
                     "PsiQuantum has demonstrated a chip-scale quantum processor using photons instead of superconducting circuits, eliminating the need for expensive cryogenic cooling systems. The breakthrough could reduce quantum computer costs by 90% and enable desktop quantum devices. Early applications in materials science and logistics optimization are showing promising results in pilot programs."),
                    ("Quantum Sensors Achieve Unprecedented Precision",
                     "New quantum sensing technology can detect gravitational waves, magnetic fields, and molecular structures with sensitivity exceeding classical sensors by 1000x. Applications span medical imaging, mineral exploration, and national security. Commercial quantum sensors are expected to create a $12 billion market within five years as manufacturing scales up."),
                    ("Quantum Networking Milestone Enables Secure Communication",
                     "Researchers have demonstrated quantum entanglement distribution over 1000km of fiber optic cable, enabling unhackable communication networks. The technology uses novel quantum repeaters that preserve entanglement while amplifying signals. Governments and financial institutions are already planning quantum-secure communication infrastructure deployments.")
                ],
                "Finance": [
                    ("New FinTech Platform Disrupts Payment Processing",
                     "Stripe competitor PayFlow has launched an innovative payment system that reduces merchant transaction costs by 40% using advanced fraud detection AI and streamlined settlement processes. Early adopters including several Fortune 500 retailers report significant efficiency improvements and reduced chargebacks. Traditional financial institutions are responding by accelerating their own digital transformation initiatives, with JPMorgan Chase announcing a competing platform."),
                    ("Blockchain Settlement System Cuts Transaction Time to Minutes",
                     "A consortium of major banks has deployed a distributed ledger system that settles cross-border transactions in under 10 minutes, compared to 3-5 days for traditional SWIFT transfers. The platform has already processed over $50 billion in transactions with zero failures. Global trade volumes are expected to increase as working capital requirements decrease dramatically."),
                    ("AI-Powered Credit Scoring Expands Financial Inclusion",
                     "Alternative credit scoring models using machine learning can assess creditworthiness for the 1.7 billion unbanked adults globally, analyzing non-traditional data from mobile phones and social networks. Early deployments in emerging markets show default rates comparable to traditional credit scores while extending credit to previously excluded populations. Microfinance institutions are rapidly adopting the technology."),
                    ("Real-Time Fraud Detection Prevents $2 Billion in Losses",
                     "Advanced AI systems deployed across major payment networks can now identify fraudulent transactions with 99.8% accuracy in milliseconds, dramatically reducing financial crime. The systems analyze behavioral patterns, device fingerprints, and network relationships invisible to traditional rule-based systems. Cybersecurity insurance premiums have dropped 30% for institutions deploying the technology."),
                    ("Decentralized Finance Protocol Reaches $100B in Assets",
                     "Automated market makers and lending protocols have attracted massive capital flows as yield-seeking investors discover DeFi alternatives to traditional savings accounts. The platforms offer transparency, 24/7 operation, and yields 5-10x higher than conventional banks. Regulatory frameworks are evolving rapidly to address the growing sector.")
                ],
                "Pharma": [
                    ("Novel Drug Delivery System Shows Promise",
                     "Pharmaceutical researchers at Johns Hopkins have developed a targeted nanoparticle delivery mechanism that concentrates drugs at disease sites with 95% precision, revolutionizing treatment effectiveness while reducing side effects. Phase II clinical trials for cancer treatments show tumor shrinkage rates 40% higher than conventional chemotherapy with dramatically fewer adverse reactions. The technology platform is being adapted for cardiovascular, neurological, and autoimmune diseases."),
                    ("mRNA Vaccine Platform Adapted for Multiple Diseases",
                     "Building on COVID-19 vaccine success, Moderna has announced breakthrough results for mRNA treatments targeting cancer, HIV, and rare genetic disorders. The platform can generate tailored therapies in weeks rather than years. Oncology trials show complete responses in 35% of previously untreatable patients, prompting accelerated regulatory pathways."),
                    ("AI Drug Discovery Identifies Treatment in Record Time",
                     "Artificial intelligence systems from Recursion Pharmaceuticals have identified a promising Alzheimer's treatment candidate in just 6 months, compared to typical 4-5 year timelines. The AI analyzed 2.3 billion biological relationships to predict drug efficacy and safety. Investors have poured $800 million into AI drug discovery startups this quarter."),
                    ("CRISPR Gene Editing Cures Genetic Disease in Trial",
                     "Patients with sickle cell disease treated with CRISPR-edited cells show complete remission with no symptoms for 18+ months in groundbreaking trials. The one-time treatment addresses the genetic root cause rather than managing symptoms. Regulatory approval for multiple genetic diseases is expected within 2 years, creating a potential $20 billion market."),
                    ("Continuous Glucose Monitor Breakthrough for Diabetes",
                     "Next-generation sensors can monitor blood glucose non-invasively through skin for 6 months without calibration, dramatically improving diabetes management. Integration with insulin pumps creates closed-loop artificial pancreas systems. The technology is expected to prevent thousands of diabetes-related complications annually.")
                ],
                "Energy": [
                    ("Solar Panel Efficiency Reaches Record High",
                     "Tandem perovskite-silicon solar cells have achieved 35% efficiency in commercial production, up from 22% for conventional panels, making solar power the cheapest electricity source globally. Manufacturing costs remain competitive as production scales up at new gigafactories. Energy analysts predict solar will dominate new power generation installations within 3 years, with fossil fuel plants becoming economically obsolete."),
                    ("Next-Generation Battery Triples Energy Density",
                     "Solid-state lithium-metal batteries from QuantumScape deliver 800 wh/kg, enabling electric vehicles with 1000+ mile range and 15-minute charging times. The batteries eliminate fire risk and last 1 million miles. Automakers have placed $10 billion in orders ahead of 2026 mass production."),
                    ("Green Hydrogen Production Costs Drop Below Natural Gas",
                     "Improved electrolyzer efficiency and cheap renewable electricity have made green hydrogen competitive with fossil fuels for the first time. Major industrial users including steel and ammonia producers are switching to carbon-free hydrogen. Infrastructure investments of $300 billion are planned to build hydrogen distribution networks."),
                    ("Advanced Geothermal Technology Unlocks Baseload Clean Power",
                     "New drilling techniques can access superhot rock formations anywhere on Earth, providing 24/7 clean electricity without weather dependence. Pilot projects deliver power at $40/MWh, competitive with coal and gas. The technology could supply all global electricity needs from a tiny fraction of Earth's geothermal energy."),
                    ("Smart Grid AI Optimizes Renewable Energy Integration",
                     "Machine learning systems can predict and balance intermittent solar and wind generation with 98% accuracy, eliminating the need for fossil fuel backup power. Grid stability has improved even with 80%+ renewable penetration. Utilities are rapidly deploying the technology to accelerate decarbonization while maintaining reliability.")
                ],
                "Telecom": [
                    ("6G Wireless Technology Promises 1Tbps Speeds",
                     "Next-generation wireless standards finalized by the ITU enable terabit-per-second data rates and microsecond latency using terahertz frequencies and AI-optimized networking. Applications in holographic communication, brain-computer interfaces, and smart cities require the massive bandwidth. Infrastructure deployment begins in 2027 with early rollouts in major tech hubs."),
                    ("Satellite-to-Phone Direct Connectivity Launches Globally",
                     "Starlink and AST SpaceMobile enable standard smartphones to connect directly to satellites, eliminating cellular dead zones worldwide. The technology provides emergency communication and basic data services anywhere on Earth. Traditional telecom operators are partnering rather than competing with satellite providers."),
                    ("Quantum Communication Network Demonstrates Unhackable Security",
                     "Commercial quantum key distribution networks now operate in major financial centers, providing mathematically guaranteed secure communication. No quantum-encrypted message has ever been intercepted. Government agencies and banks are mandating quantum security for classified and high-value transactions."),
                    ("AI Network Optimization Doubles Capacity Without New Infrastructure",
                     "Machine learning systems from Ericsson dynamically optimize 5G networks in real-time, doubling capacity and reducing power consumption by 40%. The software upgrade path allows operators to defer expensive infrastructure investments. Customer experience metrics have improved significantly in trial deployments."),
                    ("Fiber Optic Breakthrough Enables Petabit Internet Backbone",
                     "Optical chips can transmit data at petabit-per-second rates through existing fiber infrastructure using spatial multiplexing and advanced signal processing. The technology future-proofs internet backbones for decades of traffic growth. Network operators are upgrading core infrastructure to handle exploding data demands from AI and video.")
                ],
                "Robotics": [
                    ("Humanoid Robots Enter Service Industry at Scale",
                     "Figure AI and Tesla have begun mass-producing general-purpose humanoid robots for warehousing, retail, and hospitality at $50,000 per unit. The robots can perform any task a human worker can after brief training. Labor-constrained industries are rapidly adopting the technology, with 500,000 units deployed in the past year."),
                    ("Surgical Robots Achieve Superhuman Precision",
                     "AI-guided robotic surgery systems can perform microsurgeries with 10x greater precision than human surgeons, enabling previously impossible procedures. Complications and recovery times have dropped by 60% in thousands of procedures. Leading hospitals are establishing robotic surgery centers of excellence."),
                    ("Autonomous Warehouse Systems Eliminate Human Workers",
                     "Amazon and Alibaba distribution centers operate with 95% automation using coordinated fleets of mobile robots, drones, and AI management systems. Throughput has tripled while operating costs dropped 40%. The technology is spreading rapidly across logistics and manufacturing sectors."),
                    ("Agricultural Robots Increase Crop Yields 30%",
                     "Autonomous farming robots can plant, monitor, and harvest crops with precision impossible for human farmers, reducing waste and optimizing growing conditions for each plant. Water and fertilizer usage drops by half while yields increase dramatically. The technology addresses food security challenges from climate change and population growth."),
                    ("Domestic Robots Handle Household Chores Autonomously",
                     "Consumer robots from iRobot and Dyson can now clean, organize, and maintain homes with minimal human intervention using advanced perception and manipulation AI. Pre-orders exceed 2 million units at $3000 price points. The technology is especially valuable for elderly care and accessibility applications.")
                ]
            },
            "setback": {
                "AI": [
                    ("AI Model Collapse Threatens Training Data Quality",
                     "Researchers warn that synthetic data from AI systems is contaminating training datasets, potentially degrading future model performance. The phenomenon called 'model collapse' occurs when AI-generated content dominates the internet, creating a feedback loop. Companies are scrambling to secure clean historical data and develop detection methods for synthetic content."),
                    ("Energy Costs Threaten AI Industry Sustainability",
                     "Training large AI models now consumes electricity equivalent to small countries, raising concerns about environmental impact and operational costs. A single training run for frontier models costs $100+ million in compute. Researchers are urgently seeking more efficient architectures as energy constraints threaten to slow AI progress."),
                    ("AI Hallucination Problem Persists Despite Advances",
                     "Large language models continue to generate false information with confidence, limiting deployment in critical applications like healthcare and law. Several high-profile failures have resulted in lawsuits and regulatory scrutiny. The fundamental challenge of grounding AI in verifiable truth remains unsolved despite significant research efforts.")
                ],
                "Quantum": [
                    ("Quantum Computing Timeline Slips as Challenges Mount",
                     "Leading quantum computing companies have delayed commercial availability targets by 3-5 years as error correction proves more difficult than anticipated. Scaling beyond 1000 qubits faces fundamental physics obstacles. Investors are growing impatient as billions invested have yet to produce practical applications."),
                    ("Quantum Supremacy Claims Face Skepticism",
                     "Classical computing improvements have matched or exceeded claimed quantum advantages in several benchmark problems. Debate intensifies over whether quantum computers will ever achieve meaningful speedups for real-world problems. Some researchers argue quantum computing may be relegated to niche applications rather than transformative technology.")
                ],
                "Finance": [
                    ("Algorithmic Trading Malfunction Causes Flash Crash",
                     "A software bug in high-frequency trading systems triggered cascading sell-offs that erased $500 billion in market value in minutes before circuit breakers halted trading. The incident highlights systemic risks from automated trading and market fragility. Regulators are reviewing HFT oversight and considering tighter controls."),
                    ("Fintech Lending Platform Faces Rising Default Rates",
                     "AI-powered credit models failed to predict increased defaults during economic slowdown, resulting in massive losses for lenders and investors. The models trained on historical data didn't generalize to changing economic conditions. Traditional banks are reconsidering fintech partnerships as risks become apparent.")
                ],
                "Pharma": [
                    ("Drug Trial Failures Cast Doubt on AI-Designed Molecules",
                     "Three AI-discovered drug candidates have failed Phase II trials due to unexpected toxicity, raising questions about AI drug discovery approaches. The failures highlight gaps in AI understanding of complex biological systems. Biotech valuations have declined 25% as investor enthusiasm wanes."),
                    ("Antibiotic Resistance Crisis Worsens as Pipeline Dries Up",
                     "Pharmaceutical companies continue abandoning antibiotic research despite growing superbug threats, as economic incentives favor chronic disease treatments. WHO warns that antibiotic-resistant infections could cause 10 million deaths annually by 2050. Governments are considering major policy interventions to revive antibiotic development.")
                ],
                "Energy": [
                    ("Grid Instability from Renewable Intermittency Causes Blackouts",
                     "Unexpected weather patterns caused simultaneous solar and wind power drops across regions, overwhelming grid management systems and causing rolling blackouts. The incident demonstrates challenges of high renewable penetration without adequate storage. Utilities are reassessing renewable integration timelines and backup power requirements."),
                    ("Battery Material Shortages Threaten EV Transition",
                     "Lithium, cobalt, and nickel supply constraints are driving battery costs higher and creating supply chain vulnerabilities. Mining production cannot keep pace with surging demand from EV manufacturers. Some analysts predict battery shortages could delay electrification goals by a decade without major new mineral discoveries.")
                ],
                "Telecom": [
                    ("5G Deployments Fall Short of Performance Promises",
                     "Real-world 5G speeds and coverage are disappointing users expecting transformative improvements over 4G LTE. Infrastructure costs remain high while subscriber uptake lags projections. Telecom operators are reducing capital expenditure as return on investment appears uncertain."),
                    ("Satellite Internet Capacity Constraints Limit Growth",
                     "Low-earth-orbit satellite networks face congestion as subscriber numbers exceed capacity planning assumptions. Service quality is degrading with peak-time slowdowns. Additional satellite launches required to meet demand are delaying profitability and straining operator finances.")
                ],
                "Robotics": [
                    ("Autonomous Vehicle Testing Suspended After Fatal Accident",
                     "A self-driving car's failure to detect pedestrians in complex lighting conditions resulted in a fatality, triggering widespread testing halts and regulatory reviews. The incident highlights persistent perception challenges in edge cases. Public trust in autonomous vehicles has declined sharply following the accident."),
                    ("Robot Reliability Issues Plague Manufacturing Deployments",
                     "Industrial robots are experiencing higher-than-expected failure rates in real-world conditions, causing production disruptions and safety concerns. Maintenance costs exceed projections while uptime disappoints. Some manufacturers are reverting to human workers after negative ROI from automation investments.")
                ]
            },
            "societal": [
                ("AI Displacement Sparks Labor Market Transformation",
                 "Automation and AI are eliminating jobs faster than new roles emerge, particularly affecting routine cognitive and administrative work. Governments are exploring universal basic income pilots while retraining programs struggle to keep pace. The transition is creating social tension between productivity gains and employment disruption."),
                ("Data Privacy Concerns Reshape Tech Industry Practices",
                 "Growing public awareness of data collection and surveillance is driving demand for privacy-preserving technologies and regulation. Companies are adapting business models away from personal data exploitation. The shift is creating opportunities for privacy-focused alternatives to dominant platforms."),
                ("Digital Divide Widens as Technology Advances Accelerate",
                 "Gap between technologically advanced and developing regions is expanding as cutting-edge innovations concentrate in wealthy areas. Access to AI, high-speed internet, and digital services correlates strongly with economic outcomes. International development organizations are prioritizing technology access initiatives."),
                ("Aging Population Drives Healthcare Technology Investment",
                 "Demographic shifts in developed countries are creating massive demand for elder care technologies, telemedicine, and AI health monitoring. The healthcare technology market is projected to triple by 2035 as baby boomers require extensive medical services. Companies are pivoting toward age-tech opportunities."),
                ("Climate Migration Influences Infrastructure Planning",
                 "Rising sea levels and extreme weather are forcing population relocations, driving infrastructure investment in safer regions. Technology sectors are adapting to geographic shifts in workforce and customer locations. The trend is creating both challenges and opportunities for long-term strategic planning."),
                ("Education Systems Struggle to Adapt to AI Era",
                 "Traditional curricula are becoming obsolete as AI automates many skills previously taught in schools. Debate intensifies over what students should learn when information retrieval and routine analysis are automated. Educational technology companies are developing AI-era learning approaches."),
                ("Remote Work Revolution Reshapes Urban Development",
                 "Permanent shift to distributed work is reducing demand for commercial real estate while increasing investment in collaboration technologies. Cities are adapting infrastructure as commuting patterns change fundamentally. The trend is creating new geographic patterns in technology sector employment."),
                ("Synthetic Media Threatens Information Ecosystem Trust",
                 "Increasingly sophisticated deepfakes and AI-generated content are making it difficult to distinguish real from fabricated media. Trust in online information is declining as manipulation becomes easier. Technology companies are racing to develop authentication and provenance systems."),
                ("Mental Health Crisis Linked to Social Media Usage",
                 "Research increasingly connects social media algorithms optimizing for engagement with anxiety, depression, and attention disorders, particularly in young people. Regulatory pressure is mounting for design changes and age restrictions. The findings are driving demand for healthier technology alternatives."),
                ("Gig Economy Growth Challenges Traditional Labor Protections",
                 "Platform-based work is expanding rapidly while worker protections and benefits lag behind employment model changes. Debate intensifies over classification and rights of gig workers. Legislation is evolving differently across jurisdictions, creating compliance challenges for platforms.")
            ]
        }

        # Select appropriate template based on news type and sector
        if news_type in templates and sector in templates[news_type]:
            sector_templates = templates[news_type][sector]
            if isinstance(sector_templates, list):
                return random.choice(sector_templates)
            else:
                return sector_templates
        elif news_type == "societal":
            # Societal news is cross-sector
            return random.choice(templates["societal"])
        else:
            # Generic fallback
            return (f"{sector} Sector Develops Amid Market Changes",
                   f"The {sector} sector continues to navigate evolving market conditions with mixed signals for investors. Industry participants are adapting strategies to address emerging challenges and opportunities. Analysts note that competitive dynamics are shifting as new technologies and business models emerge. Some companies are positioning themselves to capitalize on long-term trends, while others focus on near-term operational execution. Market observers remain cautiously optimistic about the sector's medium-term prospects.")

    async def get_recent_news(self, game_id: int, limit: int = 10) -> List[NewsItem]:
        """Get recent news for a game"""
        result = await self.db.execute(
            select(NewsItem)
            .where(NewsItem.game_id == game_id)
            .order_by(NewsItem.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
