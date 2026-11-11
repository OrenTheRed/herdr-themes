// Stadium: your agents are players on the pitch, the active tab's terminals sit on the bench below.
// Working players run with the ball, a blocked one jumps under a VAR bubble, a finished one
// celebrates, idle ones stand and wait. One mod draws all three parts, picked by props().role:
// none for the pitch, "rail" for the strip, "pane" for terminal headers.

import { View, div, image, svg } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { agents, spaces, panes, props, run, setAgentOrder } from "herdr";
import { SQUAD, ASSET, C, K, W, STADIUM, SHORT } from "./team.js";

const icon = (p, color) => (p?.icon ? (p.tint ? svg(p.icon).text_color(color) : image(p.icon)).size(15) : div().size(15));
const WORD = { working: W.working, blocked: W.blocked, done: W.done, idle: W.idle };

export default class Stadium extends View {
  init(_props, cx) {
    this.step = 0;
    this.size = { width: 1400, height: 400 };
    this.players = JSON.parse(localStorage.getItem("players") ?? "{}");
    // The timer only moves where running players are headed; .transition does the moving.
    if (!props()?.role) cx.timer.every(3800, (cx) => { this.step++; cx.notify(); });
  }

  // Each live agent wears the first shirt no other live agent wears, kept across restarts.
  pick(list) {
    const live = new Set(list.map((a) => a.address));
    let dirty = false;
    for (const k of Object.keys(this.players)) if (!live.has(k) && list.length) { delete this.players[k]; dirty = true; }
    const taken = new Set(Object.values(this.players));
    for (const a of list) {
      if (this.players[a.address] != null) continue;
      let i = SQUAD.findIndex((_, j) => !taken.has(j));
      if (i < 0) i = Object.keys(this.players).length % SQUAD.length;
      this.players[a.address] = i;
      taken.add(i);
      dirty = true;
    }
    if (dirty) localStorage.setItem("players", JSON.stringify(this.players));
  }

  player(a, i, slot) {
    const [name, num] = SQUAD[this.players[a.address] ?? 0];
    const { working, blocked, done } = { working: a.status === "working", blocked: a.status === "blocked", done: a.status === "done" };
    const pose = done ? "cheer" : working ? "run" : "stand";
    const drift = working ? Math.sin(this.step * 0.9 + i * 1.7) * Math.min(60, slot.w * 0.3) : 0;

    const sprite = div().relative().w(64).h(96)
      .child(image(`${ASSET}/${pose}.svg`).w(64).h(96))
      .when(Boolean(K.numberBg), (el) => el.child(div().absolute().left(25).top(31).w(14).h(13).rounded(2).bg(K.numberBg ?? "#0000")))
      .child(div().absolute().left(0).top(30).w(64).text_center().text_size(12).font_weight(800).text_color(K.number).child(String(num)));
    if (working) {
      sprite.child(div().absolute().left(46).top(78).child(image(`${ASSET}/ball.svg`).size(14))
        .loop("top", { from: 76, to: 82, period: 420 }));
    }
    const body = div().id(`body-${a.address}`).relative().child(sprite);
    if (working) body.loop("top", { from: 0, to: 4, period: 460 });
    if (blocked) body.loop("top", { from: 0, to: -16, period: 820 });
    if (done) body.loop("top", { from: 0, to: -7, period: 640 });
    if (!working && !blocked && !done) body.loop("top", { from: 0, to: 2, period: 2600 });

    return v_flex().id(`player-${a.address}`).absolute().left(slot.x + drift).top(slot.y).w(120).items_center().cursor_pointer()
      .transition("left", { duration: 3800, easing: "ease-in-out" })
      .on_click(() => run("agent.focus", { terminal: a.address }))
      .when(blocked, (el) => el.child(h_flex().absolute().top(-30).gap(6).items_center().px(10).py(4).rounded(10)
        .bg("#FFF8E1").border(2).border_color("#D49A00").text_size(12).font_weight(700).text_color("#5A4200")
        .child(div().w(9).h(12).rounded(1).bg("#F6C700"))
        .child(div().child(`${W.blocked} · ${a.program?.name ?? ""}`))))
      .when(done, (el) => el.child(div().absolute().top(-34).text_size(17).font_weight(900).text_color(C.accent).child(W.shout)))
      .child(body)
      .child(div().mt(2).px(8).py(1).rounded(8).bg("#000000A0").text_size(12).font_weight(700).text_color("#FFFFFF").child(name))
      .child(div().max_w(118).truncate().text_size(10.5).text_color("#FFFFFFC0").child(a.tab_name ?? ""));
  }

