#!/usr/bin/env python3
"""Build Herdr app themes for every team in teams/*.json.

Each team gets two looks, written to dist/<id>/ in the same shape as
~/.config/herdr-app (layouts/, themes/, mods/):

  classic  layouts/<id>.json          the normal Herdr layout, agents as players
  stadium  layouts/<id>-stadium.json  a full pitch on top, terminals below

Usage: python3 build.py [team-id ...]   (no ids: every team)
"""
import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

WORDS = {
    "es": {
        "working": "atacando", "blocked": "VAR", "done": "GOL", "idle": "en el banco",
        "onPitch": "jugadores en la cancha", "workingCount": "atacando",
        "blockedCount": "en el VAR", "doneCount": "goles", "bench": "EL BANCO",
        "matchday": "FECHA", "shout": "GOOOL!",
        "onBall": "con la pelota", "spaces": "PARTIDOS", "space": "partido", "tab": "tiempo", "player": "jugador",
    },
    "it": {
        "working": "in attacco", "blocked": "VAR", "done": "GOL", "idle": "in panchina",
        "onPitch": "giocatori in campo", "workingCount": "in attacco",
        "blockedCount": "al VAR", "doneCount": "gol", "bench": "LA PANCHINA",
        "matchday": "GIORNATA", "shout": "GOOOL!",
        "onBall": "in possesso", "spaces": "PARTITE", "space": "partita", "tab": "tempo", "player": "giocatore",
    },
    "en": {
        "working": "attacking", "blocked": "VAR", "done": "GOAL", "idle": "on the bench",
        "onPitch": "players on the pitch", "workingCount": "attacking",
        "blockedCount": "at VAR", "doneCount": "goals", "bench": "THE BENCH",
        "matchday": "MATCHDAY", "shout": "GOOAAL!",
        "onBall": "on the ball", "spaces": "MATCHES", "space": "match", "tab": "half", "player": "player",
    },
}

SKIN = "#C68B59"
HAIR = "#2B1D14"


# ---------- art ----------

def kit_fill(k, x, y, w, h, clip_id):
    """A rectangle of the kit: vertical stripes or plain, clipped to clip_id."""
    parts = [f'<g clip-path="url(#{clip_id})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{k["b"]}"/>']
    if k["style"] == "stripes":
        n = 5
        sw = w / n
        for i in range(0, n, 2):
            parts.append(f'<rect x="{x + i * sw:.2f}" y="{y}" width="{sw:.2f}" height="{h}" fill="{k["a"]}"/>')
    else:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{k["a"]}"/>')
    parts.append("</g>")
    return "".join(parts)


def jersey_svg(k):
    shape = "M10 3 L4 6 L1 13 L6 15 L7 12 L7 30 L25 30 L25 12 L26 15 L31 13 L28 6 L22 3 Q16 7 10 3 Z"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        f'<defs><clipPath id="s"><path d="{shape}"/></clipPath></defs>'
        + kit_fill(k, 0, 0, 32, 32, "s")
        + f'<path d="{shape}" fill="none" stroke="#0B0B0B" stroke-width="1.2"/>'
        f'<path d="M12.5 4.2 Q16 6.4 19.5 4.2" fill="none" stroke="{k["collar"]}" stroke-width="1.6"/>'
        "</svg>"
    )


BALL_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'
    '<circle cx="10" cy="10" r="9" fill="#FFFFFF" stroke="#111111" stroke-width="1.2"/>'
    '<polygon points="10,6 13.4,8.5 12.1,12.5 7.9,12.5 6.6,8.5" fill="#111111"/>'
    '<path d="M10 6 L10 1.2 M13.4 8.5 L18.3 7.2 M12.1 12.5 L15 16.6 M7.9 12.5 L5 16.6 M6.6 8.5 L1.7 7.2" stroke="#111111" stroke-width="1.1"/>'
    "</svg>"
)


