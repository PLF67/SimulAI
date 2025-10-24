"""Game Master frontend application with Material Design"""
import sys
sys.path.append('..')

import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from material_theme import apply_material_theme, MD_COLORS, get_status_color

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SimulAI - Game Master Control",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
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
st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {MD_COLORS['primary']} 0%, {MD_COLORS['tertiary']} 100%);
        padding: 30px;
        border-radius: 16px;
        margin-bottom: 30px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h1 style="margin: 0; color: white;">🎮 Game Master Control Panel</h1>
        <p style="margin: 8px 0 0 0; opacity: 0.9; color: white;">
            Manage games, trigger events, and oversee all players
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar - Game Selection/Creation
st.sidebar.markdown(f"""
    <div style="
        background-color: {MD_COLORS['primary_container']};
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 20px;
    ">
        <h3 style="margin: 0; color: {MD_COLORS['on_primary_container']};">
            Game Management
        </h3>
    </div>
""", unsafe_allow_html=True)

# Create new game
with st.sidebar.expander("➕ Create New Game"):
    new_game_name = st.text_input("Game Name")
    total_quarters = st.number_input("Total Quarters", min_value=4, max_value=20, value=12)
    if st.button("Create Game", use_container_width=True):
        result = api_post("/games", {
            "name": new_game_name,
            "total_quarters": total_quarters
        })
        if result:
            st.success("Game created successfully!")
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
status_color = get_status_color(game['status'])

st.sidebar.markdown(f"""
    <div style="
        background-color: {MD_COLORS['surface_container']};
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
    ">
        <h4 style="margin: 0 0 12px 0; color: {MD_COLORS['on_surface']};">
            Current Game Status
        </h4>
        <div style="
            background-color: {status_color};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-align: center;
            font-weight: 500;
            margin-bottom: 8px;
        ">
            {game['status'].upper()}
        </div>
        <div style="
            text-align: center;
            font-size: 1.5rem;
            font-weight: 500;
            color: {MD_COLORS['primary']};
        ">
            Quarter {game['current_quarter']}/{game['total_quarters']}
        </div>
    </div>
""", unsafe_allow_html=True)

# Game Controls
st.sidebar.divider()
st.sidebar.subheader("⚙️ Game Controls")

col1, col2 = st.sidebar.columns(2)

with col1:
    if game['status'] == 'setup':
        if st.button("▶️ Start", use_container_width=True):
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
        if st.button("⏹️ End", use_container_width=True):
            result = api_post(f"/games/{st.session_state.game_id}/end")
            if result:
                st.success("Game ended!")
                st.rerun()

