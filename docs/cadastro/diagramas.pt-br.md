# Diagramas UML do Cadastro

## Casos de uso

O Mermaid não tem diagrama de caso de uso nativo. Este diagrama usa um `flowchart`:
o retângulo é o ator e as formas arredondadas são os casos de uso.

```mermaid
flowchart LR
    ator["«ator»<br/>Operador do cadastro"]
    subgraph sistema["SYS-CAR - Cadastro"]
        uc1(["Cadastrar proprietário PF ou PJ"])
        uc2(["Editar ou excluir proprietário"])
        uc3(["Cadastrar propriedade rural"])
        uc4(["Desenhar a área no mapa"])
        uc5(["Validar CPF ou CNPJ"])
        uc6(["Validar a área e a sobreposição"])
    end
    ator --> uc1
    ator --> uc2
    ator --> uc3
    uc3 -. inclui .-> uc4
    uc1 -. inclui .-> uc5
    uc2 -. inclui .-> uc5
    uc4 -. inclui .-> uc6
```

## Sequência: cadastrar propriedade com a área

```mermaid
sequenceDiagram
    actor Operador
    participant PA as PropriedadeAba
    participant EA as EditorArea
    participant PC as PropriedadeRuralController
    participant G as Poligono
    participant M as PropriedadeRural (ModeloBase)
    participant DB as SQLite

    Operador->>PA: informa nome e proprietário
    loop um clique por vértice
        Operador->>EA: clica no mapa
        EA->>G: Poligono(vertices) [mostra área e centro]
    end
    Operador->>PA: Salvar (Enter)
    PA->>PC: criar(nome, proprietario_id, cadastro, vertices)
    PC->>G: Poligono(vertices)
    PC->>M: listar_todos() [áreas das outras propriedades]
    PC->>G: sobrepoe(outra) para cada área
    alt área inválida ou sobreposta
        PC-->>PA: (None, "mensagem")
        PA-->>Operador: caixa de erro
    else área válida
        PC->>M: PropriedadeRural(..., poligono=texto).salvar()
        M->>DB: INSERT
        PC-->>PA: (propriedade, None)
    end
```

## Classes da implementação

`ModeloBase` e `AbaCrud` são os pontos de Template Method. `ValidadorDocumento` é a Strategy.
`Poligono` é um objeto de valor: não tem tabela (ADR-C05). `MapaCanvas` e `Projecao` estão na [ADR-002](../decisoes/ADR-002-mapa-em-canvas.pt-br.md).

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
        <<objeto de valor>>
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
    PropriedadeRuralController ..> Poligono : valida e testa sobreposição
    AbaCrud <|-- ProprietarioAba
    AbaCrud <|-- PropriedadeAba
    ProprietarioAba ..> ProprietarioController
    PropriedadeAba ..> PropriedadeRuralController
    PropriedadeAba *-- EditorArea
    EditorArea *-- MapaCanvas
    MapaCanvas *-- Projecao
    Proprietario "1" --> "0..*" PropriedadeRural
```

## Modelo de dados

Apagar um proprietário apaga as propriedades dele (`ON DELETE CASCADE`).
A coluna `poligono` aceita NULL no banco, mas o controller exige a área.

```mermaid
erDiagram
    proprietarios ||--o{ propriedades_rurais : possui
    proprietarios {
        INTEGER id PK
        TEXT nome
        TEXT tipo "PF ou PJ"
        TEXT cpf "UNIQUE, só PF"
        TEXT cnpj "UNIQUE, só PJ"
    }
    propriedades_rurais {
        INTEGER id PK
        TEXT nome
        TEXT cadastro_publico
        INTEGER proprietario_id FK
        TEXT poligono "lat,lon;lat,lon;..."
    }
```
