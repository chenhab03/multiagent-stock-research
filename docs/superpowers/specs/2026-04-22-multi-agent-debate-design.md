# Multi-Agent Bull/Bear Debate + Self Post-Mortem for `/analyze`

**Spec date**: 2026-04-22
**Status**: Approved (pending spec-reviewer + user sign-off)
**Repo**: `multiagent-stock-research`
**Scope**: Add a multi-agent debate module and historical self-review capability to the existing `/analyze` Claude Code slash command, then publish the result as an open-source repo on GitHub.

---

## 1. Goal

Extend the existing 13-module `/analyze` command with:

1. **Module 10 (新增): Multi-Agent Bull/Bear Debate** — structured adversarial debate between Bull and Bear researchers (3 rounds), judged by a portfolio-manager agent, producing a verdict that influences the final scorecard.
2. **Self Post-Mortem** — before the debate, `/analyze` reads its own past reports on the same ticker, judges which predictions came true, and feeds that bias-correction into the debate.
3. **Publish as `multiagent-stock-research` on GitHub** — desensitize API keys, write README, ship an `install.sh`.

Non-goal: any RAG/memory/SQLite layer, any cross-ticker learning, any ground-truth backtest, any multi-platform portability (Claude Code only).

## 2. Context

- Existing command: `~/.claude/commands/analyze.md` (~1390 lines) produces a 13-module institutional-grade research report covering fundamentals, valuation, management quality, technicals, bubble risk, sentiment, etc.
- Existing companion: `~/.claude/commands/report.md` renders the analysis into a Goldman-Sachs-style HTML report (21 sections mapped to the 13 modules).
- Reports are written to `/Users/deepwish/Dropbox/project/Documents/投研报告/` using filename `{TICKER}-研报-{YYYYMMDD}.html`. 103 reports already exist.
- Inspiration: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents). Their core mechanism (Bull vs Bear debate, judged by a Research Manager) is worth adopting. Their RAG memory layer is not — it depends on simulated-trade P&L feedback that we do not have.
- The existing 13 modules already produce denser structured input than TradingAgents' 4 analysts, so the debate quality ceiling is genuinely higher.

## 3. Architecture

### 3.1 Overall flow

```
/analyze TICKER [--html] [--silent] [--quick]
  │
  ▼
[Stage A] Data fetch  (unchanged)          — yfinance / akshare / TuShare / Finnhub / FSP skills
[Stage B] 13-module analysis  (unchanged)  — Modules 〇 → 九
  │
  ▼
[Stage C] Module 10: Debate  (NEW, skipped when --quick)
  │
  ├─ Step 0: History review
  │     Glob:   {OUTPUT_DIR}/*{TICKER}*研报*.html
  │     Read:   top 3 most recent files (CC native tools, no external script)
  │     Main agent generates history-review table → inserted into report
  │
  ├─ Step 1 (parallel): Round 1 opening arguments
  │     Agent(BULL_ROUND_1, context = 13-module summary + history review)
  │     Agent(BEAR_ROUND_1, context = 13-module summary + history review)
  │
  ├─ Step 2 (parallel): Round 2 rebuttals
  │     Agent(BULL_ROUND_2, context += opponent's Round 1 output)
  │     Agent(BEAR_ROUND_2, context += opponent's Round 1 output)
  │
  ├─ Step 3 (parallel): Round 3 closing statements
  │     Agent(BULL_ROUND_3, context = full transcript)
  │     Agent(BEAR_ROUND_3, context = full transcript)
  │
  └─ Step 4: Judge verdict
        Main agent applies Hold rule D (see §3.4)
        Output: verdict, disagreements table, unresolved risks, scorecard adjustments
  │
  ▼
[Stage D] Scorecard + recommendation  (modified)
  — Scorecard incorporates Judge's adjustments
  — Stop-loss in "建议操作" references unresolved risks
  — If --html, call /report which renders new Section 12B (debate block)
```

