# ADR-F07: Integration through the plugin contract

**Status:** accepted

## Context

The team developed the Fiscalização at the same time as the Cadastro, on a different branch.
The team had to merge the two branches without merge conflicts and without errors.

## Decision

1. The Fiscalização only creates new files, in the packages `model/fiscalizacao`, `controller/fiscalizacao` and `view/fiscalizacao`.
   It does not change a Cadastro file.
2. It uses MVC in its packages. The views import only controllers.
3. It connects to the system only through the plugin contract (see [ADR-001](../decisoes/ADR-001-arquitetura-mvc-plugins.en.md)):
   - each model declares the constant `SCHEMA`;
   - each tab declares `ORDEM` (from 50 to 99) and `registrar_abas(notebook)`;
   - the name `_demo.py` starts with `_`. Thus, the main window ignores it.
4. From the Cadastro, it uses only the agreed contract:
   - `get_connection()` and `init_db()`;
   - the table `propriedades_rurais` (columns `id`, `nome` and `proprietario_id`);
   - `PropriedadeRural.buscar_por_id()` and `listar_todos()`.
   This access is only in `controller/fiscalizacao/propriedades.py`.
5. The models use their own access functions (`conexao.py`: `executar`, `consultar`, `consultar_um`).
   They do not inherit from the `ModeloBase` of the Cadastro, because it did not exist at the start.
   **[ADR-F09](ADR-F09-acesso-a-dados-unificado.en.md) replaces this item.** Now the models inherit from the `ModeloBase`, and `conexao.py` does not exist.

## Consequences

- The merge has no conflicts, in each order.
- Before the integration, `_demo.py` tests the tabs.
- After the integration, the tabs show automatically in the main window.
- After the integration, issue #3 moved the models to the `ModeloBase` (see [ADR-F09](ADR-F09-acesso-a-dados-unificado.en.md)).

## Location in the code

- `src/model/fiscalizacao/__init__.py`: `criar_tabelas()`
- `src/controller/fiscalizacao/instalacao.py`: `preparar_banco()`
- `src/controller/fiscalizacao/propriedades.py`
- `src/view/fiscalizacao/_demo.py`
