import streamlit as st
from datetime import date

from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import adicionar_receita, conectar, listar_receitas, registrar_evento
from utils.holerite import extrair_texto_pdf, interpretar_holerite


aplicar_tema()
exigir_login()


def salvar_holerite(competencia, salario_bruto, inss, irrf, consignado, outros_descontos, salario_liquido, arquivo_nome):
    """Compatível com sessões iniciadas antes da atualização do banco."""
    usuario_id = st.session_state["usuario_id"]
    conn = conectar()
    conn.execute("""CREATE TABLE IF NOT EXISTS holerites(
        id INTEGER PRIMARY KEY AUTOINCREMENT, competencia TEXT NOT NULL,
        salario_bruto REAL NOT NULL DEFAULT 0, inss REAL NOT NULL DEFAULT 0,
        irrf REAL NOT NULL DEFAULT 0, consignado REAL NOT NULL DEFAULT 0,
        outros_descontos REAL NOT NULL DEFAULT 0, salario_liquido REAL NOT NULL DEFAULT 0,
        arquivo_nome TEXT, usuario_id INTEGER, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(competencia, usuario_id))""")
    existente = conn.execute("SELECT id FROM holerites WHERE competencia=? AND usuario_id=?", (competencia, usuario_id)).fetchone()
    valores = (salario_bruto, inss, irrf, consignado, outros_descontos, salario_liquido, arquivo_nome)
    if existente:
        conn.execute("UPDATE holerites SET salario_bruto=?, inss=?, irrf=?, consignado=?, outros_descontos=?, salario_liquido=?, arquivo_nome=? WHERE id=? AND usuario_id=?", (*valores, existente["id"], usuario_id))
    else:
        conn.execute("INSERT INTO holerites(competencia,salario_bruto,inss,irrf,consignado,outros_descontos,salario_liquido,arquivo_nome,usuario_id) VALUES(?,?,?,?,?,?,?,?,?)", (competencia, *valores, usuario_id))
    conn.commit()
    conn.close()


def listar_holerites():
    usuario_id = st.session_state["usuario_id"]
    conn = conectar()
    conn.execute("""CREATE TABLE IF NOT EXISTS holerites(
        id INTEGER PRIMARY KEY AUTOINCREMENT, competencia TEXT NOT NULL,
        salario_bruto REAL NOT NULL DEFAULT 0, inss REAL NOT NULL DEFAULT 0,
        irrf REAL NOT NULL DEFAULT 0, consignado REAL NOT NULL DEFAULT 0,
        outros_descontos REAL NOT NULL DEFAULT 0, salario_liquido REAL NOT NULL DEFAULT 0,
        arquivo_nome TEXT, usuario_id INTEGER, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(competencia, usuario_id))""")
    dados = conn.execute("SELECT * FROM holerites WHERE usuario_id=? ORDER BY competencia DESC", (usuario_id,)).fetchall()
    conn.commit()
    conn.close()
    return dados


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
    outros = e.number_input("Outros descontos", min_value=0.0, value=float(st.session_state.get("holerite_outros_descontos", 0.0)), step=10.0)
    liquido = f.number_input("Salário líquido", min_value=0.0, value=float(st.session_state.get("holerite_salario_liquido", 0.0)), step=100.0)
    registrar_receita = st.checkbox("Registrar o salário líquido como receita", value=True)
    salvar = st.form_submit_button("Salvar holerite", type="primary", use_container_width=True)

if salvar:
    if len(competencia) != 7 or competencia[4] != "-":
        st.error("Informe a competência no formato AAAA-MM.")
    elif liquido <= 0:
        st.error("Informe o salário líquido antes de salvar.")
    else:
        salvar_holerite(competencia, bruto, inss, irrf, consignado, outros, liquido, arquivo.name if arquivo else None)
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
st.info("INSS, IRRF e consignado são descontos do seu salário, não despesas do seu orçamento. O app registra como receita somente o valor líquido recebido.")

historico = listar_holerites()
if historico:
    st.subheader("Histórico de salários")
    for item in historico:
        descontos = item["inss"] + item["irrf"] + item["consignado"] + item["outros_descontos"]
        with st.container(border=True):
            st.markdown(f"**{item['competencia']}** · líquido: **{moeda(item['salario_liquido'])}**")
            st.caption(f"Bruto {moeda(item['salario_bruto'])} · descontos {moeda(descontos)} · INSS {moeda(item['inss'])} · IRRF {moeda(item['irrf'])} · consignado {moeda(item['consignado'])}")
