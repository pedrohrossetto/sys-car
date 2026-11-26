# ADR-C05: Área da propriedade como polígono obrigatório

**Status:** aceita

## Contexto

A `Localizacao` era uma tabela 1:1 com a propriedade. Ela guardava um ponto central digitado à mão (latitude e
longitude), a altitude e um polígono **opcional** em texto.

Problemas:

- o ponto central podia ficar fora do polígono, porque os dois eram digitados separadamente;
- sem polígono, o sistema não sabe se um alerta de desmatamento caiu dentro da propriedade;
- a aba "Localizações" era uma tela a mais para um dado que pertence à propriedade.

O grupo decidiu definir a geografia num mapa: cada propriedade tem uma **área** desenhada clique a clique.

## Decisão

1. A `Localizacao` (tabela `localizacoes`, controller e aba) sai do sistema. A altitude sai junto.
2. A propriedade ganha a coluna `poligono`: a área, no texto `lat,lon;lat,lon;...` (`model/coordenadas.py`).
   - No banco, a coluna aceita NULL. O contrato com a Fiscalização pede que colunas novas aceitem NULL.
   - O `PropriedadeRuralController` exige a área: sem área, a propriedade não é salva.
3. A classe `Poligono` (`model/geometria.py`) guarda a lógica. Ela é um **objeto de valor**: não tem tabela.
   - Validação: no mínimo 3 vértices, faixas de latitude e longitude, área diferente de zero e lados que não se cruzam.
   - `centroide()`: o centro da área. Ele substitui a latitude e a longitude da antiga Localização.
   - `area_ha()`: a área em hectares. Os vértices são projetados em metros em torno da latitude média.
   - `contem(lat, lon)`: se o ponto está dentro da área. Um ponto na borda conta como dentro.
   - `sobrepoe(outro)`: se duas áreas têm interior em comum. Encostar num lado ou num vértice não conta.
4. **Duas propriedades não podem se sobrepor.** O controller compara a área nova com as outras (no update, ele
   ignora a própria propriedade). Assim, cada ponto do mapa pertence a no máximo uma propriedade.
5. A `PropriedadeRural` expõe `area`, `centroide`, `area_ha` e `contem()`, calculados a partir do `poligono`.

## Alternativas descartadas

- **Manter a tabela `localizacoes` sem aba:** mais uma tabela e um join para um dado que é da propriedade.
- **Centro digitado e área opcional:** o centro podia ficar fora da área, e alertas sem área não podem ser ligados
  a uma propriedade.
- **Permitir sobreposição (a propriedade mais antiga ganha):** um ponto poderia ser de duas propriedades.

## Consequências

- O centro da propriedade nunca fica fora da área.
- O alerta pode descobrir a sua propriedade pelo ponto (ver ADR-F14 da Fiscalização).
- Uma propriedade gravada direto no banco, sem área, tem `area`, `centroide` e `area_ha` iguais a None e não contém
  nenhum ponto.
- Um banco antigo (sem a coluna `poligono`) é detectado na abertura. O programa pede para apagar `data/syscar.db`.

## Onde está no código

- `src/model/geometria.py`: `Poligono`
- `src/model/propriedade_rural.py`: coluna `poligono`, `area`, `centroide`, `area_ha`, `contem()`, `schema_desatualizado()`
- `src/controller/propriedade_rural_controller.py`: `_validar_area()`, `listar_areas()`
- `tests/test_cadastro_geometria.py`, `tests/test_cadastro_propriedade_area.py`
