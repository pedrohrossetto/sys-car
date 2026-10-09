# Registration UML diagrams

## Use cases

Mermaid does not have a native use case diagram. This diagram uses a `flowchart`.
The rectangle is the actor. The round shapes are the use cases.

```mermaid
flowchart LR
    ator["«actor»<br/>Registration operator"]
    subgraph sistema["SYS-CAR - Registration"]
        uc1(["Add a PF or PJ owner"])
        uc2(["Edit or delete an owner"])
        uc3(["Add a rural property"])
        uc4(["Record the location and polygon"])
        uc5(["Validate CPF or CNPJ"])
        uc6(["Validate coordinates"])
    end
    ator --> uc1
    ator --> uc2
    ator --> uc3
    ator --> uc4
    uc1 -. includes .-> uc5
    uc2 -. includes .-> uc5
    uc4 -. includes .-> uc6
```

## Sequence: add a property with its location

```mermaid
sequenceDiagram
    actor Operator
    participant PA as PropriedadeAba
    participant PC as PropriedadeRuralController
    participant LA as LocalizacaoAba
    participant LC as LocalizacaoController
    participant M as Models (ModeloBase)
    participant DB as SQLite

    Operator->>PA: selects the owner and types the name
    Operator->>PA: Salvar (Enter)
    PA->>PC: criar(nome, proprietario_id, cadastro)
    PC->>M: Proprietario.buscar_por_id(id)
    M->>DB: SELECT
    PC->>M: PropriedadeRural.salvar()
    M->>DB: INSERT
    PC-->>PA: (propriedade, None)
    PA->>PA: recarregar()
    Operator->>LA: selects the property and types the coordinates
    Operator->>LA: Salvar (Enter)
    LA->>LC: criar(propriedade_id, lat, lon, alt, poligono)
    LC->>LC: converter_latitude/longitude/poligono
    alt data is not valid
        LC-->>LA: (None, "message")
        LA-->>Operator: error dialog
    else data is valid
        LC->>M: Localizacao.salvar()
        M->>DB: INSERT
        LC-->>LA: (localizacao, None)
    end
```

## Implementation classes

`ModeloBase` and `AbaCrud` are the Template Method points. `ValidadorDocumento` is the Strategy.

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
    }
    class Proprietario {
        +nome
        +tipo
        +cpf
        +cnpj
        +documento
        +buscar_por_documento(tipo, doc)$
        +schema_desatualizado()$
    }
    class PropriedadeRural {
        +nome
        +cadastro_publico
        +proprietario_id
    }
    class Localizacao {
        +latitude
        +longitude
        +altitude
        +poligono_geometria
        +propriedade_id
        +buscar_por_propriedade(id)$
    }
    class ValidadorDocumento {
        <<abstract>>
        +normalizar(texto)
        +valido(documento)
    }
    class ValidadorCPF
    class ValidadorCNPJ
    class ProprietarioController
    class PropriedadeRuralController
    class LocalizacaoController
    class AbaCrud {
        <<abstract>>
        +salvar()
        +excluir()
        +carregar_selecionado()
        +limpar()
        #criar_campos(form)
        #enviar(id)
    }
    class ProprietarioAba
    class PropriedadeAba
    class LocalizacaoAba

    ModeloBase <|-- Proprietario
    ModeloBase <|-- PropriedadeRural
    ModeloBase <|-- Localizacao
    ValidadorDocumento <|-- ValidadorCPF
    ValidadorDocumento <|-- ValidadorCNPJ
    ProprietarioController ..> ValidadorDocumento
    ProprietarioController ..> Proprietario
    PropriedadeRuralController ..> PropriedadeRural
    LocalizacaoController ..> Localizacao
    AbaCrud <|-- ProprietarioAba
    AbaCrud <|-- PropriedadeAba
    AbaCrud <|-- LocalizacaoAba
    ProprietarioAba ..> ProprietarioController
    PropriedadeAba ..> PropriedadeRuralController
    LocalizacaoAba ..> LocalizacaoController
    Proprietario "1" --> "0..*" PropriedadeRural
    PropriedadeRural "1" *-- "0..1" Localizacao
```

## Data model

When you delete an owner, the system also deletes the properties and their locations (`ON DELETE CASCADE`).

```mermaid
erDiagram
    proprietarios ||--o{ propriedades_rurais : owns
    propriedades_rurais ||--o| localizacoes : has
    proprietarios {
        INTEGER id PK
        TEXT nome
        TEXT tipo "PF or PJ"
        TEXT cpf "UNIQUE, PF only"
        TEXT cnpj "UNIQUE, PJ only"
    }
    propriedades_rurais {
        INTEGER id PK
        TEXT nome
        TEXT cadastro_publico
        INTEGER proprietario_id FK
    }
    localizacoes {
        INTEGER id PK
        REAL latitude
        REAL longitude
        REAL altitude
        TEXT poligono_geometria
        INTEGER propriedade_id FK "UNIQUE"
    }
```
