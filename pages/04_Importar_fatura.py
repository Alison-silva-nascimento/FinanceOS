import pandas as pd
import streamlit as st
from datetime import date

from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import adicionar_compra_cartao, listar_cartoes, listar_compras_cartao, registrar_evento
from utils.mercado_pago_fatura import ler_csv_fatura, ler_pdf_fatura
from utils.nubank_fatura import ler_fatura


def importar_compras(compras, cartao_id, origem):
    existentes = {(x['data'], x['descricao'], round(x['valor'], 2)) for x in listar_compras_cartao(cartao_id)}
    total = 0
    for compra in compras:
        valor_total = float(compra['valor_parcela']) * int(compra['parcelas'])
        chave = (compra['data'], compra['descricao'], round(valor_total, 2))
        if chave not in existentes:
            adicionar_compra_cartao(cartao_id, compra['data'], compra['descricao'], compra['categoria'], valor_total, compra['parcelas'], compra['parcela_atual'], compra['competencia'])
            existentes.add(chave)
            total += 1
    registrar_evento(st.session_state['usuario_id'], f"Fatura {origem} importada", f"{total} compra(s) incluída(s)")
    return total


aplicar_tema(); exigir_login()
st.title("📥 Importar fatura")
st.caption("Revise as compras antes de importar. Os arquivos são lidos localmente e não são armazenados.")
cartoes = listar_cartoes()
if not cartoes:
    st.info("Cadastre um cartão antes de importar uma fatura.")
    st.stop()

opcoes_cartoes = {c['id']: f"{c['nome']} · {c['banco']}" for c in cartoes}
tab_nubank, tab_mercado = st.tabs(["Nubank · PDF", "Mercado Pago · PDF/CSV"])

with tab_nubank:
    st.caption("Envie o PDF da fatura Nubank e confira os lançamentos antes de importar.")
    competencia_nubank = st.text_input("Competência da fatura", value=date.today().strftime("%Y-%m"), key="competencia_nubank", help="Ex.: 2026-08")
    arquivo_nubank = st.file_uploader("Fatura Nubank em PDF", type=["pdf"], key="arquivo_nubank")
    if arquivo_nubank and st.button("Ler PDF", type="primary", key="ler_nubank"):
        if len(competencia_nubank) != 7 or competencia_nubank[4] != "-":
            st.error("Informe a competência no formato AAAA-MM.")
        else:
            try:
                compras_lidas = ler_fatura(arquivo_nubank)
                for compra in compras_lidas:
                    compra["competencia"] = competencia_nubank
                st.session_state["compras_nubank"] = compras_lidas
                cartao_nubank = next((c['id'] for c in cartoes if "nubank" in f"{c['nome']} {c['banco']}".lower()), None)
                if cartao_nubank:
                    st.session_state["cartao_importacao_nubank"] = cartao_nubank
                st.success(f"{len(compras_lidas)} compra(s) reconhecida(s). Revise antes de importar.")
            except RuntimeError as erro:
                st.error(str(erro))

    compras_nubank = st.session_state.get("compras_nubank", [])
    if compras_nubank:
        editadas = st.data_editor(pd.DataFrame(compras_nubank), hide_index=True, use_container_width=True, key="revisao_nubank")
        cartao_id = st.selectbox("Associar ao cartão", list(opcoes_cartoes), format_func=opcoes_cartoes.get, key="cartao_importacao_nubank")
        if st.button("Importar compras revisadas", use_container_width=True, key="importar_nubank"):
            total = importar_compras(editadas.to_dict("records"), cartao_id, "Nubank")
            st.success(f"{total} compra(s) importada(s). Compras iguais foram ignoradas.")
            del st.session_state["compras_nubank"]

with tab_mercado:
    st.caption("Envie o PDF da fatura ou um PDF criado a partir de print. CSV exportado pelo Mercado Pago também é aceito e não precisa de OCR.")
    competencia = st.text_input("Competência da fatura", value=date.today().strftime("%Y-%m"), key="competencia_mercado", help="Ex.: 2026-08")
    arquivo_mercado = st.file_uploader("Fatura Mercado Pago", type=["pdf", "csv"], key="arquivo_mercado")
    if arquivo_mercado and st.button("Ler arquivo", type="primary", key="ler_mercado"):
        if len(competencia) != 7 or competencia[4] != "-":
            st.error("Informe a competência no formato AAAA-MM.")
        else:
            try:
                leitor = ler_csv_fatura if arquivo_mercado.name.lower().endswith(".csv") else ler_pdf_fatura
                st.session_state["compras_mercado_pago"] = leitor(arquivo_mercado, competencia)
                cartao_mercado = next((c['id'] for c in cartoes if "mercado pago" in f"{c['nome']} {c['banco']}".lower()), None)
                if cartao_mercado:
                    st.session_state["cartao_importacao_mercado"] = cartao_mercado
                st.success(f"{len(st.session_state['compras_mercado_pago'])} lançamento(s) reconhecido(s). Revise antes de importar.")
            except RuntimeError as erro:
                st.error(str(erro))

    compras_mercado = st.session_state.get("compras_mercado_pago", [])
    if compras_mercado:
        editadas = st.data_editor(pd.DataFrame(compras_mercado), hide_index=True, use_container_width=True, key="revisao_mercado")
        cartao_id = st.selectbox("Associar ao cartão", list(opcoes_cartoes), format_func=opcoes_cartoes.get, key="cartao_importacao_mercado")
        if st.button("Importar parcelas revisadas", use_container_width=True, key="importar_mercado"):
            compras_revisadas = editadas.to_dict("records")
            total = importar_compras(compras_revisadas, cartao_id, "Mercado Pago")
            st.success(f"{total} parcela(s) importada(s). Compras iguais foram ignoradas.")
            del st.session_state["compras_mercado_pago"]
