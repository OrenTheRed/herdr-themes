// Stadium: your agents are players on the pitch, the active tab's terminals sit on the bench below.
// Working players run with the ball, a blocked one jumps under a VAR bubble, a finished one
// celebrates, idle ones stand and wait. The player you're looking at stands in a floodlight with
// the captain's armband; the others in the shown tab wear a bright name tag.
// One mod draws all three parts, picked by props().role: none for the pitch, "rail" for the
// navigation bar (spaces and tabs), "pane" for terminal headers.

import { View, div, image, svg } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { agents, spaces, panes, focused, props, run, settings, shared, setShared, setAgentOrder } from "herdr";
import { SQUAD, ASSET, MOD, C, K, GK, W, STADIUM, SHORT } from "./team.js";

// Who wears which shirt. The pitch copy decides and publishes it here, so the bar and the
// terminal headers (other copies, each with its own localStorage) name the same players.
const PLAYERS_KEY = `${MOD}.players`;

const icon = (p, color) => (p?.icon ? (p.tint ? svg(p.icon).text_color(color) : image(p.icon)).size(15) : div().size(15));
const WORD = { working: W.working, blocked: W.blocked, done: W.done, idle: W.idle };
const DOT = { working: C.primary, blocked: "#F6C700", done: C.accent, idle: "#FFFFFF55" };
// Readable text on a primary-colored chip: dark on light primaries, white on dark ones.
const ON_PRIMARY = (() => {
  const h = C.primary.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  return 0.299 * r + 0.587 * g + 0.114 * b > 150 ? C.dark : "#FFFFFF";
})();

export default class Stadium extends View {
  init(_props, cx) {
    this.step = 0;
    this.raw = { width: 1400, height: 400 };
    this.players = JSON.parse(localStorage.getItem("players") ?? "{}");
    // Publish what the pitch remembers, outside render (setShared re-renders every mod).
    if (!props()?.role) cx.spawn(async () => setShared(PLAYERS_KEY, { ...this.players }));
    // The timer only moves where running players are headed; .transition does the moving.
    if (!props()?.role) cx.timer.every(3800, (cx) => { this.step++; cx.notify(); });
  }

  // Each live agent wears the first shirt no other live agent wears, kept across restarts.
  pick(list, cx) {
    const live = new Set(list.map((a) => a.address));
    let dirty = false;
    for (const [k, i] of Object.entries(this.players)) {
      // Gone agents, and shirts a shorter or edited squad no longer has, are given back.
      const valid = Number.isInteger(i) && i >= 0 && i < SQUAD.length;
      if (!valid || (!live.has(k) && list.length)) { delete this.players[k]; dirty = true; }
    }
    const taken = new Set(Object.values(this.players));
    for (const a of list) {
      if (this.players[a.address] != null) continue;
      let i = SQUAD.findIndex((_, j) => !taken.has(j));
      if (i < 0) i = Object.keys(this.players).length % SQUAD.length;
      this.players[a.address] = i;
      taken.add(i);
      dirty = true;
    }
    if (!dirty) return;
    localStorage.setItem("players", JSON.stringify(this.players));
    const snapshot = { ...this.players };
    cx.spawn(async () => setShared(PLAYERS_KEY, snapshot));
  }

  // The pitch copy reads its own assignment; the bar and headers read the published one.
  squadOf(a) {
    const map = props()?.role ? (shared(PLAYERS_KEY) ?? {}) : this.players;
    const [name, num, role] = SQUAD[(map[a.address] ?? 0) % SQUAD.length];
    return { name, num, gk: role === "gk" };
  }

