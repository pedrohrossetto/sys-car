# ADR-F07: Integração por contrato de plugin

**Status:** aceita

## Contexto

A Fiscalização foi desenvolvida ao mesmo tempo que o Cadastro, em outro branch.
Os dois branches precisavam ser integrados sem conflito de merge e sem quebrar nada.

## Decisão

1. A Fiscalização só cria arquivos novos, nos pacotes `model/fiscalizacao`, `controller/fiscalizacao` e `view/fiscalizacao`.
   Ela não altera nenhum arquivo do Cadastro.
2. Ela segue o MVC dentro dos próprios pacotes. As views importam só controllers.
3. Ela se integra só pelo contrato de plugin do sistema (veja `docs/decisoes/ADR-001`):
   - cada model declara a constante `SCHEMA`;
   - cada aba declara `ORDEM` (de 50 a 99) e `registrar_abas(notebook)`;
   - o `_demo.py` começa com `_` para a janela principal ignorá-lo.
4. Do Cadastro, ela usa só o contrato combinado:
   - `get_connection()` e `init_db()`;
   - a tabela `propriedades_rurais` (colunas `id`, `nome` e `proprietario_id`);
   - `PropriedadeRural.buscar_por_id()` e `listar_todos()`.
   Esse acesso fica isolado em `controller/fiscalizacao/propriedades.py`.
5. Os models usam funções de acesso próprias (`conexao.py`: `executar`, `consultar`, `consultar_um`).
   Eles não herdam do `ModeloBase` do Cadastro, porque ele não existia no início do desenvolvimento.

## Consequências

- O merge não tem conflito, em qualquer ordem.
- Antes da integração, as abas são testadas pelo `_demo.py`. Depois, elas aparecem sozinhas na janela principal.
- Depois da integração, migrar os models para o `ModeloBase` é uma melhoria possível. Ela deve virar uma issue.

## Onde está no código

- `src/model/fiscalizacao/__init__.py`: `criar_tabelas()`
- `src/controller/fiscalizacao/instalacao.py`: `preparar_banco()`
- `src/controller/fiscalizacao/propriedades.py`
- `src/view/fiscalizacao/_demo.py`
