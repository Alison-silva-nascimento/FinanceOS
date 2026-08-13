"""Detecta artefatos sensíveis que continuam recuperáveis no histórico Git."""

import subprocess
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
NOMES_PROIBIDOS = {".env", "secrets.toml", "finance.db"}
SUFIXOS_PROIBIDOS = (".db", ".sqlite", ".sqlite3")


def main():
    resultado = subprocess.run(
        ["git", "log", "--all", "--name-only", "--pretty=format:"],
        cwd=RAIZ,
        text=True,
        capture_output=True,
        check=False,
    )
    if resultado.returncode:
        print("Não foi possível auditar o histórico Git.")
        return 2

    encontrados = set()
    for linha in resultado.stdout.splitlines():
        caminho = linha.strip().replace("\\", "/")
        if not caminho:
            continue
        nome = Path(caminho).name.lower()
        if nome in NOMES_PROIBIDOS or nome.endswith(SUFIXOS_PROIBIDOS):
            encontrados.add(caminho)

    if encontrados:
        print("HISTÓRICO BLOQUEADO: artefatos sensíveis ainda são recuperáveis:")
        for caminho in sorted(encontrados):
            print(f"- {caminho}")
        print("Reescreva o histórico e troque credenciais potencialmente expostas antes de publicar.")
        return 1

    print("Histórico Git sem bancos ou arquivos de configuração sensíveis conhecidos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
