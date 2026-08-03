import sqlite3
from pathlib import Path

# ==========================================
# CONFIGURAÇÃO DO BANCO
# ==========================================

DB_FILE = Path(__file__).parent / "finance.db"


def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receitas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL
        )
    """)

    # ==========================================
    # DESPESAS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL
        )
    """)

    # ==========================================
    # CARTÕES
    #==========================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cartoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        banco TEXT NOT NULL,
        bandeira TEXT NOT NULL,
        limite REAL NOT NULL,
        fechamento INTEGER NOT NULL,
        vencimento INTEGER NOT NULL,
        cor TEXT DEFAULT '#6D28D9'
    )
""")

    conn.commit()
    conn.close()


# ==========================================
# RECEITAS
# ==========================================

def adicionar_receita(data, categoria, descricao, valor):
    """
    Adiciona uma nova receita.
    """
    conn = conectar()

    conn.execute("""
        INSERT INTO receitas
        (data, categoria, descricao, valor)
        VALUES (?, ?, ?, ?)
    """, (
        data,
        categoria,
        descricao,
        valor
    ))

    conn.commit()
    conn.close()


def listar_receitas():
    """
    Retorna todas as receitas.
    """
    conn = conectar()

    dados = conn.execute("""
        SELECT *
        FROM receitas
        ORDER BY data DESC
    """).fetchall()

    conn.close()

    return dados

def obter_receita(id_receita):
    """
    Retorna uma receita pelo ID.
    """
    conn = conectar()

    receita = conn.execute("""
        SELECT *
        FROM receitas
        WHERE id = ?
    """, (id_receita,)).fetchone()

    conn.close()

    return receita

def editar_receita(id_receita, data, categoria, descricao, valor):
    """
    Atualiza uma receita existente.
    """
    conn = conectar()

    conn.execute("""
        UPDATE receitas
        SET
            data = ?,
            categoria = ?,
            descricao = ?,
            valor = ?
        WHERE id = ?
    """, (
        data,
        categoria,
        descricao,
        valor,
        id_receita
    ))

    conn.commit()
    conn.close()


def excluir_receita(id_receita):
    """
    Exclui uma receita.
    """
    conn = conectar()

    conn.execute("""
        DELETE FROM receitas
        WHERE id = ?
    """, (
        id_receita,
    ))

    conn.commit()
    conn.close()

# ==========================================
# KPIs
# ==========================================

def total_receitas():
    """
    Retorna o valor total das receitas.
    """
    conn = conectar()

    total = conn.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM receitas
    """).fetchone()[0]

    conn.close()

    return total


def quantidade_receitas():
    """
    Retorna a quantidade de receitas cadastradas.
    """
    conn = conectar()

    quantidade = conn.execute("""
        SELECT COUNT(*)
        FROM receitas
    """).fetchone()[0]

    conn.close()

    return quantidade


# ==========================================
# DESPESAS
# ==========================================

def adicionar_despesa(data, categoria, descricao, valor):
    """
    Adiciona uma nova despesa.
    """
    conn = conectar()

    conn.execute("""
        INSERT INTO despesas
        (data, categoria, descricao, valor)
        VALUES (?, ?, ?, ?)
    """, (
        data,
        categoria,
        descricao,
        valor
    ))

    conn.commit()
    conn.close()


def listar_despesas():
    """
    Retorna todas as despesas.
    """
    conn = conectar()

    dados = conn.execute("""
        SELECT *
        FROM despesas
        ORDER BY data DESC
    """).fetchall()

    conn.close()

    return dados


def obter_despesa(id_despesa):
    """
    Retorna uma despesa pelo ID.
    """
    conn = conectar()

    despesa = conn.execute("""
        SELECT *
        FROM despesas
        WHERE id = ?
    """, (
        id_despesa,
    )).fetchone()

    conn.close()

    return despesa


def editar_despesa(id_despesa, data, categoria, descricao, valor):
    """
    Atualiza uma despesa.
    """
    conn = conectar()

    conn.execute("""
        UPDATE despesas
        SET
            data = ?,
            categoria = ?,
            descricao = ?,
            valor = ?
        WHERE id = ?
    """, (
        data,
        categoria,
        descricao,
        valor,
        id_despesa
    ))

    conn.commit()
    conn.close()


def excluir_despesa(id_despesa):
    """
    Remove uma despesa.
    """
    conn = conectar()

    conn.execute("""
        DELETE FROM despesas
        WHERE id = ?
    """, (
        id_despesa,
    ))

    conn.commit()
    conn.close()


def total_despesas():
    """
    Retorna o valor total das despesas.
    """
    conn = conectar()

    total = conn.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM despesas
    """).fetchone()[0]

    conn.close()

    return total


def quantidade_despesas():
    """
    Retorna a quantidade de despesas.
    """
    conn = conectar()

    quantidade = conn.execute("""
        SELECT COUNT(*)
        FROM despesas
    """).fetchone()[0]

    conn.close()

    return quantidade

if __name__ == "__main__":
    criar_banco()
    print("Banco atualizado!")

# ==========================================
# CARTÕES
# ==========================================

def adicionar_cartao(
    nome,
    banco,
    bandeira,
    limite,
    fechamento,
    vencimento,
    cor
):

    conn = conectar()

    conn.execute("""
        INSERT INTO cartoes
        (
            nome,
            banco,
            bandeira,
            limite,
            fechamento,
            vencimento,
            cor
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        nome,
        banco,
        bandeira,
        limite,
        fechamento,
        vencimento,
        cor
    ))

    conn.commit()
    conn.close()


def listar_cartoes():

    conn = conectar()

    dados = conn.execute("""
        SELECT *
        FROM cartoes
        ORDER BY nome
    """).fetchall()

    conn.close()

    return dados


def obter_cartao(id_cartao):

    conn = conectar()

    cartao = conn.execute("""
        SELECT *
        FROM cartoes
        WHERE id = ?
    """, (id_cartao,)).fetchone()

    conn.close()

    return cartao


def editar_cartao(
    id_cartao,
    nome,
    banco,
    bandeira,
    limite,
    fechamento,
    vencimento,
    cor
):

    conn = conectar()

    conn.execute("""
        UPDATE cartoes
        SET
            nome=?,
            banco=?,
            bandeira=?,
            limite=?,
            fechamento=?,
            vencimento=?,
            cor=?
        WHERE id=?
    """, (
        nome,
        banco,
        bandeira,
        limite,
        fechamento,
        vencimento,
        cor,
        id_cartao
    ))

    conn.commit()
    conn.close()


def excluir_cartao(id_cartao):

    conn = conectar()

    conn.execute("""
        DELETE FROM cartoes
        WHERE id=?
    """, (id_cartao,))

    conn.commit()
    conn.close()


def quantidade_cartoes():

    conn = conectar()

    total = conn.execute("""
        SELECT COUNT(*)
        FROM cartoes
    """).fetchone()[0]

    conn.close()

    return total


def limite_total():

    conn = conectar()

    total = conn.execute("""
        SELECT COALESCE(SUM(limite),0)
        FROM cartoes
    """).fetchone()[0]

    conn.close()

    return total

