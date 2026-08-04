"""Leitura local de indicadores de holerites em PDF com texto selecionável."""

import re
import unicodedata
from io import BytesIO

from utils.arquivos import obter_pdf_seguro


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.upper())
    return "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")


def _valor_brl(texto):
    encontrados = re.findall(r"(?:R\$\s*)?(-?[\d.]+,[\d]{2}|-?\d+\.\d{2})", texto)
    if not encontrados:
        return None
    valor = encontrados[-1].replace(".", "").replace(",", ".")
    return float(valor)


def _buscar_linha(linhas, padroes):
    for linha in linhas:
        if any(re.search(padrao, linha) for padrao in padroes):
            valor = _valor_brl(linha)
            if valor is not None:
                return valor
    return 0.0


def extrair_texto_pdf(arquivo):
    """Retorna o texto de um PDF; o arquivo nunca é gravado em disco."""
    try:
        from pypdf import PdfReader
    except ImportError as erro:
        raise RuntimeError("Instale as dependências com `pip install -r requirements.txt`.") from erro
    try:
        leitor = PdfReader(BytesIO(obter_pdf_seguro(arquivo)))
        return "\n".join(pagina.extract_text() or "" for pagina in leitor.pages)
    except Exception as erro:
        raise RuntimeError("Não foi possível ler este PDF. Envie um holerite com texto selecionável.") from erro


def interpretar_holerite(texto):
    """Extrai as rubricas mais comuns; os valores devem ser confirmados na tela."""
    linhas = [_normalizar(linha) for linha in texto.splitlines() if linha.strip()]
    bruto = _buscar_linha(linhas, [r"SALARIO\s+BASE", r"SALARIO\s+BRUTO", r"TOTAL\s+PROVENTOS"])
    inss = _buscar_linha(linhas, [r"\bINSS\b"])
    irrf = _buscar_linha(linhas, [r"\bIRRF\b", r"IMPOSTO\s+DE\s+RENDA"])
    consignado = _buscar_linha(linhas, [r"CONSIGNAD"])
    liquido = _buscar_linha(linhas, [r"LIQUIDO\s+A\s+RECEBER", r"TOTAL\s+LIQUIDO", r"VALOR\s+LIQUIDO"])
    total_descontos = _buscar_linha(linhas, [r"TOTAL\s+DESCONTOS"])
    outros = max(total_descontos - inss - irrf - consignado, 0.0)

    competencia = None
    correspondencia = re.search(r"\b(0[1-9]|1[0-2])[/-]((?:20)?\d{2})\b", _normalizar(texto))
    if correspondencia:
        ano = correspondencia.group(2)
        competencia = f"20{ano}" if len(ano) == 2 else ano
        competencia = f"{competencia}-{correspondencia.group(1)}"

    return {
        "competencia": competencia,
        "salario_bruto": bruto,
        "inss": inss,
        "irrf": irrf,
        "consignado": consignado,
        "outros_descontos": outros,
        "salario_liquido": liquido,
    }
