from html import escape

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
  <div class="finance-kpi__title">{escape(str(icone))} &nbsp;{escape(str(titulo))}</div>
  <div class="finance-kpi__value">{escape(str(valor))}</div>
</div>
""",
        unsafe_allow_html=True,
    )
