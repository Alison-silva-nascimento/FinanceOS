"""Testes de regressão dos fluxos financeiros mais sensíveis do FinanceOS."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Diretório exclusivo por execução: o banco aplica ACLs no Windows e um
# diretório reaproveitado pode ficar indisponível para o processo seguinte.
BOOTSTRAP_DIR = Path(tempfile.mkdtemp(prefix="financeos-test-"))
os.environ["FINANCEOS_DB_FILE"] = str(BOOTSTRAP_DIR / "bootstrap.db")
os.environ["FINANCEOS_BACKUP_DIR"] = str(BOOTSTRAP_DIR / "backups")

from services import despesas_service, receitas_service
from auth import _validar_senha, _validar_usuario
from utils.mercado_pago_fatura import _compras_do_texto
from utils.nubank_fatura import _valor_csv, ler_csv_fatura


class ArquivoEmMemoria:
    def __init__(self, conteudo):
        self._conteudo = conteudo.encode("utf-8")

    def getvalue(self):
        return self._conteudo


class TesteFiltrosServicos(unittest.TestCase):
    def setUp(self):
        self.receitas = [
            {"data": "2026-07-17", "categoria": "Salário", "descricao": "Adiantamento", "valor": 1810},
            {"data": "2026-07-31", "categoria": "Extra", "descricao": "Plantão", "valor": 500},
            {"data": "2026-08-01", "categoria": "Salário", "descricao": "Holerite", "valor": 2380},
        ]
        self.despesas = [
            {"data": "2026-07-05", "categoria": "Celular", "descricao": "Fatura Claro", "valor": 72},
            {"data": "2026-08-18", "categoria": "Transporte", "descricao": "Gol G5", "valor": 939},
        ]

    def test_busca_e_filtro_de_receitas(self):
        with patch.object(receitas_service, "obter_receitas", return_value=self.receitas):
            self.assertEqual(len(receitas_service.buscar_receitas("holerite")), 1)
            self.assertEqual(len(receitas_service.filtrar_receitas(mes="07", ano=2026)), 2)
            self.assertEqual(len(receitas_service.filtrar_receitas(mes="2026-08", categoria="Salário")), 1)

    def test_busca_e_filtro_de_despesas(self):
        with patch.object(despesas_service, "obter_despesas", return_value=self.despesas):
            self.assertEqual(len(despesas_service.buscar_despesas("claro")), 1)
            self.assertEqual(len(despesas_service.filtrar_despesas(mes="08", ano=2026)), 1)
            self.assertEqual(len(despesas_service.filtrar_despesas(categoria="Celular")), 1)


class TesteImportacaoNubank(unittest.TestCase):
    def test_valores_e_credito_de_parcelamento(self):
        arquivo = ArquivoEmMemoria(
            "date,description,amount\n"
            "2026-08-05,Compra Mercado,120.50\n"
            "2026-08-05,Crédito de parcelamento de compra,-20.00\n"
            "2026-08-05,Pagamento recebido,-100.50\n"
        )
        compras = ler_csv_fatura(arquivo, "2026-08")
        self.assertEqual(len(compras), 2)
        self.assertEqual(sum(compra["valor_parcela"] for compra in compras), 100.50)
        self.assertEqual(_valor_csv("2.800,00"), 2800.0)
        self.assertEqual(_valor_csv("-113.50"), -113.50)


class TesteImportacaoMercadoPago(unittest.TestCase):
    def test_leitura_de_parcelas_no_texto_ocr(self):
        texto = "Empréstimo pessoal R$ 182,61\nSolicitado em 2 de abril · Parcela 5 de 6"
        compras = _compras_do_texto(texto, "2026-08")
        self.assertEqual(len(compras), 1)
        self.assertEqual(compras[0]["descricao"], "Empréstimo pessoal")
        self.assertEqual(compras[0]["valor_parcela"], 182.61)
        self.assertEqual((compras[0]["parcela_atual"], compras[0]["parcelas"]), (5, 6))


class TesteRegrasDeAcesso(unittest.TestCase):
    def test_padrao_de_usuario_e_senha_forte(self):
        self.assertTrue(_validar_usuario("nome.sobrenome")[0])
        self.assertFalse(_validar_usuario("Nome Sobrenome")[0])
        self.assertTrue(_validar_senha("SenhaForte#12")[0])
        self.assertFalse(_validar_senha("senhafraca")[0])


class TesteBancoTemporario(unittest.TestCase):
    def setUp(self):
        import database.db as db

        self.db = db
        self.arquivo_temporario = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.arquivo_temporario.close()
        os.unlink(self.arquivo_temporario.name)
        self.db_file_original = db.DB_FILE
        self.backup_original = db.criar_backup_diario
        self.protecao_original = db.proteger_dados_windows
        self.usuario_original = db._usuario_atual
        db.DB_FILE = Path(self.arquivo_temporario.name)
        db.criar_backup_diario = lambda: None
        db.proteger_dados_windows = lambda: True
        db._usuario_atual = lambda: 1
        db.criar_banco()
        conn = db.conectar()
        conn.execute("INSERT INTO usuarios(id,nome,usuario,senha_hash) VALUES(1,'Teste','teste.usuario','hash')")
        conn.execute("INSERT INTO cartoes(id,nome,banco,bandeira,limite,fechamento,vencimento,usuario_id) VALUES(1,'Nubank','Nubank','Mastercard',1000,1,10,1)")
        conn.commit()
        conn.close()

    def tearDown(self):
        self.db.DB_FILE = self.db_file_original
        self.db.criar_backup_diario = self.backup_original
        self.db.proteger_dados_windows = self.protecao_original
        self.db._usuario_atual = self.usuario_original
        if os.path.exists(self.arquivo_temporario.name):
            os.unlink(self.arquivo_temporario.name)

    def test_total_oficial_da_fatura_e_remocao(self):
        self.db.adicionar_compra_cartao(1, "2026-08-05", "Compra teste", "Outros", 100, 1, competencia="2026-08")
        self.db.salvar_resumo_fatura(1, "2026-08", 280, "Nubank")
        self.assertEqual(self.db.fatura_cartao(1, "2026-08"), 280.0)
        self.assertEqual(self.db.remover_faturas_cartao(1, "2026-08"), 1)
        self.assertEqual(self.db.fatura_cartao(1, "2026-08"), 0.0)
        self.assertIsNone(self.db.obter_resumo_fatura(1, "2026-08"))

    def test_recorrencia_nao_duplica_no_mes(self):
        self.db.adicionar_recorrencia("Despesa", "Celular", "Fatura Claro", 72, 5)
        self.assertEqual(self.db.gerar_recorrencias("2026-08"), 1)
        self.assertEqual(self.db.gerar_recorrencias("2026-08"), 0)
        despesas = self.db.listar_despesas()
        self.assertEqual(len(despesas), 1)
        self.assertEqual(despesas[0]["data"], "2026-08-05")


if __name__ == "__main__":
    unittest.main()
