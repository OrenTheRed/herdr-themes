# Argentina for Herdr

Your coding agents as Argentina players. Two layouts: **albiceleste** keeps the normal Herdr
window in Argentina colors, **albiceleste-Stadium** puts the whole squad on a pitch.

![albiceleste-Stadium](preview.png)

![albiceleste](preview-classic.png)

## What you see

**albiceleste-Stadium**, top to bottom:

1. **The pitch**: a night stadium at Estadio Libertadores de America, floodlights, stands, roof and seats in
   Argentina colors, fans and flags in the kit. Top left the stadium name, a scoreboard
   (ARG goals-VAR against the shown space), top right the counts. One player per agent,
   with its shirt number, name, space and tab.
2. **The bar**: every space, then the shown space's tabs, as chips you click; the player you're
   looking at; the keys.
3. **The bench**: the shown tab's terminals, each header naming its player and status.

**albiceleste**: Herdr's own window with the agents list titled "La Scaloneta": each agent wears
the Argentina jersey with a shirt number and a player's name; keepers wear their own kit.

## How it behaves

| Status | Stadium | Classic |
| --- | --- | --- |
| working | runs left and right with the ball at its feet | jersey jogs, a ball rolls on a small pitch |
| blocked | jumps under a "VAR · program" bubble with a yellow card | `VAR` tag |
| done | celebrates, arms up, "GOOOL!" | `GOL` tag |
| idle | stands, breathing | ring |

- The agent you're looking at stands in a floodlight beam with the captain's armband and a
  bouncing marker. Agents in the shown tab wear a bright name tag; the rest are dimmed.
- Click a player to show its agent, or a chip in the bar to show a space or tab. Keys:
  `⌘⌥[` `⌘⌥]` space, `⌘⇧[` `⌘⇧]` tab, `⌘[` `⌘]` player.
- Each agent keeps its player while it lives; the first agent gets Messi.
  Keepers: Dibu (23), Musso (1), Rulli (12).

## Install

Copy into your Herdr app home (`~/.config/herdr-app`, or `$HERDR_APP_HOME`) only names that are free:
`layouts/albiceleste.json`, `layouts/albiceleste.svg`, `layouts/albiceleste-Stadium.json`, `layouts/albiceleste-Stadium.svg`,
`themes/albiceleste.json`, `mods/albiceleste-agents/`, `mods/albiceleste-stadium/`. Or from the repo root:

```sh
./install.sh albiceleste
herdr-app check ~/.config/herdr-app/mods/albiceleste-stadium
herdr-app do layout.switch '{"name":"albiceleste-Stadium"}'
```

## What it cannot do yet

- Players stand in up to three rows of up to six; with many agents in a narrow window the last
  ones can pass the right edge.
- On a very short pitch block the stadium name and counts move into the scoreboard.

## Squad

2026 World Cup squad and shirt numbers, from https://mundoalbiceleste.com/2026/05/28/argentina-national-team-shirt-numbers-announced-for-world-cup-lionel-messi-to-wear-10-for-record-time/. Edit `squad` in `teams/albiceleste.json` and run `./install.sh --update albiceleste`.
