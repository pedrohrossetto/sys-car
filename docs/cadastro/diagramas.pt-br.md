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
        uc4(["Registrar localização e polígono"])
        uc5(["Validar CPF ou CNPJ"])
        uc6(["Validar coordenadas"])
    end
    ator --> uc1
    ator --> uc2
    ator --> uc3
    ator --> uc4
    uc1 -. inclui .-> uc5
    uc2 -. inclui .-> uc5
    uc4 -. inclui .-> uc6
```

## Sequência: cadastrar propriedade com localização

```mermaid
sequenceDiagram
    actor Operador
    participant PA as PropriedadeAba
    participant PC as PropriedadeRuralController
    participant LA as LocalizacaoAba
    participant LC as LocalizacaoController
    participant M as Models (ModeloBase)
    participant DB as SQLite

    Operador->>PA: escolhe proprietário e informa nome
    Operador->>PA: Salvar (Enter)
    PA->>PC: criar(nome, proprietario_id, cadastro)
    PC->>M: Proprietario.buscar_por_id(id)
    M->>DB: SELECT
    PC->>M: PropriedadeRural.salvar()
    M->>DB: INSERT
    PC-->>PA: (propriedade, None)
    PA->>PA: recarregar()
    Operador->>LA: escolhe propriedade e informa coordenadas
    Operador->>LA: Salvar (Enter)
    LA->>LC: criar(propriedade_id, lat, lon, alt, poligono)
    LC->>LC: converter_latitude/longitude/poligono
    alt dado inválido
        LC-->>LA: (None, "mensagem")
        LA-->>Operador: caixa de erro
    else dados válidos
        LC->>M: Localizacao.salvar()
        M->>DB: INSERT
        LC-->>LA: (localizacao, None)
    end
```

## Classes da implementação

`ModeloBase` e `AbaCrud` são os pontos de Template Method. `ValidadorDocumento` é a Strategy.

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

## Modelo de dados

Apagar um proprietário apaga as propriedades dele e as localizações delas (`ON DELETE CASCADE`).

```mermaid
erDiagram
    proprietarios ||--o{ propriedades_rurais : possui
    propriedades_rurais ||--o| localizacoes : tem
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
