# Fiscalização UML diagrams

Portuguese version: [diagramas.pt-br.md](diagramas.pt-br.md). The names of the classes, methods and tables are in Portuguese, as in the code.

## Use cases

Mermaid does not have a use case diagram. This diagram uses a `flowchart`:
the rectangles are the actors and the round shapes are the use cases.

```mermaid
flowchart LR
    fis["«actor»<br/>Inspector"]
    uni["«actor»<br/>Competent unit"]
    pro["«actor»<br/>Owner"]
    subgraph sistema["SYS-CAR - Fiscalização (inspection)"]
        uc1(["Mark an alert on the map"])
        uc2(["Edit or delete an alert"])
        uc3(["Notify the units"])
        uc4(["Examine an alert: confirm, cancel, resolve"])
        uc5(["Embargo a property"])
        uc6(["Lift an embargo"])
        uc7(["Request a compliance declaration"])
    end
    fis --> uc1
    fis --> uc2
    uc1 -. includes .-> uc3
    uc4 -. includes .-> uc3
    uni --> uc4
    uni --> uc5
    uni --> uc6
    pro --> uc7
```

## Alert states (State)

This diagram shows the statuses of the alert and the permitted status changes.
The CRUD `atualizar()` does not change the status (see [ADR-F12](ADR-F12-crud-do-alerta.en.md)).

```mermaid
stateDiagram-v2
    [*] --> PENDENTE: alert created
    PENDENTE --> CONFIRMADO: unit confirms
    PENDENTE --> CANCELADO: unit cancels
    CONFIRMADO --> RESOLVIDO: area corrected
    RESOLVIDO --> [*]
    CANCELADO --> [*]
    note right of PENDENTE: stops the declaration
    note right of CONFIRMADO: stops the declaration and permits an embargo
```

## Sequence: record → notify → examine → embargo

This diagram shows the path of an alert:

1. The inspector clicks on the map. The property is the property that contains the point ([ADR-F14](ADR-F14-ponto-do-alerta-define-a-propriedade.en.md)).
2. The system notifies the competent units.
3. The unit confirms the alert.
4. The unit embargoes the property.

```mermaid
sequenceDiagram
    actor Fiscal as Inspector
    participant AA as AlertasAba
    participant AC as AlertaController
    participant PR as propriedades.py
    participant R as RegistroDesmatamento
    participant P as PublicadorAlertas
    participant N as NotificadorUnidades
    actor Unidade as Unit
    participant CA as ConformidadeAba
    participant CC as ConformidadeController

    Fiscal->>AA: clicks on the map
    AA->>AC: propriedade_no_ponto(lat, lon)
    AC-->>AA: "Sítio X" or "outside a registered property"
    Fiscal->>AA: writes the description and clicks Salvar
    AA->>AC: criar(descricao, latitude, longitude, data)
    AC->>PR: propriedade_no_ponto(lat, lon) [Poligono.contem]
    PR-->>AC: property or None
    AC->>R: RegistroDesmatamento(propriedade_id or None, ...).salvar()
    AC->>P: notificar(registro, "new alert")
    P->>N: atualizar(registro, evento) [Observer]
    N->>N: creates 1 Notificacao for each unit
    Unidade->>AA: right-click > Mudar para CONFIRMADO
    AA->>AC: mudar_status(id, "CONFIRMADO")
    AC->>R: mudar_status() [State]
    AC->>P: notificar(registro, "status changed")
    Unidade->>CA: selects the property, the confirmed alert and the reason
    CA->>CC: embargar(property, unit, alert, reason)
    CC-->>CA: (embargo, None)
```

## Sequence: edit and delete an alert (CRUD)

```mermaid
sequenceDiagram
    actor Fiscal as Inspector
    participant AA as AlertasAba
    participant AC as AlertaController
    participant R as RegistroDesmatamento

    Fiscal->>AA: double-clicks the alert
    AA->>AC: buscar_por_id(id)
    AC-->>AA: record (the map click is off: the point does not change)
    Fiscal->>AA: changes the description and clicks Salvar
    AA->>AC: atualizar(id, descricao, data)
    AC->>R: salvar() [point, property and status do not change]
    Fiscal->>AA: Excluir, and confirms the warning
    AA->>AC: excluir(id)
    AC->>R: deletar()
    R->>R: ON DELETE CASCADE deletes the notifications and embargoes
```

## Sequence: request a compliance declaration (Factory Method)

This diagram shows how the system decides to issue or refuse the compliance declaration.
The result of the analysis creates the declaration (see [ADR-F11](ADR-F11-remocao-das-fontes-e-factory-na-declaracao.en.md)).

