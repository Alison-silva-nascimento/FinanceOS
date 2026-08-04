import pandas as pd
import plotly.express as px
import streamlit as st
from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import editar_categoria_compra, listar_cartoes, listar_compras_cartao, migrar_compras_cartao

aplicar_tema(); exigir_login()
st.title("🎯 Controle de gastos do cartão")
cartoes = listar_cartoes()
if not cartoes: st.info("Cadastre um cartão ou importe uma fatura."); st.stop()
opcoes = {f"{c['nome']} · {moeda(c['limite'])}": c['id'] for c in cartoes}
escolhido = st.selectbox("Cartão", list(opcoes)); compras = listar_compras_cartao(opcoes[escolhido])
competencias = sorted({x['competencia'] or str(x['data'])[:7] for x in compras}, reverse=True)
if not competencias: st.info("Ainda não há compras importadas para este cartão."); st.stop()
competencia = st.selectbox("Fatura", competencias, format_func=lambda valor: f"Fatura {valor[5:7]}/{valor[:4]}")
abertas = [x for x in compras if not x['paga'] and (x['competencia'] or str(x['data'])[:7]) == competencia]
total = sum(x['valor'] / x['parcelas'] for x in abertas); limite = next(c['limite'] for c in cartoes if c['id'] == opcoes[escolhido])
cartao_atual = next(c for c in cartoes if c['id'] == opcoes[escolhido])
nubank = next((c for c in cartoes if "nubank" in f"{c['nome']} {c['banco']}".lower()), None)
if nubank and nubank['id'] != cartao_atual['id'] and abertas:
    st.warning(f"Esta fatura está vinculada a **{cartao_atual['nome']}**. Se ela for do Nubank, você pode corrigi-la sem perder as compras.")
    if st.button(f"Migrar fatura {competencia[5:7]}/{competencia[:4]} para {nubank['nome']}", use_container_width=True):
        total_migrado = migrar_compras_cartao(cartao_atual['id'], nubank['id'], competencia)
        st.success(f"{total_migrado} compra(s) migrada(s) para {nubank['nome']}.")
        st.rerun()
a,b,c = st.columns(3); a.metric("Fatura em aberto", moeda(total)); b.metric("Limite usado", f"{total/limite:.0%}" if limite else "—"); c.metric("Compras", len(abertas))
if abertas:
    df = pd.DataFrame([dict(x) for x in abertas]); df['parcela'] = df['valor']/df['parcelas']
    x,y = st.columns(2); x.plotly_chart(px.pie(df,names='categoria',values='parcela',hole=.58),use_container_width=True); y.plotly_chart(px.bar(df.groupby('categoria',as_index=False)['parcela'].sum(),x='categoria',y='parcela'),use_container_width=True)
    st.subheader("Revisar categorias")
    categorias = ["Alimentação","Assinaturas","Compras","Saúde","Transporte","Moradia","Lazer","Outros"]
    for compra in abertas:
        a,b,c = st.columns([5,2,1]); a.write(f"{compra['descricao']} · {moeda(compra['valor']/compra['parcelas'])}"); nova = b.selectbox("Categoria",categorias,index=categorias.index(compra['categoria']) if compra['categoria'] in categorias else len(categorias)-1,key=f"cat_{compra['id']}")
        if c.button("Salvar",key=f"salvar_{compra['id']}"): editar_categoria_compra(compra['id'],nova); st.rerun()
