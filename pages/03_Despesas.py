import streamlit as st
import pandas as pd
from datetime import datetime

from components.formatadores import (
    moeda,
    formatar_data
)

from components.graficos import (
    grafico_despesas_categoria,
    grafico_despesas_mes,
)

from services.despesas_service import (
    obter_despesas,
    obter_despesa_por_id,
    salvar_despesa,
    atualizar_despesa,
    remover_despesa,
    calcular_kpis,
)
from database.db import gerar_recorrencias

from components.cards import kpi_card
from components.theme import aplicar_tema
from auth import exigir_login

aplicar_tema()
exigir_login()
gerar_recorrencias(datetime.today().strftime("%Y-%m"))

# ==========================================
# MODAL DE EDIÇÃO
# ==========================================

@st.dialog("✏️ Editar Despesa", width="large")
def modal_editar_despesa(id_despesa):

    despesa = obter_despesa_por_id(id_despesa)

    categorias = [
        "Moradia",
        "Alimentação",
        "Transporte",
        "Saúde",
        "Lazer",
        "Educação",
        "Investimentos",
        "Cartão",
        "Outros"
    ]

    data = st.date_input(
        "📅 Data",
        value=datetime.strptime(
            despesa["data"],
            "%Y-%m-%d"
        ).date()
    )

    categoria = st.selectbox(
        "📂 Categoria",
        categorias,
        index=categorias.index(despesa["categoria"])
    )

    descricao = st.text_input(
        "📝 Descrição",
        value=despesa["descricao"]
    )

    valor = st.number_input(
        "💰 Valor",
        value=float(despesa["valor"]),
        min_value=0.0,
        step=0.01
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Cancelar",
            use_container_width=True
        ):
            st.rerun()

    with col2:

        if st.button(
            "Salvar",
            type="primary",
            use_container_width=True
        ):

            atualizar_despesa(
                id_despesa,
                str(data),
                categoria,
                descricao,
                valor
            )

            st.toast("💸 Despesa atualizada!")

            st.rerun()


# ==========================================
# SESSION STATE
# ==========================================

if "editando" not in st.session_state:
    st.session_state.editando = False

if "id_despesa" not in st.session_state:
    st.session_state.id_despesa = None


st.title("💸 Despesas")


# ==========================================
# PERÍODO E KPIs
# ==========================================

todas_despesas = obter_despesas()
mes_atual = datetime.today().strftime("%Y-%m")
competencias = sorted({str(despesa["data"])[:7] for despesa in todas_despesas if despesa["data"]}, reverse=True)
if mes_atual not in competencias:
    competencias.insert(0, mes_atual)

with st.container(border=True):
    periodo_info, periodo_seletor = st.columns([3, 2])
    with periodo_info:
        st.markdown("#### 🗓️ Período das despesas")
        st.caption("Escolha o mês para consultar os lançamentos, indicadores e análises.")
    with periodo_seletor:
        competencia_selecionada = st.selectbox("Competência", competencias, key="competencia_despesas")

despesas_periodo = [
    despesa for despesa in todas_despesas
    if str(despesa["data"]).startswith(competencia_selecionada)
]
valor_periodo = sum(float(despesa["valor"]) for despesa in despesas_periodo)
quantidade_periodo = len(despesas_periodo)
media_periodo = valor_periodo / quantidade_periodo if quantidade_periodo else 0

col1, col2, col3 = st.columns(3)

with col1:

    kpi_card(
        f"Despesas em {competencia_selecionada}",
        moeda(valor_periodo),
        "💸",
        "#991B1B"
    )

with col2:

    kpi_card(
        "Lançamentos",
        str(quantidade_periodo),
        "📄",
        "#1E3A8A"
    )

with col3:

    kpi_card(
        "Média por lançamento",
        moeda(media_periodo),
        "📉",
        "#DC2626"
    )

st.divider()


# ==========================================
# MODO EDIÇÃO
# ==========================================

despesa_edicao = None

if st.session_state.editando:

    despesa_edicao = obter_despesa_por_id(
        st.session_state.id_despesa
    )


# ==========================================
# FORMULÁRIO
# ==========================================

with st.form("form_despesa"):

    if despesa_edicao:

        data_padrao = datetime.strptime(
            despesa_edicao["data"],
            "%Y-%m-%d"
        ).date()

        categoria_padrao = despesa_edicao["categoria"]
        descricao_padrao = despesa_edicao["descricao"]
        valor_padrao = float(despesa_edicao["valor"])

    else:

        data_padrao = datetime.today().date()
        categoria_padrao = "Moradia"
        descricao_padrao = ""
        valor_padrao = 0.0

    categorias = [
        "Moradia",
        "Alimentação",
        "Transporte",
        "Saúde",
        "Lazer",
        "Educação",
        "Investimentos",
        "Cartão",
        "Outros"
    ]

    data = st.date_input(
        "Data",
        value=data_padrao
    )

    categoria = st.selectbox(
        "Categoria",
        categorias,
        index=categorias.index(categoria_padrao)
    )

    descricao = st.text_input(
        "Descrição",
        value=descricao_padrao
    )

    valor = st.number_input(
        "Valor",
        value=valor_padrao,
        min_value=0.0,
        step=0.01,
        format="%.2f"
    )

    texto_botao = (
        "✏️ Atualizar Despesa"
        if st.session_state.editando
        else "💾 Salvar Despesa"
    )

    salvar = st.form_submit_button(
        texto_botao,
        use_container_width=True
    )


