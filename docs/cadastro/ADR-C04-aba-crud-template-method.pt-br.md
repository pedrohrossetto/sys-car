# ADR-C04: Template Method na AbaCrud

**Status:** aceita

## Contexto

O `app_tk.py` antigo tinha uma tela genérica, mas usava `if/elif` com o nome da entidade
para cadastrar e atualizar. Toda entidade nova aumentava essas cadeias.
A tela também recarregava o formulário a partir dos valores do Treeview.
O ttk converte o texto `"01234567890"` no número `1234567890`, então o CPF perdia o zero inicial.

## Decisão

Usar o padrão **Template Method** na view, com a classe `AbaCrud` (`src/view/aba_crud.py`):

- A `AbaCrud` monta a estrutura fixa: formulário, botões, tabela, barra de status e atalhos.
- A `AbaCrud` implementa o fluxo fixo: `salvar()`, `excluir()`, `carregar_selecionado()` e `limpar()`.
- Cada aba concreta implementa os ganchos `criar_campos()`, `limpar_campos()`, `preencher()`,
  `valores_linha()`, `enviar()` e, se precisar, `atualizar_opcoes()`.
- Cada linha da tabela usa o id do banco como `iid`. O formulário é recarregado pelo controller,
  a partir desse id, e nunca a partir dos valores exibidos.

## Consequências

- Nenhum `if/elif` por entidade na view.
- O bug do CPF com zero inicial foi corrigido.
- O botão "Salvar" cria um registro novo ou atualiza o registro carregado. Isso substitui os botões "Cadastrar" e "Atualizar".

## Onde está no código

- `src/view/aba_crud.py`: `AbaCrud`.
- `src/view/proprietario_aba.py`, `src/view/propriedade_aba.py`, `src/view/localizacao_aba.py`: abas concretas.
