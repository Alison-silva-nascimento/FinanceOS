import streamlit as st

from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import (
    adicionar_banco,
    editar_banco,
    excluir_banco,
    listar_bancos,
    quantidade_bancos,
    saldo_total_bancos,
)

aplicar_tema()
exigir_login()

BANCOS = [
    "Nubank", "Inter", "Itaú", "Bradesco", "Santander", "Caixa",
    "Banco do Brasil", "Mercado Pago", "Outro",
]
TIPOS = [
    "Conta Corrente", "Conta Poupança", "Conta Digital", "Carteira", "Dinheiro",
]


st.title("🏦 Bancos")
st.caption("Cadastre, acompanhe e mantenha suas contas bancárias atualizadas.")

c1, c2 = st.columns(2)
c1.metric("🏦 Contas", quantidade_bancos())
c2.metric("💰 Saldo Total", moeda(saldo_total_bancos()))
st.divider()

with st.form("nova_conta", clear_on_submit=True):
    st.subheader("➕ Nova conta")
    nome = st.text_input("Nome da conta", placeholder="Ex.: Conta principal")
    col1, col2 = st.columns(2)
    banco = col1.selectbox("Banco", BANCOS)
    tipo = col2.selectbox("Tipo", TIPOS)
    saldo = st.number_input("Saldo inicial", value=0.0, step=100.0, format="%.2f")
    cor = st.color_picker("Cor de identificação", "#2563EB")
    salvar = st.form_submit_button("💾 Salvar conta", use_container_width=True)

if salvar:
    if not nome.strip():
        st.error("Informe um nome para a conta.")
    else:
        adicionar_banco(nome.strip(), banco, tipo, saldo, cor)
        st.toast("Conta cadastrada com sucesso!")
        st.rerun()

st.divider()
st.subheader("Minhas contas")
contas = listar_bancos()

if not contas:
    st.info("Nenhuma conta cadastrada ainda.")

for conta in contas:
    titulo = f"{conta['nome']} · {conta['banco']} · {moeda(conta['saldo'])}"
    with st.expander(titulo):
        st.caption(f"{conta['tipo']}")
        with st.form(f"editar_conta_{conta['id']}"):
            nome_editado = st.text_input("Nome da conta", value=conta["nome"])
            col1, col2 = st.columns(2)
            banco_editado = col1.selectbox(
                "Banco", BANCOS,
                index=BANCOS.index(conta["banco"]) if conta["banco"] in BANCOS else len(BANCOS) - 1,
                key=f"banco_{conta['id']}",
            )
            tipo_editado = col2.selectbox(
                "Tipo", TIPOS, index=TIPOS.index(conta["tipo"]) if conta["tipo"] in TIPOS else 0,
                key=f"tipo_{conta['id']}",
            )
            saldo_editado = st.number_input(
                "Saldo atual", value=float(conta["saldo"]), step=100.0,
                format="%.2f", key=f"saldo_{conta['id']}",
            )
            cor_editada = st.color_picker("Cor", conta["cor"], key=f"cor_{conta['id']}")
            atualizar = st.form_submit_button("Salvar alterações", use_container_width=True)

        if atualizar:
            if not nome_editado.strip():
                st.error("Informe um nome para a conta.")
            else:
                editar_banco(
                    conta["id"], nome_editado.strip(), banco_editado, tipo_editado,
                    saldo_editado, cor_editada,
                )
                st.toast("Conta atualizada com sucesso!")
                st.rerun()

        if st.button("🗑️ Excluir conta", key=f"excluir_conta_{conta['id']}"):
            excluir_banco(conta["id"])
            st.toast("Conta excluída.")
            st.rerun()
