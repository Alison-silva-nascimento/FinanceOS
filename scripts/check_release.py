"""Falha a release quando arquivos sensíveis ou artefatos locais estão no Git."""

import shutil
import subprocess
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
NOMES_PROIBIDOS = {".env", "secrets.toml", "finance.db"}
TRECHOS_PROIBIDOS = (".pyc", "__pycache__", "/backups/", "/work/")
OBRIGATORIOS = (
    "Dockerfile", "compose.yaml", ".dockerignore", ".env.example",
    "deploy/Caddyfile", ".streamlit/config.toml",
)


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
    if erros:
        print("RELEASE BLOQUEADA")
        for erro in erros: print(f"- {erro}")
        return 1
    print("Release pronta: arquivos sensíveis ausentes e configuração básica válida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
