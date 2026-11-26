# Status do trabalho: feito e a fazer

Levantamento de 05/11/2026, feito sobre a `main` (106 testes passando).
Compara o projeto com:

- os requisitos combinados para a **primeira entrega** (T1);
- o **plano de ensino** (aulas 07 a 12), que é a base da **entrega final** (T2, 27/11).

Legenda: ✅ feito · 🟡 parcial · ❌ falta · ➖ não existe de propósito (com ADR).

## 1. Requisitos combinados para a primeira entrega

### Documentação

| Requisito | Status | Onde está / o que falta |
|---|---|---|
| Texto sobre classes, interações e interfaces | ✅ | ADRs em `docs/decisoes/`, `docs/cadastro/` e `docs/fiscalizacao/` |
| Diagramas UML | ✅ | `docs/cadastro/diagramas.pt-br.md` e `docs/fiscalizacao/diagramas.pt-br.md` (casos de uso, sequência, classes, dados); diagrama de pacotes no ADR-001 |
| Imagens | ✅ | Capturas de todas as abas em `docs/imagens/`: Proprietários, Propriedades, Alertas, Unidades e Notificações, Embargos e Declarações e Ficha da Propriedade. Elas aparecem no README e nos guias |
| Português técnico controlado (estilo ASD-STE100) | 🟡 | Cadastro e ADR-001 seguem o padrão. **Falta:** revisar a documentação da Fiscalização (`docs/fiscalizacao/`) no mesmo padrão. As versões em inglês (`*.en.md`) do Cadastro são um extra; o requisito não pede inglês |
| Leitura fácil | ✅ | `docs/cadastro/guia-leitura-facil.md` e `docs/fiscalizacao/guia-leitura-facil.md` |

### Padrões de projeto

| Requisito | Status | Onde está |
|---|---|---|
| Decisões documentadas | ✅ | ADR-001 e ADR-002 (arquitetura e mapa), ADR-C01 a C05 (Cadastro) e ADR-F01 a F14 (Fiscalização) |
| Implementação segue os padrões | ✅ | Template Method (`model/base.py`, `view/aba_crud.py`), Strategy (`model/documento.py`), Factory Method (`model/fiscalizacao/resultado_analise.py`), State (`model/fiscalizacao/status.py`), Observer (`model/fiscalizacao/observador.py`) |

### Interface gráfica

| Requisito | Status | Onde está |
|---|---|---|
| Componentes básicos | ✅ | Notebook, Menu, Entry, Radiobutton, Combobox, Treeview, Scrollbar, Checkbutton, Text, PanedWindow, **Canvas** (mapa, ADR-002), caixas de mensagem e diálogo de salvar arquivo |
| Eventos | ✅ | Enter, Esc, Delete, Ctrl+Q, duplo clique, botão direito, troca de aba, seleção de combobox, validação por tecla; no mapa: clique, arrastar, roda do mouse, movimento do mouse e redimensionar |
| Layouts | ✅ | `pack` e `grid` em todas as abas |

### Padrões de arquitetura

| Requisito | Status | Onde está |
|---|---|---|
| Decisões documentadas | ✅ | ADR-001 (MVC com contrato de plugin) e ADR-F07 |
| Implementação segue os padrões | ✅ | MVC em `src/model`, `src/controller`, `src/view`; a view só importa controller; tabelas e abas descobertas por `src/descoberta.py` |

### Organização do git e GitHub

| Requisito | Status | Onde está / o que falta |
|---|---|---|
| Branches por frente | ✅ | `frente-1-cadastro` e `frente-2-fiscalizacao` |
| Commits padronizados | ✅ | Conventional Commits em português |
| Pull Requests | ✅ | PR 1 (Fiscalização) e PR 2 (Cadastro), mergeados na `main` |
| Issues | ❌ | Nenhuma issue foi criada. **Falta:** uma issue por tarefa da entrega final, fechada pelo PR correspondente |

## 2. Plano de ensino: aulas após a primeira entrega

