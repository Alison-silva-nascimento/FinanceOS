import streamlit as st

from auth import autenticar


def tela_login():

    st.markdown("<br><br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,2,1])

    with c2:

        st.markdown("""
        # 💰 FinanceOS

        ### Controle Financeiro

        ---
        """)

        usuario = st.text_input(
            "Usuário",
            placeholder="Digite seu usuário"
        )

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="********"
        )

        st.markdown("")

        if st.button(
            "Entrar",
            use_container_width=True
        ):

            if autenticar(usuario, senha):

                st.session_state.logado = True
                st.session_state.usuario = usuario

                st.rerun()

            else:

                st.error("Usuário ou senha inválidos")

                