from datetime import datetime


def moeda(valor):
    """
    Formata um número para Real Brasileiro.
    """
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_data(data_str):
    """
    Converte AAAA-MM-DD para DD/MM/AAAA.
    """
    return datetime.strptime(
        data_str,
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")


def percentual(valor):
    """
    Formata percentual.
    """
    return f"{valor:.2f}%"
