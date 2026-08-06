"""Persistência local do FinanceOS.

Todos os registros financeiros pertencem ao usuário autenticado. Instalações
anteriores são migradas automaticamente para o primeiro usuário criado.

Este módulo contém também o histórico resumido de holerites.
"""

import calendar
import os
import sqlite3
import subprocess
from datetime import date, datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / "finance.db"
BACKUP_DIR = DB_FILE.parent.parent / "backups"

TABELAS_FINANCEIRAS = (
    "receitas", "despesas", "cartoes", "bancos", "orcamentos", "metas",
    "patrimonio", "recorrencias", "compras_cartao", "transferencias", "holerites", "conciliacoes", "faturas_pagas",
)


def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_backup_diario():
    """Cria uma cópia consistente do SQLite por dia, sem sobrescrever backups."""
    if not DB_FILE.exists():
        return None
    BACKUP_DIR.mkdir(exist_ok=True)
    destino = BACKUP_DIR / f"finance-{date.today():%Y-%m-%d}.db"
    if destino.exists():
        return destino
    origem = sqlite3.connect(DB_FILE)
    copia = sqlite3.connect(destino)
    try:
        origem.backup(copia)
    finally:
        copia.close(); origem.close()
    return destino


def proteger_dados_windows():
    """Restringe banco e backups ao usuário atual e ao sistema no Windows.

    Não substitui criptografia de ponta a ponta, mas impede que outros perfis locais
    acessem os arquivos pelo Explorador sem permissão administrativa.
    """
    if os.name != "nt" or not DB_FILE.exists():
        return False
    BACKUP_DIR.mkdir(exist_ok=True)
    marcador = BACKUP_DIR / ".acl_protegida"
    if marcador.exists():
        return True
    usuario = subprocess.check_output(["whoami"], text=True).strip()
    comandos = (
        ["icacls", str(DB_FILE), "/inheritance:r", "/grant:r", f"{usuario}:(F)", "SYSTEM:(F)"],
        ["icacls", str(BACKUP_DIR), "/inheritance:r", "/grant:r", f"{usuario}:(OI)(CI)(F)", "SYSTEM:(OI)(CI)(F)"],
    )
    try:
        for comando in comandos:
            subprocess.run(comando, check=True, capture_output=True, text=True)
        marcador.write_text("Proteção de acesso aplicada pelo FinanceOS.\n", encoding="utf-8")
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def registrar_evento(usuario_id, acao, detalhes=None):
    conn = conectar()
    conn.execute("INSERT INTO eventos_seguranca(usuario_id,acao,detalhes) VALUES(?,?,?)", (usuario_id, acao, detalhes))
    conn.commit(); conn.close()


def listar_eventos_seguranca(limite=20):
    usuario_id = _usuario_atual(); conn = conectar()
    dados = conn.execute("SELECT * FROM eventos_seguranca WHERE usuario_id=? ORDER BY criado_em DESC, id DESC LIMIT ?", (usuario_id, limite)).fetchall()
    conn.close(); return dados


def _exigir_admin():
    """Protege consultas administrativas inclusive quando uma URL é aberta diretamente."""
    try:
        import streamlit as st
        usuario = str(st.session_state.get("usuario", "")).strip().lower()
    except Exception:
        usuario = ""
    if usuario != "alison.nascimento":
        raise PermissionError("Acesso administrativo não autorizado.")


def listar_usuarios_admin():
    """Resumo de contas, sem expor hashes, fotos ou dados financeiros."""
    _exigir_admin()
    conn = conectar()
    dados = conn.execute("""
        SELECT u.id, u.nome, u.usuario, u.perfil, u.criado_em, u.ultimo_login,
               u.bloqueado_ate, COUNT(e.id) AS eventos_registrados
        FROM usuarios u
        LEFT JOIN eventos_seguranca e ON e.usuario_id = u.id
        GROUP BY u.id
        ORDER BY u.criado_em DESC, u.id DESC
    """).fetchall()
    conn.close()
    return dados


