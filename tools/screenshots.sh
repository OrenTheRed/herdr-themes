#!/bin/sh
# Capture preview.png (stadium) and preview-classic.png for each team folder.
#
# Needs a running Herdr window on a throwaway app home with the demo scene loaded
# (see tools/demo-scene.sh). Example:
#
#   T=$(mktemp -d); mkdir -p "$T/home"
#   HC_SESSION=herdr-demo HERDR_APP_HOME="$T/home" HERDR_APP_ID=herdr-demo \
#     /Applications/Herdr.app/Contents/MacOS/Herdr &
#   HC_SESSION=herdr-demo tools/demo-scene.sh "$T"
#   HERDR_APP_HOME="$T/home" ./install.sh
#   HERDR_APP_HOME="$T/home" tools/screenshots.sh
#   HC_SESSION=herdr-demo tools/demo-scene.sh --stop
#
# Usage: tools/screenshots.sh [team-id ...]
# Team ids are the file names in teams/ (albiceleste, juventus, ...); none means every team.
set -eu

cd "$(dirname "$0")/.."
APP_HOME="${HERDR_APP_HOME:-$HOME/.config/herdr-app}"
command -v herdr-app >/dev/null || { echo "herdr-app not on PATH" >&2; exit 1; }
[ -d "$APP_HOME" ] || { echo "No Herdr app home at $APP_HOME" >&2; exit 1; }

# Rebuild so layouts and themes exist before switching to them.
python3 build.py "$@" >/dev/null

shot() {
  layout=$1 out=$2
  herdr-app do layout.switch "{\"name\":\"$layout\"}"
  # Give the layout a moment to settle before the shot.
  sleep 2
  herdr-app shot "$out"
  echo "  wrote $out"
}

for f in teams/*.json; do
  id=$(basename "$f" .json)
  if [ $# -gt 0 ]; then
    case " $* " in *" $id "*) ;; *) continue ;; esac
  fi
  folder=$(python3 -c 'import json,sys; t=json.load(open(sys.argv[1])); print(t.get("folder", t["id"]))' "$f")
  code=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["code"])' "$f")
  echo "$id -> $folder ($code, $code-Stadium)"
  shot "$code-Stadium" "$folder/preview.png"
  shot "$code" "$folder/preview-classic.png"
done
echo "done"
