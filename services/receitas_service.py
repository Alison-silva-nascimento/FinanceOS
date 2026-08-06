from database.db import (
    listar_receitas,
    obter_receita,
    adicionar_receita,
    editar_receita as db_editar_receita,
    excluir_receita,
)
from datetime import date

# =========================================
# RECEITAS
# =========================================

def obter_receitas():
    """
    Retorna todas as receitas cadastradas.
    """
    return listar_receitas()


def salvar_receita(data, categoria, descricao, valor):
    """
    Salva uma nova receita.
    """
    adicionar_receita(
        data,
        categoria,
        descricao,
        valor
    )

def atualizar_receita(id_receita, data, categoria, descricao, valor):
    """
    Atualiza uma receita existente.
    """
    db_editar_receita(
        id_receita,
        data,
        categoria,
        descricao,
        valor,
    )   

def remover_receita(id_receita):
    """
    Remove uma receita pelo ID.
    """
    excluir_receita(id_receita)

def obter_receita_por_id(id_receita):
    """
    Retorna uma receita pelo ID.
    """
    return obter_receita(id_receita)


# =========================================
# FUTURAS IMPLEMENTAÇÕES
# =========================================

def buscar_receitas(texto):
    """
    Busca receitas por descrição.
    """
    pass


def filtrar_receitas(
    mes=None,
    ano=None,
    categoria=None
):
    """
    Filtra receitas.
    """
    pass


# =========================================
# KPIs
# =========================================

def calcular_kpis():
    """
    Calcula os indicadores da tela de Receitas.
    """

    receitas = obter_receitas()

    total_receitas = len(receitas)

    valor_total = sum(
        r["valor"]
        for r in receitas
    )

    mes_atual = date.today().strftime("%Y-%m")
    receita_mes = sum(
        receita["valor"]
        for receita in receitas
        if str(receita["data"]).startswith(mes_atual)
    )

    return {
        "total_receitas": total_receitas,
        "valor_total": valor_total,
        "receita_mes": receita_mes,
        "mes_atual": mes_atual,
    }

