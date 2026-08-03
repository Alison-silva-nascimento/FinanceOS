from database.db import (
    adicionar_cartao,
    listar_cartoes,
    obter_cartao,
    editar_cartao,
    excluir_cartao,
    quantidade_cartoes,
    limite_total
)

# ==========================================
# LISTAR
# ==========================================

def obter_cartoes():
    return listar_cartoes()


# ==========================================
# OBTER POR ID
# ==========================================

def obter_cartao_por_id(id_cartao):
    return obter_cartao(id_cartao)


# ==========================================
# SALVAR
# ==========================================

def salvar_cartao(
    nome,
    banco,
    bandeira,
    limite,
    fechamento,
    vencimento,
    cor
):

    adicionar_cartao(
        nome,
        banco,
        bandeira,
        limite,
        fechamento,
        vencimento,
        cor
    )


# ==========================================
# ATUALIZAR
# ==========================================

def atualizar_cartao(
    id_cartao,
    nome,
    banco,
    bandeira,
    limite,
    fechamento,
    vencimento,
    cor
):

    editar_cartao(
        id_cartao,
        nome,
        banco,
        bandeira,
        limite,
        fechamento,
        vencimento,
        cor
    )


# ==========================================
# REMOVER
# ==========================================

def remover_cartao(id_cartao):
    excluir_cartao(id_cartao)


# ==========================================
# KPIs
# ==========================================

def calcular_kpis():

    total_cartoes = quantidade_cartoes()

    limite = limite_total()

    media = (
        limite / total_cartoes
        if total_cartoes > 0
        else 0
    )

    return {
        "total_cartoes": total_cartoes,
        "limite_total": limite,
        "media_limite": media
    }
