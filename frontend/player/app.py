"""Player frontend application"""
import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SimulAI - Player Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'player_id' not in st.session_state:
    st.session_state.player_id = None
if 'game_id' not in st.session_state:
    st.session_state.game_id = None

def api_get(endpoint: str):
    """Make GET request to API"""
    try:
        response = httpx.get(f"{API_URL}{endpoint}", timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def api_post(endpoint: str, data: dict):
    """Make POST request to API"""
    try:
        response = httpx.post(f"{API_URL}{endpoint}", json=data, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# Sidebar - Player Selection
st.sidebar.title("🎮 Player Login")

games = api_get("/games")
if games:
    game_names = {game['name']: game['id'] for game in games}
    selected_game = st.sidebar.selectbox("Select Game", list(game_names.keys()))

    if selected_game:
        game_id = game_names[selected_game]
        st.session_state.game_id = game_id

        players = api_get(f"/games/{game_id}/players")
        if players:
            player_names = {player['name']: player['id'] for player in players}
            selected_player = st.sidebar.selectbox("Select Player", list(player_names.keys()))

            if selected_player:
                st.session_state.player_id = player_names[selected_player]

# New Player Registration
with st.sidebar.expander("📝 Register New Player"):
    new_name = st.text_input("Name")
    new_email = st.text_input("Email")
    if st.button("Register") and st.session_state.game_id:
        result = api_post("/players", {
            "name": new_name,
            "email": new_email,
            "game_id": st.session_state.game_id
        })
        if result:
            st.success("Player registered!")
            st.rerun()

# Main Content
if not st.session_state.player_id:
    st.title("Welcome to SimulAI Business Game! 🎮")
    st.info("Please select a game and player from the sidebar to continue.")
    st.stop()

# Get player data
player = api_get(f"/players/{st.session_state.player_id}")
game = api_get(f"/games/{st.session_state.game_id}")
portfolio = api_get(f"/players/{st.session_state.player_id}/portfolio")

if not player or not game or not portfolio:
    st.error("Failed to load player data")
    st.stop()

# Header
st.title(f"📊 {player['name']}'s Portfolio")
st.caption(f"Game: {game['name']} | Quarter: {game['current_quarter']}/{game['total_quarters']} | Status: {game['status']}")

# Portfolio Overview
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Portfolio Value", f"${portfolio['total_portfolio_value']:,.2f}")
with col2:
    st.metric("Cash Available", f"${portfolio['cash']:,.2f}")
with col3:
    st.metric("Holdings Value", f"${portfolio['total_holdings_value']:,.2f}")
with col4:
    initial_value = 100000.0  # From settings
    profit_loss = portfolio['total_portfolio_value'] - initial_value
    profit_loss_pct = (profit_loss / initial_value) * 100
    st.metric("Total P/L", f"${profit_loss:,.2f}", f"{profit_loss_pct:.2f}%")

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trading", "💼 My Holdings", "📰 News & Events", "🏆 Rankings"])

# TAB 1: Trading
with tab1:
    st.subheader("Stock Market")

    stocks = api_get("/stocks")
    if stocks:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            sectors = sorted(list(set(stock['sector'] for stock in stocks)))
            selected_sector = st.selectbox("Filter by Sector", ["All"] + sectors)

        # Filter stocks
        if selected_sector != "All":
            filtered_stocks = [s for s in stocks if s['sector'] == selected_sector]
        else:
            filtered_stocks = stocks

        # Display stocks
        for stock in filtered_stocks:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])

                with col1:
                    st.write(f"**{stock['ticker']}** - {stock['company_name']}")
                    st.caption(f"{stock['sector']} | {stock['subsector'] or 'N/A'}")

                with col2:
                    st.write(f"${stock['current_price']:.2f}")

                with col3:
                    # Calculate change from initial price
                    # We'll need to enhance this with actual historical data
                    st.write("--")

                with col4:
                    st.caption(stock['description'] or "")

                with col5:
                    # Trading controls
                    with st.popover("Trade"):
                        action = st.radio("Action", ["Buy", "Sell"], key=f"action_{stock['id']}")
                        quantity = st.number_input("Quantity", min_value=1, value=10, key=f"qty_{stock['id']}")

                        if action == "Buy":
                            total_cost = quantity * stock['current_price']
                            st.write(f"Total: ${total_cost:.2f}")

                            if st.button("Buy", key=f"buy_{stock['id']}"):
                                result = api_post("/trades/buy", {
                                    "player_id": st.session_state.player_id,
                                    "stock_id": stock['id'],
                                    "quantity": quantity,
                                    "transaction_type": "buy"
                                })
                                if result:
                                    st.success(result['message'])
                                    st.rerun()
                        else:
                            total_proceeds = quantity * stock['current_price']
                            st.write(f"Total: ${total_proceeds:.2f}")

                            if st.button("Sell", key=f"sell_{stock['id']}"):
                                result = api_post("/trades/sell", {
                                    "player_id": st.session_state.player_id,
                                    "stock_id": stock['id'],
                                    "quantity": quantity,
                                    "transaction_type": "sell"
                                })
                                if result:
                                    st.success(result['message'])
                                    st.rerun()

                st.divider()