def listar_eventos_admin(usuario_id=None, limite=200):
    """Histórico administrativo de atividades, opcionalmente filtrado por usuário."""
    _exigir_admin()
    conn = conectar()
    if usuario_id:
        dados = conn.execute("""
            SELECT e.id, u.nome, u.usuario, e.acao, e.detalhes, e.criado_em
            FROM eventos_seguranca e JOIN usuarios u ON u.id=e.usuario_id
            WHERE e.usuario_id=? ORDER BY e.criado_em DESC, e.id DESC LIMIT ?
        """, (usuario_id, limite)).fetchall()
    else:
        dados = conn.execute("""
            SELECT e.id, u.nome, u.usuario, e.acao, e.detalhes, e.criado_em
            FROM eventos_seguranca e JOIN usuarios u ON u.id=e.usuario_id
            ORDER BY e.criado_em DESC, e.id DESC LIMIT ?
        """, (limite,)).fetchall()
    conn.close()
    return dados


def _usuario_atual():
    """Obtém o id do usuário apenas durante uma sessão autenticada."""
    try:
        import streamlit as st
        usuario_id = st.session_state.get("usuario_id")
    except Exception:
        usuario_id = None
    if not usuario_id:
        raise RuntimeError("É necessário estar autenticado para acessar os dados.")
    return int(usuario_id)