  // captain: the agent you're looking at. bench: its terminals are in the shown tab.
  player(a, i, slot, captain, bench) {
    const { name, num, gk } = this.squadOf(a);
    const kit = gk ? GK : K;
    const working = a.status === "working", blocked = a.status === "blocked", done = a.status === "done";
    const pose = done ? "cheer" : working ? "run" : "stand";
    const drift = working ? Math.sin(this.step * 0.9 + i * 1.7) * Math.min(60, slot.w * 0.3) : 0;

    const sprite = div().relative().w(64).h(96)
      .child(image(`${ASSET}/${pose}${gk ? "-gk" : ""}.svg`).w(64).h(96))
      .when(Boolean(kit.numberBg), (el) => el.child(div().absolute().left(25).top(31).w(14).h(13).rounded(2).bg(kit.numberBg ?? "#0000")))
      .child(div().absolute().left(0).top(30).w(64).text_center().text_size(12).font_weight(800).text_color(kit.number).child(String(num)))
      // Captain's armband on the left sleeve.
      .when(captain, (el) => el.child(div().absolute().left(13).top(33).w(11).h(9).rounded(2).bg(C.accent).border(1).border_color("#000000AA")
        .flex().items_center().justify_center().text_size(7).font_weight(900).text_color("#000").child("C")));
    if (working) {
      sprite.child(div().absolute().left(46).top(78).child(image(`${ASSET}/ball.svg`).size(14))
        .loop("top", { from: 76, to: 82, period: 420 }));
    }
    const body = div().id(`body-${a.address}`).relative().child(sprite);
    if (working) body.loop("top", { from: 0, to: 4, period: 460 });
    if (blocked) body.loop("top", { from: 0, to: -16, period: 820 });
    if (done) body.loop("top", { from: 0, to: -7, period: 640 });
    if (!working && !blocked && !done) body.loop("top", { from: 0, to: 2, period: 2600 });

    const tag = div().mt(2).px(9).py(1).rounded(8).text_size(12).font_weight(800)
      .bg(captain || bench ? C.primary : "#000000A0")
      .text_color(captain || bench ? ON_PRIMARY : "#FFFFFF")
      .when(captain, (el) => el.border(2).border_color(C.accent))
      .child(name);

    return v_flex().id(`player-${a.address}`).absolute().left(slot.x + drift).top(slot.y).w(120).items_center().cursor_pointer()
      .opacity(captain || bench ? 1 : 0.72)
      .transition("left", { duration: 3800, easing: "ease-in-out" })
      .on_click(() => run("agent.focus", { terminal: a.address }))
      .when(captain, (el) => el
        .child(image(`${ASSET}/spotlight.svg`).absolute().left(-10).top(-120).w(140).h(220))
        .child(div().absolute().top(-50).text_size(16).font_weight(900).text_color(C.accent).child("▼")
          .loop("top", { from: -54, to: -44, period: 700 })))
      .when(bench && !captain, (el) => el.child(div().absolute().top(84).left(30).w(60).h(14).rounded(30).border(2).border_color(C.primary + "AA")))
      .when(blocked, (el) => el.child(h_flex().absolute().top(-30).gap(6).items_center().px(10).py(4).rounded(10)
        .bg("#FFF8E1").border(2).border_color("#D49A00").text_size(12).font_weight(700).text_color("#5A4200")
        .child(div().w(9).h(12).rounded(1).bg("#F6C700"))
        .child(div().child(`${W.blocked} · ${a.program?.name ?? ""}`))))
      .when(done && !blocked, (el) => el.child(div().absolute().top(captain ? -74 : -34).text_size(17).font_weight(900).text_color(C.accent).child(W.shout)))
      .child(body)
      .child(tag)
      .child(div().max_w(118).truncate().text_size(10.5).text_color("#FFFFFFC0").child(`${a.space_name} · ${a.tab_name ?? ""}`));
  }

  // The block's size in this mod's px. on_size_change reports window pixels, and the app zoom
  // scales this mod's px, so divide the zoom out here, at draw time, where a zoom change lands too.
  get size() {
    const z = Number(settings()?.zoom ?? 1) || 1;
    return { width: this.raw.width / z, height: this.raw.height / z };
  }

  // The pitch art (1600x420) fits the block's width. Images keep their aspect ratio, so a short
  // block crops the sky off the top, and a tall one gets more grass drawn below the art.
  geometry() {
    const { width, height } = this.size;
    const scale = width / 1600;
    const h = 420 * scale;
    const top = h >= height ? height - h : 0;
    const grass = top + 227 * scale;
    // Compact: the block is so short the stands are off screen; titles move into the scoreboard.
    return { scale, top, w: width, h, grass, compact: grass < 150, extra: Math.max(0, height - (top + h)), bottom: height };
  }

