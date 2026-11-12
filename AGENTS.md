# herdr-themes

Rules for every coding agent (Claude Code reads this file through `CLAUDE.md`).

Football themes for the Herdr desktop app: coding agents shown as players. Each team has a
**classic** layout (the normal Herdr window in team colors) and a **stadium** layout (the squad on
a pitch). `README.md` explains what users see and how they install it.

## Where things live

- Edit the sources, never the generated team folders:
  - `teams/<id>.json`: colors, kits (outfield and keeper), squad, stadium, language. One file per team.
  - `src/classic/`: agents-list mod and layout template, modified from Herdr's built-in agents mod.
  - `src/stadium/main.js`: the stadium mod (pitch, players, scoreboard, navigation bar, terminal headers).
  - `build.py`: writes every team folder (layouts, themes, mods, SVG art, `RECIPE.md`).
  - `install.sh`: builds, then copies into the Herdr app home.
- `argentina/`, `juventus/`, `atletico-madrid/`, `independiente/`, `hapoel-tel-aviv/` are build output.
  Change them only by running `build.py`.
- The Herdr app's mod and layout API: `~/.config/herdr-app/AGENTS.md`, `herdr.d.ts` and
  `gpui-kit.d.ts` in the same folder. Read them before you change a mod.

## Build and check

```sh
python3 build.py              # every team
python3 build.py juventus     # one team (the file name in teams/)
./install.sh --update juventus
herdr-app do layout.switch '{"name":"JUV-Stadium"}'
```

There are no automated tests. After a change, build, install, and look at both layouts of the team
you changed in all four agent states (working, blocked, done, idle). `tools/demo-scene.sh` makes
the demo scene the screenshots use. If the look changed, update `preview.png` and
`preview-classic.png`.

## Rules

- `install.sh` never overwrites a user's files without `--update`, and `--update` backs them up to
  `<app home>/.herdr-themes-backup/<time>/` first. Keep it that way.
- Keep `LICENSE` and `NOTICE` correct: `src/classic/` is derived from Herdr's built-in mod.
- Squads are real squads. When you change one, update its source in `squadNote` in
  `teams/<id>.json` (it ends up in that team's `RECIPE.md`) and in the README if it is listed there.
- Team words follow the team's language (Spanish, Italian or English); add new words to every
  language in `build.py`.