# TAB 2: My Holdings
with tab2:
    st.subheader("My Portfolio Holdings")

    if portfolio['holdings']:
        holdings_df = pd.DataFrame(portfolio['holdings'])

        # Display as table
        st.dataframe(
            holdings_df.style.format({
                'average_buy_price': '${:.2f}',
                'current_price': '${:.2f}',
                'total_value': '${:.2f}',
                'profit_loss': '${:.2f}',
                'profit_loss_percent': '{:.2f}%'
            }),
            use_container_width=True
        )

        # Pie chart
        fig = px.pie(
            holdings_df,
            values='total_value',
            names='stock_ticker',
            title='Portfolio Composition'
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("You don't have any holdings yet. Start trading to build your portfolio!")

# TAB 3: News & Events
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📰 Latest News")
        news = api_get(f"/games/{st.session_state.game_id}/news")
        if news:
            for item in news[:5]:
                with st.expander(f"Q{item['quarter']}: {item['title']}"):
                    st.write(item['content'])
                    st.caption(f"Type: {item['news_type']} | Sentiment: {item['sentiment']}")
                    st.caption(f"Related sectors: {', '.join(item['related_sectors'])}")
        else:
            st.info("No news yet")

    with col2:
        st.subheader("🎲 Game Events")
        events = api_get(f"/games/{st.session_state.game_id}/events")
        if events:
            for event in events[:5]:
                with st.expander(f"Q{event['quarter_triggered']}: {event['title']}"):
                    st.write(event['description'])
                    st.caption(f"Type: {event['event_type']}")
                    st.caption(f"Affected sectors: {', '.join(event['affected_sectors'])}")
        else:
            st.info("No events yet")

# TAB 4: Rankings
with tab4:
    st.subheader("🏆 Player Rankings")
    rankings = api_get(f"/games/{st.session_state.game_id}/rankings")

    if rankings:
        rankings_df = pd.DataFrame(rankings)

        # Highlight current player
        def highlight_player(row):
            if row['player_id'] == st.session_state.player_id:
                return ['background-color: #90EE90'] * len(row)
            return [''] * len(row)

        st.dataframe(
            rankings_df.style.apply(highlight_player, axis=1).format({
                'total_value': '${:.2f}',
                'cash': '${:.2f}',
                'holdings_value': '${:.2f}'
            }),
            use_container_width=True
        )

        # Bar chart
        fig = px.bar(
            rankings_df,
            x='player_name',
            y='total_value',
            title='Portfolio Values by Player',
            color='total_value',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No rankings yet")

# Auto-refresh option
if game['status'] == 'active':
    if st.sidebar.checkbox("Auto-refresh (30s)"):
        import time
        time.sleep(30)
        st.rerun()
