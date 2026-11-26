# Diagramas UML da Fiscalização

## Casos de uso

O Mermaid não tem diagrama de caso de uso nativo. Este diagrama usa um `flowchart`:
os retângulos são os atores e as formas arredondadas são os casos de uso.

```mermaid
flowchart LR
    fis["«ator»<br/>Fiscal"]
    uni["«ator»<br/>Unidade competente"]
    pro["«ator»<br/>Proprietário"]
    subgraph sistema["SYS-CAR - Fiscalização"]
        uc1(["Marcar alerta no mapa"])
        uc2(["Editar ou excluir alerta"])
        uc3(["Notificar unidades"])
        uc4(["Examinar alerta: confirmar, cancelar, resolver"])
        uc5(["Embargar propriedade"])
        uc6(["Levantar embargo"])
        uc7(["Solicitar declaração de conformidade"])
    end
    fis --> uc1
    fis --> uc2
    uc1 -. inclui .-> uc3
    uc4 -. inclui .-> uc3
    uni --> uc4
    uni --> uc5
    uni --> uc6
    pro --> uc7
```

## Estados do alerta (State)

Este diagrama mostra os status do alerta e as mudanças de status permitidas.
O `atualizar()` do CRUD não muda o status (ver [ADR-F12](ADR-F12-crud-do-alerta.pt-br.md)).

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

## Sequência: registrar → notificar → examinar → embargar

Este diagrama mostra o caminho de um alerta:

1. O fiscal clica no mapa. A propriedade é a que contém o ponto ([ADR-F14](ADR-F14-ponto-do-alerta-define-a-propriedade.pt-br.md)).
2. O sistema notifica as unidades competentes.
3. A unidade confirma o alerta.
4. A unidade embarga a propriedade.

```mermaid
sequenceDiagram
    actor Fiscal
    participant AA as AlertasAba
    participant AC as AlertaController
    participant PR as propriedades.py
    participant R as RegistroDesmatamento
    participant P as PublicadorAlertas
    participant N as NotificadorUnidades
    actor Unidade
    participant CA as ConformidadeAba
    participant CC as ConformidadeController

    Fiscal->>AA: clica no mapa
    AA->>AC: propriedade_no_ponto(lat, lon)
    AC-->>AA: "Sítio X" ou "fora de propriedade cadastrada"
    Fiscal->>AA: escreve a descrição e clica em Salvar
    AA->>AC: criar(descricao, latitude, longitude, data)
    AC->>PR: propriedade_no_ponto(lat, lon) [Poligono.contem]
    PR-->>AC: propriedade ou None
    AC->>R: RegistroDesmatamento(propriedade_id ou None, ...).salvar()
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

## Sequência: editar e excluir um alerta (CRUD)

```mermaid
sequenceDiagram
    actor Fiscal
    participant AA as AlertasAba
    participant AC as AlertaController
    participant R as RegistroDesmatamento

    Fiscal->>AA: duplo clique no alerta
    AA->>AC: buscar_por_id(id)
    AC-->>AA: registro (o clique no mapa fica desligado: ponto fixo)
    Fiscal->>AA: muda a descrição e clica em Salvar
    AA->>AC: atualizar(id, descricao, data)
    AC->>R: salvar() [ponto, propriedade e status não mudam]
    Fiscal->>AA: Excluir e confirma o aviso
    AA->>AC: excluir(id)
    AC->>R: deletar()
    R->>R: ON DELETE CASCADE apaga notificações e embargos
