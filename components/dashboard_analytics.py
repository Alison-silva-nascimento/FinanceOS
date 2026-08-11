import pandas as pd
import plotly.express as px
import streamlit as st


def _frame_movimentos(itens, tipo):
    linhas = [
        {
            "Data": item["data"],
            "Categoria": item["categoria"] or "Sem categoria",
            "Descrição": item["descricao"] or "Sem descrição",
            "Valor": float(item["valor"] or 0),
            "Tipo": tipo,
        }
        for item in itens
    ]
    frame = pd.DataFrame(linhas, columns=["Data", "Categoria", "Descrição", "Valor", "Tipo"])
    if not frame.empty:
        frame["Data"] = pd.to_datetime(frame["Data"], errors="coerce")
        frame = frame.dropna(subset=["Data"])
    return frame


def _estilizar(fig, altura=315, legenda=False):
    fig.update_layout(
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dbeafe",
        margin=dict(l=12, r=12, t=18, b=12),
        showlegend=legenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(bgcolor="#0f1f35", font_color="#f8fafc"),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,.12)", linecolor="rgba(148,163,184,.18)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.12)", linecolor="rgba(148,163,184,.18)")
    return fig


def render_dashboard_analytics(receitas, despesas):
    """Renderiza o raio-X mensal do Dashboard com layout responsivo."""
    st.subheader("📊 Raio-X do mês")
    st.caption("Entenda quando, onde e com o que o dinheiro foi movimentado na competência selecionada.")

    df_receitas = _frame_movimentos(receitas, "Receitas")
    df_despesas = _frame_movimentos(despesas, "Despesas")
    movimentos = pd.concat([df_receitas, df_despesas], ignore_index=True)

    painel_a, painel_b = st.columns(2)
    with painel_a:
        with st.container(border=True):
            st.markdown("#### 📈 Evolução diária")
            if movimentos.empty:
                st.info("Ainda não há movimentações para formar a evolução diária.")
            else:
                diario = movimentos.groupby(["Data", "Tipo"], as_index=False)["Valor"].sum()
                fig = px.line(
                    diario, x="Data", y="Valor", color="Tipo", markers=True,
                    color_discrete_map={"Receitas": "#22c55e", "Despesas": "#38bdf8"},
                )
                fig.update_traces(line=dict(width=3), marker=dict(size=7))
                fig.update_xaxes(title=None, tickformat="%d/%m")
                fig.update_yaxes(title=None, tickprefix="R$ ")
                st.plotly_chart(_estilizar(fig, legenda=True), use_container_width=True)

    with painel_b:
        with st.container(border=True):
            st.markdown("#### 🏆 Top 5 gastos")
            if df_despesas.empty:
                st.info("Ainda não há despesas para identificar os maiores gastos.")
            else:
                top = df_despesas.groupby("Descrição", as_index=False)["Valor"].sum().nlargest(5, "Valor").sort_values("Valor")
                fig = px.bar(top, x="Valor", y="Descrição", orientation="h", text_auto=".2s", color_discrete_sequence=["#7dd3fc"])
                fig.update_xaxes(title=None, tickprefix="R$ ")
                fig.update_yaxes(title=None)
                fig.update_traces(textposition="outside", cliponaxis=False)
                st.plotly_chart(_estilizar(fig), use_container_width=True)

    painel_c, painel_d = st.columns(2)
    with painel_c:
        with st.container(border=True):
            st.markdown("#### 🍩 Despesas por categoria")
            if df_despesas.empty:
                st.info("Ainda não há despesas para distribuir por categoria.")
            else:
                categorias = df_despesas.groupby("Categoria", as_index=False)["Valor"].sum()
                fig = px.pie(categorias, names="Categoria", values="Valor", hole=.62, color_discrete_sequence=px.colors.sequential.Blues_r)
                fig.update_traces(textposition="inside", textinfo="percent", sort=True)
                st.plotly_chart(_estilizar(fig, legenda=True), use_container_width=True)

    with painel_d:
        with st.container(border=True):
            st.markdown("#### 📅 Despesas por dia da semana")
            if df_despesas.empty:
                st.info("Ainda não há despesas para comparar os dias da semana.")
            else:
                nomes = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
                ordem = list(nomes.values())
                por_dia = df_despesas.assign(**{"Dia da semana": df_despesas["Data"].dt.dayofweek.map(nomes)}).groupby("Dia da semana", as_index=False)["Valor"].sum()
                por_dia["Dia da semana"] = pd.Categorical(por_dia["Dia da semana"], categories=ordem, ordered=True)
                por_dia = por_dia.sort_values("Dia da semana")
                fig = px.bar(por_dia, x="Dia da semana", y="Valor", text_auto=".2s", color_discrete_sequence=["#38bdf8"])
                fig.update_xaxes(title=None)
                fig.update_yaxes(title=None, tickprefix="R$ ")
                fig.update_traces(textposition="outside", cliponaxis=False)
                st.plotly_chart(_estilizar(fig), use_container_width=True)
