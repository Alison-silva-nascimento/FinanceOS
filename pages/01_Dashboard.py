import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime

from database.db import (
    listar_receitas,
    listar_despesas,
    proximos_vencimentos,
    listar_bancos,
    listar_holerites,
    listar_metas,
    listar_patrimonio,
    projecao_mes,
    gastos_cartao_categoria,
)

from components.cards import kpi_card
from components.formatadores import moeda
from components.theme import aplicar_tema
from auth import exigir_login

# ======================================================
# CONFIGURAÇÃO
# ======================================================

st.set_page_config(
    page_title="FinanceOS",
    page_icon="📊",
    layout="wide"
)
aplicar_tema()
exigir_login()

# ======================================================
# CSS
# ======================================================

st.markdown("""

<style>

.dashboard-hero { position:relative; overflow:hidden; margin:0 0 1.25rem; padding:2rem 2.15rem; border:1px solid rgba(96,165,250,.35); border-radius:22px; background:linear-gradient(120deg,rgba(29,78,216,.52),rgba(67,56,202,.38) 56%,rgba(109,40,217,.32)); box-shadow:0 18px 42px rgba(0,0,0,.2); }
.dashboard-hero::after { content:""; position:absolute; width:15rem; height:15rem; right:-5rem; top:-8rem; border-radius:50%; background:rgba(191,219,254,.13); box-shadow:-4rem 8rem 0 rgba(167,139,250,.09); }
.dashboard-hero__eyebrow { position:relative; margin-bottom:.55rem; color:#bfdbfe; font-size:.82rem; font-weight:750; letter-spacing:.09em; text-transform:uppercase; }
.dashboard-hero h1 { position:relative; margin:0 !important; font-size:2.35rem !important; }
.dashboard-hero p { position:relative; margin:.55rem 0 0; color:#dbeafe; font-size:1rem; }
.saldo-card { position:relative; overflow:hidden; display:flex; align-items:flex-end; justify-content:space-between; gap:1.5rem; margin-bottom:.4rem; padding:2rem 2.15rem; border:1px solid rgba(96,165,250,.42); border-radius:20px; background:linear-gradient(115deg,#1d4ed8 0%,#2563eb 48%,#4338ca 100%); color:white; box-shadow:0 18px 40px rgba(30,64,175,.28); }
.saldo-card::after { content:""; position:absolute; width:14rem; height:14rem; right:-4rem; bottom:-8rem; border:1px solid rgba(255,255,255,.16); border-radius:50%; box-shadow:0 0 0 2.7rem rgba(255,255,255,.05),0 0 0 5.4rem rgba(255,255,255,.035); }
.saldo-card__content,.saldo-card__summary { position:relative; z-index:1; }
.saldo-card__summary { display:flex; gap:1.4rem; padding:.85rem 1rem; border:1px solid rgba(255,255,255,.16); border-radius:13px; background:rgba(15,23,42,.18); }
.saldo-card__summary span { display:block; color:rgba(255,255,255,.72); font-size:.76rem; font-weight:650; }
.saldo-card__summary strong { display:block; margin-top:.2rem; font-size:1rem; }
.small-title { font-size:.84rem; font-weight:700; letter-spacing:.025em; opacity:.82; }
.big-money { margin-top:.35rem; font-size:clamp(2.2rem,4vw,3.2rem); font-weight:800; letter-spacing:-.055em; }
.dashboard-section { display:flex; align-items:center; gap:.65rem; margin-top:1.9rem; margin-bottom:.8rem; }
.dashboard-section h2 { margin:0 !important; font-size:1.32rem !important; }
@media (max-width: 700px) { .dashboard-hero { padding:1.45rem; border-radius:17px; } .dashboard-hero h1 { font-size:1.9rem !important; } .saldo-card { display:block; padding:1.45rem; border-radius:17px; } .saldo-card__summary { margin-top:1.25rem; gap:.85rem; } .saldo-card__summary strong { font-size:.9rem; } }

</style>

""", unsafe_allow_html=True)

# ======================================================
# DADOS
# ======================================================

