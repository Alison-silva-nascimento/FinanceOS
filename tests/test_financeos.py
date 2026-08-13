"""Testes de regressão dos fluxos financeiros mais sensíveis do FinanceOS."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Diretório exclusivo por execução: o banco aplica ACLs no Windows e um
# diretório reaproveitado pode ficar indisponível para o processo seguinte.
# A suíte jamais deve herdar a conexão remota usada por uma migração manual.
os.environ.pop("DATABASE_URL", None)

BOOTSTRAP_DIR = Path(tempfile.mkdtemp(prefix="financeos-test-"))
os.environ["FINANCEOS_DB_FILE"] = str(BOOTSTRAP_DIR / "bootstrap.db")
os.environ["FINANCEOS_BACKUP_DIR"] = str(BOOTSTRAP_DIR / "backups")

from services import despesas_service, receitas_service
from auth import _validar_senha, _validar_usuario
from utils.mercado_pago_fatura import _compras_do_texto
from utils.nubank_fatura import _valor_csv, ler_csv_fatura
from utils.outros_fatura import ler_csv_fatura as ler_csv_outros


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


class TesteImportacaoOutros(unittest.TestCase):
    def test_leitura_csv_picpay(self):
        arquivo = ArquivoEmMemoria(
            "Data da compra;Estabelecimento;Valor da compra\n"
            "05/08/2026;Mercado Central;R$ 120,50\n"
            "06/08/2026;Loja Online 2/3;89,90\n"
        )
        compras = ler_csv_outros(arquivo, "2026-08")
        self.assertEqual(len(compras), 2)
        self.assertEqual(compras[0]["data"], "2026-08-05")
        self.assertEqual(compras[1]["valor_parcela"], 89.90)
        self.assertEqual((compras[1]["parcela_atual"], compras[1]["parcelas"]), (2, 3))

    def test_extrato_picpay_mostra_apenas_movimentacoes_com_cartao(self):
        arquivo = ArquivoEmMemoria(
            'data,hora,tipo,"origem / destino",valor,"forma de pagamento"\n'
            '2026-07-26,20:58,"Pix enviado","Pessoa A","−R$ 50,00","Com saldo"\n'
            '2026-07-26,17:18,"Pix enviado","Pessoa B","−R$ 20,50","Com saldo + cartão"\n'
            '2026-07-25,15:25,"Empréstimo contratado","Crédito","+R$ 800,00",\n'
        )
        compras = ler_csv_outros(arquivo, "2026-08")
        self.assertEqual(len(compras), 1)
        self.assertEqual(compras[0]["valor_parcela"], 20.50)
        self.assertFalse(compras[0]["incluir"])
        self.assertIn("saldo + cartão", compras[0]["observacao"])


class TesteRegrasDeAcesso(unittest.TestCase):
    def test_padrao_de_usuario_e_senha_forte(self):
        self.assertTrue(_validar_usuario("nome.sobrenome")[0])
        self.assertFalse(_validar_usuario("Nome Sobrenome")[0])
        self.assertTrue(_validar_senha("SenhaForte#12")[0])
        self.assertFalse(_validar_senha("senhafraca")[0])

    def test_administrador_nao_tem_identidade_padrao_publica(self):
        import config

        self.assertNotEqual(config.ADMIN_USER, "alison.nascimento")


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
        self.db.adicionar_compra_cartao(1, "2026-08-08", "Compra manual", "Outros", 120, 2, competencia="2026-08")
        self.assertEqual(self.db.fatura_cartao(1, "2026-08"), 340.0)
        manual = next(item for item in self.db.listar_compras_cartao(1) if item["descricao"] == "Compra manual")
        self.assertTrue(self.db.editar_compra_cartao(manual["id"], "2026-08-09", "Compra corrigida", "Compras", 150, 3))
        manual_editada = next(item for item in self.db.listar_compras_cartao(1) if item["id"] == manual["id"])
        self.assertEqual(manual_editada["data"], "2026-08-09")
        self.assertEqual(manual_editada["descricao"], "Compra corrigida")
        self.assertEqual(self.db.fatura_cartao(1, "2026-08"), 330.0)
        self.db.adicionar_compra_cartao(1, "2026-08-08", "Compra importada", "Outros", 30, 1, competencia="2026-08", importacao_id=999)
        self.assertEqual(self.db.fatura_cartao(1, "2026-08"), 330.0)
        importada = next(item for item in self.db.listar_compras_cartao(1) if item["descricao"] == "Compra importada")
        with self.assertRaises(ValueError):
            self.db.editar_compra_cartao(importada["id"], "2026-08-09", "Alterada", "Outros", 40, 1)
        self.assertEqual(self.db.remover_faturas_cartao(1, "2026-08"), 3)
        self.assertEqual(self.db.fatura_cartao(1, "2026-08"), 0.0)
        self.assertIsNone(self.db.obter_resumo_fatura(1, "2026-08"))

    def test_edicao_de_credito_manual_aceita_valor_negativo(self):
        self.db.adicionar_compra_cartao(1, "2026-08-05", "Crédito", "Outros", -30, 1, competencia="2026-08")
        self.db.salvar_resumo_fatura(1, "2026-08", 100, "Manual")
        credito = next(item for item in self.db.listar_compras_cartao(1) if item["descricao"] == "Crédito")
        self.assertTrue(self.db.editar_compra_cartao(credito["id"], "2026-08-06", "Crédito corrigido", "Outros", -45, 1))
        self.assertEqual(self.db.fatura_cartao(1, "2026-08"), 85.0)
        with self.assertRaises(ValueError):
            self.db.editar_compra_cartao(credito["id"], "2026-08-06", "Crédito corrigido", "Outros", 0, 1)

    def test_pagamento_quita_competencia_e_nao_debita_duas_vezes(self):
        conn = self.db.conectar()
        conn.execute(
            "INSERT INTO bancos(id,nome,banco,tipo,saldo,usuario_id) VALUES(1,'Conta','Banco','Corrente',1000,1)"
        )
        conn.commit()
        conn.close()
        # A compra ocorreu em julho, mas pertence à fatura com competência agosto.
        self.db.adicionar_compra_cartao(
            1, "2026-07-25", "Compra do ciclo", "Outros", 100, 1,
            competencia="2026-08",
        )
        self.assertEqual(self.db.pagar_fatura(1, "2026-08", 1, 100, "2026-08-10"), 1)
        compra = self.db.listar_compras_cartao(1)[0]
        self.assertEqual(compra["paga"], 1)
        self.assertEqual(self.db.obter_banco(1)["saldo"], 900)
        self.assertEqual(self.db.fatura_cartao(1, "2026-08"), 0)
        with self.assertRaisesRegex(ValueError, "já foi paga"):
            self.db.pagar_fatura(1, "2026-08", 1, 100, "2026-08-10")
        self.assertEqual(self.db.obter_banco(1)["saldo"], 900)

    def test_migracao_soma_resumos_e_ignora_operacao_sem_compras(self):
        conn = self.db.conectar()
        conn.execute(
            "INSERT INTO cartoes(id,nome,banco,bandeira,limite,fechamento,vencimento,usuario_id) "
            "VALUES(2,'Destino','Banco','Visa',1000,1,10,1)"
        )
        conn.commit()
        conn.close()
        self.db.adicionar_compra_cartao(
            1, "2026-08-20", "Compra a migrar", "Outros", 100, 1,
            competencia="2026-09",
        )
        self.db.salvar_resumo_fatura(1, "2026-09", 100, "Origem")
        self.db.salvar_resumo_fatura(2, "2026-09", 200, "Destino")
        self.assertEqual(self.db.migrar_compras_cartao(1, 2, "2026-09"), 1)
        self.assertEqual(self.db.obter_resumo_fatura(2, "2026-09")["total_a_pagar"], 300)
        self.assertIsNone(self.db.obter_resumo_fatura(1, "2026-09"))

        self.db.salvar_resumo_fatura(1, "2026-10", 50, "Origem")
        self.db.salvar_resumo_fatura(2, "2026-10", 80, "Destino")
        self.assertEqual(self.db.migrar_compras_cartao(1, 2, "2026-10"), 0)
        self.assertEqual(self.db.obter_resumo_fatura(1, "2026-10")["total_a_pagar"], 50)
        self.assertEqual(self.db.obter_resumo_fatura(2, "2026-10")["total_a_pagar"], 80)

    def test_recorrencia_nao_duplica_no_mes(self):
        self.db.adicionar_recorrencia("Despesa", "Celular", "Fatura Claro", 72, 5)
        self.assertEqual(self.db.gerar_recorrencias("2026-08"), 1)
        self.assertEqual(self.db.gerar_recorrencias("2026-08"), 0)
        despesas = self.db.listar_despesas()
        self.assertEqual(len(despesas), 1)
        self.assertEqual(despesas[0]["data"], "2026-08-05")

    def test_lote_de_importacao_pode_ser_desfeito(self):
        lote = self.db.iniciar_importacao("fatura", "PicPay", competencia="2026-08", cartao_id=1)
        self.db.adicionar_compra_cartao(1, "2026-08-05", "Compra", "Outros", 90, 3, 1, "2026-08", lote)
        self.db.finalizar_importacao(lote, 1)
        self.assertEqual(len(self.db.listar_compras_cartao(1)), 1)
        self.assertEqual(self.db.desfazer_importacao(lote), 1)
        self.assertEqual(len(self.db.listar_compras_cartao(1)), 0)

    def test_regras_de_categoria_e_parcelas_futuras(self):
        self.db.salvar_regra_categoria("ifood", "Alimentação")
        self.assertEqual(self.db.categorizar_por_regras("IFOOD RESTAURANTE"), "Alimentação")
        self.db.adicionar_compra_cartao(1, "2026-08-05", "Notebook", "Compras", 300, 3, 1, "2026-08")
        projecao = self.db.projecao_parcelas()
        self.assertEqual([x["competencia"] for x in projecao], ["2026-08", "2026-09", "2026-10"])
        self.assertEqual(sum(x["valor"] for x in projecao), 300.0)

    def test_extrato_nao_duplica_e_bloqueia_fechamento_pendente(self):
        itens = [{"data":"2026-08-05","descricao":"Mercado","valor":-50.0}]
        self.assertEqual(self.db.importar_extrato(itens, "Teste"), 1)
        self.assertEqual(self.db.importar_extrato(itens, "Teste"), 0)
        with self.assertRaises(ValueError):
            self.db.fechar_mes("2026-08")
        conciliacao = self.db.listar_conciliacoes()[0]
        self.db.marcar_conciliado(conciliacao["id"])
        self.assertEqual(self.db.fechar_mes("2026-08")["pendencias"], 0)


if __name__ == "__main__":
    unittest.main()