  // Grass below the art in a tall block: same stripes, touchlines and halfway line.
  moreGrass(g) {
    if (g.extra < 1) return [];
    const y = g.top + g.h, s = g.scale, line = "#FFFFFFBF";
    const stripes = [];
    for (let i = 1; i * 100 * s < g.w; i += 2) stripes.push(div().absolute().left(i * 100 * s).top(y).w(100 * s).h(g.extra).bg("#FFFFFF0D"));
    return [
      div().absolute().left(0).top(y).w(g.w).h(g.extra).bg("#1F6E2E"),
      ...stripes,
      ...[20 * s, g.w / 2, g.w - 20 * s].map((x) => div().absolute().left(x - 1.5 * s).top(y).w(3 * s).h(g.extra).bg(line)),
    ];
  }

  // Where each player stands: rows of up to six across the grass, right of the scoreboard.
  slots(n, g) {
    const { width } = this.size;
    const left = 250, right = 40;
    // A player with its name and tab is about 145px tall; rows that don't fit merge into fewer, wider ones.
    // On the grass when there's room, else as low as fits.
    const y0 = Math.max(g.compact ? 8 : 60, Math.min(g.grass - 20, g.bottom - 150));
    const space = g.bottom - y0 - 145;
    let rows = n > 12 ? 3 : n > 6 ? 2 : 1;
    while (rows > 1 && space / (rows - 1) < 60) rows--;
    const cols = Math.max(1, Math.ceil(n / rows));
    const w = Math.max(100, (width - left - right) / cols);
    const rowH = rows > 1 ? Math.min(150, space / (rows - 1)) : 0;
    return Array.from({ length: n }, (_, i) => {
      const r = Math.floor(i / cols), c = i % cols;
      const stagger = r % 2 ? w * 0.35 : 0;
      return { x: left + c * w + (w - 120) / 2 + stagger, y: y0 + r * rowH, w };
    });
  }

  chip(id, label, active, status, onClick) {
    return h_flex().id(id).flex_none().gap(6).items_center().h(26).px(10).rounded(13).cursor_pointer()
      .text_size(12).font_weight(active ? 800 : 600)
      .bg(active ? C.primary : "#FFFFFF14").text_color(active ? ON_PRIMARY : C.foreground)
      .when(!active, (el) => el.hover((s) => s.bg("#FFFFFF2A")))
      .when(Boolean(status) && status !== "idle", (el) => el.child(div().size(7).rounded(4).bg(DOT[status] ?? "#FFFFFF55")))
      .child(div().max_w(150).truncate().child(label))
      .on_click(onClick);
  }

  // The navigation bar: every space as a chip, then the shown space's tabs, then the keys.
  rail() {
    const all = spaces();
    const s = all.find((x) => x.active);
    const captain = agents().find((a) => a.address === focused()?.agent);
    const key = (k, label) => h_flex().gap(4).items_center()
      .child(div().px(5).rounded(4).bg("#FFFFFF1F").text_color(C.foreground).font_family("JetBrains Mono").text_size(10.5).child(k))
      .child(div().child(label));
    return h_flex().size_full().bg(C.surface).border_t(2).border_color(C.primary).px(14).gap(8).items_center().text_color(C.foreground)
      .child(div().flex_none().text_size(10).font_weight(800).text_color(C.primary).child(W.spaces))
      .children(all.map((x) => this.chip(`sp-${x.id}`, x.name, x.active, x.status, () => run("space.select", { id: x.id }))))
      .child(div().flex_none().text_size(16).text_color(C.foreground + "66").child("›"))
      .children((s?.tabs ?? []).filter((t) => !t.settled || t.active)
        .map((t) => this.chip(`tb-${t.id}`, t.name, t.active, t.status, () => run("tab.select", { id: t.id }))))
      .child(div().flex_1())
      .when(Boolean(captain), (el) => el.child(h_flex().flex_none().gap(6).items_center().text_size(12).font_weight(700)
        .child(div().text_color(C.accent).child("▼"))
        .child(div().child(`${this.squadOf(captain).name} · ${W.onBall}`))))
      .child(h_flex().flex_none().gap(10).ml(10).text_size(10.5).text_color(C.foreground + "99")
        .child(key("⌘⌥[ ]", W.space)).child(key("⌘⇧[ ]", W.tab)).child(key("⌘[ ]", W.player)));
  }