# A floodlight beam for the player whose terminals are on the bench: soft cone, bright pool.
SPOTLIGHT_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="140" height="220" viewBox="0 0 140 220">'
    '<defs><linearGradient id="beam" x2="0" y2="1"><stop stop-color="#FFF6C8" stop-opacity="0"/>'
    '<stop offset=".55" stop-color="#FFF6C8" stop-opacity=".22"/><stop offset="1" stop-color="#FFF6C8" stop-opacity=".42"/></linearGradient>'
    '<radialGradient id="pool"><stop stop-color="#FFF6C8" stop-opacity=".75"/><stop offset="1" stop-color="#FFF6C8" stop-opacity="0"/></radialGradient></defs>'
    '<path d="M58 0 H82 L136 200 H4 Z" fill="url(#beam)"/>'
    '<ellipse cx="70" cy="202" rx="66" ry="16" fill="url(#pool)"/>'
    "</svg>"
)


def player_svg(k, pose):
    """A front-facing cartoon player, 64x96. pose: stand, run, cheer."""
    socks = k["a"]
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="64" height="96" viewBox="0 0 64 96">',
         '<ellipse cx="32" cy="91" rx="20" ry="4" fill="#000" opacity=".25"/>']
    # legs
    if pose == "run":
        o.append(f'<path d="M26 60 L18 80" stroke="{SKIN}" stroke-width="7" stroke-linecap="round"/>')
        o.append(f'<path d="M38 60 L44 79" stroke="{SKIN}" stroke-width="7" stroke-linecap="round"/>')
        o.append(f'<path d="M20 76 L16 85" stroke="{socks}" stroke-width="7.5" stroke-linecap="round"/>')
        o.append(f'<path d="M43 75 L46 84" stroke="{socks}" stroke-width="7.5" stroke-linecap="round"/>')
        o.append('<ellipse cx="13" cy="87" rx="6" ry="3" fill="#111"/><ellipse cx="49" cy="86" rx="6" ry="3" fill="#111"/>')
    else:
        for x in (26, 38):
            o.append(f'<rect x="{x - 3.5}" y="60" width="7" height="18" rx="3.5" fill="{SKIN}"/>')
            o.append(f'<rect x="{x - 4}" y="72" width="8" height="13" rx="3" fill="{socks}"/>')
            o.append(f'<ellipse cx="{x + (-1 if x < 32 else 1)}" cy="87" rx="6" ry="3" fill="#111"/>')
    # shorts
    o.append(f'<path d="M19 52 L45 52 L47 66 L34 66 L32 60 L30 66 L17 66 Z" fill="{k["shorts"]}" stroke="#0B0B0B" stroke-width="1"/>')
    # arms
    if pose == "cheer":
        arms = [("M21 30 L10 10", "M10 10 L8 5"), ("M43 30 L54 10", "M54 10 L56 5")]
    elif pose == "run":
        arms = [("M21 30 L12 44", "M12 44 L14 50"), ("M43 30 L52 22", "M52 22 L56 17")]
    else:
        arms = [("M21 30 L15 50", "M15 50 L15 55"), ("M43 30 L49 50", "M49 50 L49 55")]
    for sleeve, hand in arms:
        o.append(f'<path d="{sleeve}" stroke="{k["a"]}" stroke-width="8" stroke-linecap="round"/>')
        o.append(f'<path d="{hand}" stroke="{SKIN}" stroke-width="6" stroke-linecap="round"/>')
    # shirt body
    body = "M20 24 Q32 29 44 24 L46 54 L18 54 Z"
    o.append(f'<defs><clipPath id="b"><path d="{body}"/></clipPath></defs>')
    o.append(kit_fill(k, 16, 22, 32, 34, "b"))
    o.append(f'<path d="{body}" fill="none" stroke="#0B0B0B" stroke-width="1.2"/>')
    o.append(f'<path d="M27 25.5 Q32 29 37 25.5" fill="none" stroke="{k["collar"]}" stroke-width="2"/>')
    # head
    o.append(f'<rect x="29" y="19" width="6" height="6" fill="{SKIN}"/>')
    o.append(f'<circle cx="32" cy="13" r="9" fill="{SKIN}"/>')
    o.append(f'<path d="M23 12 Q24 2 32 3 Q41 3 41 12 Q37 7 32 8 Q27 7 23 12 Z" fill="{HAIR}"/>')
    if pose == "cheer":
        o.append('<ellipse cx="32" cy="17" rx="3" ry="2.6" fill="#5A1A1A"/>')
    else:
        o.append('<path d="M29 17 Q32 19 35 17" fill="none" stroke="#5A1A1A" stroke-width="1.2" stroke-linecap="round"/>')
    o.append('<circle cx="28.5" cy="12.5" r="1.2" fill="#1A1A1A"/><circle cx="35.5" cy="12.5" r="1.2" fill="#1A1A1A"/>')
    o.append("</svg>")
    return "".join(o)


