import streamlit as st


def kpi_card(
    titulo,
    valor,
    icone="📊",
    cor="#1E293B"
):

    st.markdown(
        f"""
<div style="
background:{cor};
border-radius:18px;
padding:22px;
box-shadow:0 4px 12px rgba(0,0,0,.25);
border:1px solid #2E3440;
margin-bottom:10px;
">

<div style="
font-size:16px;
color:#D1D5DB;
margin-bottom:12px;
font-weight:600;
">
{icone} {titulo}
</div>

<div style="
font-size:34px;
color:white;
font-weight:bold;
">
{valor}
</div>

</div>
""",
        unsafe_allow_html=True,
    )
    