receitas = listar_receitas()
despesas = listar_despesas()

mes_atual = datetime.now().strftime("%Y-%m")
mes_referencia = st.sidebar.text_input("📅 Mês do painel", value=mes_atual, help="Formato AAAA-MM")
receitas = [r for r in receitas if str(r["data"]).startswith(mes_referencia)]
despesas = [d for d in despesas if str(d["data"]).startswith(mes_referencia)]
bancos = listar_bancos()
metas = listar_metas()
patrimonio = listar_patrimonio()
holerite_mes = next((item for item in listar_holerites() if item["competencia"] == mes_referencia), None)
projecao = projecao_mes(mes_referencia)
gastos_cartao = gastos_cartao_categoria(mes_referencia)

total_receitas = sum(r["valor"] for r in receitas)

total_despesas = sum(d["valor"] for d in despesas)

saldo = total_receitas-total_despesas

economia = 0

if total_receitas>0:

    economia=(saldo/total_receitas)*100

# ======================================================
# SAUDAÇÃO
# ======================================================

hora = datetime.now().hour

if 7 <= hora <= 11:
    saudacao = "☀️ Bom dia"

elif 12 <= hora <= 18:
    saudacao = "🌤️ Boa tarde"

else:
    saudacao = "🌙 Boa noite"

st.markdown(f"""
<section class="dashboard-hero">
  <div class="dashboard-hero__eyebrow">Visão financeira pessoal</div>
  <h1>{saudacao}</h1>
  <p>Seu painel de <strong>{mes_referencia}</strong> em um só lugar.</p>
</section>
""", unsafe_allow_html=True)

# ======================================================
# CARD PRINCIPAL
# ======================================================

st.markdown(

f"""

<section class="saldo-card">
  <div class="saldo-card__content">
    <div class="small-title">Saldo do mês</div>
    <div class="big-money">{moeda(saldo)}</div>
  </div>
  <div class="saldo-card__summary">
    <div><span>Receitas</span><strong>{moeda(total_receitas)}</strong></div>
    <div><span>Despesas</span><strong>{moeda(total_despesas)}</strong></div>
  </div>
</section>

""",

unsafe_allow_html=True

)

st.write("")

# ======================================================
# KPIs
# ======================================================

c1,c2,c3,c4=st.columns(4)

with c1:

    kpi_card(

        "Receitas",

        moeda(total_receitas),

        "💰",

        "#166534"

    )

with c2:

    kpi_card(

        "Despesas",

        moeda(total_despesas),

        "💸",

        "#B91C1C"

    )

with c3:

    kpi_card(

        "Saldo",

        moeda(saldo),

        "💵",

        "#2563EB"

    )

with c4:

    kpi_card(

        "Economia",

        f"{economia:.1f}%",

        "📈",

        "#7C3AED"

    )

if holerite_mes:
    descontos_folha = [
        ("INSS", holerite_mes["inss"]),
        ("IRRF", holerite_mes["irrf"]),
        ("Consignado", holerite_mes["consignado"]),
        ("PAT", holerite_mes["pat"]),
        ("Unimed", holerite_mes["unimed"]),
        ("Outros descontos", holerite_mes["outros_descontos"]),
    ]
    descontos_folha = [(nome, valor) for nome, valor in descontos_folha if valor > 0]
    total_descontos_folha = sum(valor for _, valor in descontos_folha)
    percentual_descontos = (total_descontos_folha / holerite_mes["salario_bruto"] * 100) if holerite_mes["salario_bruto"] else 0

    st.divider()
    st.subheader("🧾 Folha salarial")
    st.caption(f"Detalhamento do holerite de {mes_referencia}. FGTS é exibido separadamente porque não reduz o salário líquido.")
    folha_a, folha_b, folha_c, folha_d = st.columns(4)
    folha_a.metric("Salário bruto", moeda(holerite_mes["salario_bruto"]))
    folha_b.metric("Descontos", moeda(total_descontos_folha), f"{percentual_descontos:.1f}% do bruto")
    folha_c.metric("Salário líquido", moeda(holerite_mes["salario_liquido"]))
    folha_d.metric("FGTS do mês", moeda(holerite_mes["fgts"]), "Depósito do empregador")

    if descontos_folha:
        grafico_folha, detalhes_folha = st.columns([1, 1])
        with grafico_folha:
            df_folha = pd.DataFrame(descontos_folha, columns=["Desconto", "Valor"])
            fig_folha = px.pie(df_folha, names="Desconto", values="Valor", hole=.58)
            fig_folha.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0", margin=dict(l=10, r=10, t=20, b=10), height=310)
            st.plotly_chart(fig_folha, use_container_width=True)
        with detalhes_folha:
            st.markdown("#### Descontos identificados")
            for nome, valor in descontos_folha:
                percentual = valor / total_descontos_folha * 100 if total_descontos_folha else 0
                st.write(f"**{nome}** · {moeda(valor)}")
                st.progress(percentual / 100, text=f"{percentual:.1f}% dos descontos")

