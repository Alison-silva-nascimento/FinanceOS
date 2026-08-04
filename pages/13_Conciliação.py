import pandas as pd
import streamlit as st
from auth import exigir_login
from components.theme import aplicar_tema
from database.db import importar_extrato, listar_conciliacoes, marcar_conciliado

aplicar_tema(); exigir_login()
st.title("🔄 Conciliação bancária")
st.caption("Importe um CSV com as colunas data, descrição e valor para conferir seu extrato.")
arquivo = st.file_uploader("Extrato CSV", type=["csv"])
if arquivo and st.button("Importar extrato", type="primary"):
    try:
        tabela = pd.read_csv(arquivo, sep=None, engine="python")
        tabela.columns = [str(c).strip().lower() for c in tabela.columns]
        obrigatorias = {"data", "descrição", "valor"}
        if not obrigatorias.issubset(tabela.columns): raise ValueError("O CSV precisa das colunas: data, descrição e valor.")
        itens = [{"data":str(x["data"]),"descricao":str(x["descrição"]),"valor":float(str(x["valor"]).replace(".","").replace(",","."))} for _,x in tabela.iterrows()]
        st.success(f"{importar_extrato(itens, arquivo.name)} lançamento(s) importado(s).")
    except Exception as erro: st.error(str(erro))
for item in listar_conciliacoes():
    a,b=st.columns([5,1]); a.write(f"{'✅' if item['conciliado'] else '⏳'} **{item['data']}** · {item['descricao']} · R$ {item['valor']:,.2f}")
    if not item['conciliado'] and b.button("Conciliar",key=f"conc_{item['id']}"): marcar_conciliado(item['id']); st.rerun()
