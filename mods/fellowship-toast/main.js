// How notifications look. Anything can post one with notify({ title, body,
// level, icon, action }); replace this mod to restyle them all. Click to
// run its action (e.g. go to the agent) and dismiss it.

import { View, div, image } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { props, closeOverlay, run, theme, shared, exec, window, appHome, checking } from "herdr";

// Written by the fellowship mod: terminal address to character.
const CAST_KEY = "fellowship.cast";
// Also written by the fellowship mod: terminal address to a rare edition's display name.
const RARE_KEY = "fellowship.rare";
const HERO_ICON_SIZE = 28;
// Herdr's own agent toasts read "<program> finished" or "<program> needs you".
const AGENT_TOAST = /^(.+) (finished|needs you)$/;
const QUEST = {
  finished: { pose: "done", line: "returned from the quest" },
  "needs you": { pose: "blocked", line: "awaits your counsel" },
};
// Takes the display name so a variant (e.g. "Gandalf the White") can reuse its hero's lines.
const HERO_LINES = {
  gandalf: {
    done: (name) => `${name} arrives precisely when he means to`,
    blocked: (name) => `${name} will not pass without your word`,
  },
  aragorn: {
    done: (name) => `${name} has returned, as was foretold`,
    blocked: (name) => `${name} calls for aid`,
  },
  frodo: {
    done: (name) => `${name}: "It's done."`,
    blocked: (name) => `${name} does not know the way`,
  },
  sam: {
    done: (name) => `${name}: "Well, I'm back."`,
    blocked: (name) => `${name} won't go on without you`,
  },
  legolas: {
    done: (name) => `${name} has found his mark`,
    blocked: (name) => `${name} holds fire for your command`,
  },
  gimli: {
    done: (name) => `${name} returned, axe notched`,
    blocked: (name) => `${name} won't take another step without you`,
  },
  sauron: {
    done: (name) => `${name}: the Eye is satisfied`,
    blocked: (name) => `${name}: the Eye turns toward you`,
  },
};

// Title and body go in as arguments, never into the script text, so quotes in them stay inert.
const SYSTEM_NOTIFICATION = ["-e", "on run argv", "-e", "display notification (item 2 of argv) with title (item 1 of argv)", "-e", "end run"];
// Clicking the banner brings Herdr forward.
const HERDR_BUNDLE = "dev.herdr.app";

function reportFailure(tool) {
  return (r) => { if (r.code !== 0) console.error(`System notification failed (${tool} ${r.code}): ${r.stderr}`); };
}

// macOS drops osascript banners started from inside Herdr, so terminal-notifier (its own app,
// its own permission) comes first; osascript only runs when it isn't installed.
function postToMacos(title, body, image) {
  const picture = image ? ["-contentImage", `${appHome()}/${image}`] : [];
  exec("terminal-notifier", ["-title", title, "-message", body || " ", "-activate", HERDR_BUNDLE, ...picture]).then(
    reportFailure("terminal-notifier"),
    () => exec("osascript", [...SYSTEM_NOTIFICATION, title, body]).then(
      reportFailure("osascript"),
      (e) => console.error(`System notification failed: ${e}`),
    ),
  );
}

function postToLinux(title, body, image) {
  const icon = image ? ["-i", `${appHome()}/${image}`] : [];
  exec("notify-send", ["-a", "Herdr", ...icon, title, body]).then(
    reportFailure("notify-send"),
    (e) => console.error(`System notification failed (is notify-send installed?): ${e}`),
  );
}

// The in-app toast can't be seen from behind another app, so mirror it to the system's banners.
// Windows has no banner command to call, so there the in-app toast is all.
function postToSystem(platform, title, body, image) {
  if (platform === "macos") postToMacos(title, body, image);
  if (platform === "linux") postToLinux(title, body, image);
}

function heroOf(p) {
  const event = AGENT_TOAST.exec(p.title ?? "");
  const terminal = p.action?.name === "agent.focus" ? p.action.args?.terminal : null;
  const hero = terminal ? shared(CAST_KEY)?.[terminal] : null;
  if (!event || !hero) return null;
  const { pose, line } = QUEST[event[2]];
  const rareName = shared(RARE_KEY)?.[terminal];
  const name = rareName ?? `${hero[0].toUpperCase()}${hero.slice(1)}`;
  const sprite = rareName ? `${hero}-rare-${pose}` : `${hero}-${pose}`;
  return {
    title: HERO_LINES[hero]?.[pose](name) ?? `${name} ${line}`,
    body: p.body ? `${event[1]} · ${p.body}` : event[1],
    icon: `mods/fellowship/sprites/${sprite}.svg`,
    banner: `mods/fellowship/banners/${sprite}.png`,
  };
}

const DOT = { error: "blocked", warning: "working", success: "done", info: "accent" };

export default class Toast extends View {
  // init, not render: from another macOS Space the window may not draw, so render may not run.
  init() {
    const w = window();
    if (checking() || !w || w.active) return;
    const raw = props() ?? {};
    const p = { ...raw, ...heroOf(raw) };
    postToSystem(w.platform, p.title ?? "Herdr", p.body ?? "", p.banner);
  }

  render(cx) {
    const t = theme();
    const raw = props() ?? {};
    const p = { ...raw, ...heroOf(raw) };
    const iconSize = p.icon === raw.icon ? 18 : HERO_ICON_SIZE;
    const login = /^([a-z0-9][a-z0-9_.-]{0,31}) needs login; run hc machine login \1$/.exec(p.body ?? "");
    const command = login ? `hc machine login ${login[1]}` : null;
    return h_flex()
      .id("toast")
      .size_full()
      .px(18)
      .gap(12)
      .items_center()
      .bg(t.popover)
      .cursor_pointer()
      .hover((s) => s.bg(t.hover))
      .on_click(() => {
        if (p.action?.name) run(p.action.name, p.action.args ?? {});
        closeOverlay(p.overlay);
      })
      .child(p.icon ? image(p.icon).w(iconSize).h(iconSize).flex_none() : div().size(8).rounded(4).flex_none().bg(t[DOT[p.level] ?? "accent"]))
      .child(
        v_flex()
          .flex_1()
          .overflow_hidden()
          .child(div().truncate().font_semibold().text_size(13).text_color(t.foreground).child(login ? `${login[1]} needs a login: run` : p.title ?? ""))
          .when(!login && Boolean(p.body), (el) => el.child(div().truncate().text_size(12).text_color(t.muted).child(p.body ?? "")))
          .when(Boolean(login), (el) => el.child(h_flex().gap(8).items_center()
            .child(div().flex_1().min_w(0).truncate().tooltip(command).text_size(12).text_color(t.muted).child(command))
            .child(div().id("toast-login-copy").flex_none().px(6).py(3).rounded(4).bg(t.raised)
              .text_size(12).text_color(t.foreground).cursor_pointer().hover(s => s.bg(t.hover))
              .on_click((_e, cx) => { cx.stop_propagation(); cx.write_to_clipboard(command); this.copied = true; cx.notify(); })
              .child(this.copied ? "Copied" : "Copy")))),
      );
  }
}