st.divider()

if gastos_cartao:
    st.subheader("💳 Fatura em aberto por categoria")
    df_cartao = pd.DataFrame([dict(item) for item in gastos_cartao])
    st.plotly_chart(px.bar(df_cartao, x="categoria", y="valor", color="categoria", text_auto=".2s"), use_container_width=True)
    st.caption("Revise as categorias em Controle de gastos do cartão para tornar esta visão mais precisa.")
    st.divider()

st.subheader("🔮 Projeção até o fim do mês")
p1,p2,p3=st.columns(3)
p1.metric("Receitas previstas", moeda(projecao["previstas_receita"]))
p2.metric("Despesas previstas", moeda(projecao["previstas_despesa"]))
p3.metric("Saldo projetado", moeda(projecao["saldo_projetado"]))

st.divider()

# ======================================================
# RESUMO DO MÊS
# ======================================================

st.subheader("📌 Resumo do mês")

r1,r2,r3=st.columns(3)

with r1:

    st.success(

        f"""

### 💰 Receitas

{moeda(total_receitas)}

"""

    )

with r2:

    st.error(

        f"""

### 💸 Despesas

{moeda(total_despesas)}

"""

    )

with r3:

    if saldo>=0:

        st.success(

            f"""

### 📈 Você economizou

{moeda(saldo)}

"""

        )

    else:

        st.error(

            f"""

### 📉 Déficit

{moeda(abs(saldo))}

"""

        )

st.divider()

# ======================================================
# VISÃO FINANCEIRA
# ======================================================

st.subheader("📈 Visão Financeira")

col1, col2 = st.columns(2)

# -----------------------------------------
# BARRAS
# -----------------------------------------

