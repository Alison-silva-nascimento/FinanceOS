import pandas as pd
import streamlit as st

from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import adicionar_compra_cartao, listar_cartoes, listar_compras_cartao, registrar_evento
from utils.nubank_fatura import ler_fatura

aplicar_tema(); exigir_login()
st.title("📥 Importar fatura Nubank")
st.caption("As compras são lidas localmente. Pagamentos, créditos, juros e renegociações são ignorados para evitar duplicidade.")
cartoes = listar_cartoes()
if not cartoes: st.info("Cadastre um cartão antes de importar a fatura."); st.stop()
arquivo = st.file_uploader("Fatura Nubank em PDF", type=["pdf"], help="PDF de até 10 MB, sem senha e com no máximo 50 páginas.")
if arquivo and st.button("Ler fatura", type="primary"):
    try:
        st.session_state["compras_nubank"] = ler_fatura(arquivo)
        cartao_nubank = next((f"{c['nome']} · {c['banco']}" for c in cartoes if "nubank" in f"{c['nome']} {c['banco']}".lower()), None)
        if cartao_nubank:
            st.session_state["cartao_importacao"] = cartao_nubank
        st.success(f"{len(st.session_state['compras_nubank'])} compra(s) reconhecida(s). Revise antes de importar.")
    except RuntimeError as erro: st.error(str(erro))

compras = st.session_state.get("compras_nubank", [])
if compras:
    df = pd.DataFrame(compras)
    df["valor_parcela"] = df["valor_parcela"].map(moeda)
    st.dataframe(df.rename(columns={"competencia":"Fatura","valor_parcela":"Valor da parcela","parcela_atual":"Parcela atual","parcelas":"Total de parcelas"}), hide_index=True, use_container_width=True)
    opcoes = {f"{c['nome']} · {c['banco']}": c['id'] for c in cartoes}
    nomes_cartoes = list(opcoes)
    indice_nubank = next((i for i, nome in enumerate(nomes_cartoes) if "nubank" in nome.lower()), 0)
    cartao = st.selectbox("Associar ao cartão", nomes_cartoes, index=indice_nubank, key="cartao_importacao", help="O Nubank é selecionado automaticamente; confirme antes de importar.")
    if st.button("Importar compras revisadas", use_container_width=True):
        existentes = {(x['data'], x['descricao'], round(x['valor'],2)) for x in listar_compras_cartao(opcoes[cartao])}
        total = 0
        for compra in compras:
            valor_total = compra['valor_parcela'] * compra['parcelas']
            chave = (compra['data'], compra['descricao'], round(valor_total,2))
            if chave not in existentes:
                adicionar_compra_cartao(opcoes[cartao], compra['data'], compra['descricao'], compra['categoria'], valor_total, compra['parcelas'], compra['parcela_atual'], compra['competencia'])
                total += 1
        registrar_evento(st.session_state["usuario_id"], "Fatura Nubank importada", f"{total} compra(s) incluída(s)")
        st.success(f"{total} compra(s) importada(s). Compras iguais foram ignoradas.")
        del st.session_state['compras_nubank']
