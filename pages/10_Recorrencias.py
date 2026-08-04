import streamlit as st
from datetime import date
from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import adicionar_recorrencia, excluir_recorrencia, gerar_recorrencias, listar_recorrencias, pausar_recorrencia

aplicar_tema(); exigir_login()
st.title("🔁 Lançamentos recorrentes")
mes = date.today().strftime("%Y-%m")
if st.button(f"Gerar lançamentos de {mes}", type="primary"):
    total = gerar_recorrencias(mes); st.success(f"{total} lançamento(s) gerado(s).")
with st.form("recorrencia", clear_on_submit=True):
    tipo = st.selectbox("Tipo", ["Despesa","Receita"]); categoria = st.text_input("Categoria"); descricao = st.text_input("Descrição"); a,b=st.columns(2); valor=a.number_input("Valor",min_value=0.01,step=10.0); dia=b.number_input("Dia do vencimento",min_value=1,max_value=31,value=5,help="Em meses menores, será ajustado para o último dia do mês.")
    salvar=st.form_submit_button("Adicionar recorrência",use_container_width=True)
if salvar and categoria.strip(): adicionar_recorrencia(tipo,categoria,descricao,valor,dia); st.rerun()
for item in listar_recorrencias():
    a,b,c=st.columns([6,1,1]); a.write(f"**Dia {item['dia']:02d}** · {item['tipo']} · {item['descricao']} — {moeda(item['valor'])}")
    if b.button("Pausar",key=f"pausar_{item['id']}"): pausar_recorrencia(item['id']); st.rerun()
    if c.button("Excluir",key=f"excluir_{item['id']}"): excluir_recorrencia(item['id']); st.rerun()
