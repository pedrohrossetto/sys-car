# ADR-F09: Acesso a dados unificado no ModeloBase

**Status:** aceita. Substitui o item 5 da [ADR-F07](ADR-F07-integracao-por-contrato-de-plugin.pt-br.md).

## Contexto

O sistema acessava o banco de duas formas:

- Os models do Cadastro herdavam do `ModeloBase` (ver [ADR-C01](../cadastro/ADR-C01-template-method-modelo-base.pt-br.md)).
- Os 8 models da Fiscalização usavam o `conexao.py`. Cada model escrevia o próprio SQL de INSERT, UPDATE, DELETE e SELECT.

O grupo desenvolveu as duas áreas ao mesmo tempo. Por isso, a Fiscalização não podia usar o `ModeloBase`, que ainda não existia.

As aulas 09 e 10 do plano de ensino pedem uma lógica única de acesso a dados, ligada à GUI no padrão MVC.

## Decisão

Todos os models do sistema herdam do `ModeloBase`:

- Os 8 models da Fiscalização declaram `TABELA` e `COLUNAS`, como os models do Cadastro.
  - `Satelite`, `Usuario`, `UnidadeCompetente`, `RegistroDesmatamento`
  - `Evidencia`, `Notificacao`, `Embargo`, `Declaracao`
- O arquivo `conexao.py` foi removido.
- As buscas específicas usam os auxiliares do `ModeloBase`. Elas não escrevem SQL completo.

A Fiscalização precisava de dois recursos que o `ModeloBase` não tinha. O `ModeloBase` agora tem esses recursos:

| Recurso | Uso na Fiscalização |
|---|---|
| `_buscar_varios(..., ordem=...)` | Listar embargos, declarações e notificações do mais novo para o mais antigo |
| `_existe(condicao, parametros)` | Verificar se uma unidade já aplicou embargo e se uma fonte já gerou alerta |

O valor padrão de `ordem` é `id`. Por isso, os models do Cadastro continuam a listar em ordem crescente.

## Consequências

- O sistema tem uma só forma de acessar o banco. Uma correção no `ModeloBase` vale para os 11 models.
- Os nomes dos métodos públicos não mudaram. Os controllers e as views não mudaram.
- `Notificacao` e `Embargo` agora gravam todas as colunas no UPDATE. Antes, eles gravavam só `status` e `ativo`.
  O resultado no banco é o mesmo, porque o objeto vem do banco antes da mudança.
- Todos os models agora têm `deletar()`. Isso prepara a issue #5 (CRUD completo).
- O `__init__.py` do pacote ainda abre uma conexão. Ele só executa os `SCHEMA` antes da integração (testes e `_demo.py`). Ele não lê nem grava registros.

## Onde está no código

- `src/model/base.py`: `_buscar_varios()` com `ordem` e `_existe()`
- `src/model/fiscalizacao/*.py`: os 8 models
- `tests/test_fiscalizacao_acesso_unificado.py`
