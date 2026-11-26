"""Dados de exemplo para a demonstração do SYS-CAR.

Uso, a partir da pasta src:

    python3 dados_exemplo.py

O script só grava num banco vazio. Se o banco já tem proprietários,
ele não faz nada, para não misturar os dados de exemplo com dados reais.

Os dados mostram todos os casos do sistema:
  - três propriedades vizinhas, com proprietário PF e PJ;
  - uma propriedade EMBARGADA, uma COM ALERTAS EM ABERTO e uma REGULAR;
  - um alerta fora de todas as áreas (sem propriedade);
  - declarações EMITIDA e NEGADA e notificações lidas e não lidas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.fiscalizacao.alerta_controller import AlertaController
from controller.fiscalizacao.conformidade_controller import ConformidadeController
from controller.fiscalizacao.unidade_controller import UnidadeController
from controller.propriedade_rural_controller import PropriedadeRuralController
from controller.proprietario_controller import ProprietarioController
from database.database import init_db

# Três quadrados vizinhos perto de Passo Fundo (RS). Formato: "lat,lon;lat,lon;...".
AREA_SITIO = "-28.260,-52.410;-28.260,-52.400;-28.250,-52.400;-28.250,-52.410"
AREA_FAZENDA = "-28.260,-52.400;-28.260,-52.385;-28.250,-52.385;-28.250,-52.400"
AREA_CHACARA = "-28.270,-52.410;-28.270,-52.400;-28.260,-52.400;-28.260,-52.410"


class ErroDeExemplo(Exception):
    """Um controller recusou um dado de exemplo."""


def _ok(resultado):
    """Os controllers devolvem (objeto, erro). Aqui um erro é um defeito do script."""
    objeto, erro = resultado
    if erro:
        raise ErroDeExemplo(erro)
    return objeto


def banco_vazio():
    return not ProprietarioController().listar()


def popular():
    """Grava os dados de exemplo. Devolve um resumo em texto."""
    donos = ProprietarioController()
    ana = _ok(donos.criar("Ana Souza", "PF", cpf="529.982.247-25"))
    joao = _ok(donos.criar("João Pereira", "PF", cpf="012.345.678-90"))
    agro = _ok(donos.criar("Agropecuária Planalto Ltda", "PJ", cnpj="11.222.333/0001-81"))

    props = PropriedadeRuralController()
    sitio = _ok(props.criar("Sítio Boa Vista", ana.id, "RS-4314100-0001", AREA_SITIO))
    fazenda = _ok(props.criar("Fazenda Planalto", agro.id, "RS-4314100-0002", AREA_FAZENDA))
    chacara = _ok(props.criar("Chácara Santa Rita", joao.id, "RS-4314100-0003", AREA_CHACARA))

    # As unidades vêm antes dos alertas: o Observer notifica as unidades já cadastradas.
    unidades = UnidadeController()
    ibama = _ok(unidades.criar("IBAMA", "Federal", "linhaverde@ibama.gov.br"))
    _ok(unidades.criar("FEPAM", "Estadual", "fepam@fepam.rs.gov.br"))
    _ok(unidades.criar("SMAM Passo Fundo", "Municipal", "smam@pmpf.rs.gov.br"))

    alertas = AlertaController()
    conformidade = ConformidadeController()

    # Fazenda: alerta confirmado e embargo ativo -> EMBARGADA.
    corte = _ok(alertas.criar("Supressão de mata nativa na área norte", -28.2530, -52.3920, "2026-11-02"))
    _ok(alertas.mudar_status(corte.id, "CONFIRMADO"))
    _ok(conformidade.embargar(fazenda.id, ibama.id, corte.id, "Desmatamento sem autorização"))
    _ok(conformidade.solicitar_declaracao(fazenda.id))

    # Sítio: alerta pendente -> COM ALERTAS EM ABERTO.
    _ok(alertas.criar("Queimada próxima ao açude", -28.2560, -52.4050, "2026-11-10"))

    # Chácara: alerta resolvido e outro cancelado -> REGULAR, com declaração emitida.
    antigo = _ok(alertas.criar("Corte de árvores isoladas", -28.2650, -52.4060, "2026-10-15"))
    _ok(alertas.mudar_status(antigo.id, "CONFIRMADO"))
    _ok(alertas.mudar_status(antigo.id, "RESOLVIDO"))
    engano = _ok(alertas.criar("Mancha de sombra confundida com clareira", -28.2620, -52.4020, "2026-10-20"))
    _ok(alertas.mudar_status(engano.id, "CANCELADO"))
    _ok(conformidade.solicitar_declaracao(chacara.id))

    # Fora de todas as áreas: alerta sem propriedade.
    _ok(alertas.criar("Clareira em área sem cadastro", -28.2450, -52.3800, "2026-11-12"))

    # Metade das notificações já foi lida.
    notificacoes = unidades.listar_notificacoes()
    for notificacao in notificacoes[len(notificacoes) // 2:]:
        _ok(unidades.marcar_lida(notificacao.id))

    return (f"3 proprietários, 3 propriedades ({sitio.nome}, {fazenda.nome}, {chacara.nome}), "
            f"3 unidades, 5 alertas, 1 embargo, 2 declarações e {len(notificacoes)} notificações.")


def main():
    init_db()
    if not banco_vazio():
        print("O banco já tem dados. Os dados de exemplo só entram num banco vazio.")
        print("Para recomeçar, apague o arquivo data/syscar.db e rode este script de novo.")
        return 1
    print("Dados de exemplo gravados:", popular())
    return 0


if __name__ == "__main__":
    sys.exit(main())
