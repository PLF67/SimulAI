"""Player frontend application with Material Design"""
import sys
sys.path.append('..')

import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional
from material_theme import apply_material_theme, MD_COLORS, get_sentiment_color

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SimulAI - Player Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Material Design theme
apply_material_theme()

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
st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {MD_COLORS['primary']} 0%, {MD_COLORS['secondary']} 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: white;
    ">
        <h2 style="margin: 0; color: white;">🎮 Player Login</h2>
    </div>
""", unsafe_allow_html=True)

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
    if st.button("Register", use_container_width=True) and st.session_state.game_id:
        result = api_post("/players", {
            "name": new_name,
            "email": new_email,
            "game_id": st.session_state.game_id
        })
        if result:
            st.success("Player registered successfully!")
            st.rerun()

# Main Content
if not st.session_state.player_id:
    st.markdown(f"""
        <div style="
            text-align: center;
            padding: 60px 20px;
            background-color: {MD_COLORS['surface_container']};
            border-radius: 16px;
            margin: 40px 0;
        ">
            <h1 style="color: {MD_COLORS['primary']}; margin-bottom: 20px;">
                Welcome to SimulAI Business Game! 🎮
            </h1>
            <p style="font-size: 1.2rem; color: {MD_COLORS['on_surface_variant']};">
                Please select a game and player from the sidebar to continue.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# Get player data
player = api_get(f"/players/{st.session_state.player_id}")
game = api_get(f"/games/{st.session_state.game_id}")
portfolio = api_get(f"/players/{st.session_state.player_id}/portfolio")

if not player or not game or not portfolio:
    st.error("Failed to load player data")
    st.stop()

# Header
st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <h1 style="color: {MD_COLORS['on_surface']}; margin-bottom: 8px;">
            📊 {player['name']}'s Portfolio
        </h1>
        <p style="color: {MD_COLORS['on_surface_variant']}; font-size: 1rem;">
            Game: <strong>{game['name']}</strong> |
            Quarter: <strong>{game['current_quarter']}/{game['total_quarters']}</strong> |
            Status: <strong style="color: {MD_COLORS['primary']};">{game['status'].upper()}</strong>
        </p>
    </div>
