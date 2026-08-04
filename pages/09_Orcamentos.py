import streamlit as st
from datetime import date
from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import listar_despesas_mes, listar_orcamentos, salvar_orcamento

aplicar_tema(); exigir_login()
st.title("🧭 Orçamentos")
mes = st.text_input("Mês de referência", value=date.today().strftime("%Y-%m"), help="Formato AAAA-MM")
categorias = ["Moradia","Alimentação","Transporte","Saúde","Lazer","Educação","Investimentos","Cartão","Outros"]
with st.form("orcamento"):
    cat = st.selectbox("Categoria", categorias); limite = st.number_input("Limite mensal", min_value=0.0, step=100.0); salvar = st.form_submit_button("Salvar orçamento", use_container_width=True)
if salvar: salvar_orcamento(cat, mes, limite); st.rerun()
gastos = listar_despesas_mes(mes)
for item in listar_orcamentos(mes):
    usado = sum(d["valor"] for d in gastos if d["categoria"] == item["categoria"]); porcentagem = usado/item["limite"] if item["limite"] else 0
    with st.container(border=True):
        st.markdown(f"### {item['categoria']}"); st.progress(min(porcentagem,1.0)); st.caption(f"{moeda(usado)} de {moeda(item['limite'])} · {porcentagem:.0%} usado")
