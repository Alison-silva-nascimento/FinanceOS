"""Área administrativa exclusiva do proprietário do FinanceOS."""

import streamlit as st

from auth import exigir_admin, resetar_senha_admin
from components.theme import aplicar_tema
from database.db import listar_eventos_admin, listar_usuarios_admin


aplicar_tema()
exigir_admin()

usuarios = listar_usuarios_admin()
por_id = {item["id"]: item for item in usuarios}

st.title("🛡️ Administração")
st.caption("Gerencie contas e consulte a trilha de atividades. Dados financeiros individuais não são exibidos nesta área.")

total_usuarios = len(usuarios)
ativos = sum(1 for item in usuarios if item["ultimo_login"])
bloqueados = sum(1 for item in usuarios if item["bloqueado_ate"])
c1, c2, c3 = st.columns(3)
c1.metric("Usuários cadastrados", total_usuarios)
c2.metric("Com acesso registrado", ativos)
c3.metric("Contas bloqueadas", bloqueados)

aba_usuarios, aba_logs, aba_senhas = st.tabs(["Usuários", "Logs de atividade", "Redefinir senha"])

with aba_usuarios:
    st.subheader("Contas criadas")
    linhas = [
        {
            "nome": item["nome"],
            "usuário": f"@{item['usuario']}",
            "perfil": "Administrador" if item["perfil"] == "admin" else "Usuário",
            "criado em": item["criado_em"] or "-",
            "último acesso": item["ultimo_login"] or "Ainda não acessou",
            "eventos": item["eventos_registrados"],
            "situação": "Bloqueado" if item["bloqueado_ate"] else "Ativo",
        }
        for item in usuarios
    ]
    st.dataframe(linhas, use_container_width=True, hide_index=True)

with aba_logs:
    st.subheader("Atividades registradas")
    opcoes = {"Todos os usuários": None}
    opcoes.update({f"{item['nome']} · @{item['usuario']}": item["id"] for item in usuarios})
    filtro = st.selectbox("Filtrar por usuário", list(opcoes), key="admin_filtro_logs")
    eventos = listar_eventos_admin(opcoes[filtro])
    if not eventos:
        st.info("Não há atividades registradas para este filtro.")
    else:
        st.dataframe(
            [
                {
                    "quando": evento["criado_em"],
                    "usuário": f"{evento['nome']} (@{evento['usuario']})",
                    "atividade": evento["acao"],
                    "detalhes": evento["detalhes"] or "-",
                }
                for evento in eventos
            ],
            use_container_width=True,
            hide_index=True,
        )

with aba_senhas:
    st.subheader("Redefinir senha de usuário")
    destinatarios = [item for item in usuarios if item["usuario"].lower() != "alison.nascimento"]
    if not destinatarios:
        st.info("Ainda não há outra conta cadastrada.")
    else:
        mapa_destinatarios = {f"{item['nome']} · @{item['usuario']}": item["usuario"] for item in destinatarios}
        with st.form("admin_reset_senha"):
            selecionado = st.selectbox("Usuário", list(mapa_destinatarios))
            nova_senha = st.text_input("Nova senha temporária", type="password", help="Mínimo de 10 caracteres, com maiúscula, minúscula e número ou símbolo.")
            confirmacao = st.text_input("Confirmar nova senha", type="password")
            redefinir = st.form_submit_button("Redefinir senha", type="primary", use_container_width=True)
        if redefinir:
            if nova_senha != confirmacao:
                st.error("As senhas não coincidem.")
            else:
                sucesso, mensagem = resetar_senha_admin(mapa_destinatarios[selecionado], nova_senha)
                (st.success if sucesso else st.error)(mensagem)
                if sucesso:
                    st.rerun()

