import calendar
from base64 import b64encode
from datetime import date, datetime
from html import escape

import streamlit as st

from auth import obter_perfil, validar_sessao_atual
from config import APP_NAME, APP_VERSION, AUTHOR, LAYOUT, PAGE_ICON, PAGE_TITLE, SIDEBAR_STATE
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import (
    criar_banco, fatura_cartao, listar_bancos, listar_cartoes, listar_despesas,
    listar_metas, listar_orcamentos, listar_receitas, listar_recorrencias,
    proximos_vencimentos, gerar_recorrencias,
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

if st.session_state.logado and not validar_sessao_atual():
    st.session_state.clear()
    st.rerun()

if not st.session_state.logado:
    tela_login()
    st.stop()



hoje = date.today()
mes_atual = hoje.strftime("%Y-%m")
# As contas recorrentes passam a integrar o painel assim que o usuário abre o
# FinanceOS no novo mês. A função controla `ultimo_mes`, portanto não duplica.
gerar_recorrencias(mes_atual)
receitas_cadastradas = listar_receitas()
receitas = [item for item in receitas_cadastradas if str(item["data"]).startswith(mes_atual)]
despesas = [item for item in listar_despesas() if str(item["data"]).startswith(mes_atual)]
total_receitas = sum(item["valor"] for item in receitas)
saldo_disponivel = total_receitas
total_despesas = sum(item["valor"] for item in despesas)
saldo = total_receitas - total_despesas
vencimentos = proximos_vencimentos()
cartoes = listar_cartoes()
orcamentos = listar_orcamentos(mes_atual)
metas = listar_metas()
recorrencias_pendentes = [item for item in listar_recorrencias() if item["ultimo_mes"] != mes_atual]


def fatura_aberta_do_mes(cartao_id):
    """Compatibilidade temporária com instalações ainda não migradas do banco."""
    try:
        return fatura_cartao(cartao_id, mes_atual)
    except TypeError:
        return fatura_cartao(cartao_id)

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
    fatura = fatura_aberta_do_mes(cartao["id"])
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
try:
    perfil_usuario = obter_perfil(st.session_state.get("usuario"))
    primeiro_nome = (perfil_usuario["nome"] or "").strip().split()[0]
except Exception:
    perfil_usuario = None
    primeiro_nome = ""
saudacao_personalizada = f"{saudacao}, {escape(primeiro_nome)}" if primeiro_nome else saudacao


def avatar_hero(foto):
    """Retorna um avatar seguro para o card inicial, a partir da foto armazenada."""
    if not foto:
        return "<span class='home-avatar home-avatar--fallback' aria-hidden='true'>👤</span>"
    conteudo = bytes(foto)
    if conteudo.startswith(b"\x89PNG"):
        mime = "image/png"
    elif conteudo.startswith(b"\xff\xd8\xff"):
        mime = "image/jpeg"
    elif conteudo.startswith(b"RIFF") and conteudo[8:12] == b"WEBP":
        mime = "image/webp"
    else:
        return "<span class='home-avatar home-avatar--fallback' aria-hidden='true'>👤</span>"
    imagem = b64encode(conteudo).decode("ascii")
    return f"<img class='home-avatar' src='data:{mime};base64,{imagem}' alt='Foto de perfil'>"


avatar_usuario = avatar_hero(perfil_usuario["foto_perfil"] if perfil_usuario else None)

st.markdown("""
<style>
.block-container, [data-testid="stMainBlockContainer"] { max-width: 1440px !important; padding-top: 2rem; }
.home-hero { position: relative; overflow:hidden; padding: clamp(1.35rem, 2.5vw, 2rem); margin: .4rem 0 1.35rem; border: 1px solid rgba(96,165,250,.35); border-radius: 20px; background:linear-gradient(120deg,rgba(29,78,216,.52),rgba(67,56,202,.38) 56%,rgba(109,40,217,.32)); box-shadow:0 18px 42px rgba(0,0,0,.2); }
.home-hero::after { content:""; position:absolute; width:15rem; height:15rem; right:-5rem; top:-8rem; border-radius:50%; background:rgba(191,219,254,.13); box-shadow:-4rem 8rem 0 rgba(167,139,250,.09); pointer-events:none; }
.home-hero__top { position:relative; z-index:1; display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
.home-avatar { width: 84px; height: 84px; flex: 0 0 84px; border: 2px solid rgba(255,255,255,.62); border-radius: 50%; object-fit: cover; box-shadow: 0 8px 20px rgba(0,0,0,.2); }
.home-avatar--fallback { display: inline-flex; align-items: center; justify-content: center; background: rgba(15,23,42,.36); font-size: 1.5rem; }
.home-hero p { position:relative; z-index:1; margin: .35rem 0 0; color: #dbeafe; }
.home-eyebrow { display: none; }
.quick-link a { min-height: 86px; display: flex; align-items: center; justify-content: center; text-align: center; font-weight: 650; border-radius: 14px; }
@media (min-width: 701px) {
  .home-avatar { position: absolute; top: 50%; right: 16%; width: 150px; height: 150px; flex-basis: 150px; margin: 0; transform: translateY(-50%); border: 3px solid rgba(255,255,255,.78); outline: 5px solid rgba(96,165,250,.15); box-shadow: 0 0 0 10px rgba(139,92,246,.10), 0 16px 30px rgba(0,0,0,.3); }
}
@media (min-width: 1200px) { .home-hero { min-height: 142px; display: flex; flex-direction: column; justify-content: center; } }
@media (max-width: 700px) {
  .home-hero { padding: 1.35rem 1.2rem; border-radius: 18px; margin: 0 0 1rem; background:linear-gradient(120deg,rgba(29,78,216,.52),rgba(67,56,202,.38) 56%,rgba(109,40,217,.32)); }
  .home-hero__top { align-items: flex-end; gap: .7rem; }
  .home-eyebrow { display: block; margin-bottom: .7rem; color: #bfdbfe; font-size: .67rem; font-weight: 780; letter-spacing: .12em; }
  .home-hero h2 { margin: 0 !important; font-size: clamp(1.35rem, 6vw, 1.8rem) !important; letter-spacing: -.035em; }
  .home-hero p { max-width: 28ch; margin-top: .6rem; font-size: .93rem; line-height: 1.5; }
  .home-avatar { width: 42px; height: 42px; flex-basis: 42px; }
  .st-key-home-kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child [data-testid="stMetric"],
  .st-key-home-kpis [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child [data-testid="stMetric"] { min-height: 128px; padding: 1.15rem; border-color: rgba(96,165,250,.46); background: radial-gradient(circle at 100% 100%, rgba(96,165,250,.28), transparent 42%), linear-gradient(125deg, rgba(30,64,175,.72), rgba(67,56,202,.68)); }
  .st-key-home-kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child [data-testid="stMetricValue"],
  .st-key-home-kpis [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child [data-testid="stMetricValue"] { font-size: clamp(1.85rem, 9vw, 2.35rem) !important; }
  .st-key-home-kpis [data-testid="stMetric"] { min-height: 98px; }
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<div class='home-hero'><div class='home-hero__top'><div><span class='home-eyebrow'>VISÃO FINANCEIRA PESSOAL</span><h2>{saudacao_personalizada}</h2></div>{avatar_usuario}</div><p>Veja o que merece sua atenção e registre a próxima movimentação.</p></div>", unsafe_allow_html=True)

with st.container(key="home-kpis"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Saldo disponível", moeda(saldo_disponivel), delta=mes_atual)
    c2.metric("Despesas fixas a vencer", moeda(sum(item["valor"] for item in vencimentos)), f"{len(vencimentos)} despesa(s) fixa(s)")
    faturas_abertas = [fatura_aberta_do_mes(cartao["id"]) for cartao in cartoes]
    fatura_total = sum(faturas_abertas)
    c3.metric("Faturas em aberto", moeda(fatura_total), f"{sum(valor > 0 for valor in faturas_abertas)} cartão(ões)")

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
with st.container(key="home-bottom"):
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
