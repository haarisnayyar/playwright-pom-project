#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BROWSERS=("chromium" "firefox" "webkit")
MAX_ATTEMPTS="${MAX_ATTEMPTS:-2}"
HEADED="${HEADED:-false}"
SLOWMO_MS="${SLOWMO_MS:-0}"

REPORTS_DIR="reports"
COMBINED_RESULTS_DIR="$REPORTS_DIR/allure-results"
COMBINED_HTML_DIR="$REPORTS_DIR/allure-html"

collect_line="$(pytest --collect-only -q --browser chromium | tail -n 1)"
per_browser_count="$(echo "$collect_line" | awk '{print $1}')"
if ! [[ "$per_browser_count" =~ ^[0-9]+$ ]]; then
  echo "Failed to parse collected test count from: $collect_line" >&2
  exit 1
fi
expected_total=$((per_browser_count * ${#BROWSERS[@]}))

run_browser() {
  local browser="$1"
  local browser_results_dir="$REPORTS_DIR/allure-results-$browser"
  local browser_html_report="$REPORTS_DIR/pytest-report-$browser.html"
  local attempt=1

  rm -rf "$browser_results_dir"
  mkdir -p "$browser_results_dir"
  rm -f "$browser_html_report"

  while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
    echo
    echo "=== Running pytest on $browser (attempt $attempt/$MAX_ATTEMPTS, headed=$HEADED, slowmo_ms=$SLOWMO_MS) ==="

    args=(
      -q
      --browser "$browser"
      --slowmo "$SLOWMO_MS"
      --alluredir="$browser_results_dir"
      --html="$browser_html_report"
      --self-contained-html
    )

    if [ "$HEADED" = "true" ]; then
      args+=(--headed)
    fi

    if pytest "${args[@]}"; then
      return 0
    fi

    if [ "$attempt" -eq "$MAX_ATTEMPTS" ]; then
      echo "ERROR: pytest run failed after $MAX_ATTEMPTS attempts on browser: $browser" >&2
      return 1
    fi

    echo "Retrying browser run for $browser..."
    attempt=$((attempt + 1))
    rm -rf "$browser_results_dir"
    mkdir -p "$browser_results_dir"
    rm -f "$browser_html_report"
  done
}

rm -rf "$COMBINED_RESULTS_DIR" "$COMBINED_HTML_DIR"
mkdir -p "$REPORTS_DIR"

echo "Discovered $per_browser_count tests per browser."
echo "Expected combined total across browsers: $expected_total"
echo "Running pytest scenarios on: ${BROWSERS[*]}"

for browser in "${BROWSERS[@]}"; do
  run_browser "$browser"
done

mkdir -p "$COMBINED_RESULTS_DIR"
for browser in "${BROWSERS[@]}"; do
  python3 - "$browser" "$REPORTS_DIR/allure-results-$browser" "$COMBINED_RESULTS_DIR" <<'PY'
import json
import shutil
import sys
from pathlib import Path

browser, src_dir, dst_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])

for item in src_dir.iterdir():
    target = dst_dir / f"{browser}-{item.name}"
    if item.name.endswith("-result.json"):
        data = json.loads(item.read_text())
        data["name"] = f"{data.get('name', 'test')} [{browser}]"
        if data.get("fullName"):
            data["fullName"] = f"{data['fullName']} [{browser}]"
        if data.get("historyId"):
            data["historyId"] = f"{data['historyId']}.{browser}"
        if data.get("testCaseId"):
            data["testCaseId"] = f"{data['testCaseId']}.{browser}"

        params = list(data.get("parameters") or [])
        params.append({"name": "browser", "value": browser})
        data["parameters"] = params

        target.write_text(json.dumps(data))
    else:
        shutil.copy2(item, target)
PY
done

allure generate "$COMBINED_RESULTS_DIR" -o "$COMBINED_HTML_DIR" --clean >/dev/null

python3 - "$expected_total" <<'PY'
import json
import sys
from pathlib import Path

expected_total = int(sys.argv[1])
summary_path = Path("reports/allure-html/widgets/summary.json")
stats = json.loads(summary_path.read_text())["statistic"]

print("\n=== Combined Allure Summary ===")
print(
    f"total={stats['total']} passed={stats['passed']} failed={stats['failed']} "
    f"broken={stats['broken']} skipped={stats['skipped']}"
)
print("Allure HTML report: reports/allure-html/index.html")

if stats["total"] != expected_total:
    raise SystemExit(f"Expected total={expected_total}, got {stats['total']}")
PY

