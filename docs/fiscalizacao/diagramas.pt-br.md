# Diagramas UML da Fiscalização

## Casos de uso

O Mermaid não tem diagrama de caso de uso nativo. Este diagrama usa um `flowchart`:
os retângulos são os atores e as formas arredondadas são os casos de uso.

```mermaid
flowchart LR
    sat["«ator»<br/>Satélite"]
    usu["«ator»<br/>Usuário denunciante"]
    uni["«ator»<br/>Unidade competente"]
    pro["«ator»<br/>Proprietário"]
    subgraph sistema["SYS-CAR - Fiscalização"]
        uc1(["Detectar desmatamento"])
        uc2(["Reportar desmatamento com evidência"])
        uc3(["Notificar unidades"])
        uc4(["Examinar alerta: confirmar, cancelar, resolver"])
        uc5(["Embargar propriedade"])
        uc6(["Levantar embargo"])
        uc7(["Solicitar declaração de conformidade"])
    end
    sat --> uc1
    usu --> uc2
    uc1 -. inclui .-> uc3
    uc2 -. inclui .-> uc3
    uc4 -. inclui .-> uc3
    uni --> uc4
    uni --> uc5
    uni --> uc6
    pro --> uc7
```

## Estados do alerta (State)

Este diagrama mostra os status do alerta e as mudanças de status permitidas.

```mermaid
stateDiagram-v2
    [*] --> PENDENTE: alerta criado
    PENDENTE --> CONFIRMADO: unidade confirma
    PENDENTE --> CANCELADO: unidade cancela
    CONFIRMADO --> RESOLVIDO: área regularizada
    RESOLVIDO --> [*]
    CANCELADO --> [*]
    note right of PENDENTE: bloqueia a declaração
    note right of CONFIRMADO: bloqueia a declaração e permite embargo
```

## Sequência: reportar → notificar → examinar → embargar

Este diagrama mostra o caminho de um alerta:

1. O usuário reporta o desmatamento.
2. O sistema notifica as unidades competentes.
3. A unidade confirma o alerta.
4. A unidade embarga a propriedade.

```mermaid
sequenceDiagram
    actor Usuario as Usuário
    participant AA as AlertasAba
    participant AC as AlertaController
    participant U as Usuario (FonteDeteccao)
    participant R as RegistroDesmatamento
    participant P as PublicadorAlertas
    participant N as NotificadorUnidades
    actor Unidade
    participant CA as ConformidadeAba
    participant CC as ConformidadeController

    Usuario->>AA: preenche o alerta e anexa evidências
    AA->>AC: registrar_por_usuario(...)
    AC->>U: reportar_desmatamento(..., evidencias)
    U->>R: criar_registro(...) [Factory Method]
    AC->>R: salvar()
    AC->>P: notificar(registro, "novo alerta")
    P->>N: atualizar(registro, evento) [Observer]
    N->>N: cria 1 Notificacao por unidade
    Unidade->>AA: botão direito > Mudar para CONFIRMADO
    AA->>AC: mudar_status(id, "CONFIRMADO")
    AC->>R: mudar_status() [State]
    AC->>P: notificar(registro, "status alterado")
    Unidade->>CA: escolhe propriedade, alerta confirmado e motivo
    CA->>CC: embargar(propriedade, unidade, alerta, motivo)
    CC-->>CA: (embargo, None)
```

## Sequência: pedir declaração de conformidade

Este diagrama mostra como o sistema decide se emite ou nega a declaração de conformidade.

```mermaid
sequenceDiagram
    actor Proprietario as Proprietário
    participant CA as ConformidadeAba
    participant CC as ConformidadeController
    participant R as RegistroDesmatamento
    participant E as Embargo
    participant D as Declaracao

    Proprietario->>CA: escolhe a propriedade e pede a declaração
    CA->>CC: solicitar_declaracao(propriedade_id)
    CC->>R: listar_por_propriedade(id)
    CC->>CC: filtra estados com BLOQUEIA_CONFORMIDADE
    CC->>E: buscar_ativo(id)
    alt há alerta pendente/confirmado ou embargo ativo
        CC->>D: Declaracao(..., "NEGADA", motivo).salvar()
    else nenhum impedimento
        CC->>D: Declaracao(..., "EMITIDA").salvar()
    end
    CC-->>CA: (declaracao, None)
    Proprietario->>CA: Salvar selecionada em .txt
    CA->>CC: texto_declaracao(id)
    CA->>CA: filedialog.asksaveasfilename()
```

## Classes da implementação

Este diagrama mostra onde está cada padrão de projeto:

