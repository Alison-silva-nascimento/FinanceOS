"""Leitura assistida de faturas de outros emissores, incluindo PicPay."""

import csv
import re
import unicodedata
from datetime import datetime
from io import BytesIO, StringIO


def _normalizar(valor):
    texto = unicodedata.normalize("NFD", str(valor).lower())
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn").strip()


def _valor(valor):
    texto = str(valor).strip().replace("−", "-").replace("–", "-").replace("R$", "").replace(" ", "")
    negativo = texto.startswith("-") or (texto.startswith("(") and texto.endswith(")"))
    texto = texto.strip("-()")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    resultado = float(texto)
    return -resultado if negativo else resultado


def _data(valor, competencia):
    texto = str(valor).strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return f"{competencia}-01"


def _compra(data, descricao, valor, competencia, incluir=True, observacao=""):
    parcela = re.search(r"(?:parcela\s*)?(\d+)\s*(?:/|de)\s*(\d+)", descricao, re.I)
    atual, total = (int(parcela.group(1)), int(parcela.group(2))) if parcela else (1, 1)
    return {
        "data": data,
        "descricao": " ".join(descricao.split()),
        "valor_parcela": valor,
        "parcela_atual": atual,
        "parcelas": total,
        "categoria": "Outros",
        "competencia": competencia,
        "incluir": incluir,
        "observacao": observacao,
    }


def ler_csv_fatura(arquivo, competencia):
    conteudo = arquivo.getvalue()
    if not conteudo or len(conteudo) > 10 * 1024 * 1024:
        raise RuntimeError("O CSV deve ter no máximo 10 MB.")
    try:
        texto = conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = conteudo.decode("latin-1")
    try:
        dialeto = csv.Sniffer().sniff(texto[:4096], delimiters=";,\t")
    except csv.Error:
        dialeto = csv.excel
        dialeto.delimiter = ";" if texto.count(";") > texto.count(",") else ","
    linhas = list(csv.DictReader(StringIO(texto), dialect=dialeto))
    if not linhas or not linhas[0]:
        raise RuntimeError("O CSV está vazio ou não possui cabeçalho.")
    colunas = {_normalizar(coluna): coluna for coluna in linhas[0]}
    nomes_descricao = ("descricao", "description", "estabelecimento", "origem / destino", "origem/destino", "nome", "titulo", "detalhe", "transacao")
    nomes_valor = ("valor", "amount", "value", "valor da compra", "valor da transacao", "montante")
    nomes_data = ("data", "date", "data da compra", "data da transacao", "data de lancamento")
    coluna_descricao = next((colunas[nome] for nome in nomes_descricao if nome in colunas), None)
    coluna_valor = next((colunas[nome] for nome in nomes_valor if nome in colunas), None)
    coluna_data = next((colunas[nome] for nome in nomes_data if nome in colunas), None)
    coluna_tipo = colunas.get("tipo")
    coluna_pagamento = next((colunas[nome] for nome in ("forma de pagamento", "meio de pagamento") if nome in colunas), None)
    if not coluna_descricao or not coluna_valor:
        raise RuntimeError("Não encontrei as colunas de descrição e valor. Você poderá editar os nomes das colunas no CSV antes de tentar novamente.")
    compras = []
    for linha in linhas:
        descricao = str(linha.get(coluna_descricao, "")).strip()
        try:
            valor = _valor(linha.get(coluna_valor, ""))
        except (TypeError, ValueError):
            continue
        if not descricao or valor == 0:
            continue
        data = _data(linha.get(coluna_data, "") if coluna_data else "", competencia)
        if coluna_pagamento:
            forma = str(linha.get(coluna_pagamento, "")).strip()
            if "cartao" not in _normalizar(forma):
                continue
            tipo = str(linha.get(coluna_tipo, "")).strip() if coluna_tipo else ""
            descricao_completa = f"{tipo} - {descricao}" if tipo else descricao
            observacao = "Confira o valor: o extrato informa uso de saldo + cartão, mas não separa quanto foi cobrado no cartão."
            compras.append(_compra(data, descricao_completa, abs(valor), competencia, incluir=False, observacao=observacao))
        elif valor > 0:
            compras.append(_compra(data, descricao, valor, competencia))
    if not compras:
        raise RuntimeError("Nenhuma movimentação de cartão foi encontrada no CSV.")
    return compras


def ler_pdf_fatura(arquivo, competencia):
    conteudo = arquivo.getvalue()
    if not conteudo or len(conteudo) > 10 * 1024 * 1024:
        raise RuntimeError("O PDF deve ter no máximo 10 MB.")
    try:
        from pypdf import PdfReader
        texto = "\n".join(pagina.extract_text() or "" for pagina in PdfReader(BytesIO(conteudo)).pages)
    except Exception as erro:
        raise RuntimeError("Não foi possível abrir este PDF.") from erro
    compras = []
    padrao = re.compile(
        r"(?m)^\s*(?P<data>\d{2}/\d{2}(?:/\d{2,4})?)\s+(?P<descricao>.+?)\s+(?:R\$\s*)?(?P<valor>[\d.]+,\d{2})\s*$"
    )
    for item in padrao.finditer(texto):
        descricao = item.group("descricao").strip()
        normalizada = _normalizar(descricao)
        if any(termo in normalizada for termo in ("pagamento recebido", "total da fatura", "saldo anterior")):
            continue
        compras.append(_compra(_data(item.group("data"), competencia), descricao, _valor(item.group("valor")), competencia))
    if not compras:
        raise RuntimeError("Nenhuma compra foi reconhecida no PDF. Se o PDF for uma imagem, prefira o CSV do PicPay ou um PDF com texto selecionável.")
    return compras
