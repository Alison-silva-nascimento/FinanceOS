import streamlit as st

from auth import alterar_senha, exigir_login, obter_perfil, salvar_foto_perfil
from components.theme import aplicar_tema
from database.db import listar_eventos_seguranca


aplicar_tema()
exigir_login()

usuario = st.session_state.get("usuario")
dados = obter_perfil(usuario)

st.title("👤 Meu perfil")
st.caption("Gerencie sua foto e sua sessão no FinanceOS.")

foto, informacoes = st.columns([1, 2])
with foto:
    if dados and dados["foto_perfil"]:
        st.image(dados["foto_perfil"], width=150)
    else:
        st.markdown("# 👤")
with informacoes:
    st.subheader(dados["nome"] if dados else usuario)
    st.caption(f"@{usuario}")
    if dados and dados["perfil"] == "admin":
        st.success("Administrador")

st.divider()
st.subheader("Foto de perfil")
arquivo = st.file_uploader("Adicionar ou trocar foto", type=["png", "jpg", "jpeg", "webp"])
if arquivo and st.button("Salvar foto", type="primary"):
    sucesso, mensagem = salvar_foto_perfil(usuario, arquivo.getvalue())
    (st.success if sucesso else st.error)(mensagem)
    if sucesso:
        st.rerun()

st.divider()
st.subheader("Segurança")
st.caption(f"Último acesso: {dados['ultimo_login'].replace('T', ' ') if dados and dados['ultimo_login'] else 'ainda não registrado'}")
with st.expander("Alterar senha"):
    with st.form("alterar_senha"):
        senha_atual = st.text_input("Senha atual", type="password")
        nova_senha = st.text_input("Nova senha", type="password", help="Use pelo menos 10 caracteres.")
        confirmar_senha = st.text_input("Confirmar nova senha", type="password")
        alterar = st.form_submit_button("Atualizar senha", type="primary", use_container_width=True)
    if alterar:
        if nova_senha != confirmar_senha:
            st.error("As novas senhas não coincidem.")
        else:
            sucesso, mensagem = alterar_senha(usuario, senha_atual, nova_senha)
            (st.success if sucesso else st.error)(mensagem)

with st.expander("Atividade recente"):
    eventos = listar_eventos_seguranca()
    if not eventos:
        st.caption("Nenhuma atividade de segurança registrada ainda.")
    for evento in eventos:
        st.caption(f"{evento['criado_em']} · {evento['acao']}")

st.divider()
st.subheader("Sessão")
if st.button("Sair da conta", use_container_width=True):
    st.session_state.clear()
    st.rerun()