  // The pitch art (1600x420) fits the block's width. Images keep their aspect ratio, so a short
  // block crops the sky off the top, and a tall one gets more grass drawn below the art.
  geometry() {
    const { width, height } = this.size;
    const scale = width / 1600;
    const h = 420 * scale;
    const top = h >= height ? height - h : 0;
    return { scale, top, w: width, h, grass: top + 227 * scale, extra: Math.max(0, height - (top + h)), bottom: height };
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
    const y0 = g.grass - 70;
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

  render() {
    const p = props() ?? {};
    if (p.role === "pane") {
      const pane = panes().find((x) => x.pane === p.pane);
      const st = pane?.status;
      return h_flex().size_full().px(12).gap(9).items_center().bg(C.surface).text_color(C.foreground).text_size(12).font_weight(600)
        .child(icon(pane?.program, C.foreground)).child(div().child(pane?.program?.name ?? "Terminal"))
        .child(div().flex_1())
        .child(div().text_color(st === "blocked" ? "#F6C700" : st === "done" ? C.accent : st === "working" ? C.primary : C.foreground + "99").child(WORD[st] ?? ""));
    }
    if (p.role === "rail") {
      const s = spaces().find((s) => s.active), tab = s?.tabs.find((t) => t.active);
      return h_flex().size_full().bg(C.surface).border_t(2).border_color(C.primary).px(20).items_center().justify_between()
        .text_color(C.foreground).text_size(13).font_weight(600)
        .child(div().child(`${s?.name ?? ""}  /  ${tab?.name ?? ""}`)).child(div().text_size(11).text_color(C.primary).child(W.bench));
    }

    const list = agents();
    this.pick(list);
    setAgentOrder(list.map((a) => a.address));
    const active = spaces().find((s) => s.active);
    const count = (st) => list.filter((a) => a.status === st).length;
    const away = (active?.name ?? "---").replace(/[^\p{L}\p{N}]/gu, "").slice(0, 3).toUpperCase() || "---";
    const g = this.geometry();
    const slots = this.slots(list.length, g);

    return div().id("root").relative().size_full().overflow_hidden().bg(C.dark)
      .on_size_change((size, cx) => { this.size = size; cx.notify(); })
      .child(image(`${ASSET}/pitch.svg`).absolute().left(0).top(g.top).w(g.w).h(g.h))
      .children(this.moreGrass(g))
      .child(v_flex().absolute().left(20).top(30).gap(2).px(10).py(6).rounded(8).bg("#05070DB3").text_color("#FFFFFF")
        .child(div().text_size(28).font_weight(800).child(STADIUM))
        .child(div().text_size(12.5).text_color("#FFFFFFB0").child(`${list.length} ${W.onPitch}`)))
      .child(v_flex().absolute().left(28).top(Math.max(96, g.grass - 4)).w(190).px(14).py(10).gap(4).rounded(6)
        .bg("#05070DE6").border(2).border_color(C.primary)
        .child(div().text_size(10).font_weight(700).text_color("#FFFFFF80").child(`${W.matchday} · ${active?.name ?? ""}`))
        .child(h_flex().gap(8).items_center().font_family("JetBrains Mono").text_size(22).font_weight(800)
          .child(div().text_color(C.primary).child(SHORT))
          .child(div().text_color("#FFD23F").child(`${count("done")}-${count("blocked")}`))
          .child(div().text_color("#FFFFFFC0").child(away))))
      .children(list.map((a, i) => this.player(a, i, slots[i])))
      .child(h_flex().absolute().right(28).top(30).gap(10).text_size(12).font_weight(600)
        .children([["working", W.workingCount, C.primary], ["blocked", W.blockedCount, "#F6C700"], ["done", W.doneCount, C.accent]]
          .map(([st, label, col]) => h_flex().gap(6).items_center().px(10).py(4).rounded(10).bg("#000000A0")
            .child(div().size(7).rounded(4).bg(col)).child(div().text_color("#FFFFFF").child(`${count(st)} ${label}`)))));
  }
}
