"""Autenticação local do FinanceOS, com senhas protegidas por PBKDF2."""

import hashlib
import hmac
import secrets

from database.db import conectar


ITERACOES_PBKDF2 = 600_000


def _gerar_hash(senha, sal=None):
    sal = sal or secrets.token_bytes(16)
    hash_senha = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), sal, ITERACOES_PBKDF2
    )
    return f"pbkdf2_sha256${ITERACOES_PBKDF2}${sal.hex()}${hash_senha.hex()}"


def _verificar_senha(senha, hash_armazenado):
    try:
        algoritmo, iteracoes, sal_hex, hash_hex = hash_armazenado.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        hash_calculado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), bytes.fromhex(sal_hex), int(iteracoes)
        ).hex()
        return hmac.compare_digest(hash_calculado, hash_hex)
    except (AttributeError, ValueError):
        return False


def possui_usuario():
    conn = conectar()
    total = conn.execute(
        "SELECT COUNT(*) FROM usuarios WHERE senha_hash IS NOT NULL AND senha_hash != ''"
    ).fetchone()[0]
    conn.close()
    return total > 0


def criar_usuario(nome, usuario, senha):
    if len(senha) < 10:
        return False, "A senha deve ter pelo menos 10 caracteres."
    if not nome.strip() or not usuario.strip():
        return False, "Informe nome e usuário."

    conn = conectar()
    try:
        conn.execute(
            "INSERT INTO usuarios (nome, usuario, senha_hash) VALUES (?, ?, ?)",
            (nome.strip(), usuario.strip(), _gerar_hash(senha)),
        )
        conn.commit()
        return True, "Usuário criado com sucesso."
    except Exception as erro:
        if "UNIQUE constraint failed" in str(erro):
            return False, "Esse nome de usuário já está em uso."
        return False, "Não foi possível criar o usuário."
    finally:
        conn.close()


def autenticar(usuario, senha):
    conn = conectar()
    registro = conn.execute(
        "SELECT usuario, senha_hash FROM usuarios WHERE usuario = ?", (usuario.strip(),)
    ).fetchone()
    conn.close()
    return registro is not None and _verificar_senha(senha, registro["senha_hash"])


def alterar_senha(usuario, senha_atual, nova_senha):
    if len(nova_senha) < 10:
        return False, "A nova senha deve ter pelo menos 10 caracteres."
    if not autenticar(usuario, senha_atual):
        return False, "A senha atual está incorreta."
    conn = conectar()
    conn.execute("UPDATE usuarios SET senha_hash=? WHERE usuario=?", (_gerar_hash(nova_senha), usuario))
    conn.commit(); conn.close()
    return True, "Senha atualizada com sucesso."


def exigir_login():
    """Redireciona páginas internas para a tela de login quando necessário."""
    import streamlit as st

    if not st.session_state.get("logado", False):
        st.switch_page("app.py")
