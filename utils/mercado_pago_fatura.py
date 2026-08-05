"""Leitura assistida de faturas Mercado Pago em PDF ou CSV."""

import csv
import os
import re
import shutil
import unicodedata
from io import BytesIO, StringIO
from pathlib import Path


def _brl(valor):
    return float(str(valor).replace("R$", "").replace(".", "").replace(",", ".").strip())


def _normalizar(valor):
    texto = unicodedata.normalize("NFD", str(valor).lower())
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn").strip()


def _ocr(imagem):
    try:
        from PIL import ImageEnhance, ImageOps
        import pytesseract
        if not shutil.which("tesseract"):
            candidatos = [
                Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
                Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
            ]
            caminho_padrao = next((caminho for caminho in candidatos if caminho.exists()), None)
            if caminho_padrao:
                pytesseract.pytesseract.tesseract_cmd = str(caminho_padrao)
        imagem = imagem.convert("RGB").resize((imagem.width * 2, imagem.height * 2))
        imagem = ImageOps.autocontrast(ImageEnhance.Contrast(imagem.convert("L")).enhance(1.8))
        try:
            return pytesseract.image_to_string(imagem, lang="por", config="--oem 3 --psm 6")
        except pytesseract.TesseractError:
            return pytesseract.image_to_string(imagem, lang="eng", config="--oem 3 --psm 6")
    except ImportError as erro:
        raise RuntimeError("O leitor OCR não está disponível. Execute `pip install -r requirements.txt` e reinicie o FinanceOS.") from erro
    except pytesseract.TesseractNotFoundError as erro:
        raise RuntimeError("O OCR Tesseract foi instalado, mas não foi localizado pelo FinanceOS. Reinicie o Streamlit; se continuar, execute `where.exe tesseract` no terminal. Arquivos CSV não precisam de OCR.") from erro


def _compras_do_texto(texto, competencia):
    # Layout mais comum do app Mercado Pago depois do OCR:
    # "Descrição  R$ valor" em uma linha e "Solicitado... Parcela X de Y" na seguinte.
    linhas = [" ".join(linha.split()) for linha in texto.splitlines() if linha.strip()]
    compras = []
    for indice, linha in enumerate(linhas[:-1]):
        proxima = linhas[indice + 1]
        valor = re.search(r"(?P<valor>[\d.]+,\d{2})\s*$", linha)
        parcela = re.search(r"Parcela\s*(?P<atual>\d+)\s*(?:de|do)\s*(?P<total>\d+)", proxima, re.IGNORECASE)
        if not valor or not parcela or not re.search(r"Solicitado", proxima, re.IGNORECASE):
            continue
        descricao = linha[:valor.start()].strip()
        descricao = re.sub(r"\s+[A-Z]{1,2}\$?\s*$", "", descricao, flags=re.IGNORECASE)
        descricao = re.sub(r"^[^A-Za-zÀ-ÿ]+", "", descricao).strip()
        descricao = re.sub(r"^(?:Ry|A)\s+", "", descricao)
        if descricao:
            compras.append({"data": f"{competencia}-01", "descricao": descricao, "valor_parcela": _brl(valor.group("valor")), "parcela_atual": int(parcela.group("atual")), "parcelas": int(parcela.group("total")), "categoria": "Outros", "competencia": competencia})
    if compras:
        return compras

    padrao = re.compile(
        r"(?P<descricao>[^\n]+?)\s*\n\s*Solicitado[^\n]*\n\s*R\$\s*(?P<valor>[\d.]+,\d{2})\s*\n\s*Parcela\s*(?P<atual>\d+)\s*(?:de|do)\s*(?P<total>\d+)", re.IGNORECASE,
    )
    compras = []
    for item in padrao.finditer(texto):
        compras.append({"data": f"{competencia}-01", "descricao": " ".join(item.group("descricao").split()), "valor_parcela": _brl(item.group("valor")), "parcela_atual": int(item.group("atual")), "parcelas": int(item.group("total")), "categoria": "Outros", "competencia": competencia})
    if compras:
        return compras

    for indice, linha in enumerate(linhas):
        valor = re.search(r"R\$\s*([\d.]+,\d{2})", linha, re.IGNORECASE)
        parcela = re.search(r"Parcela\s*(\d+)\s*(?:de|do)\s*(\d+)", linha, re.IGNORECASE)
        parcela = parcela or re.search(r"Parcela\s*(\d+)\s*(?:de|do)\s*(\d+)", " ".join(linhas[indice + 1:indice + 3]), re.IGNORECASE)
        if not valor or not parcela:
            continue
        descricao = next((candidata for candidata in reversed(linhas[max(0, indice - 3):indice]) if not re.search(r"solicitado|vence|r\$|parcela", candidata, re.IGNORECASE)), None)
        if descricao:
            compras.append({"data": f"{competencia}-01", "descricao": descricao, "valor_parcela": _brl(valor.group(1)), "parcela_atual": int(parcela.group(1)), "parcelas": int(parcela.group(2)), "categoria": "Outros", "competencia": competencia})
    return compras


