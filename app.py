import calendar
from datetime import date, datetime

import streamlit as st

from config import APP_NAME, APP_VERSION, AUTHOR, LAYOUT, PAGE_ICON, PAGE_TITLE, SIDEBAR_STATE
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import (
    criar_banco, fatura_cartao, listar_bancos, listar_cartoes, listar_despesas,
    listar_metas, listar_orcamentos, listar_receitas, listar_recorrencias,
    proximos_vencimentos,
)
from login import tela_login


if "logado" not in st.session_state:
    st.session_state.logado = False

st.set_page_config(
    page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE if st.session_state.logado else "collapsed",
)
criar_banco()
aplicar_tema()

if not st.session_state.logado:
    tela_login()
    st.stop()



hoje = date.today()
mes_atual = hoje.strftime("%Y-%m")
receitas = [item for item in listar_receitas() if str(item["data"]).startswith(mes_atual)]
despesas = [item for item in listar_despesas() if str(item["data"]).startswith(mes_atual)]
total_receitas = sum(item["valor"] for item in receitas)
total_despesas = sum(item["valor"] for item in despesas)
saldo = total_receitas - total_despesas
vencimentos = proximos_vencimentos()
cartoes = listar_cartoes()
orcamentos = listar_orcamentos(mes_atual)
metas = listar_metas()
recorrencias_pendentes = [item for item in listar_recorrencias() if item["ultimo_mes"] != mes_atual]

alertas = []
if saldo < 0:
    alertas.append(("error", "Saldo negativo", f"Suas despesas superam as receitas em {moeda(abs(saldo))} neste mês."))
for item in orcamentos:
    gasto = sum(despesa["valor"] for despesa in despesas if despesa["categoria"] == item["categoria"])
    uso = gasto / item["limite"] if item["limite"] else 0
    if uso >= 1:
        alertas.append(("error", f"Orçamento estourado: {item['categoria']}", f"Você usou {uso:.0%} do limite de {moeda(item['limite'])}."))
    elif uso >= 0.8:
        alertas.append(("warning", f"Orçamento perto do limite: {item['categoria']}", f"Você já usou {uso:.0%} do orçamento mensal."))
for cartao in cartoes:
    fatura = fatura_cartao(cartao["id"])
    uso = fatura / cartao["limite"] if cartao["limite"] else 0
    if uso >= 0.7:
        alertas.append(("warning", f"Limite do cartão em {uso:.0%}", f"{cartao['nome']}: fatura em aberto de {moeda(fatura)}."))
for vencimento in vencimentos:
    dias = (vencimento["data"] - hoje).days
    if dias <= 3:
        prazo = "vence hoje" if dias == 0 else f"vence em {dias} dia(s)"
        alertas.append(("warning", f"Conta próxima do vencimento", f"{vencimento['descricao']} {prazo}: {moeda(vencimento['valor'])}."))
for meta in metas:
    if not meta["prazo"] or meta["valor_atual"] >= meta["valor_alvo"]:
        continue
    try:
        dias = (datetime.strptime(meta["prazo"], "%Y-%m-%d").date() - hoje).days
        if 0 <= dias <= 30:
            alertas.append(("info", f"Meta próxima do prazo: {meta['nome']}", f"Faltam {dias} dia(s) e {moeda(meta['valor_alvo'] - meta['valor_atual'])}."))
    except ValueError:
        pass

hora = datetime.now().hour
saudacao = "☀️ Bom dia" if 7 <= hora <= 11 else "🌤️ Boa tarde" if 12 <= hora <= 18 else "🌙 Boa noite"

st.markdown("""
<style>
.block-container { max-width: 1180px; padding-top: 2rem; }
.home-hero { padding: 1.5rem 1.7rem; margin: .4rem 0 1.35rem; border: 1px solid rgba(96,165,250,.28); border-radius: 20px; background: linear-gradient(120deg, rgba(30,64,175,.42), rgba(88,28,135,.32)); }
.home-hero p { margin: .35rem 0 0; color: #cbd5e1; }
.quick-link a { min-height: 86px; display: flex; align-items: center; justify-content: center; text-align: center; font-weight: 650; border-radius: 14px; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"<div class='home-hero'><h2>{saudacao}</h2><p>Veja o que merece sua atenção e registre a próxima movimentação.</p></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Saldo do mês", moeda(saldo), delta=f"{mes_atual}")
c2.metric("A vencer", moeda(sum(item["valor"] for item in vencimentos)), f"{len(vencimentos)} conta(s)")
fatura_total = sum(fatura_cartao(cartao["id"]) for cartao in cartoes)
c3.metric("Faturas em aberto", moeda(fatura_total), f"{len(cartoes)} cartão(ões)")

st.subheader("⚡ Ações rápidas")
with st.container(key="quick-actions"):
    a1, a2, a3, a4, a5 = st.columns(5)
    with a1: st.page_link("pages/02_Receitas.py", label="Nova receita", icon="💰", use_container_width=True)
    with a2: st.page_link("pages/03_Despesas.py", label="Nova despesa", icon="💸", use_container_width=True)
    with a3: st.page_link("pages/11_Transferencias.py", label="Transferir", icon="↔️", use_container_width=True)
    with a4: st.page_link("pages/04_Cartoes.py", label="Compra no cartão", icon="💳", use_container_width=True)
    with a5: st.page_link("pages/12_Holerite.py", label="Importar holerite", icon="📄", use_container_width=True)

st.divider()
st.subheader(f"🔔 Central de alertas · {len(alertas)}")
if not alertas:
    st.success("Tudo sob controle. Não há alertas financeiros para este momento.")
else:
    for nivel, titulo, texto in alertas[:3]:
        getattr(st, nivel)(f"**{titulo}** — {texto}")
    if len(alertas) > 3:
        with st.expander(f"Ver mais {len(alertas) - 3} alerta(s)"):
            for nivel, titulo, texto in alertas[3:]:
                getattr(st, nivel)(f"**{titulo}** — {texto}")

st.divider()
esquerda, direita = st.columns(2)
with esquerda:
    st.subheader("📅 Próximos vencimentos")
    if not vencimentos:
        st.info("Cadastre recorrências para receber avisos de vencimento.")
    else:
        for item in vencimentos[:4]:
            st.write(f"**{item['data'].strftime('%d/%m')} · {item['descricao']}**")
            st.caption(f"{item['categoria']} · {moeda(item['valor'])}")
with direita:
    st.subheader("✅ Próximo passo")
    if recorrencias_pendentes:
        st.info(f"Você tem {len(recorrencias_pendentes)} recorrência(s) para gerar em {mes_atual}.")
        st.page_link("pages/10_Recorrencias.py", label="Gerar lançamentos", icon="🔁")
    elif not metas:
        st.info("Defina uma meta para transformar sua economia em um objetivo concreto.")
        st.page_link("pages/07_Metas.py", label="Criar uma meta", icon="🎯")
    elif not listar_bancos():
        st.info("Cadastre uma conta bancária para acompanhar seu saldo disponível.")
        st.page_link("pages/05_Bancos.py", label="Cadastrar conta", icon="🏦")
    else:
        st.success("Sua base está organizada. Use o Dashboard para acompanhar a evolução do mês.")
        st.page_link("pages/01_Dashboard.py", label="Abrir Dashboard", icon="📊")

st.caption(f"{APP_NAME} {APP_VERSION} · {AUTHOR}")
