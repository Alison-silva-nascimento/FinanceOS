"""Leitura assistida de faturas Nubank em PDF com texto selecionável."""

import re
from io import BytesIO

from utils.arquivos import obter_pdf_seguro

MESES = {"JAN":1,"FEV":2,"MAR":3,"ABR":4,"MAI":5,"JUN":6,"JUL":7,"AGO":8,"SET":9,"OUT":10,"NOV":11,"DEZ":12}
IGNORAR = ("pagamento", "desconto de antecipação", "iof complementar", "crédito de parcelamento", "encerramento de dívida", "renegociação", "limite convertido", "antecipada -")

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
        normalizada = descricao.lower()
        if any(termo in normalizada for termo in IGNORAR):
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
