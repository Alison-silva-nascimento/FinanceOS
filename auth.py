"""Autenticação local do FinanceOS, com senhas protegidas por PBKDF2."""

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta
from io import BytesIO

from database.db import conectar, registrar_evento


ITERACOES_PBKDF2 = 600_000
MAX_FOTO_BYTES = 2 * 1024 * 1024
MAX_PIXELS_FOTO = 16_000_000


def _validar_usuario(usuario):
    if not re.fullmatch(r"[a-z]+(?:\.[a-z]+)+", usuario.strip()):
        return False, "Use o formato nome.sobrenome, apenas com letras minúsculas."
    return True, ""


def _validar_senha(senha):
    if len(senha) < 10:
        return False, "A senha deve ter pelo menos 10 caracteres."
    if not any(caractere.isupper() for caractere in senha):
        return False, "A senha deve conter ao menos uma letra maiúscula."
    if not any(caractere.islower() for caractere in senha):
        return False, "A senha deve conter ao menos uma letra minúscula."
    if not any(caractere.isdigit() or not caractere.isalnum() for caractere in senha):
        return False, "A senha deve conter ao menos um número ou caractere especial."
    return True, ""


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
    if not nome.strip() or not usuario.strip():
        return False, "Informe nome e usuário."
    usuario = usuario.strip()
    valido, mensagem = _validar_usuario(usuario)
    if not valido:
        return False, mensagem
    valido, mensagem = _validar_senha(senha)
    if not valido:
        return False, mensagem

    conn = conectar()
    try:
        cursor = conn.execute(
            "INSERT INTO usuarios (nome, usuario, senha_hash, perfil) VALUES (?, ?, ?, ?)",
            (nome.strip(), usuario, _gerar_hash(senha), "usuario"),
        )
        conn.commit()
        registrar_evento(cursor.lastrowid, "Conta criada")
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
        "SELECT id, usuario, senha_hash, perfil, bloqueado_ate FROM usuarios WHERE usuario = ?", (usuario.strip(),)
    ).fetchone()
    conn.close()
    if registro is not None and _verificar_senha(senha, registro["senha_hash"]):
        conn = conectar()
        conn.execute("UPDATE usuarios SET tentativas_login=0, bloqueado_ate=NULL, ultimo_login=? WHERE id=?", (datetime.now().isoformat(timespec="seconds"), registro["id"]))
        conn.commit(); conn.close()
        registrar_evento(registro["id"], "Login realizado")
        return dict(registro)
    return None


def login_bloqueado(usuario):
    conn = conectar()
    registro = conn.execute("SELECT bloqueado_ate FROM usuarios WHERE usuario=?", (usuario.strip(),)).fetchone()
    conn.close()
    if not registro or not registro["bloqueado_ate"]:
        return False
    try:
        return datetime.fromisoformat(registro["bloqueado_ate"]) > datetime.now()
    except ValueError:
        return False


def registrar_falha_login(usuario):
    """Conta falhas no banco para que o bloqueio sobreviva ao navegador."""
    conn = conectar()
    registro = conn.execute("SELECT id, tentativas_login FROM usuarios WHERE usuario=?", (usuario.strip(),)).fetchone()
    if not registro:
        conn.close(); return False
    tentativas = int(registro["tentativas_login"] or 0) + 1
    bloqueado_ate = None
    bloqueado = tentativas >= 5
    if bloqueado:
        bloqueado_ate = (datetime.now() + timedelta(minutes=10)).isoformat(timespec="seconds")
        tentativas = 0
    conn.execute("UPDATE usuarios SET tentativas_login=?, bloqueado_ate=? WHERE id=?", (tentativas, bloqueado_ate, registro["id"]))
    conn.commit(); conn.close()
    registrar_evento(registro["id"], "Tentativa de login inválida" if not bloqueado else "Conta bloqueada por tentativas inválidas")
    return bloqueado


def alterar_senha(usuario, senha_atual, nova_senha):
    valida, mensagem = _validar_senha(nova_senha)
    if not valida:
        return False, mensagem
    if not autenticar(usuario, senha_atual):
        return False, "A senha atual está incorreta."
    conn = conectar()
    conn.execute("UPDATE usuarios SET senha_hash=? WHERE usuario=?", (_gerar_hash(nova_senha), usuario))
    conn.commit(); conn.close()
    perfil = obter_perfil(usuario)
    if perfil:
        registrar_evento(perfil["id"], "Senha alterada")
    return True, "Senha atualizada com sucesso."


def obter_perfil(usuario):
    conn = conectar()
    perfil = conn.execute(
        "SELECT id, nome, usuario, perfil, foto_perfil, ultimo_login FROM usuarios WHERE usuario=?",
        (usuario,),
    ).fetchone()
    conn.close()
    return perfil


def salvar_foto_perfil(usuario, foto):
    if len(foto) > MAX_FOTO_BYTES:
        return False, "A foto deve ter no máximo 2 MB."
    try:
        from PIL import Image
        imagem = Image.open(BytesIO(foto))
        imagem.verify()
        imagem = Image.open(BytesIO(foto))
        imagem.load()
        if imagem.width * imagem.height > MAX_PIXELS_FOTO:
            return False, "A imagem possui resolução muito alta."
        imagem.thumbnail((512, 512))
        saida = BytesIO(); imagem.convert("RGB").save(saida, format="JPEG", quality=88, optimize=True)
        foto = saida.getvalue()
    except Exception:
        return False, "Envie uma imagem válida em PNG, JPG ou WEBP."
    conn = conectar()
    conn.execute("UPDATE usuarios SET foto_perfil=? WHERE usuario=?", (foto, usuario))
    conn.commit()
    conn.close()
    perfil = obter_perfil(usuario)
    if perfil:
        registrar_evento(perfil["id"], "Foto de perfil atualizada")
    return True, "Foto atualizada."


def renderizar_menu_usuario():
    """Exibe o acesso ao perfil no topo da barra lateral."""
    import streamlit as st

    usuario = st.session_state.get("usuario")
    dados = obter_perfil(usuario) if usuario else None
    with st.sidebar:
        with st.popover("👤 Perfil", use_container_width=True):
                if dados and dados["foto_perfil"]:
                    st.image(dados["foto_perfil"], width=96)
                else:
                    st.markdown("## 👤")
                st.markdown(f"**{dados['nome'] if dados else usuario}**")
                st.caption(f"@{usuario}")
                if dados and dados["perfil"] == "admin":
                    st.caption("Administrador")
                foto = st.file_uploader("Adicionar ou trocar foto", type=["png", "jpg", "jpeg", "webp"], key="foto_perfil")
                if foto and st.button("Salvar foto", use_container_width=True, key="salvar_foto_perfil"):
                    sucesso, mensagem = salvar_foto_perfil(usuario, foto.getvalue())
                    (st.success if sucesso else st.error)(mensagem)
                    if sucesso:
                        st.rerun()
                st.divider()
                if st.button("Sair da conta", use_container_width=True, key="sair_perfil"):
                    st.session_state.clear()
                    st.rerun()


def exigir_login():
    """Redireciona páginas internas para a tela de login quando necessário."""
    import streamlit as st

    if not st.session_state.get("logado", False):
        st.switch_page("app.py")