def criar_banco():
    criar_backup_diario()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL,
        usuario TEXT NOT NULL UNIQUE, senha_hash TEXT NOT NULL,
        perfil TEXT NOT NULL DEFAULT 'usuario',
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    colunas_usuarios = {linha["name"] for linha in cursor.execute("PRAGMA table_info(usuarios)")}
    if "senha_hash" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN senha_hash TEXT")
    if "perfil" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN perfil TEXT NOT NULL DEFAULT 'usuario'")
    if "criado_em" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN criado_em TEXT")
    if "foto_perfil" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN foto_perfil BLOB")
    if "tentativas_login" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN tentativas_login INTEGER NOT NULL DEFAULT 0")
    if "bloqueado_ate" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN bloqueado_ate TEXT")
    if "ultimo_login" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN ultimo_login TEXT")
    if "sessao_versao" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN sessao_versao INTEGER NOT NULL DEFAULT 1")
    # Regra de administração do FinanceOS: a conta do proprietário é a única admin.
    cursor.execute("UPDATE usuarios SET perfil='usuario' WHERE lower(usuario) != 'alison.nascimento' AND perfil='admin'")
    cursor.execute("UPDATE usuarios SET perfil='admin' WHERE lower(usuario) = 'alison.nascimento'")
    cursor.execute("""CREATE TABLE IF NOT EXISTS eventos_seguranca(
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, acao TEXT NOT NULL,
        detalhes TEXT, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS receitas(
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL, categoria TEXT NOT NULL,
        descricao TEXT, valor REAL NOT NULL, usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS despesas(
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL, categoria TEXT NOT NULL,
        descricao TEXT, valor REAL NOT NULL, usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS cartoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, banco TEXT NOT NULL,
        bandeira TEXT NOT NULL, limite REAL NOT NULL, fechamento INTEGER NOT NULL,
        vencimento INTEGER NOT NULL, cor TEXT DEFAULT '#6D28D9', usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS bancos(
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, banco TEXT NOT NULL,
        tipo TEXT NOT NULL, saldo REAL NOT NULL, cor TEXT DEFAULT '#2563EB', usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS orcamentos(
        id INTEGER PRIMARY KEY AUTOINCREMENT, categoria TEXT NOT NULL, mes TEXT NOT NULL,
        limite REAL NOT NULL, usuario_id INTEGER, UNIQUE(categoria, mes, usuario_id))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS metas(
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, valor_alvo REAL NOT NULL,
        valor_atual REAL NOT NULL DEFAULT 0, prazo TEXT, cor TEXT DEFAULT '#3B82F6', usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS patrimonio(
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, tipo TEXT NOT NULL,
        categoria TEXT, valor REAL NOT NULL, atualizado_em TEXT NOT NULL, usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS recorrencias(
        id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL, categoria TEXT NOT NULL,
        descricao TEXT, valor REAL NOT NULL, dia INTEGER NOT NULL, ativa INTEGER NOT NULL DEFAULT 1,
        ultimo_mes TEXT, usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS compras_cartao(
        id INTEGER PRIMARY KEY AUTOINCREMENT, cartao_id INTEGER NOT NULL, data TEXT NOT NULL,
        descricao TEXT NOT NULL, categoria TEXT NOT NULL, valor REAL NOT NULL,
        parcelas INTEGER NOT NULL DEFAULT 1, parcela_atual INTEGER NOT NULL DEFAULT 1,
        paga INTEGER NOT NULL DEFAULT 0, competencia TEXT, usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS transferencias(
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL, origem_id INTEGER NOT NULL,
        destino_id INTEGER NOT NULL, valor REAL NOT NULL, descricao TEXT, usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS holerites(
        id INTEGER PRIMARY KEY AUTOINCREMENT, competencia TEXT NOT NULL,
        salario_bruto REAL NOT NULL DEFAULT 0, inss REAL NOT NULL DEFAULT 0,
        irrf REAL NOT NULL DEFAULT 0, consignado REAL NOT NULL DEFAULT 0,
        pat REAL NOT NULL DEFAULT 0, unimed REAL NOT NULL DEFAULT 0,
        fgts REAL NOT NULL DEFAULT 0, outros_descontos REAL NOT NULL DEFAULT 0,
        salario_liquido REAL NOT NULL DEFAULT 0,
        arquivo_nome TEXT, usuario_id INTEGER, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(competencia, usuario_id))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS conciliacoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL, descricao TEXT NOT NULL,
        valor REAL NOT NULL, tipo TEXT NOT NULL, conciliado INTEGER NOT NULL DEFAULT 0,
        origem TEXT, usuario_id INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS faturas_pagas(
        id INTEGER PRIMARY KEY AUTOINCREMENT, cartao_id INTEGER NOT NULL, competencia TEXT NOT NULL,
        banco_id INTEGER, valor REAL NOT NULL, pago_em TEXT NOT NULL, usuario_id INTEGER,
        UNIQUE(cartao_id, competencia, usuario_id))""")

    colunas_holerites = {linha["name"] for linha in cursor.execute("PRAGMA table_info(holerites)")}
    for coluna in ("pat", "unimed", "fgts"):
        if coluna not in colunas_holerites:
            cursor.execute(f"ALTER TABLE holerites ADD COLUMN {coluna} REAL NOT NULL DEFAULT 0")

    # Migração não destrutiva de bancos criados antes do isolamento por usuário.
    for tabela in TABELAS_FINANCEIRAS:
        colunas = {linha["name"] for linha in cursor.execute(f"PRAGMA table_info({tabela})")}
        if "usuario_id" not in colunas:
            cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN usuario_id INTEGER")
    primeiro_usuario = cursor.execute("SELECT id FROM usuarios ORDER BY id LIMIT 1").fetchone()
    if primeiro_usuario:
        for tabela in TABELAS_FINANCEIRAS:
            cursor.execute(f"UPDATE {tabela} SET usuario_id=? WHERE usuario_id IS NULL", (primeiro_usuario["id"],))
    colunas_compras = {linha["name"] for linha in cursor.execute("PRAGMA table_info(compras_cartao)")}
    if "competencia" not in colunas_compras:
        cursor.execute("ALTER TABLE compras_cartao ADD COLUMN competencia TEXT")
    cursor.execute("UPDATE compras_cartao SET competencia=substr(data, 1, 7) WHERE competencia IS NULL OR competencia='' ")
    conn.commit()
    conn.close()
    proteger_dados_windows()


def _listar(tabela, ordem="id DESC"):
    usuario_id = _usuario_atual()
    conn = conectar()
    dados = conn.execute(f"SELECT * FROM {tabela} WHERE usuario_id=? ORDER BY {ordem}", (usuario_id,)).fetchall()
    conn.close()
    return dados


def _obter(tabela, registro_id):
    usuario_id = _usuario_atual()
    conn = conectar()
    dado = conn.execute(f"SELECT * FROM {tabela} WHERE id=? AND usuario_id=?", (registro_id, usuario_id)).fetchone()
    conn.close()
    return dado


def _excluir(tabela, registro_id):
    usuario_id = _usuario_atual()
    conn = conectar()
    conn.execute(f"DELETE FROM {tabela} WHERE id=? AND usuario_id=?", (registro_id, usuario_id))
    conn.commit(); conn.close()


