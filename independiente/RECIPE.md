# Independiente for Herdr

Your coding agents as Independiente players. Two layouts: **CAI** keeps the normal Herdr
window in Independiente colors, **CAI-Stadium** puts the whole squad on a pitch.

![CAI-Stadium](preview.png)

![CAI](preview-classic.png)

## What you see

**CAI-Stadium**, top to bottom:

1. **The pitch**: a night stadium at Estadio Libertadores de America, floodlights, stands, roof and seats in
   Independiente colors, fans and flags in the kit. Top left the stadium name, a scoreboard
   (CAI goals-VAR against the shown space), top right the counts. One player per agent,
   with its shirt number, name, space and tab.
2. **The bar**: every space, then the shown space's tabs, as chips you click; the player you're
   looking at; the keys.
3. **The bench**: the shown tab's terminals, each header naming its player and status.

**CAI**: Herdr's own window with the agents list titled "El Rojo": each agent wears
the Independiente jersey with a shirt number and a player's name; keepers wear their own kit.

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
- Each agent keeps its player while it lives; the first agent gets Cabral.
  Keepers: Rey (33), Blázquez (1), Mele (77).

## Install

Copy into your Herdr app home (`~/.config/herdr-app`, or `$HERDR_APP_HOME`) only names that are free:
`layouts/CAI.json`, `layouts/CAI.svg`, `layouts/CAI-Stadium.json`, `layouts/CAI-Stadium.svg`,
`themes/CAI.json`, `mods/independiente-agents/`, `mods/independiente-stadium/`. Or from the repo root:

```sh
./install.sh independiente
herdr-app check ~/.config/herdr-app/mods/independiente-stadium
herdr-app do layout.switch '{"name":"CAI-Stadium"}'
```

## What it cannot do yet

- Players stand in up to three rows of up to six; with many agents in a narrow window the last
  ones can pass the right edge.
- On a very short pitch block the stadium name and counts move into the scoreboard.

## Squad

current squad and shirt numbers (read 2026-11-11), from Wikipedia 'Club Atlético Independiente' (https://en.wikipedia.org/w/index.php?oldid=1384844882). Edit `squad` in `teams/independiente.json` and run `./install.sh --update independiente`.
