import streamlit as st
from datetime import date
from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import adicionar_meta, aportar_meta, listar_metas

aplicar_tema(); exigir_login()
st.title("🎯 Metas")
st.caption("Transforme objetivos financeiros em um plano de aportes.")
with st.form("nova_meta", clear_on_submit=True):
    nome = st.text_input("Objetivo", placeholder="Ex.: Reserva de emergência")
    a, b = st.columns(2); alvo = a.number_input("Valor alvo", min_value=1.0, step=100.0); prazo = b.date_input("Prazo", value=date.today())
    cor = st.color_picker("Cor", "#3B82F6"); salvar = st.form_submit_button("Criar meta", use_container_width=True)
if salvar and nome.strip(): adicionar_meta(nome.strip(), alvo, str(prazo), cor); st.rerun()

for meta in listar_metas():
    progresso = min(meta["valor_atual"] / meta["valor_alvo"], 1.0)
    with st.container(border=True):
        st.markdown(f"### {meta['nome']}"); st.progress(progresso); st.caption(f"{moeda(meta['valor_atual'])} de {moeda(meta['valor_alvo'])} · prazo: {meta['prazo'] or 'não definido'}")
        aporte = st.number_input("Aporte", min_value=0.0, step=50.0, key=f"aporte_{meta['id']}")
        if st.button("Adicionar aporte", key=f"salvar_meta_{meta['id']}") and aporte > 0: aportar_meta(meta["id"], aporte); st.rerun()
