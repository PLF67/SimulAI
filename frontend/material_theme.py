"""Material Design 3 theme for SimulAI Streamlit apps"""
import streamlit as st

# Material Design 3 Color Palette (based on Material You)
MD_COLORS = {
    # Primary colors
    'primary': '#6750A4',
    'on_primary': '#FFFFFF',
    'primary_container': '#EADDFF',
    'on_primary_container': '#21005D',

    # Secondary colors
    'secondary': '#625B71',
    'on_secondary': '#FFFFFF',
    'secondary_container': '#E8DEF8',
    'on_secondary_container': '#1D192B',

    # Tertiary colors
    'tertiary': '#7D5260',
    'on_tertiary': '#FFFFFF',
    'tertiary_container': '#FFD8E4',
    'on_tertiary_container': '#31111D',

    # Error colors
    'error': '#B3261E',
    'on_error': '#FFFFFF',
    'error_container': '#F9DEDC',
    'on_error_container': '#410E0B',

    # Success colors
    'success': '#2E7D32',
    'on_success': '#FFFFFF',
    'success_container': '#C8E6C9',

    # Warning colors
    'warning': '#F57C00',
    'on_warning': '#FFFFFF',
    'warning_container': '#FFE0B2',

    # Background colors
    'surface': '#FFFBFE',
    'on_surface': '#1C1B1F',
    'surface_variant': '#E7E0EC',
    'on_surface_variant': '#49454F',
    'outline': '#79747E',
    'outline_variant': '#CAC4D0',

    # Surface container levels
    'surface_container_lowest': '#FFFFFF',
    'surface_container_low': '#F7F2FA',
    'surface_container': '#F3EDF7',
    'surface_container_high': '#ECE6F0',
    'surface_container_highest': '#E6E0E9',
}

