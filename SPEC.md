# SimulAI System Specification

## 1. Overview
SimulAI is a multiplayer business simulation platform that couples an asynchronous FastAPI backend with three Streamlit frontends. Players trade simulated stocks whose prices evolve through stochastic fluctuations and AI-driven events. The platform exposes REST endpoints for game orchestration, portfolio management, event handling, and news generation, while Streamlit applications provide tailored control surfaces for players, game masters, and spectators.

## 2. Architecture Summary
- **Backend API** – FastAPI application (`backend/api/main.py`) exposing REST endpoints for games, players, stocks, portfolios, trades, events, news, and dashboards. Database access uses SQLAlchemy async sessions managed in `backend/database/connection.py`.
- **Domain Models** – SQLAlchemy ORM models defined in `backend/models/database.py` represent games, players, stocks, holdings, transactions, game events, event templates, news items, and stock price history. Pydantic schemas (`backend/models/schemas.py`) serialize responses and requests.
- **Services Layer** – Business logic encapsulated in service classes:
  - `GameManager` drives game lifecycle, quarter progression, stock seeding, and delegates to other services. 【F:backend/services/game_manager.py†L16-L123】
  - `PortfolioManager` executes trades, updates holdings and valuations, applies market fluctuations, and assembles rankings. 【F:backend/services/portfolio_manager.py†L1-L170】
  - `EventSystem` seeds, selects, and applies event templates using a causality engine to propagate sector effects. 【F:backend/services/event_system.py†L1-L167】
  - `AINewsGenerator` synthesizes event-driven and sector news items via Anthropic/OpenAI or deterministic templates. 【F:backend/services/ai_news_generator.py†L1-L104】
- **Frontends** – Three Streamlit apps (`frontend/player`, `frontend/gamemaster`, `frontend/dashboard`) consume REST endpoints for different user roles.
- **Configuration** – Runtime settings loaded through Pydantic (`config/settings.py`), including API host/port, database URL, initial player capital, and AI provider keys.

## 3. Backend API Specification
### 3.1 Lifespan and Middleware
- Application startup initializes the database, seeds stocks, and seeds event templates by instantiating service classes within the FastAPI lifespan context. 【F:backend/api/main.py†L17-L36】
- CORS is configured to allow all origins, headers, and methods to support the Streamlit clients. 【F:backend/api/main.py†L38-L45】

### 3.2 Game Management Endpoints
| Endpoint | Method | Description | Key Behaviors |
| --- | --- | --- | --- |
| `/games` | POST | Create a new game session from `GameCreate`. | Persists a `Game` with `status="setup"`, storing total quarters. 【F:backend/api/main.py†L48-L54】|
| `/games` | GET | List all games. | Returns `GameResponse` list queried via SQLAlchemy. 【F:backend/api/main.py†L56-L62】|
| `/games/{game_id}` | GET | Retrieve a specific game. | 404 if not found. 【F:backend/api/main.py†L64-L71】|
| `/games/{game_id}/start` | POST | Start a game. | Sets `status` to `active`, initializes quarter and timestamps. 【F:backend/api/main.py†L73-L82】|
| `/games/{game_id}/advance-quarter` | POST | Advance quarter. | Delegates to `GameManager.advance_quarter`, optionally triggering events and sector news. 【F:backend/api/main.py†L84-L95】|
| `/games/{game_id}/pause` `/resume` `/end` | POST | Control lifecycle transitions. | Return message on success, HTTP 400 if invalid state. 【F:backend/api/main.py†L97-L118】|

### 3.3 Player and Ranking Endpoints
- `/players` POST registers a new player tied to a game and seeded with initial cash from settings. 【F:backend/api/main.py†L122-L134】
- `/games/{game_id}/players` GET enumerates players for a given game. 【F:backend/api/main.py†L136-L142】
- `/players/{player_id}` GET returns player details or 404. 【F:backend/api/main.py†L144-L151】
- `/games/{game_id}/rankings` GET surfaces ranking data prepared by `PortfolioManager.get_player_rankings`. 【F:backend/api/main.py†L153-L157】