- `ModeloBase` aplica o Template Method: o SQL de INSERT, UPDATE, DELETE e SELECT fica só nele. Cada model declara `TABELA` e `COLUNAS`. Os 8 models da Fiscalização herdam dele, como os do Cadastro.
- `PropriedadeRural`, `Proprietario` e `Localizacao` são do Cadastro. Aparecem aqui só para mostrar o contrato `propriedades.py`, que é o único ponto de acesso da Fiscalização ao Cadastro.
- `FonteDeteccao` aplica o Factory Method.
- `EstadoAlerta` aplica o State.
- `ObservadorAlerta` e `PublicadorAlertas` aplicam o Observer.
- `PublicadorAlertas` também aplica o Singleton: o sistema usa uma única instância, obtida por `instancia()`. O construtor continua público para os testes injetarem publicadores isolados.

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
        #_valores()
        #_de_linha(linha)$
        #_buscar_um(condicao, parametros)$
        #_buscar_varios(condicao, parametros, ordem="id")$
        #_existe(condicao, parametros)$
    }
    class FonteDeteccao {
        <<abstract>>
        +criar_registro(...)*
    }
    class Satelite {
        +nome
        +entidade_responsavel
        +detectar_desmatamento(...)
    }
    class Usuario {
        +nome
        +cpf
        +email
        +reportar_desmatamento(..., evidencias)
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
        +existe_da_fonte(coluna, fonte_id)$
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
    class Evidencia
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
    class AlertaController
    class ConformidadeController
    class FonteController
    class UnidadeController
    class FichaAba {
        +ORDEM = 90
        +mostrar()
        +recarregar()
    }
    class FichaController {
        +listar_propriedades()
        +montar(propriedade_id) (FichaPropriedade, erro)
        +descrever_origem(alerta)
    }
    class FichaPropriedade {
        <<dataclass>>
        +propriedade
        +proprietario
        +localizacao
        +alertas
        +embargo_ativo
        +unidade_do_embargo
        +declaracoes
        +alertas_em_aberto
        +situacao
    }
    class Propriedades {
        <<módulo>>
        +listar_propriedades()
        +buscar_propriedade(id)
        +nomes_das_propriedades()
        +buscar_proprietario(proprietario_id)
        +buscar_localizacao(propriedade_id)
    }
    class PropriedadeRural
    class Proprietario
    class Localizacao

    ModeloBase <|-- Satelite
    ModeloBase <|-- Usuario
    ModeloBase <|-- UnidadeCompetente
    ModeloBase <|-- RegistroDesmatamento
    ModeloBase <|-- Evidencia
    ModeloBase <|-- Notificacao
    ModeloBase <|-- Embargo
    ModeloBase <|-- Declaracao
    ModeloBase <|-- PropriedadeRural
    ModeloBase <|-- Proprietario
    ModeloBase <|-- Localizacao
    FonteDeteccao <|-- Satelite
    FonteDeteccao <|-- Usuario
    FonteDeteccao ..> RegistroDesmatamento : cria
    EstadoAlerta <|-- Pendente
    EstadoAlerta <|-- Confirmado
    EstadoAlerta <|-- Resolvido
    EstadoAlerta <|-- Cancelado
    RegistroDesmatamento --> EstadoAlerta : estado
    ObservadorAlerta <|-- NotificadorUnidades
    PublicadorAlertas o-- ObservadorAlerta
    NotificadorUnidades ..> Notificacao : cria
    RegistroDesmatamento "1" *-- "0..*" Evidencia
    RegistroDesmatamento "1" --> "0..*" Notificacao
    Notificacao "*" --> "1" UnidadeCompetente
    Embargo --> RegistroDesmatamento
    Embargo --> UnidadeCompetente
    AlertaController --> PublicadorAlertas
    AlertaController ..> FonteDeteccao
    ConformidadeController ..> Embargo
    ConformidadeController ..> Declaracao
    FonteController ..> Satelite
    FonteController ..> Usuario
    UnidadeController ..> UnidadeCompetente
    FichaAba --> FichaController
    FichaAba ..> FichaPropriedade : mostra
    FichaController ..> FichaPropriedade : cria
    FichaController ..> Propriedades
    FichaController ..> RegistroDesmatamento
    FichaController ..> Embargo
    FichaController ..> Declaracao
    FichaController ..> UnidadeCompetente
    FichaController ..> Satelite
    FichaController ..> Usuario
    FichaPropriedade ..> EstadoAlerta : BLOQUEIA_CONFORMIDADE
    Propriedades ..> PropriedadeRural
    Propriedades ..> Proprietario
    Propriedades ..> Localizacao
```

## Modelo de dados

Apagar uma propriedade apaga os alertas, as evidências, as notificações, os embargos e as declarações dela (`ON DELETE CASCADE`).
Um índice único parcial garante no máximo um embargo ativo por propriedade.

```mermaid
erDiagram
    propriedades_rurais ||--o{ registros_desmatamento : "alertas"
    satelites |o--o{ registros_desmatamento : "detecta"
    usuarios |o--o{ registros_desmatamento : "reporta"
    registros_desmatamento ||--o{ evidencias : "contém"
    registros_desmatamento ||--o{ notificacoes : "gera"
    unidades_competentes ||--o{ notificacoes : "recebe"
    propriedades_rurais ||--o{ embargos : "sofre"
    unidades_competentes ||--o{ embargos : "aplica"
    registros_desmatamento ||--o{ embargos : "justifica"
    propriedades_rurais ||--o{ declaracoes : "pede"
    registros_desmatamento {
        INTEGER id PK
        TEXT descricao
        TEXT data
        TEXT status
        REAL latitude
        REAL longitude
        INTEGER propriedade_id FK
        INTEGER satelite_id FK
        INTEGER usuario_id FK
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
