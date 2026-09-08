#!/usr/bin/env bash
# PreToolUse（Bash）：依 .shan/guard.yaml 的 git 節攔下四類「絕不該做」的 git 指令。
# 「未經同意不 commit」無法由 hook 判斷同意，不在此處理。

# shellcheck source=lib.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

GUARD="$(guard_file)"
[ -z "$GUARD" ] && exit 0

CMD="$(json_get tool_input.command)"
[ -z "$CMD" ] && exit 0
case "$CMD" in *git*) ;; *) exit 0 ;; esac

# git 子指令的定位：行首或 ; & | 之後的 git [-C <dir>] <sub>
GIT_PREFIX='(^|[;&|][[:space:]]*)git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?'
is_git_sub() { [[ "$CMD" =~ ${GIT_PREFIX}$1([[:space:]]|$) ]]; }

DENY_AMEND="$(yaml_kv "$GUARD" deny_amend)"
DENY_NO_VERIFY="$(yaml_kv "$GUARD" deny_no_verify)"
DENY_FORCE_PUSH="$(yaml_kv "$GUARD" deny_force_push)"
DENY_COMMIT_DEFAULT="$(yaml_kv "$GUARD" deny_commit_on_default_branch)"
DEFAULT_BRANCH="$(yaml_kv "$GUARD" default_branch)"

if [ "$DENY_AMEND" = "true" ] && is_git_sub commit && [[ "$CMD" =~ --amend ]]; then
  deny "shan-guard：禁止 git commit --amend（.shan/guard.yaml: deny_amend）。審查後的修正一律另開 follow-up commit，保留「原本寫錯、審查後改對」的歷史。"
fi

if [ "$DENY_NO_VERIFY" = "true" ] && [[ "$CMD" =~ --no-verify ]]; then
  deny "shan-guard：禁止 --no-verify（.shan/guard.yaml: deny_no_verify）。hook 被擋就修訊息或內容，不繞過。"
fi

if [ "$DENY_FORCE_PUSH" = "true" ] && is_git_sub push \
   && [[ "$CMD" =~ (--force|--force-with-lease|[[:space:]]-f([[:space:]]|$)) ]]; then
  deny "shan-guard：禁止 force push（.shan/guard.yaml: deny_force_push）。不得改寫已 push 的歷史。"
fi

if [ "$DENY_COMMIT_DEFAULT" = "true" ] && [ -n "$DEFAULT_BRANCH" ] && is_git_sub commit; then
  BRANCH="$(git -C "$(project_root)" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  if [ "$BRANCH" = "$DEFAULT_BRANCH" ]; then
    deny "shan-guard：目前在預設分支 \`$DEFAULT_BRANCH\` 上，禁止 commit（.shan/guard.yaml: deny_commit_on_default_branch）。先依 config G 節開分支。"
  fi
fi

exit 0
