# Status do trabalho: feito e a fazer

Levantamento de 05/11/2026, feito sobre a `main` (106 testes passando).
Compara o projeto com:

- os requisitos combinados para a **primeira entrega** (T1);
- o **plano de ensino** (aulas 07 a 12), que é a base da **entrega final** (T2, 27/11).

Legenda: ✅ feito · 🟡 parcial · ❌ falta.

## 1. Requisitos combinados para a primeira entrega

### Documentação

| Requisito | Status | Onde está / o que falta |
|---|---|---|
| Texto sobre classes, interações e interfaces | ✅ | ADRs em `docs/decisoes/`, `docs/cadastro/` e `docs/fiscalizacao/` |
| Diagramas UML | ✅ | `docs/cadastro/diagramas.pt-br.md` e `docs/fiscalizacao/diagramas.pt-br.md` (casos de uso, sequência, classes, dados); diagrama de pacotes no ADR-001 |
| Imagens | 🟡 | Capturas do Cadastro em `docs/imagens/` (README e guia do Cadastro). **Falta:** capturas das abas da Fiscalização |
| Português técnico controlado (estilo ASD-STE100) | 🟡 | Cadastro e ADR-001 seguem o padrão. **Falta:** revisar a documentação da Fiscalização (`docs/fiscalizacao/`) no mesmo padrão. As versões em inglês (`*.en.md`) do Cadastro são um extra; o requisito não pede inglês |
| Leitura fácil | ✅ | `docs/cadastro/guia-leitura-facil.md` e `docs/fiscalizacao/guia-leitura-facil.md` |

### Padrões de projeto

| Requisito | Status | Onde está |
|---|---|---|
| Decisões documentadas | ✅ | ADR-C01 a C04 (Cadastro) e ADR-F01 a F08 (Fiscalização) |
| Implementação segue os padrões | ✅ | Template Method (`model/base.py`, `view/aba_crud.py`), Strategy (`model/documento.py`), Factory Method (`model/fiscalizacao/fonte.py`), State (`model/fiscalizacao/status.py`), Observer (`model/fiscalizacao/observador.py`) |

### Interface gráfica

| Requisito | Status | Onde está |
|---|---|---|
| Componentes básicos | ✅ | Notebook, Menu, Entry, Radiobutton, Combobox, Treeview, Scrollbar, Checkbutton, Listbox, Text, Toplevel, PanedWindow, caixas de mensagem e diálogo de salvar arquivo |
| Eventos | ✅ | Enter, Esc, Delete, Ctrl+Q, duplo clique, botão direito, troca de aba, seleção de combobox, validação por tecla, saída de foco |
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
| 02 | 21/08 | Padrões criacionais: Factory e **Singleton** | ✅ | Factory Method nas fontes (ADR-F03) e Singleton no `PublicadorAlertas` (ADR-F08) |
| 07 | 09/10 | GUI + SGBD: criar e ler | ✅ | Todas as abas criam e listam registros no SQLite |
| 08 | 16/10 | GUI + SGBD: atualizar e remover | 🟡 | Ver tabela de CRUD abaixo |
| 09 | 23/10 | Unificar o acesso a dados com a GUI (MVC): adicionar, listar | 🟡 | Funciona, mas há **duas camadas de acesso a dados** (ver abaixo) |
| 10 | 30/10 | Unificar o acesso a dados (MVC): atualizar, remover | 🟡 | Mesma situação da aula 09 |
| 11 | 06/11 | Unificar o acesso a dados (MVC): relacionamentos | 🟡 | Chaves estrangeiras e `ON DELETE CASCADE` no banco. **Falta:** uma tela que mostre os dados relacionados juntos |
| 12 | 13/11 | Persistência com GUI | ✅ | A GUI grava e lê os dados no SQLite; exportação da declaração em `.txt`. Exportar e importar em CSV é um reforço opcional |
| T2 | 27/11 | Entrega e apresentação final | ❌ | — |

### CRUD por entidade (aula 08)

| Entidade | Criar | Listar | Atualizar | Excluir | Tela |
|---|---|---|---|---|---|
| Proprietário | ✅ | ✅ | ✅ | ✅ | Proprietários |
| Propriedade rural | ✅ | ✅ | ✅ | ✅ | Propriedades |
| Localização | ✅ | ✅ | ✅ | ✅ | Localizações |
| Satélite | ✅ | ✅ | ✅ | ✅ | Fontes |
| Usuário denunciante | ✅ | ✅ | ✅ | ✅ | Fontes |
| Unidade competente | ✅ | ✅ | ✅ | ✅ | Unidades e Notificações |
| Alerta de desmatamento | ✅ | ✅ | 🟡 só o status | ❌ | Alertas |
| Evidência | ✅ | ✅ | ❌ | ❌ | Alertas |
| Notificação | ✅ automática | ✅ | 🟡 só "marcar como lida" | ❌ | Unidades e Notificações |
| Embargo | ✅ | ✅ | 🟡 só "levantar embargo" | ❌ | Embargos e Declarações |
| Declaração | ✅ | ✅ | ❌ | ❌ | Embargos e Declarações |

Nem toda operação faltante precisa existir. Exemplos: uma declaração emitida pode ser tratada como documento que não se apaga; um alerta pode ser "cancelado" pelo State em vez de excluído. Nesses casos, a decisão precisa estar registrada num ADR.

### Acesso a dados (aulas 09 e 10)

- **Cadastro:** os models herdam de `ModeloBase` (`src/model/base.py`), que concentra INSERT, UPDATE, DELETE e SELECT.
- **Fiscalização:** os models usam `src/model/fiscalizacao/conexao.py` e cada um escreve o próprio SQL (exemplo: `src/model/fiscalizacao/embargo.py`).

O sistema tem, portanto, duas formas de acessar o banco. A aula 09 pede uma lógica única.

## 3. Lista do que falta para a entrega final

### Código

1. **Unificar o acesso a dados:** fazer os models da Fiscalização usarem o `ModeloBase` (aulas 09 e 10).
2. ~~**Singleton:**~~ feito no `PublicadorAlertas` com `PublicadorAlertas.instancia()` (ADR-F08, aula 02).
3. **Completar o CRUD** de alertas, evidências, embargos, declarações e notificações, ou documentar por que uma operação não existe (aula 08).
4. **Relacionamentos na tela:** uma "ficha da propriedade" com dono, localização, alertas, embargo ativo e declarações (aula 11).
5. **Persistência (opcional):** exportação/importação em CSV ou backup do banco pelo menu Arquivo (aula 12).
6. **Testes** para tudo o que for criado ou alterado.

### Documentação

7. ADRs das decisões novas: ~~Singleton~~ (ADR-F08), unificação do acesso a dados e operações que não existem de propósito.
8. Diagramas de classe atualizados depois da unificação (o Singleton já está no diagrama da Fiscalização).
9. Revisão da documentação da Fiscalização em português técnico controlado (estilo ASD-STE100).
10. Capturas de tela das abas da Fiscalização e das telas novas.
11. README atualizado.

### Git e GitHub

12. Uma issue por item desta lista, com responsável.
13. Um branch e um PR por tarefa, com `Closes #N` na descrição.

### Apresentação

14. Roteiro de demonstração (do cadastro até a declaração) e ensaio antes de 27/11.

## 4. Calendário

| Até | Meta |
|---|---|
| 13/11 | Itens 1 e 2 (mexem na base do código, vêm primeiro) e issues criadas |
| 20/11 | Itens 3, 4 e 5 |
| 27/11 | Itens 7 a 11, capturas de tela e ensaio da apresentação |
| 04/12 | P2 — Prova teórica 02 |
