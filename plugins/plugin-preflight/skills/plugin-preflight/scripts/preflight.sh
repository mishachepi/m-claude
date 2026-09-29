#!/usr/bin/env bash
# Preflight for a Claude Code plugin repo. Usage: preflight.sh [repo-path]
set -u
repo=$(cd "${1:-.}" && pwd) || exit 2
cd "$repo" || exit 2
command -v jq >/dev/null || { echo "FAIL jq is required"; exit 2; }

fails=0
fail() { echo "FAIL $*"; fails=$((fails + 1)); }
warn() { echo "WARN $*"; }
ok()   { echo "OK   $*"; }

mkt=.claude-plugin/marketplace.json
plugin_dirs=()   # relative dirs, "." for a single-plugin repo
if [ -f "$mkt" ]; then
  jq empty "$mkt" 2>/dev/null || { fail "$mkt is not valid JSON"; exit 1; }
  while IFS= read -r src; do
    d=${src#./}
    if [ -d "$d" ]; then plugin_dirs+=("$d"); else fail "marketplace source '$src' does not exist"; fi
  done < <(jq -r '.plugins[].source | select(type == "string")' "$mkt")
  # plugin dirs on disk missing from the marketplace
  for pj in plugins/*/.claude-plugin/plugin.json; do
    [ -f "$pj" ] || continue
    d=${pj%/.claude-plugin/plugin.json}
    printf '%s\n' "${plugin_dirs[@]}" | grep -qx "$d" || fail "$d has a plugin.json but is not registered in $mkt"
  done
elif [ -f .claude-plugin/plugin.json ]; then
  plugin_dirs+=(".")
else
  echo "FAIL no .claude-plugin/marketplace.json or plugin.json in $repo"; exit 1
fi

echo "== 1. claude plugin validate"
if command -v claude >/dev/null; then
  [ -f "$mkt" ] && { claude plugin validate . >/tmp/pf.$$ 2>&1 && ok "marketplace" || { fail "validate ."; sed 's/^/     /' /tmp/pf.$$; }; }
  for d in "${plugin_dirs[@]}"; do
    claude plugin validate "$d" >/tmp/pf.$$ 2>&1 && ok "$d" || { fail "validate $d"; sed 's/^/     /' /tmp/pf.$$; }
  done
  rm -f /tmp/pf.$$
else
  warn "claude CLI not found — validate skipped"
fi

echo "== 2. \${CLAUDE_PLUGIN_ROOT} paths"
checked=0
for d in "${plugin_dirs[@]}"; do
  while IFS= read -r f; do
    while IFS= read -r ref; do
      p=${ref#\$\{CLAUDE_PLUGIN_ROOT\}}
      p=$(printf '%s' "$p" | sed -E 's/[].,;:)`"\\'"'"'>]+$//')   # trailing prose/JSON punctuation
      case "$p" in *'<'*|*'...'*|*'*'*|*'$'*|*'{'*) continue;; esac
      [ -z "$p" ] || [ "$p" = "/" ] && continue
      checked=$((checked + 1))
      [ -e "$d/$p" ] || fail "$f: \${CLAUDE_PLUGIN_ROOT}$p does not exist under $d"
    done < <(grep -o '\${CLAUDE_PLUGIN_ROOT}/[^[:space:]]*' "$f" 2>/dev/null)
  done < <(find "$d" -type f \( -name '*.md' -o -name '*.json' -o -name '*.sh' -o -name '*.py' \) -not -path '*/node_modules/*')
done
ok "$checked path(s) checked"

echo "== 3. name consistency"
if [ -f "$mkt" ]; then
  mname=$(jq -r '.name' "$mkt")
  known=$(jq -r '.plugins[].name' "$mkt")
  while IFS=$'\t' read -r name ver src; do
    d=${src#./}
    pj="$d/.claude-plugin/plugin.json"
    [ -f "$pj" ] || { fail "$name: $pj missing"; continue; }
    pname=$(jq -r '.name' "$pj"); pver=$(jq -r '.version // ""' "$pj")
    [ "$pname" = "$name" ] || fail "marketplace name '$name' != plugin.json name '$pname' ($pj)"
    [ "$(basename "$d")" = "$name" ] || warn "dir '$d' basename differs from name '$name'"
    [ -z "$pver" ] || [ "$pver" = "$ver" ] || fail "$name: version marketplace=$ver plugin.json=$pver"
  done < <(jq -r '.plugins[] | select(.source|type=="string") | [.name, (.version // ""), .source] | @tsv' "$mkt")
  # stale `<name>@<marketplace>` references in docs
  while IFS= read -r line; do
    f=${line%%:*}; ref=${line#*:}; n=${ref%@*}
    echo "$known" | grep -qx "$n" || fail "$f: references '$ref' but '$n' is not in $mkt"
  done < <(grep -roE --include='*.md' --include='*.json' "[a-z0-9][a-z0-9-]*@$mname" . --exclude-dir=.git 2>/dev/null | sed 's|^\./||' | sort -u)
  ok "checked $(echo "$known" | wc -l | tr -d ' ') marketplace entries"
else
  ok "single-plugin repo — no marketplace to compare"
fi

echo "== 4. secrets in outgoing diff"
base=""
for c in '@{u}' origin/HEAD origin/main main; do
  git rev-parse -q --verify "$c" >/dev/null 2>&1 && { base=$c; break; }
done
[ -n "$base" ] || base=$(git rev-list --max-parents=0 HEAD 2>/dev/null | tail -1)
[ "$base" = "main" ] && [ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] && [ "$(git rev-parse main)" = "$(git rev-parse HEAD)" ] && base=$(git rev-list --max-parents=0 HEAD | tail -1)
added=$( { git diff "$base"...HEAD 2>/dev/null; git diff HEAD 2>/dev/null; } | grep -E '^\+[^+]' | sed 's/^+//')
pat='AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}|xox[baprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----|[0-9]{8,10}:[A-Za-z0-9_-]{35}|eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+|(api[_-]?key|secret|token|passw(or)?d)["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"'][A-Za-z0-9/+_=-]{16,}["'"'"']'
hits=$(printf '%s\n' "$added" | grep -Ei "$pat" | sed -E 's/(.{6})[^[:space:]]{6,}/\1…[redacted]/g' | head -20)
if [ -n "$hits" ]; then fail "possible secret(s) in added lines (values redacted):"; echo "$hits" | sed 's/^/     /'; else ok "no built-in pattern matched (base: $base)"; fi
if command -v gitleaks >/dev/null; then
  gitleaks git --log-opts="$base..HEAD" --redact --no-banner >/dev/null 2>&1 && ok "gitleaks clean" || fail "gitleaks reported findings (run: gitleaks git --log-opts=\"$base..HEAD\" --redact)"
fi

echo
[ "$fails" -eq 0 ] && { echo "PREFLIGHT GREEN"; exit 0; } || { echo "PREFLIGHT RED — $fails failure(s)"; exit 1; }
