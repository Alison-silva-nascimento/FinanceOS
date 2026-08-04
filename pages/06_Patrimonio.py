import streamlit as st
from datetime import date
from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import adicionar_patrimonio, listar_patrimonio

aplicar_tema(); exigir_login()
st.title("🏠 Patrimônio")
st.caption("Registre ativos e dívidas para acompanhar seu patrimônio líquido.")

itens = listar_patrimonio()
ativos = sum(i["valor"] for i in itens if i["tipo"] == "Ativo")
passivos = sum(i["valor"] for i in itens if i["tipo"] == "Passivo")
a, b, c = st.columns(3); a.metric("Ativos", moeda(ativos)); b.metric("Dívidas", moeda(passivos)); c.metric("Patrimônio líquido", moeda(ativos-passivos))

with st.form("novo_item_patrimonio", clear_on_submit=True):
    st.subheader("Adicionar item")
    nome = st.text_input("Nome", placeholder="Ex.: Tesouro Selic, veículo ou financiamento")
    x, y, z = st.columns(3); tipo = x.selectbox("Tipo", ["Ativo", "Passivo"]); categoria = y.selectbox("Categoria", ["Investimento", "Imóvel", "Veículo", "Reserva", "Empréstimo", "Financiamento", "Outro"]); valor = z.number_input("Valor atual", min_value=0.0, step=100.0)
    salvar = st.form_submit_button("Salvar item", use_container_width=True)
if salvar and nome.strip(): adicionar_patrimonio(nome.strip(), tipo, categoria, valor, str(date.today())); st.rerun()

for item in itens:
    sinal = "−" if item["tipo"] == "Passivo" else "+"
    st.write(f"**{item['nome']}** · {item['categoria']} — {sinal} {moeda(item['valor'])}")
