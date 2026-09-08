#!/usr/bin/env bash
# shan-skills harness 層共用函式。由 guard-*.sh source，不單獨執行。
#
# 約定：
#   - hook 的輸入是 stdin 的 JSON（tool_name / tool_input / cwd）
#   - 任何自身錯誤一律放行（exit 0、不輸出），護欄不得因為自己壞掉而擋住工作
#   - 拒絕時輸出 PreToolUse 的 permissionDecision JSON 並 exit 0

set -u

HOOK_INPUT="$(cat 2>/dev/null || true)"

# json_get <點路徑>：從 HOOK_INPUT 取字串值，例如 json_get tool_input.file_path
# 優先用 node（Claude Code 的 npm 安裝必有），其次 jq，最後 sed 粗略比對
json_get() {
  local path="$1"
  if command -v node >/dev/null 2>&1; then
    printf '%s' "$HOOK_INPUT" | node -e '
      let s = "";
      process.stdin.on("data", d => s += d).on("end", () => {
        try {
          const o = JSON.parse(s);
          const v = process.argv[1].split(".").reduce((a, k) => a == null ? undefined : a[k], o);
          if (v != null) process.stdout.write(String(v));
        } catch (e) {}
      });' "$path" 2>/dev/null
  elif command -v jq >/dev/null 2>&1; then
    printf '%s' "$HOOK_INPUT" | jq -r --arg p "$path" 'getpath($p | split(".")) // empty' 2>/dev/null
  else
    local key="${path##*.}"
    printf '%s' "$HOOK_INPUT" \
      | sed -n -E "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"((\\\\.|[^\"\\\\])*)\".*/\1/p" \
      | head -1 \
      | sed -e 's/\\"/"/g' -e 's#\\/#/#g' -e 's/\\\\/\\/g'
  fi
}

# 專案根：hook 環境變數優先，其次 stdin 的 cwd。反斜線一律轉成斜線
project_root() {
  local r="${CLAUDE_PROJECT_DIR:-}"
  [ -z "$r" ] && r="$(json_get cwd)"
  r="${r//\\//}"
  printf '%s' "${r%/}"
}

# guard.yaml 路徑；不存在或全域停用時回傳空字串
guard_file() {
  [ "${SHAN_GUARD_OFF:-0}" = "1" ] && return 0
  local f="$(project_root)/.shan/guard.yaml"
  [ -f "$f" ] && printf '%s' "$f"
}

# yaml_list <檔> <頂層鍵>：列出該鍵底下「  - 值」的每一項，略過樣板佔位符 <...>
yaml_list() {
  local file="$1" key="$2"
  sed -n -E "/^$key:[[:space:]]*(#.*)?$/,/^[^[:space:]#]/p" "$file" \
    | sed -n -E 's/^[[:space:]]+-[[:space:]]*"?([^"#]*[^"#[:space:]])"?[[:space:]]*(#.*)?$/\1/p' \
    | grep -v '^<' || true
}

# yaml_kv <檔> <鍵>：取第一個符合的純量值（任意縮排），去掉引號與行尾註解
yaml_kv() {
  local file="$1" key="$2"
  sed -n -E "s/^[[:space:]]*$key:[[:space:]]*\"?([^\"#]*[^\"#[:space:]])\"?[[:space:]]*(#.*)?$/\1/p" "$file" \
    | head -1 | grep -v '^<' || true
}

# deny <理由>：輸出拒絕決定並結束
deny() {
  local reason="$1"
  reason="${reason//\\/\\\\}"
  reason="${reason//\"/\\\"}"
  reason="${reason//$'\n'/ }"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
  exit 0
}