# Receitas e despesas
def adicionar_receita(data, categoria, descricao, valor):
    _adicionar_lancamento("receitas", data, categoria, descricao, valor)


def adicionar_despesa(data, categoria, descricao, valor):
    _adicionar_lancamento("despesas", data, categoria, descricao, valor)


def _adicionar_lancamento(tabela, data, categoria, descricao, valor):
    usuario_id = _usuario_atual(); conn = conectar()
    conn.execute(f"INSERT INTO {tabela}(data,categoria,descricao,valor,usuario_id) VALUES(?,?,?,?,?)", (data, categoria, descricao, valor, usuario_id))
    conn.commit(); conn.close()


def listar_receitas(): return _listar("receitas", "data DESC, id DESC")
def listar_despesas(): return _listar("despesas", "data DESC, id DESC")
def obter_receita(registro_id): return _obter("receitas", registro_id)
def obter_despesa(registro_id): return _obter("despesas", registro_id)
def excluir_receita(registro_id): _excluir("receitas", registro_id)
def excluir_despesa(registro_id): _excluir("despesas", registro_id)


def _editar_lancamento(tabela, registro_id, data, categoria, descricao, valor):
    usuario_id = _usuario_atual(); conn = conectar()
    conn.execute(f"UPDATE {tabela} SET data=?, categoria=?, descricao=?, valor=? WHERE id=? AND usuario_id=?", (data, categoria, descricao, valor, registro_id, usuario_id))
    conn.commit(); conn.close()


def editar_receita(registro_id, data, categoria, descricao, valor): _editar_lancamento("receitas", registro_id, data, categoria, descricao, valor)
def editar_despesa(registro_id, data, categoria, descricao, valor): _editar_lancamento("despesas", registro_id, data, categoria, descricao, valor)
def total_receitas(): return sum(item["valor"] for item in listar_receitas())
def total_despesas(): return sum(item["valor"] for item in listar_despesas())
def quantidade_receitas(): return len(listar_receitas())
def quantidade_despesas(): return len(listar_despesas())
def listar_despesas_mes(mes): return [item for item in listar_despesas() if str(item["data"]).startswith(mes)]


# Cartões
def adicionar_cartao(nome, banco, bandeira, limite, fechamento, vencimento, cor):
    usuario_id = _usuario_atual(); conn = conectar()
    conn.execute("INSERT INTO cartoes(nome,banco,bandeira,limite,fechamento,vencimento,cor,usuario_id) VALUES(?,?,?,?,?,?,?,?)", (nome,banco,bandeira,limite,fechamento,vencimento,cor,usuario_id))
    conn.commit(); conn.close()


def listar_cartoes(): return _listar("cartoes", "nome")
def obter_cartao(registro_id): return _obter("cartoes", registro_id)
def quantidade_cartoes(): return len(listar_cartoes())
def limite_total(): return sum(item["limite"] for item in listar_cartoes())


def editar_cartao(registro_id, nome, banco, bandeira, limite, fechamento, vencimento, cor):
    usuario_id = _usuario_atual(); conn = conectar()
    conn.execute("UPDATE cartoes SET nome=?, banco=?, bandeira=?, limite=?, fechamento=?, vencimento=?, cor=? WHERE id=? AND usuario_id=?", (nome,banco,bandeira,limite,fechamento,vencimento,cor,registro_id,usuario_id))
    conn.commit(); conn.close()


def excluir_cartao(registro_id):
    usuario_id = _usuario_atual(); conn = conectar()
    conn.execute("DELETE FROM compras_cartao WHERE cartao_id=? AND usuario_id=?", (registro_id, usuario_id))
    conn.execute("DELETE FROM cartoes WHERE id=? AND usuario_id=?", (registro_id, usuario_id))
    conn.commit(); conn.close()


def adicionar_compra_cartao(cartao_id, data, descricao, categoria, valor, parcelas, parcela_atual=1, competencia=None):
    usuario_id = _usuario_atual()
    if not _obter("cartoes", cartao_id): raise ValueError("Cartão inválido.")
    competencia = competencia or str(data)[:7]
    conn = conectar(); conn.execute("INSERT INTO compras_cartao(cartao_id,data,descricao,categoria,valor,parcelas,parcela_atual,competencia,usuario_id) VALUES(?,?,?,?,?,?,?,?,?)", (cartao_id,data,descricao,categoria,valor,parcelas,parcela_atual,competencia,usuario_id)); conn.commit(); conn.close()


