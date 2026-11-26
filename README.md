# Sistema de Cadastro Ambiental Rural (sys-car)

## Detalhes

- Instituição:
  - Instituto Federal Sul-Riograndense de Passo Fundo
- Disciplina:
  - Linguagem de Programação Orientada a Objetos - 4° Semestre
- Docente:
  - Leonardo Deliyannis Constantin

## Descrição

- Proprietários poderão registrar suas propriedades rurais, declarando as coordenadas e o polígono que delimita cada propriedade.
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

    class REGISTRO_DESMATAMENTO {
        -INT id
        -STRING descricao
        -DATE data
        -STATUS_ALERTA status
        -FLOAT latitude
        -FLOAT longitude
        +criar()
        +ler()
        +atualizar()
        +excluir()
        +enviarNotificacao(detalhes)
        +atualizarStatus(status)
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
        -POLIGONO area
        +centroide()
        +areaHa()
        +contem(ponto)
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
    REGISTRO_DESMATAMENTO "0..*" --> "0..1" PROPRIEDADE_RURAL : o ponto cai na área
    REGISTRO_DESMATAMENTO "1" --> "0..*" NOTIFICACAO : gera
    REGISTRO_DESMATAMENTO ..> STATUS_ALERTA : utiliza

    NOTIFICACAO "*" --> "1" UNIDADE_COMPETENTE : destinada
    UNIDADE_COMPETENTE "0..*" --> "0..*" PROPRIEDADE_RURAL : embarga

    PROPRIETARIO "1" --> "1..*" PROPRIEDADE_RURAL : possui
```

O diagrama acima é o modelo **conceitual**. A propriedade tem uma área (polígono) que não se sobrepõe à de outra
propriedade; o alerta é um ponto no mapa e pertence à propriedade cuja área contém o ponto (ou a nenhuma).
 Os diagramas da implementação ficam em [`docs/`](docs/README.md).

## Interface

A janela principal tem uma aba para cada cadastro. As abas Propriedades, Alertas e Ficha da Propriedade têm um
mapa: a área da propriedade é desenhada clique a clique, e o alerta é um clique no lugar do desmatamento
(roda do mouse: zoom; arrastar: mover).

![Aba Proprietários com dois cadastros na lista](docs/imagens/aba-proprietarios.png)

![Aba Propriedades: formulário, mapa para desenhar a área e lista com a área em hectares](docs/imagens/aba-propriedades.png)

![Aba Alertas: mapa com as áreas das propriedades e os alertas, lista e formulário do novo alerta](docs/imagens/aba-alertas.png)

![Aba Ficha da Propriedade: área, proprietário, embargo, alertas, declarações e o mapa da propriedade](docs/imagens/aba-ficha.png)

## Documentação

Toda a documentação técnica (decisões de projeto, diagramas UML em pt-BR e EN e guias em Leitura Fácil) está em [`docs/README.md`](docs/README.md).

## Estrutura do Projeto

O projeto segue o padrão **MVC (Model-View-Controller)** com banco de dados **SQLite** e interface **Tkinter**.

```
sys-car/
├── README.md
├── docs/                         # documentação (ADRs, UML, guias)
├── data/                         # (criada automaticamente) banco SQLite
│   └── syscar.db
├── tests/                        # testes automatizados (unittest)
└── src/
    ├── main.py                   # ponto de entrada
    ├── descoberta.py             # descoberta automática de tabelas e abas
    ├── database/
    │   └── database.py           # conexão + init_db() (executa o SCHEMA de cada model)
    ├── model/                    # classes de domínio; cada uma declara seu SCHEMA
    │   ├── base.py               # ModeloBase (Template Method)
    │   ├── documento.py          # validadores de CPF/CNPJ (Strategy)
    │   ├── coordenadas.py        # validação de latitude, longitude e texto do polígono
    │   ├── geometria.py          # Poligono: centroide, área, ponto dentro, sobreposição
    │   ├── proprietario.py
    │   ├── propriedade_rural.py  # com a área (polígono) da propriedade
    │   └── fiscalizacao/         # alertas, notificações, embargos, declarações
    ├── controller/               # regras de negócio e validações
    └── view/
        ├── janela_principal.py   # janela, menu e descoberta das abas
        ├── aba_crud.py           # AbaCrud (Template Method)
        ├── widgets.py            # Seletor e tabela com rolagem
        ├── projecao.py           # lat/lon <-> pixels do mapa (sem tkinter)
        ├── mapa.py               # MapaCanvas e EditorArea (mapa em Canvas)
        └── *_aba.py              # uma aba por entidade
```

### Executar

```bash
python3 src/main.py
```

O programa precisa do **Tkinter**:

- Linux (Debian/Ubuntu): `sudo apt install python3-tk`
- Windows e macOS: o instalador oficial do Python (python.org) já inclui o Tkinter.

Na primeira execução, o programa cria a pasta `data/` e o banco `data/syscar.db`.

> **Banco de uma versão antiga:** se o programa avisar que o banco é de uma versão antiga, apague o arquivo `data/syscar.db` e rode de novo.

### Testes

```bash
python3 -m unittest discover -s tests -v
```

### Como adicionar uma entidade nova

Nenhum arquivo central precisa ser editado:

1. **model/**: crie a classe e declare a constante `SCHEMA` com o `CREATE TABLE IF NOT EXISTS`. O `init_db()` encontra sozinho.
2. **controller/**: crie o controller com as regras. Os métodos de escrita devolvem `(resultado, erro)`.
3. **view/**: crie o módulo da aba com `ORDEM` e `registrar_abas(notebook)`. A janela principal encontra sozinha.
4. **tests/**: crie os testes da entidade.

O acompanhamento do que falta fazer fica nas issues do GitHub.
