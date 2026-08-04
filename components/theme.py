"""Tema visual compartilhado por todas as páginas do FinanceOS."""

import streamlit as st


def aplicar_tema():
    st.markdown(
        """
        <style>
        :root { --blue:#3b82f6; --violet:#8b5cf6; --surface:rgba(19,28,48,.82); --surface-strong:#121c31; --border:rgba(148,163,184,.18); --border-strong:rgba(148,163,184,.30); --text:#e6edf7; --muted:#94a3b8; --space-1:.5rem; --space-2:.75rem; --space-3:1rem; --space-4:1.5rem; --space-5:2rem; }
        .stApp { background:radial-gradient(circle at 6% 10%,rgba(37,99,235,.12),transparent 25rem),radial-gradient(circle at 94% 75%,rgba(124,58,237,.11),transparent 26rem),#0b1120; color:var(--text); font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }
        [data-testid="stHeader"] { background:rgba(11,17,32,.75); }
        [data-testid="stMainBlockContainer"] { max-width:1280px; padding-top:2.4rem; padding-bottom:3.25rem; }
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
        *:focus-visible { outline:3px solid rgba(96,165,250,.55) !important; outline-offset:2px; }
        hr { border-color:var(--border) !important; }
        [data-testid="stPlotlyChart"] { padding:.6rem; border:1px solid var(--border); border-radius:16px; background:rgba(15,23,42,.45); }
        .st-key-mobile-nav { display:none; }
        /* Layout mobile-first: cada grupo de colunas vira uma sequência vertical. */
        @media (max-width: 768px) {
            html, body, [data-testid="stAppViewContainer"], section.main {
                width:100% !important;
                max-width:100% !important;
                overflow-x:hidden !important;
            }
            .main .block-container, [data-testid="stMainBlockContainer"] {
                width:100% !important;
                max-width:100% !important;
                min-width:0 !important;
                margin:0 !important;
                padding:1.15rem .9rem 2.5rem !important;
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
            [data-testid="stSidebar"] { min-width:min(82vw, 320px) !important; }
            /* No celular, o menu nativo é substituído por uma versão curta e agrupada. */
            [data-testid="stSidebarNav"] { display:none !important; }
            .st-key-mobile-nav { display:block; padding:.35rem .15rem 1rem; }
            .st-key-mobile-nav [data-testid="stPageLink"] { margin:.1rem 0; }
            .st-key-mobile-nav [data-testid="stPageLink"] a { min-height:2.75rem !important; padding:.55rem .7rem !important; border:0; background:transparent; box-shadow:none; }
            .st-key-mobile-nav [data-testid="stPageLink"] a:hover { background:rgba(59,130,246,.15); transform:none; }
            .st-key-mobile-nav [data-testid="stExpander"] { margin-top:.6rem; padding:.15rem .7rem; border-radius:12px !important; box-shadow:none; }
            .st-key-mobile-nav [data-testid="stExpander"] summary { color:#cbd5e1; }
            .st-key-mobile-nav [data-testid="stExpander"] [data-testid="stPageLink"] a { min-height:2.45rem !important; }
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
        </style>
        """,
        unsafe_allow_html=True,
    )
    _renderizar_navegacao_mobile()


def _renderizar_navegacao_mobile():
    """Atalhos compactos exibidos somente por CSS em telas pequenas."""
    with st.sidebar:
        with st.container(key="mobile-nav"):
            st.page_link("pages/00_👤_Perfil.py", label="Perfil", icon="👤")
            st.page_link("app.py", label="Início", icon="🏠")
            st.page_link("pages/01_Dashboard.py", label="Análises", icon="📊")
            st.page_link("pages/02_Receitas.py", label="Receitas", icon="💰")
            st.page_link("pages/03_Despesas.py", label="Despesas", icon="💸")
            st.page_link("pages/04_Cartoes.py", label="Cartões", icon="💳")
            st.page_link("pages/04_Controle_de_gastos.py", label="Controle de gastos", icon="🎯")
            with st.expander("Mais opções"):
                st.page_link("pages/05_Bancos.py", label="Bancos", icon="🏦")
                st.page_link("pages/06_Patrimonio.py", label="Patrimônio", icon="🏠")
                st.page_link("pages/07_Metas.py", label="Metas", icon="🎯")
                st.page_link("pages/08_Configuracoes.py", label="Configurações", icon="⚙️")
                st.page_link("pages/09_Orcamentos.py", label="Orçamentos", icon="🧾")
                st.page_link("pages/10_Recorrencias.py", label="Recorrências", icon="🔁")
                st.page_link("pages/11_Transferencias.py", label="Transferências", icon="↔️")
                st.page_link("pages/12_Holerite.py", label="Holerite", icon="📄")
                st.page_link("pages/13_Conciliação.py", label="Conciliação", icon="✅")
                st.page_link("pages/14_Relatórios.py", label="Relatórios", icon="📈")
                st.page_link("pages/16_Importar_fatura.py", label="Importar fatura", icon="📥")
