# ADR-C01: Template Method no ModeloBase

**Status:** aceita

## Contexto

Os models `Proprietario`, `PropriedadeRural` e `Localizacao` repetiam o mesmo código:
abrir a conexão, montar o SQL, executar, fazer commit e fechar.
Só mudavam o nome da tabela e as colunas.

## Decisão

Usar o padrão **Template Method** em `src/model/base.py`:

- A classe `ModeloBase` define o algoritmo fixo de `salvar()`, `deletar()`, `buscar_por_id()` e `listar_todos()`.
- Cada subclasse informa só as partes variáveis:
  - `TABELA`: o nome da tabela;
  - `COLUNAS`: as colunas, sem o `id`;
  - os ganchos `_valores()` e `_de_linha()`, quando a conversão padrão não serve.
- As buscas específicas (`buscar_por_cpf`, `buscar_por_propriedade`) usam os auxiliares `_buscar_um()` e `_buscar_varios()`.

## Consequências

- Cada model tem só o próprio `SCHEMA`, o construtor e as buscas específicas.
- A interface pública dos models não mudou. Isso mantém o contrato com a Fiscalização.
- O construtor da subclasse precisa aceitar os nomes de `COLUNAS` e `id` como argumentos nomeados.

## Onde está no código

- `src/model/base.py`: `ModeloBase`.
- `src/model/proprietario.py`, `src/model/propriedade_rural.py`, `src/model/localizacao.py`: subclasses.
