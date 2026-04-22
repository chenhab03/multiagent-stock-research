# Multi-Agent Debate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Bull/Bear debate module (Module 10) and historical self-review to the `/analyze` Claude Code slash command, then publish the desensitized result as a v1.0.0 public GitHub repo named `multiagent-stock-research`.

**Architecture:** The private `~/.claude/commands/analyze.md` (1267 lines) and `~/.claude/commands/report.md` (355 lines) are forked into `commands/analyze.md` and `commands/report.md` inside `/Users/deepwish/Dropbox/project/Documents/投研报告/dev/`. API keys and the output path are replaced with env-var reads. Module 10 is inserted into analyze.md between Module 九 (sentiment, ends ~L1117) and the composite scorecard (starts L1118). The debate itself is orchestrated inside analyze.md's prompt: history review uses Claude Code's native `Glob`+`Read` tools, and three rounds of Bull vs Bear subagents are dispatched via the `Agent` tool with `subagent_type=general-purpose`. The Judge verdict is produced in the main agent context, not a subagent. Report.md gains a new Section 12B that renders the debate as HTML.

**Tech Stack:** Claude Code (Skill + Agent + Glob + Read + Bash tools). No external runtime dependencies. Existing Python inside analyze.md (yfinance/akshare/TuShare/Finnhub data fetch) is preserved as-is except for two token constants and one output path constant switched to `os.environ.get(...)`.

**Spec:** [2026-04-22-multi-agent-debate-design.md](../specs/2026-04-22-multi-agent-debate-design.md)

---

## Ground rules for the implementer

