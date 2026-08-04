import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "database" / "finance.db"


def autenticar(usuario, senha):

    conn = sqlite3.connect(DB)

    usuario_db = conn.execute("""
        SELECT *
        FROM usuarios
        WHERE usuario = ?
        AND senha = ?
    """, (
        usuario,
        senha
    )).fetchone()

    conn.close()

    return usuario_db is not None