  render(cx) {
    const p = props() ?? {};
    if (p.role === "pane") {
      const pane = panes().find((x) => x.pane === p.pane);
      const st = pane?.status;
      const agent = pane?.terminal ? agents().find((a) => a.address === pane.terminal) : null;
      const who = agent ? this.squadOf(agent).name : null;
      return h_flex().size_full().px(12).gap(9).items_center().bg(C.surface).text_color(C.foreground).text_size(12).font_weight(600)
        .child(icon(pane?.program, C.foreground)).child(div().child(pane?.program?.name ?? "Terminal"))
        .when(Boolean(who), (el) => el.child(div().px(8).rounded(8).bg(C.primary).text_color(ON_PRIMARY).font_weight(800).child(who)))
        .child(div().flex_1())
        .child(div().text_color(DOT[st] ?? C.foreground + "99").child(WORD[st] ?? ""));
    }
    if (p.role === "rail") return this.rail();

    const list = agents();
    this.pick(list, cx);
    setAgentOrder(list.map((a) => a.address));
    const active = spaces().find((s) => s.active);
    const tab = active?.tabs.find((t) => t.active);
    const captainAddr = focused()?.agent;
    const count = (st) => list.filter((a) => a.status === st).length;
    const away = (active?.name ?? "---").replace(/[^\p{L}\p{N}]/gu, "").slice(0, 3).toUpperCase() || "---";
    const g = this.geometry();
    const slots = this.slots(list.length, g);
    // Draw the captain last so its spotlight and armband sit above everyone else.
    const order = list.map((a, i) => ({ a, i })).sort((x, y) => (x.a.address === captainAddr) - (y.a.address === captainAddr));

    return div().id("root").relative().size_full().overflow_hidden().bg(C.dark)
      // The reported size is in window pixels; this mod's px are scaled by the app zoom, so divide it out.
      .on_size_change((size, cx) => { this.raw = size; cx.notify(); })
      .child(image(`${ASSET}/pitch.svg`).absolute().left(0).top(g.top).w(g.w).h(g.h))
      .children(this.moreGrass(g))
      .when(!g.compact, (el) => el.child(v_flex().absolute().left(20).top(30).gap(2).px(10).py(6).rounded(8).bg("#05070DB3").text_color("#FFFFFF")
        .child(div().text_size(26).font_weight(800).child(STADIUM))
        .child(div().text_size(12.5).text_color("#FFFFFFB0").child(`${list.length} ${W.onPitch}`))))
      .child(v_flex().absolute().left(g.compact ? 12 : 28).top(g.compact ? 10 : Math.max(96, g.grass - 4)).w(g.compact ? 220 : 190).px(14).py(10).gap(4).rounded(6)
        .bg("#05070DE6").border(2).border_color(C.primary)
        .when(g.compact, (el) => el.child(div().text_size(12).font_weight(800).text_color("#FFFFFF").truncate().child(STADIUM)))
        .child(div().text_size(10).font_weight(700).text_color("#FFFFFF80").child(`${W.matchday} · ${active?.name ?? ""}`))
        .child(h_flex().gap(8).items_center().font_family("JetBrains Mono").text_size(22).font_weight(800)
          .child(div().text_color(C.primary).child(SHORT))
          .child(div().text_color("#FFD23F").child(`${count("done")}-${count("blocked")}`))
          .child(div().text_color("#FFFFFFC0").child(away)))
        .when(g.compact, (el) => el.child(div().text_size(10.5).text_color("#FFFFFFB0")
          .child(`${count("working")} ${W.workingCount} · ${count("blocked")} ${W.blockedCount} · ${count("done")} ${W.doneCount}`))))
      .children(order.map(({ a, i }) => this.player(a, i, slots[i], a.address === captainAddr,
        a.space === active?.id && a.tab === tab?.id)))
      .when(!g.compact, (el) => el.child(h_flex().absolute().right(28).top(30).gap(10).text_size(12).font_weight(600)
        .children([["working", W.workingCount, C.primary], ["blocked", W.blockedCount, "#F6C700"], ["done", W.doneCount, C.accent]]
          .map(([st, label, col]) => h_flex().gap(6).items_center().px(10).py(4).rounded(10).bg("#000000A0")
            .child(div().size(7).rounded(4).bg(col)).child(div().text_color("#FFFFFF").child(`${count(st)} ${label}`))))));
  }
}
