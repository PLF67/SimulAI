# SimulAI - Business Simulation Game

A sophisticated business simulation game where players compete by building and managing investment portfolios in a dynamic market influenced by AI-generated events and news.

## 🎮 Overview

SimulAI is a comprehensive business game application that simulates realistic market dynamics with:

- **Multiple Players**: Compete against others to build the most valuable portfolio
- **Dynamic Markets**: Stock prices influenced by events, news, and market forces
- **Event System**: Real-world inspired events with causality chains affecting multiple sectors
- **AI-Powered News**: Automatically generated news articles that reflect market developments
- **Causality Engine**: Understands implicit connections between events and business sectors
- **Quarterly Trading**: Strategic decision-making at quarterly intervals
- **Game Master Control**: Full oversight and event triggering capabilities

## 🏗️ Architecture

### Backend (FastAPI)
- **Portfolio Manager**: Handles all trading, valuations, and portfolio calculations
- **Event System**: Manages events with intelligent causality engine
- **AI News Generator**: Creates realistic news using Claude (Anthropic) or GPT (OpenAI)
- **Game Manager**: Orchestrates overall game flow and state

### Frontend (Streamlit)
1. **Player Dashboard**: Individual player interface for trading and portfolio management
2. **Game Master Control Panel**: Admin interface for game management and event triggering
3. **Public Dashboard**: Real-time leaderboard and market statistics

### Database (SQLite/Async)
- Games, Players, Stocks, Holdings, Transactions
- Events, Event Templates, News Items
- Historical price data

## 📊 Features

### For Players
- View and manage personal portfolio
- Buy/sell stocks across multiple sectors
- Monitor real-time market performance
- Read AI-generated news and event updates
- Track rankings and competition
- See profit/loss metrics

### For Game Masters
- Create and manage multiple games
- Add players to games
- Start/pause/resume/end games
- Advance quarters manually
- Trigger specific events
- Monitor all player portfolios
- View comprehensive analytics

### Stock Sectors
- **AI**: Machine Learning, Deep Learning, NLP
- **Quantum Computing**: Quantum Hardware, Cryptography, Software
- **Finance**: Digital Banking, Blockchain, Payments
- **Pharmaceuticals**: Biotech, Gene Therapy, Vaccines
- **Energy**: Renewable, Nuclear Fusion, Energy Storage
- **Telecommunications**: 5G, Satellite Communications
- **Robotics**: Industrial Automation, Autonomous Vehicles

### Event Types
- **Breakthroughs**: Positive developments boosting sectors
- **Crises**: Negative events causing market disruptions
- **Regulations**: Policy changes with mixed effects