# Advance Quarter
if game['status'] == 'active' and game['current_quarter'] <= game['total_quarters']:
    st.sidebar.divider()
    st.sidebar.subheader("📅 Quarter Management")

    trigger_events = st.sidebar.checkbox("Trigger random events", value=True)

    if st.sidebar.button("⏭️ Advance Quarter", use_container_width=True, type="primary"):
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
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            Player Management
        </h2>
    """, unsafe_allow_html=True)

    # Add new player
    with st.expander("➕ Add New Player"):
        col1, col2 = st.columns(2)
        with col1:
            player_name = st.text_input("Player Name")
        with col2:
            player_email = st.text_input("Player Email")

        if st.button("Add Player", use_container_width=True):
            result = api_post("/players", {
                "name": player_name,
                "email": player_email,
                "game_id": st.session_state.game_id
            })
            if result:
                st.success("Player added successfully!")
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
            }).background_gradient(subset=['total_value'], cmap='RdYlGn'),
            use_container_width=True,
            height=350
        )

        # Player portfolios chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Cash',
            x=df['player_name'],
            y=df['cash'],
            marker_color=MD_COLORS['success']
        ))
        fig.add_trace(go.Bar(
            name='Holdings',
            x=df['player_name'],
            y=df['holdings_value'],
            marker_color=MD_COLORS['primary']
        ))
        fig.update_layout(
            barmode='stack',
            title='Player Portfolio Breakdown',
            xaxis_title='Player',
            yaxis_title='Value ($)',
            font_family="Roboto",
            paper_bgcolor=MD_COLORS['surface'],
            plot_bgcolor=MD_COLORS['surface']
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players yet")

# TAB 2: Events
with tab2:
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            Event Management
        </h2>
    """, unsafe_allow_html=True)

    # Trigger manual event
    st.write("### 🎯 Trigger Event")
    event_templates = api_get("/event-templates")

    if event_templates:
        # Display as Material Design cards
        for template in event_templates:
            st.markdown(f"""
                <div style="
                    background-color: {MD_COLORS['surface_container']};
                    border-radius: 12px;
                    padding: 20px;
                    margin: 12px 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
                ">
            """, unsafe_allow_html=True)

            with st.expander(f"{template['title']} ({template['event_type']})"):
                st.write(template['description'])
                st.write(f"**Affected Sectors:** {', '.join(template['affected_sectors'])}")
                st.write(f"**Probability:** {template['probability']:.0%}")

                # Impact multipliers
                st.write("**Impact Multipliers:**")
                for sector, multiplier in template['impact_multipliers'].items():
                    impact_pct = (multiplier - 1) * 100
                    color = MD_COLORS['success'] if impact_pct > 0 else MD_COLORS['error']
                    st.markdown(f"""
                        <div style="color: {color}; font-weight: 500;">
                            • {sector}: {impact_pct:+.1f}%
                        </div>
                    """, unsafe_allow_html=True)

                if st.button(f"Trigger This Event", key=f"trigger_{template['id']}", use_container_width=True):
                    result = api_post(
                        f"/games/{st.session_state.game_id}/trigger-event",
                        {"event_template_id": template['id']}
                    )
                    if result:
                        st.success("Event triggered!")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Recent events
    st.write("### 📜 Recent Events")
    events = api_get(f"/games/{st.session_state.game_id}/events")

    if events:
        for event in events:
            event_type_colors = {
                'breakthrough': MD_COLORS['success'],
                'crisis': MD_COLORS['error'],
                'default': MD_COLORS['primary']
            }
            border_color = event_type_colors.get(event['event_type'], event_type_colors['default'])

            st.markdown(f"""
                <div style="
                    background-color: {MD_COLORS['surface_container']};
                    border-left: 4px solid {border_color};
                    border-radius: 8px;
                    padding: 16px;
                    margin: 12px 0;
                ">
                    <strong style="font-size: 1.1rem; color: {MD_COLORS['on_surface']};">
                        Q{event['quarter_triggered']}: {event['title']}
                    </strong><br>
                    <p style="margin: 8px 0; color: {MD_COLORS['on_surface_variant']};">
                        {event['description']}
                    </p>
                    <span style="font-size: 0.85rem; color: {MD_COLORS['on_surface_variant']};">
                        Type: <strong>{event['event_type']}</strong> |
                        Sectors: {', '.join(event['affected_sectors'])} |
                        {event['triggered_at'][:10]}
                    </span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No events triggered yet")

# TAB 3: Market Overview
with tab3:
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            Market Overview
        </h2>
    """, unsafe_allow_html=True)

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
            st.write("### 📊 Sector Performance")
            st.dataframe(
                sector_perf.style.format({
                    'Avg Change %': '{:.2f}%'
                }).background_gradient(subset=['Avg Change %'], cmap='RdYlGn'),
                use_container_width=True,
                height=300
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
            fig.update_layout(
                font_family="Roboto",
                paper_bgcolor=MD_COLORS['surface'],
                plot_bgcolor=MD_COLORS['surface']
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("### 📋 All Stocks")
            st.dataframe(
                df[['ticker', 'company_name', 'sector', 'current_price', 'change_pct']].style.format({
                    'current_price': '${:.2f}',
                    'change_pct': '{:.2f}%'
                }).background_gradient(subset=['change_pct'], cmap='RdYlGn'),
                use_container_width=True,
                height=400
            )

# TAB 4: News Feed
with tab4:
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            News Feed
        </h2>
    """, unsafe_allow_html=True)

    news = api_get(f"/games/{st.session_state.game_id}/news")

    if news:
        for item in news:
            # Sentiment color
            sentiment_colors = {
                'positive': MD_COLORS['success'],
                'negative': MD_COLORS['error'],
                'neutral': MD_COLORS['warning']
            }
            sentiment_color = sentiment_colors.get(item['sentiment'], MD_COLORS['primary'])
            sentiment_emoji = '🟢' if item['sentiment'] == 'positive' else ('🔴' if item['sentiment'] == 'negative' else '🟡')

            st.markdown(f"""
                <div style="
                    background-color: {MD_COLORS['surface_container']};
                    border-left: 4px solid {sentiment_color};
                    border-radius: 8px;
                    padding: 16px;
                    margin: 12px 0;
                ">
                    {sentiment_emoji} <strong style="font-size: 1.1rem; color: {MD_COLORS['on_surface']};">
                        Q{item['quarter']}: {item['title']}
                    </strong><br>
                    <p style="margin: 8px 0; color: {MD_COLORS['on_surface']};">
                        {item['content']}
                    </p>
                    <span style="font-size: 0.85rem; color: {MD_COLORS['on_surface_variant']};">
                        Type: <strong>{item['news_type']}</strong> |
                        Sectors: {', '.join(item['related_sectors'])} |
                        {item['created_at'][:10]}
                    </span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No news yet")

# TAB 5: Analytics
with tab5:
    st.markdown(f"""
        <h2 style="color: {MD_COLORS['on_surface']}; margin-bottom: 20px;">
            Game Analytics
        </h2>
    """, unsafe_allow_html=True)

    # Get dashboard data
    dashboard = api_get(f"/games/{st.session_state.game_id}/dashboard")

    if dashboard:
        col1, col2 = st.columns(2)

        with col1:
            st.write("### 📈 Top Gaining Stocks")
            if dashboard['top_gaining_stocks']:
                df = pd.DataFrame(dashboard['top_gaining_stocks'])
                st.dataframe(
                    df[['ticker', 'company_name', 'sector', 'price_change_percent']].style.format({
                        'price_change_percent': '{:.2f}%'
                    }).background_gradient(subset=['price_change_percent'], cmap='Greens'),
                    use_container_width=True,
                    height=300
                )

        with col2:
            st.write("### 📉 Top Losing Stocks")
            if dashboard['top_losing_stocks']:
                df = pd.DataFrame(dashboard['top_losing_stocks'])
                st.dataframe(
                    df[['ticker', 'company_name', 'sector', 'price_change_percent']].style.format({
                        'price_change_percent': '{:.2f}%'
                    }).background_gradient(subset=['price_change_percent'], cmap='Reds_r'),
                    use_container_width=True,
                    height=300
                )

        # Game statistics with Material Design cards
        st.write("### 📊 Game Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🎲 Total Events", len(dashboard['recent_events']))
        with col2:
            st.metric("📰 Total News", len(dashboard['recent_news']))
        with col3:
            st.metric("👥 Active Players", len(dashboard['player_rankings']))

# Auto-refresh
st.sidebar.divider()
if st.sidebar.checkbox("🔄 Auto-refresh (10s)"):
    import time
    time.sleep(10)
    st.rerun()