### 3.4 Stock and Portfolio Endpoints
- `/stocks` GET lists all seeded stocks; `/stocks/{stock_id}` GET returns individual stock. 【F:backend/api/main.py†L163-L179】
- `/players/{player_id}/portfolio` GET composes portfolio summary combining cash, holdings, and profit/loss metrics. 【F:backend/api/main.py†L181-L216】

### 3.5 Trading Endpoints
- `/trades/buy` and `/trades/sell` POST expect `TransactionCreate` payloads and route through `PortfolioManager.buy_stock/sell_stock`. Pre-check ensures player exists to determine game_id and raises HTTP 400 on validation errors (insufficient funds/shares). 【F:backend/api/main.py†L218-L261】

### 3.6 Event and News Endpoints
- `/games/{game_id}/events` GET lists recent `GameEvent` entries; `/event-templates` GET returns all available templates for manual triggering. 【F:backend/api/main.py†L263-L277】
- `/games/{game_id}/trigger-event` POST triggers a specific template, applies market effects, and invokes AI news generation for the resulting event. 【F:backend/api/main.py†L279-L296】
- `/games/{game_id}/news` GET fetches recent AI-generated news items. 【F:backend/api/main.py†L300-L305】

### 3.7 Dashboard Endpoint
- `/games/{game_id}/dashboard` GET aggregates a comprehensive snapshot: game info, rankings, recent events/news, and top movers computed from price deltas. 【F:backend/api/main.py†L307-L355】
- Root `/` returns metadata including link to interactive docs. 【F:backend/api/main.py†L357-L366】

## 4. Service Responsibilities
### 4.1 GameManager
- Maintains references to `PortfolioManager`, `EventSystem`, and `AINewsGenerator` to coordinate actions.
- `advance_quarter` workflow: apply random market fluctuation, optionally trigger probabilistic events (60% chance) and generate 3–6 pieces of sector news, refresh player valuations, advance quarter, and close completed games. 【F:backend/services/game_manager.py†L64-L118】
- Seeding utilities populate stocks on startup using `INITIAL_STOCKS`. 【F:backend/services/game_manager.py†L120-L133】

### 4.2 PortfolioManager
- Handles transactional integrity for buy/sell operations, updating holdings, cash balances, and recording `Transaction` entries per quarter. 【F:backend/services/portfolio_manager.py†L18-L118】
- Calculates and persists player portfolio valuations, aggregates rankings, and applies sector or global price adjustments while logging history to `StockPrice`. 【F:backend/services/portfolio_manager.py†L120-L215】

### 4.3 EventSystem & CausalityEngine
- Loads event templates from `EVENT_TEMPLATES` seed data with associated probabilities and impact multipliers. 【F:backend/services/event_system.py†L125-L166】
- `trigger_random_event` weights selection by template probability; `trigger_event` records `GameEvent`, derives cascading sector multipliers via `CausalityEngine.calculate_secondary_effects`, and calls `PortfolioManager.apply_sector_change` for each sector. 【F:backend/services/event_system.py†L57-L119】
- Causality rules encode sector relationships (strengthens, dependent_on) and adjust multipliers according to event type (breakthrough, crisis, regulation). 【F:backend/services/event_system.py†L9-L55】

### 4.4 AI News Generator
- Supports Anthropic or OpenAI clients when API keys are configured; otherwise falls back to deterministic template content. 【F:backend/services/ai_news_generator.py†L7-L46】
- Generates event-based news articles and ambient sector stories, tagging sentiment and sectors before persisting `NewsItem` records. 【F:backend/services/ai_news_generator.py†L48-L95】