def apply_material_theme():
    """Apply Material Design 3 theme to Streamlit app"""
    st.markdown(f"""
    <style>
        /* Import Material Symbols font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');

        /* Root variables */
        :root {{
            --md-sys-color-primary: {MD_COLORS['primary']};
            --md-sys-color-on-primary: {MD_COLORS['on_primary']};
            --md-sys-color-primary-container: {MD_COLORS['primary_container']};
            --md-sys-color-secondary: {MD_COLORS['secondary']};
            --md-sys-color-surface: {MD_COLORS['surface']};
            --md-sys-color-surface-variant: {MD_COLORS['surface_variant']};
            --md-sys-color-outline: {MD_COLORS['outline']};
        }}

        /* Global styles */
        html, body, [class*="css"] {{
            font-family: 'Roboto', sans-serif;
        }}

        /* Main container */
        .stApp {{
            background-color: {MD_COLORS['surface']};
        }}

        /* Headers with Material Design typography */
        h1 {{
            font-family: 'Roboto', sans-serif;
            font-weight: 400;
            font-size: 2.5rem;
            line-height: 3rem;
            letter-spacing: 0;
            color: {MD_COLORS['on_surface']};
        }}

        h2 {{
            font-family: 'Roboto', sans-serif;
            font-weight: 400;
            font-size: 2rem;
            line-height: 2.5rem;
            color: {MD_COLORS['on_surface']};
        }}

        h3 {{
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
            font-size: 1.5rem;
            line-height: 2rem;
            color: {MD_COLORS['on_surface']};
        }}

        /* Streamlit metric cards */
        [data-testid="stMetricValue"] {{
            font-size: 2rem;
            font-weight: 500;
            color: {MD_COLORS['primary']};
        }}

        [data-testid="stMetric"] {{
            background-color: {MD_COLORS['surface_container']};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }}

        /* Buttons - Material Design Filled */
        .stButton > button {{
            background-color: {MD_COLORS['primary']};
            color: {MD_COLORS['on_primary']};
            border: none;
            border-radius: 20px;
            padding: 10px 24px;
            font-weight: 500;
            font-size: 0.875rem;
            letter-spacing: 0.1px;
            text-transform: none;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            transition: all 0.3s cubic-bezier(.25,.8,.25,1);
        }}

        .stButton > button:hover {{
            box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
            background-color: {MD_COLORS['primary']};
            transform: translateY(-1px);
        }}

        .stButton > button:active {{
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            transform: translateY(0);
        }}

        /* Input fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div {{
            border: 1px solid {MD_COLORS['outline']};
            border-radius: 4px;
            padding: 12px;
            font-size: 1rem;
            background-color: {MD_COLORS['surface']};
            color: {MD_COLORS['on_surface']};
        }}

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {{
            border-color: {MD_COLORS['primary']};
            border-width: 2px;
            outline: none;
        }}

        /* Selectbox */
        .stSelectbox [data-baseweb="select"] {{
            background-color: {MD_COLORS['surface_container']};
            border-radius: 4px;
        }}

        /* Tabs - Material Design style */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
            background-color: {MD_COLORS['surface']};
            border-bottom: 1px solid {MD_COLORS['outline_variant']};
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 48px;
            border-radius: 0;
            padding: 0 16px;
            color: {MD_COLORS['on_surface_variant']};
            font-weight: 500;
            background-color: transparent;
            border: none;
        }}

        .stTabs [aria-selected="true"] {{
            color: {MD_COLORS['primary']};
            border-bottom: 3px solid {MD_COLORS['primary']};
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {MD_COLORS['surface_container_low']};
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: {MD_COLORS['on_surface']};
        }}

        /* Expander - Material Design elevation */
        .streamlit-expanderHeader {{
            background-color: {MD_COLORS['surface_container']};
            border-radius: 8px;
            border: 1px solid {MD_COLORS['outline_variant']};
            font-weight: 500;
            color: {MD_COLORS['on_surface']};
        }}

        .streamlit-expanderHeader:hover {{
            background-color: {MD_COLORS['surface_container_high']};
        }}

        /* Dataframe */
        .stDataFrame {{
            border: 1px solid {MD_COLORS['outline_variant']};
            border-radius: 8px;
            overflow: hidden;
        }}

        /* Info/Success/Warning/Error boxes */
        .stAlert {{
            border-radius: 8px;
            padding: 16px;
            border: none;
        }}

        [data-baseweb="notification"] {{
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        /* Success alert */
        .stSuccess {{
            background-color: {MD_COLORS['success_container']};
            color: {MD_COLORS['on_surface']};
        }}

        /* Error alert */
        .stError {{
            background-color: {MD_COLORS['error_container']};
            color: {MD_COLORS['on_error_container']};
        }}

        /* Warning alert */
        .stWarning {{
            background-color: {MD_COLORS['warning_container']};
            color: {MD_COLORS['on_surface']};
        }}

        /* Info alert */
        .stInfo {{
            background-color: {MD_COLORS['primary_container']};
            color: {MD_COLORS['on_primary_container']};
        }}

        /* Divider */
        hr {{
            border: none;
            height: 1px;
            background-color: {MD_COLORS['outline_variant']};
            margin: 2rem 0;
        }}

        /* Container with elevation */
        .element-container {{
            background-color: {MD_COLORS['surface']};
        }}

        /* Plotly charts */
        .js-plotly-plot .plotly {{
            border-radius: 8px;
        }}

        /* Radio buttons */
        .stRadio > div {{
            background-color: {MD_COLORS['surface_container']};
            border-radius: 8px;
            padding: 8px;
        }}

        /* Checkbox */
        .stCheckbox {{
            background-color: transparent;
        }}

        /* Card-like containers */
        .card {{
            background-color: {MD_COLORS['surface_container']};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            margin: 10px 0;
        }}

        .card:hover {{
            box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
        }}

        /* Caption text */
        .caption {{
            color: {MD_COLORS['on_surface_variant']};
            font-size: 0.75rem;
            font-weight: 400;
            letter-spacing: 0.4px;
        }}
    </style>
    """, unsafe_allow_html=True)

def create_material_card(title, content, color='surface_container'):
    """Create a Material Design card component"""
    bg_color = MD_COLORS.get(color, MD_COLORS['surface_container'])

    card_html = f"""
    <div style="
        background-color: {bg_color};
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        margin: 10px 0;
        transition: box-shadow 0.3s cubic-bezier(.25,.8,.25,1);
    ">
        <h3 style="margin-top: 0; color: {MD_COLORS['on_surface']};">{title}</h3>
        <div style="color: {MD_COLORS['on_surface_variant']};">
            {content}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def create_elevated_container(content_func):
    """Create an elevated container for content"""
    with st.container():
        st.markdown("""
        <div style="
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 4px 8px rgba(0,0,0,0.1);
            margin: 16px 0;
        ">
        """, unsafe_allow_html=True)
        content_func()
        st.markdown("</div>", unsafe_allow_html=True)

def material_icon(icon_name, size=24):
    """Insert a Material Design icon"""
    return f'<span class="material-symbols-outlined" style="font-size: {size}px; vertical-align: middle;">{icon_name}</span>'

def get_sentiment_color(sentiment):
    """Get Material Design color for sentiment"""
    if sentiment == 'positive':
        return MD_COLORS['success']
    elif sentiment == 'negative':
        return MD_COLORS['error']
    else:
        return MD_COLORS['warning']

def get_status_color(status):
    """Get Material Design color for game status"""
    status_colors = {
        'setup': MD_COLORS['warning'],
        'active': MD_COLORS['success'],
        'paused': MD_COLORS['warning'],
        'completed': MD_COLORS['primary'],
    }
    return status_colors.get(status, MD_COLORS['outline'])
