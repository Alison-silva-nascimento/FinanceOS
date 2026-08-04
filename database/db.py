import sqlite3
import calendar
from datetime import date
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

    # Usuários autenticados. Senhas são armazenadas apenas como hash.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Atualiza instalações antigas que possuíam a tabela de usuários sem hash.
    colunas_usuarios = {
        linha["name"] for linha in cursor.execute("PRAGMA table_info(usuarios)")
    }
    if "senha_hash" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN senha_hash TEXT")

    # BANCOS

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bancos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT NOT NULL,

        banco TEXT NOT NULL,

        tipo TEXT NOT NULL,

        saldo REAL NOT NULL,

        cor TEXT DEFAULT '#2563EB'

)
""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS orcamentos(
        id INTEGER PRIMARY KEY, categoria TEXT NOT NULL, mes TEXT NOT NULL,
        limite REAL NOT NULL, UNIQUE(categoria, mes))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS metas(
        id INTEGER PRIMARY KEY, nome TEXT NOT NULL, valor_alvo REAL NOT NULL,
        valor_atual REAL NOT NULL DEFAULT 0, prazo TEXT, cor TEXT DEFAULT '#3B82F6')""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS patrimonio(
        id INTEGER PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL,
        categoria TEXT, valor REAL NOT NULL, atualizado_em TEXT NOT NULL)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS recorrencias(
        id INTEGER PRIMARY KEY, tipo TEXT NOT NULL, categoria TEXT NOT NULL,
        descricao TEXT, valor REAL NOT NULL, dia INTEGER NOT NULL,
        ativa INTEGER NOT NULL DEFAULT 1, ultimo_mes TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS compras_cartao(
        id INTEGER PRIMARY KEY, cartao_id INTEGER NOT NULL, data TEXT NOT NULL,
        descricao TEXT NOT NULL, categoria TEXT NOT NULL, valor REAL NOT NULL,
        parcelas INTEGER NOT NULL DEFAULT 1, parcela_atual INTEGER NOT NULL DEFAULT 1,
        paga INTEGER NOT NULL DEFAULT 0)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS transferencias(
        id INTEGER PRIMARY KEY, data TEXT NOT NULL, origem_id INTEGER NOT NULL,
        destino_id INTEGER NOT NULL, valor REAL NOT NULL, descricao TEXT)""")
    

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

# ==========================================
# BANCOS
# ==========================================

def adicionar_banco(nome, banco, tipo, saldo, cor):

    conn = conectar()

    conn.execute("""
        INSERT INTO bancos
        (
            nome,
            banco,
            tipo,
            saldo,
            cor
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        nome,
        banco,
        tipo,
        saldo,
        cor
    ))

    conn.commit()
    conn.close()


def listar_bancos():

    conn = conectar()

    dados = conn.execute("""
        SELECT *
        FROM bancos
        ORDER BY nome
    """).fetchall()

    conn.close()

    return dados


def obter_banco(id_banco):

    conn = conectar()

    banco = conn.execute("""
        SELECT *
        FROM bancos
        WHERE id=?
    """, (id_banco,)).fetchone()

    conn.close()

    return banco


def editar_banco(
    id_banco,
    nome,
    banco,
    tipo,
    saldo,
    cor
):

    conn = conectar()

    conn.execute("""
        UPDATE bancos
        SET
            nome=?,
            banco=?,
            tipo=?,
            saldo=?,
            cor=?
        WHERE id=?
    """, (
        nome,
        banco,
        tipo,
        saldo,
        cor,
        id_banco
    ))

    conn.commit()
    conn.close()


def excluir_banco(id_banco):

    conn = conectar()

    conn.execute("""
        DELETE FROM bancos
        WHERE id=?
    """, (id_banco,))

    conn.commit()
    conn.close()


def quantidade_bancos():

    conn = conectar()

    total = conn.execute("""
        SELECT COUNT(*)
        FROM bancos
    """).fetchone()[0]

    conn.close()

    return total


def saldo_total_bancos():

    conn = conectar()

    total = conn.execute("""
        SELECT COALESCE(SUM(saldo),0)
        FROM bancos
    """).fetchone()[0]

    conn.close()

    return total


# Garante que uma instalação nova tenha as tabelas necessárias antes de
# qualquer página consultar ou gravar dados.
criar_banco()


if __name__ == "__main__":
    print("Banco atualizado!")


def listar_despesas_mes(mes):
    return [d for d in listar_despesas() if str(d["data"]).startswith(mes)]


def salvar_orcamento(categoria, mes, limite):
    conn = conectar(); conn.execute("INSERT INTO orcamentos(categoria,mes,limite) VALUES(?,?,?) ON CONFLICT(categoria,mes) DO UPDATE SET limite=excluded.limite", (categoria, mes, limite)); conn.commit(); conn.close()


def listar_orcamentos(mes):
    conn = conectar(); dados = conn.execute("SELECT * FROM orcamentos WHERE mes=? ORDER BY categoria", (mes,)).fetchall(); conn.close(); return dados


