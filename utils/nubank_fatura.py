"""Leitura assistida de faturas Nubank em PDF com texto selecionável."""

import csv
import re
import unicodedata
from io import BytesIO

from utils.arquivos import obter_pdf_seguro

MESES = {"JAN":1,"FEV":2,"MAR":3,"ABR":4,"MAI":5,"JUN":6,"JUL":7,"AGO":8,"SET":9,"OUT":10,"NOV":11,"DEZ":12}
IGNORAR = ("pagamento recebido", "desconto de antecip", "iof complementar", "encerramento de divida", "limite convertido", "antecipada -")
IGNORAR_PDF = ("encerramento de divida", "antecipada -", "renegociacao de pendencias", "limite convertido", "iof complementar por renegociacao")

def categorizar(descricao):
    texto = descricao.lower()
    regras = {"Alimentação":("ifood","restaurante","pizza","sorvete","natural","bar"),"Assinaturas":("openai","chatgpt","youtube","discord","hbo","apple.com","melimais"),"Transporte":("posto","uber","despachante"),"Saúde":("bluefit","farmacia","seguro"),"Compras":("mercadolivre","mercado","neshastore")}
    for categoria, termos in regras.items():
        if any(termo in texto for termo in termos): return categoria
    return "Outros"


def _brl(valor):
    return float(valor.replace(".", "").replace(",", "."))


def ler_fatura(arquivo):
    try:
        from pypdf import PdfReader
        leitor = PdfReader(BytesIO(obter_pdf_seguro(arquivo)))
    except Exception as erro:
        raise RuntimeError("Não foi possível abrir o PDF. Use a fatura Nubank com texto selecionável.") from erro
    texto = "\n".join(p.extract_text() or "" for p in leitor.pages)
    referencia = re.search(r"FATURA\s+\d{2}\s+(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+(20\d{2})", texto)
    if not referencia:
        raise RuntimeError("Não identifiquei a competência da fatura.")
    ano = int(referencia.group(2))
    competencia = f"{ano}-{MESES[referencia.group(1)]:02d}"
    transacoes = []
    padrao = re.compile(r"(?m)^(\d{2})\s+(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+(.+?)\s+R\$\s*([\d.]+,\d{2})")
    for dia, mes, descricao, valor in padrao.findall(texto):
        descricao = " ".join(descricao.replace("\n", " ").split())
        normalizada = _normalizar_coluna(descricao)
        if any(termo in normalizada for termo in IGNORAR_PDF):
            continue
        parcela = re.search(r"Parcela\s+(\d+)/(\d+)", descricao, re.I)
        atual, total = (int(parcela.group(1)), int(parcela.group(2))) if parcela else (1, 1)
        transacoes.append({
            "data": f"{ano}-{MESES[mes]:02d}-{int(dia):02d}", "descricao": descricao,
            "valor_parcela": _brl(valor), "parcela_atual": atual, "parcelas": total,
            "categoria": categorizar(descricao), "competencia": competencia,
        })
    if not transacoes:
        raise RuntimeError("Nenhuma compra reconhecida. Revise se este é o PDF da fatura Nubank.")
    return transacoes


def extrair_resumo_fatura_pdf(arquivo):
    """Retorna competência, período e total a pagar de uma fatura Nubank em PDF."""
    try:
        from pypdf import PdfReader
        leitor = PdfReader(BytesIO(obter_pdf_seguro(arquivo)))
    except Exception as erro:
        raise RuntimeError("Não foi possível abrir o PDF da fatura Nubank.") from erro
    texto = "\n".join(p.extract_text() or "" for p in leitor.pages)
    referencia = re.search(r"FATURA\s+\d{2}\s+(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+(20\d{2})", texto)
    total = re.search(r"(?:Total a pagar|Pagamento total da fatura)\s*R\$\s*([\d.]+,\d{2})", texto, re.I)
    periodo = re.search(r"Per[ií]odo vigente:\s*(\d{2}\s+[A-Z]{3}\s+a\s+\d{2}\s+[A-Z]{3})", texto, re.I)
    if not referencia or not total:
        raise RuntimeError("Não identifiquei o resumo da fatura Nubank no PDF.")
    competencia = f"{referencia.group(2)}-{MESES[referencia.group(1)]:02d}"
    return {"competencia": competencia, "total_a_pagar": _brl(total.group(1)), "periodo": periodo.group(1) if periodo else None}


def _normalizar_coluna(valor):
    texto = unicodedata.normalize("NFD", str(valor).lower())
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn").strip()


def _valor_csv(valor):
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    negativo = texto.startswith("-") or (texto.startswith("(") and texto.endswith(")"))
    texto = texto.strip("-()")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    resultado = float(texto)
    return -resultado if negativo else resultado


def _data_csv(valor):
    texto = str(valor).strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            from datetime import datetime
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def ler_csv_fatura(arquivo, competencia):
    """Lê CSVs usuais da Nubank e deixa os lançamentos prontos para revisão."""
    conteudo = arquivo.getvalue()
    if not conteudo or len(conteudo) > 10 * 1024 * 1024:
        raise RuntimeError("O CSV deve ter no máximo 10 MB.")
    try:
        texto = conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = conteudo.decode("latin-1")
    try:
        dialecto = csv.Sniffer().sniff(texto[:4096], delimiters=";,\t")
    except csv.Error:
        dialecto = csv.excel
        dialecto.delimiter = ";" if texto.count(";") > texto.count(",") else ","
    linhas = list(csv.DictReader(texto.splitlines(), dialect=dialecto))
    if not linhas or not linhas[0]:
        raise RuntimeError("Não foi possível identificar as colunas do CSV Nubank.")
    colunas = {_normalizar_coluna(coluna): coluna for coluna in linhas[0]}
    coluna_data = next((colunas[chave] for chave in ("data", "date", "data da transacao", "transaction date") if chave in colunas), None)
    coluna_descricao = next((colunas[chave] for chave in ("descricao", "description", "titulo", "title", "descricao da transacao") if chave in colunas), None)
    coluna_valor = next((colunas[chave] for chave in ("valor", "amount", "value", "valor da transacao") if chave in colunas), None)
    if not all((coluna_data, coluna_descricao, coluna_valor)):
        raise RuntimeError("O CSV precisa ter colunas de data, descrição e valor.")
    compras = []
    for linha in linhas:
        data = _data_csv(linha.get(coluna_data, ""))
        descricao = " ".join(str(linha.get(coluna_descricao, "")).split())
        try:
            valor = _valor_csv(linha.get(coluna_valor, ""))
        except ValueError:
            continue
        normalizada = _normalizar_coluna(descricao)
        credito_parcelamento = "parcelamento de compra" in normalizada
        # Pagamentos e descontos de antecipação não pertencem à fatura em aberto.
        # Já o crédito de parcelamento reduz o valor da própria fatura e deve ser preservado.
        if any(termo in normalizada for termo in IGNORAR) or "renegociacao de pendencias" in normalizada:
            continue
        if valor <= 0 and not credito_parcelamento:
            continue
        parcela = re.search(r"(?:PARCELA\s*)?(\d+)\s*/\s*(\d+)", descricao, re.I)
        atual, total = (int(parcela.group(1)), int(parcela.group(2))) if parcela else (1, 1)
        if data and descricao:
            compras.append({
                "data": data, "descricao": descricao, "valor_parcela": valor,
                "parcela_atual": atual, "parcelas": total,
                "categoria": categorizar(descricao), "competencia": competencia,
            })
    if not compras:
        raise RuntimeError("Nenhum lançamento foi reconhecido no CSV Nubank. Revise o arquivo exportado.")
    return compras
