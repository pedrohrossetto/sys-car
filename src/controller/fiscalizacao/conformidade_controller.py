from controller.erros import devolve_erro
from controller.fiscalizacao.propriedades import buscar_propriedade, listar_propriedades
from model.fiscalizacao.declaracao import Declaracao
from model.fiscalizacao.embargo import Embargo
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento
from model.fiscalizacao.resultado_analise import analisar
from model.fiscalizacao.regras import data_iso, texto_obrigatorio
from model.fiscalizacao.status import StatusAlerta
from model.fiscalizacao.unidade_competente import UnidadeCompetente


class ConformidadeController:
    """Embargos e declarações de conformidade ambiental."""

    # ---------------- embargos ----------------
    def registros_confirmados(self, propriedade_id):
        return [
            r for r in RegistroDesmatamento.listar_por_propriedade(propriedade_id)
            if r.status == StatusAlerta.CONFIRMADO.value
        ]

    @devolve_erro
    def embargar(self, propriedade_id, unidade_id, registro_id, motivo):
        if not buscar_propriedade(propriedade_id):
            return None, "Propriedade não encontrada."
        if unidade_id is None or not UnidadeCompetente.buscar_por_id(unidade_id):
            return None, "Unidade não encontrada."
        registro = RegistroDesmatamento.buscar_por_id(registro_id) if registro_id else None
        if (not registro or registro.propriedade_id != int(propriedade_id)
                or registro.status != StatusAlerta.CONFIRMADO.value):
            return None, "Embargo exige um alerta CONFIRMADO desta propriedade."
        if Embargo.buscar_ativo(propriedade_id):
            return None, "Esta propriedade já está embargada."
        try:
            motivo = texto_obrigatorio(motivo, "Motivo")
        except ValueError as erro:
            return None, str(erro)
        embargo = Embargo(int(propriedade_id), unidade_id, registro.id, data_iso(), motivo)
        embargo.salvar()
        return embargo, None

    @devolve_erro
    def levantar_embargo(self, embargo_id):
        embargo = Embargo.buscar_por_id(embargo_id)
        if not embargo:
            return None, "Embargo não encontrado."
        if not embargo.ativo:
            return None, "Este embargo já foi levantado."
        embargo.ativo = 0
        embargo.salvar()
        return embargo, None

    @devolve_erro
    def alterar_motivo(self, embargo_id, motivo):
        """Único campo editável do embargo (ADR-F13). Vale para embargo ativo ou levantado."""
        embargo = Embargo.buscar_por_id(embargo_id) if embargo_id is not None else None
        if not embargo:
            return None, "Embargo não encontrado."
        try:
            embargo.motivo = texto_obrigatorio(motivo, "Motivo")
        except ValueError as erro:
            return None, str(erro)
        embargo.salvar()
        return embargo, None

    def buscar_embargo(self, embargo_id):
        return Embargo.buscar_por_id(embargo_id)

    def listar_embargos(self):
        return Embargo.listar_todos()

    # ---------------- declarações ----------------
    @devolve_erro
    def solicitar_declaracao(self, propriedade_id):
        """Sempre grava o pedido. Devolve (Declaracao, None); o resultado pode ser NEGADA."""
        propriedade = buscar_propriedade(propriedade_id)
        if not propriedade:
            return None, "Propriedade não encontrada."
        impedimentos = [
            f"alerta {r.id} {r.status}"
            for r in RegistroDesmatamento.listar_por_propriedade(propriedade.id)
            if r.estado.BLOQUEIA_CONFORMIDADE
        ]
        embargo = Embargo.buscar_ativo(propriedade.id)
        if embargo:
            impedimentos.append(f"embargo {embargo.id} ativo")
        # Factory Method (ADR-F11): o resultado da análise cria a declaração certa.
        declaracao = analisar(impedimentos).criar_declaracao(propriedade.id, data_iso())
        declaracao.salvar()
        return declaracao, None

    def listar_declaracoes(self):
        return Declaracao.listar_todas()

    @devolve_erro
    def texto_declaracao(self, declaracao_id):
        declaracao = Declaracao.buscar_por_id(declaracao_id)
        if not declaracao:
            return None, "Declaração não encontrada."
        propriedade = buscar_propriedade(declaracao.propriedade_id)
        nome = propriedade.nome if propriedade else f"#{declaracao.propriedade_id}"
        linhas = [
            "SYS-CAR - DECLARAÇÃO DE CONFORMIDADE AMBIENTAL",
            "",
            f"Número: {declaracao.id}",
            f"Data: {declaracao.data}",
            f"Propriedade: {nome} (#{declaracao.propriedade_id})",
            f"Resultado: {declaracao.resultado}",
        ]
        if declaracao.emitida:
            linhas.append(
                "Não há alertas de desmatamento pendentes ou confirmados nem embargo ativo."
            )
        else:
            linhas.append(f"Motivo: {declaracao.motivo}")
        return "\n".join(linhas) + "\n", None

    def listar_propriedades(self):
        return listar_propriedades()
