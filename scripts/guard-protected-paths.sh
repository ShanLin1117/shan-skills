#!/usr/bin/env bash
# PreToolUse（Edit / Write / NotebookEdit）：拒絕寫入 .shan/guard.yaml 的 protected_paths。
# allowed_paths 優先——用來替受保護目錄下的少數可寫檔開洞（例如 tasks.md 的勾選）。

# shellcheck source=lib.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

GUARD="$(guard_file)"
[ -z "$GUARD" ] && exit 0

FILE="$(json_get tool_input.file_path)"
[ -z "$FILE" ] && FILE="$(json_get tool_input.notebook_path)"
[ -z "$FILE" ] && exit 0
FILE="${FILE//\\//}"

ROOT="$(project_root)"
REL="$FILE"
shopt -s nocasematch
case "$FILE" in
  "$ROOT"/*) REL="${FILE#"$ROOT"/}" ;;
esac

# 用 [[ == ]] 的 glob 比對：* 與 ** 都跨越 /，寧可多擋不可少擋
matches() {
  local p="$1"
  [[ "$REL" == $p ]] || [[ "$FILE" == $p ]] || [[ "$FILE" == */$p ]]
}

while IFS= read -r p; do
  [ -z "$p" ] && continue
  matches "$p" && exit 0
done < <(yaml_list "$GUARD" allowed_paths)

while IFS= read -r p; do
  [ -z "$p" ] && continue
  if matches "$p"; then
    deny "shan-guard：\`$REL\` 命中受保護路徑 \`$p\`（.shan/guard.yaml）。這是 spec 層級或不可逆的檔案：停下來、在草稿區 issues/ 開票、告知使用者，不要改寫。若是使用者明確要求修改，請使用者暫時調整 guard.yaml 或以 SHAN_GUARD_OFF=1 啟動。"
  fi
done < <(yaml_list "$GUARD" protected_paths)

exit 0
