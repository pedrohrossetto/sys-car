# ADR-002: Mapa próprio em Canvas

**Status:** aceita

## Contexto

A área da propriedade (ADR-C05) e o ponto do alerta (ADR-F14) são definidos clicando num mapa.
O projeto usa só a biblioteca padrão do Python (Tkinter e SQLite). Não há `pip install`.

## Decisão

Desenhar o mapa num `tk.Canvas`, sem dependência externa.

- `view/projecao.py`, classe `Projecao`: converte latitude/longitude em pixels e de volta.
  - Projeção equirretangular. Um grau de latitude tem sempre a mesma altura. Um grau de longitude é estreitado por
    `cos(latitude de referência)`, para as áreas não aparecerem esticadas.
  - A latitude de referência só muda ao enquadrar. Mover e dar zoom não deformam o desenho.
  - Zoom mantém parado o ponto sob o cursor. A escala tem limites mínimo e máximo.
  - A grade escolhe o passo (de 10° a 0,00001°) para as linhas ficarem a pelo menos 70 pixels umas das outras.
  - O módulo **não importa tkinter**. Os testes rodam em máquinas sem Tk.
- `view/mapa.py`:
  - `MapaCanvas`: grade com rótulos, áreas (polígonos), pontos (cor pelo status do alerta) e a área em edição.
    Roda do mouse: zoom. Arrastar com o botão esquerdo: mover. Clicar sem arrastar: `ao_clicar(lat, lon)`.
    Botão "Enquadrar tudo". As coordenadas sob o cursor aparecem embaixo do mapa.
  - `EditorArea`: desenho da área de uma propriedade. Cada clique é um vértice. Botões "Desfazer vértice" e "Limpar
    área". Mostra vértices, área (ha) e centro, ou o erro de validação do `Poligono`.
- O mapa aparece nas abas Propriedades (desenhar a área), Alertas (marcar o ponto) e Ficha da Propriedade (só leitura).

## Alternativas descartadas

- **`tkintermapview`** (mapa do OpenStreetMap dentro do Tkinter): tem imagem real de fundo, mas é a primeira
  dependência do projeto (`pip install`) e precisa de internet para carregar o mapa. Na apresentação, sem internet,
  o mapa ficaria em branco.

## Consequências

- O programa continua sem dependências e funciona sem internet.
- O mapa não tem imagem de fundo (ruas, rios, satélite). Ele é um plano de coordenadas com grade.
- A projeção equirretangular deforma em áreas muito grandes ou perto dos polos. Para propriedades rurais, a diferença
  é pequena.
- No macOS, o Tk ignora o `stipple`: o preenchimento das áreas fica sólido em vez de transparente.

## Onde está no código

- `src/view/projecao.py`: `Projecao`
- `src/view/mapa.py`: `MapaCanvas`, `EditorArea`
- `tests/test_view_projecao.py`