def pitch_svg(team):
    """Night stadium: sky, floodlights, stands full of fans, ad boards, the pitch."""
    W, H = 1600, 420
    c, k = team["colors"], team["kit"]
    rnd = random.Random(team["id"])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" preserveAspectRatio="none">',
         '<defs>',
         '<linearGradient id="sky" x2="0" y2="1"><stop stop-color="#050a1a"/><stop offset="1" stop-color="#16244a"/></linearGradient>',
         '<radialGradient id="glow"><stop stop-color="#fffbe6" stop-opacity=".95"/><stop offset=".35" stop-color="#fff3b0" stop-opacity=".35"/><stop offset="1" stop-color="#fff3b0" stop-opacity="0"/></radialGradient>',
         '<linearGradient id="grass" x2="0" y2="1"><stop stop-color="#2c8a3c"/><stop offset="1" stop-color="#1f6e2e"/></linearGradient>',
         '</defs>',
         f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    # stars
    for _ in range(40):
        o.append(f'<circle cx="{rnd.randint(0, W)}" cy="{rnd.randint(0, 50)}" r="{rnd.choice((0.8, 1, 1.3))}" fill="#fff" opacity="{rnd.uniform(.3, .8):.2f}"/>')
    # roof and stands in the club's colors: a dark roof trimmed in the primary color,
    # seat rows striped in the kit colors behind the fans, tier walls in the primary color.
    o.append(f'<rect x="0" y="44" width="{W}" height="18" fill="{c["dark"]}"/>')
    o.append(f'<rect x="0" y="58" width="{W}" height="4" fill="{c["primary"]}"/>')
    for x in range(0, W, 40):
        o.append(f'<rect x="{x + 18}" y="44" width="4" height="14" fill="{c["surface"]}"/>')
    o.append(f'<path d="M0 62 L{W} 62 L{W} 205 L0 205 Z" fill="{c["surface"]}"/>')
    for row in range(14):
        col = k["a"] if row % 2 == 0 else k["b"]
        o.append(f'<rect x="0" y="{66 + row * 9.6:.1f}" width="{W}" height="5" fill="{col}" opacity=".28"/>')
    for y in (110, 158):
        o.append(f'<rect x="0" y="{y}" width="{W}" height="4" fill="{c["primary"]}" opacity=".85"/>')
    # fans
    crowd = team["crowd"]
    for row in range(14):
        y = 70 + row * 9.6
        x = rnd.uniform(0, 6)
        while x < W:
            col = rnd.choice(crowd) if rnd.random() < .78 else rnd.choice(("#c9b8a8", "#3b3b3b", "#8a6a50"))
            o.append(f'<circle cx="{x:.1f}" cy="{y + rnd.uniform(-1.2, 1.2):.1f}" r="3.1" fill="{col}"/>')
            x += rnd.uniform(6.5, 9)
    # big flags in the stands, in kit colors
    for fx in (180, 560, 1040, 1420):
        fy = rnd.randint(72, 120)
        o.append(f'<g transform="translate({fx} {fy}) rotate({rnd.randint(-8, 8)})">'
                 + kit_fill(k, 0, 0, 90, 42, f"f{fx}")
                 + "</g>")
        o.append(f'<defs><clipPath id="f{fx}"><rect width="90" height="42" rx="3"/></clipPath></defs>')
    # floodlights
    for fx in (90, 540, 1060, 1510):
        o.append(f'<rect x="{fx - 3}" y="8" width="6" height="40" fill="{c["surface"]}"/>')
        o.append(f'<rect x="{fx - 26}" y="2" width="52" height="16" rx="3" fill="#cfd6e6"/>')
        o.append(f'<circle cx="{fx}" cy="10" r="95" fill="url(#glow)"/>')
    # ad boards
    o.append(f'<rect x="0" y="205" width="{W}" height="22" fill="{c["dark"]}"/>')
    for i, x in enumerate(range(0, W, 160)):
        col = k["a"] if i % 2 == 0 else c["primary"]
        o.append(f'<rect x="{x + 6}" y="208" width="148" height="16" rx="2" fill="{col}" opacity=".9"/>')
        o.append(f'<rect x="{x + 20}" y="214" width="{rnd.randint(50, 110)}" height="4" rx="2" fill="#fff" opacity=".75"/>')
    # pitch with mowing stripes
    o.append(f'<rect x="0" y="227" width="{W}" height="{H - 227}" fill="url(#grass)"/>')
    for i, x in enumerate(range(0, W, 100)):
        if i % 2:
            o.append(f'<rect x="{x}" y="227" width="100" height="{H - 227}" fill="#ffffff" opacity=".05"/>')
    line = 'fill="none" stroke="#ffffff" stroke-opacity=".75" stroke-width="3"'
    # Touchlines run off the bottom edge: the mod draws more grass below when the block is tall.
    o.append(f'<path d="M20 {H} V240 H{W - 20} V{H}" {line}/>')
    o.append(f'<path d="M{W / 2} 240 V{H}" {line}/>')
    o.append(f'<ellipse cx="{W / 2}" cy="{(240 + H - 15) / 2}" rx="90" ry="60" {line}/>')
    o.append(f'<circle cx="{W / 2}" cy="{(240 + H - 15) / 2}" r="4" fill="#fff" opacity=".8"/>')
    mid = (240 + H - 15) / 2
    for side in (0, 1):
        x0 = 20 if side == 0 else W - 20
        sgn = 1 if side == 0 else -1
        o.append(f'<path d="M{x0} {mid - 80} H{x0 + sgn * 150} V{mid + 80} H{x0}" {line}/>')
        o.append(f'<path d="M{x0} {mid - 35} H{x0 + sgn * 55} V{mid + 35} H{x0}" {line}/>')
        # goal with net
        gx = x0 - sgn * 4
        o.append(f'<rect x="{min(gx, gx - sgn * 16)}" y="{mid - 32}" width="16" height="64" fill="#ffffff" opacity=".15"/>')
        o.append(f'<path d="M{gx} {mid - 32} H{gx - sgn * 16} V{mid + 32} H{gx}" fill="none" stroke="#fff" stroke-width="4"/>')
    o.append("</svg>")
    return "".join(o)