def adicionar_meta(nome, valor_alvo, prazo, cor):
    conn = conectar(); conn.execute("INSERT INTO metas(nome,valor_alvo,prazo,cor) VALUES(?,?,?,?)", (nome, valor_alvo, prazo, cor)); conn.commit(); conn.close()


def listar_metas():
    conn = conectar(); dados = conn.execute("SELECT * FROM metas ORDER BY prazo", ()).fetchall(); conn.close(); return dados


def aportar_meta(id_meta, valor):
    conn = conectar(); conn.execute("UPDATE metas SET valor_atual=valor_atual+? WHERE id=?", (valor, id_meta)); conn.commit(); conn.close()


def adicionar_patrimonio(nome, tipo, categoria, valor, data):
    conn = conectar(); conn.execute("INSERT INTO patrimonio(nome,tipo,categoria,valor,atualizado_em) VALUES(?,?,?,?,?)", (nome, tipo, categoria, valor, data)); conn.commit(); conn.close()


def listar_patrimonio():
    conn = conectar(); dados = conn.execute("SELECT * FROM patrimonio ORDER BY tipo,nome").fetchall(); conn.close(); return dados


def adicionar_recorrencia(tipo, categoria, descricao, valor, dia):
    conn = conectar(); conn.execute("INSERT INTO recorrencias(tipo,categoria,descricao,valor,dia) VALUES(?,?,?,?,?)", (tipo,categoria,descricao,valor,dia)); conn.commit(); conn.close()


def listar_recorrencias():
    conn = conectar(); dados = conn.execute("SELECT * FROM recorrencias WHERE ativa=1 ORDER BY dia").fetchall(); conn.close(); return dados


def proximos_vencimentos(limite=5):
    """Calcula a próxima ocorrência real de cada despesa recorrente."""
    hoje = date.today()
    vencimentos = []
    for item in listar_recorrencias():
        if item["tipo"] != "Despesa":
            continue
        ano, mes = hoje.year, hoje.month
        dia = min(int(item["dia"]), calendar.monthrange(ano, mes)[1])
        vencimento = date(ano, mes, dia)
        if vencimento < hoje:
            ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
            dia = min(int(item["dia"]), calendar.monthrange(ano, mes)[1])
            vencimento = date(ano, mes, dia)
        vencimentos.append({"data": vencimento, "descricao": item["descricao"], "categoria": item["categoria"], "valor": item["valor"]})
    return sorted(vencimentos, key=lambda item: item["data"])[:limite]


def gerar_recorrencias(mes):
    conn = conectar(); itens = conn.execute("SELECT * FROM recorrencias WHERE ativa=1 AND (ultimo_mes IS NULL OR ultimo_mes != ?)", (mes,)).fetchall()
    for item in itens:
        ano, numero_mes = map(int, mes.split("-"))
        dia_real = min(int(item["dia"]), calendar.monthrange(ano, numero_mes)[1])
        data = f"{mes}-{dia_real:02d}"
        tabela = "receitas" if item["tipo"] == "Receita" else "despesas"
        conn.execute(f"INSERT INTO {tabela}(data,categoria,descricao,valor) VALUES(?,?,?,?)", (data,item["categoria"],item["descricao"],item["valor"]))
        conn.execute("UPDATE recorrencias SET ultimo_mes=? WHERE id=?", (mes,item["id"]))
    conn.commit(); conn.close(); return len(itens)


def transferir(data, origem_id, destino_id, valor, descricao):
    conn = conectar()
    try:
        conn.execute("UPDATE bancos SET saldo=saldo-? WHERE id=?", (valor, origem_id)); conn.execute("UPDATE bancos SET saldo=saldo+? WHERE id=?", (valor, destino_id)); conn.execute("INSERT INTO transferencias(data,origem_id,destino_id,valor,descricao) VALUES(?,?,?,?,?)", (data,origem_id,destino_id,valor,descricao)); conn.commit()
    finally: conn.close()


def adicionar_compra_cartao(cartao_id, data, descricao, categoria, valor, parcelas):
    conn = conectar(); conn.execute("INSERT INTO compras_cartao(cartao_id,data,descricao,categoria,valor,parcelas) VALUES(?,?,?,?,?,?)", (cartao_id,data,descricao,categoria,valor,parcelas)); conn.commit(); conn.close()


def listar_compras_cartao(cartao_id):
    conn = conectar(); dados = conn.execute("SELECT * FROM compras_cartao WHERE cartao_id=? ORDER BY data DESC", (cartao_id,)).fetchall(); conn.close(); return dados


def fatura_cartao(cartao_id):
    conn = conectar(); total = conn.execute("SELECT COALESCE(SUM(valor/parcelas),0) FROM compras_cartao WHERE cartao_id=? AND paga=0", (cartao_id,)).fetchone()[0]; conn.close(); return total
