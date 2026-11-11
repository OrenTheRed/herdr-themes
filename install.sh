#!/bin/sh
# Build and copy team themes into the Herdr app folder.
# Usage: ./install.sh [team-id ...]     (no ids: every team)
# Then pick a layout: ctrl-shift-l, or  herdr-app do layout.switch '{"name":"<team-id>-stadium"}'
set -eu

APP_HOME="${HERDR_APP_HOME:-$HOME/.config/herdr-app}"
cd "$(dirname "$0")"

[ -d "$APP_HOME" ] || { echo "No Herdr app folder at $APP_HOME (start the Herdr app once first)." >&2; exit 1; }

python3 build.py "$@"

for team in dist/*/; do
  id=$(basename "$team")
  if [ $# -gt 0 ]; then
    case " $* " in *" $id "*) ;; *) continue ;; esac
  fi
  mkdir -p "$APP_HOME/layouts" "$APP_HOME/themes" "$APP_HOME/mods"
  cp "$team"layouts/*.json "$team"layouts/*.svg "$APP_HOME/layouts/"
  cp "$team"themes/*.json "$APP_HOME/themes/"
  for mod in "$team"mods/*/; do
    name=$(basename "$mod")
    mkdir -p "$APP_HOME/mods/$name"
    cp "$mod"* "$APP_HOME/mods/$name/"
  done
  echo "installed $id: layouts $id and $id-stadium"
done
