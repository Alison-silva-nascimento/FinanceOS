"""Adaptador PostgreSQL para o FinanceOS.

Mantém a API de execução usada pelo SQLite para que as páginas não precisem
conhecer o banco em uso. A URL nunca é registrada em código ou no Git.
"""

import re
import threading


_POOL_LOCK = threading.Lock()
_POOLS = {}
_ESQUEMA_LOCK = threading.Lock()
_ESQUEMAS_INICIALIZADOS = set()

def _sql_postgres(sql):
    """Converte para PostgreSQL os trechos SQLite usados pela aplicação."""
    sql = re.sub(
        r"GROUP_CONCAT\s*\(\s*([A-Za-z_][\w.]*)\s*\)",
        r"STRING_AGG(\1::text, ',')",
        sql,
        flags=re.IGNORECASE,
    )
    return sql.replace("?", "%s")


class CursorPostgres:
    def __init__(self, cursor):
        self._cursor = cursor
        self._lastrowid = None

    def execute(self, sql, parametros=None):
        self._cursor.execute(_sql_postgres(sql), parametros or ())
        insercao = re.match(r"\s*INSERT\s+INTO\s+[^\s(]+\s*\(([^)]*)\)", sql, flags=re.IGNORECASE)
        colunas = insercao.group(1).lower().replace('"', '').split(",") if insercao else []
        # Migrações preservam o id do SQLite. Nesse caso nenhuma sequência é
        # acionada e LASTVAL() não existe na sessão; a aplicação normal não
        # envia "id" e continua recebendo o lastrowid normalmente.
        if insercao and "id" not in {coluna.strip() for coluna in colunas}:
            self._cursor.execute("SELECT LASTVAL() AS id")
            self._lastrowid = self._cursor.fetchone()["id"]
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._lastrowid

    def __iter__(self):
        return iter(self._cursor)


class ConexaoPostgres:
    def __init__(self, conexao, pool):
        self._conexao = conexao
        self._pool = pool
        self._fechada = False

    def cursor(self):
        return CursorPostgres(self._conexao.cursor())

    def execute(self, sql, parametros=None):
        return self.cursor().execute(sql, parametros)

    def commit(self):
        self._conexao.commit()

    def rollback(self):
        self._conexao.rollback()

    def close(self):
        if self._fechada:
            return
        try:
            self._pool.putconn(self._conexao)
        finally:
            self._fechada = True


def _obter_pool(database_url):
    try:
        from psycopg.rows import dict_row
        from psycopg_pool import ConnectionPool
    except ImportError as erro:
        raise RuntimeError("PostgreSQL não está disponível. Instale as dependências do FinanceOS.") from erro
    with _POOL_LOCK:
        pool = _POOLS.get(database_url)
        if pool is None:
            pool = ConnectionPool(
                conninfo=database_url, min_size=0, max_size=4, timeout=10,
                kwargs={"row_factory": dict_row, "connect_timeout": 10},
            )
            _POOLS[database_url] = pool
        return pool


def conectar_postgres(database_url):
    pool = _obter_pool(database_url)
    return ConexaoPostgres(pool.getconn(), pool)


_AGORA_TEXTO = "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::text"

