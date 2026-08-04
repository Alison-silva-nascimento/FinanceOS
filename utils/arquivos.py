"""Valida anexos sem gravar arquivos enviados em disco."""

from io import BytesIO

MAX_PDF_BYTES = 10 * 1024 * 1024
MAX_PAGINAS_PDF = 50


def obter_pdf_seguro(arquivo):
    """Retorna bytes de um PDF válido, limitado e não criptografado."""
    dados = arquivo.getvalue()
    if not dados or len(dados) > MAX_PDF_BYTES:
        raise RuntimeError("O PDF deve ter no máximo 10 MB.")
    if not dados.startswith(b"%PDF-"):
        raise RuntimeError("O arquivo enviado não é um PDF válido.")
    try:
        from pypdf import PdfReader
        leitor = PdfReader(BytesIO(dados))
        if leitor.is_encrypted:
            raise RuntimeError("PDF protegido por senha não é aceito.")
        if len(leitor.pages) > MAX_PAGINAS_PDF:
            raise RuntimeError("O PDF possui páginas demais para importação.")
    except RuntimeError:
        raise
    except Exception as erro:
        raise RuntimeError("Não foi possível validar este PDF.") from erro
    return dados
