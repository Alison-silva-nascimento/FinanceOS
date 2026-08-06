import streamlit as st
import pandas as pd
from components.aggrid_table import mostrar_aggrid
from components.formatadores import (
    moeda,
    formatar_data
)

from components.graficos import (
    grafico_receitas_categoria,
    grafico_receitas_mes,
)

from services.receitas_service import (
    obter_receitas,
    obter_receita_por_id,
    salvar_receita,
    atualizar_receita,
    remover_receita,
    calcular_kpis,
)

from components.cards import kpi_card
from components.theme import aplicar_tema
from datetime import datetime
from auth import exigir_login

aplicar_tema()
exigir_login()

# ==========================================
# MODAL DE EDIÇÃO
# ==========================================

@st.dialog("✏️ Editar Receita", width="large")
def modal_editar_receita(id_receita):

    receita = obter_receita_por_id(id_receita)

    categorias = [
        "Salário",
        "Plantão",
        "Extra",
        "Outros"
    ]

    data = st.date_input(
        "📅 Data",
        value=datetime.strptime(
            receita["data"],
            "%Y-%m-%d"
        ).date()
    )

    categoria = st.selectbox(
        "📂 Categoria",
        categorias,
        index=categorias.index(receita["categoria"])
    )

    descricao = st.text_input(
        "📝 Descrição",
        value=receita["descricao"]
    )

    valor = st.number_input(
        "💰 Valor",
        value=float(receita["valor"]),
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

            atualizar_receita(
                id_receita,
                str(data),
                categoria,
                descricao,
                valor
            )

            st.toast("✅ Receita atualizada!")

            st.rerun()

# ==========================================

if "editando" not in st.session_state:
    st.session_state.editando = False

if "id_receita" not in st.session_state:
    st.session_state.id_receita = None

st.title("💰 Receitas")

# ==========================================
# KPIs
# ==========================================

kpis = calcular_kpis()

col1, col2, col3 = st.columns(3)

with col1:
    kpi_card(
        "Total Receitas",
        moeda(kpis["valor_total"]),
        "💰",
        "#14532D"
    )

with col2:
    kpi_card(
        "Quantidade",
        str(kpis["total_receitas"]),
        "📄",
        "#1E3A8A"
    )


with col3:
    kpi_card(
        f"Receita do mês · {kpis['mes_atual']}",
        moeda(kpis["receita_mes"]),
        "🗓️",
        "#7C3AED"
    )

st.divider()

# ==========================================
# MODO EDIÇÃO
# ==========================================

receita_edicao = None

if st.session_state.editando:

    receita_edicao = obter_receita_por_id(
        st.session_state.id_receita
    )

# ==========================================
# FORMULÁRIO
# ==========================================

with st.form("form_receita"):

    # -----------------------------
    # Valores padrão
    # -----------------------------

    if receita_edicao:

        data_padrao = datetime.strptime(
            receita_edicao["data"],
            "%Y-%m-%d"
        ).date()

        categoria_padrao = receita_edicao["categoria"]
        descricao_padrao = receita_edicao["descricao"]
        valor_padrao = float(receita_edicao["valor"])

    else:

        data_padrao = datetime.today().date()
        categoria_padrao = "Salário"
        descricao_padrao = ""
        valor_padrao = 0.0

    categorias = [
        "Salário",
        "Plantão",
        "Extra",
        "Outros"
    ]

    # -----------------------------
    # Campos
    # -----------------------------

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
        min_value=0.0,
        value=valor_padrao,
        step=0.01,
        format="%.2f"
    )

    # -----------------------------
    # Botão
    # -----------------------------

    texto_botao = (
        "✏️ Atualizar Receita"
        if st.session_state.editando
        else "💾 Salvar Receita"
    )

    salvar = st.form_submit_button(
        texto_botao,
        use_container_width=True
    )

# ==========================================
# SALVAR / ATUALIZAR
# ==========================================