def listar_compras_cartao(cartao_id):
    usuario_id = _usuario_atual(); conn = conectar(); dados = conn.execute("SELECT * FROM compras_cartao WHERE cartao_id=? AND usuario_id=? ORDER BY data DESC", (cartao_id,usuario_id)).fetchall(); conn.close(); return dados
def fatura_cartao(cartao_id): return sum(item["valor"] / item["parcelas"] for item in listar_compras_cartao(cartao_id) if not item["paga"])

def editar_categoria_compra(registro_id, categoria):
    usuario_id = _usuario_atual(); conn = conectar(); conn.execute("UPDATE compras_cartao SET categoria=? WHERE id=? AND usuario_id=?", (categoria,registro_id,usuario_id)); conn.commit(); conn.close()

def migrar_compras_cartao(cartao_origem_id, cartao_destino_id, competencia):
    """Move uma fatura para outro cartão, sempre dentro do mesmo usuário."""
    usuario_id = _usuario_atual()
    if cartao_origem_id == cartao_destino_id:
        raise ValueError("Escolha cartões diferentes para migrar a fatura.")
    conn = conectar()
    destino = conn.execute("SELECT id FROM cartoes WHERE id=? AND usuario_id=?", (cartao_destino_id, usuario_id)).fetchone()
    if not destino:
        conn.close(); raise ValueError("Cartão de destino inválido.")
    cursor = conn.execute("UPDATE compras_cartao SET cartao_id=? WHERE cartao_id=? AND competencia=? AND usuario_id=?", (cartao_destino_id, cartao_origem_id, competencia, usuario_id))
    conn.commit(); conn.close()
    return cursor.rowcount


def listar_duplicatas_compra_cartao(cartao_id, competencia):
    """Identifica repetições exatas de uma compra dentro da mesma fatura."""
    usuario_id = _usuario_atual(); conn = conectar()
    dados = conn.execute("""
        SELECT data, descricao, valor, parcelas, parcela_atual,
               COUNT(*) AS quantidade, GROUP_CONCAT(id) AS ids
        FROM compras_cartao
        WHERE cartao_id=? AND competencia=? AND usuario_id=?
        GROUP BY data, descricao, valor, parcelas, parcela_atual
        HAVING COUNT(*) > 1
        ORDER BY data DESC, descricao
    """, (cartao_id, competencia, usuario_id)).fetchall()
    conn.close(); return dados


def remover_duplicatas_compra_cartao(cartao_id, competencia):
    """Mantém o registro mais antigo de cada compra exatamente duplicada."""
    usuario_id = _usuario_atual(); conn = conectar()
    grupos = conn.execute("""
        SELECT MIN(id) AS manter_id, GROUP_CONCAT(id) AS ids
        FROM compras_cartao
        WHERE cartao_id=? AND competencia=? AND usuario_id=?
        GROUP BY data, descricao, valor, parcelas, parcela_atual
        HAVING COUNT(*) > 1
    """, (cartao_id, competencia, usuario_id)).fetchall()
    removidas = 0
    for grupo in grupos:
        ids = [int(valor) for valor in grupo["ids"].split(",") if int(valor) != grupo["manter_id"]]
        if ids:
            marcadores = ",".join("?" for _ in ids)
            cursor = conn.execute(f"DELETE FROM compras_cartao WHERE id IN ({marcadores}) AND usuario_id=?", (*ids, usuario_id))
            removidas += cursor.rowcount
    conn.commit(); conn.close()
    return removidas


def remover_faturas_cartao(cartao_id, competencia=None):
    """Remove somente compras ainda não pagas de uma ou todas as faturas do cartão."""
    usuario_id = _usuario_atual(); conn = conectar()
    if not conn.execute("SELECT id FROM cartoes WHERE id=? AND usuario_id=?", (cartao_id, usuario_id)).fetchone():
        conn.close(); raise ValueError("Cartão inválido.")
    sql = "DELETE FROM compras_cartao WHERE cartao_id=? AND usuario_id=? AND paga=0"
    parametros = [cartao_id, usuario_id]
    if competencia:
        sql += " AND competencia=?"; parametros.append(competencia)
    cursor = conn.execute(sql, parametros)
    conn.commit(); conn.close()
    return cursor.rowcount

