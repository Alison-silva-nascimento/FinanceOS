import pandas as pd
import streamlit as st
from datetime import date

from auth import exigir_login
from components.formatadores import moeda
from components.theme import aplicar_tema
from database.db import (adicionar_compra_cartao, finalizar_importacao, iniciar_importacao,
                         categorizar_por_regras, listar_cartoes, listar_compras_cartao, registrar_evento)
try:
    from database.db import salvar_resumo_fatura
except ImportError:
    # Compatibilidade com instalações em que db.py ainda não foi atualizado.
    def salvar_resumo_fatura(cartao_id, competencia, total_a_pagar, origem="Nubank"):
        return None
from utils.mercado_pago_fatura import ler_csv_fatura, ler_pdf_fatura
from utils.nubank_fatura import extrair_resumo_fatura_pdf, ler_csv_fatura as ler_csv_nubank, ler_fatura
from utils.outros_fatura import ler_csv_fatura as ler_csv_outros, ler_pdf_fatura as ler_pdf_outros


def importar_compras(compras, cartao_id, origem):
    competencia = compras[0].get("competencia") if compras else None
    importacao_id = iniciar_importacao("fatura", origem, competencia=competencia, cartao_id=cartao_id)
    existentes = {(x['data'], x['descricao'], round(x['valor'], 2)) for x in listar_compras_cartao(cartao_id)}
    total = 0
    for compra in compras:
        if not compra.get('categoria') or compra.get('categoria') == 'Outros':
            compra['categoria'] = categorizar_por_regras(compra.get('descricao', ''), compra.get('categoria') or 'Outros')
        valor_total = float(compra['valor_parcela']) * int(compra['parcelas'])
        chave = (compra['data'], compra['descricao'], round(valor_total, 2))
        if chave not in existentes:
            adicionar_compra_cartao(cartao_id, compra['data'], compra['descricao'], compra['categoria'], valor_total, compra['parcelas'], compra['parcela_atual'], compra['competencia'], importacao_id)
            existentes.add(chave)
            total += 1
    finalizar_importacao(importacao_id, total, "concluida" if total else "sem_novos")
    registrar_evento(st.session_state['usuario_id'], f"Fatura {origem} importada", f"{total} compra(s) incluída(s) · lote {importacao_id}")
    return total


aplicar_tema(); exigir_login()
st.title("📥 Importar fatura")
st.caption("Revise as compras antes de importar. Os arquivos são lidos localmente e não são armazenados.")
cartoes = listar_cartoes()
if not cartoes:
    st.info("Cadastre um cartão antes de importar uma fatura.")
    st.stop()

opcoes_cartoes = {c['id']: f"{c['nome']} · {c['banco']}" for c in cartoes}
tab_nubank, tab_mercado, tab_outros = st.tabs(["Nubank", "Mercado Pago", "Outros"])


def limpar_previa_importacao(*chaves):
    """Remove dados temporários quando o usuário retira o arquivo do upload."""
    for chave in chaves:
        st.session_state.pop(chave, None)


