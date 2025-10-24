"""Overall game dashboard with Material Design - Public view"""
import sys
sys.path.append('..')

import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from material_theme import apply_material_theme, MD_COLORS, get_sentiment_color

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SimulAI - Live Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Material Design theme
apply_material_theme()

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

# Header with Material Design
st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {MD_COLORS['primary']} 0%, {MD_COLORS['tertiary']} 100%);
        padding: 40px;
        border-radius: 16px;
        margin-bottom: 30px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h1 style="margin: 0; color: white; font-size: 2.5rem;">
            📊 SimulAI Business Game
        </h1>
        <p style="margin: 12px 0 0 0; font-size: 1.2rem; opacity: 0.9; color: white;">
            Live Dashboard - Real-time game statistics and leaderboards
        </p>
    </div>
""", unsafe_allow_html=True)

# Game Selection
games = api_get("/games")
if games:
    game_names = {game['name']: game['id'] for game in games}
    selected_game = st.selectbox("🎮 Select Game to View", list(game_names.keys()))

    if selected_game:
        st.session_state.game_id = game_names[selected_game]

if not st.session_state.game_id:
    st.markdown(f"""
        <div style="
            text-align: center;
            padding: 60px 20px;
            background-color: {MD_COLORS['surface_container']};
            border-radius: 16px;
            margin: 40px 0;
        ">
            <h2 style="color: {MD_COLORS['primary']};">Please select a game to view.</h2>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# Get dashboard data
dashboard = api_get(f"/games/{st.session_state.game_id}/dashboard")

if not dashboard:
    st.error("Failed to load dashboard data")
    st.stop()

game = dashboard['game']

# Game Status Bar with Material Design Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎮 Game Status", game['status'].upper())
with col2:
    st.metric("📅 Current Quarter", f"{game['current_quarter']}/{game['total_quarters']}")
with col3:
    st.metric("👥 Active Players", len(dashboard['player_rankings']))
with col4:
    progress = (game['current_quarter'] / game['total_quarters']) * 100
    st.metric("⏱️ Progress", f"{progress:.0f}%")

st.divider()

# Main Dashboard Layout
col_left, col_right = st.columns([2, 1])