if salvar:

    if st.session_state.editando:

        atualizar_despesa(
            st.session_state.id_despesa,
            str(data),
            categoria,
            descricao,
            valor
        )

        st.toast("💸 Despesa atualizada com sucesso!")

        st.session_state.editando = False
        st.session_state.id_despesa = None

    else:

        salvar_despesa(
            str(data),
            categoria,
            descricao,
            valor
        )

        st.toast("💸 Despesa cadastrada com sucesso!")

    st.rerun()

st.divider()

# ==========================================
# PESQUISA
# ==========================================

pesquisa = st.text_input(
    "🔍 Pesquisar",
    placeholder="Descrição ou categoria..."
)

despesas = list(despesas_periodo)

if pesquisa:

    pesquisa = pesquisa.lower()

    despesas = [

        d for d in despesas

        if pesquisa in (d["descricao"] or "").lower()

        or pesquisa in d["categoria"].lower()

    ]

st.divider()

# ==========================================
# GRÁFICOS
# ==========================================

st.subheader("📊 Análises")

df_grafico = pd.DataFrame([dict(d) for d in despesas])

if not df_grafico.empty:

    df_grafico["Data"] = pd.to_datetime(df_grafico["data"])
    df_grafico["Valor"] = df_grafico["valor"]
    df_grafico["Categoria"] = df_grafico["categoria"]

    col1, col2 = st.columns(2)

    with col1:
        grafico_despesas_categoria(df_grafico)

    with col2:
        grafico_despesas_mes(df_grafico)

st.divider()

# ==========================================
# FILTRO
# ==========================================

categoria_filtro = st.selectbox(
    "📂 Categoria",
    [
        "Todas",
        "Moradia",
        "Alimentação",
        "Transporte",
        "Saúde",
        "Lazer",
        "Educação",
        "Investimentos",
        "Cartão",
        "Outros"
    ]
)

if categoria_filtro != "Todas":

    despesas = [

        d for d in despesas

        if d["categoria"] == categoria_filtro

    ]

if not despesas:

    st.info("Nenhuma despesa cadastrada.")

    st.stop()

else:

    df = pd.DataFrame([dict(d) for d in despesas])

    df = df.rename(columns={
        "id": "ID",
        "data": "Data",
        "categoria": "Categoria",
        "descricao": "Descrição",
        "valor": "Valor"
    })

    df["Data"] = df["Data"].apply(formatar_data)
    df["Valor"] = df["Valor"].apply(moeda)

    df = df[
        [
            "ID",
            "Data",
            "Categoria",
            "Descrição",
            "Valor"
        ]
    ]

# ==========================================
# DESPESAS CADASTRADAS
# ==========================================

st.subheader("💸 Despesas cadastradas")

st.markdown(
    """
    <style>
    @media (min-width: 769px) {
        .st-key-despesas-lista [data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            align-items: center !important;
        }
        .st-key-despesas-lista [data-testid="stColumn"] {
            min-width: 0 !important;
        }
        .st-key-despesas-lista .stButton > button {
            min-width: 2.35rem !important;
            min-height: 2.45rem !important;
            padding: .25rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container(key="despesas-lista"):
    cab1, cab2, cab3, cab4, cab5 = st.columns([1.2, 1.3, 2.5, 1.2, 1.0], gap="small")

    cab1.markdown("**📅 Data**")
    cab2.markdown("**📂 Categoria**")
    cab3.markdown("**📝 Descrição**")
    cab4.markdown("**💰 Valor**")
    cab5.markdown("**⚙️ Ações**")

    st.divider()

    for _, row in df.iterrows():

        col1, col2, col3, col4, col5 = st.columns([1.2, 1.3, 2.5, 1.2, 1.0], gap="small")

        with col1:
            st.write(row["Data"])

        with col2:
            st.write(row["Categoria"])

        with col3:
            st.write(row["Descrição"])

        with col4:
            st.write(row["Valor"])

        with col5:
            acao_editar, acao_excluir = st.columns(2, gap="small")
            with acao_editar:
                if st.button("✏️", key=f"edit_{row['ID']}", use_container_width=True, help="Editar despesa"):
                    modal_editar_despesa(row["ID"])
            with acao_excluir:
                if st.button("🗑", key=f"del_{row['ID']}", use_container_width=True, help="Excluir despesa"):
                    st.session_state["confirmar_exclusao"] = row["ID"]


# ==========================================
# CONFIRMAÇÃO DE EXCLUSÃO
# ==========================================

if "confirmar_exclusao" in st.session_state:

    st.warning("⚠️ Deseja realmente excluir esta despesa?")

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Cancelar",
            use_container_width=True
        ):

            del st.session_state["confirmar_exclusao"]

            st.rerun()

    with c2:

        if st.button(
            "🗑 Excluir",
            type="primary",
            use_container_width=True
        ):

            remover_despesa(
                int(st.session_state["confirmar_exclusao"])
            )

            del st.session_state["confirmar_exclusao"]

            st.toast("🗑 Despesa excluída com sucesso!")

            st.rerun()
