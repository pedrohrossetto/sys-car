# ADR-C03: Remoção do modo console

**Status:** aceita

## Contexto

O programa antigo tinha dois modos: a interface Tkinter e um modo console, usado quando o Tkinter faltava.
O modo console repetia todas as telas em texto, em cerca de 350 linhas.
Cada regra nova precisava ser feita duas vezes.
A Fiscalização não tem modo console. Depois da integração, o console mostraria só metade do sistema.

## Decisão

Remover o modo console (`menu_console.py` e as três views de console) e o `app_tk.py` antigo.
O programa exige Tkinter. Sem Tkinter, o `main.py` mostra como instalar e termina com código 1.

## Consequências

- As regras de tela ficam em um lugar só.
- Em Linux sem o pacote `python3-tk`, o usuário precisa instalar o pacote antes de usar o programa.
  No Windows e no macOS, o instalador oficial do Python já inclui o Tkinter.

## Onde está no código

- `src/main.py`: mensagem `SEM_TKINTER`.
