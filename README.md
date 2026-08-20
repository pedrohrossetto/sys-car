# Sistema de Cadastro Ambiental Rural (sys-car)

## Detalhes

- Instituição:
  - Instituto Federal Sul-Riograndense de Passo Fundo
- Disciplina:
  - Linguagem de Programação Orientada a Objetos - 4° Semestre
- Docente:
  - Leonardo Deliyannis Constantin

## Descrição

- Proprietários poderão registrar suas propriedades rurais, declarando os limites das propriedades sobre um mapa interativo.
- Poderão requisitar declarações de conformidade ambiental, onde será buscado em uma base de alertas de desmatamento se há algum alerta, se não houver, será emitido.
- As propriedades registradas poderão ser embargadas por autoridades competentes se for comprovado desmatamento ilegal

## Integrantes:

- Pedro Henrique Carteli Rossetto
  - Desenvolvedor
  - @pedrohrossetto
- Matheus Pastore Polese
  - Desenvolvedor
  - @MatheusPolese
- Victor Hugo Andreon
  - Desenvolvedor
  - @VictorAndreon
- Eduardo Milani
  - Desenvolvedor
  - @EduardoMilani8

## Diagrama do Modelo Conceitual

```mermaid
classDiagram
direction TB

    class SATELITE {
        -INT id
        -STRING nome
        -STRING entidade_responsavel
        +detectarDesmatamento()
    }

    class USUARIO {
        -INT id
        -STRING nome
        -STRING cpf
        -STRING email
        +reportarDesmatamento(evidencia)
    }

    class REGISTRO_DESMATAMENTO {
        -INT id
        -STRING descricao
        -DATE data
        -STATUS_ALERTA status
        +enviarNotificacao(detalhes)
        +atualizarStatus(status)
    }

    class LOCALIZACAO {
        -FLOAT latitude
        -FLOAT longitude
        -FLOAT altitude
        -GEOMETRY poligono_geometria
    }

    class EVIDENCIA {
        -INT id
        -STRING tipo
        -STRING link
        -DATE data
    }

    class NOTIFICACAO {
        -INT id
        -DATE data
        -STRING status
        -STRING mensagem
        +enviarNotificacao()
    }

    class STATUS_ALERTA {
        <<enumeration>>
        PENDENTE
        CONFIRMADO
        RESOLVIDO
        CANCELADO
    }

    class UNIDADE_COMPETENTE {
        -INT id
        -STRING nome
        -STRING tipo_unidade_orgao
        -STRING contato
        +examinarAlerta(id_alerta)
        +embargarPropriedade(id_propriedade)
    }

    class PROPRIEDADE_RURAL {
        -INT id
        -STRING nome
        -STRING cadastro_pub
        +gerarDeclaracaoConformidade()
    }

    class PROPRIETARIO {
        -INT id
        -STRING nome
        -STRING cpf
        -STRING cnpj
        +registrarPropriedade()
    }

    %% Relacionamentos
    SATELITE "1" --> "0..*" REGISTRO_DESMATAMENTO : registra
    USUARIO "1" --> "0..*" REGISTRO_DESMATAMENTO : registra
    REGISTRO_DESMATAMENTO "1" *-- "1" LOCALIZACAO : possui
    REGISTRO_DESMATAMENTO "1" *-- "0..*" EVIDENCIA : contem
    REGISTRO_DESMATAMENTO "1" --> "0..*" NOTIFICACAO : gera
    REGISTRO_DESMATAMENTO ..> STATUS_ALERTA : utiliza

    NOTIFICACAO "*" --> "1" UNIDADE_COMPETENTE : destinada
    UNIDADE_COMPETENTE "0..*" --> "0..*" PROPRIEDADE_RURAL : embarga

    PROPRIEDADE_RURAL "1" *-- "1" LOCALIZACAO : possui
    PROPRIETARIO "1" --> "1..*" PROPRIEDADE_RURAL : possui
```