def mini_kit(k, x, y, w, h, cid):
    return f'<defs><clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1"/></clipPath></defs>' + kit_fill(k, x, y, w, h, cid)


def preview_classic(team):
    """Settings > Look tile: sidebar of jerseys beside two terminal panes."""
    c, k = team["colors"], team["kit"]
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="240" height="150" viewBox="0 0 240 150">',
         f'<rect width="240" height="150" rx="6" fill="{c["dark"]}"/>',
         f'<rect x="0" y="0" width="64" height="150" rx="6" fill="{c["surface"]}" opacity=".55"/>',
         f'<rect x="8" y="10" width="34" height="5" rx="2" fill="{c["primary"]}"/>']
    for i in range(5):
        y = 26 + i * 18
        o.append(mini_kit(k, 8, y, 10, 11, f"j{i}"))
        o.append(f'<rect x="22" y="{y + 3}" width="{30 - (i % 3) * 5}" height="4" rx="2" fill="{c["primary"] if i == 0 else c["foreground"]}" opacity="{1 if i == 0 else .5}"/>')
    o.append(f'<rect x="72" y="10" width="76" height="130" rx="4" fill="none" stroke="{c["primary"]}" stroke-width="2"/>')
    o.append(f'<rect x="156" y="10" width="76" height="130" rx="4" fill="none" stroke="{c["surface"]}" stroke-width="2"/>')
    for i in range(6):
        o.append(f'<rect x="80" y="{22 + i * 10}" width="{40 + (i * 13) % 25}" height="3" rx="1.5" fill="{c["foreground"]}" opacity=".45"/>')
        o.append(f'<rect x="164" y="{22 + i * 10}" width="{36 + (i * 17) % 28}" height="3" rx="1.5" fill="{c["foreground"]}" opacity=".35"/>')
    o.append("</svg>")
    return "".join(o)


