import streamlit as st
from time import time

from auth import autenticar, criar_usuario, possui_usuario


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
                radial-gradient(circle at 15% 18%, rgba(37, 99, 235, .28), transparent 28rem),
                radial-gradient(circle at 88% 80%, rgba(124, 58, 237, .22), transparent 26rem),
                linear-gradient(135deg, #090f1f 0%, #0b1224 48%, #11142a 100%);
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
            border: 1px solid rgba(147, 197, 253, .32);
            border-radius: 999px;
            background: rgba(30, 64, 175, .20);
            color: #bfdbfe;
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
            color: #60a5fa;
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
            border: 1px solid rgba(148, 163, 184, .26) !important;
            border-radius: 22px !important;
            background: rgba(15, 23, 42, .72) !important;
            box-shadow: 0 25px 65px rgba(0, 0, 0, .32);
            backdrop-filter: blur(18px);
        }

        div[data-testid="stForm"] [data-testid="stWidgetLabel"] p {
            color: #dbeafe;
            font-size: .82rem;
            font-weight: 650;
        }

        div[data-testid="stForm"] input {
            min-height: 2.9rem;
            border: 1px solid rgba(148, 163, 184, .25) !important;
            border-radius: 10px !important;
            background: rgba(30, 41, 59, .78) !important;
            color: #f8fafc !important;
        }

        div[data-testid="stForm"] input:focus {
            border-color: #60a5fa !important;
            box-shadow: 0 0 0 3px rgba(96, 165, 250, .18) !important;
        }

        div[data-testid="stFormSubmitButton"] button {
            min-height: 2.9rem;
            border: 0 !important;
            border-radius: 10px !important;
            background: linear-gradient(100deg, #2563eb, #7c3aed) !important;
            color: white !important;
            font-weight: 750 !important;
            box-shadow: 0 10px 25px rgba(37, 99, 235, .28);
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

        @media (max-width: 700px) {
            [data-testid="stMainBlockContainer"] { padding-top: 3.5rem; }
            div[data-testid="stForm"] { padding: 1.25rem !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, coluna, _ = st.columns([1, 1.35, 1])

    with coluna:
        st.markdown(
            """
            <div class="login-eyebrow">✦ &nbsp; Gestão financeira pessoal</div>
            <div class="login-title">Seu dinheiro,<br><span>com clareza.</span></div>
            <div class="login-description">
                Organize receitas, despesas e objetivos em um só lugar, com controle e privacidade.
            </div>
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
                        st.session_state.logado = True
                        st.session_state.usuario = usuario.strip()
                        st.rerun()
                    st.error(mensagem) if not sucesso else None
            st.markdown(
                '<div class="login-trust"><span>🔒 Senha protegida</span><span>•</span><span>Dados locais</span></div>',
                unsafe_allow_html=True,
            )
            return

        with st.form("login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

        if entrar:
            bloqueado_ate = st.session_state.get("bloqueado_ate", 0)
            if time() < bloqueado_ate:
                st.error("Muitas tentativas. Aguarde um minuto e tente novamente.")
            elif autenticar(usuario, senha):
                st.session_state.logado = True
                st.session_state.usuario = usuario.strip()
                st.session_state.tentativas_login = 0
                st.rerun()
            else:
                tentativas = st.session_state.get("tentativas_login", 0) + 1
                st.session_state.tentativas_login = tentativas
                if tentativas >= 5:
                    st.session_state.bloqueado_ate = time() + 60
                    st.session_state.tentativas_login = 0
                    st.error("Muitas tentativas. Aguarde um minuto e tente novamente.")
                else:
                    st.error("Usuário ou senha inválidos.")

        st.markdown(
            '<div class="login-trust"><span>🔒 Acesso protegido</span><span>•</span><span>Dados armazenados localmente</span></div>',
            unsafe_allow_html=True,
        )