def gastos_cartao_categoria(mes=None):
    usuario_id = _usuario_atual(); conn = conectar()
    sql = "SELECT categoria, COALESCE(SUM(valor/parcelas),0) valor FROM compras_cartao WHERE usuario_id=? AND paga=0"
    parametros = [usuario_id]
    if mes:
        sql += " AND competencia=?"; parametros.append(mes)
    dados = conn.execute(sql + " GROUP BY categoria ORDER BY valor DESC", parametros).fetchall()
    conn.close(); return dados

def fatura_cartao_mes(cartao_id, mes):
    return sum(item["valor"] / item["parcelas"] for item in listar_compras_cartao(cartao_id) if item["competencia"] == mes and not item["paga"])

def pagar_fatura(cartao_id, mes, banco_id, valor, pago_em):
    usuario_id = _usuario_atual(); conn = conectar()
    banco = conn.execute("SELECT saldo FROM bancos WHERE id=? AND usuario_id=?", (banco_id, usuario_id)).fetchone()
    if not banco or valor <= 0 or banco["saldo"] < valor: conn.close(); raise ValueError("Conta inválida ou saldo insuficiente.")
    conn.execute("UPDATE bancos SET saldo=saldo-? WHERE id=? AND usuario_id=?", (valor, banco_id, usuario_id))
    conn.execute("INSERT INTO faturas_pagas(cartao_id,competencia,banco_id,valor,pago_em,usuario_id) VALUES(?,?,?,?,?,?) ON CONFLICT(cartao_id,competencia,usuario_id) DO UPDATE SET banco_id=excluded.banco_id,valor=excluded.valor,pago_em=excluded.pago_em", (cartao_id,mes,banco_id,valor,pago_em,usuario_id))
    conn.execute("UPDATE compras_cartao SET paga=1 WHERE cartao_id=? AND usuario_id=? AND data LIKE ?", (cartao_id,usuario_id,f"{mes}%"))
    conn.commit(); conn.close()


# Contas e transferências
def adicionar_banco(nome, banco, tipo, saldo, cor):
    usuario_id = _usuario_atual(); conn = conectar(); conn.execute("INSERT INTO bancos(nome,banco,tipo,saldo,cor,usuario_id) VALUES(?,?,?,?,?,?)", (nome,banco,tipo,saldo,cor,usuario_id)); conn.commit(); conn.close()
def listar_bancos(): return _listar("bancos", "nome")
def obter_banco(registro_id): return _obter("bancos", registro_id)
def quantidade_bancos(): return len(listar_bancos())
def saldo_total_bancos(): return sum(item["saldo"] for item in listar_bancos())


def editar_banco(registro_id, nome, banco, tipo, saldo, cor):
    usuario_id = _usuario_atual(); conn = conectar(); conn.execute("UPDATE bancos SET nome=?, banco=?, tipo=?, saldo=?, cor=? WHERE id=? AND usuario_id=?", (nome,banco,tipo,saldo,cor,registro_id,usuario_id)); conn.commit(); conn.close()
def excluir_banco(registro_id): _excluir("bancos", registro_id)


def transferir(data, origem_id, destino_id, valor, descricao):
    usuario_id = _usuario_atual()
    if origem_id == destino_id or valor <= 0: raise ValueError("Transferência inválida.")
    conn = conectar()
    try:
        origem = conn.execute("SELECT saldo FROM bancos WHERE id=? AND usuario_id=?", (origem_id, usuario_id)).fetchone()
        destino = conn.execute("SELECT id FROM bancos WHERE id=? AND usuario_id=?", (destino_id, usuario_id)).fetchone()
        if not origem or not destino: raise ValueError("Conta inválida.")
        if valor > origem["saldo"]: raise ValueError("Saldo insuficiente.")
        conn.execute("UPDATE bancos SET saldo=saldo-? WHERE id=? AND usuario_id=?", (valor,origem_id,usuario_id))
        conn.execute("UPDATE bancos SET saldo=saldo+? WHERE id=? AND usuario_id=?", (valor,destino_id,usuario_id))
        conn.execute("INSERT INTO transferencias(data,origem_id,destino_id,valor,descricao,usuario_id) VALUES(?,?,?,?,?,?)", (data,origem_id,destino_id,valor,descricao,usuario_id))
        conn.commit()
    finally: conn.close()


