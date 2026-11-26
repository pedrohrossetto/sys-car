# Roteiro da apresentação final (T2, 27/11)

Este roteiro mostra a ordem da demonstração, o que cada parte cumpre do plano de ensino e quem fala.
A divisão de quem fala é uma proposta. O grupo confirma a divisão no ensaio de 26/11.

Tempo total previsto: 15 minutos.

## Antes de começar

1. Apague o banco antigo: o arquivo `data/syscar.db`.
2. Grave os dados de exemplo. A partir da pasta `src`:

   ```bash
   python3 dados_exemplo.py
   ```

   O script grava 3 proprietários, 3 propriedades vizinhas, 3 unidades, 5 alertas, 1 embargo e 2 declarações.
   Ele só grava num banco vazio.
3. Abra o sistema: `python3 src/main.py`.
4. Deixe aberto no editor: `src/model/base.py`, `src/model/fiscalizacao/status.py` e `src/model/fiscalizacao/resultado_analise.py`.

### Dados de exemplo

| Propriedade | Proprietário | Situação | Por quê |
|---|---|---|---|
| Sítio Boa Vista | Ana Souza (PF) | COM ALERTAS EM ABERTO | Tem um alerta PENDENTE |
| Fazenda Planalto | Agropecuária Planalto Ltda (PJ) | EMBARGADA | Alerta CONFIRMADO e embargo ativo do IBAMA. A declaração foi NEGADA |
| Chácara Santa Rita | João Pereira (PF) | REGULAR | Um alerta RESOLVIDO e um CANCELADO. A declaração foi EMITIDA |

Um quinto alerta fica fora de todas as áreas ("fora de propriedade cadastrada").

## Roteiro

| # | Parte | O que mostrar | Aula ou requisito | Quem fala | Tempo |
|---|---|---|---|---|---|
| 1 | Abertura | O problema: o CAR registra as propriedades rurais, e a fiscalização acompanha o desmatamento. As 6 abas do sistema | T2: entrega e apresentação final | Eduardo | 1 min |
| 2 | Arquitetura | MVC com contrato de plugin: cada model declara `SCHEMA`, cada aba declara `ORDEM` e `registrar_abas`. A janela descobre as abas sozinha. Diagrama de pacotes do ADR-001 | Padrões de arquitetura (ADR-001) | Eduardo | 2 min |
| 3 | Cadastrar proprietário | Criar um proprietário PF com CPF inválido (erro na tela) e depois com CPF válido. Mostrar a máscara de CPF e CNPJ | Aula 07 (criar e ler). Strategy na validação do documento (ADR-C02) | Pedro | 1 min |
| 4 | Cadastrar propriedade | Desenhar a área no mapa (clique, arrastar, roda do mouse). Tentar sobrepor a área de outra propriedade (o sistema recusa). Editar e excluir | Aula 08 (atualizar e remover). Canvas e eventos (ADR-002, ADR-C05) | Pedro | 2 min |
| 5 | Marcar alerta | Clicar no mapa dentro do Sítio Boa Vista. O sistema mostra a propriedade do ponto. Salvar. Mostrar o alerta fora de todas as áreas | ADR-F14 (o ponto define a propriedade). Aula 11 (relacionamentos) | Matheus | 1 min |
| 6 | Notificar unidades | Aba Unidades e Notificações: cada unidade recebeu uma notificação do alerta novo. Marcar como lida | Observer (ADR-F02) e Singleton no publicador (ADR-F08, aula 02) | Matheus | 1 min |
| 7 | Confirmar o alerta | Botão direito no alerta: o menu mostra só as mudanças permitidas. Confirmar | State no status do alerta (ADR-F01) | Matheus | 1 min |
| 8 | Embargar | Aba Embargos e Declarações: embargar o Sítio com o alerta confirmado. Alterar o motivo. Levantar o embargo | Aula 08. Embargo como entidade (ADR-F06, ADR-F13) | Victor | 1 min |
| 9 | Pedir declaração | Pedir a declaração da Fazenda (NEGADA, com as pendências) e da Chácara (EMITIDA). Salvar em `.txt` | Factory Method na declaração (ADR-F11, aula 02). Aula 12 (persistência) | Victor | 2 min |
| 10 | Ficha da propriedade | Escolher cada propriedade: proprietário, área no mapa, alertas, embargo e declarações numa tela só. Mostrar as 3 situações | Aula 11 (relacionamentos na GUI, ADR-F10) | Eduardo | 1 min |
| 11 | Código e qualidade | `ModeloBase` (Template Method, um só acesso a dados). Estratégia de exceções: o model lança, o controller captura, a view mostra. Rodar os testes | Aulas 09 e 10 (ADR-F09). Unidade 1.4 da ementa (ADR-003). Testes automatizados | Victor | 1 min |
| 12 | Documentação e fechamento | ADRs em português controlado e em inglês ASD-STE100, diagramas UML, guias em Leitura Fácil. Issues, milestone e PRs no GitHub | Requisitos de documentação e de organização do git | Eduardo | 1 min |

## Perguntas prováveis

| Pergunta | Resposta curta | Onde está |
|---|---|---|
| Por que a declaração não pode ser excluída? | Ela é um documento entregue a alguém. Mudar ou apagar faria o documento diferir do sistema | ADR-F13 |
| Por que o Singleton não troca o `__new__`? | Os testes precisam de publicadores isolados, e cada controller inscreveria o notificador de novo | ADR-F08 |
| O que acontece se o banco falhar? | O `ModeloBase` lança `ErroDeBanco` com mensagem em português. O controller devolve `(None, "mensagem")` e a tela mostra | ADR-003 |
| Por que o mapa não usa uma biblioteca? | O Canvas do Tkinter basta, e o sistema não depende de internet nem de instalação extra | ADR-002 |
| Por que um alerta pode ficar sem propriedade? | O desmatamento aconteceu mesmo fora de uma área cadastrada. O alerta continua no mapa | ADR-F14 |

## Ensaio (26/11)

- [ ] Rodar o roteiro inteiro com os dados de exemplo, do passo 1 ao 12.
- [ ] Cronometrar cada parte.
- [ ] Confirmar quem fala cada parte.
- [ ] Rodar os testes: `python3 -m unittest discover -s tests`.
