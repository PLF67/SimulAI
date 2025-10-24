"""Game Master frontend application"""
import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SimulAI - Game Master Control",
    page_icon="🎮",
    layout="wide"
)

def api_get(endpoint: str):
    """Make GET request to API"""
    try:
        response = httpx.get(f"{API_URL}{endpoint}", timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def api_post(endpoint: str, data: dict = None):
    """Make POST request to API"""
    try:
        response = httpx.post(f"{API_URL}{endpoint}", json=data or {}, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# Initialize session state
if 'game_id' not in st.session_state:
    st.session_state.game_id = None

# Header
st.title("🎮 Game Master Control Panel")
st.caption("Manage games, trigger events, and oversee all players")

# Sidebar - Game Selection/Creation
st.sidebar.title("Game Management")

# Create new game
with st.sidebar.expander("➕ Create New Game"):
    new_game_name = st.text_input("Game Name")
    total_quarters = st.number_input("Total Quarters", min_value=4, max_value=20, value=12)
    if st.button("Create Game"):
        result = api_post("/games", {
            "name": new_game_name,
            "total_quarters": total_quarters
        })
        if result:
            st.success("Game created!")
            st.rerun()

# Select existing game
games = api_get("/games")
if games:
    game_names = {game['name']: game['id'] for game in games}
    selected_game = st.sidebar.selectbox("Select Game", list(game_names.keys()))

    if selected_game:
        st.session_state.game_id = game_names[selected_game]

if not st.session_state.game_id:
    st.info("Please create or select a game from the sidebar.")
    st.stop()

# Get game data
game = api_get(f"/games/{st.session_state.game_id}")
if not game:
    st.error("Failed to load game data")
    st.stop()

# Game Status Display
st.sidebar.divider()
st.sidebar.subheader("Current Game Status")
st.sidebar.metric("Status", game['status'].upper())
st.sidebar.metric("Quarter", f"{game['current_quarter']}/{game['total_quarters']}")

# Game Controls
st.sidebar.divider()
st.sidebar.subheader("Game Controls")

col1, col2 = st.sidebar.columns(2)

with col1:
    if game['status'] == 'setup':
        if st.button("▶️ Start Game", use_container_width=True):
            result = api_post(f"/games/{st.session_state.game_id}/start")
            if result:
                st.success("Game started!")
                st.rerun()

    elif game['status'] == 'active':
        if st.button("⏸️ Pause", use_container_width=True):
            result = api_post(f"/games/{st.session_state.game_id}/pause")
            if result:
                st.success("Game paused!")
                st.rerun()

    elif game['status'] == 'paused':
        if st.button("▶️ Resume", use_container_width=True):
            result = api_post(f"/games/{st.session_state.game_id}/resume")
            if result:
                st.success("Game resumed!")
                st.rerun()

with col2:
    if game['status'] in ['active', 'paused']:
        if st.button("⏹️ End Game", use_container_width=True):
            result = api_post(f"/games/{st.session_state.game_id}/end")
            if result:
                st.success("Game ended!")
                st.rerun()

# Advance Quarter
if game['status'] == 'active' and game['current_quarter'] <= game['total_quarters']:
    st.sidebar.divider()
    st.sidebar.subheader("Quarter Management")

    trigger_events = st.sidebar.checkbox("Trigger random events", value=True)

    if st.sidebar.button("⏭️ Advance to Next Quarter", use_container_width=True, type="primary"):
        with st.spinner("Processing quarter..."):
            result = api_post(
                f"/games/{st.session_state.game_id}/advance-quarter",
                {"trigger_events": trigger_events}
            )
            if result:
                st.success("Quarter advanced!")
                st.rerun()

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👥 Players",
    "🎲 Events",
    "📊 Market Overview",
    "📰 News Feed",
    "📈 Analytics"
])

