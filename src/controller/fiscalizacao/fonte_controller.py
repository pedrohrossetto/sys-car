from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento
from model.fiscalizacao.regras import (
    cpf_formato_valido, email_valido, normalizar_cpf, texto_obrigatorio,
)
from model.fiscalizacao.satelite import Satelite
from model.fiscalizacao.usuario import Usuario


class FonteController:
    """Cadastro das fontes de detecção: satélites e usuários denunciantes."""

    # ---------------- satélites ----------------
    def criar_satelite(self, nome, entidade_responsavel=None):
        try:
            satelite = Satelite(
                texto_obrigatorio(nome, "Nome"), (entidade_responsavel or "").strip() or None
            )
        except ValueError as erro:
            return None, str(erro)
        satelite.salvar()
        return satelite, None

    def atualizar_satelite(self, id, nome, entidade_responsavel=None):
        satelite = Satelite.buscar_por_id(id)
        if not satelite:
            return None, "Satélite não encontrado."
        try:
            satelite.nome = texto_obrigatorio(nome, "Nome")
        except ValueError as erro:
            return None, str(erro)
        satelite.entidade_responsavel = (entidade_responsavel or "").strip() or None
        satelite.salvar()
        return satelite, None

    def excluir_satelite(self, id):
        satelite = Satelite.buscar_por_id(id)
        if not satelite:
            return None, "Satélite não encontrado."
        if RegistroDesmatamento.existe_da_fonte("satelite_id", id):
            return None, "Este satélite tem alertas registrados e não pode ser excluído."
        satelite.deletar()
        return True, None

    def buscar_satelite(self, id):
        return Satelite.buscar_por_id(id)

    def listar_satelites(self):
        return Satelite.listar_todos()

    # ---------------- usuários ----------------
    def criar_usuario(self, nome, cpf, email):
        dados, erro = self._validar_usuario(nome, cpf, email)
        if erro:
            return None, erro
        usuario = Usuario(*dados)
        usuario.salvar()
        return usuario, None

    def atualizar_usuario(self, id, nome, cpf, email):
        usuario = Usuario.buscar_por_id(id)
        if not usuario:
            return None, "Usuário não encontrado."
        dados, erro = self._validar_usuario(nome, cpf, email, id_atual=usuario.id)
        if erro:
            return None, erro
        usuario.nome, usuario.cpf, usuario.email = dados
        usuario.salvar()
        return usuario, None

    def excluir_usuario(self, id):
        usuario = Usuario.buscar_por_id(id)
        if not usuario:
            return None, "Usuário não encontrado."
        if RegistroDesmatamento.existe_da_fonte("usuario_id", id):
            return None, "Este usuário tem denúncias registradas e não pode ser excluído."
        usuario.deletar()
        return True, None

    def buscar_usuario(self, id):
        return Usuario.buscar_por_id(id)

    def listar_usuarios(self):
        return Usuario.listar_todos()

    def email_valido(self, email):
        return email_valido(email)

    def _validar_usuario(self, nome, cpf, email, id_atual=None):
        try:
            nome = texto_obrigatorio(nome, "Nome")
        except ValueError as erro:
            return None, str(erro)
        cpf = normalizar_cpf(cpf)
        if not cpf_formato_valido(cpf):
            return None, "CPF deve ter 11 dígitos."
        if not email_valido(email):
            return None, "E-mail inválido."
        existente = Usuario.buscar_por_cpf(cpf)
        if existente and existente.id != id_atual:
            return None, "CPF já cadastrado para outro usuário."
        return (nome, cpf, email.strip()), None
