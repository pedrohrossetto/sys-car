# ADR-F04: Coordenadas embutidas no registro

**Status:** aceita

## Contexto

No modelo conceitual, `REGISTRO_DESMATAMENTO` é composto por uma `LOCALIZACAO`.
Na implementação do Cadastro, a tabela `localizacoes` tem `propriedade_id UNIQUE NOT NULL`:
cada localização pertence a uma propriedade, em relação 1:1.
Para usar essa tabela nos alertas, seria necessário mudar uma tabela do Cadastro.
Isso também cria dependência entre as duas áreas.

## Decisão

O registro guarda as próprias coordenadas: as colunas `latitude` e `longitude` ficam na tabela `registros_desmatamento`.
A relação de composição continua: o sistema cria e apaga as coordenadas junto com o alerta.
O alerta também aponta para a propriedade (`propriedade_id`), com `ON DELETE CASCADE`.

## Consequências

- A Fiscalização não altera nenhuma tabela do Cadastro.
- O banco valida as faixas: latitude entre -90 e 90 e longitude entre -180 e 180.
- O alerta guarda um ponto, não um polígono.
- O sistema não verifica se o ponto está dentro do polígono da propriedade. Essa verificação está fora do escopo.

## Onde está no código

- `src/model/fiscalizacao/registro_desmatamento.py`: `SCHEMA`
