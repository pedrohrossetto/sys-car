import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.fiscalizacao.fonte_controller import FonteController
from database import database
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento
from model.fiscalizacao.satelite import Satelite
from model.fiscalizacao.usuario import Usuario
from test_fiscalizacao_apoio import BancoTemporario


class TestFactoryMethod(BancoTemporario):
    def test_satelite_cria_registro_com_a_propria_origem(self):
        satelite = Satelite("Landsat")
        satelite.salvar()
        registro = satelite.detectar_desmatamento(self.propriedade_id, "Corte", 1.0, 2.0, "2026-01-01")
        self.assertIsInstance(registro, RegistroDesmatamento)
        self.assertEqual((registro.satelite_id, registro.usuario_id, registro.status),
                         (satelite.id, None, "PENDENTE"))
        self.assertIsNone(registro.id)

    def test_usuario_exige_evidencia(self):
        usuario = Usuario("Joana", "52998224725", "a@b.com")
        usuario.salvar()
        with self.assertRaisesRegex(ValueError, "pelo menos uma evidência"):
            usuario.reportar_desmatamento(self.propriedade_id, "x", 0, 0, "2026-01-01", [])
        registro = usuario.reportar_desmatamento(
            self.propriedade_id, "x", 0, 0, "2026-01-01", [("Foto", "l")])
        self.assertEqual((registro.usuario_id, registro.satelite_id), (usuario.id, None))

    def test_registro_salvo_e_state(self):
        satelite = Satelite("Landsat")
        satelite.salvar()
        registro = satelite.detectar_desmatamento(self.propriedade_id, "Corte", 1.0, 2.0, "2026-01-01")
        registro.salvar()
        registro.mudar_status("CONFIRMADO")
        registro.salvar()
        salvo = RegistroDesmatamento.buscar_por_id(registro.id)
        self.assertEqual((salvo.status, salvo.latitude), ("CONFIRMADO", 1.0))
        self.assertEqual([r.id for r in RegistroDesmatamento.listar_por_propriedade(self.propriedade_id)],
                         [registro.id])
        self.assertTrue(RegistroDesmatamento.existe_da_fonte("satelite_id", satelite.id))

    def test_check_exige_exatamente_uma_origem(self):
        satelite = Satelite("Landsat")
        satelite.salvar()
        usuario = Usuario("Joana", "52998224725", "a@b.com")
        usuario.salvar()
        conn = database.get_connection()
        try:
            for sat, usu in ((None, None), (satelite.id, usuario.id)):
                with self.subTest(sat=sat, usu=usu):
                    with self.assertRaises(sqlite3.IntegrityError):
                        conn.execute(
                            "INSERT INTO registros_desmatamento (descricao, data, status, latitude, "
                            "longitude, propriedade_id, satelite_id, usuario_id) "
                            "VALUES ('x', '2026-01-01', 'PENDENTE', 0, 0, ?, ?, ?)",
                            (self.propriedade_id, sat, usu))
        finally:
            conn.close()


class TestFonteController(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.fontes = FonteController()

    def test_usuario_valido_guarda_cpf_sem_mascara(self):
        usuario, erro = self.fontes.criar_usuario("Joana", "012.345.678-90", " joana@ex.com ")
        self.assertIsNone(erro)
        salvo = self.fontes.buscar_usuario(usuario.id)
        self.assertEqual((salvo.cpf, salvo.email), ("01234567890", "joana@ex.com"))

    def test_usuario_invalido(self):
        self.assertEqual(self.fontes.criar_usuario("Joana", "123", "a@b.com")[1], "CPF deve ter 11 dígitos.")
        self.assertEqual(self.fontes.criar_usuario("Joana", "52998224725", "joana")[1], "E-mail inválido.")
        self.assertEqual(self.fontes.criar_usuario("", "52998224725", "a@b.com")[1], "Preencha o campo Nome.")

    def test_cpf_duplicado(self):
        self.fontes.criar_usuario("Joana", "52998224725", "a@b.com")
        self.assertEqual(self.fontes.criar_usuario("Outra", "529.982.247-25", "c@d.com")[1],
                         "CPF já cadastrado para outro usuário.")

    def test_atualizar_usuario_mantendo_cpf(self):
        usuario, _ = self.fontes.criar_usuario("Joana", "52998224725", "a@b.com")
        self.assertIsNone(self.fontes.atualizar_usuario(usuario.id, "Joana S.", "52998224725", "a@b.com")[1])
        self.assertEqual(self.fontes.buscar_usuario(usuario.id).nome, "Joana S.")

    def test_satelite_crud(self):
        satelite, _ = self.fontes.criar_satelite("Landsat", " ")
        self.assertIsNone(satelite.entidade_responsavel)
        self.fontes.atualizar_satelite(satelite.id, "Landsat 9", "NASA")
        self.assertEqual(self.fontes.buscar_satelite(satelite.id).nome, "Landsat 9")
        self.assertEqual(self.fontes.excluir_satelite(satelite.id), (True, None))
        self.assertEqual(self.fontes.excluir_satelite(satelite.id)[1], "Satélite não encontrado.")

    def test_exclusao_de_fonte_com_registros_e_bloqueada(self):
        satelite, _ = self.fontes.criar_satelite("Landsat")
        usuario, _ = self.fontes.criar_usuario("Joana", "52998224725", "a@b.com")
        Satelite.buscar_por_id(satelite.id).detectar_desmatamento(
            self.propriedade_id, "x", 0, 0, "2026-01-01").salvar()
        Usuario.buscar_por_id(usuario.id).reportar_desmatamento(
            self.propriedade_id, "y", 0, 0, "2026-01-01", [("Foto", "l")]).salvar()
        self.assertEqual(self.fontes.excluir_satelite(satelite.id)[1],
                         "Este satélite tem alertas registrados e não pode ser excluído.")
        self.assertEqual(self.fontes.excluir_usuario(usuario.id)[1],
                         "Este usuário tem denúncias registradas e não pode ser excluído.")
        self.assertEqual((self.contar("satelites"), self.contar("usuarios")), (1, 1))


if __name__ == "__main__":
    unittest.main()
