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

# ---------- One chart style for the whole app ----------
_axis = dict(showgrid=True, gridcolor=COLORS["rule"], zeroline=False,
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
    margin=dict(l=8, r=8, t=36, b=8),
    hoverlabel=dict(bgcolor="white", bordercolor=COLORS["rule"],
                    font=dict(family=BODY_FONT, size=12, color=COLORS["ink"])),
))
pio.templates["lab"] = LAB
pio.templates.default = "lab"

def show(fig):
    st.plotly_chart(fig, use_container_width=True, theme=None)

# ---------- Page styling ----------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:wght@400;500;600&display=swap');
:root {--paper:#F5F6F4; --surface:#FFFFFF; --ink:#1B2430; --muted:#5B6672; --rule:#DDE1E5; --accent:#1F5F5B;}
html, body, .stApp, [data-testid="stAppViewContainer"] {background: var(--paper);}
html, body, .stApp, p, li, label, button, input, textarea, th, td,
[data-baseweb="tab"], [data-testid="stMarkdownContainer"] {
    font-family: 'IBM Plex Sans', system-ui, sans-serif; color: var(--ink);}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Newsreader', Georgia, serif !important; font-weight: 500 !important;
    letter-spacing: -0.01em; color: var(--ink) !important;}
.stApp h3 {font-size: 1.4rem !important; margin-top: 1.6rem;}
[data-testid="stMarkdownContainer"] p {max-width: 72ch; line-height: 1.6;}
.block-container {max-width: 1180px; padding-top: 2.5rem; padding-bottom: 3rem;}
#MainMenu, footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"] {border-right: 1px solid var(--rule);}
.brand {font-family: 'Newsreader', Georgia, serif; font-size: 1.5rem; font-weight: 500; line-height: 1.2;}
.brand-sub {color: var(--muted); font-size: 0.85rem; margin: 4px 0 18px 0;}

.masthead {border-bottom: 1px solid var(--rule); padding-bottom: 14px; margin-bottom: 22px;}
.masthead h1 {font-family: 'Newsreader', Georgia, serif; font-weight: 500; font-size: 2.5rem;
    letter-spacing: -0.02em; margin: 0 0 6px 0; padding: 0; color: var(--ink);}
.masthead p {color: var(--muted); margin: 0; max-width: 70ch;}

.stat-strip {display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    border-top: 2px solid var(--ink); margin: 6px 0 26px 0;}
.stat {padding: 14px 20px 6px 0;}
.stat + .stat {border-left: 1px solid var(--rule); padding-left: 20px;}
.stat-label {color: var(--muted); font-size: 0.85rem;}
.stat-value {font-family: 'Newsreader', Georgia, serif; font-size: 1.85rem; line-height: 1.25;
    font-variant-numeric: tabular-nums;}
.stat-note {color: var(--muted); font-size: 0.85rem; font-variant-numeric: tabular-nums;}
@media (max-width: 640px) {.stat + .stat {border-left: none; padding-left: 0;}}

.note {border-left: 3px solid var(--accent); padding: 4px 0 4px 18px; margin: 14px 0 26px 0; max-width: 78ch;}
.note-title {font-weight: 600; margin-bottom: 4px;}
.note ul {margin: 6px 0 0 18px; padding: 0;}
.note li {margin: 5px 0; line-height: 1.55;}
.note p {margin: 4px 0 0 0;}

.stTabs [data-baseweb="tab-list"] {gap: 28px; border-bottom: 1px solid var(--rule);}
.stTabs [data-baseweb="tab"] {height: auto; padding: 10px 2px; background: transparent;}
.stTabs [data-baseweb="tab-highlight"] {background-color: var(--accent); height: 2px;}
.stTabs [data-baseweb="tab-border"] {display: none;}

[data-testid="stFormSubmitButton"] button {background: var(--accent); color: #FFFFFF; border: 0; border-radius: 4px;}
[data-testid="stFormSubmitButton"] button p {color: #FFFFFF;}
[data-testid="stFormSubmitButton"] button:hover {background: #174A47;}
.stDownloadButton button {background: transparent; border: 1px solid var(--rule); border-radius: 4px;}
[data-testid="stExpander"] {border: 1px solid var(--rule); border-radius: 4px; background: var(--surface);}
table {border-collapse: collapse; width: 100%; font-size: 0.93rem;}
th {text-align: left; font-weight: 600; border-bottom: 2px solid var(--ink); padding: 8px 10px;}
td {border-bottom: 1px solid var(--rule); padding: 8px 10px; vertical-align: top;}
.foot {border-top: 1px solid var(--rule); margin-top: 40px; padding-top: 14px; color: var(--muted); font-size: 0.85rem;}
"""

def inject_css():
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)

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

def footer():
    st.markdown('<div class="foot">Developed by Anant Aravind Pillai. Data from Yahoo Finance '
                '(daily closing prices). Educational project, not investment advice.</div>',
                unsafe_allow_html=True)