with tab_nubank:
    st.caption("Envie o PDF ou CSV da Nubank e confira os lançamentos antes de importar.")
    competencia_nubank = st.text_input("Competência da fatura", value=date.today().strftime("%Y-%m"), key="competencia_nubank", help="Ex.: 2026-08")
    arquivo_nubank = st.file_uploader("Fatura Nubank", type=["pdf", "csv"], key="arquivo_nubank")
    if arquivo_nubank is None:
        limpar_previa_importacao(
            "compras_nubank", "resumo_nubank_importacao", "revisao_nubank",
            "periodo_inicial_nubank", "periodo_final_nubank",
            "valor_fatura_nubank", "valor_fatura_nubank_confirmado",
        )
    if arquivo_nubank and st.button("Ler arquivo", type="primary", key="ler_nubank"):
        if len(competencia_nubank) != 7 or competencia_nubank[4] != "-":
            st.error("Informe a competência no formato AAAA-MM.")
        else:
            try:
                arquivo_csv = arquivo_nubank.name.lower().endswith(".csv")
                leitor = ler_csv_nubank if arquivo_csv else ler_fatura
                compras_lidas = leitor(arquivo_nubank, competencia_nubank) if leitor is ler_csv_nubank else leitor(arquivo_nubank)
                resumo_pdf = None if arquivo_csv else extrair_resumo_fatura_pdf(arquivo_nubank)
                for compra in compras_lidas:
                    compra["competencia"] = competencia_nubank
                    compra["incluir"] = not arquivo_csv
                st.session_state["compras_nubank"] = compras_lidas
                st.session_state["resumo_nubank_importacao"] = resumo_pdf
                if resumo_pdf:
                    st.session_state["valor_fatura_nubank"] = resumo_pdf["total_a_pagar"]
                    st.session_state["valor_fatura_nubank_confirmado"] = resumo_pdf["total_a_pagar"]
                cartao_nubank = next((c['id'] for c in cartoes if "nubank" in f"{c['nome']} {c['banco']}".lower()), None)
                if cartao_nubank:
                    st.session_state["cartao_importacao_nubank"] = cartao_nubank
                st.success(f"{len(compras_lidas)} compra(s) reconhecida(s). Revise antes de importar.")
                if arquivo_csv:
                    st.warning("O CSV da Nubank pode trazer histórico, créditos e parcelas futuras. Marque somente as compras desta fatura na coluna 'incluir'.")
                elif resumo_pdf:
                    periodo = f" · período {resumo_pdf['periodo']}" if resumo_pdf.get("periodo") else ""
                    st.info(f"PDF Nubank identificado: total a pagar de {moeda(resumo_pdf['total_a_pagar'])}{periodo}. Compras financeiras foram separadas das categorias.")
            except RuntimeError as erro:
                st.error(str(erro))

    compras_nubank = st.session_state.get("compras_nubank", [])
    if compras_nubank:
        marcar_todas, desmarcar_todas, selecionar_periodo = st.columns(3)
        if marcar_todas.button("✓ Marcar todas", use_container_width=True, key="marcar_todas_nubank"):
            for compra in compras_nubank:
                compra["incluir"] = True
            st.session_state["compras_nubank"] = compras_nubank
            st.session_state.pop("revisao_nubank", None)
            st.rerun()
        if desmarcar_todas.button("Desmarcar todas", use_container_width=True, key="desmarcar_todas_nubank"):
            for compra in compras_nubank:
                compra["incluir"] = False
            st.session_state["compras_nubank"] = compras_nubank
            st.session_state.pop("revisao_nubank", None)
            st.rerun()
        aplicar_periodo = selecionar_periodo.button("Selecionar período", use_container_width=True, key="selecionar_periodo_nubank")
        datas_compras = sorted({str(compra["data"]) for compra in compras_nubank if compra.get("data")})
        if datas_compras:
            periodo_inicio, periodo_fim = st.columns(2)
            data_inicial = periodo_inicio.date_input(
                "De",
                value=date.fromisoformat(datas_compras[0]),
                min_value=date.fromisoformat(datas_compras[0]),
                max_value=date.fromisoformat(datas_compras[-1]),
                key="periodo_inicial_nubank",
            )
            data_final = periodo_fim.date_input(
                "Até",
                value=date.fromisoformat(datas_compras[-1]),
                min_value=date.fromisoformat(datas_compras[0]),
                max_value=date.fromisoformat(datas_compras[-1]),
                key="periodo_final_nubank",
            )
            if aplicar_periodo:
                if data_final < data_inicial:
                    st.error("A data final deve ser posterior à data inicial.")
                else:
                    inicio, fim = data_inicial.isoformat(), data_final.isoformat()
                    for compra in compras_nubank:
                        compra["incluir"] = inicio <= str(compra.get("data", "")) <= fim
                    st.session_state["compras_nubank"] = compras_nubank
                    st.session_state.pop("revisao_nubank", None)
                    st.rerun()
        st.caption("Use “Marcar todas” para importar a fatura inteira ou selecione apenas as compras desejadas na tabela.")
        editadas = st.data_editor(
            pd.DataFrame(compras_nubank),
            hide_index=True,
            use_container_width=True,
            key="revisao_nubank",
            column_config={"incluir": st.column_config.CheckboxColumn("Importar", help="Marque somente os lançamentos desta fatura.")},
        )
        compras_marcadas = [compra for compra in editadas.to_dict("records") if compra.get("incluir", True)]
        total_marcado = sum(float(compra["valor_parcela"]) for compra in compras_marcadas)
        valor_fatura_nubank = st.number_input(
            "Total a pagar exibido no Nubank (opcional)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Informe o total mostrado no aplicativo Nubank para conferir a seleção do CSV aberto.",
            key="valor_fatura_nubank",
            on_change=lambda: st.session_state.__setitem__("valor_fatura_nubank_confirmado", st.session_state["valor_fatura_nubank"]),
        )
        valor_fatura_nubank = float(st.session_state.get("valor_fatura_nubank_confirmado", valor_fatura_nubank) or 0.0)
        resumo_importacao, resumo_fatura, resumo_ajuste = st.columns(3)
        resumo_importacao.metric("Total selecionado para importar", moeda(total_marcado))
        if valor_fatura_nubank:
            ajuste_financeiro = valor_fatura_nubank - total_marcado
            resumo_fatura.metric("Total a pagar Nubank", moeda(valor_fatura_nubank))
            resumo_ajuste.metric("Ajustes financeiros", moeda(ajuste_financeiro))
            if ajuste_financeiro >= -0.02:
                st.info("Ajustes financeiros incluem fatura anterior, renegociação, créditos e outros lançamentos não distribuídos nas categorias.")
            else:
                st.warning("As compras selecionadas superam o total a pagar da fatura. Revise o período e as linhas marcadas.")
        else:
            resumo_fatura.metric("Total a pagar Nubank", "—")
            resumo_ajuste.metric("Ajustes financeiros", "—")
        indice_nubank = next((indice for indice, cartao_id_opcao in enumerate(opcoes_cartoes) if "nubank" in opcoes_cartoes[cartao_id_opcao].lower()), 0)
        cartao_id = st.selectbox("Associar ao cartão", list(opcoes_cartoes), index=indice_nubank, format_func=opcoes_cartoes.get, key="cartao_importacao_nubank")
        if st.button("Importar compras revisadas", use_container_width=True, key="importar_nubank"):
            compras_revisadas = [compra for compra in editadas.to_dict("records") if compra.pop("incluir", True)]
            if not compras_revisadas:
                st.error("Marque ao menos uma compra para importar.")
            elif valor_fatura_nubank and total_marcado > valor_fatura_nubank + 0.02:
                st.error("A importação foi bloqueada porque as compras selecionadas superam o total a pagar da fatura Nubank.")
            else:
                total = importar_compras(compras_revisadas, cartao_id, "Nubank")
                if valor_fatura_nubank:
                    salvar_resumo_fatura(cartao_id, competencia_nubank, valor_fatura_nubank, "Nubank")
                st.success(f"{total} compra(s) importada(s). Compras iguais foram ignoradas.")
                del st.session_state["compras_nubank"]

