#!/bin/sh
# Build team themes and copy them into the Herdr app home.
#
#   ./install.sh [team-id ...]            install; skip any name already there (no overwrite)
#   ./install.sh --update [team-id ...]   replace this repo's files, after backing them up
#
# Team ids are the file names in teams/ (albiceleste, juventus, ...); none means every team.
# The app home is $HERDR_APP_HOME, else ~/.config/herdr-app. Backups of replaced files go to
# <app home>/.herdr-themes-backup/<time>/.
set -eu

update=0
if [ "${1:-}" = "--update" ]; then update=1; shift; fi

APP_HOME="${HERDR_APP_HOME:-$HOME/.config/herdr-app}"
cd "$(dirname "$0")"
[ -d "$APP_HOME" ] || { echo "No Herdr app home at $APP_HOME (start the Herdr app once first)." >&2; exit 1; }

python3 build.py "$@" >/dev/null
BACKUP="$APP_HOME/.herdr-themes-backup/$(date +%Y%m%d-%H%M%S)"

# place <source> <destination-relative-to-app-home>
place() {
  src=$1 rel=$2 dst="$APP_HOME/$2"
  if [ -e "$dst" ]; then
    if [ "$update" -eq 0 ]; then echo "  skip $rel (already there; use --update to replace)"; return; fi
    mkdir -p "$(dirname "$BACKUP/$rel")"
    mv "$dst" "$BACKUP/$rel"
  fi
  mkdir -p "$(dirname "$dst")"
  cp -R "$src" "$dst"
  echo "  put  $rel"
}

for f in teams/*.json; do
  id=$(basename "$f" .json)
  if [ $# -gt 0 ]; then
    case " $* " in *" $id "*) ;; *) continue ;; esac
  fi
  folder=$(python3 -c 'import json,sys; t=json.load(open(sys.argv[1])); print(t.get("folder", t["id"]))' "$f")
  code=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["code"])' "$f")
  echo "$id -> layouts $code and $code-Stadium"
  for p in "$folder"/layouts/* "$folder"/themes/*; do
    place "$p" "${p#"$folder"/}"
  done
  for p in "$folder"/mods/*; do
    place "$p" "mods/$(basename "$p")"
  done
done
[ -d "$BACKUP" ] && echo "Replaced files are in $BACKUP"
command -v herdr-app >/dev/null && echo "Check a mod: herdr-app check $APP_HOME/mods/<id>-stadium"
exit 0