| Aula | Data | Conteúdo | Status | Situação |
|---|---|---|---|---|
| Ementa | — | Unidade 1.4: **tratamento de exceções** (sem aula própria no cronograma) | ✅ | O model lança, o controller captura e a view mostra. Erros do banco viram `ErroDeBanco` num ponto só (issue #19, ADR-003) |
| 02 | 21/08 | Padrões criacionais: Factory e **Singleton** | ✅ | Factory Method na criação da declaração (ADR-F11, substitui a ADR-F03) e Singleton no `PublicadorAlertas` (ADR-F08) |
| 07 | 09/10 | GUI + SGBD: criar e ler | ✅ | Todas as abas criam e listam registros no SQLite |
| 08 | 16/10 | GUI + SGBD: atualizar e remover | ✅ | Ver tabela de CRUD abaixo (issue #5, ADR-F12 e ADR-F13) |
| 09 | 23/10 | Unificar o acesso a dados com a GUI (MVC): adicionar, listar | ✅ | Todos os models herdam do `ModeloBase` (issue #3, ADR-F09) |
| 10 | 30/10 | Unificar o acesso a dados (MVC): atualizar, remover | ✅ | Mesma situação da aula 09 |
| 11 | 06/11 | Unificar o acesso a dados (MVC): relacionamentos | ✅ | Chaves estrangeiras e `ON DELETE CASCADE` no banco. A aba "Ficha da Propriedade" mostra os dados relacionados juntos (issue #6, ADR-F10) |
| 12 | 13/11 | Persistência com GUI | ✅ | A GUI grava e lê os dados no SQLite; exportação da declaração em `.txt`. Exportar e importar em CSV é um reforço opcional |
| T2 | 27/11 | Entrega e apresentação final | ❌ | — |

### CRUD por entidade (aula 08)

| Entidade | Criar | Listar | Atualizar | Excluir | Tela |
|---|---|---|---|---|---|
| Proprietário | ✅ | ✅ | ✅ | ✅ | Proprietários |
| Propriedade rural (com a área no mapa, ADR-C05) | ✅ | ✅ | ✅ | ✅ | Propriedades |
| Unidade competente | ✅ | ✅ | ✅ | ✅ | Unidades e Notificações |
| Alerta de desmatamento | ✅ | ✅ | ✅ dados pelo formulário, status pelo State (ADR-F12) | ✅ em cascata (ADR-F12) | Alertas |
| Notificação | ✅ automática | ✅ | ✅ "marcar como lida" | ➖ não existe (ADR-F13) | Unidades e Notificações |
| Embargo | ✅ | ✅ | ✅ motivo e "levantar embargo" | ➖ não existe; "levantar" faz o papel (ADR-F13) | Embargos e Declarações |
| Declaração | ✅ | ✅ | ➖ documento imutável (ADR-F13) | ➖ documento imutável (ADR-F13) | Embargos e Declarações |

Nem toda operação faltante precisa existir. Exemplos: uma declaração emitida pode ser tratada como documento que não se apaga; um alerta pode ser "cancelado" pelo State em vez de excluído. Nesses casos, a decisão precisa estar registrada num ADR.

### Acesso a dados (aulas 09 e 10)

- **Cadastro:** os models herdam de `ModeloBase` (`src/model/base.py`), que concentra INSERT, UPDATE, DELETE e SELECT.
- **Fiscalização:** os models também herdam de `ModeloBase`. O `conexao.py` foi removido (issue #3, ADR-F09).

O sistema tem uma só forma de acessar o banco, como pedem as aulas 09 e 10.

## 3. Lista do que falta para a entrega final

### Código

1. ✅ **Unificar o acesso a dados:** os models da Fiscalização usam o `ModeloBase` (aulas 09 e 10, issue #3).
2. ✅ **Singleton:** `PublicadorAlertas.instancia()` (ADR-F08, aula 02, issue #4).
3. ✅ **Completar o CRUD** (aula 08, issue #5): CRUD do alerta (ADR-F12); motivo do embargo editável; operações que não existem de propósito em ADR-F13. Satélite, usuário e evidência saíram do sistema (ADR-F11).
4. ✅ **Relacionamentos na tela:** a aba "Ficha da Propriedade" mostra dono, área (com mapa), alertas, embargo ativo e declarações (aula 11, issue #6).
5. **Persistência (opcional):** exportação/importação em CSV ou backup do banco pelo menu Arquivo (aula 12, issue #7). A aula 12 já está coberta pelo SQLite.
6. ✅ **Testes** para tudo o que foi criado ou alterado: 186 testes automatizados.

### Documentação

7. ✅ ADRs das decisões novas: ADR-F08 a ADR-F14, ADR-C05, ADR-002 e ADR-003.
8. ✅ Diagramas de classe atualizados (issue #12).
9. ✅ Revisão da documentação da Fiscalização em português técnico controlado (issue #8).
10. ✅ Capturas de tela de todas as abas (issue #9).
11. ✅ README atualizado: funcionalidades, padrões de projeto e testes (issue #10).

### Git e GitHub

12. ✅ Uma issue por item desta lista, no milestone "Entrega final – 27/11".
13. ✅ Um branch e um PR por tarefa, com `Closes #N` na descrição.

### Apresentação

14. Roteiro de demonstração (do cadastro até a declaração) e ensaio antes de 27/11.

## 4. Calendário

| Até | Meta |
|---|---|
| 13/11 | Itens 1 e 2 (mexem na base do código, vêm primeiro) e issues criadas |
| 20/11 | Itens 3, 4 e 5 |
| 27/11 | Itens 7 a 11, capturas de tela e ensaio da apresentação |
| 04/12 | P2 — Prova teórica 02 |
