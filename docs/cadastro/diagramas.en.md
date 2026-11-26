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
        uc4(["Draw the area on the map"])
        uc5(["Validate CPF or CNPJ"])
        uc6(["Validate the area and the overlap"])
    end
    ator --> uc1
    ator --> uc2
    ator --> uc3
    uc3 -. includes .-> uc4
    uc1 -. includes .-> uc5
    uc2 -. includes .-> uc5
    uc4 -. includes .-> uc6
```

## Sequence: add a property with its area

```mermaid
sequenceDiagram
    actor Operator
    participant PA as PropriedadeAba
    participant EA as EditorArea
    participant PC as PropriedadeRuralController
    participant G as Poligono
    participant M as PropriedadeRural (ModeloBase)
    participant DB as SQLite

    Operator->>PA: types the name and selects the owner
    loop one click for each vertex
        Operator->>EA: clicks on the map
        EA->>G: Poligono(vertices) [shows area and centre]
    end
    Operator->>PA: Save (Enter)
    PA->>PC: criar(nome, proprietario_id, cadastro, vertices)
    PC->>G: Poligono(vertices)
    PC->>M: listar_todos() [areas of the other properties]
    PC->>G: sobrepoe(outra) for each area
    alt area not valid or overlap
        PC-->>PA: (None, "message")
        PA-->>Operator: error box
    else area valid
        PC->>M: PropriedadeRural(..., poligono=text).salvar()
        M->>DB: INSERT
        PC-->>PA: (propriedade, None)
    end
```

## Implementation classes

`ModeloBase` and `AbaCrud` are the Template Method points. `ValidadorDocumento` is the Strategy.
`Poligono` is a value object: it has no table (ADR-C05). `MapaCanvas` and `Projecao` are in [ADR-002](../decisoes/ADR-002-mapa-em-canvas.en.md).

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
        +poligono
        +area Poligono
        +centroide
        +area_ha
        +contem(lat, lon)
        +schema_desatualizado()$
    }
    class Poligono {
        <<value object>>
        +vertices
        +de_texto(texto)$
        +para_texto()
        +centroide()
        +area_ha()
        +contem(lat, lon)
        +sobrepoe(outro)
    }
    class ValidadorDocumento {
        <<abstract>>
        +normalizar(texto)
        +valido(documento)
    }
    class ValidadorCPF
    class ValidadorCNPJ
    class ProprietarioController
    class PropriedadeRuralController {
        +criar(nome, proprietario_id, cadastro, poligono)
        +atualizar(id, ..., poligono)
        +listar_areas(exceto_id)
    }
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
    class EditorArea
    class MapaCanvas
    class Projecao

    ModeloBase <|-- Proprietario
    ModeloBase <|-- PropriedadeRural
    PropriedadeRural ..> Poligono : area
    ValidadorDocumento <|-- ValidadorCPF
    ValidadorDocumento <|-- ValidadorCNPJ
    ProprietarioController ..> ValidadorDocumento
    ProprietarioController ..> Proprietario
    PropriedadeRuralController ..> PropriedadeRural
    PropriedadeRuralController ..> Poligono : validates and tests overlap
    AbaCrud <|-- ProprietarioAba
    AbaCrud <|-- PropriedadeAba
    ProprietarioAba ..> ProprietarioController
    PropriedadeAba ..> PropriedadeRuralController
    PropriedadeAba *-- EditorArea
    EditorArea *-- MapaCanvas
    MapaCanvas *-- Projecao
    Proprietario "1" --> "0..*" PropriedadeRural
```

## Data model

When you delete an owner, the system also deletes the properties (`ON DELETE CASCADE`).
The column `poligono` accepts NULL in the database, but the controller requires the area.

```mermaid
erDiagram
    proprietarios ||--o{ propriedades_rurais : owns
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
        TEXT poligono "lat,lon;lat,lon;..."
    }
```
