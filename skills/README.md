# Skills for v1.1.0

## options-strategy-advisor-flow

Drop-in enhancement for the existing `options-strategy-advisor` skill (which ships with the Financial Services Plugins marketplace).

Install:
```bash
cp options-strategy-advisor-flow/flow_analyzer.py ~/.claude/skills/options-strategy-advisor/scripts/
```

Uses CBOE delayed options data (free, no API key). Computes Put/Call ratio, Max Pain, IV term structure/skew, Top OI strikes, GEX.

## a-share-flow-analyzer

New skill for A-share smart-money flow (融资融券 + 龙虎榜 + 主力资金).

Install:
```bash
cp -r a-share-flow-analyzer ~/.claude/skills/
```

Requires `TUSHARE_TOKEN` env var.

Both analyzers are called automatically from `/analyze` Module 六C when running v1.1.0+.