_ESQUEMA = (
    f"""CREATE TABLE IF NOT EXISTS usuarios(
        id BIGSERIAL PRIMARY KEY, nome TEXT NOT NULL, usuario TEXT NOT NULL UNIQUE,
        senha_hash TEXT NOT NULL, perfil TEXT NOT NULL DEFAULT 'usuario',
        criado_em TEXT NOT NULL DEFAULT {_AGORA_TEXTO}, foto_perfil BYTEA,
        tentativas_login INTEGER NOT NULL DEFAULT 0, bloqueado_ate TEXT,
        ultimo_login TEXT, sessao_versao INTEGER NOT NULL DEFAULT 1)""",
    f"""CREATE TABLE IF NOT EXISTS eventos_seguranca(
        id BIGSERIAL PRIMARY KEY, usuario_id BIGINT, acao TEXT NOT NULL,
        detalhes TEXT, criado_em TEXT NOT NULL DEFAULT {_AGORA_TEXTO})""",
    """CREATE TABLE IF NOT EXISTS receitas(
        id BIGSERIAL PRIMARY KEY, data TEXT NOT NULL, categoria TEXT NOT NULL,
        descricao TEXT, valor DOUBLE PRECISION NOT NULL, usuario_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS despesas(
        id BIGSERIAL PRIMARY KEY, data TEXT NOT NULL, categoria TEXT NOT NULL,
        descricao TEXT, valor DOUBLE PRECISION NOT NULL, usuario_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS cartoes(
        id BIGSERIAL PRIMARY KEY, nome TEXT NOT NULL, banco TEXT NOT NULL,
        bandeira TEXT NOT NULL, limite DOUBLE PRECISION NOT NULL, fechamento INTEGER NOT NULL,
        vencimento INTEGER NOT NULL, cor TEXT DEFAULT '#6D28D9', usuario_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS bancos(
        id BIGSERIAL PRIMARY KEY, nome TEXT NOT NULL, banco TEXT NOT NULL,
        tipo TEXT NOT NULL, saldo DOUBLE PRECISION NOT NULL, cor TEXT DEFAULT '#2563EB', usuario_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS orcamentos(
        id BIGSERIAL PRIMARY KEY, categoria TEXT NOT NULL, mes TEXT NOT NULL,
        limite DOUBLE PRECISION NOT NULL, usuario_id BIGINT, UNIQUE(categoria, mes, usuario_id))""",
    """CREATE TABLE IF NOT EXISTS metas(
        id BIGSERIAL PRIMARY KEY, nome TEXT NOT NULL, valor_alvo DOUBLE PRECISION NOT NULL,
        valor_atual DOUBLE PRECISION NOT NULL DEFAULT 0, prazo TEXT,
        cor TEXT DEFAULT '#3B82F6', usuario_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS patrimonio(
        id BIGSERIAL PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL,
        categoria TEXT, valor DOUBLE PRECISION NOT NULL, atualizado_em TEXT NOT NULL, usuario_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS recorrencias(
        id BIGSERIAL PRIMARY KEY, tipo TEXT NOT NULL, categoria TEXT NOT NULL,
        descricao TEXT, valor DOUBLE PRECISION NOT NULL, dia INTEGER NOT NULL,
        ativa INTEGER NOT NULL DEFAULT 1, ultimo_mes TEXT, usuario_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS compras_cartao(
        id BIGSERIAL PRIMARY KEY, cartao_id BIGINT NOT NULL, data TEXT NOT NULL,
        descricao TEXT NOT NULL, categoria TEXT NOT NULL, valor DOUBLE PRECISION NOT NULL,
        parcelas INTEGER NOT NULL DEFAULT 1, parcela_atual INTEGER NOT NULL DEFAULT 1,
        paga INTEGER NOT NULL DEFAULT 0, competencia TEXT, usuario_id BIGINT, importacao_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS transferencias(
        id BIGSERIAL PRIMARY KEY, data TEXT NOT NULL, origem_id BIGINT NOT NULL,
        destino_id BIGINT NOT NULL, valor DOUBLE PRECISION NOT NULL, descricao TEXT, usuario_id BIGINT)""",
    f"""CREATE TABLE IF NOT EXISTS holerites(
        id BIGSERIAL PRIMARY KEY, competencia TEXT NOT NULL,
        salario_bruto DOUBLE PRECISION NOT NULL DEFAULT 0, inss DOUBLE PRECISION NOT NULL DEFAULT 0,
        irrf DOUBLE PRECISION NOT NULL DEFAULT 0, consignado DOUBLE PRECISION NOT NULL DEFAULT 0,
        adiantamento_salarial DOUBLE PRECISION NOT NULL DEFAULT 0, pat DOUBLE PRECISION NOT NULL DEFAULT 0,
        unimed DOUBLE PRECISION NOT NULL DEFAULT 0, fgts DOUBLE PRECISION NOT NULL DEFAULT 0,
        outros_descontos DOUBLE PRECISION NOT NULL DEFAULT 0, salario_liquido DOUBLE PRECISION NOT NULL DEFAULT 0,
        arquivo_nome TEXT, usuario_id BIGINT, criado_em TEXT NOT NULL DEFAULT {_AGORA_TEXTO},
        UNIQUE(competencia, usuario_id))""",
    """CREATE TABLE IF NOT EXISTS conciliacoes(
        id BIGSERIAL PRIMARY KEY, data TEXT NOT NULL, descricao TEXT NOT NULL,
        valor DOUBLE PRECISION NOT NULL, tipo TEXT NOT NULL, conciliado INTEGER NOT NULL DEFAULT 0,
        origem TEXT, usuario_id BIGINT, importacao_id BIGINT, vinculo_tipo TEXT, vinculo_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS faturas_pagas(
        id BIGSERIAL PRIMARY KEY, cartao_id BIGINT NOT NULL, competencia TEXT NOT NULL,
        banco_id BIGINT, valor DOUBLE PRECISION NOT NULL, pago_em TEXT NOT NULL, usuario_id BIGINT,
        UNIQUE(cartao_id, competencia, usuario_id))""",
    f"""CREATE TABLE IF NOT EXISTS faturas_resumo(
        id BIGSERIAL PRIMARY KEY, cartao_id BIGINT NOT NULL, competencia TEXT NOT NULL,
        total_a_pagar DOUBLE PRECISION NOT NULL, origem TEXT, usuario_id BIGINT,
        atualizado_em TEXT NOT NULL DEFAULT {_AGORA_TEXTO}, UNIQUE(cartao_id, competencia, usuario_id))""",
    f"""CREATE TABLE IF NOT EXISTS importacoes(
        id BIGSERIAL PRIMARY KEY, tipo TEXT NOT NULL, origem TEXT NOT NULL,
        arquivo_nome TEXT, competencia TEXT, cartao_id BIGINT, quantidade INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'concluida', criado_em TEXT NOT NULL DEFAULT {_AGORA_TEXTO},
        desfeito_em TEXT, usuario_id BIGINT)""",
    """CREATE TABLE IF NOT EXISTS regras_categoria(
        id BIGSERIAL PRIMARY KEY, termo TEXT NOT NULL, categoria TEXT NOT NULL,
        usuario_id BIGINT, UNIQUE(termo, usuario_id))""",
    f"""CREATE TABLE IF NOT EXISTS fechamentos_mensais(
        id BIGSERIAL PRIMARY KEY, competencia TEXT NOT NULL, receitas DOUBLE PRECISION NOT NULL,
        despesas DOUBLE PRECISION NOT NULL, faturas DOUBLE PRECISION NOT NULL, saldo DOUBLE PRECISION NOT NULL,
        observacoes TEXT, fechado_em TEXT NOT NULL DEFAULT {_AGORA_TEXTO}, usuario_id BIGINT,
        UNIQUE(competencia, usuario_id))""",
)


def criar_esquema_postgres(database_url, usuario_admin):
    """Inicializa o esquema somente uma vez por processo da aplicação."""
    pool = _obter_pool(database_url)
    chave = (id(pool), usuario_admin)
    with _ESQUEMA_LOCK:
        if chave in _ESQUEMAS_INICIALIZADOS:
            return
        conexao = conectar_postgres(database_url)
        try:
            for sql in _ESQUEMA:
                conexao.execute(sql)
            if usuario_admin:
                conexao.execute("UPDATE usuarios SET perfil='usuario' WHERE lower(usuario) != ? AND perfil='admin'", (usuario_admin,))
                conexao.execute("UPDATE usuarios SET perfil='admin' WHERE lower(usuario) = ?", (usuario_admin,))
            conexao.commit()
            _ESQUEMAS_INICIALIZADOS.add(chave)
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()


TABELAS_MIGRAVEIS = (
    "usuarios", "eventos_seguranca", "receitas", "despesas", "cartoes", "bancos",
    "orcamentos", "metas", "patrimonio", "recorrencias", "compras_cartao",
    "transferencias", "holerites", "conciliacoes", "faturas_pagas", "faturas_resumo",
    "importacoes", "regras_categoria", "fechamentos_mensais",
)
