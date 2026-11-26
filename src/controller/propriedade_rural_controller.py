from controller.erros import devolve_erro
from model.geometria import Poligono
from model.propriedade_rural import PropriedadeRural
from model.proprietario import Proprietario


class PropriedadeRuralController:
    # Mesmo padrão (resultado, erro) dos outros controllers.
    # poligono: lista de pares (lat, lon) ou texto 'lat,lon;lat,lon;...' (ADR-C05).
    @devolve_erro
    def criar(self, nome, proprietario_id, cadastro_publico=None, poligono=None):
        dados, erro = self._validar(nome, proprietario_id, cadastro_publico, poligono)
        if erro:
            return None, erro
        propriedade = PropriedadeRural(**dados)
        propriedade.salvar()
        return propriedade, None

    def buscar_por_id(self, id):
        return PropriedadeRural.buscar_por_id(id)

    def listar(self):
        return PropriedadeRural.listar_todos()

    def listar_areas(self, exceto_id=None):
        """[(id, nome, Poligono)] das propriedades com área, para o mapa."""
        return [(p.id, p.nome, p.area) for p in PropriedadeRural.listar_todos()
                if p.poligono and p.id != exceto_id]

    @devolve_erro
    def atualizar(self, id, nome, proprietario_id, cadastro_publico=None, poligono=None):
        propriedade = PropriedadeRural.buscar_por_id(id)
        if not propriedade:
            return None, "Propriedade não encontrada."
        dados, erro = self._validar(nome, proprietario_id, cadastro_publico, poligono,
                                    id_atual=propriedade.id)
        if erro:
            return None, erro
        for campo, valor in dados.items():
            setattr(propriedade, campo, valor)
        propriedade.salvar()
        return propriedade, None

    @devolve_erro
    def excluir(self, id):
        propriedade = PropriedadeRural.buscar_por_id(id)
        if not propriedade:
            return None, "Propriedade não encontrada."
        propriedade.deletar()
        return True, None

    def banco_desatualizado(self):
        return PropriedadeRural.schema_desatualizado()

    def _validar(self, nome, proprietario_id, cadastro_publico, poligono, id_atual=None):
        nome = (nome or "").strip()
        if not nome:
            return None, "Nome é obrigatório."
        if proprietario_id is None or not Proprietario.buscar_por_id(proprietario_id):
            return None, "Proprietário não encontrado."
        area, erro = self._validar_area(poligono, id_atual)
        if erro:
            return None, erro
        cadastro_publico = (cadastro_publico or "").strip() or None
        return {
            "nome": nome,
            "proprietario_id": int(proprietario_id),
            "cadastro_publico": cadastro_publico,
            "poligono": area.para_texto(),
        }, None

    def _validar_area(self, poligono, id_atual):
        """Área obrigatória, válida e sem sobreposição com outra propriedade."""
        vazio = poligono is None or (isinstance(poligono, str) and not poligono.strip()) \
            or (not isinstance(poligono, str) and len(poligono) == 0)
        if vazio:
            return None, "Desenhe a área da propriedade no mapa."
        try:
            area = Poligono.de_texto(poligono) if isinstance(poligono, str) else Poligono(poligono)
        except ValueError as erro:
            return None, str(erro)
        for outro_id, outro_nome, outra_area in self.listar_areas(exceto_id=id_atual):
            if area.sobrepoe(outra_area):
                return None, f"A área se sobrepõe à da propriedade {outro_nome} (#{outro_id})."
        return area, None
