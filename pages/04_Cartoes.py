import streamlit as st
from streamlit_modal import Modal
from components.theme import aplicar_tema
from services.cartoes_service import (
    obter_cartoes,
    salvar_cartao,
    remover_cartao,
    atualizar_cartao,
    obter_cartao_por_id,
    calcular_kpis
)
from auth import exigir_login
from database.db import adicionar_compra_cartao, fatura_cartao, fatura_cartao_mes, listar_bancos, listar_compras_cartao, pagar_fatura

# =====================================================
# MODAL EDITAR
# =====================================================
modal_editar = Modal(
    "✏️ Editar Cartão",
    key="editar_cartao_modal",
    max_width=550
)

# =====================================================
# FUNÇÃO EDITAR
# =====================================================

if "editar_cartao" not in st.session_state:
    st.session_state.editar_cartao = None

# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Cartões",
    page_icon="💳",
    layout="wide"
)
aplicar_tema()
exigir_login()

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.credit-card{

    border-radius:22px;

    padding:28px;

    color:white;

    min-height:320px;

    box-shadow:0 18px 40px rgba(0,0,0,.45);

    margin-bottom:18px;

    transition:.30s;

    position:relative;

    overflow:hidden;

}

.credit-card:hover{

    transform:translateY(-6px);

    box-shadow:0 28px 55px rgba(0,0,0,.60);

}

.credit-card::before{

    content:"";

    position:absolute;

    width:280px;

    height:280px;

    border-radius:50%;

    background:rgba(255,255,255,.05);

    right:-120px;

    top:-120px;

}

.card-top{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

}

.card-title{

    font-size:30px;

    font-weight:700;

    margin-top:8px;

}

.card-bank{

    opacity:.8;

    margin-top:4px;

    font-size:14px;

}