```mermaid
sequenceDiagram
    actor Proprietario as Owner
    participant CA as ConformidadeAba
    participant CC as ConformidadeController
    participant R as RegistroDesmatamento
    participant E as Embargo
    participant RA as ResultadoAnalise
    participant D as Declaracao

    Proprietario->>CA: selects the property and requests the declaration
    CA->>CC: solicitar_declaracao(propriedade_id)
    CC->>R: listar_por_propriedade(id)
    CC->>CC: keeps the states with BLOQUEIA_CONFORMIDADE
    CC->>E: buscar_ativo(id)
    CC->>RA: analisar(impedimentos)
    RA-->>CC: SemPendencias or ComPendencias
    CC->>RA: criar_declaracao(propriedade_id, data) [Factory Method]
    RA-->>CC: Declaracao EMITIDA or NEGADA
    CC->>D: salvar()
    CC-->>CA: (declaracao, None)
    Proprietario->>CA: saves the selected declaration in a .txt file
    CA->>CC: texto_declaracao(id)
    CA->>CA: filedialog.asksaveasfilename()
```

## Implementation classes

This diagram shows the location of each design pattern:

- `ModeloBase` applies the Template Method. Only `ModeloBase` has the SQL for INSERT, UPDATE, DELETE and SELECT. Each model declares `TABELA` and `COLUNAS`. The 5 Fiscalização models inherit from it, as the Cadastro models do. Thus, the alert CRUD (`criar`, `atualizar`, `excluir`) is in `AlertaController`, which uses `salvar()` and `deletar()` of `ModeloBase`.
- `PropriedadeRural`, `Proprietario` and `Poligono` are Cadastro classes. They are in this diagram only to show the contract `propriedades.py`. This contract is the only access of the Fiscalização to the Cadastro. `propriedade_no_ponto()` uses `Poligono.contem()` to find the property of the alert (ADR-F14).
- `ResultadoAnalise` applies the Factory Method.
- `EstadoAlerta` applies the State pattern.
- `ObservadorAlerta` and `PublicadorAlertas` apply the Observer pattern.
- `TransicaoInvalida` and `ErroDeBanco` are the exceptions of the system (see [ADR-003](../decisoes/ADR-003-estrategia-de-excecoes.en.md)).
- `PublicadorAlertas` also applies the Singleton pattern. The system uses one instance, from `instancia()`. The constructor stays public. Thus, the tests can give isolated publishers.

