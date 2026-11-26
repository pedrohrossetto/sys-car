# ADR-F14: O ponto do alerta define a propriedade

**Status:** aceita. Substitui a [ADR-F04](ADR-F04-coordenadas-embutidas-no-registro.pt-br.md) e altera a
[ADR-F12](ADR-F12-crud-do-alerta.pt-br.md).

## Contexto

A ADR-F04 guardava as coordenadas no alerta, mas a propriedade era escolhida numa lista, separada do ponto.
Ela deixava fora do escopo a verificação "o ponto está dentro da área da propriedade?".

Agora toda propriedade tem uma área, e as áreas não se sobrepõem ([ADR-C05](../cadastro/ADR-C05-area-da-propriedade.pt-br.md)).
O alerta é marcado com um clique no mapa ([ADR-002](../decisoes/ADR-002-mapa-em-canvas.pt-br.md)).

## Decisão

1. O alerta é criado só com o ponto (`AlertaController.criar(descricao, latitude, longitude, data)`).
2. A propriedade do alerta é **a que contém o ponto**: `propriedade_no_ponto()` no contrato com o Cadastro
   (`controller/fiscalizacao/propriedades.py`, ver ADR-F07). Como as áreas não se sobrepõem, há no máximo uma.
3. Se o ponto não cai em nenhuma área, o alerta fica **sem propriedade** (`propriedade_id` NULL).
   - Ele aparece no mapa e na lista ("fora de propriedade cadastrada") e notifica as unidades.
   - Ele não bloqueia declaração e não permite embargo: o embargo continua exigindo um alerta CONFIRMADO da propriedade.
4. O vínculo é gravado na criação. **O ponto não muda depois**: o update altera só a descrição e a data.
   Para corrigir um ponto, o usuário exclui o alerta e cria outro. Isso altera a ADR-F12, que permitia mudar as coordenadas.
5. Apagar uma propriedade **não apaga** os alertas dela: `ON DELETE SET NULL`. O desmatamento aconteceu; o alerta
   fica no mapa, sem propriedade. Os embargos e as declarações da propriedade continuam sendo apagados em cascata.

## Alternativas descartadas

- **Propriedade calculada a cada consulta (sem a coluna):** a propriedade de um alerta mudaria sozinha quando uma
  área fosse editada, e o embargo poderia ficar ligado a um alerta de outra propriedade.
- **Ponto móvel, recalculando a propriedade:** o mesmo problema com os embargos.
- **Apagar os alertas junto com a propriedade:** apagaria o registro de um desmatamento que aconteceu.

## Riscos aceitos

- Editar a área de uma propriedade **não religa** os alertas antigos. Um alerta pode ficar ligado a uma propriedade
  cuja área nova não contém mais o ponto, ou sem propriedade embora o ponto esteja numa área desenhada depois.
- Um banco antigo (propriedade sem `poligono`) é detectado na abertura, e o programa pede para apagar `data/syscar.db`.

## Onde está no código

- `src/model/fiscalizacao/registro_desmatamento.py`: `propriedade_id` opcional, `ON DELETE SET NULL`
- `src/controller/fiscalizacao/propriedades.py`: `propriedade_no_ponto()`, `listar_areas()`
- `src/controller/fiscalizacao/alerta_controller.py`: `criar()`, `atualizar()`, `descrever_local()`
- `src/view/fiscalizacao/alertas_aba.py`: clique no mapa
- `tests/test_fiscalizacao_alertas.py`, `tests/test_fiscalizacao_conformidade.py`
