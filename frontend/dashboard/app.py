"""Overall game dashboard - Public view"""
import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SimulAI - Live Dashboard",
    page_icon="📊",
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

# Initialize session state
if 'game_id' not in st.session_state:
    st.session_state.game_id = None

# Header
st.title("📊 SimulAI Business Game - Live Dashboard")
st.caption("Real-time game statistics and leaderboards")

# Game Selection
games = api_get("/games")
if games:
    game_names = {game['name']: game['id'] for game in games}
    selected_game = st.selectbox("Select Game to View", list(game_names.keys()))

    if selected_game:
        st.session_state.game_id = game_names[selected_game]

if not st.session_state.game_id:
    st.info("Please select a game to view.")
    st.stop()

# Get dashboard data
dashboard = api_get(f"/games/{st.session_state.game_id}/dashboard")

if not dashboard:
    st.error("Failed to load dashboard data")
    st.stop()

game = dashboard['game']

# Game Status Bar
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Game Status", game['status'].upper())
with col2:
    st.metric("Current Quarter", f"{game['current_quarter']}/{game['total_quarters']}")
with col3:
    st.metric("Active Players", len(dashboard['player_rankings']))
with col4:
    progress = (game['current_quarter'] / game['total_quarters']) * 100
    st.metric("Progress", f"{progress:.0f}%")

st.divider()

# Main Dashboard Layout
col_left, col_right = st.columns([2, 1])

