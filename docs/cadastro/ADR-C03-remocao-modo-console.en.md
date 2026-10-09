# ADR-C03: Removal of the console mode

**Status:** accepted

## Context

The old program had two modes: the Tkinter interface and a console mode for computers without Tkinter.
The console mode had a text copy of all screens, in approximately 350 lines.
It was necessary to write each new rule two times.
Inspection does not have a console mode. After the merge, the console would show only half of the system.

## Decision

Remove the console mode (`menu_console.py` and the three console views) and the old `app_tk.py`.
The program needs Tkinter. If Tkinter is not available, `main.py` shows how to install it and stops with code 1.

## Consequences

- The screen rules are in one location only.
- On Linux without the package `python3-tk`, the user must install the package first.
  On Windows and macOS, the official Python installer includes Tkinter.

## Location in the code

- `src/main.py`: message `SEM_TKINTER`.
