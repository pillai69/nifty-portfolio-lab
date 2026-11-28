import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

COLORS = {
    "paper": "#F5F6F4", "surface": "#FFFFFF", "ink": "#1B2430", "muted": "#5B6672",
    "rule": "#DDE1E5", "accent": "#1F5F5B", "blue": "#3B5B8C", "amber": "#C26A2E",
    "gray": "#5E6B78", "pos": "#1E7B4F", "neg": "#B3402E",
}
STRATEGY_COLORS = {
    "Max Sharpe": COLORS["accent"], "Min Variance": COLORS["blue"],
    "Equal Weight": COLORS["amber"], "Nifty 50 Index": COLORS["gray"],
}
BODY_FONT = "IBM Plex Sans, system-ui, sans-serif"
LINKEDIN = "https://www.linkedin.com/in/pillaianant/"
GITHUB = "https://github.com/pillai69"
REPO = "https://github.com/pillai69/nifty-portfolio-lab"

# ---------- One chart style for the whole app ----------
_axis = dict(showgrid=True, gridcolor=COLORS["rule"], zeroline=False, automargin=True,
             linecolor=COLORS["rule"], ticks="outside", tickcolor=COLORS["rule"],
             tickfont=dict(size=12, color=COLORS["muted"]),
             title=dict(font=dict(size=12, color=COLORS["muted"])))

LAB = go.layout.Template(layout=dict(
    font=dict(family=BODY_FONT, size=13, color=COLORS["ink"]),
    colorway=["#1F5F5B", "#C26A2E", "#3B5B8C", "#8A7A3A", "#7A4E78", "#4F8A6B",
              "#A33B3B", "#5E6B78", "#2F7F9E", "#B08A3E"],
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=_axis, yaxis=_axis,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                title=dict(text=""), font=dict(size=12)),
    margin=dict(l=8, r=8, t=44, b=8),
    hoverlabel=dict(bgcolor="white", bordercolor=COLORS["rule"],
                    font=dict(family=BODY_FONT, size=12, color=COLORS["ink"])),
    transition=dict(duration=400, easing="cubic-in-out"),
))
pio.templates["lab"] = LAB
pio.templates.default = "lab"

def show(fig):
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})

def range_buttons(fig):
    # 6M / 1Y / 3Y / All buttons on the top right of a time-series chart
    fig.update_xaxes(rangeselector=dict(
        buttons=[dict(count=6, label="6M", step="month", stepmode="backward"),
                 dict(count=1, label="1Y", step="year", stepmode="backward"),
                 dict(count=3, label="3Y", step="year", stepmode="backward"),
                 dict(step="all", label="All")],
        x=1, xanchor="right", y=1.02, yanchor="bottom",
        bgcolor="rgba(0,0,0,0)", activecolor=COLORS["rule"], bordercolor=COLORS["rule"],
        borderwidth=1, font=dict(size=12, color=COLORS["ink"])))

