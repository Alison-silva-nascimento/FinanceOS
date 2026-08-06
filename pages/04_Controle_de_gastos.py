import pandas as pd
import plotly.express as px
import streamlit as st
from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import (editar_categoria_compra, listar_cartoes, listar_compras_cartao,
                         listar_duplicatas_compra_cartao, migrar_compras_cartao,
                         registrar_evento, remover_duplicatas_compra_cartao,
                         remover_faturas_cartao, obter_resumo_fatura)

aplicar_tema(); exigir_login()
st.title("🎯 Controle de gastos do cartão")
cartoes = listar_cartoes()
if not cartoes: st.info("Cadastre um cartão ou importe uma fatura."); st.stop()
opcoes = {f"{c['nome']} · {moeda(c['limite'])}": c['id'] for c in cartoes}
opcoes_cartao = list(opcoes)
indice_nubank = next((indice for indice, rotulo in enumerate(opcoes_cartao) if "nubank" in rotulo.lower()), 0)
escolhido = st.selectbox("Cartão", opcoes_cartao, index=indice_nubank)
compras = listar_compras_cartao(opcoes[escolhido])
competencias = sorted({x['competencia'] or str(x['data'])[:7] for x in compras}, reverse=True)
if not competencias: st.info("Ainda não há compras importadas para este cartão."); st.stop()
competencia = st.selectbox("Fatura", competencias, format_func=lambda valor: f"Fatura {valor[5:7]}/{valor[:4]}")
abertas = [x for x in compras if not x['paga'] and (x['competencia'] or str(x['data'])[:7]) == competencia]
total = sum(x['valor'] / x['parcelas'] for x in abertas); limite = next(c['limite'] for c in cartoes if c['id'] == opcoes[escolhido])
cartao_atual = next(c for c in cartoes if c['id'] == opcoes[escolhido])
resumo_fatura = obter_resumo_fatura(cartao_atual['id'], competencia)
total_a_pagar = float(resumo_fatura['total_a_pagar']) if resumo_fatura else total
nubank = next((c for c in cartoes if "nubank" in f"{c['nome']} {c['banco']}".lower()), None)
if nubank and nubank['id'] != cartao_atual['id'] and abertas:
    st.warning(f"Esta fatura está vinculada a **{cartao_atual['nome']}**. Se ela for do Nubank, você pode corrigi-la sem perder as compras.")
    if st.button(f"Migrar fatura {competencia[5:7]}/{competencia[:4]} para {nubank['nome']}", use_container_width=True):
        total_migrado = migrar_compras_cartao(cartao_atual['id'], nubank['id'], competencia)
        st.success(f"{total_migrado} compra(s) migrada(s) para {nubank['nome']}.")
        st.rerun()

duplicatas = listar_duplicatas_compra_cartao(cartao_atual['id'], competencia)
if duplicatas:
    excesso = sum(item['quantidade'] - 1 for item in duplicatas)
    st.warning(f"Encontrei {excesso} compra(s) duplicada(s) nesta fatura. Apenas compras idênticas em todos os campos foram marcadas.")
    st.dataframe(pd.DataFrame([dict(item) for item in duplicatas]).drop(columns=['ids']), hide_index=True, use_container_width=True)
    if st.button(f"Remover {excesso} duplicata(s) e manter uma cópia", type="secondary", use_container_width=True):
        removidas = remover_duplicatas_compra_cartao(cartao_atual['id'], competencia)
        registrar_evento(st.session_state['usuario_id'], "Compras duplicadas removidas", f"{removidas} item(ns) da fatura {competencia}")
        st.success(f"{removidas} duplicata(s) removida(s).")
        st.rerun()
else:
    st.caption("✓ Nenhuma compra exatamente duplicada nesta fatura.")

with st.expander("Gerenciar faturas", expanded=False):
    st.caption("Use esta opção quando uma fatura tiver sido importada no cartão errado ou com dados incorretos. Faturas já pagas não são removidas por segurança.")
    escopo = st.radio("O que deseja remover?", ["A fatura selecionada", "Todas as faturas em aberto deste cartão"], key="escopo_remocao_fatura")
    confirmacao = st.text_input("Digite REMOVER para confirmar", key="confirmacao_remocao_fatura")
    if st.button("Remover fatura(s)", type="secondary", use_container_width=True, key="remover_faturas"):
        if confirmacao.strip().upper() != "REMOVER":
            st.error("Digite REMOVER para confirmar a exclusão.")
        else:
            competencia_remover = competencia if escopo == "A fatura selecionada" else None
            removidas = remover_faturas_cartao(cartao_atual['id'], competencia_remover)
            descricao = f"fatura {competencia}" if competencia_remover else "todas as faturas em aberto"
            registrar_evento(st.session_state['usuario_id'], "Faturas removidas", f"{removidas} compra(s): {descricao} · cartão {cartao_atual['nome']}")
            st.success(f"{removidas} compra(s) removida(s). Agora você pode importar a fatura correta.")
            st.rerun()
a,b,c,d = st.columns(4)
a.metric("Total a pagar", moeda(total_a_pagar))
b.metric("Compras do ciclo", moeda(total))
c.metric("Limite usado", f"{total_a_pagar/limite:.0%}" if limite else "—")
d.metric("Compras", len(abertas))
if resumo_fatura and abs(total_a_pagar - total) > 0.02:
    st.caption(f"Inclui {moeda(total_a_pagar - total)} de ajustes financeiros da fatura (saldo anterior, renegociação, créditos ou encargos), sem misturar esse valor às categorias de gastos.")
if abertas:
    df = pd.DataFrame([dict(x) for x in abertas]); df['parcela'] = df['valor']/df['parcelas']
    x,y = st.columns(2); x.plotly_chart(px.pie(df,names='categoria',values='parcela',hole=.58),use_container_width=True); y.plotly_chart(px.bar(df.groupby('categoria',as_index=False)['parcela'].sum(),x='categoria',y='parcela'),use_container_width=True)
    with st.expander(f"🧾 Ver gastos da fatura · {len(abertas)} compra(s)", expanded=False):
        st.caption("Abra para consultar os gastos e, se necessário, corrigir a categoria de cada compra.")
        categorias = ["Alimentação","Assinaturas","Compras","Saúde","Transporte","Moradia","Lazer","Outros"]
        if st.button("Salvar todas as categorias", type="primary", key=f"salvar_todas_{cartao_atual['id']}_{competencia}"):
            alteradas = 0
            for compra in abertas:
                categoria_escolhida = st.session_state.get(f"cat_{compra['id']}", compra["categoria"])
                if categoria_escolhida != compra["categoria"]:
                    editar_categoria_compra(compra["id"], categoria_escolhida)
                    alteradas += 1
            if alteradas:
                st.success(f"{alteradas} categoria(s) atualizada(s).")
            else:
                st.info("Não há alterações de categoria para salvar.")
            st.rerun()
        for compra in abertas:
            a,b,c = st.columns([5,2,1]); a.write(f"{compra['descricao']} · {moeda(compra['valor']/compra['parcelas'])}"); nova = b.selectbox("Categoria",categorias,index=categorias.index(compra['categoria']) if compra['categoria'] in categorias else len(categorias)-1,key=f"cat_{compra['id']}")
            if c.button("Salvar",key=f"salvar_{compra['id']}"): editar_categoria_compra(compra['id'],nova); st.rerun()