if salvar:

    if st.session_state.editando:

        atualizar_receita(
            st.session_state.id_receita,
            str(data),
            categoria,
            descricao,
            valor
        )

        st.toast("✅ Receita atualizada com sucesso!")

        st.session_state.editando = False
        st.session_state.id_receita = None

    else:

        salvar_receita(
            str(data),
            categoria,
            descricao,
            valor
        )

        st.toast("💰 Receita cadastrada com sucesso!")

    st.rerun()

st.divider()

# ==========================================
# PESQUISA
# ==========================================

pesquisa = st.text_input(
    "🔍 Pesquisar",
    placeholder="Descrição ou categoria..."
)


# ==========================================
# TABELA
# ==========================================



receitas = obter_receitas()


if pesquisa:

    pesquisa = pesquisa.lower()

    receitas = [

        r for r in receitas

        if pesquisa in (r["descricao"] or "").lower()

        or pesquisa in r["categoria"].lower()

    ]

st.divider()

st.subheader("📊 Análises")

df_grafico = pd.DataFrame([dict(r) for r in receitas])

if not df_grafico.empty:
    df_grafico["Data"] = pd.to_datetime(df_grafico["data"])
    df_grafico["Valor"] = df_grafico["valor"]
    df_grafico["Categoria"] = df_grafico["categoria"]

    col1, col2 = st.columns(2)

    with col1:
        grafico_receitas_categoria(df_grafico)

    with col2:
        grafico_receitas_mes(df_grafico)

# ==========================================
# FILTRO
# ==========================================

categoria_filtro = st.selectbox(
    "📂 Categoria",
    [
        "Todas",
        "Salário",
        "Plantão",
        "Extra",
        "Outros"
    ]
)

if categoria_filtro != "Todas":

    receitas = [

        r for r in receitas

        if r["categoria"] == categoria_filtro

    ]

df = pd.DataFrame()

if not receitas:

    st.info("Nenhuma receita cadastrada.")

else:

    df = pd.DataFrame([dict(r) for r in receitas])

    df = df.rename(columns={
        "id": "ID",
        "data": "Data",
        "categoria": "Categoria",
        "descricao": "Descrição",
        "valor": "Valor"
    })

    df["Data"] = df["Data"].apply(formatar_data)

    df["Valor"] = df["Valor"].apply(moeda)

    df["Excluir"] = "🗑"

    df = df[
        [   "ID",
            "Data",
            "Categoria",
            "Descrição",
            "Valor",
            "Excluir"
        ]
    ]

# ==========================================
# RECEITAS CADASTRADAS
# ==========================================

st.subheader("📋 Receitas cadastradas")

# Cabeçalho
cab1, cab2, cab3, cab4, cab5, cab6 = st.columns([2, 2, 3, 2, 1, 1])

cab1.markdown("**📅 Data**")
cab2.markdown("**📂 Categoria**")
cab3.markdown("**📝 Descrição**")
cab4.markdown("**💰 Valor**")
cab5.markdown("**✏️**")
cab6.markdown("**🗑️**")

st.divider()

# Linhas
for _, row in df.iterrows():

    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 3, 2, 1, 1])

    with col1:
        st.write(row["Data"])

    with col2:
        st.write(row["Categoria"])

    with col3:
        st.write(row["Descrição"])

    with col4:
        st.write(row["Valor"])

    # =====================================
    # EDITAR
    # =====================================

    with col5:

        if st.button(
        "✏️",
        key=f"edit_{row['ID']}"
    ):

         modal_editar_receita(row["ID"])

    # =====================================
    # EXCLUIR
    # =====================================

    with col6:

        if st.button(
            "🗑",
            key=f"del_{row['ID']}"
        ):

            st.session_state["confirmar_exclusao"] = row["ID"]


# ==========================================
# CONFIRMAÇÃO DE EXCLUSÃO
# ==========================================

if "confirmar_exclusao" in st.session_state:

    st.warning("⚠️ Deseja realmente excluir esta receita?")

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

            remover_receita(
                int(st.session_state["confirmar_exclusao"])
            )

            del st.session_state["confirmar_exclusao"]

            st.toast("🗑 Receita excluída com sucesso!")

            st.rerun()

