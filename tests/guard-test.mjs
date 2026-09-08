// harness 層測試：對 scripts/guard-*.sh 餵 PreToolUse JSON，驗證拒絕／放行。執行：node tests/guard-test.mjs
import { spawnSync } from "node:child_process";
import { mkdirSync, rmSync, writeFileSync, renameSync } from "node:fs";
import path from "node:path";
import os from "node:os";

const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..");
const SB = path.join(os.tmpdir(), "shan-guard-sandbox");
const SBW = SB.replace(/\//g, "\\");

rmSync(SB, { recursive: true, force: true });
mkdirSync(path.join(SB, ".shan"), { recursive: true });
const git = (...a) => spawnSync("git", ["-C", SB, ...a], { encoding: "utf8" });
git("init", "-q", "-b", "master");
git("commit", "-q", "--allow-empty", "-m", "init");
const GUARD = `version: 2
protected_paths:
  - ".kiro/specs/**/*.md"
  - ".kiro/steering/**"
allowed_paths:
  - ".kiro/specs/**/tasks.md"
protected_existing_paths:
  - "src/main/resources/db/migration/V*.sql"
git:
  default_branch: "master"
  deny_commit_on_default_branch: true   # 註解
  deny_amend: true
  deny_no_verify: true
  deny_force_push: true
`;
const guardPath = path.join(SB, ".shan", "guard.yaml");
writeFileSync(guardPath, GUARD);

let fails = 0;
function run(name, expect, script, input, env = {}) {
  const r = spawnSync("bash", [`${REPO}/scripts/${script}`], {
    input: typeof input === "string" ? input : JSON.stringify({ cwd: SBW, ...input }),
    encoding: "utf8",
    env: { ...process.env, CLAUDE_PROJECT_DIR: SBW, ...env },
  });
  const got = r.stdout.includes('"deny"') ? "deny" : "allow";
  const ok = got === expect && r.status === 0;
  if (!ok) fails++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${ok ? "" : `  expect=${expect} got=${got} rc=${r.status} out=${r.stdout} err=${r.stderr}`}`);
}
const P = "guard-protected-paths.sh", G = "guard-git.sh";
const W = (rel) => ({ tool_name: "Write", tool_input: { file_path: path.join(SBW, rel), content: "x" } });
const B = (command) => ({ tool_name: "Bash", tool_input: { command } });

run("spec requirements 拒絕（Windows 絕對路徑）", "deny", P, W("\\.kiro\\specs\\foo\\requirements.md"));
run("spec design 拒絕（相對路徑）", "deny", P, { tool_name: "Edit", tool_input: { file_path: ".kiro/specs/foo/design.md" } });
run("spec tasks.md 放行（allowed_paths）", "allow", P, W("\\.kiro\\specs\\foo\\tasks.md"));
run("一般原始碼放行", "allow", P, W("\\src\\main\\java\\X.java"));
mkdirSync(path.join(SB, "src/main/resources/db/migration"), { recursive: true });
writeFileSync(path.join(SB, "src/main/resources/db/migration/V19__old.sql"), "-- applied");
run("已存在的 migration 拒絕（protected_existing_paths）", "deny", P, W("\\src\\main\\resources\\db\\migration\\V19__old.sql"));
run("新增的 migration 放行（檔案不存在）", "allow", P, W("\\src\\main\\resources\\db\\migration\\V20__x.sql"));
run("已存在的 migration 以相對路徑仍拒絕", "deny", P, { tool_name: "Edit", tool_input: { file_path: "src/main/resources/db/migration/V19__old.sql" } });
run("steering 子目錄拒絕", "deny", P, W("\\.kiro\\steering\\a\\b.md"));
run("content 內含假 file_path 不誤判", "allow", P, { tool_name: "Write", tool_input: { content: 'see "file_path":".kiro/specs/foo/design.md" here', file_path: path.join(SBW, "README.md") } });
run("大小寫不同仍拒絕", "deny", P, W("\\.Kiro\\Specs\\foo\\Design.md"));
run("NotebookEdit 的 notebook_path 也檢查", "deny", P, { tool_name: "NotebookEdit", tool_input: { notebook_path: path.join(SBW, ".kiro/specs/x/y.md") } });
run("git commit --amend 拒絕", "deny", G, B("git commit --amend -m x"));
run("master 上 commit 拒絕", "deny", G, B('git add a && git commit -m "feat: x"'));
run("git -C 形式 master commit 拒絕", "deny", G, B(`git -C "${SBW}" commit -m x`));
run("heredoc 多行 commit 在 master 拒絕", "deny", G, B("git commit -q -F - <<'EOF'\nfeat: x\n\nbody\nEOF"));
run("--no-verify 拒絕", "deny", G, B("git commit --no-verify -m x"));
run("push -f 拒絕", "deny", G, B("git push -f origin feat"));
run("push --force-with-lease 拒絕", "deny", G, B("git push --force-with-lease"));
run("git log 放行", "allow", G, B("git log --oneline -5"));
run("非 git 指令含 --amend 字樣放行", "allow", G, B("grep -rn -- --amend docs/"));
run("grep -f 不當 force push", "allow", G, B("grep -f patterns file"));
run("git push 正常放行", "allow", G, B("git push -u origin feat/x"));
run("git 指令在 cwd 以外的 -C 目錄仍以專案根判斷分支", "deny", G, B("git -C /tmp commit -m x"));
git("checkout", "-q", "-b", "feat/x");
run("feature 分支 commit 放行", "allow", G, B("git commit -m x"));
run("feature 分支 amend 仍拒絕", "deny", G, B("git commit --amend"));
run("SHAN_GUARD_OFF=1 放行", "allow", P, W("\\.kiro\\specs\\foo\\design.md"), { SHAN_GUARD_OFF: "1" });
renameSync(guardPath, guardPath + ".bak");
run("無 guard.yaml 靜默放行", "allow", P, W("\\.kiro\\specs\\foo\\design.md"));
renameSync(guardPath + ".bak", guardPath);
run("壞 JSON 放行", "allow", G, "not json at all");
run("空輸入放行", "allow", P, "");

console.log(fails === 0 ? "\n全部通過" : `\n失敗 ${fails} 項`);
process.exit(fails === 0 ? 0 : 1);