## 5. Data Model Highlights
- **Game** tracks lifecycle fields (`status`, `current_quarter`, timestamps) and relationships to players/events/news. 【F:backend/models/database.py†L8-L24】
- **Player** stores cash and portfolio values plus relationships to holdings and transactions. 【F:backend/models/database.py†L26-L43】
- **Stock** defines sector, volatility, and associations to holdings/transactions/price history. 【F:backend/models/database.py†L45-L65】
- **Holding**, **Transaction**, **StockPrice** capture trading state and historical price changes per quarter. 【F:backend/models/database.py†L67-L117】
- **GameEvent** and **EventTemplate** store event metadata and multiplier maps; **NewsItem** stores generated stories with sentiment and sector tags. 【F:backend/models/database.py†L119-L173】
- Pydantic schemas in `backend/models/schemas.py` define request/response contracts for all resources, ensuring compatibility with FastAPI responses. 【F:backend/models/schemas.py†L1-L116】

## 6. Frontend Applications
### 6.1 Player Dashboard (`frontend/player/app.py`)
- Sidebar allows selecting game and player or registering a new player via `/players`. 【F:frontend/player/app.py†L20-L68】
- Provides metrics for portfolio value, cash, holdings, and total P/L, along with trading controls for each stock that invoke `/trades/buy` or `/trades/sell`. 【F:frontend/player/app.py†L70-L166】
- Additional tabs display holdings (data table and pie chart), latest news/events, and leaderboard with highlighted current player. 【F:frontend/player/app.py†L168-L256】

### 6.2 Game Master Console (`frontend/gamemaster/app.py`)
- Enables creating games, selecting active game, and controlling lifecycle (start/pause/resume/end, advance quarter). 【F:frontend/gamemaster/app.py†L28-L118】
- Player management tab adds players and visualizes rankings. 【F:frontend/gamemaster/app.py†L134-L189】
- Event tab lists templates and allows manual triggering; subsequent sections show recent events, market overview analytics, news feed, and aggregated dashboard data. 【F:frontend/gamemaster/app.py†L191-L310】

### 6.3 Public Dashboard (`frontend/dashboard/app.py`)
- Selects a game and consumes `/games/{id}/dashboard` to show overall status, leaderboard, market movers, sector performance, and recent events/news. 【F:frontend/dashboard/app.py†L22-L183】
- Provides additional analytical tabs for market analysis, player comparison, and event timeline visualizations, refreshing data on demand. 【F:frontend/dashboard/app.py†L185-L276】

## 7. Data Seeding and Initialization
- Startup seeds stocks and event templates from `backend/database/seed_data.py`, ensuring consistent initial universe of sectors and scenarios. 【F:backend/database/seed_data.py†L1-L166】
- Database tables auto-create via `init_db()` using SQLAlchemy metadata with SQLite (default) or configured database URL. 【F:backend/database/connection.py†L1-L32】

## 8. Configuration & Deployment Considerations
- Settings class allows overriding database connection, API host/port, AI provider, and initial cash via environment variables (`.env`). 【F:config/settings.py†L1-L34】
- Streamlit apps assume backend reachable at `http://localhost:8000`; scripts `run_backend.sh`, `run_player_frontend.sh`, etc., coordinate service startup (not modified by this specification).
- AI text generation requires valid API keys; without keys the system falls back to template narratives, ensuring gameplay continuity.

## 9. Game Loop Summary
1. **Setup** – Create game, register players, and seed stocks/events at startup.
2. **Activation** – Start game to set `status="active"` and quarter to 1.
3. **Quarter Progression** – Game master advances quarters, invoking market fluctuations, probabilistic events, AI news, and valuation updates.
4. **Player Interaction** – Players trade via Streamlit UI, impacting holdings and cash tracked in the database.
5. **Event & News Feedback** – Events adjust sector multipliers and spawn news items, influencing stock prices and player strategies.
6. **Completion** – Once `current_quarter > total_quarters`, `GameManager` marks the game `completed` and records `ended_at` timestamp. 【F:backend/services/game_manager.py†L96-L118】

This specification reflects the current repository implementation and should be updated alongside functional changes to maintain alignment.
