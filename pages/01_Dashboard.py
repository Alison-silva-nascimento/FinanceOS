import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime

from database.db import (
    listar_receitas,
    listar_despesas,
)

from components.cards import kpi_card
from components.formatadores import moeda

# ======================================================
# CONFIGURAÇÃO
# ======================================================

st.set_page_config(
    page_title="FinanceOS",
    page_icon="📊",
    layout="wide"
)

# ======================================================
# CSS
# ======================================================

st.markdown("""

<style>

.block-container{
    padding-top:2rem;
}

.card-hover{
    transition:.25s;
}

.card-hover:hover{

    transform:translateY(-4px);

    filter:brightness(1.06);

}

.saldo-card{

    background:linear-gradient(135deg,#2563EB,#1D4ED8);

    border-radius:18px;

    padding:30px;

    color:white;

    box-shadow:0 8px 20px rgba(0,0,0,.25);

}

.small-title{

    font-size:14px;

    opacity:.75;

}

.big-money{

    font-size:42px;

    font-weight:700;

}

.subtitle{

    opacity:.8;

}

</style>

""", unsafe_allow_html=True)

# ======================================================
# DADOS
# ======================================================

receitas = listar_receitas()
despesas = listar_despesas()

total_receitas = sum(r["valor"] for r in receitas)

total_despesas = sum(d["valor"] for d in despesas)

saldo = total_receitas-total_despesas

economia = 0

if total_receitas>0:

    economia=(saldo/total_receitas)*100

# ======================================================
# SAUDAÇÃO
# ======================================================

hora=datetime.now().hour

if hora<12:

    saudacao="Bom dia ☀️"

elif hora<18:

    saudacao="Boa tarde 🌤"

else:

    saudacao="Boa noite 🌙"

st.markdown(f"""

# {saudacao}

### Bem-vindo ao **FinanceOS**

""")

# ======================================================
# CARD PRINCIPAL
# ======================================================

st.markdown(

f"""

<div class="saldo-card">

<div class="small-title">

Saldo Atual

</div>

<div class="big-money">

{moeda(saldo)}

</div>

<div class="subtitle">

Receitas: {moeda(total_receitas)}
&nbsp;&nbsp;&nbsp;&nbsp;

Despesas: {moeda(total_despesas)}

</div>

</div>

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

    despesas_sort=sorted(

        despesas,

        key=lambda x:x["data"]

    )

    for d in despesas_sort[:5]:

        with st.container(border=True):

            x,y=st.columns([4,1])

            with x:

                st.markdown(

                    f"### 💳 {d['descricao']}"

                )

                st.caption(

                    pd.to_datetime(

                        d["data"]

                    ).strftime("%d/%m/%Y")

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

    with st.container(border=True):

        st.markdown(

            "### 🚧 Em desenvolvimento"

        )

        st.progress(0)

        st.caption(

            "Em breve você poderá cadastrar metas."

        )

st.divider()

# ======================================================
# BANCOS E PATRIMÔNIO
# ======================================================

c1,c2=st.columns(2)

with c1:

    st.subheader("🏦 Bancos")

    with st.container(border=True):

        st.info(

            "Nenhuma conta cadastrada."

        )

with c2:

    st.subheader("🏠 Patrimônio")

    with st.container(border=True):

        st.info(

            "Nenhum patrimônio cadastrado."

        )

st.divider()

# ======================================================
# RODAPÉ
# ======================================================

st.caption(

    "FinanceOS • Dashboard Financeiro • Desenvolvido por Alison S. Nascimento"

)

