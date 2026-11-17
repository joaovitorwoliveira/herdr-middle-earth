#!/usr/bin/env bash
# Installs the Middle-earth layout into a Herdr desktop home and switches to it.
# Anything it would replace is first kept as <name>.bak-<time>.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERDR_HOME="${HERDR_APP_HOME:-$HOME/.config/herdr-app}"
STAMP="$(date +%Y%m%d-%H%M%S)"
LAYOUT="middle-earth"
MODS=(fellowship fellowship-toast fellowship-status realms)
THEMES=(shire mordor)

fail() { echo "install.sh: $*" >&2; exit 1; }

command -v python3 >/dev/null || fail "python3 is needed to merge settings.json and programs.json."
[ -d "$HERDR_HOME" ] || fail "no Herdr home at $HERDR_HOME. Open Herdr once, or set HERDR_APP_HOME."

keep_aside() {
  if [ -e "$1" ]; then
    mv "$1" "$1.bak-$STAMP"
    echo "  kept the old $(basename "$1") as $(basename "$1").bak-$STAMP"
  fi
}

echo "Installing into $HERDR_HOME"
mkdir -p "$HERDR_HOME/layouts" "$HERDR_HOME/themes" "$HERDR_HOME/mods"

for mod in "${MODS[@]}"; do
  keep_aside "$HERDR_HOME/mods/$mod"
  cp -R "$REPO/mods/$mod" "$HERDR_HOME/mods/$mod"
done
for theme in "${THEMES[@]}"; do
  keep_aside "$HERDR_HOME/themes/$theme.json"
  cp "$REPO/themes/$theme.json" "$HERDR_HOME/themes/"
done
keep_aside "$HERDR_HOME/layouts/$LAYOUT.json"
cp "$REPO/layouts/$LAYOUT.json" "$HERDR_HOME/layouts/"

# Sounds and program icons live in the person's own files, not the layout, so they are merged in.
merge_json() {
  local target="$HERDR_HOME/$1" snippet="$REPO/$2"
  [ -e "$target" ] && cp "$target" "$target.bak-$STAMP"
  python3 - "$target" "$snippet" <<'PY'
import json, os, sys

target, snippet = sys.argv[1], sys.argv[2]

def merge(base, extra):
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merge(base[key], value)
        else:
            base[key] = value
    return base

try:
    current = json.load(open(target)) if os.path.exists(target) else {}
except json.JSONDecodeError as e:
    sys.exit(f"install.sh: {target} is not valid JSON ({e}); fix it and run again.")
with open(target, "w") as f:
    json.dump(merge(current, json.load(open(snippet))), f, indent=2)
    f.write("\n")
PY
  echo "  merged $2 into $1"
}
merge_json settings.json settings.snippet.json
merge_json programs.json programs.json

if command -v herdr-app >/dev/null; then
  for mod in "${MODS[@]}"; do
    (cd "$HERDR_HOME" && herdr-app check "mods/$mod") || fail "mods/$mod did not load; see the message above."
  done
  herdr-app do layout.switch "{\"name\":\"$LAYOUT\"}" >/dev/null \
    || echo "Herdr isn't running: pick Middle-earth with ctrl-shift-l when it opens."
fi

if [ "$(uname)" = "Darwin" ] && ! command -v terminal-notifier >/dev/null; then
  cat <<'TXT'

Optional: system banners with the character's sprite when Herdr is in the background.
  brew install terminal-notifier
  open "$(brew --prefix terminal-notifier)/terminal-notifier.app"   # allow notifications once
TXT
fi

echo "Done. ctrl-shift-l switches layouts."
