import unicodedata

import pandas as pd
import streamlit as st

from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import (importar_extrato, listar_conciliacoes, marcar_conciliado,
                         sugerir_conciliacoes)


def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).lower().strip())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def valor_brl(valor):
    texto = str(valor).replace("−", "-").replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


aplicar_tema(); exigir_login()
st.title("🔄 Conciliação bancária")
st.caption("Importe extratos, elimine duplicidades e associe cada movimentação ao lançamento correspondente.")

arquivo = st.file_uploader("Extrato CSV", type=["csv"])
if arquivo and st.button("Importar extrato", type="primary"):
    try:
        tabela = pd.read_csv(arquivo, sep=None, engine="python")
        colunas = {normalizar(c): c for c in tabela.columns}
        coluna_data = colunas.get("data") or colunas.get("date")
        coluna_descricao = next((colunas[c] for c in ("descricao", "origem / destino", "origem/destino", "estabelecimento") if c in colunas), None)
        coluna_valor = colunas.get("valor") or colunas.get("amount")
        if not all((coluna_data, coluna_descricao, coluna_valor)):
            raise ValueError("O CSV precisa ter colunas de data, descrição/origem e valor.")
        itens = [{"data":str(x[coluna_data])[:10],"descricao":str(x[coluna_descricao]),"valor":valor_brl(x[coluna_valor])} for _,x in tabela.iterrows()]
        incluidos = importar_extrato(itens, "Extrato bancário", arquivo.name)
        st.success(f"{incluidos} lançamento(s) novo(s) importado(s). Duplicidades foram ignoradas.")
        st.rerun()
    except Exception as erro:
        st.error(str(erro))

pendentes = [item for item in listar_conciliacoes() if not item["conciliado"]]
concluidos = [item for item in listar_conciliacoes() if item["conciliado"]]
st.metric("Pendências de conciliação", len(pendentes))

for item in pendentes:
    with st.expander(f"⏳ {item['data']} · {item['descricao']} · {moeda(item['valor'])}"):
        sugestoes = sugerir_conciliacoes(item["id"])
        if sugestoes:
            opcoes = {f"{x['data']} · {x['descricao']} · {moeda(x['valor'])}": x for x in sugestoes}
            escolhido = st.selectbox("Correspondência sugerida", list(opcoes), key=f"sug_{item['id']}")
            if st.button("Conciliar com lançamento", key=f"vinc_{item['id']}", use_container_width=True):
                sugestao = opcoes[escolhido]
                marcar_conciliado(item["id"], sugestao["vinculo_tipo"], sugestao["id"]); st.rerun()
        else:
            st.info("Nenhum lançamento com mesmo valor e data próxima foi encontrado.")
        if st.button("Marcar como conferido sem vínculo", key=f"manual_{item['id']}", use_container_width=True):
            marcar_conciliado(item["id"]); st.rerun()

with st.expander(f"Concluídos ({len(concluidos)})"):
    for item in concluidos[:100]:
        st.caption(f"✅ {item['data']} · {item['descricao']} · {moeda(item['valor'])}")