""", unsafe_allow_html=True)

# Portfolio Overview - Material Design Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        "💰 Total Portfolio Value",
        f"${portfolio['total_portfolio_value']:,.2f}"
    )
with col2:
    st.metric(
        "💵 Cash Available",
        f"${portfolio['cash']:,.2f}"
    )
with col3:
    st.metric(
        "📈 Holdings Value",
        f"${portfolio['total_holdings_value']:,.2f}"
    )
with col4:
    initial_value = 100000.0
    profit_loss = portfolio['total_portfolio_value'] - initial_value
    profit_loss_pct = (profit_loss / initial_value) * 100
    st.metric(
        "🎯 Total P/L",
        f"${profit_loss:,.2f}",
        f"{profit_loss_pct:.2f}%"
    )

st.divider()

# Tabs with Material Design
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Trading",
    "💼 My Holdings",
    "📰 News & Events",
    "🏆 Rankings"
])

# TAB 1: Trading
with tab1:
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            Stock Market
        </h2>
    """, unsafe_allow_html=True)

    stocks = api_get("/stocks")
    if stocks:
        # Filters
        col1, col2 = st.columns([1, 3])
        with col1:
            sectors = sorted(list(set(stock['sector'] for stock in stocks)))
            selected_sector = st.selectbox("Filter by Sector", ["All"] + sectors)

        # Filter stocks
        if selected_sector != "All":
            filtered_stocks = [s for s in stocks if s['sector'] == selected_sector]
        else:
            filtered_stocks = stocks

        # Display stocks as Material Design cards
        for stock in filtered_stocks:
            st.markdown(f"""
                <div style="
                    background-color: {MD_COLORS['surface_container']};
                    border-radius: 12px;
                    padding: 20px;
                    margin: 12px 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
                    transition: box-shadow 0.3s cubic-bezier(.25,.8,.25,1);
                ">
            """, unsafe_allow_html=True)

            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])

            with col1:
                st.markdown(f"""
                    <strong style="font-size: 1.1rem; color: {MD_COLORS['primary']};">
                        {stock['ticker']}
                    </strong> - {stock['company_name']}<br>
                    <span style="color: {MD_COLORS['on_surface_variant']}; font-size: 0.85rem;">
                        {stock['sector']} | {stock['subsector'] or 'N/A'}
                    </span>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div style="font-size: 1.3rem; font-weight: 500; color: {MD_COLORS['primary']};">
                        ${stock['current_price']:.2f}
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.write("--")

            with col4:
                st.caption(stock['description'] or "")

            with col5:
                # Trading controls
                with st.popover("💹 Trade", use_container_width=True):
                    action = st.radio(
                        "Action",
                        ["Buy", "Sell"],
                        key=f"action_{stock['id']}"
                    )
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        value=10,
                        key=f"qty_{stock['id']}"
                    )

                    if action == "Buy":
                        total_cost = quantity * stock['current_price']
                        st.info(f"Total: ${total_cost:.2f}")

                        if st.button("Buy", key=f"buy_{stock['id']}", use_container_width=True):
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
                        st.info(f"Total: ${total_proceeds:.2f}")

                        if st.button("Sell", key=f"sell_{stock['id']}", use_container_width=True):
                            result = api_post("/trades/sell", {
                                "player_id": st.session_state.player_id,
                                "stock_id": stock['id'],
                                "quantity": quantity,
                                "transaction_type": "sell"
                            })
                            if result:
                                st.success(result['message'])
                                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# TAB 2: My Holdings
with tab2:
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            My Portfolio Holdings
        </h2>
    """, unsafe_allow_html=True)

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
            use_container_width=True,
            height=400
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Pie chart with Material Design colors
        fig = px.pie(
            holdings_df,
            values='total_value',
            names='stock_ticker',
            title='Portfolio Composition',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            font_family="Roboto",
            paper_bgcolor=MD_COLORS['surface'],
            plot_bgcolor=MD_COLORS['surface']
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("You don't have any holdings yet. Start trading to build your portfolio!")

# TAB 3: News & Events
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
            <h3 style="color: {MD_COLORS['on_surface']};">📰 Latest News</h3>
        """, unsafe_allow_html=True)

        news = api_get(f"/games/{st.session_state.game_id}/news")
        if news:
            for item in news[:5]:
                sentiment_color = get_sentiment_color(item['sentiment'])
                sentiment_emoji = '🟢' if item['sentiment'] == 'positive' else ('🔴' if item['sentiment'] == 'negative' else '🟡')

                with st.expander(f"{sentiment_emoji} Q{item['quarter']}: {item['title']}"):
                    st.markdown(f"""
                        <div style="
                            background-color: {MD_COLORS['surface_container']};
                            padding: 16px;
                            border-radius: 8px;
                            border-left: 4px solid {sentiment_color};
                        ">
                            <p>{item['content']}</p>
                            <p style="color: {MD_COLORS['on_surface_variant']}; font-size: 0.85rem;">
                                Type: <strong>{item['news_type']}</strong> |
                                Sentiment: <strong>{item['sentiment']}</strong><br>
                                Related sectors: {', '.join(item['related_sectors'])}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No news yet")

    with col2:
        st.markdown(f"""
            <h3 style="color: {MD_COLORS['on_surface']};">🎲 Game Events</h3>
        """, unsafe_allow_html=True)

        events = api_get(f"/games/{st.session_state.game_id}/events")
        if events:
            for event in events[:5]:
                event_icon = '🚀' if event['event_type'] == 'breakthrough' else ('⚠️' if event['event_type'] == 'crisis' else '📋')

                with st.expander(f"{event_icon} Q{event['quarter_triggered']}: {event['title']}"):
                    st.markdown(f"""
                        <div style="
                            background-color: {MD_COLORS['surface_container']};
                            padding: 16px;
                            border-radius: 8px;
                        ">
                            <p>{event['description']}</p>
                            <p style="color: {MD_COLORS['on_surface_variant']}; font-size: 0.85rem;">
                                Type: <strong>{event['event_type']}</strong><br>
                                Affected sectors: {', '.join(event['affected_sectors'])}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No events yet")

# TAB 4: Rankings
with tab4:
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            🏆 Player Rankings
        </h2>
    """, unsafe_allow_html=True)

    rankings = api_get(f"/games/{st.session_state.game_id}/rankings")

    if rankings:
        rankings_df = pd.DataFrame(rankings)

        # Highlight current player
        def highlight_player(row):
            if row['player_id'] == st.session_state.player_id:
                return [f'background-color: {MD_COLORS["primary_container"]}'] * len(row)
            return [''] * len(row)

        st.dataframe(
            rankings_df.style.apply(highlight_player, axis=1).format({
                'total_value': '${:.2f}',
                'cash': '${:.2f}',
                'holdings_value': '${:.2f}'
            }),
            use_container_width=True,
            height=400
        )

        # Bar chart with Material Design colors
        fig = px.bar(
            rankings_df,
            x='player_name',
            y='total_value',
            title='Portfolio Values by Player',
            color='total_value',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            font_family="Roboto",
            paper_bgcolor=MD_COLORS['surface'],
            plot_bgcolor=MD_COLORS['surface']
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No rankings yet")

# Auto-refresh option
if game['status'] == 'active':
    st.sidebar.divider()
    if st.sidebar.checkbox("🔄 Auto-refresh (30s)"):
        import time
        time.sleep(30)
        st.rerun()
