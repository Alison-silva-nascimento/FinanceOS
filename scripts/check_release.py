"""Falha a release quando arquivos sensíveis ou artefatos locais estão no Git."""

import shutil
import subprocess
import sys
import re
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
NOMES_PROIBIDOS = {".env", "secrets.toml", "finance.db"}
TRECHOS_PROIBIDOS = (".pyc", "__pycache__", "/backups/", "/work/")
PADROES_SEGREDOS = ("supabase_service_role", "service_role_key")
URI_COM_CREDENCIAL = re.compile(r"postgres(?:ql)?://[^\s:/]+:[^\s/@]+@[^\s/]+", re.IGNORECASE)
OBRIGATORIOS = (
    "Dockerfile", "compose.yaml", ".dockerignore", ".env.example",
    "deploy/Caddyfile", ".streamlit/config.toml", ".github/dependabot.yml",
    ".github/workflows/security.yml", ".github/workflows/codeql.yml",
    "scripts/check_secrets.py", "scripts/check_git_history.py",
)
ARQUIVOS_VERIFICADORES = {"scripts/check_release.py"}


def executar(*argumentos):
    return subprocess.run(argumentos, cwd=RAIZ, text=True, capture_output=True, check=False)


def main():
    erros = []
    git = executar("git", "ls-files")
    if git.returncode:
        erros.append("Não foi possível consultar os arquivos rastreados pelo Git.")
    else:
        for arquivo in git.stdout.splitlines():
            caminho = f"/{arquivo.replace(chr(92), '/')}"
            nome = Path(arquivo).name
            if nome in NOMES_PROIBIDOS or any(trecho in caminho for trecho in TRECHOS_PROIBIDOS):
                erros.append(f"Arquivo proibido rastreado: {arquivo}")
            destino = RAIZ / arquivo
            if arquivo not in ARQUIVOS_VERIFICADORES and destino.is_file() and destino.stat().st_size <= 2 * 1024 * 1024:
                try:
                    conteudo = destino.read_text(encoding="utf-8", errors="ignore").lower()
                except OSError:
                    conteudo = ""
                segredo_literal = any(padrao in conteudo for padrao in PADROES_SEGREDOS)
                uri_real = any(
                    "..." not in ocorrencia.group(0)
                    for ocorrencia in URI_COM_CREDENCIAL.finditer(conteudo)
                )
                if arquivo != ".env.example" and (segredo_literal or uri_real):
                    erros.append(f"Possível credencial ou URI de banco rastreada: {arquivo}")
    for arquivo in OBRIGATORIOS:
        if not (RAIZ / arquivo).is_file():
            erros.append(f"Arquivo obrigatório ausente: {arquivo}")
    compose = (RAIZ / "compose.yaml").read_text(encoding="utf-8")
    for trecho in ("financeos:", "proxy:", "financeos_data:", "no-new-privileges:true"):
        if trecho not in compose:
            erros.append(f"Configuração ausente no Compose: {trecho}")
    if shutil.which("docker"):
        validacao = executar("docker", "compose", "config", "--quiet")
        if validacao.returncode:
            erros.append(f"Docker Compose inválido: {validacao.stderr.strip()}")
    auditoria_historico = executar(sys.executable, "scripts/check_git_history.py")
    if auditoria_historico.returncode:
        erros.append(auditoria_historico.stdout.strip() or "Histórico Git não passou na auditoria.")
    auditoria_segredos = executar(sys.executable, "scripts/check_secrets.py")
    if auditoria_segredos.returncode:
        erros.append(auditoria_segredos.stdout.strip() or "Arquivos não passaram na auditoria de segredos.")
    if erros:
        print("RELEASE BLOQUEADA")
        for erro in erros: print(f"- {erro}")
        return 1
    print("Release pronta: arquivos sensíveis ausentes e configuração básica válida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
