import streamlit as st
import pandas as pd


def mostrar_tabela(
    df: pd.DataFrame,
    titulo: str = "",
    esconder_indice: bool = True,
):
    """
    Exibe uma tabela padronizada do FinanceOS.
    """

    if titulo:
        st.subheader(titulo)

    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=esconder_indice,
    )
    