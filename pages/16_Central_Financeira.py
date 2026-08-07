from datetime import date

import pandas as pd
import streamlit as st

from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import (alertas_financeiros, desfazer_importacao, excluir_regra_categoria,
                         fechar_mes, listar_fechamentos, listar_importacoes,
                         listar_regras_categoria, projecao_parcelas, registrar_evento,
                         resumo_fechamento, salvar_regra_categoria)

aplicar_tema(); exigir_login()
st.title("🧭 Central Financeira")
st.caption("Importações, fechamento mensal, regras inteligentes, parcelas futuras e alertas em um só lugar.")

tab_importacoes, tab_fechamento, tab_regras, tab_parcelas, tab_alertas = st.tabs([
    "Importações", "Fechamento", "Categorias", "Parcelas futuras", "Alertas"
])

with tab_importacoes:
    importacoes = listar_importacoes()
    if not importacoes:
        st.info("Nenhuma importação registrada após a atualização.")
    for item in importacoes:
        titulo = f"{item['criado_em']} · {item['origem']} · {item['quantidade']} item(ns) · {item['status']}"
        with st.expander(titulo):
            st.caption(f"Tipo: {item['tipo']} · Competência: {item['competencia'] or '-'} · Cartão: {item['cartao_nome'] or '-'}")
            if item["status"] != "desfeita":
                confirmacao = st.checkbox("Confirmo que desejo desfazer este lote", key=f"conf_imp_{item['id']}")
                if st.button("Desfazer importação", disabled=not confirmacao, key=f"undo_{item['id']}"):
                    try:
                        removidos = desfazer_importacao(item["id"])
                        registrar_evento(st.session_state["usuario_id"], "Importação desfeita", f"Lote {item['id']} · {removidos} registro(s)")
                        st.success(f"{removidos} registro(s) removido(s)."); st.rerun()
                    except ValueError as erro: st.error(str(erro))

with tab_fechamento:
    competencia = st.text_input("Competência", value=date.today().strftime("%Y-%m"), key="mes_fechamento")
    resumo = resumo_fechamento(competencia)
    a,b,c,d = st.columns(4)
    a.metric("Receitas", moeda(resumo["receitas"])); b.metric("Despesas", moeda(resumo["despesas"]))
    c.metric("Faturas", moeda(resumo["faturas"])); d.metric("Saldo", moeda(resumo["saldo"]))
    if resumo["pendencias"]: st.warning(f"Há {resumo['pendencias']} movimentação(ões) sem conciliação neste mês.")
    observacoes = st.text_area("Observações do fechamento")
    if st.button("Fechar mês", type="primary", disabled=bool(resumo["pendencias"])):
        try:
            fechar_mes(competencia, observacoes); registrar_evento(st.session_state["usuario_id"], "Mês fechado", competencia); st.success("Fechamento salvo.")
        except ValueError as erro: st.error(str(erro))
    fechamentos = listar_fechamentos()
    if fechamentos: st.dataframe(pd.DataFrame([dict(x) for x in fechamentos]), hide_index=True, use_container_width=True)

with tab_regras:
    st.caption("As regras podem ser usadas para padronizar categorias de estabelecimentos recorrentes.")
    with st.form("regra_categoria", clear_on_submit=True):
        termo = st.text_input("Texto contido na descrição", placeholder="Ex.: ifood")
        categoria = st.text_input("Categoria", placeholder="Ex.: Alimentação")
        salvar = st.form_submit_button("Salvar regra")
    if salvar and termo.strip() and categoria.strip(): salvar_regra_categoria(termo, categoria); st.rerun()
    for regra in listar_regras_categoria():
        a,b = st.columns([5,1]); a.write(f"**{regra['termo']}** → {regra['categoria']}")
        if b.button("Excluir", key=f"del_regra_{regra['id']}"): excluir_regra_categoria(regra["id"]); st.rerun()

with tab_parcelas:
    parcelas = projecao_parcelas()
    if parcelas:
        df = pd.DataFrame(parcelas); st.bar_chart(df.set_index("competencia")); st.dataframe(df, hide_index=True, use_container_width=True)
    else: st.info("Não há parcelas futuras em aberto.")

with tab_alertas:
    alertas = alertas_financeiros()
    if not alertas: st.success("Nenhum alerta financeiro relevante no momento.")
    for alerta in alertas:
        (st.error if alerta["nivel"] == "Crítico" else st.warning)(f"{alerta['nivel']}: {alerta['mensagem']}")