def preview_stadium(team):
    """Settings > Look tile: crowd and pitch with players on top, the bench below."""
    c, k = team["colors"], team["kit"]
    rnd = random.Random(team["id"] + "-preview")
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="240" height="150" viewBox="0 0 240 150">',
         '<defs><clipPath id="r"><rect width="240" height="150" rx="6"/></clipPath></defs><g clip-path="url(#r)">',
         f'<rect width="240" height="150" fill="{c["dark"]}"/>',
         '<rect width="240" height="34" fill="#1b2233"/>']
    for row in range(4):
        for x in range(4, 240, 7):
            o.append(f'<circle cx="{x + rnd.uniform(-1, 1):.1f}" cy="{6 + row * 7}" r="2.1" fill="{rnd.choice(team["crowd"])}"/>')
    o.append(f'<rect y="34" width="240" height="4" fill="{c["primary"]}"/>')
    o.append('<rect y="38" width="240" height="34" fill="#2c8a3c"/>')
    for x in range(0, 240, 30):
        o.append(f'<rect x="{x}" y="38" width="15" height="34" fill="#fff" opacity=".05"/>')
    o.append('<path d="M120 38 V72" stroke="#fff" stroke-opacity=".7" stroke-width="1"/><circle cx="120" cy="55" r="9" fill="none" stroke="#fff" stroke-opacity=".7"/>')
    for i, x in enumerate((40, 82, 150, 196)):
        y = 44 + (i % 2) * 8
        o.append(mini_kit(k, x, y, 9, 11, f"p{i}"))
        o.append(f'<circle cx="{x + 4.5}" cy="{y - 2.5}" r="2.6" fill="{SKIN}"/>')
    o.append(f'<rect y="72" width="240" height="7" fill="{c["surface"]}"/><rect y="72" width="240" height="1.5" fill="{c["primary"]}"/>')
    o.append(f'<rect x="6" y="84" width="110" height="60" rx="3" fill="none" stroke="{c["primary"]}" stroke-width="2"/>')
    o.append(f'<rect x="124" y="84" width="110" height="60" rx="3" fill="none" stroke="{c["surface"]}" stroke-width="2"/>')
    o.append("</g></svg>")
    return "".join(o)


def _inner(svg_text):
    """The children of an <svg> document, to nest it in another."""
    return svg_text[svg_text.index(">") + 1: svg_text.rindex("</svg>")]


