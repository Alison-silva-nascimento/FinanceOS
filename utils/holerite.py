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
    # Em alguns holerites a referência vem depois do valor (ex.: INSS 533,91 / 14,00).
    # O maior número monetário da mesma rubrica é o valor financeiro, não a referência.
    valores = [float(valor.replace(".", "").replace(",", ".")) for valor in encontrados]
    return max(valores, key=abs)


def _buscar_linha(linhas, padroes):
    for indice, linha in enumerate(linhas):
        if any(re.search(padrao, linha) for padrao in padroes):
            valor = _valor_brl(linha)
            if valor is not None:
                return valor
            # O demonstrativo da Unimed deixa o valor na linha seguinte à rubrica.
            for proxima_linha in linhas[indice + 1:indice + 3]:
                valor = _valor_brl(proxima_linha)
                if valor is not None:
                    return valor
    return 0.0


def _valores_brl(texto):
    return [float(valor.replace(".", "").replace(",", ".")) for valor in re.findall(r"(?:R\$\s*)?(-?[\d.]+,[\d]{2}|-?\d+\.\d{2})", texto)]


def _resumo_unimed(texto):
    """Lê o rodapé do demonstrativo da Unimed, cujos rótulos e valores saem em blocos separados."""
    trecho = re.search(r"TOTAL\s+DE\s+VENCIMENTOS(?P<valores>.*?)(?:ASSINATURA|$)", texto, re.S)
    if not trecho:
        return {}
    valores = _valores_brl(trecho.group("valores"))
    if len(valores) < 9:
        return {}
    # Ordem extraída pelo PDF da Unimed: total de vencimentos, salário INSS,
    # total de descontos, faixa IRRF, base FGTS, FGTS, líquido, base IRRF e salário base.
    return {
        "salario_bruto": valores[0],
        "total_descontos": valores[2],
        "fgts": valores[5],
        "salario_liquido": valores[6],
    }


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
    adiantamento_salarial = _buscar_linha(linhas, [r"(?:DESC\.?\s*)?ADTO\s+SALARIAL", r"ADIANTAMENTO\s+SALARIAL"])
    pat = _buscar_linha(linhas, [r"DESCONTO\s+PAT", r"\bPAT\b"])
    unimed = _buscar_linha(linhas, [r"COPARTICIPACAO\s+UNIMED", r"CARTAO\s+UNIMED", r"\bUNIMED\b"])
    fgts = _buscar_linha(linhas, [r"FGTS\s+DO\s+MES", r"\bFGTS\b"])
    liquido = _buscar_linha(linhas, [r"LIQUIDO\s+A\s+RECEBER", r"TOTAL\s+LIQUIDO", r"VALOR\s+LIQUIDO"])
    total_descontos = _buscar_linha(linhas, [r"TOTAL\s+DESCONTOS"])

    resumo = _resumo_unimed("\n".join(linhas))
    bruto = bruto or resumo.get("salario_bruto", 0.0)
    total_descontos = total_descontos or resumo.get("total_descontos", 0.0)
    fgts = fgts or resumo.get("fgts", 0.0)
    liquido = liquido or resumo.get("salario_liquido", 0.0)
    outros = round(max(total_descontos - inss - irrf - consignado - adiantamento_salarial - pat - unimed, 0.0), 2)

    competencia = None
    texto_normalizado = _normalizar(texto)
    cabecalho_unimed = re.search(r"MES/ANO\s*/\s*(20\d{2}).*?DEMONSTRATIVO.*?\n\s*(0[1-9]|1[0-2])\s*\n", texto_normalizado, re.S)
    correspondencia = re.search(r"\b(0[1-9]|1[0-2])[/-]((?:20)?\d{2})\b", texto_normalizado)
    if cabecalho_unimed:
        competencia = f"{cabecalho_unimed.group(1)}-{cabecalho_unimed.group(2)}"
    elif correspondencia:
        ano = correspondencia.group(2)
        competencia = f"20{ano}" if len(ano) == 2 else ano
        competencia = f"{competencia}-{correspondencia.group(1)}"

    return {
        "competencia": competencia,
        "salario_bruto": bruto,
        "inss": inss,
        "irrf": irrf,
        "consignado": consignado,
        "adiantamento_salarial": adiantamento_salarial,
        "pat": pat,
        "unimed": unimed,
        "fgts": fgts,
        "outros_descontos": outros,
        "salario_liquido": liquido,
    }
