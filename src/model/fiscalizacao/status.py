"""Status do alerta de desmatamento (padrão State).

Cada estado é uma classe que sabe para quais estados pode ir.
O registro delega a mudança de status ao seu estado atual, então
não existe if/elif de transições espalhado pelo código.

    PENDENTE --> CONFIRMADO --> RESOLVIDO
        \\--> CANCELADO
"""
from enum import Enum


class StatusAlerta(str, Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADO = "CONFIRMADO"
    RESOLVIDO = "RESOLVIDO"
    CANCELADO = "CANCELADO"


class TransicaoInvalida(ValueError):
    pass


class EstadoAlerta:
    STATUS = None
    PROXIMOS = ()
    # True se um alerta neste estado impede a declaração de conformidade.
    BLOQUEIA_CONFORMIDADE = False

    @property
    def finalizado(self):
        return not self.PROXIMOS

    def ir_para(self, novo_status):
        novo = _converter(novo_status)
        if novo not in self.PROXIMOS:
            raise TransicaoInvalida(
                f"Não é possível mudar de {self.STATUS.value} para {novo.value}."
            )
        return estado_de(novo)


class Pendente(EstadoAlerta):
    STATUS = StatusAlerta.PENDENTE
    PROXIMOS = (StatusAlerta.CONFIRMADO, StatusAlerta.CANCELADO)
    BLOQUEIA_CONFORMIDADE = True


class Confirmado(EstadoAlerta):
    STATUS = StatusAlerta.CONFIRMADO
    PROXIMOS = (StatusAlerta.RESOLVIDO,)
    BLOQUEIA_CONFORMIDADE = True


class Resolvido(EstadoAlerta):
    STATUS = StatusAlerta.RESOLVIDO


class Cancelado(EstadoAlerta):
    STATUS = StatusAlerta.CANCELADO


_ESTADOS = {classe.STATUS: classe() for classe in (Pendente, Confirmado, Resolvido, Cancelado)}


def _converter(status):
    try:
        return StatusAlerta(status)
    except ValueError:
        raise TransicaoInvalida(f"Status desconhecido: {status}.") from None


def estado_de(status):
    """Devolve o objeto de estado correspondente ao status (texto ou enum)."""
    return _ESTADOS[_converter(status)]