```mermaid
classDiagram
    direction LR
    class ModeloBase {
        <<abstract>>
        +TABELA
        +COLUNAS
        +salvar()
        +deletar()
        +buscar_por_id(id)$
        +listar_todos()$
        +colunas_no_banco()$
        #_valores()
        #_de_linha(linha)$
        #_buscar_um(condicao, parametros)$
        #_buscar_varios(condicao, parametros, ordem="id")$
        #_existe(condicao, parametros)$
    }
    class RegistroDesmatamento {
        +descricao
        +data
        +status
        +latitude
        +longitude
        +propriedade_id
        +estado
        +mudar_status(novo)
        +listar_por_propriedade(id)$
        +schema_desatualizado()$
    }
    class EstadoAlerta {
        <<abstract>>
        +STATUS
        +PROXIMOS
        +BLOQUEIA_CONFORMIDADE
        +finalizado
        +ir_para(novo)
    }
    class Pendente
    class Confirmado
    class Resolvido
    class Cancelado
    class ValueError {
        <<Python>>
    }
    class Exception {
        <<Python>>
    }
    class TransicaoInvalida
    class ErroDeBanco {
        +de(erro_sqlite)$
    }
    class ObservadorAlerta {
        <<abstract>>
        +atualizar(registro, evento)*
    }
    class PublicadorAlertas {
        <<singleton>>
        -_instancia$
        +instancia()$ PublicadorAlertas
        +inscrever(obs)
        +cancelar_inscricao(obs)
        +notificar(registro, evento)
    }
    class NotificadorUnidades
    class Notificacao
    class UnidadeCompetente
    class Embargo {
        +buscar_ativo(propriedade_id)$
        +existe_da_unidade(unidade_id)$
    }
    class Declaracao {
        +emitida
        +listar_todas()$
        +listar_por_propriedade(propriedade_id)$
    }
    class ResultadoAnalise {
        <<abstract>>
        +criar_declaracao(propriedade_id, data)* Declaracao
    }
    class SemPendencias
    class ComPendencias {
        +impedimentos
    }
    class AlertaController {
        +criar(descricao, latitude, longitude, data)
        +buscar_por_id(id)
        +listar(incluir_finalizados)
        +atualizar(id, descricao, data)
        +descrever_local(registro)
        +excluir(id)
        +mudar_status(id, novo_status)
        +transicoes_possiveis(id)
    }
    class ConformidadeController {
        +solicitar_declaracao(propriedade_id)
        +embargar(...)
        +levantar_embargo(id)
        +alterar_motivo(embargo_id, motivo)
    }
    class UnidadeController
    class FichaAba {
        +ORDEM = 90
        +mostrar()
        +recarregar()
    }
    class FichaController {
        +listar_propriedades()
        +montar(propriedade_id) (FichaPropriedade, erro)
    }
    class FichaPropriedade {
        <<dataclass>>
        +propriedade
        +proprietario
        +alertas
        +embargo_ativo
        +unidade_do_embargo
        +declaracoes
        +alertas_em_aberto
        +situacao
    }
    class Propriedades {
        <<module>>
        +listar_propriedades()
        +buscar_propriedade(id)
        +nomes_das_propriedades()
        +buscar_proprietario(proprietario_id)
        +propriedade_no_ponto(lat, lon)
        +listar_areas()
    }
    class PropriedadeRural {
        +area Poligono
        +contem(lat, lon)
    }
    class Proprietario
    class Poligono {
        <<value object>>
        +contem(lat, lon)
    }

    ModeloBase <|-- UnidadeCompetente
    ModeloBase <|-- RegistroDesmatamento
    ModeloBase <|-- Notificacao
    ModeloBase <|-- Embargo
    ModeloBase <|-- Declaracao
    ModeloBase <|-- PropriedadeRural
    ModeloBase <|-- Proprietario
    ResultadoAnalise <|-- SemPendencias
    ResultadoAnalise <|-- ComPendencias
    ResultadoAnalise ..> Declaracao : creates
    EstadoAlerta <|-- Pendente
    EstadoAlerta <|-- Confirmado
    EstadoAlerta <|-- Resolvido
    EstadoAlerta <|-- Cancelado
    ValueError <|-- TransicaoInvalida
    Exception <|-- ErroDeBanco
    EstadoAlerta ..> TransicaoInvalida : raises
    ModeloBase ..> ErroDeBanco : raises
    RegistroDesmatamento --> EstadoAlerta : estado
    ObservadorAlerta <|-- NotificadorUnidades
    PublicadorAlertas o-- ObservadorAlerta
    NotificadorUnidades ..> Notificacao : creates
    RegistroDesmatamento "1" --> "0..*" Notificacao
    Notificacao "*" --> "1" UnidadeCompetente
    Embargo --> RegistroDesmatamento
    Embargo --> UnidadeCompetente
    AlertaController --> PublicadorAlertas
    AlertaController ..> RegistroDesmatamento : CRUD
    ConformidadeController ..> Embargo
    ConformidadeController ..> ResultadoAnalise : analisar()
    UnidadeController ..> UnidadeCompetente
    FichaAba --> FichaController
    FichaAba ..> FichaPropriedade : shows
    FichaController ..> FichaPropriedade : creates
    FichaController ..> Propriedades
    FichaController ..> RegistroDesmatamento
    FichaController ..> Embargo
    FichaController ..> Declaracao
    FichaController ..> UnidadeCompetente
    FichaPropriedade ..> EstadoAlerta : BLOQUEIA_CONFORMIDADE
    Propriedades ..> PropriedadeRural
    Propriedades ..> Proprietario
    PropriedadeRural ..> Poligono : area
    RegistroDesmatamento "0..*" --> "0..1" PropriedadeRural : the point is in the area
```

## Data model

The deletion of a property deletes its embargoes and declarations (`ON DELETE CASCADE`). Its alerts stay without a property (`ON DELETE SET NULL`, ADR-F14).
The deletion of an alert deletes its notifications and embargoes.
A partial unique index permits a maximum of one active embargo for each property.

```mermaid
erDiagram
    propriedades_rurais |o--o{ registros_desmatamento : "contains the point"
    registros_desmatamento ||--o{ notificacoes : "creates"
    unidades_competentes ||--o{ notificacoes : "receives"
    propriedades_rurais ||--o{ embargos : "has"
    unidades_competentes ||--o{ embargos : "applies"
    registros_desmatamento ||--o{ embargos : "justifies"
    propriedades_rurais ||--o{ declaracoes : "requests"
    registros_desmatamento {
        INTEGER id PK
        TEXT descricao
        TEXT data
        TEXT status
        REAL latitude
        REAL longitude
        INTEGER propriedade_id FK "NULL = outside a property"
    }
    embargos {
        INTEGER id PK
        INTEGER propriedade_id FK
        INTEGER unidade_id FK
        INTEGER registro_id FK
        TEXT data
        TEXT motivo
        INTEGER ativo
    }
    declaracoes {
        INTEGER id PK
        INTEGER propriedade_id FK
        TEXT data
        TEXT resultado
        TEXT motivo
    }
```
