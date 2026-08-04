import streamlit as st
from datetime import datetime

from config import LAYOUT, PAGE_ICON, PAGE_TITLE, SIDEBAR_STATE
from components.theme import aplicar_tema
from database.db import criar_banco
from login import tela_login


if "logado" not in st.session_state:
    st.session_state.logado = False

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE if st.session_state.logado else "collapsed",
)
criar_banco()
aplicar_tema()

if not st.session_state.logado:
    tela_login()
    st.stop()

with st.sidebar:
    st.caption(f"Conectado como {st.session_state.get('usuario', '')}")
    if st.button("Sair", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================================
# SAUDAÇÃO
# ==========================================================
hora = datetime.now().hour

if hora < 12:
    saudacao = "☀️ Bom dia"
elif hora < 18:
    saudacao = "🌤 Boa tarde"
else:
    saudacao = "🌙 Boa noite"

# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
    max-width:1400px;
}

.hero{

    background:linear-gradient(135deg,#2563EB,#1D4ED8);

    border-radius:22px;

    padding:45px;

    color:white;

    margin-bottom:35px;

    box-shadow:0 15px 40px rgba(37,99,235,.30);

}

.hero h1{

    font-size:44px;

    margin-bottom:8px;

}

.hero p{

    font-size:18px;

    opacity:.92;

}

.card{

    background:#161B22;

    border:1px solid #2D333B;

    border-radius:18px;

    padding:25px;

    transition:.25s;

    height:170px;

}

.card:hover{

    transform:translateY(-6px);

    border:1px solid #3B82F6;

    box-shadow:0 10px 30px rgba(59,130,246,.25);

}

.atalho{

    background:#161B22;

    border-radius:15px;

    border:1px solid #2D333B;

    padding:18px;

    text-align:center;

    transition:.25s;

}

.atalho:hover{

    border:1px solid #2563EB;

    transform:scale(1.03);

}

.numero{

    font-size:36px;

    font-weight:bold;

}

.titulo{

    font-size:22px;

    font-weight:bold;

}

.footer{

    text-align:center;

    color:#8B949E;

    margin-top:60px;

}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# CABEÇALHO
# ==========================================================

col1,col2=st.columns([7,2])

with col1:

    st.title("💰 FinanceOS")

    st.caption("Versão 0.1.0 Alpha")

with col2:

    st.metric(

        "Status",

        "ONLINE 🟢"

    )

st.divider()

# ==========================================================
# HERO
# ==========================================================

st.markdown(f"""

<div class="hero">

<h1>{saudacao}, Alison 👋</h1>

<p>

Bem-vindo ao <b>FinanceOS</b>.

Seu sistema financeiro está evoluindo para controlar
Receitas, Despesas, Cartões, Bancos,
Patrimônio e Metas em um único lugar.

</p>

<br>

<b>🚀 Projeto em desenvolvimento ativo.</b>

</div>

""",unsafe_allow_html=True)

# ==========================================================
# CARD PRINCIPAL
# ==========================================================

st.markdown("""

<div class="card">

<div class="titulo">

📊 Painel Principal

</div>

<br>

Acompanhe toda sua vida financeira em um único sistema.

O FinanceOS foi criado para substituir planilhas e
centralizar suas informações financeiras de forma
moderna, organizada e intuitiva.

</div>

""",unsafe_allow_html=True)

st.write("")

# ==========================================================
# AÇÕES RÁPIDAS
# ==========================================================

st.subheader("⚡ Ações Rápidas")

a1, a2, a3, a4 = st.columns(4)

with a1:

    st.markdown("""
<div class="atalho">

<h2>💰</h2>

<b>Nova Receita</b>

<br><br>

Cadastre uma nova entrada.

</div>
""", unsafe_allow_html=True)

with a2:

    st.markdown("""
<div class="atalho">

<h2>💸</h2>

<b>Nova Despesa</b>

<br><br>

Cadastre uma nova saída.

</div>
""", unsafe_allow_html=True)

with a3:

    st.markdown("""
<div class="atalho">

<h2>💳</h2>

<b>Cartões</b>

<br><br>

Gerencie suas faturas.

</div>
""", unsafe_allow_html=True)

with a4:

    st.markdown("""
<div class="atalho">

<h2>🏦</h2>

<b>Bancos</b>

<br><br>

Contas e saldos.

</div>
""", unsafe_allow_html=True)

st.write("")

# ==========================================================
# ESTATÍSTICAS
# ==========================================================

st.subheader("📊 Visão Geral")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown("""

<div class="card">

<div style="font-size:42px;">📄</div>

<div class="titulo">

Módulos

</div>

<div class="numero">

8

</div>

Total planejado.

</div>

""", unsafe_allow_html=True)

with c2:

    st.markdown("""

<div class="card">

<div style="font-size:42px;">✅</div>

<div class="titulo">

Concluídos

</div>

<div class="numero" style="color:#22C55E;">

3

</div>

Dashboard<br>

Receitas<br>

Despesas

</div>

""", unsafe_allow_html=True)

with c3:

    st.markdown("""

<div class="card">

<div style="font-size:42px;">🚧</div>

<div class="titulo">

Em andamento

</div>

<div class="numero" style="color:#F59E0B;">

5

</div>

Cartões<br>

Bancos<br>

Patrimônio

</div>

""", unsafe_allow_html=True)

with c4:

    st.markdown("""

<div class="card">

<div style="font-size:42px;">🎯</div>

<div class="titulo">

Meta

</div>

<div class="numero">

v1.0

</div>

Primeira versão completa.

</div>

""", unsafe_allow_html=True)

st.divider()

# ==========================================================
# RESUMO
# ==========================================================

st.subheader("🚀 O que você já pode fazer")

r1, r2 = st.columns(2)

with r1:

    with st.container(border=True):

        st.markdown("### 💰 Financeiro")

        st.success("Cadastrar Receitas")

        st.success("Cadastrar Despesas")

        st.success("Editar registros")

        st.success("Excluir registros")

        st.success("Pesquisar")

with r2:

    with st.container(border=True):

        st.markdown("### 📊 Dashboard")

        st.success("KPIs")

        st.success("Gráficos")

        st.success("Saldo")

        st.success("Últimas movimentações")

        st.info("Em breve: Cartões")

st.divider()

# ==========================================================
# ROADMAP
# ==========================================================

st.subheader("🗺 Roadmap do Projeto")

progresso = 38

st.progress(progresso / 100)

st.caption(f"{progresso}% do FinanceOS concluído")

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.markdown("### ✅ Concluído")

        st.write("✔ Dashboard")

        st.write("✔ Receitas")

        st.write("✔ Despesas")

with col2:

    with st.container(border=True):

        st.markdown("### 🚧 Próximas etapas")

        st.write("💳 Cartões")

        st.write("🏦 Bancos")

        st.write("🏠 Patrimônio")

        st.write("🎯 Metas")

        st.write("📈 Investimentos")

st.divider()

# ==========================================================
# FEED
# ==========================================================

st.subheader("📰 Atualizações")

feed1, feed2 = st.columns(2)

with feed1:

    with st.container(border=True):

        st.markdown("## 🚀 Últimas melhorias")

        st.success("Novo Dashboard")

        st.success("Gráficos Financeiros")

        st.success("Layout Responsivo")

        st.success("Sistema de KPIs")

        st.success("Pesquisa Inteligente")

        st.success("Edição por Modal")

with feed2:

    with st.container(border=True):

        st.markdown("## 🔜 Em breve")

        st.info("💳 Gestão de Cartões")

        st.info("🏦 Gestão Bancária")

        st.info("🏠 Patrimônio")

        st.info("🎯 Metas")

        st.info("📊 Relatórios")

        st.info("☁ Backup")

st.divider()

# ==========================================================
# FRASE
# ==========================================================

st.subheader("💡 Pensamento Financeiro")

with st.container(border=True):

    st.markdown("""

### 📖 Frase da Semana

> **"Quem domina seu dinheiro,
> domina suas escolhas."**

""")

st.divider()

# ==========================================================
# PAINEL
# ==========================================================

st.subheader("⚡ Status do Sistema")

s1, s2, s3 = st.columns(3)

with s1:

    st.metric(

        "Versão",

        "0.1.0"

    )

with s2:

    st.metric(

        "Módulos",

        "3 / 8"

    )

with s3:

    st.metric(

        "Projeto",

        "38%"

    )

st.divider()

# ==========================================================
# PRÓXIMOS RECURSOS
# ==========================================================

st.subheader("🚀 Próximos Recursos")

f1, f2, f3 = st.columns(3)

with f1:

    with st.container(border=True):

        st.markdown("### 💳 Cartões")

        st.write(
            """
• Controle de limite

• Fechamento

• Vencimento

• Parcelas

• Faturas
"""
        )

with f2:

    with st.container(border=True):

        st.markdown("### 🏦 Bancos")

        st.write(
            """
• Contas

• Saldo

• PIX

• Transferências

• Conciliação
"""
        )

with f3:

    with st.container(border=True):

        st.markdown("### 🎯 Metas")

        st.write(
            """
• Objetivos

• Barra de progresso

• Economia

• Alertas

• Evolução
"""
        )

st.divider()

# ==========================================================
# POR QUE USAR O FINANCEOS
# ==========================================================

st.subheader("💡 Por que usar o FinanceOS?")

c1, c2 = st.columns(2)

with c1:

    with st.container(border=True):

        st.markdown("### ✅ Organização")

        st.write(
            """
Centralize toda sua vida financeira em um único sistema.

• Receitas

• Despesas

• Cartões

• Bancos

• Patrimônio
"""
        )

with c2:

    with st.container(border=True):

        st.markdown("### 📈 Crescimento")

        st.write(
            """
Acompanhe sua evolução financeira.

• Dashboard

• KPIs

• Gráficos

• Relatórios

• Metas
"""
        )

st.divider()

# ==========================================================
# INFORMAÇÕES
# ==========================================================

st.subheader("ℹ Informações")

info1, info2, info3 = st.columns(3)

with info1:

    st.info(
        """
### 👨‍💻 Desenvolvedor

Alison S. Nascimento
"""
    )

with info2:

    st.success(
        """
### ⚙️ Tecnologia

Python

Streamlit

SQLite

Plotly
"""
    )

with info3:

    st.warning(
        """
### 📦 Versão

FinanceOS

v0.1.0 Alpha
"""
    )

st.divider()

# ==========================================================
# RODAPÉ
# ==========================================================

st.markdown(
    """
<div class="footer">

<h3>💰 FinanceOS</h3>

<p>
Sistema de Gestão Financeira Pessoal
</p>

<p>
Versão <b>0.1.0 Alpha</b>
</p>

<p>
Desenvolvido por <b>Alison S. Nascimento</b>
</p>

<br>

<p style="opacity:.7;">
© 2026 • Todos os direitos reservados
</p>

</div>
""",
    unsafe_allow_html=True
)