def poster(team):
    """A README picture of the stadium look: every player state, then the bench."""
    c, k, w = team["colors"], team["kit"], WORDS[team["words"]]
    squad = team["squad"]
    font = 'font-family="Helvetica, Arial, sans-serif"'
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="600" viewBox="0 0 1600 600">',
         f'<rect width="1600" height="600" fill="{c["dark"]}"/>',
         f'<svg x="0" y="0" width="1600" height="420">{_inner(pitch_svg(team))}</svg>',
         f'<rect x="20" y="24" width="330" height="62" rx="8" fill="#05070D" opacity=".75"/>',
         f'<text x="34" y="60" {font} font-size="30" font-weight="800" fill="#fff">{team["stadium"]}</text>',
         f'<text x="34" y="78" {font} font-size="13" fill="#fff" opacity=".7">6 {w["onPitch"]}</text>',
         f'<rect x="28" y="236" width="200" height="70" rx="6" fill="#05070D" opacity=".9" stroke="{c["primary"]}" stroke-width="2"/>',
         f'<text x="42" y="256" {font} font-size="10" font-weight="700" fill="#fff" opacity=".55">{w["matchday"]} · WEBSITE</text>',
         f'<text x="42" y="290" font-family="Menlo, monospace" font-size="24" font-weight="800" fill="{c["primary"]}">{team["short"]} <tspan fill="#FFD23F">1-1</tspan> <tspan fill="#fff" opacity=".75">WEB</tspan></text>']
    cast = [("run", 300, 190, "working"), ("cheer", 520, 300, "done"), ("run", 760, 200, "working"),
            ("stand", 990, 300, "blocked"), ("run", 1220, 190, "working"), ("stand", 1420, 300, "idle")]
    for i, (pose, x, y, state) in enumerate(cast):
        name, num = squad[i][0], squad[i][1]
        kit = team["gkKit"] if "gk" in squad[i][2:] else k
        o.append(f'<svg x="{x}" y="{y}" width="64" height="96">{_inner(player_svg(kit, pose))}</svg>')
        if kit.get("numberBg"):
            o.append(f'<rect x="{x + 25}" y="{y + 31}" width="14" height="13" rx="2" fill="{kit["numberBg"][:7]}"/>')
        o.append(f'<text x="{x + 32}" y="{y + 41}" text-anchor="middle" {font} font-size="11" font-weight="800" fill="{kit["number"]}">{num}</text>')
        o.append(f'<rect x="{x + 32 - len(name) * 4 - 8}" y="{y + 98}" width="{len(name) * 8 + 16}" height="19" rx="9" fill="#000" opacity=".65"/>')
        o.append(f'<text x="{x + 32}" y="{y + 112}" text-anchor="middle" {font} font-size="12" font-weight="700" fill="#fff">{name}</text>')
        if state == "working":
            o.append(f'<svg x="{x + 46}" y="{y + 80}" width="14" height="14" viewBox="0 0 20 20">{_inner(BALL_SVG)}</svg>')
        if state == "done":
            o.append(f'<text x="{x + 32}" y="{y - 14}" text-anchor="middle" {font} font-size="18" font-weight="900" fill="{c["accent"]}">{w["shout"]}</text>')
        if state == "blocked":
            o.append(f'<rect x="{x - 32}" y="{y - 36}" width="128" height="26" rx="12" fill="#FFF8E1" stroke="#D49A00" stroke-width="2"/>')
            o.append(f'<rect x="{x - 20}" y="{y - 29}" width="9" height="12" rx="1" fill="#F6C700"/>')
            o.append(f'<text x="{x - 6}" y="{y - 18}" {font} font-size="12" font-weight="700" fill="#5A4200">{w["blocked"]} · Claude Code</text>')
    # counts, top right
    for j, (n, label, col) in enumerate(((3, w["workingCount"], c["primary"]), (1, w["blockedCount"], "#F6C700"), (1, w["doneCount"], c["accent"]))):
        x = 1130 + j * 150
        o.append(f'<rect x="{x}" y="26" width="140" height="26" rx="13" fill="#000" opacity=".65"/>')
        o.append(f'<circle cx="{x + 16}" cy="39" r="4" fill="{col}"/>')
        o.append(f'<text x="{x + 28}" y="43" {font} font-size="12.5" font-weight="600" fill="#fff">{n} {label}</text>')
    # the bench: rail and two terminals
    # navigation bar: spaces, then the shown space's tabs, then the player on the ball
    pr = c["primary"].lstrip("#")
    on_primary = c["dark"] if (0.299 * int(pr[0:2], 16) + 0.587 * int(pr[2:4], 16) + 0.114 * int(pr[4:6], 16)) > 150 else "#FFFFFF"
    o.append(f'<rect y="420" width="1600" height="29" fill="{c["surface"]}"/><rect y="420" width="1600" height="2" fill="{c["primary"]}"/>')
    o.append(f'<text x="14" y="439" {font} font-size="10" font-weight="800" fill="{c["primary"]}">{w["spaces"]}</text>')
    x = 14 + len(w["spaces"]) * 7.5 + 8
    for label, active in (("website", True), ("api", False), ("›", None), ("pricing page", True), ("tests", False)):
        if active is None:
            o.append(f'<text x="{x}" y="440" {font} font-size="15" fill="{c["foreground"]}" opacity=".5">›</text>')
            x += 16
            continue
        cw = len(label) * 7 + 20
        o.append(f'<rect x="{x}" y="425" width="{cw}" height="20" rx="10" fill="{c["primary"] if active else "#FFFFFF"}" opacity="{1 if active else .1}"/>')
        o.append(f'<text x="{x + cw / 2}" y="439" text-anchor="middle" {font} font-size="11.5" font-weight="{800 if active else 600}" fill="{on_primary if active else c["foreground"]}">{label}</text>')
        x += cw + 6
    o.append(f'<text x="1580" y="439" text-anchor="end" {font} font-size="12" font-weight="700" fill="{c["foreground"]}"><tspan fill="{c["accent"]}">▼</tspan> {squad[0][0]} · {w["onBall"]}</text>')
    for j, (title, state, lines, border) in enumerate((
            ("Claude Code", w["working"], ["&gt; Make the pricing page easier to scan.", "Edit src/pages/pricing.astro", "Working / checking accessibility"], c["primary"]),
            ("Codex", w["done"], ["&gt; Clean up the pricing card styles.", "Checks passed: 24 tests, no type errors.", "Done / pricing cards are ready"], c["surface"]))):
        x = 10 + j * 795
        o.append(f'<rect x="{x}" y="458" width="785" height="134" rx="4" fill="{c["dark"]}" stroke="{border}" stroke-width="3"/>')
        o.append(f'<rect x="{x + 1.5}" y="459.5" width="782" height="27" fill="{c["surface"]}"/>')
        o.append(f'<text x="{x + 14}" y="478" {font} font-size="12" font-weight="600" fill="{c["foreground"]}">{title}</text>')
        o.append(f'<text x="{x + 770}" y="478" text-anchor="end" {font} font-size="12" font-weight="600" fill="{c["primary"] if j == 0 else c["accent"]}">{state}</text>')
        for li, line in enumerate(lines):
            o.append(f'<text x="{x + 14}" y="{512 + li * 22}" font-family="Menlo, monospace" font-size="13" fill="{c["foreground"]}" opacity=".85">{line}</text>')
    o.append("</svg>")
    return "".join(o)