### Causality Engine
The system understands implicit connections:
- AI breakthroughs boost Robotics and Finance
- Energy innovations strengthen Robotics and Transportation
- Quantum advances impact AI and Cryptography
- Pharma developments benefit from AI and Quantum progress

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd SimulAI
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (optional: add AI API keys)
```

### Step 4: Create Data Directory
```bash
mkdir -p data
```

## 🎯 Usage

### Option 1: Run All Components Together (Recommended)
```bash
./run_all.sh
```

This starts:
- Backend API: http://localhost:8000
- Player Frontend: http://localhost:8501
- Game Master Frontend: http://localhost:8502
- Dashboard: http://localhost:8503

### Option 2: Run Components Separately

**Backend API:**
```bash
./run_backend.sh
# or
python -m uvicorn backend.api.main:app --reload
```

**Player Frontend:**
```bash
./run_player_frontend.sh
# or
streamlit run frontend/player/app.py --server.port 8501
```

**Game Master Frontend:**
```bash
./run_gamemaster_frontend.sh
# or
streamlit run frontend/gamemaster/app.py --server.port 8502
```

**Public Dashboard:**
```bash
./run_dashboard.sh
# or
streamlit run frontend/dashboard/app.py --server.port 8503
```

## 📖 How to Play

### For Game Masters:

1. **Create a Game**
   - Open Game Master interface (http://localhost:8502)
   - Use "Create New Game" in sidebar
   - Set game name and total quarters (default: 12)

2. **Add Players**
   - Go to "Players" tab
   - Add players with name and email
   - Each player starts with $100,000

3. **Start the Game**
   - Click "Start Game" button
   - Game status changes to "Active"

4. **Manage Quarters**
   - Click "Advance to Next Quarter" to progress
   - Events and news are automatically generated
   - Market prices fluctuate based on events and volatility

5. **Trigger Events** (Optional)
   - Go to "Events" tab
   - Select and trigger specific events manually
   - View impact on different sectors

6. **Monitor Progress**
   - View player rankings
   - Analyze market performance
   - Review event history

### For Players:

1. **Select Game and Player**
   - Open Player interface (http://localhost:8501)
   - Select your game from dropdown
   - Select your player name

2. **View Portfolio**
   - See current cash and holdings
   - Monitor total portfolio value
   - Track profit/loss

3. **Trade Stocks**
   - Browse available stocks
   - Filter by sector
   - Buy or sell shares
   - Trades execute at current market prices

4. **Stay Informed**
   - Read latest news
   - Review game events
   - Understand sector impacts

5. **Check Rankings**
   - View leaderboard
   - Compare with other players
   - Track your rank

6. **Strategy Tips**
   - Diversify across sectors
   - Watch for event announcements
   - Consider causality effects
   - Balance risk and opportunity

## 🔧 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints:

**Games:**
- `POST /games` - Create game
- `GET /games` - List games
- `POST /games/{id}/start` - Start game
- `POST /games/{id}/advance-quarter` - Advance quarter

**Players:**
- `POST /players` - Create player
- `GET /games/{id}/players` - List players
- `GET /games/{id}/rankings` - Get rankings

**Trading:**
- `POST /trades/buy` - Buy stock
- `POST /trades/sell` - Sell stock
- `GET /players/{id}/portfolio` - Get portfolio

**Events:**
- `POST /games/{id}/trigger-event` - Trigger event
- `GET /games/{id}/events` - Get events
- `GET /games/{id}/news` - Get news

## 🤖 AI Integration

### Optional AI News Generation

The system can generate realistic news using AI:

1. **Using Anthropic Claude:**
   ```bash
   ANTHROPIC_API_KEY=your_key_here
   AI_PROVIDER=anthropic
   ```

2. **Using OpenAI GPT:**
   ```bash
   OPENAI_API_KEY=your_key_here
   AI_PROVIDER=openai
   ```

3. **Without AI:**
   - News is generated using templates
   - Still functional but less dynamic

## 📁 Project Structure

```
SimulAI/
├── backend/
│   ├── api/
│   │   └── main.py              # FastAPI application
│   ├── database/
│   │   ├── connection.py        # Database connection
│   │   └── seed_data.py         # Initial data
│   ├── models/
│   │   ├── database.py          # SQLAlchemy models
│   │   └── schemas.py           # Pydantic schemas
│   └── services/
│       ├── portfolio_manager.py # Portfolio management
│       ├── event_system.py      # Event and causality engine
│       ├── ai_news_generator.py # AI news generation
│       └── game_manager.py      # Game orchestration
├── frontend/
│   ├── player/
│   │   └── app.py               # Player interface
│   ├── gamemaster/
│   │   └── app.py               # Game master interface
│   └── dashboard/
│       └── app.py               # Public dashboard
├── config/
│   └── settings.py              # Application settings
├── data/                        # Database storage
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🎲 Game Mechanics

### Portfolio Valuation
- **Total Value** = Cash + Sum(Holdings × Current Price)
- **P/L** = Total Value - Initial Investment
- **ROI** = (P/L / Initial Investment) × 100%

### Price Changes
1. **Random Fluctuations**: Based on stock volatility (quarterly)
2. **Event Impacts**: Multipliers applied to affected sectors
3. **Causality Effects**: Secondary impacts on related sectors

### Causality Examples
- **AI Breakthrough** → Boosts Robotics (+5%), Finance (+3%)
- **Energy Crisis** → Hurts Robotics (-10%), Telecom (-5%)
- **Regulation** → Sector-specific impacts with spillover effects

### Trading Rules
- Trades execute at current market price
- Must have sufficient cash to buy
- Must own shares to sell
- Portfolio values update each quarter
- Can only trade during active game

## 🏆 Winning Strategy

1. **Diversification**: Don't put all eggs in one basket
2. **Event Awareness**: Read news and events carefully
3. **Sector Correlation**: Understand causality relationships
4. **Risk Management**: Balance high-volatility and stable stocks
5. **Quarter Timing**: Plan trades strategically
6. **Cash Reserve**: Keep some cash for opportunities

## 🔒 Security Notes

- This is a simulation game for educational/entertainment purposes
- No real money is involved
- API keys should be kept secure
- Database is local SQLite (not production-ready for large scale)

## 🚧 Future Enhancements

Potential additions:
- Options and derivatives trading
- Short selling
- Market maker system
- Historical price charts
- Player chat/communication
- Tournament mode
- Custom event creation
- Export game results
- Multiplayer real-time mode

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional stock sectors
- More event templates
- Enhanced AI prompts
- UI/UX improvements
- Performance optimizations
- Testing coverage

## 📄 License

[Specify your license here]

## 📧 Support

For issues, questions, or suggestions:
- Create an issue in the repository
- Contact the development team

## 🎉 Credits

Built with:
- FastAPI - Modern Python web framework
- Streamlit - Interactive web apps
- SQLAlchemy - SQL toolkit and ORM
- Anthropic Claude / OpenAI GPT - AI news generation
- Plotly - Interactive visualizations

---

**Enjoy the game and may the best investor win! 📈🏆**
