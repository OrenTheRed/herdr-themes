# Juventus for Herdr

Your coding agents as Juventus players. Two layouts: **JUV** keeps the normal Herdr
window in Juventus colors, **JUV-Stadium** puts the whole squad on a pitch.

![JUV-Stadium](preview.png)

![JUV](preview-classic.png)

## What you see

**JUV-Stadium**, top to bottom:

1. **The pitch**: a night stadium at Allianz Stadium, floodlights, stands, roof and seats in
   Juventus colors, fans and flags in the kit. Top left the stadium name, a scoreboard
   (JUV goals-VAR against the shown space), top right the counts. One player per agent,
   with its shirt number, name, space and tab.
2. **The bar**: every space, then the shown space's tabs, as chips you click; the player you're
   looking at; the keys.
3. **The bench**: the shown tab's terminals, each header naming its player and status.

**JUV**: Herdr's own window with the agents list titled "Bianconeri": each agent wears
the Juventus jersey with a shirt number and a player's name; keepers wear their own kit.

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
- Each agent keeps its player while it lives; the first agent gets Dybala.
  Keepers: Buffon (1), Neto (25), Audero (32).

## Install

Copy into your Herdr app home (`~/.config/herdr-app`, or `$HERDR_APP_HOME`) only names that are free:
`layouts/JUV.json`, `layouts/JUV.svg`, `layouts/JUV-Stadium.json`, `layouts/JUV-Stadium.svg`,
`themes/JUV.json`, `mods/juventus-agents/`, `mods/juventus-stadium/`. Or from the repo root:

```sh
./install.sh juventus
herdr-app check ~/.config/herdr-app/mods/juventus-stadium
herdr-app do layout.switch '{"name":"JUV-Stadium"}'
```

## What it cannot do yet

- Players stand in up to three rows of up to six; with many agents in a narrow window the last
  ones can pass the right edge.
- On a very short pitch block the stadium name and counts move into the scoreboard.

## Squad

2016-17 season squad and shirt numbers, from Wikipedia '2016-17 Juventus FC season' (https://en.wikipedia.org/w/index.php?oldid=1383808656). Edit `squad` in `teams/juventus.json` and run `./install.sh --update juventus`.