with col_left:
    # Player Rankings
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            🏆 Leaderboard
        </h2>
    """, unsafe_allow_html=True)

    if dashboard['player_rankings']:
        rankings_df = pd.DataFrame(dashboard['player_rankings'])

        # Styled dataframe with gradient
        st.dataframe(
            rankings_df.style.format({
                'total_value': '${:,.2f}',
                'cash': '${:,.2f}',
                'holdings_value': '${:,.2f}'
            }).background_gradient(subset=['total_value'], cmap='RdYlGn'),
            use_container_width=True,
            height=350
        )

        # Rankings chart with Material Design colors
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Cash',
            x=rankings_df['player_name'],
            y=rankings_df['cash'],
            marker_color=MD_COLORS['success']
        ))

        fig.add_trace(go.Bar(
            name='Holdings',
            x=rankings_df['player_name'],
            y=rankings_df['holdings_value'],
            marker_color=MD_COLORS['primary']
        ))

        fig.update_layout(
            barmode='stack',
            title='Portfolio Composition by Player',
            xaxis_title='Player',
            yaxis_title='Value ($)',
            height=400,
            font_family="Roboto",
            paper_bgcolor=MD_COLORS['surface'],
            plot_bgcolor=MD_COLORS['surface']
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Market Performance
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            📈 Market Performance
        </h2>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.write("**🟢 Top Gainers**")
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
        st.write("**🔴 Top Losers**")
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
            height=350
        )
        fig.update_layout(
            font_family="Roboto",
            paper_bgcolor=MD_COLORS['surface'],
            plot_bgcolor=MD_COLORS['surface']
        )
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    # Recent Events with Material Design cards
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            🎲 Recent Events
        </h2>
    """, unsafe_allow_html=True)

    if dashboard['recent_events']:
        for event in dashboard['recent_events'][:5]:
            # Event type icon and color
            event_icons = {
                'breakthrough': '🚀',
                'crisis': '⚠️',
                'default': '📋'
            }
            event_colors = {
                'breakthrough': MD_COLORS['success'],
                'crisis': MD_COLORS['error'],
                'default': MD_COLORS['primary']
            }

            icon = event_icons.get(event['event_type'], event_icons['default'])
            border_color = event_colors.get(event['event_type'], event_colors['default'])

            st.markdown(f"""
                <div style="
                    background-color: {MD_COLORS['surface_container']};
                    border-left: 4px solid {border_color};
                    border-radius: 8px;
                    padding: 16px;
                    margin: 12px 0;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                ">
                    {icon} <strong style="font-size: 1rem; color: {MD_COLORS['on_surface']};">
                        Q{event['quarter_triggered']}: {event['title']}
                    </strong><br>
                    <p style="margin: 8px 0; font-size: 0.9rem; color: {MD_COLORS['on_surface_variant']};">
                        {event['description'][:150]}...
                    </p>
                    <span style="font-size: 0.75rem; color: {MD_COLORS['on_surface_variant']};">
                        Sectors: {', '.join(event['affected_sectors'][:3])}
                    </span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No events yet")

    st.divider()

    # Recent News with Material Design styling
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            📰 Latest News
        </h2>
    """, unsafe_allow_html=True)

    if dashboard['recent_news']:
        for news in dashboard['recent_news'][:5]:
            # Sentiment icon and color
            sentiment_emojis = {
                'positive': '🟢',
                'negative': '🔴',
                'neutral': '🟡'
            }
            sentiment_emoji = sentiment_emojis.get(news['sentiment'], '🟡')
            sentiment_color = get_sentiment_color(news['sentiment'])

            st.markdown(f"""
                <div style="
                    background-color: {MD_COLORS['surface_container']};
                    border-left: 4px solid {sentiment_color};
                    border-radius: 8px;
                    padding: 16px;
                    margin: 12px 0;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                ">
                    {sentiment_emoji} <strong style="font-size: 1rem; color: {MD_COLORS['on_surface']};">
                        {news['title']}
                    </strong><br>
                    <p style="margin: 8px 0; font-size: 0.9rem; color: {MD_COLORS['on_surface_variant']};">
                        {news['content'][:120]}...
                    </p>
                    <span style="font-size: 0.75rem; color: {MD_COLORS['on_surface_variant']};">
                        Q{news['quarter']} | {news['news_type']}
                    </span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No news yet")

# Bottom Section - Detailed Statistics
st.divider()
st.markdown(f"""
    <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
        📊 Detailed Statistics
    </h2>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Market Analysis", "👥 Player Comparison", "📜 Game History"])

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
            use_container_width=True,
            height=350
        )

        # Scatter plot with Material Design colors
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
        fig.update_layout(
            font_family="Roboto",
            paper_bgcolor=MD_COLORS['surface'],
            plot_bgcolor=MD_COLORS['surface']
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if dashboard['player_rankings']:
        st.write("### Player Performance Comparison")

        # Prepare data for comparison
        rankings_df = pd.DataFrame(dashboard['player_rankings'])

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
        fig.update_layout(
            font_family="Roboto",
            paper_bgcolor=MD_COLORS['surface'],
            plot_bgcolor=MD_COLORS['surface']
        )
        st.plotly_chart(fig, use_container_width=True)

        # Portfolio allocation
        col1, col2 = st.columns(2)

        with col1:
            st.write("#### 💵 Cash Distribution")
            fig = px.pie(
                rankings_df,
                values='cash',
                names='player_name',
                title='Cash by Player',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                font_family="Roboto",
                paper_bgcolor=MD_COLORS['surface']
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("#### 📈 Holdings Distribution")
            fig = px.pie(
                rankings_df,
                values='holdings_value',
                names='player_name',
                title='Holdings by Player',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(
                font_family="Roboto",
                paper_bgcolor=MD_COLORS['surface']
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
            use_container_width=True,
            height=300
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
        fig.update_layout(
            font_family="Roboto",
            paper_bgcolor=MD_COLORS['surface'],
            plot_bgcolor=MD_COLORS['surface']
        )
        fig.update_traces(
            line_color=MD_COLORS['primary'],
            marker=dict(size=10, color=MD_COLORS['secondary'])
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No event history yet")

# Footer with refresh button
st.divider()

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.rerun()

# Sidebar info with Material Design
st.sidebar.markdown(f"""
    <div style="
        background-color: {MD_COLORS['primary_container']};
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    ">
        <h3 style="color: {MD_COLORS['on_primary_container']}; margin-top: 0;">
            📊 Dashboard Info
        </h3>
        <p style="color: {MD_COLORS['on_primary_container']}; font-size: 0.9rem; line-height: 1.6;">
            This dashboard shows real-time statistics for the SimulAI business game.
        </p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style="
        background-color: {MD_COLORS['surface_container']};
        padding: 16px;
        border-radius: 8px;
    ">
        <h4 style="color: {MD_COLORS['on_surface']}; margin-top: 0;">
            Features
        </h4>
        <ul style="color: {MD_COLORS['on_surface_variant']}; font-size: 0.85rem; line-height: 1.8;">
            <li>Live leaderboard</li>
            <li>Market performance</li>
            <li>Recent events & news</li>
            <li>Detailed analytics</li>
        </ul>
        <p style="color: {MD_COLORS['on_surface_variant']}; font-size: 0.85rem; margin-bottom: 0;">
            The dashboard auto-refreshes to show the latest game state.
        </p>
    </div>
""", unsafe_allow_html=True)

# Auto-refresh toggle
st.sidebar.divider()
if st.sidebar.checkbox("🔄 Auto-refresh (15s)"):
    import time
    time.sleep(15)
    st.rerun()