with tab_mercado:
    st.caption("Envie o PDF da fatura ou um PDF criado a partir de print. CSV exportado pelo Mercado Pago também é aceito e não precisa de OCR.")
    competencia = st.text_input("Competência da fatura", value=date.today().strftime("%Y-%m"), key="competencia_mercado", help="Ex.: 2026-08")
    arquivo_mercado = st.file_uploader("Fatura Mercado Pago", type=["pdf", "csv"], key="arquivo_mercado")
    if arquivo_mercado is None:
        limpar_previa_importacao(
            "compras_mercado_pago", "revisao_mercado",
            "valor_fatura_mercado", "valor_fatura_mercado_confirmado",
        )
    if arquivo_mercado and st.button("Ler arquivo", type="primary", key="ler_mercado"):
        if len(competencia) != 7 or competencia[4] != "-":
            st.error("Informe a competência no formato AAAA-MM.")
        else:
            try:
                leitor = ler_csv_fatura if arquivo_mercado.name.lower().endswith(".csv") else ler_pdf_fatura
                st.session_state["compras_mercado_pago"] = leitor(arquivo_mercado, competencia)
                st.session_state["valor_fatura_mercado"] = 0.0
                st.session_state["valor_fatura_mercado_confirmado"] = 0.0
                cartao_mercado = next((c['id'] for c in cartoes if "mercado pago" in f"{c['nome']} {c['banco']}".lower()), None)
                if cartao_mercado:
                    st.session_state["cartao_importacao_mercado"] = cartao_mercado
                st.success(f"{len(st.session_state['compras_mercado_pago'])} lançamento(s) reconhecido(s). Revise antes de importar.")
            except RuntimeError as erro:
                st.error(str(erro))

    compras_mercado = st.session_state.get("compras_mercado_pago", [])
    if compras_mercado:
        editadas = st.data_editor(pd.DataFrame(compras_mercado), hide_index=True, use_container_width=True, key="revisao_mercado")
        total_parcelas = sum(float(compra["valor_parcela"]) for compra in editadas.to_dict("records"))
        valor_fatura_mercado = st.number_input(
            "Total a pagar exibido no Mercado Pago (opcional)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Informe o total mostrado no app para conferir os lançamentos e manter o painel de faturas em aberto correto.",
            key="valor_fatura_mercado",
            on_change=lambda: st.session_state.__setitem__("valor_fatura_mercado_confirmado", st.session_state["valor_fatura_mercado"]),
        )
        valor_fatura_mercado = float(st.session_state.get("valor_fatura_mercado_confirmado", valor_fatura_mercado) or 0.0)
        resumo_parcelas, resumo_fatura, resumo_ajuste = st.columns(3)
        resumo_parcelas.metric("Parcelas reconhecidas", moeda(total_parcelas))
        if valor_fatura_mercado:
            ajuste_financeiro = valor_fatura_mercado - total_parcelas
            resumo_fatura.metric("Total a pagar Mercado Pago", moeda(valor_fatura_mercado))
            resumo_ajuste.metric("Ajustes financeiros", moeda(ajuste_financeiro))
            if ajuste_financeiro >= -0.02:
                st.info("A diferença pode incluir encargos, créditos, saldo anterior ou valores não identificados no arquivo.")
            else:
                st.warning("As parcelas reconhecidas superam o total informado. Revise o arquivo antes de importar.")
        else:
            resumo_fatura.metric("Total a pagar Mercado Pago", "—")
            resumo_ajuste.metric("Ajustes financeiros", "—")
        cartao_id = st.selectbox("Associar ao cartão", list(opcoes_cartoes), format_func=opcoes_cartoes.get, key="cartao_importacao_mercado")
        if st.button("Importar parcelas revisadas", use_container_width=True, key="importar_mercado"):
            compras_revisadas = editadas.to_dict("records")
            if valor_fatura_mercado and total_parcelas > valor_fatura_mercado + 0.02:
                st.error("A importação foi bloqueada porque as parcelas superam o total informado do Mercado Pago.")
            else:
                total = importar_compras(compras_revisadas, cartao_id, "Mercado Pago")
                if valor_fatura_mercado:
                    salvar_resumo_fatura(cartao_id, competencia, valor_fatura_mercado, "Mercado Pago")
                st.success(f"{total} parcela(s) importada(s). Compras iguais foram ignoradas.")
                del st.session_state["compras_mercado_pago"]

