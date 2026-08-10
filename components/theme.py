"""Tema visual compartilhado por todas as páginas do FinanceOS."""

from base64 import b64encode
from html import escape

import streamlit as st
import streamlit.components.v1 as components

from config import ADMIN_USER, SESSION_TIMEOUT_MINUTES


def aplicar_tema():
    st.markdown(
        """
        <style>
        :root { color-scheme:dark; --blue:#3b82f6; --violet:#8b5cf6; --surface:rgba(19,28,48,.82); --surface-strong:#121c31; --border:rgba(148,163,184,.18); --border-strong:rgba(148,163,184,.30); --text:#e6edf7; --muted:#94a3b8; --space-1:.5rem; --space-2:.75rem; --space-3:1rem; --space-4:1.5rem; --space-5:2rem; }
        html { min-height:100%; background:#0b1120; -webkit-text-size-adjust:100%; text-size-adjust:100%; }
        body { min-height:100vh; min-height:100dvh; overscroll-behavior-y:none; -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; }
        button,a,input,textarea,select,[role="button"] { touch-action:manipulation; }
        .stApp { background:radial-gradient(circle at 6% 10%,rgba(37,99,235,.12),transparent 25rem),radial-gradient(circle at 94% 75%,rgba(124,58,237,.11),transparent 26rem),#0b1120; color:var(--text); font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }
        [data-testid="stHeader"] { background:rgba(11,17,32,.75); }
        [data-testid="stMainBlockContainer"] { max-width:1440px; padding-top:2.4rem; padding-bottom:3.25rem; }
        [data-testid="stVerticalBlock"] { gap:var(--space-3); }
        h1,h2,h3 { color:#f8fafc !important; letter-spacing:-.025em; line-height:1.15; } h1 { font-weight:780 !important; } h2 { font-weight:740 !important; margin-top:var(--space-5) !important; } h3 { font-weight:700 !important; }
        [data-testid="stCaptionContainer"],.stCaption { color:var(--muted) !important; }
        hr { margin:var(--space-5) 0 !important; }

        [data-testid="stSidebar"] { background:linear-gradient(180deg,#101a31,#0b1120 78%); border-right:1px solid var(--border); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#b8c5da; }
        [data-testid="stSidebarNav"] a { margin:.14rem .5rem; padding:.48rem .65rem; border-radius:10px; color:#cbd5e1 !important; transition:background .18s ease,transform .18s ease,color .18s ease; }
        /* app.py permanece como entrada técnica; na interface ele é a Início. */
        [data-testid="stSidebarNav"] li:first-child a { font-size:0 !important; }
        [data-testid="stSidebarNav"] li:first-child a * { display:none !important; }
        [data-testid="stSidebarNav"] li:first-child a::after { content:"Início"; display:block; font-size:.875rem; font-weight:600; }
        /* O Streamlit sempre lista app.py primeiro; o Perfil é a entrada pessoal
           e deve abrir a navegação. */
        [data-testid="stSidebarNav"] ul { display:flex; flex-direction:column; }
        [data-testid="stSidebarNav"] li:has(a[href*="Perfil"]) { order:-1; }
        [data-testid="stSidebarNav"] li:has(a[href*="Perfil"]) { display:none; }
        [data-testid="stSidebarNav"] ul { padding-top:3.25rem; }
        [data-testid="stSidebarNav"] a:hover { background:rgba(59,130,246,.16); transform:translateX(3px); }
        [data-testid="stSidebarNav"] a[aria-current="page"] { background:linear-gradient(100deg,rgba(37,99,235,.85),rgba(124,58,237,.78)); }

        [data-testid="stMetric"] { position:relative; overflow:hidden; min-height:124px; padding:1.1rem 1.25rem; border:1px solid var(--border); border-radius:16px; background:linear-gradient(135deg,rgba(30,41,59,.82),rgba(15,23,42,.72)); box-shadow:0 12px 30px rgba(0,0,0,.14); transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease; }
        [data-testid="stMetric"]::after { content:""; position:absolute; right:-2.7rem; bottom:-3.3rem; width:8rem; height:8rem; border-radius:50%; background:rgba(59,130,246,.09); }
        [data-testid="stMetric"]:hover { transform:translateY(-3px); border-color:rgba(96,165,250,.5); box-shadow:0 16px 34px rgba(0,0,0,.2); }
        [data-testid="stMetricLabel"] { color:#aebcd1; } [data-testid="stMetricValue"] { color:#f8fafc; font-weight:760; }
        .finance-kpi { position:relative; overflow:hidden; min-height:132px; margin-bottom:.6rem; padding:1.2rem; border:1px solid rgba(148,163,184,.2); border-radius:16px; background:linear-gradient(135deg,rgba(30,41,59,.88),rgba(15,23,42,.82)); box-shadow:0 12px 30px rgba(0,0,0,.15); transition:transform .2s ease,border-color .2s ease; }
        .finance-kpi::after { content:""; position:absolute; width:100px; height:100px; right:-35px; bottom:-40px; border-radius:50%; background:var(--accent); opacity:.17; }
        .finance-kpi:hover { transform:translateY(-3px); border-color:var(--accent); }
        .finance-kpi__title { color:#cbd5e1; font-size:.92rem; font-weight:650; }
        .finance-kpi__value { margin-top:.65rem; color:#fff; font-size:2rem; font-weight:780; letter-spacing:-.04em; }

        [data-testid="stVerticalBlockBorderWrapper"],div[data-testid="stForm"],[data-testid="stExpander"] { border:1px solid var(--border) !important; border-radius:16px !important; background:linear-gradient(145deg,rgba(20,31,53,.72),rgba(15,23,42,.66)) !important; box-shadow:0 10px 28px rgba(0,0,0,.12); }
        [data-testid="stVerticalBlockBorderWrapper"] { transition:transform .2s ease,border-color .2s ease; }
        [data-testid="stVerticalBlockBorderWrapper"]:hover { transform:translateY(-2px); border-color:rgba(96,165,250,.35) !important; }
        div[data-testid="stForm"] { padding:1.35rem !important; }
        [data-testid="stExpander"] summary { padding:.35rem .15rem; font-weight:650; }

        [data-testid="stWidgetLabel"] p { color:#cbd5e1; font-size:.86rem; font-weight:620; }
        [data-baseweb="input"] > div,[data-baseweb="select"] > div,[data-testid="stDateInput"] input,[data-testid="stTextArea"] textarea { border:1px solid rgba(148,163,184,.24) !important; border-radius:10px !important; background:rgba(30,41,59,.72) !important; color:#f8fafc !important; transition:border-color .18s ease,box-shadow .18s ease,background .18s ease; }
        [data-baseweb="input"] > div:focus-within,[data-baseweb="select"] > div:focus-within { border-color:var(--blue) !important; box-shadow:0 0 0 3px rgba(59,130,246,.15) !important; }

        .stButton > button,[data-testid="stFormSubmitButton"] > button { min-height:2.65rem; border:1px solid rgba(96,165,250,.5) !important; border-radius:10px !important; background:linear-gradient(100deg,#2563eb,#4f46e5) !important; color:#fff !important; font-weight:700 !important; box-shadow:0 8px 18px rgba(37,99,235,.2); transition:transform .18s ease,filter .18s ease,box-shadow .18s ease; }
        .stButton > button:hover,[data-testid="stFormSubmitButton"] > button:hover { transform:translateY(-2px); filter:brightness(1.12); box-shadow:0 12px 24px rgba(37,99,235,.3); }
        .stButton > button[kind="secondary"] { background:rgba(30,41,59,.85) !important; }
        [data-testid="stPageLink"] a { min-height:3.2rem; padding:.7rem .9rem; border:1px solid var(--border); border-radius:12px; background:rgba(30,41,59,.42); color:#e2e8f0 !important; font-weight:650; transition:transform .18s ease,border-color .18s ease,background .18s ease; }
        [data-testid="stPageLink"] a:hover { transform:translateY(-2px); border-color:rgba(96,165,250,.55); background:rgba(37,99,235,.15); text-decoration:none; }
        [data-testid="stAlert"] { border-radius:12px; border:1px solid var(--border); padding:.85rem 1rem; }
        [data-testid="stDataFrame"],[data-testid="stTable"] { border:1px solid var(--border); border-radius:14px; overflow:hidden; }
        [data-testid="stDataFrame"] { max-width:100%; overscroll-behavior-x:contain; -webkit-overflow-scrolling:touch; }
        input,textarea,select { -webkit-appearance:none; appearance:none; }
        *:focus-visible { outline:3px solid rgba(96,165,250,.55) !important; outline-offset:2px; }
        hr { border-color:var(--border) !important; }
        [data-testid="stPlotlyChart"] { padding:.6rem; border:1px solid var(--border); border-radius:16px; background:rgba(15,23,42,.45); }
        .st-key-mobile-nav, .st-key-mobile-bottom-nav { display:none; }
        [data-testid="stSidebar"] { position:relative; }
        .st-key-sidebar-user { position:absolute; z-index:4; top:3rem; left:.65rem; right:.65rem; margin:0; }
        .st-key-sidebar-user [data-testid="stHorizontalBlock"] { align-items:center; gap:.35rem; }
        .st-key-sidebar-user img { width:24px !important; height:24px !important; border-radius:50% !important; object-fit:cover; }
        .st-key-sidebar-user .stButton > button { width:100%; max-width:152px; min-height:2.2rem; padding:.35rem .55rem; justify-content:flex-start; background:linear-gradient(100deg,#2563eb,#5b35d5) !important; border:0 !important; box-shadow:none; font-size:.78rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .st-key-sidebar-session { margin:.35rem .5rem .75rem; padding-top:.8rem; border-top:1px solid var(--border); }
        .st-key-sidebar-session .stButton > button { min-height:2.5rem; background:rgba(30,41,59,.88) !important; border-color:rgba(96,165,250,.48) !important; box-shadow:none; }
        @media (min-width: 1200px) {
            [data-testid="stMainBlockContainer"] { width:calc(100% - 4.5rem) !important; max-width:1440px !important; }
        }
        @media (min-width: 1800px) {
            [data-testid="stMainBlockContainer"] { width:calc(100% - 7rem) !important; max-width:1680px !important; }
            [data-testid="stHorizontalBlock"] { gap:1.25rem !important; }
            [data-testid="stMetric"] { min-height:132px; }
        }
        @media (min-width: 769px) and (max-width: 1100px) {
            [data-testid="stMainBlockContainer"] { padding-left:1.5rem; padding-right:1.5rem; }
            .st-key-home-kpis [data-testid="stHorizontalBlock"], .st-key-home-bottom [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
            .st-key-home-kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"], .st-key-home-kpis [data-testid="stHorizontalBlock"] > [data-testid="column"] { flex:0 0 calc(50% - .45rem) !important; width:calc(50% - .45rem) !important; }
            .st-key-home-bottom [data-testid="stHorizontalBlock"] > [data-testid="stColumn"], .st-key-home-bottom [data-testid="stHorizontalBlock"] > [data-testid="column"] { flex:0 0 100% !important; width:100% !important; }
            .st-key-quick-actions [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
            .st-key-quick-actions [data-testid="stHorizontalBlock"] > [data-testid="stColumn"], .st-key-quick-actions [data-testid="stHorizontalBlock"] > [data-testid="column"] { flex:0 0 calc(33.333% - .5rem) !important; width:calc(33.333% - .5rem) !important; }
        }
        /* Layout mobile-first: cada grupo de colunas vira uma sequência vertical. */
        @media (max-width: 768px) {
            html, body, [data-testid="stAppViewContainer"], section.main {
                width:100% !important;
                max-width:100% !important;
                overflow-x:hidden !important;
            }
            .main .block-container, [data-testid="stMainBlockContainer"] {
                /* Reserva a trilha recolhida do Streamlit para ela não cobrir texto. */
                width:calc(100% - 2.15rem) !important;
                max-width:100% !important;
                min-width:0 !important;
                margin-left:2.15rem !important;
                margin-right:0 !important;
                padding:calc(7.15rem + env(safe-area-inset-top)) .9rem calc(2.4rem + env(safe-area-inset-bottom)) !important;
                box-sizing:border-box !important;
            }
            /* Streamlit mantém larguras calculadas em linha; sobrescrevê-las evita
               colunas estreitas, que causavam campos comprimidos em celulares. */
            [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; gap:.7rem !important; align-items:stretch !important; }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
            [data-testid="stHorizontalBlock"] > [data-testid="column"] { width:100% !important; min-width:0 !important; flex:0 0 100% !important; margin:0 !important; }
            [data-testid="stColumn"] > div, [data-testid="column"] > div,
            [data-testid="stElementContainer"] { min-width:0 !important; }
            [data-testid="stVerticalBlock"] { gap:.75rem !important; }
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
            [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input { min-height:2.8rem !important; font-size:16px !important; }
            [data-testid="stPageLink"] a, [data-testid="stPageLink-NavLink"] { width:100% !important; min-height:3rem !important; }
            .stButton > button, [data-testid="stFormSubmitButton"] > button { min-height:3rem; font-size:.98rem; }
            [data-testid="stDataFrame"] { overflow-x:auto; }
            [data-testid="stSidebar"] { min-width:min(84vw, 340px) !important; }
            /* No celular, o menu nativo é substituído por uma versão curta e agrupada. */
            [data-testid="stSidebarNav"] { display:none !important; }
            .st-key-mobile-nav { display:block; padding:.8rem .15rem .75rem; }
            .st-key-mobile-nav [data-testid="stPageLink"] { margin:.1rem 0; }
            .st-key-mobile-nav [data-testid="stPageLink"] a { min-height:2.75rem !important; padding:.55rem .7rem !important; border:0; background:transparent; box-shadow:none; }
            .st-key-mobile-nav [data-testid="stPageLink"] a:hover { background:rgba(59,130,246,.15); transform:none; }
            .st-key-mobile-nav [data-testid="stExpander"] { margin-top:.55rem; padding:.15rem .7rem; border-radius:12px !important; border-color:rgba(96,165,250,.22) !important; background:rgba(30,41,59,.42) !important; box-shadow:none; }
            .st-key-mobile-nav [data-testid="stExpander"] summary { min-height:2.55rem; color:#cbd5e1; font-weight:680; }
            .st-key-mobile-nav [data-testid="stExpander"] [data-testid="stPageLink"] a { min-height:2.45rem !important; }
            .st-key-sidebar-session { margin:.4rem .15rem .75rem; padding-top:.7rem; }
            /* No Streamlit web, a navegação superior não disputa espaço com controles fixos do navegador. */
            .st-key-mobile-bottom-nav { display:block; position:fixed; z-index:999; top:calc(3rem + env(safe-area-inset-top)); right:env(safe-area-inset-right); bottom:auto; left:calc(2.15rem + env(safe-area-inset-left)); margin:0 !important; padding:.4rem .45rem; border-top:1px solid rgba(148,163,184,.14); border-bottom:1px solid rgba(148,163,184,.24); background:rgba(11,17,32,.97); box-shadow:0 10px 24px rgba(0,0,0,.2); -webkit-backdrop-filter:blur(14px); backdrop-filter:blur(14px); }
            .st-key-mobile-bottom-nav [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:.25rem !important; align-items:stretch !important; }
            .st-key-mobile-bottom-nav [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
            .st-key-mobile-bottom-nav [data-testid="stHorizontalBlock"] > [data-testid="column"] { width:auto !important; min-width:0 !important; flex:1 1 0 !important; margin:0 !important; }
            .st-key-mobile-bottom-nav [data-testid="stPageLink"] a { width:100% !important; min-height:2.9rem !important; padding:.3rem .12rem !important; border:0 !important; border-radius:10px !important; background:transparent; color:#cbd5e1 !important; font-size:.68rem; font-weight:680; line-height:1.15; text-align:center; justify-content:center; white-space:pre-line; box-shadow:none; }
            .st-key-mobile-bottom-nav [data-testid="stPageLink"] a:hover,
            .st-key-mobile-bottom-nav [data-testid="stPageLink"] a[aria-current="page"] { background:linear-gradient(110deg,rgba(37,99,235,.32),rgba(124,58,237,.30)) !important; color:#fff !important; transform:none; }
            .st-key-sidebar-user [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
            .st-key-sidebar-user [data-testid="stHorizontalBlock"] > [data-testid="column"] { width:auto !important; min-width:0 !important; margin:0 !important; }
            .st-key-sidebar-user [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child,
            .st-key-sidebar-user [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child { flex:0 0 34px !important; }
            .st-key-sidebar-user [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child,
            .st-key-sidebar-user [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child { flex:1 1 0 !important; }
            .st-key-quick-actions [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
            .st-key-quick-actions [data-testid="stHorizontalBlock"] > [data-testid="column"] { width:calc(50% - .35rem) !important; flex:0 0 calc(50% - .35rem) !important; }
            .st-key-quick-actions [data-testid="stPageLink"] a { min-height:2.85rem !important; padding:.55rem .65rem !important; font-size:.86rem; }
        }

        @media (max-width: 420px) {
            .main .block-container, [data-testid="stMainBlockContainer"] { padding-left:.7rem !important; padding-right:.7rem !important; }
            h1 { font-size:1.6rem !important; }
            .hero { padding:1.15rem !important; } .hero h1 { font-size:1.65rem !important; }
            .big-money { font-size:1.8rem !important; }
            [data-testid="stMetricValue"] { font-size:1.45rem !important; }
            [data-testid="stHorizontalBlock"] { gap:.6rem !important; }
            [data-testid="stVerticalBlock"] { gap:.65rem !important; }
        }
        @media (max-height: 720px) and (min-width: 769px) {
            [data-testid="stMainBlockContainer"] { padding-top:1.25rem; padding-bottom:1.5rem; }
            [data-testid="stDialog"] > div { max-height:88dvh !important; overflow-y:auto !important; }
            [data-testid="stMetric"] { min-height:104px; padding:.85rem 1rem; }
            h1 { margin-bottom:.65rem !important; }
        }
        @media (hover:none), (pointer:coarse) {
            .stButton > button,[data-testid="stFormSubmitButton"] > button,[data-testid="stPageLink"] a { min-height:44px; }
            [data-testid="stMetric"]:hover,.finance-kpi:hover,[data-testid="stVerticalBlockBorderWrapper"]:hover,
            .stButton > button:hover,[data-testid="stPageLink"] a:hover { transform:none !important; }
        }
        @media (prefers-reduced-motion:reduce) {
            *,*::before,*::after { scroll-behavior:auto !important; animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; }
        }
        @media (prefers-contrast:more) {
            :root { --border:rgba(203,213,225,.48); --muted:#cbd5e1; }
            .stButton > button,[data-testid="stPageLink"] a { border-width:2px !important; }
        }
        @media (display-mode:standalone) and (max-width:768px) {
            [data-testid="stHeader"] { padding-top:env(safe-area-inset-top); }
        }

        /* FinanceOS 2026: acabamento inspirado em painéis financeiros profissionais. */
        :root {
            --fos-bg:#07111f;
            --fos-panel:#101d31;
            --fos-panel-2:#14243b;
            --fos-line:rgba(125,151,184,.18);
            --fos-line-active:rgba(56,189,248,.48);
            --fos-cyan:#38bdf8;
            --fos-blue:#3b82f6;
            --fos-green:#34d399;
            --fos-shadow:0 18px 42px rgba(0,5,15,.24);
        }
        .stApp {
            background:
                radial-gradient(44rem 30rem at -8% 52%,rgba(37,99,235,.14),transparent 68%),
                radial-gradient(38rem 28rem at 106% 45%,rgba(20,184,166,.12),transparent 66%),
                linear-gradient(180deg,#07111f 0%,#091321 100%);
        }
        [data-testid="stHeader"] {
            background:linear-gradient(180deg,rgba(7,17,31,.94),rgba(7,17,31,.70));
            backdrop-filter:blur(16px);
            border-bottom:1px solid rgba(125,151,184,.07);
        }
        [data-testid="stMainBlockContainer"] { max-width:1360px; padding-top:1.75rem; }
        h1 { font-size:clamp(1.8rem,3vw,2.55rem) !important; }
        h2 { font-size:clamp(1.3rem,2vw,1.65rem) !important; }
        h1,h2,h3 { text-wrap:balance; }

        /* Navegação: mais compacta, com leitura de aplicativo em vez de site. */
        [data-testid="stSidebar"] {
            background:rgba(8,18,33,.94);
            border-right:1px solid var(--fos-line);
            box-shadow:12px 0 40px rgba(0,5,15,.12);
        }
        [data-testid="stSidebarNav"] a {
            min-height:2.35rem;
            margin:.08rem .55rem;
            padding:.42rem .72rem;
            border:1px solid transparent;
            border-radius:9px;
            font-size:.82rem;
        }
        [data-testid="stSidebarNav"] a:hover {
            border-color:rgba(56,189,248,.18);
            background:rgba(56,189,248,.08);
            color:#f8fafc !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            border-color:rgba(56,189,248,.34);
            background:linear-gradient(100deg,rgba(37,99,235,.28),rgba(14,165,233,.16));
            box-shadow:inset 3px 0 0 var(--fos-cyan),0 8px 20px rgba(0,0,0,.12);
        }

        /* Superfícies e indicadores. */
        [data-testid="stMetric"],.finance-kpi {
            min-height:108px;
            padding:1rem 1.1rem;
            border-color:var(--fos-line) !important;
            border-radius:13px;
            background:linear-gradient(145deg,rgba(20,36,59,.92),rgba(12,25,43,.92));
            box-shadow:var(--fos-shadow);
        }
        [data-testid="stMetric"]::after,.finance-kpi::after {
            right:-3.5rem; bottom:-4.5rem; width:9rem; height:9rem;
            background:radial-gradient(circle,rgba(56,189,248,.15),transparent 68%);
        }
        [data-testid="stMetricLabel"] { color:#9fb1c8; font-size:.78rem; }
        [data-testid="stMetricValue"] { font-size:clamp(1.55rem,2.25vw,2.05rem); letter-spacing:-.04em; }
        [data-testid="stMetricDelta"] { width:max-content; padding:.12rem .4rem; border-radius:999px; background:rgba(52,211,153,.10); }
        [data-testid="stVerticalBlockBorderWrapper"],div[data-testid="stForm"],[data-testid="stExpander"] {
            border-color:var(--fos-line) !important;
            border-radius:13px !important;
            background:linear-gradient(145deg,rgba(17,31,52,.88),rgba(10,22,38,.88)) !important;
            box-shadow:var(--fos-shadow);
        }
        [data-testid="stExpander"] summary { min-height:2.55rem; padding:.32rem .65rem; font-size:.84rem; }

        /* Controles compactos, estados claros e foco acessível. */
        [data-baseweb="input"] > div,[data-baseweb="select"] > div,
        [data-testid="stDateInput"] input,[data-testid="stTextArea"] textarea {
            min-height:2.45rem;
            border-color:var(--fos-line) !important;
            border-radius:8px !important;
            background:rgba(18,36,59,.86) !important;
        }
        [data-baseweb="input"] > div:focus-within,[data-baseweb="select"] > div:focus-within {
            border-color:var(--fos-line-active) !important;
            box-shadow:0 0 0 3px rgba(56,189,248,.10) !important;
        }
        [data-testid="stWidgetLabel"] p { color:#aebed1; font-size:.78rem; }
        .stButton > button,[data-testid="stFormSubmitButton"] > button {
            min-height:2.45rem;
            border-color:rgba(56,189,248,.35) !important;
            border-radius:8px !important;
            background:linear-gradient(105deg,#2563eb,#0284c7) !important;
            box-shadow:0 8px 22px rgba(2,132,199,.16);
            font-size:.82rem;
        }
        .stButton > button[kind="secondary"] {
            background:rgba(18,36,59,.82) !important;
            box-shadow:none;
        }
        [data-testid="stPageLink"] a { border-radius:9px; background:rgba(18,36,59,.54); font-size:.84rem; }
        [data-testid="stAlert"] { border-radius:9px; background:rgba(18,36,59,.68); }

        /* Tabelas e gráficos recebem a mesma moldura visual. */
        [data-testid="stDataFrame"],[data-testid="stTable"] {
            border-color:var(--fos-line);
            border-radius:11px;
            background:rgba(8,20,35,.68);
            box-shadow:var(--fos-shadow);
        }
        [data-testid="stPlotlyChart"] {
            border-color:var(--fos-line);
            border-radius:13px;
            background:linear-gradient(145deg,rgba(12,25,43,.82),rgba(7,17,31,.72));
            box-shadow:var(--fos-shadow);
        }
        div[data-baseweb="tab-list"] {
            width:max-content;
            max-width:100%;
            padding:.25rem;
            border:1px solid var(--fos-line);
            border-radius:999px;
            background:rgba(15,30,50,.76);
            overflow-x:auto;
        }
        button[data-baseweb="tab"] { min-height:2rem; padding:.25rem .75rem; border-radius:999px; font-size:.78rem; }
        button[data-baseweb="tab"][aria-selected="true"] { background:linear-gradient(100deg,#2563eb,#0891b2); color:white; }

        /* Compatibilidade com os heróis já existentes no Início e Dashboard. */
        .home-hero,.dashboard-hero,.saldo-card {
            border-color:rgba(56,189,248,.25) !important;
            border-radius:16px !important;
            background:
                radial-gradient(circle at 88% 20%,rgba(56,189,248,.16),transparent 28%),
                linear-gradient(115deg,rgba(17,43,75,.98),rgba(19,37,64,.96) 55%,rgba(13,56,71,.88)) !important;
            box-shadow:0 22px 55px rgba(0,5,15,.28) !important;
        }
        .vencimento-card {
            border-color:var(--fos-line) !important;
            border-radius:11px !important;
            background:linear-gradient(135deg,rgba(20,36,59,.88),rgba(11,24,41,.88)) !important;
        }

        /* Navegação principal horizontal: somente desktop web. */
        .st-key-desktop-nav { display:none; }
        @media (min-width:769px) {
            [data-testid="stSidebar"],
            [data-testid="collapsedControl"] { display:none !important; }
            [data-testid="stMainBlockContainer"] {
                width:calc(100% - 3rem) !important;
                max-width:1360px !important;
                padding-top:1rem !important;
            }
            .st-key-desktop-nav {
                display:block;
                position:sticky;
                z-index:900;
                top:.5rem;
                margin:0 0 1.35rem;
                padding:.42rem .52rem;
                border:1px solid var(--fos-line);
                border-radius:13px;
                background:rgba(8,20,35,.90);
                box-shadow:0 16px 38px rgba(0,5,15,.24);
                backdrop-filter:blur(18px);
            }
            .st-key-desktop-nav [data-testid="stHorizontalBlock"] {
                align-items:center;
                gap:.28rem !important;
            }
            .st-key-desktop-nav [data-testid="stColumn"],
            .st-key-desktop-nav [data-testid="column"] { min-width:0; }
            .st-key-desktop-nav .financeos-nav-brand {
                display:flex;
                align-items:center;
                gap:.45rem;
                min-height:2.35rem;
                padding:0 .5rem;
                color:#f8fafc;
                font-size:.9rem;
                font-weight:800;
                letter-spacing:-.02em;
                white-space:nowrap;
            }
            .st-key-desktop-nav .financeos-nav-mark {
                color:var(--fos-cyan);
            }
            .st-key-desktop-nav .financeos-nav-user {
                display:flex;
                align-items:center;
                gap:.35rem;
                min-width:0;
                margin-left:.18rem;
                padding-left:.55rem;
                border-left:1px solid var(--fos-line);
            }
            .st-key-desktop-nav .financeos-nav-avatar {
                display:flex;
                align-items:center;
                justify-content:center;
                width:27px;
                height:27px;
                flex:0 0 27px;
                overflow:hidden;
                border:1px solid rgba(56,189,248,.34);
                border-radius:50%;
                background:linear-gradient(135deg,rgba(37,99,235,.55),rgba(8,145,178,.40));
                color:#fff;
                font-size:.68rem;
                font-weight:800;
                box-shadow:0 0 0 3px rgba(56,189,248,.06);
            }
            .st-key-desktop-nav .financeos-nav-avatar img {
                width:100%;
                height:100%;
                object-fit:cover;
            }
            .st-key-desktop-nav .financeos-nav-name {
                max-width:6.5rem;
                overflow:hidden;
                color:#b8c7da;
                font-size:.72rem;
                font-weight:700;
                text-overflow:ellipsis;
                white-space:nowrap;
            }
            .st-key-desktop-nav [data-testid="stPageLink"] a,
            .st-key-desktop-nav [data-testid="stPopover"] > button {
                justify-content:center;
                width:100%;
                min-height:2.35rem !important;
                padding:.38rem .55rem !important;
                border:1px solid transparent !important;
                border-radius:8px !important;
                background:transparent !important;
                box-shadow:none !important;
                color:#b8c7da !important;
                font-size:.76rem !important;
                font-weight:680 !important;
                white-space:nowrap;
            }
            .st-key-desktop-nav [data-testid="stPageLink"] a:hover,
            .st-key-desktop-nav [data-testid="stPopover"] > button:hover {
                transform:none !important;
                border-color:rgba(56,189,248,.20) !important;
                background:rgba(56,189,248,.08) !important;
                color:#fff !important;
            }
            .st-key-desktop-nav [data-testid="stPageLink"] a[aria-current="page"] {
                border-color:rgba(56,189,248,.36) !important;
                background:linear-gradient(100deg,rgba(37,99,235,.34),rgba(8,145,178,.22)) !important;
                color:#fff !important;
                box-shadow:inset 0 -2px 0 var(--fos-cyan) !important;
            }
            .st-key-desktop-nav [data-testid="stPopover"] { width:100%; }
        }

        @media (max-width:768px) {
            [data-testid="stMainBlockContainer"] { padding-top:calc(7rem + env(safe-area-inset-top)) !important; }
            [data-testid="stMetric"],.finance-kpi { min-height:94px; border-radius:11px; }
            div[data-baseweb="tab-list"] { width:100%; border-radius:11px; }
            button[data-baseweb="tab"] { flex:1 0 auto; }
            .home-hero,.dashboard-hero,.saldo-card { border-radius:14px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _configurar_navegador()
    if str(st.session_state.get("usuario", "")).strip().lower() != ADMIN_USER:
        st.markdown(
            "<style>[data-testid='stSidebarNav'] li:has(a[href*='Admin']) { display:none !important; }</style>",
            unsafe_allow_html=True,
        )
    _renderizar_cabecalho_usuario()
    _renderizar_navegacao_desktop()
    _renderizar_navegacao_mobile()
    _renderizar_barra_inferior_mobile()
    _renderizar_sessao_sidebar()


def _renderizar_navegacao_desktop():
    """Barra agrupada no topo; o CSS a mantém invisível em telas móveis."""
    if not st.session_state.get("logado"):
        return
    usuario_admin = str(st.session_state.get("usuario", "")).strip().lower() == ADMIN_USER
    nome_usuario = str(st.session_state.get("usuario", "")).strip().lstrip("@") or "Usuário"
    foto_usuario = None
    try:
        from auth import obter_perfil
        perfil = obter_perfil(st.session_state.get("usuario"))
        if perfil:
            nome_usuario = (perfil["nome"] or nome_usuario).strip().split()[0]
            foto_usuario = perfil["foto_perfil"]
    except Exception:
        pass
    iniciais = "".join(parte[0] for parte in nome_usuario.split()[:2]).upper() or "U"
    avatar = escape(iniciais)
    if foto_usuario:
        conteudo = bytes(foto_usuario)
        if conteudo.startswith(b"\x89PNG"):
            mime = "image/png"
        elif conteudo.startswith(b"\xff\xd8\xff"):
            mime = "image/jpeg"
        elif conteudo.startswith(b"RIFF") and conteudo[8:12] == b"WEBP":
            mime = "image/webp"
        else:
            mime = None
        if mime:
            fonte = b64encode(conteudo).decode("ascii")
            avatar = f'<img src="data:{mime};base64,{fonte}" alt="Foto de perfil">'
    with st.container(key="desktop-nav"):
        marca, inicio, dashboard, movimentacoes, cartoes, planejamento, relatorios, mais = st.columns(
            [1.8, .68, .84, 1.08, .75, 1.02, .84, .65]
        )
        with marca:
            st.markdown(
                f'<div class="financeos-nav-brand"><span class="financeos-nav-mark">◆</span>'
                f'<strong>FinanceOS</strong><span class="financeos-nav-user">'
                f'<span class="financeos-nav-avatar">{avatar}</span>'
                f'<span class="financeos-nav-name">{escape(nome_usuario)}</span></span></div>',
                unsafe_allow_html=True,
            )
        with inicio:
            st.page_link("app.py", label="Início", use_container_width=True)
        with dashboard:
            st.page_link("pages/01_Dashboard.py", label="Dashboard", use_container_width=True)
        with movimentacoes:
            with st.popover("Movimentações", use_container_width=True):
                st.page_link("pages/02_Receitas.py", label="Receitas", icon="💰", use_container_width=True)
                st.page_link("pages/03_Despesas.py", label="Despesas", icon="💸", use_container_width=True)
                st.page_link("pages/11_Transferencias.py", label="Transferências", icon="↔️", use_container_width=True)
                st.page_link("pages/13_Conciliação.py", label="Conciliação", icon="✅", use_container_width=True)
        with cartoes:
            with st.popover("Cartões", use_container_width=True):
                st.page_link("pages/04_Cartoes.py", label="Cartões", icon="💳", use_container_width=True)
                st.page_link("pages/04_Controle_de_gastos.py", label="Controle de gastos", icon="🎯", use_container_width=True)
                st.page_link("pages/04_Importar_fatura.py", label="Importar fatura", icon="📥", use_container_width=True)
        with planejamento:
            with st.popover("Planejamento", use_container_width=True):
                st.page_link("pages/05_Bancos.py", label="Bancos", icon="🏦", use_container_width=True)
                st.page_link("pages/06_Patrimonio.py", label="Patrimônio", icon="🏠", use_container_width=True)
                st.page_link("pages/07_Metas.py", label="Metas", icon="🎯", use_container_width=True)
                st.page_link("pages/09_Orcamentos.py", label="Orçamentos", icon="📋", use_container_width=True)
                st.page_link("pages/10_Recorrencias.py", label="Recorrências", icon="🔁", use_container_width=True)
        with relatorios:
            st.page_link("pages/14_Relatórios.py", label="Relatórios", use_container_width=True)
        with mais:
            with st.popover("Mais", use_container_width=True):
                st.page_link("pages/12_Holerite.py", label="Holerite", icon="📄", use_container_width=True)
                st.page_link("pages/16_Central_Financeira.py", label="Central financeira", icon="🧭", use_container_width=True)
                st.page_link("pages/08_Configuracoes.py", label="Configurações", icon="⚙️", use_container_width=True)
                st.page_link("pages/00_👤_Perfil.py", label="Meu perfil", icon="👤", use_container_width=True)
                if usuario_admin:
                    st.page_link("pages/15_Admin.py", label="Administração", icon="🛡️", use_container_width=True)
                st.divider()
                if st.button("Sair da conta", use_container_width=True, key="sair_desktop"):
                    st.session_state.clear()
                    st.rerun()


def _configurar_navegador():
    """Adiciona metadados web no documento principal sem armazenar dados no navegador."""
    components.html(
        """
        <script>
        (() => {
          const doc = window.parent.document;
          const addMeta = (name, content) => {
            let el = doc.head.querySelector(`meta[name="${name}"]`);
            if (!el) { el = doc.createElement("meta"); el.name = name; doc.head.appendChild(el); }
            el.content = content;
          };
          addMeta("viewport", "width=device-width,initial-scale=1,viewport-fit=cover");
          addMeta("theme-color", "#0b1120");
          addMeta("apple-mobile-web-app-capable", "yes");
          addMeta("apple-mobile-web-app-status-bar-style", "black-translucent");
          addMeta("apple-mobile-web-app-title", "FinanceOS");
          if (!doc.head.querySelector('link[rel="manifest"]')) {
            const manifest = doc.createElement("link"); manifest.rel = "manifest";
            manifest.href = "/app/static/manifest.webmanifest"; doc.head.appendChild(manifest);
          }
          if (!doc.head.querySelector('link[rel="mask-icon"]')) {
            const icon = doc.createElement("link"); icon.rel = "mask-icon";
            icon.href = "/app/static/financeos-icon.svg"; icon.color = "#2563eb"; doc.head.appendChild(icon);
          }
          let banner = doc.getElementById("financeos-offline");
          if (!banner) {
            banner = doc.createElement("div"); banner.id = "financeos-offline";
            Object.assign(banner.style,{display:"none",position:"fixed",zIndex:"10000",left:"50%",bottom:"calc(1rem + env(safe-area-inset-bottom))",transform:"translateX(-50%)",padding:".65rem 1rem",borderRadius:"10px",background:"#991b1b",color:"white",font:"600 14px system-ui",boxShadow:"0 8px 24px rgba(0,0,0,.35)"});
            banner.textContent = "Sem conexão. Não feche a página até a internet voltar."; doc.body.appendChild(banner);
          }
          const sync = () => banner.style.display = navigator.onLine ? "none" : "block";
          window.parent.addEventListener("online", sync); window.parent.addEventListener("offline", sync); sync();
          window.parent.clearTimeout(window.parent.__financeosSessionTimer);
          window.parent.__financeosSessionTimer = window.parent.setTimeout(() => window.parent.location.reload(), __SESSION_TIMEOUT__ * 60 * 1000);
        })();
        </script>
        """.replace("__SESSION_TIMEOUT__", str(SESSION_TIMEOUT_MINUTES)),
        height=0,
        width=0,
    )


def _renderizar_navegacao_mobile():
    """Atalhos compactos exibidos somente por CSS em telas pequenas."""
    if not st.session_state.get("logado"):
        return
    with st.sidebar:
        with st.container(key="mobile-nav"):
            st.page_link("app.py", label="Início")
            st.page_link("pages/01_Dashboard.py", label="Dashboard")
            st.page_link("pages/02_Receitas.py", label="Receitas")
            st.page_link("pages/03_Despesas.py", label="Despesas")
            st.page_link("pages/04_Cartoes.py", label="Cartões")
            with st.expander("Cartões e faturas"):
                st.page_link("pages/04_Controle_de_gastos.py", label="Controle de gastos")
                st.page_link("pages/04_Importar_fatura.py", label="Importar fatura")
            with st.expander("Organizar finanças"):
                st.page_link("pages/05_Bancos.py", label="Bancos")
                st.page_link("pages/06_Patrimonio.py", label="Patrimônio")
                st.page_link("pages/07_Metas.py", label="Metas")
                st.page_link("pages/08_Configuracoes.py", label="Configurações")
                st.page_link("pages/09_Orcamentos.py", label="Orçamentos")
                st.page_link("pages/10_Recorrencias.py", label="Recorrências")
                st.page_link("pages/11_Transferencias.py", label="Transferências")
                st.page_link("pages/12_Holerite.py", label="Holerite")
                st.page_link("pages/13_Conciliação.py", label="Conciliação")
                st.page_link("pages/14_Relatórios.py", label="Relatórios")
                st.page_link("pages/16_Central_Financeira.py", label="Central financeira")
                if str(st.session_state.get("usuario", "")).strip().lower() == ADMIN_USER:
                    st.page_link("pages/15_Admin.py", label="Admin")


def _renderizar_barra_inferior_mobile():
    """Navegação principal fixa, exibida apenas em telas pequenas por CSS."""
    if not st.session_state.get("logado"):
        return
    with st.container(key="mobile-bottom-nav"):
        inicio, receitas, despesas, cartoes, perfil = st.columns(5)
        with inicio:
            st.page_link("app.py", label="⌂\nInício")
        with receitas:
            st.page_link("pages/02_Receitas.py", label="↓\nReceitas")
        with despesas:
            st.page_link("pages/03_Despesas.py", label="↑\nDespesas")
        with cartoes:
            st.page_link("pages/04_Cartoes.py", label="▣\nCartões")
        with perfil:
            st.page_link("pages/00_👤_Perfil.py", label="●\nPerfil")


def _renderizar_cabecalho_usuario():
    """Atalho de perfil com foto e nome, visível em desktop e mobile."""
    if not st.session_state.get("logado"):
        return
    try:
        from auth import obter_perfil
        dados = obter_perfil(st.session_state.get("usuario"))
    except Exception:
        dados = None
    with st.sidebar:
        with st.container(key="sidebar-user"):
            foto, nome = st.columns([1, 6])
            with foto:
                if dados and dados["foto_perfil"]:
                    st.image(dados["foto_perfil"])
                else:
                    st.markdown("👤")
            with nome:
                nome_exibicao = (dados["nome"] or "").strip().split()[0] if dados else "Meu perfil"
                if st.button(nome_exibicao or "Meu perfil", key="abrir_perfil_sidebar", use_container_width=True):
                    st.switch_page("pages/00_👤_Perfil.py")


def _renderizar_sessao_sidebar():
    """Mantém a saída acessível no fim da navegação em todas as páginas internas."""
    if not st.session_state.get("logado"):
        return
    with st.sidebar:
        with st.container(key="sidebar-session"):
            if st.button("Sair da conta", use_container_width=True, key="sair_sidebar"):
                st.session_state.clear()
                st.rerun()