with col1:

    df_bar = pd.DataFrame({

        "Tipo": [
            "Receitas",
            "Despesas",
            "Saldo"
        ],

        "Valor": [
            total_receitas,
            total_despesas,
            saldo
        ]

    })

    fig = px.bar(

        df_bar,

        x="Tipo",

        y="Valor",

        text_auto=".2s",

        color="Tipo",

        color_discrete_map={

            "Receitas":"#16A34A",

            "Despesas":"#DC2626",

            "Saldo":"#2563EB"

        }

    )

    fig.update_layout(

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        showlegend=False,

        margin=dict(l=10,r=10,t=20,b=10),

        height=380

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

# -----------------------------------------
# PIZZA
# -----------------------------------------

with col2:

    df_pie = pd.DataFrame({

        "Tipo":[

            "Receitas",

            "Despesas"

        ],

        "Valor":[

            total_receitas,

            total_despesas

        ]

    })

    fig = px.pie(

        df_pie,

        names="Tipo",

        values="Valor",

        hole=.65,

        color="Tipo",

        color_discrete_map={

            "Receitas":"#16A34A",

            "Despesas":"#DC2626"

        }

    )

    fig.update_layout(

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        height=380,

        margin=dict(l=10,r=10,t=20,b=10)

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

st.divider()

# ======================================================
# ÚLTIMAS MOVIMENTAÇÕES
# ======================================================

st.subheader("🧾 Últimas movimentações")

movimentos=[]

for r in receitas:

    movimentos.append({

        "Tipo":"Receita",

        "Categoria":r["categoria"],

        "Descrição":r["descricao"],

        "Valor":r["valor"],

        "Data":r["data"]

    })

for d in despesas:

    movimentos.append({

        "Tipo":"Despesa",

        "Categoria":d["categoria"],

        "Descrição":d["descricao"],

        "Valor":d["valor"],

        "Data":d["data"]

    })

movimentos=sorted(

    movimentos,

    key=lambda x:x["Data"],

    reverse=True

)

for mov in movimentos[:6]:

    icone="💰"

    cor="#16A34A"

    sinal="+"

    if mov["Tipo"]=="Despesa":

        icone="💸"

        cor="#DC2626"

        sinal="-"

    with st.container(border=True):

        a,b=st.columns([5,1])

        with a:

            st.markdown(

                f"""

### {icone} {mov['Descrição']}

**{mov['Categoria']}**

📅 {pd.to_datetime(mov['Data']).strftime('%d/%m/%Y')}

"""

            )

        with b:

            st.markdown(

                f"""

<h2 style="color:{cor};text-align:right;">

{sinal} {moeda(abs(mov["Valor"]))}

</h2>

""",

unsafe_allow_html=True

            )

st.divider()

# ======================================================
# PRÓXIMOS VENCIMENTOS
# ======================================================

c1,c2=st.columns([2,1])

with c1:

    st.subheader("📅 Próximos vencimentos")

    vencimentos = proximos_vencimentos()

    if not vencimentos:
        st.info("Cadastre contas em Recorrências para receber alertas de vencimento.")

    for d in vencimentos:

        with st.container(border=True):

            x,y=st.columns([4,1])

            with x:

                st.markdown(

                    f"### 💳 {d['descricao']}"

                )

                st.caption(

                    f"{d['data'].strftime('%d/%m/%Y')} · {d['categoria']}"

                )

            with y:

                st.markdown(

                    f"""

<h3 style="text-align:right;color:#DC2626;">

{moeda(d["valor"])}

</h3>

""",

unsafe_allow_html=True

                )

# ======================================================
# METAS
# ======================================================

with c2:

    st.subheader("🎯 Metas")
    if not metas:
        st.info("Nenhuma meta cadastrada. Acesse Metas para criar a primeira.")
    else:
        for meta in metas[:3]:
            progresso = min(meta["valor_atual"] / meta["valor_alvo"], 1) if meta["valor_alvo"] else 0
            with st.container(border=True):
                st.markdown(f"**{meta['nome']}** · {progresso:.0%}")
                st.progress(progresso)
                st.caption(f"{moeda(meta['valor_atual'])} de {moeda(meta['valor_alvo'])}")

st.divider()

# ======================================================
# BANCOS E PATRIMÔNIO
# ======================================================

c1,c2=st.columns(2)

with c1:

    st.subheader("🏦 Bancos")
    if not bancos:
        st.info("Nenhuma conta cadastrada.")
    else:
        st.metric("Saldo em contas", moeda(sum(banco["saldo"] for banco in bancos)))
        for banco in bancos[:4]:
            st.caption(f"{banco['nome']} · {moeda(banco['saldo'])}")

with c2:

    st.subheader("🏠 Patrimônio")
    if not patrimonio:
        st.info("Nenhum item cadastrado.")
    else:
        ativos = sum(item["valor"] for item in patrimonio if item["tipo"] == "Ativo")
        passivos = sum(item["valor"] for item in patrimonio if item["tipo"] == "Passivo")
        st.metric("Patrimônio líquido", moeda(ativos - passivos))
        st.caption(f"Ativos: {moeda(ativos)} · Dívidas: {moeda(passivos)}")

st.divider()

# ======================================================
# RODAPÉ
# ======================================================

st.caption(

    "FinanceOS • Dashboard Financeiro • Desenvolvido por Alison S. Nascimento"

)