def ler_pdf_fatura(arquivo, competencia):
    """Renderiza as páginas localmente e aplica OCR; aceita PDF criado a partir de print."""
    if len(arquivo.getvalue()) > 10 * 1024 * 1024:
        raise RuntimeError("O PDF deve ter no máximo 10 MB.")
    try:
        import fitz
        from PIL import Image
        documento = fitz.open(stream=arquivo.getvalue(), filetype="pdf")
        if documento.page_count > 10:
            raise RuntimeError("O PDF possui páginas demais para importação.")
        textos = []
        for pagina in documento:
            pixmap = pagina.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            imagem = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            textos.append(_ocr(imagem))
        texto = "\n".join(textos)
    except RuntimeError:
        raise
    except Exception as erro:
        raise RuntimeError("Não foi possível abrir ou ler este PDF.") from erro
    compras = _compras_do_texto(texto, competencia)
    if not compras:
        raise RuntimeError("Nenhuma parcela foi identificada. Use um PDF nítido, com a lista completa de itens e valores visível.")
    return compras


def ler_csv_fatura(arquivo, competencia):
    """Lê CSV exportado pelo Mercado Pago e apresenta tudo para revisão."""
    try:
        bruto = arquivo.getvalue().decode("utf-8-sig")
    except UnicodeDecodeError:
        bruto = arquivo.getvalue().decode("latin-1")
    amostra = bruto[:4096]
    try:
        dialeto = csv.Sniffer().sniff(amostra, delimiters=";,\t")
    except csv.Error:
        dialeto = csv.excel
    linhas = list(csv.DictReader(StringIO(bruto), dialect=dialeto))
    if not linhas:
        raise RuntimeError("O CSV está vazio ou não possui cabeçalho.")
    colunas = {_normalizar(coluna): coluna for coluna in linhas[0]}
    descricao_coluna = next((colunas[nome] for nome in ("descricao", "descricao da operacao", "conceito", "detalhe") if nome in colunas), None)
    valor_coluna = next((colunas[nome] for nome in ("valor", "valor da operacao", "montante", "amount") if nome in colunas), None)
    data_coluna = next((colunas[nome] for nome in ("data", "data de liberacao", "date") if nome in colunas), None)
    if not descricao_coluna or not valor_coluna:
        raise RuntimeError("Não encontrei as colunas de descrição e valor neste CSV. Use o CSV exportado pelo Mercado Pago.")
    compras = []
    for linha in linhas:
        try:
            valor = _brl(linha[valor_coluna])
        except ValueError:
            continue
        if valor <= 0:
            continue
        data = linha.get(data_coluna, "") if data_coluna else ""
        compras.append({"data": data if re.match(r"\d{4}-\d{2}-\d{2}", data) else f"{competencia}-01", "descricao": linha[descricao_coluna].strip(), "valor_parcela": valor, "parcela_atual": 1, "parcelas": 1, "categoria": "Outros", "competencia": competencia})
    if not compras:
        raise RuntimeError("Nenhum lançamento positivo foi encontrado no CSV.")
    return compras