with tab_outros:
    st.caption("Importe faturas de outros cartões, como PicPay, em CSV ou PDF com texto selecionável. Revise os lançamentos antes de salvar.")
    competencia_outros = st.text_input("Competência da fatura", value=date.today().strftime("%Y-%m"), key="competencia_outros", help="Ex.: 2026-08")
    origem_outros = st.text_input("Emissor", value="PicPay", key="origem_outros", help="Nome que será registrado no histórico da importação.")
    arquivo_outros = st.file_uploader("Fatura de outro cartão", type=["pdf", "csv"], key="arquivo_outros")
    if arquivo_outros is None:
        limpar_previa_importacao(
            "compras_outros", "revisao_outros",
            "valor_fatura_outros", "valor_fatura_outros_confirmado",
        )
    if arquivo_outros and st.button("Ler arquivo", type="primary", key="ler_outros"):
        if len(competencia_outros) != 7 or competencia_outros[4] != "-":
            st.error("Informe a competência no formato AAAA-MM.")
        elif not origem_outros.strip():
            st.error("Informe o nome do emissor.")
        else:
            try:
                leitor = ler_csv_outros if arquivo_outros.name.lower().endswith(".csv") else ler_pdf_outros
                st.session_state["compras_outros"] = leitor(arquivo_outros, competencia_outros)
                st.session_state["valor_fatura_outros"] = 0.0
                st.session_state["valor_fatura_outros_confirmado"] = 0.0
                cartao_picpay = next((c['id'] for c in cartoes if "picpay" in f"{c['nome']} {c['banco']}".lower()), None)
                if cartao_picpay:
                    st.session_state["cartao_importacao_outros"] = cartao_picpay
                st.success(f"{len(st.session_state['compras_outros'])} lançamento(s) reconhecido(s). Revise antes de importar.")
                if any(not compra.get("incluir", True) for compra in st.session_state["compras_outros"]):
                    st.warning("Este é um extrato de conta PicPay. Foram exibidas somente movimentações que mencionam cartão. Como 'saldo + cartão' não separa os valores, confira o valor e marque manualmente o que pertence à fatura.")
            except RuntimeError as erro:
                st.error(str(erro))

    compras_outros = st.session_state.get("compras_outros", [])
    if compras_outros:
        editadas = st.data_editor(
            pd.DataFrame(compras_outros), hide_index=True, use_container_width=True, key="revisao_outros",
            column_config={
                "incluir": st.column_config.CheckboxColumn("Importar", help="Marque apenas o valor que realmente foi cobrado no cartão."),
                "observacao": st.column_config.TextColumn("Atenção", disabled=True),
            },
        )
        todas_editadas = editadas.to_dict("records")
        compras_revisadas = [compra for compra in todas_editadas if compra.get("incluir", True)]
        total_compras = sum(float(compra["valor_parcela"]) for compra in compras_revisadas)
        valor_fatura_outros = st.number_input(
            "Total a pagar exibido na fatura (opcional)", min_value=0.0, value=0.0, step=10.0,
            help="Informe o total exibido no PicPay para conferir os lançamentos e manter o painel correto.",
            key="valor_fatura_outros",
            on_change=lambda: st.session_state.__setitem__("valor_fatura_outros_confirmado", st.session_state["valor_fatura_outros"]),
        )
        valor_fatura_outros = float(st.session_state.get("valor_fatura_outros_confirmado", valor_fatura_outros) or 0.0)
        resumo_compras, resumo_fatura, resumo_ajuste = st.columns(3)
        resumo_compras.metric("Compras reconhecidas", moeda(total_compras))
        resumo_fatura.metric("Total a pagar", moeda(valor_fatura_outros) if valor_fatura_outros else "—")
        resumo_ajuste.metric("Ajustes financeiros", moeda(valor_fatura_outros - total_compras) if valor_fatura_outros else "—")
        cartao_id = st.selectbox("Associar ao cartão", list(opcoes_cartoes), format_func=opcoes_cartoes.get, key="cartao_importacao_outros")
        if st.button("Importar compras revisadas", use_container_width=True, key="importar_outros"):
            if not compras_revisadas:
                st.error("Marque ao menos uma movimentação para importar.")
            elif valor_fatura_outros and total_compras > valor_fatura_outros + 0.02:
                st.error("A importação foi bloqueada porque as compras superam o total informado da fatura.")
            else:
                origem = origem_outros.strip()
                total = importar_compras(compras_revisadas, cartao_id, origem)
                if valor_fatura_outros:
                    salvar_resumo_fatura(cartao_id, competencia_outros, valor_fatura_outros, origem)
                st.success(f"{total} compra(s) importada(s). Compras iguais foram ignoradas.")
                del st.session_state["compras_outros"]
