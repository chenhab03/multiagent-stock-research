# Multi-Agent Debate Mechanism

## Why a debate?

A single LLM pass on fundamentals + valuation + technicals + sentiment naturally hedges. It writes both sides weakly. The antidote, proven by TauricResearch/TradingAgents, is a structured adversarial debate: force one agent to build the strongest Bull case, another the strongest Bear case, then a third to judge.

We adopt that pattern and extend it in three ways:

1. **Richer input** — the debate operates on 13 modules of structured analysis, not just 4 analysts + sentiment. The Bull and Bear subagents receive a distilled ~3000-token summary of all prior modules, including specific numbers, scores, and framework verdicts.
2. **Self post-mortem** — the main agent reads its own past HTML reports on the ticker (via `Glob` + `Read`) and generates a "what was I wrong about last time" review. This prior-call reconciliation table is injected into both Bull and Bear prompts, forcing each side to account for the agent's historical track record.
3. **Hold rule D** — instead of banning Hold (TradingAgents' rule) or allowing it freely, we distinguish *active* Hold (deliberate judgment, waiting for a specific catalyst) from *passive* Hold (genuine indecision, position halved as penalty).

---

## Flow

```
Main agent context (full 13-module analysis in window)
│
├─ Step 0: History review
│   └─ Glob → Read past HTML reports → generate prior-call reconciliation table
│
├─ Step 1: Round 1 — Opening (parallel)
│   ├─ [Agent: Bull Researcher]  →  Top 3 bull theses (JSON)
│   └─ [Agent: Bear Researcher]  →  Top 3 bear theses (JSON)
│   → Main agent collects → ROUND_1_TRANSCRIPT
│
├─ Step 2: Round 2 — Rebuttal (parallel)
│   ├─ [Agent: Bull Researcher]  →  Rebuttals to each Bear Round 1 claim (JSON)
│   └─ [Agent: Bear Researcher]  →  Rebuttals to each Bull Round 1 claim (JSON)
│   → Main agent collects → ROUND_2_TRANSCRIPT
│
├─ Step 3: Round 3 — Closing (parallel)
│   ├─ [Agent: Bull Researcher]  →  Strengthened points + concessions + final confidence (JSON)
│   └─ [Agent: Bear Researcher]  →  Symmetric (JSON)
│   → Main agent collects → ROUND_3_TRANSCRIPT
│
└─ Step 4: Judge verdict (main agent, no subagent)
    └─ Reads full transcript → verdict JSON → renders markdown for report
```

All Bull/Bear subagents use `subagent_type=general-purpose`. They are dispatched in parallel pairs using the `Agent` tool. Each subagent receives only its own prompt — Bull does not see Bear's Round 1 until Round 2, and Bear does not see Bull's Round 1 until Round 2.

---

## Role prompts

### Bull Researcher and Bear Researcher

The Bull and Bear share the same structural template; only the role label, orientation, and output direction differ. See `commands/analyze.md` §Module 十 Step 1 for the exact Bull template and §Step 2 for the rebuttal template.

Key constraints in both prompts:
- Every claim must cite a specific number or fact from the module summary
- Every claim must stand alone (no cross-referencing the opponent's arguments in Round 1)
- Every claim must be Popper-falsifiable: state what evidence would disprove it
- Every claim carries a confidence score 1-10
- Output is strict JSON — no freeform prose, no hedging language

### Bear Researcher

Symmetric mirror of the Bull template. The Bear prompt has an additional constraint: no softer language like "but there is potential" — the bear case must be argued at full strength.

### Round 2 prompts

Each side receives the full Round 1 output of the opponent. They must rebut each opposing claim individually, with one of three verdicts per rebuttal: `refuted` / `partially_refuted` / `concede`. Concessions are critical — they prevent the final Judge from having to dismiss a strongly-argued claim that one side never actually engaged with.

See `commands/analyze.md` §Module 十 Step 2 for exact templates.

### Round 3 prompts

Each side receives the full transcript of both Round 1 and Round 2. The closing statement (under 400 characters) must: (a) identify which of its own arguments survived unrebutted, (b) explicitly concede points the opponent successfully argued, and (c) state a final confidence score with a delta explanation vs Round 1.

See `commands/analyze.md` §Module 十 Step 3 for exact templates.

### Judge

The main agent acts as Judge in Step 4 — no subagent. It reads all three rounds of transcript (already in its context window) and applies the Hold rule D framework below. The Judge outputs a structured JSON verdict that is then rendered into the final report section.

See `commands/analyze.md` §Module 十 Step 4 for the exact Judge prompt template and JSON schema.

---

## Hold rule D

The verdict must be one of exactly four options. "And the answer is somewhere in the middle" is not allowed.

| Verdict | Condition | Position size | Scorecard impact |
|---|---|---|---|
| BUY | Bull arguments decisively win; Bear's majority of claims were successfully refuted; Bull's final confidence materially exceeds Bear's | 100% of calculated position | `scorecard_adjustments` applied |
| SELL | Bear arguments decisively win | 100% of calculated position (short or exit) | `scorecard_adjustments` applied |
| HOLD_active | Judge deliberately chooses to wait — must state either: a specific catalyst not yet landed, or a specific key variable not yet resolved, or that price is already at fair value with no significant edge | 100% of calculated position | `scorecard_adjustments` applied |
| HOLD_passive | Bull and Bear are genuinely balanced; Judge cannot make a clear call | **50% of calculated position** | `scorecard_adjustments` applied **plus −1 composite score** |

The key design choice: do not let Hold be free. Either commit to a directional view, or commit to reducing exposure. A Judge that hides behind HOLD_passive is penalized in both position size and scorecard, making it a last resort rather than a default escape.

The `unresolved_risks` field of the verdict (claims Bear raised that Bull never successfully refuted) feeds directly into the stop-loss trigger conditions in the 建议操作 section.

---

## Token budget

| Step | Agent calls | Tokens (approximate) |
|---|---|---|
| Step 0 — history review | 0 extra calls (main agent reads files) | +45k input from HTML files |
| Step 1 — Round 1 opening | 2 subagents in parallel | ~18k total |
| Step 2 — Round 2 rebuttal | 2 subagents in parallel | ~22k total |
| Step 3 — Round 3 closing | 2 subagents in parallel | ~26k total |
| Step 4 — Judge | 0 extra calls (main agent output) | ~5k output |
| **Total added per full run** | **6 subagent calls** | **~116k tokens** |

Baseline `/analyze` without Module 10: ~80k tokens. With Module 10 (full debate): ~196k tokens. With `--quick` flag: ~80k tokens (Module 10 is entirely skipped).

The MODULE_SUMMARY passed to each subagent is generated by the main agent before dispatching Step 1. It extracts 4-6 key numbers and a one-sentence conclusion from each of modules 〇 through 九, targeting ~3000 tokens. Detailed calculations and formula derivations are excluded.

---

## Why 3 rounds, not 2 or 4?

- **Round 1** establishes the independently strongest cases. Bull and Bear subagents do not see each other's output — this forces non-hedged, fully committed opening arguments. Each claim must be falsifiable, removing vague assertions before the debate even begins.
- **Round 2** is where most of the analytical value is generated. Each side must engage specifically with every opposing claim, either refuting it with data or conceding. Concessions in Round 2 are the mechanism by which the Judge can identify which risks are genuinely unresolved. A 2-round structure (open + close) would skip this step entirely and leave the Judge unable to distinguish "Bear raised this risk but Bull ignored it" from "Bull successfully rebutted it."
- **Round 3** introduces calibrated confidence: each side selectively strengthens the claims that survived Round 2 rebuttal and explicitly acknowledges what the opponent got right. The delta in confidence (e.g., Bull drops from 8/10 to 6/10) signals to the Judge that a previously strong argument was partially undermined.
- A 4th round adds marginal analytical cost and the Judge verdict rarely changes after Round 3 — each additional exchange approaches diminishing returns once both sides have conceded what they are willing to concede.
- A 2-round structure misses the "concede with calibration" phase, which is the most important signal for the Judge.

---

## Why main-agent Judge, not a subagent Judge?

The main agent has the full 13-module analysis (modules 〇 through 九, ~80k tokens) in its context window throughout the entire debate. A subagent Judge would need to receive the full analysis summary plus all three rounds of transcript as input — a large token cost for minor independence benefit.

The main agent switching to a "Portfolio Manager" perspective in Step 4 is a standard in-context role shift. It has the additional advantage that the Judge can directly reference specific datapoints from earlier modules without them being re-stated in the prompt. This makes the Judge's key-disagreement table more precise: instead of "Bull claimed margins are expanding," the main-agent Judge can write "Bull claimed margins are expanding — however, Module 二B's 90-day estimate revision shows sell-side has cut Q3 gross margin estimates by 80bps, which supports Bear's rebuttal."
