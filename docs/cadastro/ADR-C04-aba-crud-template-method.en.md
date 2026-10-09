# ADR-C04: Template Method in AbaCrud

**Status:** accepted

## Context

The old `app_tk.py` had a generic screen. But it used `if/elif` with the entity name to add and to update records.
Each new entity made these chains longer.
The screen also loaded the form from the values in the Treeview.
ttk changes the text `"01234567890"` into the number `1234567890`. Thus, the CPF lost its first zero.

## Decision

Use the **Template Method** pattern in the view, with the class `AbaCrud` (`src/view/aba_crud.py`):

- `AbaCrud` makes the fixed structure: form, buttons, table, status bar and keyboard shortcuts.
- `AbaCrud` has the fixed flow: `salvar()`, `excluir()`, `carregar_selecionado()` and `limpar()`.
- Each concrete tab has the hooks `criar_campos()`, `limpar_campos()`, `preencher()`, `valores_linha()`, `enviar()` and, if necessary, `atualizar_opcoes()`.
- Each table row uses the database id as its `iid`. The controller loads the form from this id.
  The form never uses the values that the table shows.

## Consequences

- The view does not have an `if/elif` for each entity.
- The CPF problem with the first zero is solved.
- The "Salvar" button adds a new record or updates the loaded record. It replaces the old "Cadastrar" and "Atualizar" buttons.

## Location in the code

- `src/view/aba_crud.py`: `AbaCrud`.
- `src/view/proprietario_aba.py`, `src/view/propriedade_aba.py`, `src/view/localizacao_aba.py`: concrete tabs.
