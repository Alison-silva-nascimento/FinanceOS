"""Bloqueia padrões comuns de credenciais nos arquivos rastreados pelo Git."""

import re
import subprocess
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
LIMITE = 2 * 1024 * 1024
IGNORADOS = {"scripts/check_secrets.py", ".env.example"}
PADROES = {
    "URI PostgreSQL com senha": re.compile(r"postgres(?:ql)?://[^\s:/]+:[^\s/@]+@[^\s/]+", re.I),
    "chave privada": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "token GitHub": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "JWT Supabase": re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\b"),
}


def main():
    consulta = subprocess.run(
        ["git", "ls-files"], cwd=RAIZ, text=True, capture_output=True, check=False
    )
    if consulta.returncode:
        print("Não foi possível consultar os arquivos rastreados.")
        return 2

    achados = []
    for relativo in consulta.stdout.splitlines():
        relativo = relativo.replace("\\", "/")
        arquivo = RAIZ / relativo
        if relativo in IGNORADOS or not arquivo.is_file() or arquivo.stat().st_size > LIMITE:
            continue
        conteudo = arquivo.read_text(encoding="utf-8", errors="ignore")
        for descricao, padrao in PADROES.items():
            for correspondencia in padrao.finditer(conteudo):
                valor = correspondencia.group(0)
                if "..." not in valor and "USUARIO" not in valor and "SENHA" not in valor:
                    linha = conteudo.count("\n", 0, correspondencia.start()) + 1
                    achados.append(f"{relativo}:{linha}: {descricao}")

    if achados:
        print("VERIFICAÇÃO DE SEGREDOS BLOQUEADA")
        for achado in achados:
            print(f"- {achado}")
        return 1
    print("Verificação de segredos concluída sem ocorrências conhecidas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
