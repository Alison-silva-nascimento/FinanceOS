import pandas as pd
import streamlit as st
from auth import exigir_login
from components.theme import aplicar_tema
from database.db import listar_despesas, listar_holerites, listar_receitas

aplicar_tema(); exigir_login()
st.title("📑 Relatórios")
st.caption("Exporte seu histórico financeiro e acompanhe a evolução mensal.")
movimentos=[]
for item in listar_receitas(): movimentos.append({"tipo":"Receita","data":item['data'],"categoria":item['categoria'],"descricao":item['descricao'],"valor":item['valor']})
for item in listar_despesas(): movimentos.append({"tipo":"Despesa","data":item['data'],"categoria":item['categoria'],"descricao":item['descricao'],"valor":-item['valor']})
df=pd.DataFrame(movimentos)
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Baixar relatório CSV",df.to_csv(index=False).encode("utf-8-sig"),"financeos_relatorio.csv","text/csv")
    st.bar_chart(df.assign(mes=df['data'].str[:7]).groupby(['mes','tipo'])['valor'].sum().unstack(fill_value=0))
holerites=listar_holerites()
if holerites: st.subheader("Histórico de salários"); st.dataframe(pd.DataFrame([dict(x) for x in holerites]),use_container_width=True,hide_index=True)
