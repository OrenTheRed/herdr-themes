# herdr-themes

Football club themes for the [Herdr](https://herdr.dev) desktop app. Your coding agents become players.

Every team has two looks:

- **Classic**: the normal Herdr window in the team's colors. In the agents list, each agent wears the team jersey with a shirt number and a player's name. A working agent's jersey jogs, and a ball rolls on a small pitch next to it.
- **Stadium**: a full night stadium on top of the window, with the active tab's terminals on "the bench" below. Inspired by Herdr's [pasture](https://github.com/herdrdev/herdr-layout-examples/tree/main/pasture) example.

| State | Classic | Stadium |
| --- | --- | --- |
| working | jersey jogs, ball rolls | player runs with the ball |
| blocked | `VAR` tag | player jumps under a VAR bubble with a yellow card |
| done | `GOL` / `GOAL` tag | player celebrates, arms up |
| idle | ring | player stands and waits |

## Teams

| Team | Layouts | Stadium |
| --- | --- | --- |
| Argentina | `albiceleste`, `albiceleste-stadium` | ![](previews/albiceleste-stadium.svg) |
| Juventus | `juventus`, `juventus-stadium` | ![](previews/juventus-stadium.svg) |
| Atletico Madrid | `atletico-madrid`, `atletico-madrid-stadium` | ![](previews/atletico-madrid-stadium.svg) |
| Independiente | `independiente`, `independiente-stadium` | ![](previews/independiente-stadium.svg) |
| Hapoel Tel Aviv | `hapoel-tel-aviv`, `hapoel-tel-aviv-stadium` | ![](previews/hapoel-tel-aviv-stadium.svg) |

## Install

Needs the Herdr app (it creates `~/.config/herdr-app` on first start) and `python3`.

```sh
./install.sh                 # every team
./install.sh juventus        # one team
```

Then pick a layout in Settings > Look, cycle with `ctrl-shift-l`, or:

```sh
herdr-app do layout.switch '{"name":"albiceleste-stadium"}'
```

`ctrl-alt-shift-escape` always brings back Herdr's default screen.

## How it is built

```
teams/<id>.json      colors, kit, squad, stadium, language: the only file to edit per team
src/classic/         agents-list mod + layout template (a modified copy of Herdr's built-in agents mod)
src/stadium/         stadium mod: pitch, scoreboard, bench strip, terminal headers
build.py             writes dist/<id>/ (layouts, themes, mods, art) and previews/
install.sh           build, then copy dist/ into ~/.config/herdr-app
```

All art (jerseys, players, ball, stadium) is generated SVG from the team colors. Add a team by copying a file in `teams/` and running `./install.sh <new-id>`.

Squads: Argentina uses the 2022 World Cup squad with that tournament's shirt numbers. The clubs use legends, numbered 1 to 15 by lineup position, not their real shirt numbers. Both lists were written from memory and are not checked against a source. Edit `squad` in the team file to change them.

Built for Herdr app 0.1.15.
