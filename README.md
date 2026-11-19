# THE WORLD TODAY — 19 November 2026

A one-day newspaper front page summing up the world news of Thursday
19 November 2026, drawn entirely in code.

## What it is

`main.py` (Python 3.13, standard library only) draws a 1024x1024
newspaper front page and writes exactly one PNG to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). No network, no
randomness, no time — two runs produce byte-identical output.

The page carries **19 verified stories**:

- Lead: GTA VI begins its global rollout, back to Vice City.
- Trump, Xi and Putin meet at APEC in Shenzhen; Voyager 1 reaches one
  light-day from Earth.
- US–Iran fire across the Gulf; EU offers Ukraine a EUR 45bn loan;
  Israeli tanks cross Gaza's Yellow Line; Anthropic prices a record
  $81.3bn IPO.
- Australia sanctions settlers; the Gas Husky tanker sinks off
  Bulgaria; Peltola wins Alaska 56–44; the US loses measles-free status.
- World in Brief: Deutsche Bank / Epstein files, the NSA outage, Fed
  minutes, the Bayesian report, Haaland, Cyclone Akvan, Nvidia, Carney.

Every story is sourced in `SOURCES.md` (two independent sources each).
One candidate story — the McDonald's UK sex-abuse case — was dropped:
only the BBC report could be confirmed in search.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## How it is drawn

- A hand-written 5x7 pixel font (A–Z, 0–9, punctuation).
- A hand-written PNG encoder (zlib + CRC, filter 0).
- Pixel-art illustrations per story: neon Vice City skyline, Shenzhen
  towers and three leaders, Voyager 1's gold dish, Gulf fire, the EU
  stars, a Gaza tank at the Yellow Line, IPO bars, and more.

## Files

- `main.py` — the whole entry.
- `README.md` — this file.
- `SOURCES.md` — every story with its sources and date note.
- `LICENSE` — MIT.
