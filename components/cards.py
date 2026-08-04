import streamlit as st


def kpi_card(
    titulo,
    valor,
    icone="📊",
    cor="#1E293B"
):

    st.markdown(
        f"""
<div class="finance-kpi" style="--accent:{cor};">
  <div class="finance-kpi__title">{icone} &nbsp;{titulo}</div>
  <div class="finance-kpi__value">{valor}</div>
</div>
""",
        unsafe_allow_html=True,
    )