### 3.2 Subagent prompt contract

All four debate roles (Bull, Bear, Judge, History-Reviewer) are defined inline in `commands/analyze.md`. Each Bull/Bear subagent receives:

- `TICKER`
- 13-module **summary** (not full text) — ~5k tokens covering key findings and numbers from each module
- History-review markdown from Step 0
- Round number (1, 2, or 3)
- Opponent's prior-round output (Rounds 2 and 3 only)

Output format is strict JSON:

```json
{
  "thesis": [{"claim": "...", "data": "...", "confidence": 1-10}],
  "rebuttals": [...],          // Round 2 only
  "closing": "...",            // Round 3 only
  "overall_confidence": 1-10
}
```

Bull and Bear prompts are **symmetric mirrors** of each other. Key anti-hedge instructions: "Do not write the opposing case. Do not soften with 'but there are risks'. That is the other role's job."

### 3.3 Judge prompt

Runs in the main agent context (not a subagent), receives the full transcript plus history review. Output JSON:

```json
{
  "verdict": "BUY | SELL | HOLD_active | HOLD_passive",
  "key_disagreements": [
    {"issue": "...", "bull_view": "...", "bear_view": "...", "judgment": "bull|bear|tie"}
  ],
  "winner_reasons": ["..."],
  "loser_fatal_flaws": ["..."],
  "unresolved_risks": ["..."],
  "scorecard_adjustments": {"基本面质量": "+1", "估值吸引力": "-1"}
}
```

### 3.4 Hold rule D (mixed)

The Judge may return one of four verdicts:

| Verdict | When | Downstream effect |
|---|---|---|
| `BUY` | Bull case clearly dominates | Normal scorecard, normal position size |
| `SELL` | Bear case clearly dominates | Normal scorecard, normal position size |
| `HOLD_active` | Judge actively chooses Hold with a specific reason (waiting for catalyst, key variable unresolved, near fair value with no edge) | Normal position size, verdict flagged as "active hold" |
| `HOLD_passive` | Bull and Bear have roughly equivalent merit and Judge cannot decide | **Position size halved**, scorecard composite score -1, verdict flagged "passive hold — low conviction" |

Rationale: don't let the LLM use Hold as a cop-out (TradingAgents bans Hold entirely for this reason), but also don't force a binary call when genuine ambiguity exists. Distinguish conviction from indecision.

### 3.5 History review

Uses Claude Code's native `Glob` and `Read` tools — no external Python script.

Procedure described in `commands/analyze.md`:
1. Glob `{OUTPUT_DIR}/*{TICKER}*研报*.html` where `{OUTPUT_DIR}` defaults to `~/equity-research/` but is overridable via env var `RESEARCH_OUTPUT_DIR`.
2. Take 3 most recent files (Glob sorts by mtime desc).
3. Read each. The LLM extracts relevant sections (评级 / 目标价 / 投资论题 / 风险) in-context — no field-level parsing.
4. Main agent generates a review table comparing each past call to current price and events.

Token cost: reading 3 full HTMLs ~45k tokens input. Acceptable given Claude 1M context.

Zero historical reports → output "首次分析该股票" and skip review. Debate proceeds without the bias-correction input.

### 3.6 Token budget

| Phase | New calls | Token impact |
|---|---|---|
| Existing 13 modules | 0 | ~50k in / ~30k out (unchanged) |
| History review | 0 extra calls (in main agent) | +45k input |
| Debate Round 1 (parallel) | 2 subagents | 2 × (7k in + 2k out) = 18k |
| Debate Round 2 (parallel) | 2 subagents | 2 × (9k in + 2k out) = 22k |
| Debate Round 3 (parallel) | 2 subagents | 2 × (11k in + 2k out) = 26k |
| Judge | 0 extra calls | +5k out |
| **Total additional per /analyze** | +6 subagent calls | **~115k tokens** |
| **Full run total** | | **~195k tokens** (vs ~80k currently, ~2.4× cost) |