- The repo is at `/Users/deepwish/Dropbox/project/Documents/投研报告/dev/` (we'll call this `$REPO` for brevity in this doc — in your shell set `REPO="/Users/deepwish/Dropbox/project/Documents/投研报告/dev"`).
- `$REPO/.git` has already been marked Dropbox-ignored via `xattr`. Do not undo that.
- `$REPO/.gitignore` is already in place and committed.
- The initial commit `b919ef3` already contains this plan's parent spec.
- The private source files live at `~/.claude/commands/analyze.md` and `~/.claude/commands/report.md`. **Never modify those in this plan — only read them.** The public forks at `$REPO/commands/*.md` are what we edit.
- Desensitization rule: the committed files must never contain a real 32+ hex-char token, a `/Users/<name>/` path, or an email address. A `check.sh` script catches violations.
- Verification before commit: every task that modifies a command file ends with `./check.sh` passing. Every task that modifies a Python snippet inside a command ends with a `python3 -c "import ast; ast.parse(open('commands/analyze.md').read().split('```python')[N].split('```')[0])"` on any changed snippet. Every E2E task ends with a successful `/analyze` run against the named ticker.
- Commits should be small and semantic. Message format: `<type>: <summary>` using `feat`, `fix`, `chore`, `docs`, `test`, `refactor` as the type.

---

## File map

| Path (relative to `$REPO`) | Action | Source |
|---|---|---|
| `commands/analyze.md` | Create | Fork `~/.claude/commands/analyze.md`, desensitize, insert Module 10 |
| `commands/report.md` | Create | Fork `~/.claude/commands/report.md`, desensitize, insert Section 12B |
| `install.sh` | Create | New — copies `commands/*.md` to `~/.claude/commands/` with backup |
| `check.sh` | Create | New — greps for token/path leaks pre-commit |
| `LICENSE` | Create | MIT template, copyright holder "Han Chen" |
| `README.md` | Create | New — bilingual (EN on top, 中文 below) |
| `docs/methodology.md` | Create | New — 13-module framework distilled from analyze.md's quality-standards section |
| `docs/debate-mechanism.md` | Create | New — debate flow, role prompts, Hold rule D |
| `docs/superpowers/specs/...` | Already exists | Spec doc from previous session (committed as `b919ef3`) |
| `docs/superpowers/plans/2026-04-22-multi-agent-debate-plan.md` | This document | — |
| `.gitignore` | Already exists | — |
| `.git/` | Already exists | — |

Nothing else. No `scripts/`, no `tests/`, no `.env.example`, no `requirements.txt`.

---

## Phase 1 — Fork and desensitize

Pure copy + 3 small edits. Gets the baseline published-grade command files into the repo before any feature work. Keeps the initial change set small and reviewable.

### Task 1: Fork analyze.md

**Files:**
- Create: `$REPO/commands/analyze.md`
- Source: `~/.claude/commands/analyze.md`

- [ ] **Step 1: Copy the file verbatim**

Run:
```bash
REPO="/Users/deepwish/Dropbox/project/Documents/投研报告/dev"
cp ~/.claude/commands/analyze.md "$REPO/commands/analyze.md"
wc -l "$REPO/commands/analyze.md"
```

Expected: `1267 lines`

- [ ] **Step 2: Replace the two hardcoded API tokens**

Find in `$REPO/commands/analyze.md` around lines 67-68:
```python
TUSHARE_TOKEN = "<REDACTED_TUSHARE_HEX_TOKEN>"
FINNHUB_TOKEN = "<REDACTED_FINNHUB_TOKEN>"
```

Replace with:
```python
import os
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
FINNHUB_TOKEN = os.environ.get("FINNHUB_TOKEN", "")
if not TUSHARE_TOKEN:
    print("⚠️  Set TUSHARE_TOKEN env var for A-share analyst data (https://tushare.pro)")
if not FINNHUB_TOKEN:
    print("⚠️  Set FINNHUB_TOKEN env var for US insider/institutional data (https://finnhub.io)")
```

Because the same two constants are referenced from multiple Python code blocks further down in the file (HK and US data fetch sections), add the same `os.environ.get(...)` pattern to every block that assigns or reads them. Grep to find them all:

```bash
grep -n 'TUSHARE_TOKEN\|FINNHUB_TOKEN' "$REPO/commands/analyze.md"
```

For each match that re-assigns the constant, replace the literal string with the `os.environ.get(...)` form. For matches that only read the variable, no change needed.

- [ ] **Step 3: Replace the hardcoded output directory**

Grep all references:
```bash
grep -n '/Users/deepwish/Dropbox/project/Documents/投研报告' "$REPO/commands/analyze.md"
```

For each occurrence inside a Python code block, replace the literal string with:
```python
os.environ.get("RESEARCH_OUTPUT_DIR", os.path.expanduser("~/equity-research/"))
```

For each occurrence inside plain markdown prose (instructions to the LLM), replace the literal with the placeholder `{RESEARCH_OUTPUT_DIR}` and add one note at the top of the "输入解析" section explaining that the LLM should read the env var at the start of each run:

```markdown
### 输出路径
本命令所有报告写入 `$RESEARCH_OUTPUT_DIR` 环境变量指定的目录，默认 `~/equity-research/`。后文中所有 `{RESEARCH_OUTPUT_DIR}` 占位符均指向此路径。
```

- [ ] **Step 4: Verify Python syntax of every code block**

The file has ~15 Python code blocks. Extract and ast-parse each one:
```bash
python3 <<'EOF'
import re
with open("/Users/deepwish/Dropbox/project/Documents/投研报告/dev/commands/analyze.md") as f:
    text = f.read()
blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
print(f"Found {len(blocks)} python blocks")
import ast
for i, b in enumerate(blocks):
    try:
        ast.parse(b)
    except SyntaxError as e:
        print(f"Block {i}: SYNTAX ERROR — {e}")
        print(b[:200])
        raise
print("All python blocks parse OK")
EOF
```

Expected: `All python blocks parse OK`

- [ ] **Step 5: Commit**

```bash
cd "$REPO"
git add commands/analyze.md
git commit -m "feat: fork analyze.md, desensitize API keys and output path"
```

---

### Task 2: Fork report.md

**Files:**
- Create: `$REPO/commands/report.md`
- Source: `~/.claude/commands/report.md`

- [ ] **Step 1: Copy verbatim**

```bash
cp ~/.claude/commands/report.md "$REPO/commands/report.md"
wc -l "$REPO/commands/report.md"
```

Expected: `355 lines`

- [ ] **Step 2: Replace hardcoded output paths**

```bash
grep -n '/Users/deepwish' "$REPO/commands/report.md"
```

For each match, replace the absolute path with `{RESEARCH_OUTPUT_DIR}` (prose) or `os.environ.get("RESEARCH_OUTPUT_DIR", os.path.expanduser("~/equity-research/"))` (code), same policy as Task 1.

- [ ] **Step 3: Verify no token leaks**

```bash
grep -iE "tushare_token\s*=\s*['\"]|finnhub_token\s*=\s*['\"]" "$REPO/commands/report.md"
```

Expected: no output (report.md shouldn't have tokens in the first place).

- [ ] **Step 4: Commit**

```bash
cd "$REPO"
git add commands/report.md
git commit -m "feat: fork report.md, parameterize output path"
```

---

### Task 3: Create check.sh (pre-commit leak scanner)

**Files:**
- Create: `$REPO/check.sh`

- [ ] **Step 1: Write the script**

```bash
cat > "$REPO/check.sh" <<'SCRIPT'
#!/usr/bin/env bash
# Pre-commit verification: scan for API tokens and hardcoded user paths
# that must never ship in the public repo.
set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

fail=0

echo "→ Checking for API token leaks..."
if grep -rE "tushare_token\s*=\s*['\"][a-f0-9]{20,}" commands/ docs/ 2>/dev/null; then
    echo "  ✗ LEAK: literal TuShare token found"
    fail=1
fi
if grep -rE "finnhub_token\s*=\s*['\"][a-z0-9]{20,}" commands/ docs/ 2>/dev/null; then
    echo "  ✗ LEAK: literal Finnhub token found"
    fail=1
fi

echo "→ Checking for hardcoded user paths..."
# exclude docs/superpowers/** from this check — specs and plans may reference
# the user's local environment as context
if grep -rE "/Users/[a-z_][a-z0-9_-]+/" commands/ 2>/dev/null; then
    echo "  ✗ LEAK: hardcoded absolute /Users/ path in commands/"
    fail=1
fi

echo "→ Checking for email leaks..."
if grep -rE "[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}" commands/ docs/methodology.md docs/debate-mechanism.md README.md 2>/dev/null; then
    echo "  ✗ LEAK: email address in public-facing file"
    fail=1
fi

if [ $fail -eq 0 ]; then
    echo "✓ All leak checks passed"
else
    echo ""
    echo "FAIL: fix the leaks above before committing"
    exit 1
fi
SCRIPT
chmod +x "$REPO/check.sh"
```

- [ ] **Step 2: Run it**

```bash
cd "$REPO"
./check.sh
```

Expected: `✓ All leak checks passed`

If it fails, fix the leak first; don't modify `check.sh` to hide it.

- [ ] **Step 3: Commit**

```bash
git add check.sh
git commit -m "chore: add check.sh for API key and path leak detection"
```

---

## Phase 2 — History review (Module 10 Step 0)

Add the historical self-review procedure to `analyze.md`. This is prompt engineering, not Python — the logic lives in markdown instructions that tell the main agent to use `Glob`+`Read`.

### Task 4: Add Module 10 header and history-review section

**Files:**
- Modify: `$REPO/commands/analyze.md` (insert around line 1117, right before `## 📋 综合评分卡`)

- [ ] **Step 1: Find the insertion point**

```bash
grep -n "^## 📋 综合评分卡\|^## 九、舆情" "$REPO/commands/analyze.md"
```

Expected output shows line ~1078 for 九 start and ~1118 for scorecard. Module 10 goes between them: right after module 九 ends (which in turn is right before `---\n\n## 📋 综合评分卡`).

- [ ] **Step 2: Insert Module 10 header + Step 0 prose**

Insert just above the `## 📋 综合评分卡` line:

```markdown
---

## 十、多空辩论与终审裁决 (v1.0 新增)

**执行条件**：仅当未传入 `--quick` flag 时执行。

### Step 0 — 历史判断对账 (Prior Call Review)

在辩论开始前，你必须先对自己过去对该股票的判断进行诚实复盘，以修正本次分析的潜在偏误。

**操作步骤**：

1. 使用 `Glob` 工具搜索历史报告：
   - Pattern: `{RESEARCH_OUTPUT_DIR}/*{TICKER}*研报*.html`
   - Ticker 大小写不敏感，A 股纯数字、港股 4-5 位数字、美股字母代码均支持
2. Glob 默认按 mtime 倒序排列，取前 3 个文件
3. 对每个文件使用 `Read` 工具读取完整内容（HTML 格式）
4. 基于读到的内容，生成以下对账表：

```markdown
### 历史判断对账表

当前价：$[X] | 当前日期：[YYYY-MM-DD] | 找到历史报告：[N] 份

| 日期 | 当时评级 | 当时目标价 | 当时核心多头论点 | 当时核心风险 | 实际后续走势 | 对/错 |
|------|---------|-----------|-----------------|------------|-------------|-------|
| [日期1] | [BUY/SELL/HOLD] | $[X] | [一句话] | [一句话] | [价格变化+事件] | [✅对/❌错/⏳未定] |
| ...  | ... | ... | ... | ... | ... | ... |

### 关键反思
- **哪些判断兑现了？** [列举]
- **哪些预测错得离谱？原因是什么？** [诚实剖析，不要辩护]
- **哪些多头/空头担忧没有发生？** [可用于校准本次辩论的偏误]
- **如果上次看多/看空但股价相反走，本次分析应该更谨慎在哪些维度？**
```

5. 如果找到 0 份历史报告，输出：
   ```markdown
   ### 历史判断对账表
   当前价：$[X] | 首次分析该股票 — 无历史可对账
   ```
   然后直接进入 Step 1（辩论开场），不生成反思段落。

6. 如果 Glob 失败或目录不存在，降级：在对账表位置写 `（历史报告目录不可访问，跳过对账）`，继续辩论。

**这个对账表将插入到最终报告的"模块十"开头，并作为后续三轮辩论的 context 传给 Bull/Bear subagent。**

---
```

(Step 1/2/3 prompts follow in subsequent tasks.)

- [ ] **Step 3: Verify the file still has valid markdown structure**

```bash
grep -n "^## " "$REPO/commands/analyze.md" | head -30
```

Expected: sections appear in order 〇 → 一 → 二 → 二A → 二B → 三 → 四 → 五 → 六 → 七 → 七A → 七B → 八 → 九 → **十** → 📋 综合评分卡 → 建议操作 → 质量标准 → HTML 输出.

- [ ] **Step 4: check.sh still passes**

```bash
cd "$REPO"
./check.sh
```

- [ ] **Step 5: Commit**

```bash
git add commands/analyze.md
git commit -m "feat(analyze): add Module 10 history review (Step 0)"
```

---

### Task 5: Smoke-test history review on a real ticker

No automated test possible. Manual E2E smoke test only.

- [ ] **Step 1: Install the current dev analyze.md into ~/.claude/commands/ (keep backup)**

```bash
cp ~/.claude/commands/analyze.md ~/.claude/commands/analyze.md.pre-v1-backup
cp "$REPO/commands/analyze.md" ~/.claude/commands/analyze.md
```

- [ ] **Step 2: Set env vars for the test run**

```bash
export TUSHARE_TOKEN="<your_real_token>"
export FINNHUB_TOKEN="<your_real_token>"
export RESEARCH_OUTPUT_DIR="/Users/deepwish/Dropbox/project/Documents/投研报告"
```

- [ ] **Step 3: In Claude Code, run**

```
/analyze NVDA --quick
```

The `--quick` flag isn't implemented yet (that's Task 9), so this will actually run the full flow including the new Module 10 Step 0 but without the rest of Module 10 being defined. This is fine for a smoke test of the history review alone. You should see:

- The history-review table appear with up to 3 past NVDA reports (or "首次分析" if none exist).
- The "关键反思" bullets filled in.
- The rest of the report proceeds, potentially erroring out when it reaches the undefined Step 1 later. That's expected and OK.

- [ ] **Step 4: If history review output looks reasonable, continue. If it looks wrong (wrong files found, malformed table), fix Task 4's prompt and rerun.**

- [ ] **Step 5: Restore the backup (we're not done; don't leave a broken command installed)**

```bash
cp ~/.claude/commands/analyze.md.pre-v1-backup ~/.claude/commands/analyze.md
```

---

## Phase 3 — Debate prompts (Module 10 Steps 1–3)

Three rounds of parallel Bull/Bear subagents via the `Agent` tool.

### Task 6: Define the Bull/Bear role prompt templates

**Files:**
- Modify: `$REPO/commands/analyze.md` (continue Module 10 section, after Step 0)

- [ ] **Step 1: Append Step 1 prose and role prompt templates**

Append after the Step 0 block from Task 4:

```markdown
### Step 1 — Round 1 开场辩论

**派发两个 subagent 并行执行**（使用 `Agent` 工具，`subagent_type=general-purpose`）：

#### Bull Researcher 提示词模板

```
你是 Bull Researcher，独立论证 BUY {TICKER}。

## 可用信息

### 13 模块分析摘要
{MODULE_SUMMARY}

（这是 2500-5000 token 的摘要，涵盖基本面/估值/管理层/技术面/情绪等关键发现和数字。）

### 历史判断对账
{HISTORY_REVIEW}

## 任务
列出 Top 3 多头论据。每条必须：
- 引用具体数字或事实（来自 13 模块摘要）
- 独立成立，不提及 Bear 的论据
- 标注 confidence 1-10
- 说明该论据如果错了，会被什么 evidence 证伪（Popper style）

## 不要
- Hedge 措辞（"但也有风险"）
- 写 Bear Case（那不是你的任务）
- 泛泛而谈（"公司优秀"、"行业景气"）— 必须具体

## 输出（严格 JSON，无额外文字）
{
  "thesis": [
    {"claim": "...", "data": "...", "confidence": 1-10, "falsifiable_by": "..."},
    {"claim": "...", "data": "...", "confidence": 1-10, "falsifiable_by": "..."},
    {"claim": "...", "data": "...", "confidence": 1-10, "falsifiable_by": "..."}
  ],
  "overall_confidence": 1-10
}
```

#### Bear Researcher 提示词模板

```
你是 Bear Researcher，独立论证 SELL 或避免持有 {TICKER}。

## 可用信息

### 13 模块分析摘要
{MODULE_SUMMARY}

### 历史判断对账
{HISTORY_REVIEW}

## 任务
列出 Top 3 空头论据。每条必须：
- 引用具体数字或事实（来自 13 模块摘要）
- 独立成立，不提及 Bull 的论据
- 标注 confidence 1-10
- 说明该论据如果错了，会被什么 evidence 证伪（Popper style）

## 不要
- Hedge 措辞（"但也有潜力"）
- 写 Bull Case（那不是你的任务）
- 泛泛而谈 — 必须具体（具体的客户/产品/财务风险）

## 输出（严格 JSON，无额外文字）
{
  "thesis": [...],
  "overall_confidence": 1-10
}
```

### 派发指令

使用 `Agent` 工具并发派发两个 subagent：
- `description`: "Bull researcher for {TICKER}"
- `subagent_type`: `general-purpose`
- `prompt`: [上方 Bull 提示词模板，{TICKER}/{MODULE_SUMMARY}/{HISTORY_REVIEW} 填入真实值]

同时派发 Bear subagent（对称）。

### MODULE_SUMMARY 生成规则

`{MODULE_SUMMARY}` 由**主 agent 在派发 subagent 前生成**，从已完成的模块〇~九 中抽取：
- 每个模块保留：关键数字（4-6 个）、最终结论（1 句话）、scorecard 评分
- 丢弃：详细计算过程、公式推导、备选方案讨论
- 目标长度：~3000 tokens

如果某模块产出已经很简洁，直接复制即可。

### 收到两个 subagent 返回后

- 把两个 JSON 合并存入 `ROUND_1_TRANSCRIPT`（稍后用于 Round 2 context）。
- 在最终报告中先不展示（Round 3 结束后再统一展示）。
```

- [ ] **Step 2: Append Step 2 (rebuttal round) instructions**

```markdown
### Step 2 — Round 2 反驳辩论

**再次并行派发**，但两个 subagent 的 prompt 现在注入对方 Round 1 的输出。

#### Bull Round 2 提示词模板

```
你是 Bull Researcher。你在 Round 1 已经提出了自己的多头论据。现在 Bear 提出了他们的空头论据（见下方）。你的任务是**逐条反驳**他们的论据。

## 可用信息

### 13 模块分析摘要
{MODULE_SUMMARY}

### 历史判断对账
{HISTORY_REVIEW}

### 你 Round 1 的多头论据
{BULL_ROUND_1}

### Bear Round 1 的空头论据（反驳对象）
{BEAR_ROUND_1}

## 任务
对 Bear Round 1 每一条 thesis 逐条反驳：
- 引用具体数据反驳（不能只说"我不同意"）
- 明确标注：你成功反驳了 / 你部分反驳了 / 你承认这一条确实站得住

## 输出（严格 JSON）
{
  "rebuttals": [
    {
      "target_bear_claim": "（Bear Round 1 claim 1 的原话）",
      "my_rebuttal": "...",
      "supporting_data": "...",
      "verdict": "refuted | partially_refuted | concede"
    },
    ... (对每条 Bear thesis 都要有一个 rebuttal)
  ]
}
```

#### Bear Round 2 提示词模板

[对称镜像，把 Bull/Bear 互换]

### 派发与存储

同 Step 1，并行派发两个 subagent，结果合并进 `ROUND_2_TRANSCRIPT`。
```

- [ ] **Step 3: Append Step 3 (closing round) instructions**

```markdown
### Step 3 — Round 3 终陈

**第三次并行派发**。双方基于完整 transcript 做终陈。

#### Bull Round 3 提示词模板

```
你是 Bull Researcher。两轮辩论已结束，现在做终陈。

## 可用信息（完整 transcript）
### 13 模块分析摘要
{MODULE_SUMMARY}

### 历史判断对账
{HISTORY_REVIEW}

### 你 Round 1 的多头论据
{BULL_ROUND_1}

### Bear Round 1 的空头论据
{BEAR_ROUND_1}

### 你 Round 2 的反驳
{BULL_ROUND_2}

### Bear Round 2 的反驳
{BEAR_ROUND_2}

## 任务
写一段简短的终陈（<400 字）：
1. **强化**：哪些多头论据未被 Bear 有效反驳？这些是你的 conviction 基石。
2. **承认**：哪些空头担忧 Bear 说得对，你不得不承认？
3. **结论**：基于上述，你对 BUY {TICKER} 的最终 confidence（1-10）是多少？比 Round 1 更高/更低/不变？

## 输出（严格 JSON）
{
  "strengthened_points": ["..."],
  "conceded_points": ["..."],
  "final_confidence": 1-10,
  "confidence_delta_reason": "..."
}
```

#### Bear Round 3 提示词模板

[对称镜像]

### 派发与存储

同前，并行派发，合并为 `ROUND_3_TRANSCRIPT`。
```

- [ ] **Step 4: check.sh and file structure sanity**

```bash
cd "$REPO"
./check.sh
grep -c "^### Step" commands/analyze.md
```

Expected: `./check.sh` passes; Step count increases by 3 (Steps 0, 1, 2, 3 under Module 10).

- [ ] **Step 5: Commit**

```bash
git add commands/analyze.md
git commit -m "feat(analyze): add Bull/Bear 3-round debate prompts (Module 10 Steps 1-3)"
```

---

## Phase 4 — Judge verdict and scorecard integration (Module 10 Step 4)

### Task 7: Add the Judge prompt and Hold rule D

**Files:**
- Modify: `$REPO/commands/analyze.md` (Module 10, append after Step 3)

- [ ] **Step 1: Append Step 4 (Judge) prose**

```markdown
### Step 4 — Judge 终审裁决

**主 agent 直接完成，不派发 subagent**（Judge 需要看所有 context，放在主 agent 里更方便）。

你现在切换到 Portfolio Manager 视角，对三轮辩论做裁决。

## 可用信息（已在你的 context 里）
- 13 模块完整分析
- 历史判断对账
- ROUND_1_TRANSCRIPT / ROUND_2_TRANSCRIPT / ROUND_3_TRANSCRIPT

## Hold 规则 D（重要 — 不允许和稀泥式 Hold）

你的 verdict 必须是以下四个之一：

1. **BUY** — Bull 论据明显占优（Bull final_confidence 显著高于 Bear，且 Bear 的大部分 thesis 被成功反驳）
2. **SELL** — Bear 论据明显占优
3. **HOLD_active** — 你**主动**选择 Hold，理由必须是以下之一：
   - 等待特定催化剂落地（明确写出是哪个催化剂）
   - 关键变量未明朗（明确写出是哪个变量）
   - 股价已在合理估值区间，无显著 edge
4. **HOLD_passive** — Bull/Bear 论据相当，你无法裁决。这个是"认怂"verdict。
   - **惩罚**：仓位自动砍半，综合评分扣 1 分
   - 只在确实无法判断时使用，不要用它逃避表态

## 裁决输出（严格 JSON）

```json
{
  "verdict": "BUY | SELL | HOLD_active | HOLD_passive",
  "key_disagreements": [
    {
      "issue": "（例如：毛利率是否已见顶）",
      "bull_view": "...",
      "bear_view": "...",
      "judgment": "bull | bear | tie",
      "judge_reasoning": "..."
    },
    ... (3-5 条核心分歧)
  ],
  "winner_reasons": ["胜方胜在哪"],
  "loser_fatal_flaws": ["败方致命伤是什么"],
  "unresolved_risks": [
    "（Bear 提出但 Bull 未能反驳的风险 — 这些将成为止损/减仓触发条件）"
  ],
  "scorecard_adjustments": {
    "基本面质量": "+1",
    "估值吸引力": "-2",
    ...
  },
  "hold_reason": "（如果 verdict 是 HOLD_active 或 HOLD_passive，说明具体理由）",
  "confidence_in_verdict": 1-10
}
```

### 将裁决渲染成报告内容

裁决完成后，生成如下 markdown 插入到报告的模块十末尾（Step 0 的对账表已在开头）：

```markdown
### 🥊 辩论 Transcript 精华

#### 🐂 多头 Top 3（Round 1）
1. **[claim 1]** — [data] (confidence: X/10)
2. ...

#### 🐻 空头 Top 3（Round 1）
1. ...

#### 反驳结果（Round 2）
- ✅ 多头成功反驳空头: [claim + 反驳点]
- ❌ 多头未能反驳空头: [claim] → **这进入未解风险清单**
- ✅ 空头成功反驳多头: [claim + 反驳点]
- ❌ 空头未能反驳多头: [claim]

#### 终陈（Round 3）
- **多头终 confidence**: X/10 （Round 1 是 Y/10，变化原因：...）
- **空头终 confidence**: X/10

### 🏆 Judge 终审

| 项目 | 内容 |
|------|------|
| **裁决** | [BUY / SELL / HOLD_active / HOLD_passive] |
| **裁决置信度** | [X]/10 |
| **胜方理由** | [...] |
| **败方致命伤** | [...] |
| **Hold 理由（如适用）** | [...] |

#### 核心分歧表
| 议题 | 🐂 多头立场 | 🐻 空头立场 | 裁决 | 理由 |
|------|------------|------------|------|------|
| [...] | [...] | [...] | [✅多头/❌空头/⏳平] | [...] |

#### ⚠️ 未被反驳的风险（→ 止损/减仓触发条件）
- [风险 1]
- [风险 2]
- [风险 3]

#### 对评分卡的影响
| 维度 | 原始分 | 辩论后 | 调整原因 |
|------|-------|--------|---------|
| 基本面质量 | X | X+/- | [...] |
| ... | ... | ... | ... |
```

**重要**：这段渲染完后，报告才能接着走 `## 📋 综合评分卡` 区块。综合评分卡里的"综合评分"一行必须应用 Judge 的 `scorecard_adjustments`。如果 verdict 是 `HOLD_passive`，综合评分额外 -1 分。
```

- [ ] **Step 2: Modify the 综合评分卡 section to incorporate debate adjustments**

Find `## 📋 综合评分卡` (around line 1118) and modify the table to add a new row **at the bottom**, just before `### 多框架交叉验证`:

```markdown
| **辩论调整** | [见模块十 scorecard_adjustments] | Bull/Bear Debate | 从模块十 Judge 的 scorecard_adjustments 应用调整 |
| **HOLD_passive 惩罚** | [−1 如适用] | Hold Rule D | 仅当 verdict=HOLD_passive 时 -1；否则 0 |
| **综合评分（辩论调整后）** | **[X]/10** | | **14 维度 + 辩论调整** |
```

Keep the original "**综合评分** **[X]/10**" row for transparency; the new row shows the post-debate value.

- [ ] **Step 3: Modify the 建议操作 section to reference unresolved risks**

Find `## 建议操作` (around line 1153). In its table, modify the **止损位** row:

```markdown
| **止损位** | $[X] — 触发条件：[从模块十未被反驳的风险清单中选 2-3 条最具体的作为监测点] |
```

And add a row for Hold rule D:

```markdown
| **仓位调整规则** | [正常仓位 / HOLD_passive → 正常仓位的 50% / HOLD_active → 正常仓位] |
```

- [ ] **Step 4: check.sh**

```bash
cd "$REPO"
./check.sh
```

- [ ] **Step 5: Commit**

```bash
git add commands/analyze.md
git commit -m "feat(analyze): add Judge verdict, Hold rule D, and scorecard integration"
```

---

### Task 8: Full E2E smoke test of Module 10

- [ ] **Step 1: Install the latest dev analyze.md**

```bash
cp "$REPO/commands/analyze.md" ~/.claude/commands/analyze.md
```

- [ ] **Step 2: In Claude Code, run (NO --quick flag this time — we want the full debate)**

```
/analyze NVDA
```

- [ ] **Step 3: Verify the following all appear in the output:**

- [ ] Module 10 header `## 十、多空辩论与终审裁决`
- [ ] Step 0 history review table (or "首次分析")
- [ ] Bull Top 3 with specific data cited
- [ ] Bear Top 3 with specific data cited
- [ ] Rebuttal list with at least some `✅ 成功反驳` and `❌ 未能反驳`
- [ ] Round 3 closing with confidence deltas
- [ ] Judge verdict ∈ {BUY, SELL, HOLD_active, HOLD_passive}
- [ ] Key disagreements table with 3-5 rows
- [ ] Unresolved risks listed
- [ ] Scorecard adjustment table
- [ ] Final "综合评分（辩论调整后）" row in 综合评分卡
- [ ] 建议操作 止损位 references unresolved risks

- [ ] **Step 4: If anything is wrong, fix the corresponding prompt block and repeat**

Common issues and where to fix them:
- Bull/Bear don't cite numbers → tighten "必须引用具体数字" wording in Task 6 Step 1
- Round 2 doesn't reference Round 1 claims → verify Round 2 prompt includes `{BEAR_ROUND_1}` / `{BULL_ROUND_1}` correctly
- Judge always picks HOLD_passive → strengthen the "不允许和稀泥式 Hold" wording in Task 7 Step 1
- Scorecard row not appearing → re-check Task 7 Step 2 placement

- [ ] **Step 5: No commit needed (no file changes if all passed)**

If fixes were needed:
```bash
cd "$REPO"
git add commands/analyze.md
git commit -m "fix(analyze): tighten Module 10 prompts after E2E smoke test"
```

---

## Phase 5 — `--quick` flag

### Task 9: Add `--quick` flag handling

**Files:**
- Modify: `$REPO/commands/analyze.md` (around lines 14-23, the `### 输入解析` and `### 批量模式执行逻辑` sections)

- [ ] **Step 1: Find the input-parsing section**

```bash
grep -n "^### 输入解析\|^### 批量模式\|argument-hint" "$REPO/commands/analyze.md" | head
```

- [ ] **Step 2: Modify input parsing to recognize `--quick`**

In the "可选标志" subsection under `### 输入解析` (around line 20), add:

```markdown
  - `--quick` — 跳过模块十辩论（快速筛查模式），成本降回原始 ~80k tokens
```

- [ ] **Step 3: Modify batch-mode logic to pass `--quick` through**

In the "批量模式执行逻辑" subsection, ensure the flag list parsing includes `--quick` alongside `--html` and `--silent`.

- [ ] **Step 4: Modify Module 10 header to respect `--quick`**

At the very top of the Module 10 section (added in Task 4), the line `**执行条件**：仅当未传入 --quick flag 时执行。` is already there. Expand it:

```markdown
**执行条件**：仅当未传入 `--quick` flag 时执行本整个模块十。

如果 `--quick` 存在：
1. 跳过模块十全部内容（Step 0 至 Step 4）
2. 在最终报告中插入一行说明：`> 本次运行使用 --quick 模式，已跳过多空辩论。如需完整深度研究，重新运行不带 --quick 的 /analyze {TICKER}。`
3. 综合评分卡的 "辩论调整" 和 "HOLD_passive 惩罚" 两行标注为 `N/A (--quick mode)`
4. 建议操作的"止损位"回落到仅用模块七的风险清单（不引用模块十未解风险）
```

- [ ] **Step 5: check.sh**

```bash
cd "$REPO"
./check.sh
```

- [ ] **Step 6: E2E verify `--quick`**

Install and run:
```bash
cp "$REPO/commands/analyze.md" ~/.claude/commands/analyze.md
```
In CC: `/analyze NVDA --quick`

Verify:
- [ ] Module 10 section is absent or shows only the `--quick mode` note
- [ ] Scorecard shows `N/A (--quick mode)` for debate-related rows
- [ ] Total token consumption is close to pre-v1.0 baseline (~80k)

- [ ] **Step 7: Commit**

```bash
cd "$REPO"
git add commands/analyze.md
git commit -m "feat(analyze): add --quick flag to skip debate for fast screening"
```

---

## Phase 6 — report.md Section 12B

### Task 10: Add Section 12B specification to report.md

**Files:**
- Modify: `$REPO/commands/report.md` (insert between line 253 "### 12A" and line 269 "### 13")

- [ ] **Step 1: Find insertion point**

```bash
grep -n "^### 12A\|^### 13\." "$REPO/commands/report.md"
```

- [ ] **Step 2: Insert Section 12B block**

Between the existing Section 12A block and Section 13 block, insert:

````markdown
### 12B. 多空辩论与终审裁决（对应模块十，v1.0 新增）

**条件**：仅当 /analyze 输出包含"模块十"内容时渲染此区块。如果 /analyze 使用了 --quick，跳过本节，在 HTML 里显示一行灰色提示："本次分析使用 --quick 快速模式，未进行多空辩论。"

**视觉风格**：配合现有高盛风格的深蓝色调 (#0B2744)。新增色：牛绿 #0D7A48、熊红 #A82020、持有琥珀 #8B6914。

**结构**（HTML 骨架）：

```html
<section class="section debate-section">
  <h2 class="section-title">
    <span class="section-number">十</span> 多空辩论与终审裁决
  </h2>

  <!-- 裁决横幅 -->
  <div class="verdict-banner verdict-{BUY|SELL|HOLD-active|HOLD-passive}">
    <div class="verdict-label">🏆 Judge Verdict</div>
    <div class="verdict-value">{BUY | SELL | HOLD}</div>
    <div class="verdict-subtitle">{active / passive 如适用}</div>
    <div class="verdict-confidence">Confidence: {X}/10</div>
  </div>

  <!-- Step 0: 历史判断对账 -->
  <div class="subsection">
    <h3>历史判断对账（Prior Call Review）</h3>
    <table class="history-review">
      <thead>
        <tr>
          <th>日期</th><th>当时评级</th><th>目标价</th>
          <th>当时核心论点</th><th>当时核心风险</th>
          <th>实际走势</th><th>对/错</th>
        </tr>
      </thead>
      <tbody>
        <!-- 每行一份历史报告 -->
        <!-- 对/错列使用 .correct 或 .wrong class 染色 -->
      </tbody>
    </table>
    <div class="reflection-box">
      <h4>关键反思</h4>
      <ul>{每条以 • 开头}</ul>
    </div>
  </div>

  <!-- Bull vs Bear Top 3 对比 -->
  <div class="subsection">
    <h3>Round 1: 开场论据</h3>
    <div class="bull-bear-grid">
      <div class="bull-column">
        <h4>🐂 多头 Top 3</h4>
        <ol>
          <li>
            <strong>{claim}</strong>
            <div class="data">{data}</div>
            <div class="confidence">Confidence: {X}/10</div>
          </li>
          ...
        </ol>
      </div>
      <div class="bear-column">
        <h4>🐻 空头 Top 3</h4>
        <ol>...</ol>
      </div>
    </div>
  </div>

  <!-- 反驳结果 -->
  <div class="subsection">
    <h3>Round 2: 反驳结果</h3>
    <ul class="rebuttal-list">
      <li class="rebuttal-success">✅ <strong>多头成功反驳空头:</strong> {...}</li>
      <li class="rebuttal-failed">❌ <strong>多头未能反驳空头:</strong> {...} <em>(→ 进入未解风险)</em></li>
      <li class="rebuttal-success">✅ <strong>空头成功反驳多头:</strong> {...}</li>
      <li class="rebuttal-failed">❌ <strong>空头未能反驳多头:</strong> {...}</li>
    </ul>
  </div>

  <!-- 终陈 -->
  <div class="subsection">
    <h3>Round 3: 终陈</h3>
    <div class="closing-grid">
      <div class="bull-closing">
        <div class="confidence-delta">多头终 confidence: <strong>{X}/10</strong> (Δ {+/-Y})</div>
        <p>{reason}</p>
      </div>
      <div class="bear-closing">...</div>
    </div>
  </div>

  <!-- 核心分歧 -->
  <div class="subsection">
    <h3>核心分歧矩阵</h3>
    <table class="debate-matrix">
      <thead>
        <tr><th>议题</th><th>🐂 多头立场</th><th>🐻 空头立场</th><th>裁决</th><th>理由</th></tr>
      </thead>
      <tbody>...</tbody>
    </table>
  </div>

  <!-- 未解风险 -->
  <div class="subsection warning-box">
    <h3>⚠️ 未被反驳的风险 → 止损/减仓触发条件</h3>
    <ul>
      <li>{风险 1}</li>
      ...
    </ul>
  </div>

  <!-- 评分卡调整 -->
  <div class="subsection">
    <h3>对综合评分卡的影响</h3>
    <table class="scorecard-adjustment">
      <thead><tr><th>维度</th><th>原始分</th><th>辩论后</th><th>调整原因</th></tr></thead>
      <tbody>...</tbody>
    </table>
  </div>
</section>
```

**CSS**（插入到 report.md 的 CSS 总定义区域）：

```css
.debate-section { margin-top: 4rem; padding-top: 2rem; border-top: 3px solid #0B2744; }

.verdict-banner {
  padding: 2rem; text-align: center; border-radius: 4px;
  margin: 1.5rem 0 2.5rem; color: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.verdict-label { font-size: 0.9rem; letter-spacing: 2px; opacity: 0.85; }
.verdict-value { font-size: 2.5rem; font-weight: 700; margin: 0.3rem 0; }
.verdict-subtitle { font-size: 0.9rem; opacity: 0.8; }
.verdict-confidence { font-size: 1rem; margin-top: 0.5rem; }

.verdict-BUY { background: linear-gradient(135deg, #0A5F38, #0D7A48); }
.verdict-SELL { background: linear-gradient(135deg, #8B1A1A, #A82020); }
.verdict-HOLD-active { background: linear-gradient(135deg, #8B6914, #A68318); }
.verdict-HOLD-passive { background: linear-gradient(135deg, #666666, #888888); }

.bull-bear-grid, .closing-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;
  margin: 1.5rem 0;
}
.bull-column { border-left: 4px solid #0D7A48; padding-left: 1.25rem; }
.bear-column { border-left: 4px solid #A82020; padding-left: 1.25rem; }

.bull-column h4, .bear-column h4 { margin-top: 0; }
.bull-column ol li, .bear-column ol li { margin-bottom: 1rem; }
.bull-column .data, .bear-column .data {
  font-size: 0.85rem; color: #555; font-style: italic; margin: 0.25rem 0;
}
.bull-column .confidence, .bear-column .confidence {
  font-size: 0.8rem; color: #888;
}

.debate-matrix th { background: #0B2744; color: white; font-weight: 600; padding: 0.75rem; }
.debate-matrix td { padding: 0.75rem; border-bottom: 1px solid #e0e0e0; }

.history-review th { background: #0B2744; color: white; padding: 0.6rem; }
.history-review td { padding: 0.6rem; vertical-align: top; }
.history-review .correct { color: #0D7A48; font-weight: 600; }
.history-review .wrong { color: #A82020; font-weight: 600; }

.rebuttal-list { list-style: none; padding-left: 0; }
.rebuttal-list li { padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0; }
.rebuttal-success { color: #0D7A48; }
.rebuttal-failed { color: #A82020; }
.rebuttal-failed em { color: #8B1A1A; margin-left: 0.5rem; }

.warning-box {
  background: #FDF6E3; border-left: 4px solid #8B6914;
  padding: 1rem 1.5rem; border-radius: 2px;
}
.warning-box h3 { margin-top: 0; color: #6B4E0A; }

.reflection-box {
  background: #F8F9FA; padding: 1rem 1.5rem;
  margin-top: 1rem; border-radius: 2px;
}
.reflection-box h4 { margin-top: 0; color: #0B2744; }

.scorecard-adjustment th { background: #0B2744; color: white; padding: 0.6rem; }
.scorecard-adjustment td { padding: 0.6rem; }

@media print {
  .debate-section { page-break-before: always; }
  .verdict-banner { box-shadow: none; }
}
```

**数据映射**（从 /analyze 的 markdown 输出 → HTML 字段）：
- verdict-banner 的 verdict-value 和 verdict class → 模块十 Step 4 Judge 的 `verdict` 字段
- verdict-confidence → `confidence_in_verdict`
- history-review 表 → 模块十 Step 0 对账表直接迁移
- bull-column / bear-column → Round 1 的 thesis 列表
- rebuttal-list → Round 2 汇总
- closing-grid → Round 3 final_confidence + delta
- debate-matrix → `key_disagreements`
- warning-box → `unresolved_risks`
- scorecard-adjustment → `scorecard_adjustments` + 原始分
````

- [ ] **Step 3: Update Section 14 (综合评分卡) in report.md to render debate-adjusted score**

Find `### 14. 综合评分卡` (around line 289). Add a subsection right after the main table:

```markdown
**新增渲染要求（v1.0）**：

在综合评分卡的最后一行（综合评分 X/10）**之下**新增两行 row（HTML `<tr>`）：
- `辩论调整` — 显示各维度的调整值（来自 Judge 的 scorecard_adjustments）
- `综合评分（辩论调整后）` — 加粗、字号 1.3rem、背景色 #F5F5DC（米色强调）

如果 --quick 模式或 Judge verdict 为 `HOLD_passive`，额外显示：
- HOLD_passive 时：新增一行 `HOLD 惩罚 −1` 并相应调整最终分
- --quick 时：两行均显示 `N/A (--quick mode)`
```

- [ ] **Step 4: Update Section 14 "建议操作" rendering to include Hold rule D**

In the 建议操作 subsection (also in Section 14 of report.md, around line 310), add:

```markdown
**新增渲染要求（v1.0）**：

- **止损位** 说明需 append: "触发条件: [列 2-3 条来自模块十未被反驳的风险]"
- 新增一行表格 **仓位调整规则**: 
  - verdict=HOLD_passive → "正常仓位的 50%（被动 Hold 惩罚）"
  - verdict=HOLD_active → "正常仓位（主动 Hold，等待 [catalyst]）"
  - verdict=BUY/SELL → "正常仓位"
```

- [ ] **Step 5: check.sh**

```bash
cd "$REPO"
./check.sh
```

- [ ] **Step 6: Commit**

```bash
git add commands/report.md
git commit -m "feat(report): add Section 12B for Module 10 debate rendering + CSS"
```

---

### Task 11: E2E test report.md on real analyze output

- [ ] **Step 1: Install latest report.md**

```bash
cp "$REPO/commands/report.md" ~/.claude/commands/report.md
```

- [ ] **Step 2: In CC, run on a ticker that has a recent analysis**

```
/analyze NVDA --html
```

- [ ] **Step 3: Open the generated HTML in Chrome**

```bash
open "$RESEARCH_OUTPUT_DIR/NVDA-研报-$(date +%Y%m%d).html"
```

- [ ] **Step 4: Visually verify**

- [ ] Section 12B is present between sentiment section and charts section
- [ ] Verdict banner color matches verdict value (green=BUY, red=SELL, amber=HOLD active, grey=HOLD passive)
- [ ] Bull (green border) and Bear (red border) columns align cleanly
- [ ] History review table has 对/错 cells in correct colors
- [ ] Rebuttal list items have ✅/❌ with correct green/red color
- [ ] Warning box for unresolved risks uses amber background
- [ ] Scorecard shows both original and debate-adjusted composite score
- [ ] 建议操作 shows stop-loss triggers citing unresolved risks
- [ ] Print preview (Cmd-P) → A4 landscape doesn't break the layout

- [ ] **Step 5: If any visual issues, fix the CSS in `$REPO/commands/report.md` Task 10 Step 2, then redo E2E**

- [ ] **Step 6: No commit if all passed; otherwise**

```bash
git add commands/report.md
git commit -m "fix(report): tweak Section 12B CSS after HTML QA"
```

---

## Phase 7 — Install script and pre-publish docs

### Task 12: Write install.sh

**Files:**
- Create: `$REPO/install.sh`

- [ ] **Step 1: Write the script**

```bash
cat > "$REPO/install.sh" <<'SCRIPT'
#!/usr/bin/env bash
# Install multiagent-stock-research commands into Claude Code.
set -euo pipefail

COMMANDS_DIR="${HOME}/.claude/commands"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$COMMANDS_DIR" ]; then
    echo "⚠️  ${COMMANDS_DIR} does not exist. Is Claude Code installed?"
    echo "   Create the directory with: mkdir -p \"${COMMANDS_DIR}\""
    exit 1
fi

echo "Installing commands to ${COMMANDS_DIR}..."

for cmd in analyze report; do
    src="${SCRIPT_DIR}/commands/${cmd}.md"
    dst="${COMMANDS_DIR}/${cmd}.md"

    if [ ! -f "$src" ]; then
        echo "✗ Source file missing: $src"
        exit 1
    fi

    if [ -f "$dst" ]; then
        backup="${dst}.backup-$(date +%Y%m%d-%H%M%S)"
        mv "$dst" "$backup"
        echo "  📦 Backed up existing ${cmd}.md → $(basename "$backup")"
    fi

    cp "$src" "$dst"
    echo "  ✓ Installed /${cmd}"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installation complete."
echo ""
echo "  Next steps:"
echo ""
echo "  1. Set API keys (add to ~/.zshrc or ~/.bashrc):"
echo "       export TUSHARE_TOKEN='your_token'    # A-shares (https://tushare.pro)"
echo "       export FINNHUB_TOKEN='your_token'    # US market (https://finnhub.io)"
echo "       export RESEARCH_OUTPUT_DIR='\${HOME}/equity-research'  # optional, default: ~/equity-research/"
echo ""
echo "  2. Restart Claude Code."
echo ""
echo "  3. Test:"
echo "       /analyze NVDA"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SCRIPT
chmod +x "$REPO/install.sh"
```

- [ ] **Step 2: Dry-run test**

```bash
bash -n "$REPO/install.sh"
```

Expected: no syntax errors.

- [ ] **Step 3: Full install test (end-to-end)**

Before running, save what you have:
```bash
mkdir -p /tmp/cc-backup
cp ~/.claude/commands/analyze.md /tmp/cc-backup/
cp ~/.claude/commands/report.md /tmp/cc-backup/
```

Run installer:
```bash
cd "$REPO"
./install.sh
```

Verify:
- [ ] Installer completes without errors
- [ ] Original `analyze.md` has been backed up with a timestamp suffix
- [ ] New `analyze.md` at `~/.claude/commands/analyze.md` is identical to `$REPO/commands/analyze.md`
- [ ] Same for report.md

```bash
diff "$REPO/commands/analyze.md" ~/.claude/commands/analyze.md && echo "analyze.md identical"
diff "$REPO/commands/report.md" ~/.claude/commands/report.md && echo "report.md identical"
```

- [ ] **Step 4: Commit**

```bash
git add install.sh
git commit -m "chore: add install.sh for copying commands into ~/.claude/commands"
```

---

### Task 13: Write LICENSE

**Files:**
- Create: `$REPO/LICENSE`

- [ ] **Step 1: Write MIT license**

```bash
cat > "$REPO/LICENSE" <<'EOF'
MIT License

Copyright (c) 2026 Han Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

DISCLAIMER: This software is for research and educational purposes only.
It is not financial advice. No representation is made that any investment
strategy or analysis will result in profit. Past performance does not
guarantee future results. Consult a licensed professional before making
investment decisions.
EOF
```

- [ ] **Step 2: Commit**

```bash
git add LICENSE
git commit -m "docs: add MIT license + disclaimer"
```

---

### Task 14: Write README.md (bilingual, single file)

**Files:**
- Create: `$REPO/README.md`

- [ ] **Step 1: Compose the README**

Full content (~200 lines) goes here. Key sections:

```markdown
# multiagent-stock-research

> Multi-agent equity research workflow for Claude Code — inspired by TradingAgents, rebuilt as a buy-side analyst command with a Goldman-Sachs-style HTML report.

[English](#english) | [中文](#中文说明)

---

## English

### What it is
A single `/analyze NVDA` command in Claude Code produces an institutional-grade research report with:

- **13 analysis modules** — macro environment, fundamentals, management quality, earnings momentum, valuation (DCF / comps / SOTP / reverse-DCF), industry positioning, catalysts, technical levels + institutional flow, risk sizing, balance-sheet health, cross-asset correlations, bubble detection, sentiment
- **Module 10: Multi-agent Bull vs Bear debate** (3 rounds: opening, rebuttal, closing) judged by a portfolio-manager agent
- **Self post-mortem** — reads your past reports on the same ticker, judges which predictions came true, feeds that bias-correction into the debate
- **Goldman-Sachs-style HTML report** — 21 sections, Goldman color palette, print-ready A4
- **Markets**: US / HK / A-shares

### vs TradingAgents

| | multiagent-stock-research | TradingAgents |
|---|---|---|
| Analysis depth | 13 modules | 4 analysts |
| Debate rounds | 3 (open / rebuttal / closing) | configurable, default 1 |
| Markets | US + HK + A-shares | US only |
| Self-reflection | ✅ reads own past reports | ❌ |
| Output format | Goldman-style HTML + scorecard + stop-loss triggers | trade decision string |
| Methodology frameworks | Graham / Buffett / O'Neil / Minervini / Druckenmiller / Marks | generic LLM prompting |
| Install | 1 shell script, no Python setup | Python package + Docker |
| Runtime deps | none (Claude Code only) | LangGraph + multiple LLM SDKs |

### Quick start

```bash
# 1. Clone
git clone https://github.com/YOUR_USER/multiagent-stock-research
cd multiagent-stock-research

# 2. Install
./install.sh

# 3. Configure (add to ~/.zshrc or ~/.bashrc)
export TUSHARE_TOKEN="..."      # A-share analyst data — https://tushare.pro
export FINNHUB_TOKEN="..."      # US insider/institutional — https://finnhub.io
export RESEARCH_OUTPUT_DIR="$HOME/equity-research"   # optional, default ~/equity-research

# 4. Use in Claude Code
/analyze NVDA --html
```

### Commands

| Command | Behavior |
|---|---|
| `/analyze TICKER` | Full 13 modules + debate, markdown output |
| `/analyze TICKER --html` | Also generate HTML report |
| `/analyze TICKER --silent` | No console output, progress lines only |
| `/analyze TICKER --quick` | Skip Module 10 debate (fast screening) |
| `/analyze T1,T2,T3 --html --silent` | Batch mode |
| `/report TICKER` | Regenerate HTML from latest analysis |

### Sample output
_Screenshot of an anonymized NVDA report goes here once we have one._

### Architecture
See [docs/debate-mechanism.md](docs/debate-mechanism.md) for the debate flow and [docs/methodology.md](docs/methodology.md) for the 13-module framework.

### Roadmap
- [ ] More markets (Japan, Europe)
- [ ] Optional memory layer with manual outcome feedback
- [ ] Alternative agent framework integrations (OpenCode, Cursor, generic Python)

### Contributing
PRs welcome for: bug fixes in prompts, new markets, additional frameworks, translations.

### License
MIT — see [LICENSE](LICENSE).

### Disclaimer
Research and educational use only. **Not investment advice.** No guarantee of accuracy or profitability. Consult a licensed professional before making investment decisions.

---

## 中文说明

### 这是什么
Claude Code 里一个 `/analyze NVDA` 命令 → 机构级深度研报，包含：

- **13 模块分析** — 大盘环境、基本面、管理层质量、盈利动量、估值（DCF / 可比 / SOTP / 反向 DCF）、行业定位、催化剂、技术面 + 机构资金、仓位风险、资产负债表、跨资产相关性、泡沫检测、舆情
- **模块十：多智能体多空辩论**（3 轮：开场 / 反驳 / 终陈）由组合经理 agent 裁决
- **自我复盘** — 读取同股票过往报告，判断过去预测对错，喂给本次辩论做偏误校正
- **高盛风格 HTML 研报** — 21 区块，高盛配色，A4 打印友好
- **市场覆盖**：美股 / 港股 / A 股

### vs TradingAgents
[同上英文对比表]

### 快速开始
[同上英文命令]

### 命令参数
[同上英文]

### 方法论
[Graham 安全边际、Buffett 护城河、O'Neil CAN SLIM、Minervini Stage、Druckenmiller 宏观、Marks 周期等框架的集成]

### License
MIT

### 免责声明
仅供研究和教育用途。**不构成投资建议。**过往业绩不保证未来收益，投资前请咨询持牌专业人士。
```

- [ ] **Step 2: Lint the markdown**

```bash
# Sanity check: line count and no stray syntax
wc -l "$REPO/README.md"
grep -cE "^#+\s" "$REPO/README.md"  # count headings
```

Expected: ~200 lines, 20+ headings.

- [ ] **Step 3: Run check.sh**

```bash
cd "$REPO"
./check.sh
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add bilingual README with comparison vs TradingAgents"
```

---

### Task 15: Write docs/methodology.md

**Files:**
- Create: `$REPO/docs/methodology.md`

- [ ] **Step 1: Extract the methodology summary**

Source material: the "质量标准" / "必须包含" section of `~/.claude/commands/analyze.md` (around lines 1174-1226).

Structure the doc as:

```markdown
# 13-Module Equity Research Methodology

## Why 13 modules?
The existing multi-agent trading frameworks (TradingAgents, etc.) use 4 analyst roles. That works, but it under-uses the density of information a modern LLM can hold in context. By front-loading the analysis with 13 distinct structured modules, the downstream Bull vs Bear debate operates on denser evidence and produces higher-quality disagreements.

## The modules

### Module 〇: Macro environment
- Macro regime (expansion / contraction / transition)
- Market breadth health (200-DMA, new highs vs lows)
- Market top probability (Distribution Days, Leading Stock Deterioration, Defensive Sector Rotation)
- Global risk-on / risk-off signals
- Marks cycle positioning (offense / defense)

### Module 一: Executive summary
[one-paragraph distilled thesis]

### Module 二: Fundamentals
[...]

### Module 二A: Management quality (added 2025)
- CEO/CFO backgrounds
- Capital allocation track record
- Insider ownership + recent transactions
- Guidance hit rate (last 8 quarters)
- Succession risk

### Module 二B: Earnings model + estimate tracking
...

[Continue for all 13 modules with ~4-8 bullets each. Source: analyze.md "质量标准" section.]

## Framework integration
Each module draws on one or more of these frameworks:
- **Benjamin Graham** — safety margin, Graham Number
- **Warren Buffett** — moat (5-dimensional rating: Brand, Switching Cost, Network Effect, Cost Advantage, Scale)
- **William O'Neil** — CAN SLIM 7-dimension scorecard
- **Mark Minervini** — Stage Analysis + VCP (Volatility Contraction Pattern)
- **Stanley Druckenmiller** — macro + concentration
- **Howard Marks** — cycle positioning (debt cycle, sentiment cycle, capex cycle)
- **Post-Earnings Announcement Drift** (PEAD)
- **Distribution Days** (O'Neil market-top detection)

## Cross-framework validation
The final report includes a 6-framework consensus check:
| Framework | Conclusion | Agrees? |
|---|---|---|
| Graham | Undervalued / Fair / Overvalued | — |
| Buffett | Wide / Narrow / No moat | — |
| Marks cycle | Offense / Neutral / Defense | — |
| Technical (Stage + Dow) | Up / Sideways / Down | — |
| Management | Excellent / Adequate / Concerning | — |
| Sentiment | Supportive / Neutral / Contrarian-against | — |
| **Consensus** | X/6 agreement, high/medium/low | |
```

- [ ] **Step 2: Commit**

```bash
git add docs/methodology.md
git commit -m "docs: add 13-module methodology explainer"
```

---

### Task 16: Write docs/debate-mechanism.md

**Files:**
- Create: `$REPO/docs/debate-mechanism.md`

- [ ] **Step 1: Write the doc**

```markdown
# Multi-Agent Debate Mechanism

## Why a debate?
A single LLM pass on fundamentals + valuation + technicals + sentiment naturally hedges. It writes both sides weakly. The antidote, proven by TauricResearch/TradingAgents, is a structured adversarial debate: force one agent to build the strongest Bull case, another the strongest Bear case, then a third to judge.

We adopt that pattern and extend it in three ways:
1. **Richer input** — the debate operates on 13 modules of structured analysis, not just 4 analysts + sentiment.
2. **Self post-mortem** — the main agent reads its own past reports on the ticker and generates a "what was I wrong about last time" review, which is injected into both Bull and Bear prompts.
3. **Hold rule D** — instead of banning Hold (TradingAgents' rule) or allowing it freely, we distinguish *active* Hold (deliberate judgment, waiting for a catalyst) from *passive* Hold (genuine indecision, position halved as penalty).

## Flow
[ASCII diagram of Step 0 → Step 1 (parallel) → Step 2 (parallel) → Step 3 (parallel) → Step 4]

## Role prompts

### Bull Researcher (Round 1 — opening)
[exact prompt template from analyze.md Module 10 Step 1]

### Bull Researcher (Round 2 — rebuttal)
[...]

### Bull Researcher (Round 3 — closing)
[...]

### Bear Researcher
[Symmetric mirror — in fact, "Bull" and "Bear" share the same template with one role-label substitution]

### Judge
[exact prompt template from Module 10 Step 4]

## Hold rule D

| Verdict | Condition | Position size | Scorecard impact |
|---|---|---|---|
| BUY | Bull decisively wins | 100% of calculated position | `scorecard_adjustments` applied |
| SELL | Bear decisively wins | 100% of calculated position (short) | `scorecard_adjustments` applied |
| HOLD_active | Judge chooses Hold with a specific reason | 100% of calculated position | `scorecard_adjustments` applied |
| HOLD_passive | Judge cannot decide | **50%** of calculated position | `scorecard_adjustments` applied + **−1** composite |

The key design choice: don't let Hold be free. Either commit, or commit to reducing risk.

## Token budget

| Step | Calls | Tokens (approx) |
|---|---|---|
| Step 0 history review | 0 extra (main agent) | +45k input |
| Step 1 Round 1 | 2 subagents parallel | 18k |
| Step 2 Round 2 | 2 subagents parallel | 22k |
| Step 3 Round 3 | 2 subagents parallel | 26k |
| Step 4 Judge | 0 extra | +5k output |
| **Total added per run** | 6 subagent calls | ~115k |

Baseline /analyze without Module 10: ~80k tokens. With Module 10: ~195k. With `--quick`: ~80k.

## Why 3 rounds, not 2 or 4?
- **Round 1** establishes independent strongest cases. 2 subagents don't see each other — forces non-hedged opening.
- **Round 2** is the alpha of the debate: forces each side to engage specifically with the other's strongest points.
- **Round 3** lets each side selectively strengthen and selectively concede — this is where calibrated confidence emerges.
- A 4th round adds marginal cost and the Judge rarely changes verdict.
- A 2-round structure misses the "concede with calibration" phase.

## Why main-agent Judge, not subagent Judge?
The main agent has full 13-module context in its window. A subagent Judge would need to be fed everything again — large token cost for minor independence benefit. The main agent sitting in "Judge role" is a standard pattern and works well for verdicts.
```

- [ ] **Step 2: Commit**

```bash
git add docs/debate-mechanism.md
git commit -m "docs: add debate mechanism design doc"
```

---

## Phase 8 — Final verification and regression

### Task 17: Full E2E checklist across 4 tickers

Manual. No automated assertions.

- [ ] **Step 1: Set up clean env**

```bash
export TUSHARE_TOKEN="<real>"
export FINNHUB_TOKEN="<real>"
export RESEARCH_OUTPUT_DIR="/Users/deepwish/Dropbox/project/Documents/投研报告"
cp "$REPO/commands/analyze.md" ~/.claude/commands/analyze.md
cp "$REPO/commands/report.md" ~/.claude/commands/report.md
```

- [ ] **Step 2: Run the four canonical tests**

In Claude Code, run sequentially:

1. `/analyze NVDA --html`
2. `/analyze 0700.HK --html`
3. `/analyze 600519 --html`
4. `/analyze PLTR --html`

(PLTR is the cold-start test — pick a ticker with NO existing history file in `$RESEARCH_OUTPUT_DIR`. Verify by `ls $RESEARCH_OUTPUT_DIR/*PLTR*研报*.html` returns nothing before the run.)

- [ ] **Step 3: For each run, verify**

- [ ] Module 10 present and well-formed
- [ ] Step 0 history review appropriate (shows history OR "首次分析")
- [ ] Bull Top 3 / Bear Top 3 / rebuttals / closing all present with specific numbers
- [ ] Judge verdict is one of {BUY, SELL, HOLD_active, HOLD_passive}
- [ ] Unresolved risks fed into 建议操作 stop-loss
- [ ] Scorecard shows debate-adjusted composite
- [ ] HTML Section 12B renders correctly in Chrome
- [ ] No API tokens leaked in output (grep)
- [ ] Total token consumption < 220k per run

- [ ] **Step 4: Test `/analyze NVDA --quick`**

Verify:
- [ ] Module 10 section absent or showing only "--quick mode" notice
- [ ] Scorecard shows `N/A (--quick mode)` for debate rows
- [ ] Token consumption < 100k

- [ ] **Step 5: Test batch mode**

```
/analyze NVDA,AAPL,TSLA --html --silent --quick
```

Verify:
- [ ] 3 HTML files produced
- [ ] Silent mode suppresses console markdown for all 3
- [ ] All 3 use --quick (fast)

- [ ] **Step 6: Document findings**

If any check failed, file a fix in the appropriate phase and redo. If all passed, no commit; proceed.

---

### Task 18: Regression diff vs pre-v1.0 baseline

- [ ] **Step 1: Obtain the pre-v1.0 baseline**

```bash
ls -la ~/.claude/commands/analyze.md.pre-v1-backup 2>/dev/null || \
  cp /tmp/cc-backup/analyze.md ~/.claude/commands/analyze.md.pre-v1-backup
```

- [ ] **Step 2: Generate two reports on the same ticker**

```bash
# Run with new version (already installed)
# In CC: /analyze META
# Save NVDA_new.html

# Swap to old version
cp ~/.claude/commands/analyze.md.pre-v1-backup ~/.claude/commands/analyze.md
# In CC: /analyze META
# Save NVDA_old.html

# Restore new version
cp "$REPO/commands/analyze.md" ~/.claude/commands/analyze.md
```

- [ ] **Step 3: Diff module 〇 through 九 only (the parts that should be unchanged)**

Visually compare both HTMLs. Modules 〇 through 九 should be substantively identical (some numerical variance from data-freshness is acceptable; structure and field presence must match).

Acceptable differences:
- Numeric values updated (market moved)
- Sentiment score varied (sampling variance)

Unacceptable differences:
- Missing sections
- New or removed rows in scorecard (except the new 辩论调整 and 辩论调整后 rows which are expected additions in Section 14)
- Changed column headers

If unacceptable differences appear, investigate and fix before publishing.

- [ ] **Step 4: No commit unless fixes were needed**

---

### Task 19: Run final check.sh

- [ ] **Step 1**

```bash
cd "$REPO"
./check.sh
```

Expected: all checks pass.

- [ ] **Step 2: Confirm git log looks clean**

```bash
git log --oneline
```

Expected: linear history, semantic commits, no "WIP" or "fix typo" noise (if there is, consider interactive rebase — but only if comfortable, otherwise leave as-is).

---

## Phase 9 — Publish to GitHub as v1.0.0

### Task 20: Create GitHub repo

- [ ] **Step 1: Create repo via gh CLI**

```bash
cd "$REPO"
gh repo create multiagent-stock-research \
  --public \
  --description "Multi-agent equity research workflow for Claude Code — 13 modules + Bull/Bear debate + self post-mortem. US/HK/A-shares." \
  --source=. \
  --remote=origin \
  --push
```

This creates the repo and pushes the current main branch.

- [ ] **Step 2: Set repo topics**

```bash
gh repo edit multiagent-stock-research \
  --add-topic claude-code \
  --add-topic agent \
  --add-topic stock-research \
  --add-topic llm \
  --add-topic multi-agent \
  --add-topic equity-research \
  --add-topic financial-analysis \
  --add-topic investment-research
```

- [ ] **Step 3: Verify repo is visible and correctly tagged**

```bash
gh repo view multiagent-stock-research --web
```

Opens in browser. Verify: public, README renders, topics visible, LICENSE detected.

---

### Task 21: Create v1.0.0 release

- [ ] **Step 1: Tag**

```bash
cd "$REPO"
git tag -a v1.0.0 -m "Initial public release"
git push origin v1.0.0
```

- [ ] **Step 2: Create release with notes**

```bash
gh release create v1.0.0 \
  --title "v1.0.0 — Initial public release" \
  --notes "$(cat <<'EOF'
## First public release of `multiagent-stock-research`

A multi-agent equity research workflow for Claude Code. One `/analyze NVDA` command produces an institutional-grade report with 13 analysis modules, a 3-round Bull vs Bear debate, and a self post-mortem against your own past reports.

### Highlights
- 13 structured analysis modules (macro environment, fundamentals, management quality, earnings momentum, valuation with DCF/comps/SOTP/reverse-DCF, industry positioning, catalysts, technicals, risk/position sizing, balance sheet, cross-asset correlations, bubble detection, sentiment)
- Multi-agent Bull vs Bear debate judged by a portfolio-manager agent (3 rounds)
- Historical self-review: reads your past same-ticker reports, judges which predictions came true, feeds that into the debate
- Hold rule D: distinguishes active Hold from passive Hold (with position-size penalty)
- Goldman-Sachs-style HTML report (21 sections, new Section 12B for debate)
- Markets: US, HK, A-shares
- Frameworks integrated: Graham, Buffett, O'Neil, Minervini, Druckenmiller, Marks, PEAD, Distribution Days

### Install
See [README.md](README.md) for quick-start. Short version: clone, run `./install.sh`, set two env vars, done.

### Acknowledgements
Inspired by [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents). This is a buy-side research take on the same core debate mechanism, with richer input, multi-market coverage, and more methodology frameworks.

### Disclaimer
Research and educational purposes only. Not investment advice.
EOF
)"
```

- [ ] **Step 3: Verify release**

```bash
gh release view v1.0.0
gh release view v1.0.0 --web
```

---

### Task 22: Draft share posts

**Files:**
- Create: `$REPO/docs/share-posts.md` (for your own reference; NOT pushed unless you want it)

- [ ] **Step 1: Draft posts for X, 即刻, V2EX**

```markdown
# Share post drafts

## X / Twitter (EN, 280 chars)

> Just open-sourced multiagent-stock-research 🚀
> A buy-side twist on @TauricResearch's TradingAgents:
> • 13 analysis modules (not 4)
> • Bull vs Bear debate in 3 rounds
> • Self post-mortem: reads past reports, grades past predictions
> • US / HK / A-shares
> • Goldman-style HTML report
> github.com/[...]/multiagent-stock-research

## 即刻 (中文，500 字上限)

> 开源了一个 Claude Code 研报 command：multiagent-stock-research
>
> 灵感来自 TradingAgents，但做成买方投研工作流：
> - 13 个结构化分析模块（基本面 + 估值 DCF/反向DCF/SOTP + 管理层质量 + 技术面 + 泡沫/情绪/相关性 ...）
> - 多智能体多空辩论 3 轮（开场、反驳、终陈），由组合经理裁决
> - 自我复盘：扫描过往同票报告，评估哪些预测对了 / 错了，喂给本次辩论做偏误校正
> - Hold 规则 D：主动 Hold vs 被动 Hold，后者仓位自动砍半
> - 高盛风格 HTML 研报（A4 打印友好）
> - 支持美股 / 港股 / A 股
> - 集成 Graham / Buffett / O'Neil / Minervini / Druckenmiller / Marks 等多框架
>
> 一个 /analyze NVDA 输出一份可以拿去客户面前汇报的研报。
>
> github 地址：[url]
>
> 免责声明不用我说你们都懂 🙏

## V2EX (中文, 节点: 推广 / 分享发现)

> [标题] 开源：Claude Code 里的多智能体投研 command（/analyze）
>
> [正文]
> 最近把自用的 /analyze command 打磨成了开源项目 multiagent-stock-research，分享一下。
>
> ## 做了什么
> 输入股票代码，一个命令产出一份 50 页的机构级研报，含 13 个分析模块 + 多空辩论 + 高盛风格 HTML。
>
> ## 和 TradingAgents 的区别
> - TradingAgents 主要做交易决策（BUY/SELL/HOLD 字符串）
> - 这个项目做**研报**（可视化 + 评分卡 + 止损位）
> - TradingAgents 4 个分析师，这个 13 个模块
> - TradingAgents 只覆盖美股，这个美港A 三市场都支持
> - 都有多空辩论，但这个扩展了 3 轮（开场/反驳/终陈）+ 自我复盘
>
> ## 为什么 Claude Code
> 直接用 FSP 金融插件 + 自建的 20 多个交易 skill 做深度。别的 agent 框架要达到一样深度工作量翻倍，先不搞。
>
> ## 装起来 2 分钟
> clone + install.sh + 两个 API key（TuShare/Finnhub 都免费）
>
> 地址：[url]
> 欢迎 issue / PR / 骂。
```

- [ ] **Step 2: (optional) Commit share drafts**

If you want these in the repo for future reference:
```bash
cd "$REPO"
git add docs/share-posts.md
git commit -m "docs: add share post drafts (v1.0 launch)"
git push
```

Otherwise, keep as a local file and don't commit. Your call.

---

## Done

At this point:
- `$REPO` contains commands, docs, install script, LICENSE, README, and this plan
- `check.sh` passes
- Full E2E on 4 tickers passed
- Regression diff shows no unintended changes in modules 〇-九
- GitHub repo public with v1.0.0 release
- Share posts drafted

Next (not in this plan): monitor issue tracker, iterate based on user feedback, consider Phase 10 (memory layer) once 30+ users report via real usage.