# TAB 1: Players
with tab1:
    st.subheader("Player Management")

    # Add new player
    with st.expander("➕ Add New Player"):
        col1, col2 = st.columns(2)
        with col1:
            player_name = st.text_input("Player Name")
        with col2:
            player_email = st.text_input("Player Email")

        if st.button("Add Player"):
            result = api_post("/players", {
                "name": player_name,
                "email": player_email,
                "game_id": st.session_state.game_id
            })
            if result:
                st.success("Player added!")
                st.rerun()

    st.divider()

    # Player list
    players = api_get(f"/games/{st.session_state.game_id}/players")
    rankings = api_get(f"/games/{st.session_state.game_id}/rankings")

    if rankings:
        df = pd.DataFrame(rankings)
        st.dataframe(
            df.style.format({
                'total_value': '${:.2f}',
                'cash': '${:.2f}',
                'holdings_value': '${:.2f}'
            }),
            use_container_width=True
        )

        # Player portfolios chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Cash',
            x=df['player_name'],
            y=df['cash'],
            marker_color='lightblue'
        ))
        fig.add_trace(go.Bar(
            name='Holdings',
            x=df['player_name'],
            y=df['holdings_value'],
            marker_color='darkblue'
        ))
        fig.update_layout(
            barmode='stack',
            title='Player Portfolio Breakdown',
            xaxis_title='Player',
            yaxis_title='Value ($)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players yet")

# TAB 2: Events
with tab2:
    st.subheader("Event Management")

    # Trigger manual event
    st.write("### Trigger Event")
    event_templates = api_get("/event-templates")

    if event_templates:
        # Display as cards
        for template in event_templates:
            with st.expander(f"{template['title']} ({template['event_type']})"):
                st.write(template['description'])
                st.write(f"**Affected Sectors:** {', '.join(template['affected_sectors'])}")
                st.write(f"**Probability:** {template['probability']:.0%}")

                # Impact multipliers
                st.write("**Impact Multipliers:**")
                for sector, multiplier in template['impact_multipliers'].items():
                    impact_pct = (multiplier - 1) * 100
                    st.write(f"- {sector}: {impact_pct:+.1f}%")

                if st.button(f"Trigger This Event", key=f"trigger_{template['id']}"):
                    result = api_post(
                        f"/games/{st.session_state.game_id}/trigger-event",
                        {"event_template_id": template['id']}
                    )
                    if result:
                        st.success("Event triggered!")
                        st.rerun()

    st.divider()

    # Recent events
    st.write("### Recent Events")
    events = api_get(f"/games/{st.session_state.game_id}/events")

    if events:
        for event in events:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Q{event['quarter_triggered']}: {event['title']}**")
                    st.caption(event['description'])
                    st.caption(f"Type: {event['event_type']} | Sectors: {', '.join(event['affected_sectors'])}")
                with col2:
                    st.caption(f"Triggered: {event['triggered_at'][:10]}")
                st.divider()
    else:
        st.info("No events triggered yet")

# TAB 3: Market Overview
with tab3:
    st.subheader("Market Overview")

    stocks = api_get("/stocks")
    if stocks:
        # Calculate performance metrics
        for stock in stocks:
            stock['change_pct'] = ((stock['current_price'] - stock.get('initial_price', stock['current_price'])) /
                                   stock.get('initial_price', stock['current_price'])) * 100

        df = pd.DataFrame(stocks)

        # Sector performance
        sector_perf = df.groupby('sector').agg({
            'change_pct': 'mean',
            'ticker': 'count'
        }).reset_index()
        sector_perf.columns = ['Sector', 'Avg Change %', 'Stock Count']

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Sector Performance")
            st.dataframe(
                sector_perf.style.format({
                    'Avg Change %': '{:.2f}%'
                }),
                use_container_width=True
            )

            # Sector chart
            fig = px.bar(
                sector_perf,
                x='Sector',
                y='Avg Change %',
                title='Average Sector Performance',
                color='Avg Change %',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("### All Stocks")
            st.dataframe(
                df[['ticker', 'company_name', 'sector', 'current_price', 'change_pct']].style.format({
                    'current_price': '${:.2f}',
                    'change_pct': '{:.2f}%'
                }),
                use_container_width=True
            )

# TAB 4: News Feed
with tab4:
    st.subheader("News Feed")

    news = api_get(f"/games/{st.session_state.game_id}/news")

    if news:
        for item in news:
            with st.container():
                # Sentiment color
                if item['sentiment'] == 'positive':
                    sentiment_color = '🟢'
                elif item['sentiment'] == 'negative':
                    sentiment_color = '🔴'
                else:
                    sentiment_color = '🟡'

                st.write(f"{sentiment_color} **Q{item['quarter']}: {item['title']}**")
                st.write(item['content'])
                st.caption(f"Type: {item['news_type']} | Sectors: {', '.join(item['related_sectors'])} | {item['created_at'][:10]}")
                st.divider()
    else:
        st.info("No news yet")

# TAB 5: Analytics
with tab5:
    st.subheader("Game Analytics")

    # Get dashboard data
    dashboard = api_get(f"/games/{st.session_state.game_id}/dashboard")

    if dashboard:
        col1, col2 = st.columns(2)

        with col1:
            st.write("### Top Gaining Stocks")
            if dashboard['top_gaining_stocks']:
                df = pd.DataFrame(dashboard['top_gaining_stocks'])
                st.dataframe(
                    df[['ticker', 'company_name', 'sector', 'price_change_percent']].style.format({
                        'price_change_percent': '{:.2f}%'
                    }),
                    use_container_width=True
                )

        with col2:
            st.write("### Top Losing Stocks")
            if dashboard['top_losing_stocks']:
                df = pd.DataFrame(dashboard['top_losing_stocks'])
                st.dataframe(
                    df[['ticker', 'company_name', 'sector', 'price_change_percent']].style.format({
                        'price_change_percent': '{:.2f}%'
                    }),
                    use_container_width=True
                )

        # Game statistics
        st.write("### Game Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Events", len(dashboard['recent_events']))
        with col2:
            st.metric("Total News", len(dashboard['recent_news']))
        with col3:
            st.metric("Active Players", len(dashboard['player_rankings']))

# Auto-refresh
if st.sidebar.checkbox("Auto-refresh (10s)"):
    import time
    time.sleep(10)
    st.rerun()
