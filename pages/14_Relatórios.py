import pandas as pd
import streamlit as st
from auth import exigir_login
from components.theme import aplicar_tema
from database.db import listar_despesas, listar_holerites, listar_receitas

aplicar_tema(); exigir_login()
st.title("📑 Relatórios")
st.caption("Exporte seu histórico financeiro e acompanhe a evolução mensal.")
receitas = [{"data": item["data"], "categoria": item["categoria"], "descricao": item["descricao"], "valor": item["valor"]} for item in listar_receitas()]
despesas = [{"data": item["data"], "categoria": item["categoria"], "descricao": item["descricao"], "valor": item["valor"]} for item in listar_despesas()]
df_receitas = pd.DataFrame(receitas, columns=["data", "categoria", "descricao", "valor"])
df_despesas = pd.DataFrame(despesas, columns=["data", "categoria", "descricao", "valor"])
movimentos=[]
for item in receitas: movimentos.append({"tipo":"Receita", **item})
for item in despesas: movimentos.append({"tipo":"Despesa", **item, "valor":-item["valor"]})
df=pd.DataFrame(movimentos)
st.subheader("Exportar lançamentos")
c_receitas, c_despesas = st.columns(2)
with c_receitas:
    st.download_button(
        "Baixar receitas CSV",
        df_receitas.to_csv(index=False).encode("utf-8-sig"),
        "financeos_receitas.csv",
        "text/csv",
        use_container_width=True,
    )
with c_despesas:
    st.download_button(
        "Baixar despesas CSV",
        df_despesas.to_csv(index=False).encode("utf-8-sig"),
        "financeos_despesas.csv",
        "text/csv",
        use_container_width=True,
    )

if not df.empty:
    st.subheader("Histórico financeiro")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.bar_chart(df.assign(mes=df['data'].str[:7]).groupby(['mes','tipo'])['valor'].sum().unstack(fill_value=0))
holerites=listar_holerites()
if holerites: st.subheader("Histórico de salários"); st.dataframe(pd.DataFrame([dict(x) for x in holerites]),use_container_width=True,hide_index=True)
