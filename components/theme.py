"""Tema visual compartilhado por todas as páginas do FinanceOS."""

import streamlit as st


def aplicar_tema():
    st.markdown(
        """
        <style>
        :root { --blue:#3b82f6; --violet:#8b5cf6; --surface:rgba(19,28,48,.82); --border:rgba(148,163,184,.18); --text:#e6edf7; --muted:#94a3b8; }
        .stApp { background:radial-gradient(circle at 6% 10%,rgba(37,99,235,.12),transparent 25rem),radial-gradient(circle at 94% 75%,rgba(124,58,237,.11),transparent 26rem),#0b1120; color:var(--text); }
        [data-testid="stHeader"] { background:rgba(11,17,32,.75); }
        [data-testid="stMainBlockContainer"] { max-width:1440px; padding-top:2.4rem; }
        h1,h2,h3 { color:#f8fafc !important; letter-spacing:-.025em; } h1 { font-weight:780 !important; }
        [data-testid="stCaptionContainer"],.stCaption { color:var(--muted) !important; }

        [data-testid="stSidebar"] { background:linear-gradient(180deg,#101a31,#0b1120 78%); border-right:1px solid var(--border); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#b8c5da; }
        [data-testid="stSidebarNav"] a { margin:.12rem .5rem; border-radius:10px; transition:background .18s ease,transform .18s ease; }
        [data-testid="stSidebarNav"] a:hover { background:rgba(59,130,246,.16); transform:translateX(3px); }
        [data-testid="stSidebarNav"] a[aria-current="page"] { background:linear-gradient(100deg,rgba(37,99,235,.85),rgba(124,58,237,.78)); }

        [data-testid="stMetric"] { min-height:128px; padding:1.1rem 1.25rem; border:1px solid var(--border); border-radius:16px; background:linear-gradient(135deg,rgba(30,41,59,.82),rgba(15,23,42,.72)); box-shadow:0 12px 30px rgba(0,0,0,.14); transition:transform .2s ease,border-color .2s ease; }
        [data-testid="stMetric"]:hover { transform:translateY(-3px); border-color:rgba(96,165,250,.5); }
        [data-testid="stMetricLabel"] { color:#aebcd1; } [data-testid="stMetricValue"] { color:#f8fafc; font-weight:760; }
        .finance-kpi { position:relative; overflow:hidden; min-height:132px; margin-bottom:.6rem; padding:1.2rem; border:1px solid rgba(148,163,184,.2); border-radius:16px; background:linear-gradient(135deg,rgba(30,41,59,.88),rgba(15,23,42,.82)); box-shadow:0 12px 30px rgba(0,0,0,.15); transition:transform .2s ease,border-color .2s ease; }
        .finance-kpi::after { content:""; position:absolute; width:100px; height:100px; right:-35px; bottom:-40px; border-radius:50%; background:var(--accent); opacity:.17; }
        .finance-kpi:hover { transform:translateY(-3px); border-color:var(--accent); }
        .finance-kpi__title { color:#cbd5e1; font-size:.92rem; font-weight:650; }
        .finance-kpi__value { margin-top:.65rem; color:#fff; font-size:2rem; font-weight:780; letter-spacing:-.04em; }

        [data-testid="stVerticalBlockBorderWrapper"],div[data-testid="stForm"],[data-testid="stExpander"] { border:1px solid var(--border) !important; border-radius:16px !important; background:rgba(15,23,42,.62) !important; box-shadow:0 10px 28px rgba(0,0,0,.12); }
        [data-testid="stVerticalBlockBorderWrapper"] { transition:transform .2s ease,border-color .2s ease; }
        [data-testid="stVerticalBlockBorderWrapper"]:hover { transform:translateY(-2px); border-color:rgba(96,165,250,.35) !important; }
        div[data-testid="stForm"] { padding:1.35rem !important; }
        [data-testid="stExpander"] summary { padding:.35rem .15rem; font-weight:650; }

        [data-testid="stWidgetLabel"] p { color:#cbd5e1; font-size:.86rem; font-weight:620; }
        [data-baseweb="input"] > div,[data-baseweb="select"] > div,[data-testid="stDateInput"] input,[data-testid="stTextArea"] textarea { border:1px solid rgba(148,163,184,.24) !important; border-radius:10px !important; background:rgba(30,41,59,.72) !important; color:#f8fafc !important; }
        [data-baseweb="input"] > div:focus-within,[data-baseweb="select"] > div:focus-within { border-color:var(--blue) !important; box-shadow:0 0 0 3px rgba(59,130,246,.15) !important; }

        .stButton > button,[data-testid="stFormSubmitButton"] > button { min-height:2.55rem; border:1px solid rgba(96,165,250,.5) !important; border-radius:10px !important; background:linear-gradient(100deg,#2563eb,#4f46e5) !important; color:#fff !important; font-weight:700 !important; box-shadow:0 8px 18px rgba(37,99,235,.2); transition:transform .18s ease,filter .18s ease; }
        .stButton > button:hover,[data-testid="stFormSubmitButton"] > button:hover { transform:translateY(-2px); filter:brightness(1.12); }
        .stButton > button[kind="secondary"] { background:rgba(30,41,59,.85) !important; }
        [data-testid="stAlert"] { border-radius:12px; border:1px solid var(--border); }
        [data-testid="stDataFrame"],[data-testid="stTable"] { border:1px solid var(--border); border-radius:14px; overflow:hidden; }
        hr { border-color:var(--border) !important; }
        [data-testid="stPlotlyChart"] { padding:.6rem; border:1px solid var(--border); border-radius:16px; background:rgba(15,23,42,.45); }
        /* Layout mobile-first: cada grupo de colunas vira uma sequência vertical. */
        @media (max-width: 768px) {
            [data-testid="stMainBlockContainer"] { padding:1.15rem .9rem 2.5rem; }
            [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; gap:.8rem !important; }
            [data-testid="stColumn"], [data-testid="column"] { min-width:100% !important; flex:1 1 100% !important; }
            [data-testid="stMetric"] { min-height:96px; padding:.9rem 1rem; }
            .finance-kpi { min-height:108px; padding:1rem; }
            .finance-kpi__value { font-size:1.7rem; }
            h1 { font-size:1.85rem !important; } h2 { font-size:1.4rem !important; } h3 { font-size:1.12rem !important; }
            .hero { padding:1.45rem !important; border-radius:16px !important; margin-bottom:1.4rem !important; }
            .hero h1 { font-size:2rem !important; } .hero p { font-size:1rem !important; }
            .card { min-height:auto !important; height:auto !important; padding:1.15rem !important; }
            .numero { font-size:2rem !important; }
            .saldo-card { padding:1.35rem !important; border-radius:16px !important; }
            .big-money { font-size:2.15rem !important; overflow-wrap:anywhere; }
            .credit-card { min-height:auto !important; padding:1.35rem !important; }
            .card-title { font-size:1.55rem !important; } .card-number { font-size:1.1rem !important; letter-spacing:3px !important; }
            [data-testid="stPlotlyChart"] { padding:.15rem; border-radius:12px; }
            [data-testid="stPlotlyChart"] > div { min-height:280px !important; }
            div[data-testid="stForm"] { padding:1rem !important; border-radius:14px !important; }
            .stButton > button, [data-testid="stFormSubmitButton"] > button { min-height:3rem; font-size:.98rem; }
            [data-testid="stDataFrame"] { overflow-x:auto; }
            [data-testid="stSidebar"] { min-width:min(82vw, 320px) !important; }
        }

        @media (max-width: 420px) {
            [data-testid="stMainBlockContainer"] { padding-left:.7rem; padding-right:.7rem; }
            h1 { font-size:1.6rem !important; }
            .hero { padding:1.15rem !important; } .hero h1 { font-size:1.65rem !important; }
            .big-money { font-size:1.8rem !important; }
            [data-testid="stMetricValue"] { font-size:1.45rem !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