# ---------- code and layouts ----------

def team_js(team, mod):
    w = WORDS[team["words"]]
    data = {
        "SQUAD": team["squad"],
        "ASSET": f"mods/{mod}",
        "MOD": mod,
        "C": team["colors"],
        "K": team["kit"],
        "GK": team["gkKit"],
        "W": w,
        "LIST_TITLE": team["listTitle"],
        "STADIUM": team["stadium"],
        "SHORT": team["short"],
        "NAME": team["name"],
    }
    lines = [f"// Written by build.py from teams/{team['id']}.json ({team['squadNote']}). Edit the team file, not this."]
    lines += [f"export const {k} = {json.dumps(v, ensure_ascii=False)};" for k, v in data.items()]
    return "\n".join(lines) + "\n"


def theme_json(team):
    c = team["colors"]
    return {
        "background": c["dark"],
        "foreground": c["foreground"],
        "selection": c["selection"],
        "cursor": c["accent"],
        "ansi": [
            c["surface"], "#E5484D", "#3FB950", "#F6B40E", c["primary"], "#B49BE0", c["light"], "#DCE6F0",
            "#5A6B7D", "#FF6B6F", "#5FD36F", "#FFCB3D", c["light"], "#CDB8F2", "#C9E3F7", "#FFFFFF",
        ],
        "colors": {"accent": c["primary"], "working": c["primary"], "done": c["accent"]},
    }


