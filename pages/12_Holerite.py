import streamlit as st
from datetime import date

from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import adicionar_receita, listar_holerites, listar_receitas, registrar_evento, salvar_holerite
from utils.holerite import extrair_texto_pdf, interpretar_holerite


aplicar_tema()
exigir_login()

st.title("📄 Meu holerite")
st.caption("Importe o PDF, revise as rubricas e registre apenas o salário líquido no seu financeiro.")

arquivo = st.file_uploader("Enviar holerite em PDF", type=["pdf"], help="O arquivo é lido localmente, não é armazenado e deve ter até 10 MB.")
if arquivo:
    try:
        valores_lidos = interpretar_holerite(extrair_texto_pdf(arquivo))
        for campo, valor in valores_lidos.items():
            chave = f"holerite_{campo}"
            if chave not in st.session_state:
                st.session_state[chave] = valor
        st.success("Rubricas identificadas. Confira os valores antes de salvar.")
    except RuntimeError as erro:
        st.error(str(erro))

competencia_padrao = st.session_state.get("holerite_competencia") or date.today().strftime("%Y-%m")
with st.form("salvar_holerite"):
    competencia = st.text_input("Competência", value=competencia_padrao, help="Formato AAAA-MM")
    a, b, c = st.columns(3)
    bruto = a.number_input("Salário bruto", min_value=0.0, value=float(st.session_state.get("holerite_salario_bruto", 0.0)), step=100.0)
    inss = b.number_input("INSS", min_value=0.0, value=float(st.session_state.get("holerite_inss", 0.0)), step=10.0)
    irrf = c.number_input("IRRF", min_value=0.0, value=float(st.session_state.get("holerite_irrf", 0.0)), step=10.0)
    d, e, f = st.columns(3)
    consignado = d.number_input("Consignado", min_value=0.0, value=float(st.session_state.get("holerite_consignado", 0.0)), step=10.0)
    pat = e.number_input("Desconto PAT", min_value=0.0, value=float(st.session_state.get("holerite_pat", 0.0)), step=10.0)
    unimed = f.number_input("Coparticipação Unimed", min_value=0.0, value=float(st.session_state.get("holerite_unimed", 0.0)), step=10.0)
    g, h, i = st.columns(3)
    outros = g.number_input("Outros descontos", min_value=0.0, value=float(st.session_state.get("holerite_outros_descontos", 0.0)), step=10.0)
    fgts = h.number_input("FGTS do mês (depósito)", min_value=0.0, value=float(st.session_state.get("holerite_fgts", 0.0)), step=10.0, help="Informativo: não é descontado do salário líquido.")
    liquido = i.number_input("Salário líquido", min_value=0.0, value=float(st.session_state.get("holerite_salario_liquido", 0.0)), step=100.0)
    registrar_receita = st.checkbox("Registrar o salário líquido como receita", value=True)
    salvar = st.form_submit_button("Salvar holerite", type="primary", use_container_width=True)

if salvar:
    if len(competencia) != 7 or competencia[4] != "-":
        st.error("Informe a competência no formato AAAA-MM.")
    elif liquido <= 0:
        st.error("Informe o salário líquido antes de salvar.")
    else:
        salvar_holerite(competencia, bruto, inss, irrf, consignado, pat, unimed, fgts, outros, liquido, arquivo.name if arquivo else None)
        descricao = f"Holerite {competencia}"
        ja_registrado = any(item["descricao"] == descricao for item in listar_receitas())
        if registrar_receita and not ja_registrado:
            adicionar_receita(f"{competencia}-01", "Salário", descricao, liquido)
        registrar_evento(st.session_state["usuario_id"], "Holerite registrado", f"Competência {competencia}")
        st.success("Holerite salvo." + (" O salário líquido foi registrado como receita." if registrar_receita and not ja_registrado else ""))
        if registrar_receita and ja_registrado:
            st.info("A receita deste holerite já existia; nenhum lançamento duplicado foi criado.")

st.divider()
st.subheader("Como o FinanceOS trata o holerite")
st.info("INSS, IRRF, consignado, PAT e Unimed são descontos do seu salário, não despesas do orçamento. O FGTS é um depósito do empregador e aparece apenas como informação. O app registra como receita somente o valor líquido recebido.")

historico = listar_holerites()
if historico:
    st.subheader("Histórico de salários")
    for item in historico:
        descontos = item["inss"] + item["irrf"] + item["consignado"] + item["pat"] + item["unimed"] + item["outros_descontos"]
        with st.container(border=True):
            st.markdown(f"**{item['competencia']}** · líquido: **{moeda(item['salario_liquido'])}**")
            st.caption(f"Bruto {moeda(item['salario_bruto'])} · descontos {moeda(descontos)} · INSS {moeda(item['inss'])} · IRRF {moeda(item['irrf'])} · consignado {moeda(item['consignado'])} · PAT {moeda(item['pat'])} · Unimed {moeda(item['unimed'])} · FGTS {moeda(item['fgts'])}")
