# ADR-F11: Remoção das fontes e da evidência, com o Factory Method na declaração

**Status:** aceita. Substitui a [ADR-F03](ADR-F03-factory-method-fontes.pt-br.md) e a [ADR-F05](ADR-F05-validacao-cpf-por-formato.pt-br.md).

## Contexto

Satélite, usuário denunciante e evidência só dizem de onde veio um alerta.
Eles não fazem parte do fluxo principal do sistema: cadastro, alerta, embargo e declaração.
Mesmo assim, eles ocupavam 3 tabelas, a aba "Fontes", o `FonteController`, as regras de CPF e e-mail e muitos testes.

O grupo decidiu reduzir o escopo e remover essas 3 entidades.

Problema: o único Factory Method do sistema estava nas fontes (`FonteDeteccao`, ver ADR-F03).
A aula 02 do plano de ensino pede padrões criacionais: Factory e Singleton.
Sem as fontes, o Factory Method precisa de outro lugar.

## Decisão

1. Remover `Satelite`, `Usuario`, `Evidencia` e `FonteDeteccao`, a aba "Fontes" e o `FonteController`.
   - A tabela `registros_desmatamento` perde as colunas `satelite_id` e `usuario_id` e o `CHECK` de origem.
   - As regras de CPF e e-mail da Fiscalização (ADR-F05) saem junto, porque só o usuário denunciante as usava.
2. Colocar o **Factory Method** na criação da **declaração de conformidade**:
   - `ResultadoAnalise` (abstrata) declara o método fábrica `criar_declaracao(propriedade_id, data)`.
   - `SemPendencias.criar_declaracao()` devolve uma declaração EMITIDA.
   - `ComPendencias(impedimentos).criar_declaracao()` devolve uma declaração NEGADA, com as pendências no motivo.
   - `analisar(impedimentos)` escolhe o resultado concreto.
   - O `ConformidadeController.solicitar_declaracao()` monta a lista de impedimentos e chama
     `analisar(impedimentos).criar_declaracao(...)`. O `if/else` sai do controller.
3. Um banco antigo ainda tem a coluna `satelite_id`. O programa detecta isso (`RegistroDesmatamento.schema_desatualizado()`)
   e pede para apagar o arquivo `data/syscar.db`, como já faz com o proprietário.

## Alternativas descartadas

- **Manter o Factory Method nas fontes, com uma coluna `origem` no alerta:** sem a evidência, as duas fábricas
  só mudariam o valor de uma coluna. O padrão ficaria artificial.
- **Factory Method no proprietário PF/PJ:** o Strategy do documento (ADR-C02) já trata essa diferença.
- **Remover o Factory Method sem substituto:** a aula 02 ficaria sem o padrão Factory.

## Consequências

- Menos código e menos telas: 3 tabelas, 1 aba e 1 controller a menos.
- O sistema não guarda mais a origem do alerta nem as evidências. A descrição do alerta pode citar a origem.
- A declaração tem uma regra de criação diferente para cada resultado. Um resultado novo (por exemplo, "emitida
  com ressalvas") é uma subclasse nova de `ResultadoAnalise`.
- O texto do motivo da declaração negada não mudou.

## Onde está no código

- `src/model/fiscalizacao/resultado_analise.py`: `ResultadoAnalise`, `SemPendencias`, `ComPendencias`, `analisar()`
- `src/controller/fiscalizacao/conformidade_controller.py`: `solicitar_declaracao()`
- `src/model/fiscalizacao/registro_desmatamento.py`: `schema_desatualizado()`
- `src/model/base.py`: `colunas_no_banco()`
- `tests/test_fiscalizacao_conformidade.py`: `TestFactoryMethodDaDeclaracao`