def classic_layout(team):
    layout = json.loads((ROOT / "src/classic/layout.json").read_text())

    def walk(x):
        if isinstance(x, dict):
            content = x.get("content")
            if isinstance(content, dict) and content.get("mod") == "albiceleste-agents":
                content["mod"] = f"{team['id']}-agents"
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(layout)
    layout["theme"] = team["code"]
    layout["preview"] = f"layouts/{team['code']}.svg"
    return layout


def stadium_layout(team):
    c, mod = team["colors"], f"{team['id']}-stadium"
    return {
        "id": f"{team['id']}-stadium-root", "type": "column", "titlebar": "none", "theme": team["code"],
        "preview": f"layouts/{team['code']}-Stadium.svg",
        "traffic_lights": [12, 16], "font_size": 13, "ui_font": "Geist", "background": c["dark"],
        "colors": {"accent": c["primary"], "border": c["surface"]},
        "terminal_padding": [10, 12], "resizable": False,
        "children": [
            {"id": "stadium-field", "type": "block", "size": {"weight": 0.85}, "content": {"mod": mod}},
            {"id": "stadium-rail", "type": "block", "size": {"px": 44}, "content": {"mod": mod, "props": {"role": "rail"}}},
            {"id": "stadium-bench", "type": "block", "size": {"weight": 1}, "padding": [0, 10], "background": c["dark"],
             "content": {"tab": "active", "pane": {
                 "gap": 10, "radius": 4, "lone": True, "background": c["dark"],
                 "border": {"width": 3, "color": c["surface"]}, "focus": {"width": 3, "color": c["primary"]},
                 "header": {"content": {"mod": mod, "props": {"role": "pane"}}, "height": 28, "position": "top", "reveal": "always"},
             }}},
        ],
    }


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if isinstance(text, str) else json.dumps(text, indent=2, ensure_ascii=False) + "\n")


def build(team):
    """Mods keep the lowercase team id; layouts and themes use the short code the settings list shows."""
    tid, code, k, gk = team["id"], team["code"], team["kit"], team["gkKit"]
    out = DIST / tid
    if out.exists():
        shutil.rmtree(out)
    # classic
    m = out / "mods" / f"{tid}-agents"
    write(m / "main.js", (ROOT / "src/classic/main.js").read_text())
    write(m / "team.js", team_js(team, f"{tid}-agents"))
    write(m / "mod.json", {"place": "none", "title": team["listTitle"]})
    write(m / "jersey.svg", jersey_svg(k))
    write(m / "jersey-gk.svg", jersey_svg(gk))
    write(m / "ball.svg", BALL_SVG)
    write(out / "layouts" / f"{code}.json", classic_layout(team))
    # stadium
    s = out / "mods" / f"{tid}-stadium"
    write(s / "main.js", (ROOT / "src/stadium/main.js").read_text())
    write(s / "team.js", team_js(team, f"{tid}-stadium"))
    write(s / "mod.json", {"place": "none"})
    write(s / "pitch.svg", pitch_svg(team))
    for pose in ("stand", "run", "cheer"):
        write(s / f"{pose}.svg", player_svg(k, pose))
        write(s / f"{pose}-gk.svg", player_svg(gk, pose))
    write(s / "ball.svg", BALL_SVG)
    write(s / "spotlight.svg", SPOTLIGHT_SVG)
    write(out / "layouts" / f"{code}-Stadium.json", stadium_layout(team))
    write(out / "layouts" / f"{code}.svg", preview_classic(team))
    write(out / "layouts" / f"{code}-Stadium.svg", preview_stadium(team))
    # shared colors
    write(out / "themes" / f"{code}.json", theme_json(team))
    # README pictures (not installed)
    write(ROOT / "previews" / f"{tid}-stadium.svg", poster(team))
    write(ROOT / "previews" / f"{tid}.svg", preview_classic(team))
    return out


def main():
    wanted = set(sys.argv[1:])
    teams = [json.loads(p.read_text()) for p in sorted((ROOT / "teams").glob("*.json"))]
    for t in teams:
        if wanted and t["id"] not in wanted:
            continue
        print("built", build(t).relative_to(ROOT))


if __name__ == "__main__":
    main()