with col_left:
    # Player Rankings
    st.subheader("🏆 Leaderboard")

    if dashboard['player_rankings']:
        rankings_df = pd.DataFrame(dashboard['player_rankings'])

        # Styled dataframe
        st.dataframe(
            rankings_df.style.format({
                'total_value': '${:,.2f}',
                'cash': '${:,.2f}',
                'holdings_value': '${:,.2f}'
            }).background_gradient(subset=['total_value'], cmap='RdYlGn'),
            use_container_width=True,
            height=300
        )

        # Rankings chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Cash',
            x=rankings_df['player_name'],
            y=rankings_df['cash'],
            marker_color='lightgreen'
        ))

        fig.add_trace(go.Bar(
            name='Holdings',
            x=rankings_df['player_name'],
            y=rankings_df['holdings_value'],
            marker_color='darkgreen'
        ))

        fig.update_layout(
            barmode='stack',
            title='Portfolio Composition by Player',
            xaxis_title='Player',
            yaxis_title='Value ($)',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Market Performance
    st.subheader("📈 Market Performance")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Top Gainers**")
        if dashboard['top_gaining_stocks']:
            gainers_df = pd.DataFrame(dashboard['top_gaining_stocks'])
            st.dataframe(
                gainers_df[['ticker', 'company_name', 'price_change_percent']].style.format({
                    'price_change_percent': '{:.2f}%'
                }).background_gradient(subset=['price_change_percent'], cmap='Greens'),
                use_container_width=True,
                height=250
            )

    with col2:
        st.write("**Top Losers**")
        if dashboard['top_losing_stocks']:
            losers_df = pd.DataFrame(dashboard['top_losing_stocks'])
            st.dataframe(
                losers_df[['ticker', 'company_name', 'price_change_percent']].style.format({
                    'price_change_percent': '{:.2f}%'
                }).background_gradient(subset=['price_change_percent'], cmap='Reds_r'),
                use_container_width=True,
                height=250
            )

    # Sector heatmap
    stocks = api_get("/stocks")
    if stocks:
        for stock in stocks:
            stock['change_pct'] = ((stock['current_price'] - stock.get('initial_price', stock['current_price'])) /
                                   stock.get('initial_price', stock['current_price'])) * 100

        stocks_df = pd.DataFrame(stocks)

        # Sector performance
        sector_perf = stocks_df.groupby('sector')['change_pct'].mean().reset_index()
        sector_perf.columns = ['Sector', 'Avg Change %']

        fig = px.bar(
            sector_perf,
            x='Sector',
            y='Avg Change %',
            title='Sector Performance',
            color='Avg Change %',
            color_continuous_scale='RdYlGn',
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    # Recent Events
    st.subheader("🎲 Recent Events")

    if dashboard['recent_events']:
        for event in dashboard['recent_events'][:5]:
            # Event type icon
            if event['event_type'] == 'breakthrough':
                icon = '🚀'
            elif event['event_type'] == 'crisis':
                icon = '⚠️'
            else:
                icon = '📋'

            with st.container():
                st.write(f"{icon} **Q{event['quarter_triggered']}: {event['title']}**")
                st.caption(event['description'][:150] + "...")
                st.caption(f"Sectors: {', '.join(event['affected_sectors'][:3])}")
                st.divider()
    else:
        st.info("No events yet")

    st.divider()

    # Recent News
    st.subheader("📰 Latest News")

    if dashboard['recent_news']:
        for news in dashboard['recent_news'][:5]:
            # Sentiment icon
            if news['sentiment'] == 'positive':
                icon = '🟢'
            elif news['sentiment'] == 'negative':
                icon = '🔴'
            else:
                icon = '🟡'

            with st.container():
                st.write(f"{icon} **{news['title']}**")
                st.caption(news['content'][:120] + "...")
                st.caption(f"Q{news['quarter']} | {news['news_type']}")
                st.divider()
    else:
        st.info("No news yet")

# Bottom Section - Detailed Statistics
st.divider()
st.subheader("📊 Detailed Statistics")

tab1, tab2, tab3 = st.tabs(["Market Analysis", "Player Comparison", "Game History"])

with tab1:
    if stocks:
        st.write("### All Stocks")

        display_df = stocks_df[['ticker', 'company_name', 'sector', 'current_price', 'change_pct']].copy()
        display_df.columns = ['Ticker', 'Company', 'Sector', 'Current Price', 'Change %']

        st.dataframe(
            display_df.style.format({
                'Current Price': '${:.2f}',
                'Change %': '{:.2f}%'
            }).background_gradient(subset=['Change %'], cmap='RdYlGn'),
            use_container_width=True
        )

        # Scatter plot
        fig = px.scatter(
            stocks_df,
            x='sector',
            y='change_pct',
            size='current_price',
            color='sector',
            hover_data=['ticker', 'company_name'],
            title='Stock Performance by Sector',
            labels={'change_pct': 'Change %', 'sector': 'Sector'}
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if dashboard['player_rankings']:
        st.write("### Player Performance Comparison")

        # Prepare data for comparison
        rankings_df = pd.DataFrame(dashboard['player_rankings'])

        # Portfolio allocation chart
        fig = px.sunburst(
            rankings_df,
            path=['player_name'],
            values='total_value',
            title='Portfolio Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

        # ROI comparison
        initial_value = 100000.0  # From settings
        rankings_df['roi_pct'] = ((rankings_df['total_value'] - initial_value) / initial_value) * 100

        fig = px.bar(
            rankings_df,
            x='player_name',
            y='roi_pct',
            title='Return on Investment (ROI) by Player',
            color='roi_pct',
            color_continuous_scale='RdYlGn',
            labels={'roi_pct': 'ROI %', 'player_name': 'Player'}
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.write("### Event Timeline")

    events = api_get(f"/games/{st.session_state.game_id}/events")

    if events:
        events_df = pd.DataFrame(events)
        events_df['quarter'] = events_df['quarter_triggered']

        st.dataframe(
            events_df[['quarter', 'title', 'event_type', 'affected_sectors']],
            use_container_width=True
        )

        # Event timeline chart
        event_counts = events_df.groupby('quarter').size().reset_index(name='count')

        fig = px.line(
            event_counts,
            x='quarter',
            y='count',
            title='Events per Quarter',
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No event history yet")

# Footer with auto-refresh
st.divider()
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Auto-refresh toggle
if st.sidebar.checkbox("Auto-refresh (15s)"):
    import time
    time.sleep(15)
    st.rerun()

# Sidebar info
st.sidebar.title("📊 Dashboard Info")
st.sidebar.info("""
This dashboard shows real-time statistics for the SimulAI business game.

**Features:**
- Live leaderboard
- Market performance
- Recent events & news
- Detailed analytics

The dashboard auto-refreshes to show the latest game state.
""")