.card-chip{

    width:62px;

    height:46px;

    border-radius:10px;

    background:
    linear-gradient(
    135deg,
    #FFE082,
    #D4AF37,
    #B8860B);

    margin-top:22px;

    box-shadow:
    inset 0 0 4px rgba(255,255,255,.6);

}

.card-number{

    margin-top:30px;

    font-size:27px;

    letter-spacing:6px;

    font-family:monospace;

}

.progress{

    margin-top:25px;

    width:100%;

    height:10px;

    background:rgba(255,255,255,.20);

    border-radius:20px;

    overflow:hidden;

}

.progress div{

    height:100%;

    border-radius:20px;

}

.card-footer{

    display:flex;

    justify-content:space-between;

    margin-top:25px;

}

.small{

    font-size:12px;

    opacity:.75;

}

.value{

    font-size:17px;

    font-weight:bold;

}

.info-line{

    margin-top:18px;

    font-size:15px;

}

.status{

    margin-top:15px;

    display:inline-block;

    padding:5px 14px;

    border-radius:30px;

    background:rgba(255,255,255,.15);

    font-size:13px;

}

.cards-section{
    display:flex;
    align-items:center;
    gap:12px;
    margin:30px 0 14px;
    padding:15px 18px;
    border:1px solid rgba(148,163,184,.22);
    border-radius:15px;
    background:linear-gradient(100deg,rgba(30,41,59,.7),rgba(15,23,42,.5));
}
.cards-section__icon{font-size:24px;}
.cards-section__title{font-size:18px;font-weight:750;}
.cards-section__text{font-size:13px;color:#aab6cf;margin-top:2px;}

</style>
""", unsafe_allow_html=True)


# =====================================================
# DADOS
# =====================================================

kpis = calcular_kpis()

# =====================================================
# TÍTULO
# =====================================================

st.title("💳 Cartões")

st.caption("Gerencie todos os seus cartões em um único lugar.")

st.divider()

# =====================================================
# KPIs
# =====================================================

k1, k2, k3 = st.columns(3)

with k1:

    st.markdown(f"""
    <div class="kpi">
        <small>💳 Total de cartões</small>
        <h1>{kpis['total_cartoes']}</h1>
    </div>
    """, unsafe_allow_html=True)

with k2:

    st.markdown(f"""
    <div class="kpi">
        <small>💰 Limite Total</small>
        <h1>R$ {kpis['limite_total']:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

with k3:

    st.markdown(f"""
    <div class="kpi">
        <small>📈 Média por cartão</small>
        <h1>R$ {kpis['media_limite']:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# =====================================================
# LAYOUT
# =====================================================

col1, col2 = st.columns([1, 1.35])

# =====================================================
# FORMULÁRIO
# =====================================================

with col1:

    st.markdown("""
    <div class="card">
    <h3>➕ Novo cartão</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.form("novo_cartao", clear_on_submit=True):

        nome = st.text_input(
            "Nome do cartão",
            placeholder="Ex: Nubank Platinum"
        )

        banco = st.text_input(
            "Banco",
            placeholder="Ex: Nubank"
        )

        bandeira = st.selectbox(
            "Bandeira",
            [
                "Mastercard",
                "Visa",
                "Elo",
                "American Express",
                "Hipercard"
            ]
        )

        limite = st.number_input(
            "Limite",
            min_value=0.0,
            step=100.0
        )

        c1, c2 = st.columns(2)

        with c1:

            fechamento = st.number_input(
                "Fechamento",
                min_value=1,
                max_value=31,
                value=20
            )

        with c2:

            vencimento = st.number_input(
                "Vencimento",
                min_value=1,
                max_value=31,
                value=30
            )

        cor = st.color_picker(
            "Cor do cartão",
            "#6D28D9"
        )

        salvar = st.form_submit_button(
            "💾 Salvar cartão",
            use_container_width=True
        )

        if salvar:

            if nome.strip() == "" or banco.strip() == "":

                st.error("Informe o nome e o banco.")

            else:

                salvar_cartao(
                    nome,
                    banco,
                    bandeira,
                    limite,
                    fechamento,
                    vencimento,
                    cor
                )

                st.success("Cartão cadastrado com sucesso!")

                st.rerun()

# =====================================================
# LISTA DOS CARTÕES
# =====================================================

with col2:

    st.subheader("💳 Meus cartões")

    cartoes = obter_cartoes()

    from datetime import datetime
    hoje = datetime.now().day

# =====================================
# MODAL DE EDIÇÃO
# =====================================

if modal_editar.is_open():

    with modal_editar.container():

        cartao = obter_cartao_por_id(
            st.session_state["editar_cartao"]
        )


        nome = st.text_input(
            "Nome do cartão",
            value=cartao["nome"]
        )

        banco = st.text_input(
            "Banco",
            value=cartao["banco"]
        )

        bandeira = st.selectbox(
            "Bandeira",
            ["Mastercard", "Visa", "Elo", "American Express"],
            index=["Mastercard","Visa","Elo","American Express"].index(
                cartao["bandeira"]
            )
        )

        limite = st.number_input(
            "Limite",
            value=float(cartao["limite"])
        )

        fechamento = st.number_input(
            "Fechamento",
            min_value=1,
            max_value=31,
            value=int(cartao["fechamento"])
        )

        vencimento = st.number_input(
            "Vencimento",
            min_value=1,
            max_value=31,
            value=int(cartao["vencimento"])
        )

        cor = st.color_picker(
            "Cor",
            value=cartao["cor"]
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Cancelar",
                use_container_width=True
            ):
                modal_editar.close()
                st.rerun()

        with col2:

            if st.button(
                "Salvar alterações",
                type="primary",
                use_container_width=True
            ):

                atualizar_cartao(
                    cartao["id"],
                    nome,
                    banco,
                    bandeira,
                    limite,
                    fechamento,
                    vencimento,
                    cor
                )

                st.success("Cartão atualizado!")

                modal_editar.close()

                st.rerun()



# =====================================================
# CARTÕES CADASTRADOS
# =====================================================

st.markdown('<div class="cards-section"><div class="cards-section__icon">💳</div><div><div class="cards-section__title">Meus cartões</div><div class="cards-section__text">Limites, vencimentos e utilização por cartão.</div></div></div>', unsafe_allow_html=True)

if not cartoes:

    st.info("Nenhum cartão cadastrado.")

else:

    cols = st.columns(2)

    for i, cartao in enumerate(cartoes):

        utilizado = fatura_cartao(cartao["id"])

        disponivel = cartao["limite"] - utilizado

        percentual = (
            (utilizado / cartao["limite"]) * 100
            if cartao["limite"] > 0
            else 0
        )

        if percentual < 50:
            cor_barra = "#22C55E"
            status = "🟢 Limite saudável"

        elif percentual < 80:
            cor_barra = "#F59E0B"
            status = "🟡 Atenção"

        else:
            cor_barra = "#EF4444"
            status = "🔴 Limite alto"

        with cols[i % 2]:

            st.markdown(
                f"""
<div class="credit-card"
style="background:linear-gradient(135deg,{cartao["cor"]},#111827);">

<div class="card-top">

<div>

<div style="font-size:28px;">
💳
</div>

<div class="card-title">
{cartao["nome"]}
</div>

<div class="card-bank">
🏦 {cartao["banco"]}
</div>

</div>

<div style="text-align:right;">

<div style="
font-size:18px;
font-weight:bold;
margin-top:8px;">
{cartao["bandeira"]}
</div>

</div>

</div>

<div class="card-chip"></div>

<div class="card-number">
•••• •••• •••• 4587
</div>

<div class="progress">

<div style="
width:{percentual}%;
background:{cor_barra};
height:100%;
border-radius:20px;">
</div>

</div>

<div class="info-line">
<b>Utilizado:</b>
R$ {utilizado:,.2f}
</div>

<div class="info-line">
<b>Disponível:</b>
R$ {disponivel:,.2f}
</div>

<div class="card-footer">

<div>
<div class="small">Limite</div>
<div class="value">
R$ {cartao["limite"]:,.2f}
</div>
</div>

<div>
<div class="small">Fecha</div>
<div class="value">
{cartao["fechamento"]}
</div>
</div>

<div>
<div class="small">Vence</div>
<div class="value">
{cartao["vencimento"]}
</div>
</div>

</div>

<div class="status">
{status}
</div>

</div>
""",
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:

                 if st.button(
                    "✏️ Editar",
                    key=f"editar_{cartao['id']}",
                    use_container_width=True,
                ):
                    st.session_state["editar_cartao"] = cartao["id"]
                    modal_editar.open()
                    st.rerun()

            with col2:

                if st.button(
                "🗑️ Excluir",
                key=f"excluir_{cartao['id']}",
                use_container_width=True,
            ):

                 remover_cartao(cartao["id"])

                 st.toast("Cartão removido!")

                 st.rerun()

st.divider()
st.markdown('<div class="cards-section"><div class="cards-section__icon">🧾</div><div><div class="cards-section__title">Compras e faturas</div><div class="cards-section__text">Registre compras ou consulte cada fatura em aberto.</div></div></div>', unsafe_allow_html=True)
if cartoes:
    opcoes_cartao = {f"{c['nome']} · limite {c['limite']:,.2f}": c["id"] for c in cartoes}
    with st.form("nova_compra_cartao", clear_on_submit=True):
        cartao_escolhido = st.selectbox("Cartão", list(opcoes_cartao))
        data_compra = st.date_input("Data da compra")
        descricao_compra = st.text_input("Descrição da compra")
        a,b,c = st.columns(3); categoria_compra=a.text_input("Categoria", value="Cartão"); valor_compra=b.number_input("Valor total", min_value=0.01, step=10.0); parcelas=c.number_input("Parcelas", min_value=1, max_value=48, value=1)
        salvar_compra = st.form_submit_button("Adicionar compra", use_container_width=True)
    if salvar_compra and descricao_compra.strip():
        adicionar_compra_cartao(opcoes_cartao[cartao_escolhido], str(data_compra), descricao_compra.strip(), categoria_compra, valor_compra, parcelas); st.rerun()
    for nome, id_cartao in opcoes_cartao.items():
        compras = listar_compras_cartao(id_cartao)
        if compras:
            with st.expander(f"{nome} · fatura em aberto: R$ {fatura_cartao(id_cartao):,.2f}"):
                for compra in compras: st.write(f"{compra['data']} · {compra['descricao']} — R$ {compra['valor']/compra['parcelas']:,.2f} ({compra['parcelas']}x)")

st.markdown('<div class="cards-section"><div class="cards-section__icon">✅</div><div><div class="cards-section__title">Pagamento de fatura</div><div class="cards-section__text">Quite a fatura usando uma conta bancária cadastrada.</div></div></div>', unsafe_allow_html=True)
bancos = listar_bancos()
if cartoes and bancos:
    mes_fatura = st.text_input("Competência da fatura", value=__import__('datetime').date.today().strftime('%Y-%m'))
    cartao_pagamento = st.selectbox("Cartão para pagamento", list(opcoes_cartao), key="cartao_pagamento")
    valor_fatura = fatura_cartao_mes(opcoes_cartao[cartao_pagamento], mes_fatura)
    conta_pagamento = st.selectbox("Pagar pela conta", [f"{b['nome']} · R$ {b['saldo']:,.2f}" for b in bancos])
    if st.button(f"Pagar fatura de R$ {valor_fatura:,.2f}", disabled=valor_fatura <= 0, use_container_width=True):
        try:
            banco_id = bancos[[f"{b['nome']} · R$ {b['saldo']:,.2f}" for b in bancos].index(conta_pagamento)]['id']
            pagar_fatura(opcoes_cartao[cartao_pagamento], mes_fatura, banco_id, valor_fatura, str(__import__('datetime').date.today()))
            st.success("Fatura paga e saldo da conta atualizado."); st.rerun()
        except ValueError as erro: st.error(str(erro))


