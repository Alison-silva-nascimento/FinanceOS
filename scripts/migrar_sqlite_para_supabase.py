"""Migra os dados locais do FinanceOS para um PostgreSQL/Supabase vazio.

Uso (PowerShell):
  $env:DATABASE_URL = 'postgresql://...'
  python scripts/migrar_sqlite_para_supabase.py --confirmar
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import ADMIN_USER
from database.postgres import TABELAS_MIGRAVEIS, conectar_postgres, criar_esquema_postgres


def _colunas_sqlite(conexao, tabela):
    return [linha["name"] for linha in conexao.execute(f"PRAGMA table_info({tabela})")]


def _colunas_postgres(conexao, tabela):
    dados = conexao.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=?",
        (tabela,),
    ).fetchall()
    return {linha["column_name"] for linha in dados}


def migrar(caminho_sqlite, database_url, substituir=False):
    criar_esquema_postgres(database_url, ADMIN_USER)
    origem = sqlite3.connect(caminho_sqlite)
    origem.row_factory = sqlite3.Row
    destino = conectar_postgres(database_url)
    try:
        existentes = {linha["name"] for linha in origem.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not existentes.intersection(TABELAS_MIGRAVEIS):
            raise RuntimeError("O arquivo informado não parece ser um banco FinanceOS válido.")
        if substituir:
            destino.execute("TRUNCATE TABLE " + ", ".join(TABELAS_MIGRAVEIS) + " RESTART IDENTITY CASCADE")
        else:
            total = sum(destino.execute(f"SELECT COUNT(*) AS total FROM {tabela}").fetchone()["total"] for tabela in TABELAS_MIGRAVEIS)
            if total:
                raise RuntimeError("O Supabase já possui dados. Use --substituir somente após confirmar que deseja apagar a produção.")
        # Versões muito antigas criavam a linha "Administrador/admin" sem
        # senha. Ela nunca foi uma conta autenticável; seus lançamentos eram
        # dados locais legados. Vinculamos esses itens ao administrador real.
        usuarios_origem = origem.execute("SELECT id, usuario, senha_hash FROM usuarios").fetchall()
        # Somente a antiga conta técnica "Administrador/@admin" deve ficar
        # fora da migração. Contas reais (inclusive de versões antigas) não
        # podem ser descartadas apenas por não terem preenchido um campo
        # posteriormente acrescentado ao SQLite.
        usuarios_invalidos = {
            linha["id"] for linha in usuarios_origem
            if str(linha["usuario"] or "").strip().lower() == "admin"
            and not str(linha["senha_hash"] or "").strip()
        }
        administrador = next(
            (linha for linha in usuarios_origem if str(linha["usuario"] or "").lower() == ADMIN_USER and linha["id"] not in usuarios_invalidos),
            None,
        )
        if usuarios_invalidos and not administrador:
            raise RuntimeError("Há dados legados sem conta válida, mas não encontrei alison.nascimento para vinculá-los.")

        resumo = {}
        for tabela in TABELAS_MIGRAVEIS:
            if tabela not in existentes:
                continue
            colunas = [coluna for coluna in _colunas_sqlite(origem, tabela) if coluna in _colunas_postgres(destino, tabela)]
            if not colunas:
                continue
            linhas = origem.execute(f"SELECT {', '.join(colunas)} FROM {tabela}").fetchall()
            if tabela == "usuarios":
                linhas = [linha for linha in linhas if linha["id"] not in usuarios_invalidos]
            if linhas:
                placeholders = ", ".join("?" for _ in colunas)
                for linha in linhas:
                    valores = []
                    for coluna in colunas:
                        valor = linha[coluna]
                        if coluna == "usuario_id" and valor in usuarios_invalidos:
                            valor = administrador["id"]
                        # Bancos SQLite criados por versões antigas podem ter
                        # timestamps técnicos nulos. O PostgreSQL exige esses
                        # campos, então registramos o momento da migração sem
                        # alterar os valores financeiros do lançamento.
                        if coluna in {"criado_em", "atualizado_em", "fechado_em"} and not valor:
                            valor = datetime.now(timezone.utc).isoformat(timespec="seconds")
                        if tabela == "usuarios" and coluna == "perfil" and not valor:
                            valor = "usuario"
                        if tabela == "usuarios" and coluna == "sessao_versao" and not valor:
                            valor = 1
                        valores.append(valor)
                    destino.execute(
                        f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES ({placeholders})",
                        tuple(valores),
                    )
            resumo[tabela] = len(linhas)
        if usuarios_invalidos:
            resumo["contas_legadas_vinculadas_a_alison"] = len(usuarios_invalidos)
        for tabela in TABELAS_MIGRAVEIS:
            destino.execute(
                f"SELECT setval(pg_get_serial_sequence('{tabela}', 'id'), COALESCE((SELECT MAX(id) FROM {tabela}), 1), (SELECT COUNT(*) > 0 FROM {tabela}))"
            )
        destino.commit()
        return resumo
    except Exception:
        destino.rollback()
        raise
    finally:
        origem.close()
        destino.close()


def main():
    parser = argparse.ArgumentParser(description="Migra finance.db local para o Supabase.")
    parser.add_argument("--sqlite", default=str(ROOT / "database" / "finance.db"), help="Caminho do finance.db local")
    parser.add_argument("--confirmar", action="store_true", help="Confirma a gravação na produção")
    parser.add_argument("--substituir", action="store_true", help="Apaga dados existentes no Supabase antes de migrar")
    args = parser.parse_args()
    if not args.confirmar:
        parser.error("Para gravar, execute novamente com --confirmar.")
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        parser.error("Defina DATABASE_URL no ambiente; não informe a senha na linha de comando.")
    resumo = migrar(Path(args.sqlite), database_url, args.substituir)
    print("Migração concluída:")
    for tabela, quantidade in resumo.items():
        print(f"- {tabela}: {quantidade}")


if __name__ == "__main__":
    main()
