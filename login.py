from base64 import b64encode
from pathlib import Path

import streamlit as st

from auth import autenticar, criar_usuario, login_bloqueado, possui_usuario, registrar_falha_login
from config import ALLOW_REGISTRATION


def _logo_financeos():
    """Retorna a marca local como data URI, sem depender de serviço externo."""
    caminho = Path(__file__).resolve().parent / "static" / "financeos-login-logo.png"
    if not caminho.exists():
        return ""
    return f"data:image/png;base64,{b64encode(caminho.read_bytes()).decode('ascii')}"


def tela_login():
    st.markdown(
        """
        <style>
        [data-testid="stHeader"], [data-testid="stToolbar"] {
            background: transparent;
        }

        /* A navegação só fica disponível depois de autenticar. */
        [data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }

        .stApp {
            background:
                radial-gradient(42rem 30rem at -6% 35%, rgba(37, 99, 235, .19), transparent 68%),
                radial-gradient(36rem 28rem at 106% 64%, rgba(20, 184, 166, .14), transparent 66%),
                linear-gradient(180deg, #07111f 0%, #091321 100%);
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1180px;
            padding-top: 7.5rem;
        }

        .login-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: .55rem;
            padding: .42rem .8rem;
            border: 1px solid rgba(56, 189, 248, .32);
            border-radius: 999px;
            background: rgba(14, 116, 144, .13);
            color: #bae6fd;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .04em;
            text-transform: uppercase;
        }

        .login-title {
            margin: 1.15rem 0 .65rem;
            color: #f8fafc;
            font-size: clamp(2.2rem, 4vw, 3.45rem);
            font-weight: 800;
            letter-spacing: -.06em;
            line-height: 1;
        }

        .login-title span {
            color: #38bdf8;
        }

        .login-description {
            max-width: 34rem;
            margin-bottom: 2rem;
            color: #aab6cf;
            font-size: 1.05rem;
            line-height: 1.65;
        }

        div[data-testid="stForm"] {
            max-width: 540px;
            padding: 1.75rem !important;
            border: 1px solid rgba(125, 151, 184, .20) !important;
            border-radius: 16px !important;
            background:
                radial-gradient(circle at 100% 0, rgba(56, 189, 248, .07), transparent 34%),
                linear-gradient(145deg, rgba(17, 31, 52, .92), rgba(10, 22, 38, .92)) !important;
            box-shadow: 0 24px 60px rgba(0, 5, 15, .34);
            backdrop-filter: blur(18px);
        }

        div[data-testid="stForm"] [data-testid="stWidgetLabel"] p {
            color: #dbeafe;
            font-size: .82rem;
            font-weight: 650;
        }

        div[data-testid="stForm"] input {
            min-height: 2.9rem;
            border: 1px solid rgba(125, 151, 184, .20) !important;
            border-radius: 8px !important;
            background: rgba(18, 36, 59, .86) !important;
            color: #f8fafc !important;
        }

        div[data-testid="stForm"] input:focus {
            border-color: rgba(56, 189, 248, .55) !important;
            box-shadow: 0 0 0 3px rgba(56, 189, 248, .12) !important;
        }

        div[data-testid="stFormSubmitButton"] button {
            min-height: 2.9rem;
            border: 0 !important;
            border-radius: 8px !important;
            background: linear-gradient(105deg, #2563eb, #0284c7) !important;
            color: white !important;
            font-weight: 750 !important;
            box-shadow: 0 10px 25px rgba(2, 132, 199, .24);
            transition: transform .2s ease, filter .2s ease;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px);
            filter: brightness(1.12);
        }

        .login-trust {
            display: flex;
            gap: 1rem;
            margin-top: 1.4rem;
            color: #94a3b8;
            font-size: .8rem;
        }

        div[data-baseweb="tab-list"] {
            width: max-content;
            max-width: 100%;
            margin-bottom: .7rem;
            padding: .24rem;
            border: 1px solid rgba(125, 151, 184, .18);
            border-radius: 999px;
            background: rgba(15, 30, 50, .72);
        }

        button[data-baseweb="tab"] {
            min-height: 2.1rem;
            padding: .28rem .8rem;
            border-radius: 999px;
            color: #aebed1;
            font-size: .8rem;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(100deg, rgba(37, 99, 235, .88), rgba(8, 145, 178, .82));
            color: #fff;
        }

        [data-testid="stAlert"] {
            border: 1px solid rgba(125, 151, 184, .18);
            border-radius: 10px;
            background: rgba(18, 36, 59, .74);
        }

        @media (max-width: 700px) {
            .main .block-container, [data-testid="stMainBlockContainer"] {
                width:100% !important;
                max-width:100% !important;
                margin:0 auto !important;
                padding:2rem 1rem calc(2rem + env(safe-area-inset-bottom)) !important;
                box-sizing:border-box !important;
            }
            [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] {
                width:100% !important;
                justify-content:center !important;
            }
            [data-testid="stMainBlockContainer"] [data-testid="stColumn"],
            [data-testid="stMainBlockContainer"] [data-testid="column"] {
                width:100% !important;
                max-width:34rem !important;
                margin:0 auto !important;
                flex:0 0 100% !important;
            }
            .login-eyebrow { width:max-content; max-width:100%; margin-left:auto; margin-right:auto; }
            .login-title,.login-description,.login-trust,
            [data-testid="stTabs"],div[data-testid="stForm"],[data-testid="stAlert"] {
                width:min(100%,32rem) !important;
                max-width:32rem !important;
                margin-left:auto !important;
                margin-right:auto !important;
                box-sizing:border-box !important;
            }
            div[data-testid="stForm"] { padding:1.25rem !important; border-radius:14px !important; }
            div[data-baseweb="tab-list"] { margin-left:auto; margin-right:auto; }
            .login-trust { justify-content:center; flex-wrap:wrap; gap:.45rem .75rem; text-align:center; }
        }

        /* Apresentação da marca: inspirada em landing pages financeiras,
           preservando integralmente as cores e a identidade do FinanceOS. */
        [data-testid="stMainBlockContainer"] {
            max-width: 1180px;
            padding-top: 4.5rem;
            padding-bottom: 4rem;
        }
        [data-testid="stMainBlockContainer"] > div > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
            align-items: center;
            gap: clamp(2rem, 5vw, 5rem) !important;
        }
        .login-brand-panel {
            position: relative;
            overflow: hidden;
            min-height: 620px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: clamp(2rem, 4vw, 3.5rem);
            border: 1px solid rgba(56, 189, 248, .22);
            border-radius: 28px;
            background:
                radial-gradient(circle at 18% 12%, rgba(45, 212, 191, .20), transparent 30%),
                radial-gradient(circle at 92% 88%, rgba(37, 99, 235, .28), transparent 36%),
                linear-gradient(145deg, rgba(12, 35, 61, .98), rgba(7, 22, 39, .98));
            box-shadow: 0 34px 90px rgba(0, 5, 15, .38);
        }
        .login-brand-panel::before,.login-brand-panel::after {
            content: "";
            position: absolute;
            border: 1px solid rgba(56, 189, 248, .12);
            border-radius: 50%;
            pointer-events: none;
        }
        .login-brand-panel::before { width:24rem; height:24rem; right:-13rem; top:-12rem; }
        .login-brand-panel::after { width:18rem; height:18rem; left:-10rem; bottom:-9rem; }
        .login-brand-logo {
            position: relative;
            z-index: 1;
            display: block;
            width: min(100%, 340px);
            margin: 0 auto 2.1rem;
            border-radius: 22px;
            filter: drop-shadow(0 20px 34px rgba(0, 0, 0, .35));
        }
        .login-brand-kicker {
            position:relative; z-index:1; color:#67e8f9; font-size:.78rem;
            font-weight:800; letter-spacing:.13em; text-transform:uppercase;
        }
        .login-brand-title {
            position:relative; z-index:1; max-width:31rem; margin:.85rem 0 1rem;
            color:#f8fafc; font-size:clamp(2rem,3.5vw,3.25rem); font-weight:820;
            letter-spacing:-.055em; line-height:1.04;
        }
        .login-brand-title span { color:#2dd4bf; }
        .login-brand-copy {
            position:relative; z-index:1; max-width:30rem; color:#b8c7da;
            font-size:1rem; line-height:1.65;
        }
        .login-brand-points {
            position:relative; z-index:1; display:flex; flex-wrap:wrap;
            gap:.6rem; margin-top:1.6rem;
        }
        .login-brand-points span {
            padding:.48rem .7rem; border:1px solid rgba(103,232,249,.18);
            border-radius:999px; background:rgba(8,145,178,.10);
            color:#c8f7ff; font-size:.74rem; font-weight:650;
        }
        .login-access-heading {
            margin:0 0 .45rem; color:#f8fafc; font-size:clamp(1.55rem,2.2vw,2.1rem);
            font-weight:780; letter-spacing:-.035em;
        }
        .login-access-copy { margin:0 0 1.4rem; color:#94a3b8; line-height:1.55; }

        @media (max-width:700px) {
            .login-brand-panel {
                min-height:auto; width:min(100%,32rem); margin:0 auto .65rem;
                padding:1.35rem 1.2rem; border-radius:18px; text-align:center;
            }
            .login-brand-logo { width:150px; margin-bottom:.85rem; border-radius:14px; }
            .login-brand-kicker { font-size:.68rem; }
            .login-brand-title {
                margin:.55rem auto .65rem; font-size:1.65rem; letter-spacing:-.035em;
            }
            .login-brand-copy { margin:0 auto; font-size:.88rem; line-height:1.5; }
            .login-brand-points { display:none; }
            .login-access-heading,.login-access-copy {
                width:min(100%,32rem); margin-left:auto; margin-right:auto; text-align:center;
            }
            .login-access-heading { margin-top:.6rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo = _logo_financeos()
    logo_html = f'<img class="login-brand-logo" src="{logo}" alt="FinanceOS">' if logo else ""
    painel_marca, coluna = st.columns([1.08, .92], gap="large")

    with painel_marca:
        st.markdown(
            f"""
            <section class="login-brand-panel" aria-label="Apresentação do FinanceOS">
                {logo_html}
                <div class="login-brand-kicker">Gestão financeira pessoal</div>
                <div class="login-brand-title">Controle hoje.<br><span>Planeje amanhã.</span></div>
                <div class="login-brand-copy">
                    Receitas, despesas, cartões e objetivos reunidos em uma experiência clara,
                    segura e feita para suas decisões.
                </div>
                <div class="login-brand-points">
                    <span>✓ Visão completa</span>
                    <span>✓ Dados protegidos</span>
                    <span>✓ Controle em um só lugar</span>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

    with coluna:
        st.markdown(
            """
            <div class="login-eyebrow">✦ &nbsp; Gestão financeira pessoal</div>
            <div class="login-access-heading">Seu dinheiro, com clareza.</div>
            <div class="login-access-copy">Entre na sua conta ou crie seu acesso ao FinanceOS.</div>
            """,
            unsafe_allow_html=True,
        )

        if not possui_usuario():
            st.info("Crie o primeiro acesso para proteger seus dados.")
            with st.form("criar_primeiro_usuario"):
                nome = st.text_input("Seu nome")
                usuario = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password", help="Mínimo de 10 caracteres.")
                confirmacao = st.text_input("Confirmar senha", type="password")
                criar = st.form_submit_button("Criar acesso", use_container_width=True)

            if criar:
                if senha != confirmacao:
                    st.error("As senhas não coincidem.")
                else:
                    sucesso, mensagem = criar_usuario(nome, usuario, senha)
                    if sucesso:
                        perfil = autenticar(usuario, senha)
                        st.session_state.logado = True
                        st.session_state.usuario = usuario.strip()
                        st.session_state.usuario_id = perfil["id"]
                        st.session_state.perfil = perfil["perfil"]
                        st.session_state.sessao_versao = perfil.get("sessao_versao", 1)
                        st.rerun()
                    st.error(mensagem) if not sucesso else None
            st.markdown(
                '<div class="login-trust"><span>🔒 Senha protegida</span><span>•</span><span>Dados protegidos no Supabase</span></div>',
                unsafe_allow_html=True,
            )
            return

        if ALLOW_REGISTRATION:
            aba_entrar, aba_cadastrar = st.tabs(["Entrar", "Cadastrar-se"])
        else:
            aba_entrar = st.container()
            aba_cadastrar = None
        with aba_entrar:
            with st.form("login"):
                usuario = st.text_input("Usuário", help="Formato: nome.sobrenome")
                senha = st.text_input("Senha", type="password")
                entrar = st.form_submit_button("Entrar", use_container_width=True)

            if entrar:
                if login_bloqueado(usuario):
                    st.error("Esta conta está temporariamente bloqueada. Aguarde 10 minutos e tente novamente.")
                elif perfil := autenticar(usuario, senha):
                    st.session_state.logado = True
                    st.session_state.usuario = usuario.strip()
                    st.session_state.usuario_id = perfil["id"]
                    st.session_state.perfil = perfil["perfil"]
                    st.session_state.sessao_versao = perfil.get("sessao_versao", 1)
                    st.rerun()
                else:
                    if registrar_falha_login(usuario):
                        st.error("Muitas tentativas. Esta conta foi bloqueada por 10 minutos.")
                    else:
                        st.error("Usuário ou senha inválidos.")

        if aba_cadastrar is not None:
          with aba_cadastrar:
            st.caption("Crie seu acesso. Suas receitas, despesas, cartões e relatórios ficarão separados dos demais usuários.")
            with st.form("cadastrar_usuario"):
                nome_novo = st.text_input("Nome completo")
                usuario_novo = st.text_input("Usuário", help="Formato obrigatório: nome.sobrenome, em minúsculas. Ex.: maria.silva")
                senha_nova = st.text_input("Senha", type="password", help="Mínimo de 10 caracteres, com maiúscula, minúscula e número ou símbolo.")
                confirmar_nova = st.text_input("Confirmar senha", type="password")
                cadastrar = st.form_submit_button("Criar minha conta", use_container_width=True)
            if cadastrar:
                if senha_nova != confirmar_nova:
                    st.error("As senhas não coincidem.")
                else:
                    sucesso, mensagem = criar_usuario(nome_novo, usuario_novo, senha_nova)
                    if sucesso:
                        perfil = autenticar(usuario_novo, senha_nova)
                        st.session_state.logado = True
                        st.session_state.usuario = usuario_novo.strip()
                        st.session_state.usuario_id = perfil["id"]
                        st.session_state.perfil = perfil["perfil"]
                        st.session_state.sessao_versao = perfil.get("sessao_versao", 1)
                        st.rerun()
                    st.error(mensagem) if not sucesso else None

        st.markdown(
            '<div class="login-trust"><span>🔒 Acesso protegido</span><span>•</span><span>Dados protegidos no Supabase</span></div>',
            unsafe_allow_html=True,
        )
