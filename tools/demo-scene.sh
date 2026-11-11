#!/bin/sh
# Start the made-up demo scene used for the screenshots: nine fake agents in three spaces
# (website, api, docs). No real work, people or data. Run it against a throwaway core and app home
# so your own spaces never show:
#
#   T=$(mktemp -d); mkdir -p "$T/home"
#   HC_SESSION=herdr-demo HERDR_APP_HOME="$T/home" HERDR_APP_ID=herdr-demo /Applications/Herdr.app/Contents/MacOS/Herdr &
#   HC_SESSION=herdr-demo tools/demo-scene.sh "$T"
#   HERDR_APP_HOME="$T/home" ./install.sh
#   HERDR_APP_HOME="$T/home" herdr-app do layout.switch '{"name":"albiceleste-Stadium"}'
#   HERDR_APP_HOME="$T/home" herdr-app shot preview.png
#   HC_SESSION=herdr-demo tools/demo-scene.sh --stop
set -eu
: "${HC_SESSION:?set HC_SESSION to a throwaway core session, e.g. herdr-demo}"

if [ "${1:-}" = "--stop" ]; then
  for n in $(hc ls --json | python3 -c 'import json,sys; [print(t["name"]) for t in json.load(sys.stdin)["terminals"] if (t.get("name") or "").startswith("demo-")]'); do
    hc kill "$n" >/dev/null 2>&1 || true
  done
  exit 0
fi

ROOT="${1:?usage: demo-scene.sh <scratch-dir> | --stop}"
AGENT="$ROOT/fake-agent.sh"
cat >"$AGENT" <<'EOF'
#!/bin/sh
# fake-agent.sh <app> <state> <title> <line>...: print a made-up session, report a status, wait.
app=$1 state=$2 title=$3; shift 3
printf '\033]0;%s\007' "$title"
for line in "$@"; do printf '%s\n' "$line"; done
printf '\033]7501;state=%s:app=%s\007' "$state" "$app"
exec sleep 86400
EOF

# agent <name> <space> <tab> <app> <state> <title> <lines...>
agent() {
  name=$1 space=$2 tab=$3; shift 3
  mkdir -p "$ROOT/work/$space"
  hc run --bg --json --keep --name "$name" --cwd "$ROOT/work/$space" \
    --label "herdr.space=demo-$space" --label "herdr.tab=demo-$space-$tab" -- sh "$AGENT" "$@" >/dev/null
}

agent demo-a website pricing claude-code working "pricing page" \
  "> Make the pricing page easier to scan." "" "I checked the plans and the mobile layout." \
  "Read   src/pages/pricing.astro" "Edit   src/components/PlanCard.astro" \
  "  + Clear plan names and shorter descriptions" "  + A visible monthly / yearly switch" \
  "" "Working / checking keyboard focus order"
agent demo-b website pricing codex done "pricing cards" \
  "> Clean up the pricing card styles." "" "I moved the repeated spacing into tokens." \
  "Updated src/styles/pricing.css" "  + Equal card heights without fixed sizes" \
  "Checks passed: 24 tests, no type errors." "" "Done / pricing cards are ready"
agent demo-c website checkout claude-code blocked "checkout" \
  "> Add Apple Pay to checkout." "" "The payment sheet needs the merchant id." \
  "Allow running: npm run build:payments ?" "  1. Yes   2. No"
agent demo-d api auth claude-code working "auth tokens" \
  "> Rotate refresh tokens on every use." "" "Read   src/auth/session.ts" \
  "Edit   src/auth/refresh.ts" "Running 132 tests..."
agent demo-e api billing codex working "invoices" \
  "> Send invoices as PDF." "" "Edit   src/billing/invoice.ts" "Rendering a sample invoice..."
agent demo-f api billing claude-code idle "webhooks" \
  "> Retry failed webhooks with backoff." "" "Done. 3 retries, then the dead-letter queue."
agent demo-g docs guides claude-code done "quick start" \
  "> Rewrite the quick start." "" "Five steps, one copy-paste block each." "Done / quick start is shorter"
agent demo-h docs guides codex working "screenshots" \
  "> Refresh the screenshots in the guides." "" "Capturing 12 pages..."
agent demo-i docs api-ref claude-code idle "api reference" \
  "> Check every endpoint has an example." "" "All 48 endpoints have one."
echo "demo scene: 9 agents in spaces website, api, docs"