# ---------- Page styling ----------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:wght@400;500;600&display=swap');
:root {--paper:#F5F6F4; --surface:#FFFFFF; --ink:#1B2430; --muted:#5B6672; --rule:#DDE1E5;
       --accent:#1F5F5B; --pos:#1E7B4F; --neg:#B3402E;}
html {scroll-behavior: smooth;}

/* Background: flat and quiet */
.stApp {background-color: var(--paper); background-image: none;}
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main {background: transparent !important;}
header[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {display: none;}
#MainMenu, footer {visibility: hidden;}
.block-container {max-width: 1180px; padding-top: 0.6rem; padding-bottom: 3rem;}

/* Type */
html, body, .stApp, p, li, label, button, input, textarea, th, td,
[data-baseweb="tab"], [data-testid="stMarkdownContainer"] {
    font-family: 'IBM Plex Sans', system-ui, sans-serif; color: var(--ink);}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Newsreader', Georgia, serif !important; font-weight: 500 !important;
    letter-spacing: -0.01em; color: var(--ink) !important;}
.stApp h3 {font-size: 1.3rem !important; margin-top: 1.6rem;}
[data-testid="stMarkdownContainer"] p {max-width: 72ch; line-height: 1.6;}

/* Navbar */
/* The wrapper around the navbar is what has to stick, because it is a direct child of the page */
[data-testid="stLayoutWrapper"]:has(> .st-key-navbar) {position: sticky; top: 0; z-index: 100; background: var(--paper);}
.st-key-navbar {margin: 10px 0 22px 0; padding: 10px 22px;
    background: rgba(255,255,255,0.78); -webkit-backdrop-filter: blur(16px) saturate(150%);
    backdrop-filter: blur(16px) saturate(150%); border: 1px solid var(--rule); border-radius: 12px;
    box-shadow: none; animation: drop 0.6s cubic-bezier(.2,.7,.2,1) both;}
.st-key-navbar [data-testid="stHorizontalBlock"] {flex-wrap: nowrap !important; align-items: center; gap: 1.8rem;}
.st-key-navbar [data-testid="stColumn"] {flex: 0 0 auto !important; width: auto !important; min-width: 0 !important;}
.nav-brand {font-family: 'Newsreader', Georgia, serif; font-size: 1.45rem; font-weight: 500;
    letter-spacing: -0.01em; white-space: nowrap; transition: color 0.25s ease; height: 24px; line-height: 24px;}
.nav-brand:hover {color: var(--accent);}
.nav-brand .short {display: none;}
.st-key-navbar a[data-testid="stPageLink-NavLink"] {
    background: linear-gradient(var(--accent), var(--accent)) left bottom / 0 2px no-repeat !important;
    border-radius: 0; padding: 0; min-height: 24px; transition: background-size 0.35s cubic-bezier(.2,.7,.2,1);}
.st-key-navbar a[data-testid="stPageLink-NavLink"] p {color: var(--muted); font-weight: 500;
    transition: color 0.25s ease;}
.st-key-navbar a[data-testid="stPageLink-NavLink"]:hover {background-size: 100% 2px !important;}
.st-key-navbar a[data-testid="stPageLink-NavLink"]:hover p {color: var(--ink);}
.nav-right {text-align: right; white-space: nowrap; height: 24px; line-height: 24px;}
.nav-right a {color: var(--muted); text-decoration: none; font-size: 0.95rem; font-weight: 500; display: inline-block; height: 24px; line-height: 24px;
    background: linear-gradient(var(--accent), var(--accent)) left bottom / 0 2px no-repeat;
    transition: background-size 0.35s cubic-bezier(.2,.7,.2,1), color 0.25s ease;}
.nav-right a:hover {color: var(--ink); background-size: 100% 2px;}
.nav-right a + a {margin-left: 22px;}
.st-key-navbar label p {font-size: 0.9rem; color: var(--muted); white-space: nowrap;}
.st-key-navbar p {margin: 0 !important; line-height: 1.3;}
.st-key-navbar [data-testid="stMarkdownContainer"] {margin-bottom: 0 !important;}
@media (max-width: 760px) {
    .st-key-navbar {padding: 8px 14px;}
    .st-key-navbar [data-testid="stHorizontalBlock"] {gap: 0.9rem;}
    .st-key-navbar label p {display: none;}
    .nav-brand {font-size: 1.15rem;}
    .nav-brand .long {display: none;}
    .nav-brand .short {display: inline;}
}

/* Masthead, key figures, notes */
.masthead {border-bottom: 1px solid var(--rule); padding-bottom: 14px; margin-bottom: 20px;}
.masthead h1 {font-family: 'Newsreader', Georgia, serif; font-weight: 500; font-size: 2.3rem;
    letter-spacing: -0.02em; margin: 0 0 6px 0; padding: 0; color: var(--ink);}
.masthead p {color: var(--muted); margin: 0; max-width: 70ch;}
.stat-strip {display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    border-top: 1px solid var(--ink); margin: 6px 0 26px 0;}
.stat {position: relative; padding: 14px 20px 10px 0;}
.stat + .stat {border-left: 1px solid var(--rule); padding-left: 20px;}
.stat::after {content: ""; position: absolute; left: 0; bottom: 0; height: 2px; width: 0; background: var(--accent);
    transition: width 0.4s cubic-bezier(.2,.7,.2,1);}
.stat + .stat::after {left: 20px;}
.stat:hover::after {width: calc(100% - 20px);}
.stat-label {color: var(--muted); font-size: 0.85rem;}
.stat-value {font-family: 'Newsreader', Georgia, serif; font-size: 1.85rem; line-height: 1.25;
    font-variant-numeric: tabular-nums; transition: color 0.25s ease;}
.stat:hover .stat-value {color: var(--accent);}
.stat-note {color: var(--muted); font-size: 0.85rem; font-variant-numeric: tabular-nums;}
@media (max-width: 640px) {.stat + .stat {border-left: none; padding-left: 0;} .stat + .stat::after {left: 0;}}
.note {border-left: 3px solid var(--accent); padding: 8px 0 8px 18px; margin: 14px 0 26px 0; max-width: 78ch;}
.note-title {font-weight: 600; margin-bottom: 4px;}
.note ul {margin: 6px 0 0 18px; padding: 0;}
.note li {margin: 5px 0; line-height: 1.55;}
.note p {margin: 4px 0 0 0;}

/* Ticker tape */
.tape {display: flex; align-items: stretch; background: transparent; border: 1px solid var(--rule);
    border-radius: 4px; overflow: hidden; margin: 0 0 22px 0;}
.tape-label {flex: none; display: flex; align-items: center; padding: 9px 16px; color: var(--muted);
    border-right: 1px solid var(--rule); font-size: 0.82rem; font-weight: 500; white-space: nowrap;}
.tape-window {flex: 1; overflow: hidden;
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 4%, #000 96%, transparent);
    mask-image: linear-gradient(90deg, transparent, #000 4%, #000 96%, transparent);}
.tape-track {display: inline-flex; white-space: nowrap; animation: tape 40s linear infinite; will-change: transform;}
.tape-window:hover .tape-track {animation-play-state: paused;}
.tk {display: inline-flex; gap: 10px; padding: 9px 22px; border-right: 1px solid var(--rule);
    font-size: 0.9rem; font-variant-numeric: tabular-nums;}
.tk b {font-weight: 600;} .tk-px {color: var(--muted);} .up {color: var(--pos);} .down {color: var(--neg);}
@keyframes tape {from {transform: translateX(0);} to {transform: translateX(-50%);}}

/* Tabs, panels, controls */
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"] {
    transition: border-color 0.2s ease, box-shadow 0.2s ease;}
[data-baseweb="select"] > div:focus-within, [data-baseweb="input"]:focus-within {
    border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(31,95,91,0.18);}
.stTabs [data-baseweb="tab-list"] {gap: 28px; border-bottom: 1px solid var(--rule);}
.stTabs [data-baseweb="tab"] {height: auto; padding: 10px 2px; background: transparent; transition: color 0.2s ease;}
.stTabs [data-baseweb="tab-highlight"] {background-color: var(--accent); height: 2px;}
.stTabs [data-baseweb="tab-border"] {display: none;}
.stTabs [data-baseweb="tab-panel"] {animation: fade 0.45s ease both;}
[data-testid="stPlotlyChart"] {background: transparent; border: 0; padding: 0;}
[data-testid="stDataFrame"] {border: 1px solid var(--rule); border-radius: 6px; overflow: hidden;}
[data-testid="stExpander"] {border: 1px solid var(--rule); border-radius: 6px; background: transparent;}
[data-testid="stFormSubmitButton"] button, .stDownloadButton button {
    border-radius: 4px; transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.2s ease, border-color 0.2s ease;}
[data-testid="stFormSubmitButton"] button {background: var(--accent); color: #FFFFFF; border: 0;}
[data-testid="stFormSubmitButton"] button p {color: #FFFFFF;}
[data-testid="stFormSubmitButton"] button:hover {background: #174A47; transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(31,95,91,0.28);}
.stDownloadButton button {background: transparent; border: 1px solid var(--rule);}
.stDownloadButton button:hover {border-color: var(--accent); transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(27,36,48,0.10);}
[data-testid="stChatMessage"] {background: transparent; border-bottom: 1px solid var(--rule); border-radius: 0; padding: 1.1rem 0;}
[data-testid="stChatMessage"] p {max-width: 78ch;}
table {border-collapse: collapse; width: 100%; font-size: 0.93rem;}
th {text-align: left; font-weight: 600; border-bottom: 2px solid var(--ink); padding: 8px 10px;}
td {border-bottom: 1px solid var(--rule); padding: 8px 10px; vertical-align: top;}
.foot {border-top: 1px solid var(--rule); margin-top: 40px; padding-top: 14px; color: var(--muted); font-size: 0.85rem;}

/* One entrance sequence on load, then everything stays still */
@keyframes rise {from {opacity: 0; transform: translateY(10px);} to {opacity: 1; transform: none;}}
@keyframes fade {from {opacity: 0;} to {opacity: 1;}}
@keyframes drop {from {opacity: 0; transform: translateY(-8px);} to {opacity: 1; transform: none;}}
.masthead {animation: rise 0.6s cubic-bezier(.2,.7,.2,1) both;}
.tape {animation: rise 0.6s cubic-bezier(.2,.7,.2,1) 0.08s both;}
.stat-strip {animation: rise 0.6s cubic-bezier(.2,.7,.2,1) 0.16s both;}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {animation: none !important; transition: none !important;}
    html {scroll-behavior: auto;}
}
"""

# Dark mode works by inverting the light design, so pure white here becomes pure black.
DARK_CSS = "html {background-color: #FFFFFF; filter: invert(1) hue-rotate(180deg);} .stApp {background-color: #FFFFFF;}"
LIGHT_CSS = "html {filter: none;}"

def init_theme():
    # Dark is the default. Only an explicit ?theme=light link starts in light mode.
    if "dark" not in st.session_state:
        st.session_state["dark"] = st.query_params.get("theme", "dark") != "light"

def inject_css():
    extra = DARK_CSS if st.session_state.get("dark", False) else LIGHT_CSS
    # No fade on the very first paint; the fade is only for switching modes afterwards
    move = ("html {transition: filter 0.5s ease, background-color 0.5s ease;}"
            if st.session_state.get("css_seen") else "html {transition: none;}")
    st.session_state["css_seen"] = True
    st.markdown("<style>" + CSS + move + extra + "</style>", unsafe_allow_html=True)

def navbar(pages, current):
    n = len(pages)
    active = [p.title for p in pages].index(current.title) + 2   # column number of the current page
    spacer, links = n + 2, n + 3
    link = f'.st-key-navbar [data-testid="stColumn"]:nth-child({active}) a[data-testid="stPageLink-NavLink"]'
    col = '.st-key-navbar [data-testid="stColumn"]'
    st.markdown(
        f'<style>{col}:nth-child({spacer}) {{flex: 1 1 auto !important;}}'
        f'{link} {{background-size: 100% 2px !important;}}'
        f'{link} p {{color: var(--ink);}}'
        f'@media (max-width: 760px) {{{col}:nth-child({spacer}), {col}:nth-child({links}) '
        f'{{display: none !important;}} {col}:nth-child({n + 1}) {{margin-right: auto;}}'
        f'.st-key-navbar [data-testid="stHorizontalBlock"] {{gap: 0.7rem;}}}}</style>',
        unsafe_allow_html=True)
    with st.container(key="navbar"):
        cols = st.columns(n + 4, vertical_alignment="center")
        cols[0].markdown('<div class="nav-brand"><span class="long">Nifty Portfolio Lab</span>'
                         '<span class="short">Nifty Lab</span></div>', unsafe_allow_html=True)
        for c, page in zip(cols[1:n + 1], pages):
            c.page_link(page, label=page.title)
        cols[n + 2].markdown(
            f'<div class="nav-right"><a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>'
            f'<a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a></div>',
            unsafe_allow_html=True)
        cols[n + 3].toggle("Dark mode", key="dark")
    st.query_params["theme"] = "dark" if st.session_state.get("dark") else "light"

def masthead(title, subtitle):
    st.markdown(f'<div class="masthead"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def stat_strip(items):
    cells = "".join(
        f'<div class="stat"><div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div><div class="stat-note">{sub}</div></div>'
        for label, value, sub in items)
    st.markdown(f'<div class="stat-strip">{cells}</div>', unsafe_allow_html=True)

def note(title, items, bullets=True):
    if bullets:
        body = "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    else:
        body = "<p>" + items[0] + "</p>"
    st.markdown(f'<div class="note"><div class="note-title">{title}</div>{body}</div>',
                unsafe_allow_html=True)

def ticker(prices):
    # Scrolling tape: last close and one-day change for each selected stock
    if len(prices) < 2:
        return
    last, prev = prices.iloc[-1], prices.iloc[-2]
    chg = last / prev - 1
    one = "".join(
        f'<span class="tk"><b>{n}</b><span class="tk-px">{last[n]:,.2f}</span>'
        f'<span class="{"up" if chg[n] >= 0 else "down"}">{chg[n]:+.2%}</span></span>'
        for n in prices.columns)
    dur = max(30, 5 * len(prices.columns))
    st.markdown(
        f'<style>.tape-track{{animation-duration:{dur}s;}}</style>'
        f'<div class="tape"><div class="tape-label">Last close, {prices.index[-1]:%d %b}</div>'
        f'<div class="tape-window"><div class="tape-track">{one}{one}</div></div></div>',
        unsafe_allow_html=True)

def footer():
    st.markdown('<div class="foot">Developed by Anant Aravind Pillai. Data from Yahoo Finance '
                '(daily closing prices). Educational project, not investment advice.</div>',
                unsafe_allow_html=True)