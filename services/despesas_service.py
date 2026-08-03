from database.db import (
    listar_despesas,
    obter_despesa,
    adicionar_despesa,
    editar_despesa as db_editar_despesa,
    excluir_despesa,
)

# =========================================
# DESPESAS
# =========================================

def obter_despesas():
    """
    Retorna todas as despesas cadastradas.
    """
    return listar_despesas()


def salvar_despesa(data, categoria, descricao, valor):
    """
    Salva uma nova despesa.
    """
    adicionar_despesa(
        data,
        categoria,
        descricao,
        valor
    )


def atualizar_despesa(id_despesa, data, categoria, descricao, valor):
    """
    Atualiza uma despesa existente.
    """
    db_editar_despesa(
        id_despesa,
        data,
        categoria,
        descricao,
        valor,
    )


def remover_despesa(id_despesa):
    """
    Remove uma despesa.
    """
    excluir_despesa(id_despesa)


def obter_despesa_por_id(id_despesa):
    """
    Retorna uma despesa pelo ID.
    """
    return obter_despesa(id_despesa)


# =========================================
# FUTURAS IMPLEMENTAÇÕES
# =========================================

def buscar_despesas(texto):
    """
    Busca despesas por descrição.
    """
    pass


def filtrar_despesas(
    mes=None,
    ano=None,
    categoria=None
):
    """
    Filtra despesas.
    """
    pass


# =========================================
# KPIs
# =========================================

def calcular_kpis():
    """
    Calcula os indicadores da tela de Despesas.
    """

    despesas = obter_despesas()

    total_despesas = len(despesas)

    valor_total = sum(
        d["valor"]
        for d in despesas
    )

    media = 0

    if total_despesas > 0:
        media = valor_total / total_despesas

    return {
        "total_despesas": total_despesas,
        "valor_total": valor_total,
        "media": media,
    }
