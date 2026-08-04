import streamlit as st
from datetime import date
from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import listar_bancos, transferir

aplicar_tema(); exigir_login()
st.title("↔️ Transferências")
contas = listar_bancos()
if len(contas) < 2: st.info("Cadastre pelo menos duas contas em Bancos para transferir valores."); st.stop()
opcoes = {f"{c['nome']} ({moeda(c['saldo'])})": c['id'] for c in contas}
with st.form("transferencia"):
    data=st.date_input("Data",value=date.today()); origem=st.selectbox("Origem",list(opcoes)); destino=st.selectbox("Destino",list(opcoes),index=1); valor=st.number_input("Valor",min_value=0.01,step=50.0); descricao=st.text_input("Descrição",placeholder="Ex.: reserva mensal")
    salvar=st.form_submit_button("Confirmar transferência",use_container_width=True)
if salvar:
    if origem == destino: st.error("Escolha contas diferentes.")
    elif valor > next(c['saldo'] for c in contas if c['id']==opcoes[origem]): st.error("Saldo insuficiente na conta de origem.")
    else: transferir(str(data),opcoes[origem],opcoes[destino],valor,descricao); st.success("Transferência realizada."); st.rerun()