```

## Sequência: pedir declaração de conformidade (Factory Method)

Este diagrama mostra como o sistema decide se emite ou nega a declaração de conformidade.
O resultado da análise cria a declaração (ver [ADR-F11](ADR-F11-remocao-das-fontes-e-factory-na-declaracao.pt-br.md)).

```mermaid
sequenceDiagram
    actor Proprietario as Proprietário
    participant CA as ConformidadeAba
    participant CC as ConformidadeController
    participant R as RegistroDesmatamento
    participant E as Embargo
    participant RA as ResultadoAnalise
    participant D as Declaracao

    Proprietario->>CA: escolhe a propriedade e pede a declaração
    CA->>CC: solicitar_declaracao(propriedade_id)
    CC->>R: listar_por_propriedade(id)
    CC->>CC: filtra estados com BLOQUEIA_CONFORMIDADE
    CC->>E: buscar_ativo(id)
    CC->>RA: analisar(impedimentos)
    RA-->>CC: SemPendencias ou ComPendencias
    CC->>RA: criar_declaracao(propriedade_id, data) [Factory Method]
    RA-->>CC: Declaracao EMITIDA ou NEGADA
    CC->>D: salvar()
    CC-->>CA: (declaracao, None)
    Proprietario->>CA: Salvar selecionada em .txt
    CA->>CC: texto_declaracao(id)
    CA->>CA: filedialog.asksaveasfilename()
```

## Classes da implementação

Este diagrama mostra onde está cada padrão de projeto:

- `ModeloBase` aplica o Template Method: o SQL de INSERT, UPDATE, DELETE e SELECT fica só nele. Cada model declara `TABELA` e `COLUNAS`. Os 5 models da Fiscalização herdam dele, como os do Cadastro. Por isso o CRUD do alerta (`criar`, `atualizar`, `excluir`) está no `AlertaController`, que usa `salvar()` e `deletar()` do `ModeloBase`.
- `PropriedadeRural`, `Proprietario` e `Poligono` são do Cadastro. Aparecem aqui só para mostrar o contrato `propriedades.py`, que é o único ponto de acesso da Fiscalização ao Cadastro. `propriedade_no_ponto()` usa `Poligono.contem()` para achar a propriedade do alerta (ADR-F14).
- `ResultadoAnalise` aplica o Factory Method.
- `EstadoAlerta` aplica o State.
- `ObservadorAlerta` e `PublicadorAlertas` aplicam o Observer.
- `TransicaoInvalida` e `ErroDeBanco` são as exceções próprias do sistema (ver [ADR-003](../decisoes/ADR-003-estrategia-de-excecoes.pt-br.md)).
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
        <<módulo>>
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
        <<objeto de valor>>
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
    ResultadoAnalise ..> Declaracao : cria
    EstadoAlerta <|-- Pendente
    EstadoAlerta <|-- Confirmado
    EstadoAlerta <|-- Resolvido
    EstadoAlerta <|-- Cancelado
    ValueError <|-- TransicaoInvalida
    Exception <|-- ErroDeBanco
    EstadoAlerta ..> TransicaoInvalida : lança
    ModeloBase ..> ErroDeBanco : lança
    RegistroDesmatamento --> EstadoAlerta : estado
    ObservadorAlerta <|-- NotificadorUnidades
    PublicadorAlertas o-- ObservadorAlerta
    NotificadorUnidades ..> Notificacao : cria
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
    FichaAba ..> FichaPropriedade : mostra
    FichaController ..> FichaPropriedade : cria
    FichaController ..> Propriedades
    FichaController ..> RegistroDesmatamento
    FichaController ..> Embargo
    FichaController ..> Declaracao
    FichaController ..> UnidadeCompetente
    FichaPropriedade ..> EstadoAlerta : BLOQUEIA_CONFORMIDADE
    Propriedades ..> PropriedadeRural
    Propriedades ..> Proprietario
    PropriedadeRural ..> Poligono : area
    RegistroDesmatamento "0..*" --> "0..1" PropriedadeRural : o ponto cai na área
```

## Modelo de dados

Apagar uma propriedade apaga os embargos e as declarações dela (`ON DELETE CASCADE`). Os alertas dela ficam sem propriedade (`ON DELETE SET NULL`, ADR-F14).
Apagar um alerta apaga as notificações e os embargos dele.
Um índice único parcial garante no máximo um embargo ativo por propriedade.

```mermaid
erDiagram
    propriedades_rurais |o--o{ registros_desmatamento : "contém o ponto"
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
        INTEGER propriedade_id FK "NULL = fora de propriedade"
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