# Orçamentos, metas, patrimônio e recorrências
def salvar_orcamento(categoria, mes, limite):
    usuario_id = _usuario_atual(); conn = conectar()
    existente = conn.execute("SELECT id FROM orcamentos WHERE categoria=? AND mes=? AND usuario_id=?", (categoria,mes,usuario_id)).fetchone()
    if existente: conn.execute("UPDATE orcamentos SET limite=? WHERE id=?", (limite,existente["id"]))
    else: conn.execute("INSERT INTO orcamentos(categoria,mes,limite,usuario_id) VALUES(?,?,?,?)", (categoria,mes,limite,usuario_id))
    conn.commit(); conn.close()
def listar_orcamentos(mes):
    usuario_id = _usuario_atual(); conn = conectar(); dados = conn.execute("SELECT * FROM orcamentos WHERE mes=? AND usuario_id=? ORDER BY categoria", (mes,usuario_id)).fetchall(); conn.close(); return dados


def adicionar_meta(nome, valor_alvo, prazo, cor):
    usuario_id = _usuario_atual(); conn = conectar(); conn.execute("INSERT INTO metas(nome,valor_alvo,prazo,cor,usuario_id) VALUES(?,?,?,?,?)", (nome,valor_alvo,prazo,cor,usuario_id)); conn.commit(); conn.close()
def listar_metas(): return _listar("metas", "prazo, nome")
def aportar_meta(registro_id, valor):
    usuario_id = _usuario_atual(); conn = conectar(); conn.execute("UPDATE metas SET valor_atual=valor_atual+? WHERE id=? AND usuario_id=?", (valor,registro_id,usuario_id)); conn.commit(); conn.close()


def adicionar_patrimonio(nome, tipo, categoria, valor, data):
    usuario_id = _usuario_atual(); conn = conectar(); conn.execute("INSERT INTO patrimonio(nome,tipo,categoria,valor,atualizado_em,usuario_id) VALUES(?,?,?,?,?,?)", (nome,tipo,categoria,valor,data,usuario_id)); conn.commit(); conn.close()
def listar_patrimonio(): return _listar("patrimonio", "tipo, nome")


def adicionar_recorrencia(tipo, categoria, descricao, valor, dia):
    usuario_id = _usuario_atual(); conn = conectar(); conn.execute("INSERT INTO recorrencias(tipo,categoria,descricao,valor,dia,usuario_id) VALUES(?,?,?,?,?,?)", (tipo,categoria,descricao,valor,dia,usuario_id)); conn.commit(); conn.close()
def listar_recorrencias():
    usuario_id = _usuario_atual(); conn = conectar(); dados = conn.execute("SELECT * FROM recorrencias WHERE ativa=1 AND usuario_id=? ORDER BY dia", (usuario_id,)).fetchall(); conn.close(); return dados

def pausar_recorrencia(registro_id):
    usuario_id = _usuario_atual(); conn = conectar(); conn.execute("UPDATE recorrencias SET ativa=0 WHERE id=? AND usuario_id=?", (registro_id,usuario_id)); conn.commit(); conn.close()

def excluir_recorrencia(registro_id): _excluir("recorrencias", registro_id)


def proximos_vencimentos(limite=5):
    hoje = date.today(); vencimentos = []
    for item in listar_recorrencias():
        if item["tipo"] != "Despesa" or not item["ativa"]: continue
        ano, mes = hoje.year, hoje.month; dia = min(int(item["dia"]), calendar.monthrange(ano, mes)[1]); vencimento = date(ano, mes, dia)
        if vencimento < hoje:
            ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1); dia = min(int(item["dia"]), calendar.monthrange(ano, mes)[1]); vencimento = date(ano, mes, dia)
        vencimentos.append({"data": vencimento, "descricao": item["descricao"], "categoria": item["categoria"], "valor": item["valor"]})
    return sorted(vencimentos, key=lambda item: item["data"])[:limite]


