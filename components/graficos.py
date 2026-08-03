import streamlit as st
import plotly.express as px


# ==========================================
# RECEITAS POR CATEGORIA
# ==========================================

def grafico_receitas_categoria(df):
    """
    Exibe um gráfico de pizza das receitas por categoria.
    """

    if df.empty:
        st.info("Sem dados para exibir.")
        return

    grafico = (
        df.groupby("Categoria")["Valor"]
        .sum()
        .reset_index()
    )

    st.markdown("#### 🍩 Receitas por Categoria")

    fig = px.pie(
        grafico,
        names="Categoria",
        values="Valor",
        hole=0.70,
        color="Categoria",
        color_discrete_sequence=[
            "#16A34A",
            "#3B82F6",
            "#F59E0B",
            "#EF4444",
        ]
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>"
    )

    fig.update_layout(
        showlegend=False,
        height=360,
        margin=dict(l=0, r=0, t=25, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==========================================
# EVOLUÇÃO DAS RECEITAS
# ==========================================

def grafico_receitas_mes(df):
    """
    Exibe a evolução das receitas ao longo do tempo.
    """

    if df.empty:
        st.info("Sem dados para exibir.")
        return

    grafico = (
        df.groupby("Data")["Valor"]
        .sum()
        .reset_index()
        .sort_values("Data")
    )

    st.markdown("#### 📈 Evolução das Receitas")

    fig = px.line(
        grafico,
        x="Data",
        y="Valor",
        markers=True,
        color_discrete_sequence=["#16A34A"]
    )

    fig.update_traces(
        line=dict(width=4),
        marker=dict(size=10)
    )

    fig.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=25, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="",
        yaxis_title="Valor (R$)",
        hovermode="x unified"
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False
    )

    fig.update_xaxes(
        showgrid=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ==========================================
# DESPESAS
# ==========================================

def grafico_despesas_categoria(df):
    """
    Gráfico de despesas por categoria.
    """

    if df.empty:
        st.info("Sem dados para exibir.")
        return

    grafico = (
        df.groupby("Categoria")["Valor"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        grafico,
        names="Categoria",
        values="Valor",
        hole=0.55,
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def grafico_despesas_mes(df):
    """
    Evolução mensal das despesas.
    """

    if df.empty:
        st.info("Sem dados para exibir.")
        return

    grafico = (
        df.groupby("Data")["Valor"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        grafico,
        x="Data",
        y="Valor",
        text_auto=".2s"
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=350,
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    