Batch runs (e.g., 8 tickers) scale linearly: ~1.5M tokens. `--quick` flag skips the debate and preserves the original ~80k cost for fast screening.

## 4. Component inventory

| # | File | Purpose | Size (approx) |
|---|---|---|---|
| 1 | `commands/analyze.md` | Desensitized fork of current `~/.claude/commands/analyze.md` + new Module 10 section + 4 debate role prompts + history-review procedure | current 1390 → ~1700 lines |
| 2 | `commands/report.md` | Desensitized fork of current `~/.claude/commands/report.md` + new Section 12B rendering spec + CSS for debate blocks | current 355 → ~500 lines |
| 3 | `install.sh` | Copy `commands/*.md` to `~/.claude/commands/` with backup of existing files | ~25 lines |
| 4 | `README.md` | Bilingual (EN on top, 中文 below), positioning, Quick Start, comparison vs TradingAgents, commands, sample output, roadmap, disclaimer | ~200 lines |
| 5 | `LICENSE` | MIT | standard |
| 6 | `.gitignore` | `.env`, `*.html`, `*.pdf`, `.DS_Store`, `__pycache__/`, `*.db`, etc. | ~15 lines |
| 7 | `docs/methodology.md` | 13-module framework explanation (distilled from analyze.md's "必须包含" section) | ~300 lines |
| 8 | `docs/debate-mechanism.md` | Debate flow diagram + role prompts + Hold rule D explanation | ~200 lines |
| 9 | `docs/superpowers/specs/2026-04-22-multi-agent-debate-design.md` | this document | — |
| 10 | `docs/superpowers/plans/2026-04-22-multi-agent-debate-plan.md` | Implementation plan (produced by writing-plans skill) | — |

No Python scripts. No tests directory. No requirements files. Zero runtime dependencies beyond Claude Code itself.

### 4.1 Final repo structure

```
multiagent-stock-research/
├── .git/                       (Dropbox-ignored via xattr)
├── .gitignore
├── LICENSE
├── README.md
├── install.sh
├── commands/
│   ├── analyze.md
│   └── report.md
└── docs/
    ├── methodology.md
    ├── debate-mechanism.md
    └── superpowers/
        ├── specs/
        │   └── 2026-04-22-multi-agent-debate-design.md
        └── plans/
            └── 2026-04-22-multi-agent-debate-plan.md
```

## 5. Command interface

Unchanged from current command shape; one new flag.

| Invocation | Behavior |
|---|---|
| `/analyze NVDA` | 13 modules + debate + markdown console output |
| `/analyze NVDA --html` | + generate HTML report with new Section 12B |
| `/analyze NVDA --silent` | no console markdown, only progress lines |
| `/analyze NVDA --html --silent` | silent + HTML (batch-friendly) |
| `/analyze NVDA,AAPL,TSLA --html --silent` | batch mode, each ticker fully debated |
| `/analyze NVDA --quick` | **NEW** — skip Module 10 debate (fast screening) |
| `/report NVDA` | regenerate HTML from existing analysis |

Debate rounds are fixed at 3. No `--debate-rounds` flag (YAGNI).

Silent mode never prints subagent output — that behavior is independent of `--silent`. `--silent` controls main-agent verbosity only.

## 6. Report section 12B (HTML)

`commands/report.md` inserts a new block between Section 12A (sentiment) and Section 13 (charts):

```
12A. Sentiment / module 九
12B. Multi-Agent Debate & Judge Verdict  ← NEW
13.  ECharts interactive visualizations
14.  Composite scorecard + cross-framework validation + recommendation (reflects debate)
15.  Bottom line + footer
```

Visual design:
- Verdict banner at top (green for BUY, red for SELL, amber for HOLD, different amber shades for active vs passive).
- History review table with 对/错 coloring (green check, red cross).
- Bull and Bear Top-3 shown as a two-column grid (left green border, right red border).
- Rebuttal outcomes as a checklist (✅ successful rebuttal / ❌ unresolved).
- Unresolved risks highlighted in a warning box, labeled as "→ stop-loss / trim triggers".
- Scorecard adjustment table showing original score → debate-adjusted score with reasoning.

CSS additions (~80 lines) integrate with the existing Goldman-Sachs color palette (deep blue `#0B2744`, green `#0D7A48`, red `#A82020`, amber `#8B6914`).

The composite scorecard in Section 14 gains a new row: `辩论调整后最终分` showing the delta.

## 7. Error handling

| Scenario | Strategy |
|---|---|
| Zero historical reports found | Print "首次分析该股票 — 无历史可对账" in the review block; debate proceeds normally |
| `Read` fails on a historical HTML file (corrupt, too large) | Skip that file, continue with the rest |
| Subagent call fails (network, rate limit) | Retry once. If still failing, skip that round for that side; Judge works with incomplete transcript and scorecard is flagged "辩论不完整" |
| Subagent returns malformed JSON | Main agent tolerant-parses: fill missing fields with defaults (`confidence: 5`, `data: "N/A"`), proceed |
| Judge cannot decide between BUY/SELL even after transcript analysis | Fall back to `HOLD_passive` (position halved, scorecard -1) |
| Data-fetch stage fails (unchanged from current behavior) | Error out before reaching debate; no partial run |
| `RESEARCH_OUTPUT_DIR` env var not set | Default to `~/equity-research/` and create directory if missing |
| Env vars `TUSHARE_TOKEN` / `FINNHUB_TOKEN` missing | Print warning; relevant data sections become N/A; analysis continues |

No state persistence. Every `/analyze` invocation is independent. Same-day re-runs overwrite the HTML file (matches current behavior).

## 8. Desensitization

Only two categories of changes from the private `~/.claude/commands/` versions:

**API keys** (2 lines in analyze.md, L67-68):
```python
# private version
TUSHARE_TOKEN = "<REDACTED>"
FINNHUB_TOKEN = "<REDACTED>"

# public version
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
FINNHUB_TOKEN = os.environ.get("FINNHUB_TOKEN", "")
```

**Output path** (~5 occurrences in analyze.md + report.md):
```python
# private
OUTPUT_DIR = "/Users/deepwish/Dropbox/project/Documents/投研报告/"

# public
OUTPUT_DIR = os.environ.get(
    "RESEARCH_OUTPUT_DIR",
    os.path.expanduser("~/equity-research/")
)
```

Nothing else changes. Email / username / other local references are not in the command files.

Git history safety: all commits from day one use the desensitized form. The private command files at `~/.claude/commands/` are never committed to this repo. No history rewriting ever needed.

## 9. Testing strategy

No unit test framework (no Python code to test). Testing is entirely end-to-end and manual, with structured checklists.

### 9.1 E2E verification set

Run all four and confirm every item on the checklist:

```
1. /analyze NVDA          (US, has history)
2. /analyze 0700.HK       (HK, has history)
3. /analyze 600519        (A-share, has history)
4. /analyze PLTR          (US, cold-start — no history)
```

### 9.2 Verification checklist

Per-run checks:
- [ ] Module 10 section appears in markdown output
- [ ] History review table shows N past reports (or "首次分析")
- [ ] Bull Top-3 and Bear Top-3 both cite specific numbers
- [ ] Rebuttal round quotes opponent's Round 1 claims
- [ ] Judge verdict ∈ {BUY, SELL, HOLD_active, HOLD_passive}
- [ ] Unresolved risks are cited in the stop-loss section of "建议操作"
- [ ] Scorecard shows a "辩论调整" row
- [ ] `grep -i "tushare_token\|finnhub_token" output.html` returns no hex tokens
- [ ] Total token consumption < 220k per run (from Claude Code's built-in meter)

### 9.3 HTML rendering checks (manual)

- [ ] Open HTML in Chrome: Section 12B renders without broken layout
- [ ] Bull/Bear two-column grid aligned, border colors correct
- [ ] Verdict banner color matches verdict value
- [ ] History review 对/错 cells show green/red text
- [ ] Print preview (A4 landscape) not broken

### 9.4 Regression (non-debate modules)

Run the current `~/.claude/commands/analyze.md` on NVDA and save as baseline. Run the new version on NVDA. Diff the modules 〇 through 九. Any non-trivial difference outside of the scorecard adjustment must be flagged.

### 9.5 Pre-commit checks

Add a simple shell script `./check.sh` runnable before each commit:

```bash
#!/usr/bin/env bash
set -e
echo "Checking for API token leaks..."
rg -i "tushare_token\s*=\s*['\"][a-f0-9]{20,}" commands/ docs/ && { echo "LEAK"; exit 1; } || echo "clean"
rg -i "finnhub_token\s*=\s*['\"][a-f0-9]{20,}" commands/ docs/ && { echo "LEAK"; exit 1; } || echo "clean"
echo "Checking for absolute paths..."
rg "/Users/[a-z]+/" commands/ && { echo "HARDCODED PATH"; exit 1; } || echo "clean"
```

## 10. Publishing plan

1. Complete implementation (see plan doc).
2. Run full E2E checklist on 4 tickers.
3. Run `./check.sh` — must pass.
4. Initial commits on `main` branch (all files desensitized from day one).
5. Create GitHub repo `multiagent-stock-research`, public, MIT license.
6. Set topics: `claude-code`, `agent`, `stock-research`, `llm`, `multi-agent`, `equity-research`.
7. Push.
8. Create Release `v1.0.0` with release notes (direct 1.0 launch, not a 0.x preview).
9. Share on X / V2EX / 即刻 with pre-drafted posts.

## 11. Out of scope (explicit)

- Persistence layer (SQLite / JSON memory / embedding store).
- Cross-ticker RAG retrieval.
- Automated outcome feedback / backtest loop.
- Any reflection or lesson generation.
- Alternative agent framework integrations (OpenCode, Codex, Cursor, generic Python). Future work.
- Porting FSP plugin logic to standalone. Future work.
- Refactoring of the existing 13-module prompts beyond desensitization.
- Adding / removing analysis modules.
- New visualization styles beyond what section 12B requires.
- CI / GitHub Actions automation (too expensive with Claude API; manual E2E instead).
- Unit test framework adoption (no Python code to test).

## 12. Open questions

None remaining at spec sign-off. All design decisions made:

- Subagent dispatch model: real parallel via `Agent` tool (not single-prompt role-play).
- Debate rounds: 3 (opening / rebuttal / closing).
- Token strategy: subagents receive 13-module **summary** not full text.
- History review: Claude native `Glob` + `Read`, no external script.
- Hold rule: D (mixed active/passive distinction, passive halves position).
- Module 12B placement: between 12A and 13.
- Bull/Bear visual: green/red border accents on a Goldman-style palette.
- New flag: `--quick` only, no `--debate-rounds`.
- Scope: Claude Code only, no portability layer.
- Desensitization: API keys + output path only.
- README: single bilingual file.

## 13. Success criteria

The spec is considered delivered when:

1. A fresh Claude Code user can `git clone`, run `./install.sh`, set two env vars, and run `/analyze NVDA --html` successfully on first try.
2. Generated HTML contains a complete Section 12B with history review, Bull/Bear Top-3, rebuttal outcomes, unresolved risks, and verdict banner.
3. `./check.sh` passes — no token leaks, no hardcoded user paths.
4. E2E checklist passes on all 4 canonical tickers.
5. Regression diff on existing 13 modules shows no unintended changes.
6. Repo is public on GitHub with README, LICENSE, and a v1.0.0 release.