def gerar_recorrencias(mes):
    usuario_id = _usuario_atual(); conn = conectar()
    itens = conn.execute("SELECT * FROM recorrencias WHERE ativa=1 AND usuario_id=? AND (ultimo_mes IS NULL OR ultimo_mes != ?)", (usuario_id,mes)).fetchall()
    for item in itens:
        ano, numero_mes = map(int, mes.split("-")); dia = min(int(item["dia"]), calendar.monthrange(ano,numero_mes)[1]); tabela = "receitas" if item["tipo"] == "Receita" else "despesas"
        conn.execute(f"INSERT INTO {tabela}(data,categoria,descricao,valor,usuario_id) VALUES(?,?,?,?,?)", (f"{mes}-{dia:02d}",item["categoria"],item["descricao"],item["valor"],usuario_id))
        conn.execute("UPDATE recorrencias SET ultimo_mes=? WHERE id=? AND usuario_id=?", (mes,item["id"],usuario_id))
    conn.commit(); conn.close(); return len(itens)


# Holerites
def salvar_holerite(competencia, salario_bruto, inss, irrf, consignado, pat, unimed, fgts, outros_descontos, salario_liquido, arquivo_nome):
    """Salva os indicadores de um holerite, sem guardar o arquivo original."""
    usuario_id = _usuario_atual(); conn = conectar()
    existente = conn.execute("SELECT id FROM holerites WHERE competencia=? AND usuario_id=?", (competencia, usuario_id)).fetchone()
    valores = (salario_bruto, inss, irrf, consignado, pat, unimed, fgts, outros_descontos, salario_liquido, arquivo_nome)
    if existente:
        conn.execute("UPDATE holerites SET salario_bruto=?, inss=?, irrf=?, consignado=?, pat=?, unimed=?, fgts=?, outros_descontos=?, salario_liquido=?, arquivo_nome=? WHERE id=? AND usuario_id=?", (*valores, existente["id"], usuario_id))
    else:
        conn.execute("INSERT INTO holerites(competencia,salario_bruto,inss,irrf,consignado,pat,unimed,fgts,outros_descontos,salario_liquido,arquivo_nome,usuario_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (competencia, *valores, usuario_id))
    conn.commit(); conn.close()


def listar_holerites():
    return _listar("holerites", "competencia DESC")


# Conciliação e projeção mensal
def importar_extrato(lancamentos, origem="CSV"):
    usuario_id = _usuario_atual(); conn = conectar()
    for item in lancamentos:
        conn.execute("INSERT INTO conciliacoes(data,descricao,valor,tipo,origem,usuario_id) VALUES(?,?,?,?,?,?)", (item["data"],item["descricao"],item["valor"],"Receita" if item["valor"] >= 0 else "Despesa",origem,usuario_id))
    conn.commit(); conn.close(); return len(lancamentos)

def listar_conciliacoes(): return _listar("conciliacoes", "data DESC, id DESC")
def marcar_conciliado(registro_id):
    usuario_id = _usuario_atual(); conn = conectar(); conn.execute("UPDATE conciliacoes SET conciliado=1 WHERE id=? AND usuario_id=?", (registro_id,usuario_id)); conn.commit(); conn.close()

def projecao_mes(mes):
    receitas = sum(item["valor"] for item in listar_receitas() if str(item["data"]).startswith(mes))
    despesas = sum(item["valor"] for item in listar_despesas() if str(item["data"]).startswith(mes))
    previstas_receita = sum(item["valor"] for item in listar_recorrencias() if item["tipo"] == "Receita" and item["ultimo_mes"] != mes)
    previstas_despesa = sum(item["valor"] for item in listar_recorrencias() if item["tipo"] == "Despesa" and item["ultimo_mes"] != mes)
    return {"receitas":receitas,"despesas":despesas,"previstas_receita":previstas_receita,"previstas_despesa":previstas_despesa,"saldo_projetado":receitas+previstas_receita-despesas-previstas_despesa}


criar_banco()
