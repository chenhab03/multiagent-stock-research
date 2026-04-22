# 13-Module Equity Research Methodology

## Why 13 modules?

The existing multi-agent trading frameworks (TradingAgents, etc.) use 4 analyst roles. That works, but it under-uses the density of information a modern LLM can hold in context. By front-loading the analysis with 13 distinct structured modules, the downstream Bull vs Bear debate operates on denser evidence and produces higher-quality disagreements.

Each module maps to a distinct information domain. Modules build on each other: the macro environment (〇) sets the risk-on/risk-off context that shapes the buy/sell recommendation in the executive summary (一), and both feed into the debate (十).

---

## The modules

### Module 〇: Macro environment (大盘环境)

Establishes the market regime before any individual-stock analysis begins, so that every subsequent module is interpreted in the right risk context.

- Macro regime classification: Risk-On expansion / Risk-Off contraction / transition, derived from yield curve, credit spreads, RSP/SPY concentration, equity-bond correlation
- Market breadth health: S&P 500 stocks above 200-DMA percentage, new-highs minus new-lows, advance-decline line trend, breadth composite score out of 100
- Market top probability: Distribution Days count (rolling 25 sessions), leading-stock deterioration level (low/medium/high), defensive sector rotation signal, top-risk composite score with traffic-light rating
- Global risk appetite: Dollar, VIX, credit spreads, commodities, EM equities — combined directional read
- Howard Marks cycle positioning (4 dimensions): industry cycle stage, market sentiment position vs 5-year P/E percentile, credit cycle signal, capex cycle direction
- Offense vs defense verdict for the current macro environment and its specific tailwind/headwind effect on the subject ticker

### Module 一: Executive summary (执行摘要)

One-paragraph distilled thesis produced after all data is gathered, written last but displayed first.

- Rating: Buy / Hold / Sell with a one-sentence rationale
- Price target with explicit upside/downside percentage and time horizon
- Core investment thesis in a single paragraph: what the company does, why now, the risk-reward asymmetry
- Conviction level: High / Medium / Low with brief justification

### Module 二: Fundamentals (基本面分析)

Most recent earnings results, business-specific KPIs, and earnings quality checks.

- Latest quarterly results table: revenue, EPS, gross margin, operating margin vs consensus — beat/miss magnitude
- Key business KPIs specific to the company (e.g., DAU, ARR, same-store sales) with YoY and QoQ changes
- Management guidance vs market expectations for the next quarter and full year
- Earnings-Trade Analyzer 5-factor score (only when a recent earnings event exists): gap size, pre-earnings trend, volume trend, MA200 position, MA50 position — scored out of 100 with A/B/C/D grade
- Earnings quality checks: operating cash flow / net income ratio, accrual ratio (>20% is a warning), accounts-receivable days trend, capex/depreciation ratio, free cash flow yield

### Module 二A: Management quality (管理层质量评估)

Management is the largest long-run variable in equity returns; evaluated separately from financials.

- Core team table: CEO/CFO/key executives with tenure and background classification (industry veteran / parachute hire / founder)
- Capital allocation track record across 4 dimensions: M&A ROI, organic growth investment efficiency, shareholder returns (dividends + buybacks as % of FCF vs peers), balance-sheet conservatism trend
- Alignment indicators: insider ownership percentage, net insider transactions over last 12 months (dollar amount and direction), compensation structure (equity-to-cash ratio), performance metrics used in incentive plans
- Guidance hit rate: last 8 quarters of revenue/EPS guidance vs actual results — hit / miss / exceed, with a cumulative rate
- Succession risk: key-person dependency level, management bench depth, whether a transition plan exists
- Overall management rating: A/B/C/D with a one-sentence summary

### Module 二B: Earnings model and estimate tracking (盈利模型与预期追踪)

Markets trade on expectation gaps, not reported numbers. This module tracks where the consensus is heading.

- Estimate revision momentum: current-quarter, next-quarter, full-year EPS consensus vs 90 days ago — direction (upgrade/downgrade/flat) and signal
- Analyst count: number upgrading vs downgrading over the same period
- Historical beat/miss record: last 8 quarters for both EPS and revenue, with beat percentages and an 8-quarter beat rate fraction
- Key sensitivity analysis: for resource/cyclical companies, commodity price sensitivity on EPS and target price; for tech/consumer, user-growth or ARPU sensitivity; at least 3 variable scenarios
- Sell-side consensus summary: count of strong-buy / buy / hold / sell ratings, consensus target price range and implied upside/downside vs current price

### Module 三: Valuation (估值分析)

Four complementary valuation lenses, each checking a different implicit assumption.

- Comparable company analysis: EV/Revenue, EV/EBITDA, P/E, revenue growth for 3-4 peers vs subject — median shown explicitly
- Graham safety margin: Graham Number (√(22.5 × EPS × BVPS)), current price, safety margin percentage; note on applicability for high-growth companies
- DCF intrinsic value: three scenarios (conservative / neutral / optimistic) with explicit growth-rate assumptions, WACC, implied value, and safety margin — not just a point estimate
- Reverse DCF — market-implied growth: at current price, what perpetual growth rate and 5-year CAGR is the market pricing in? Compare to historical realized growth
- SOTP sum-of-the-parts: segment-by-segment valuation (EV/EBITDA / DCF / P/E / NAV as appropriate), net debt deduction, SOTP total vs current market cap
- Scenario analysis: bull / base / bear target prices with probability weights and key assumptions for each

### Module 四: Industry competition (行业与竞争格局)

Competitive positioning and structural industry dynamics.

- Industry positioning: sector/niche, growth rate, penetration rate, cycle stage (early / growth / mature / declining)
- Buffett moat: 5-dimension rating (Brand/IP, Switching Costs, Network Effects, Cost Advantage, Efficient Scale) each scored 1-10, with a composite rating of Wide / Narrow / None and a moat trend direction (widening / stable / narrowing)
- vs major competitors: specific differentiation analysis against named rivals
- Hot-theme linkage (Theme Detector): current macro themes, relevance to the ticker, directional impact
- Supply-side analysis (cyclical/resource companies): new capacity pipeline, ore-grade trends, environmental approval constraints, scrap recovery rates, geopolitical supply-disruption risk; for tech/consumer, substitute technology maturity and competitive product launch cadence

### Module 五: Catalysts (催化剂与投资论题)

Identifies the events and logic that could move the stock in both directions.

- Near-term catalysts (0-6 months): specific events with approximate dates — earnings, product launches, regulatory decisions, buyback announcements
- Medium-term catalysts (6-24 months): strategic moves, market expansions, new business lines
- Bull thesis: top 3 long arguments with specific data support
- Bear thesis: top 3 short arguments / risks
- 18-month scenario paths (Scenario Analyzer): three paths (optimistic / base / pessimistic) with probability weights, 12-month price range, and the causal chain of 3 sequential effects for each path

### Module 六: Technicals (技术面与市场信号)

Price structure, institutional flow, and options sentiment.

- Price structure table: current price, 52-week high/low, distance from high, RSI-14, 50-DMA, 200-DMA
- Key technical levels: support and resistance prices, trend direction, Minervini Stage classification (Stage 1 base / Stage 2 uptrend / Stage 3 top / Stage 4 downtrend)
- Dow Theory confirmation: primary trend, secondary trend, volume confirmation — all three dimensions stated
- 13F institutional flow: last 2 quarters, count of institutions adding vs reducing, net change, named representative institutions and their direction; Smart Money accumulation vs distribution verdict
- Insider transactions: named individuals, titles, dollar amounts, dates; buyback program status and execution progress
- Options market analysis: Put/Call Ratio, IV30, 52-week IV Rank, notable unusual activity; specific strategy recommendations for bullish / bearish / neutral setups with max risk and max reward stated

### Module 七: Risk management and position sizing (风险管理与仓位建议)

Converts the analysis into an actionable trading plan with quantified risk.

- Risk matrix: company-level, industry-level, macro-level risks each rated High/Medium/Low with specific descriptions
- Scientific position sizing (Position Sizer): two methods side by side — fixed-dollar-risk method (using stop distance) and ATR method (2x ATR stop) — applied to a $100,000 reference account at 1% max risk per trade; Kelly Criterion shown; recommended shares and dollar amount
- Trade plan: entry strategy (all-at-once / scaled / wait for pullback to $X), stop-loss level with basis (technical level / ATR / prior low), two target levels with scale-out percentage, risk-reward ratio, expected holding period
- Stress-test matrix: at least 4 scenarios (core commodity/KPI -20%, currency shock, multi-factor simultaneous adverse, black-swan) showing EPS impact, target-price impact, and portfolio impact

### Module 七A: Balance sheet health (资产负债表深度分析)

Structural solvency check to detect hidden financial fragility.

- Leverage and coverage: net debt / EBITDA (vs industry median), EBITDA / interest coverage, debt-to-assets ratio, current ratio, quick ratio — all with industry benchmarks and traffic-light signal
- Debt maturity schedule: near-term (current year), medium-term (next 2 years), long-term (3+ years) — dollar amounts, percentage of total debt, refinancing risk rating
- Credit ratings: agency, current rating, outlook, most recent change with date
- Foreign-currency exposure: overseas revenue share, major currency exposures, estimated net-income impact per 10% currency move

### Module 七B: Cross-asset correlations and factor exposure (跨资产相关性与因子暴露)

Positions the stock within a portfolio context — what risk factors does owning it add or reduce?

- 60-day rolling correlation matrix: benchmark index (CSI 300 or S&P 500), 2 key commodities (e.g., gold, copper, lithium), DXY, 10-year Treasury yield — each with a directional interpretation
- Style factor exposure: Value / Growth / Momentum / Quality / Size / Volatility — each rated High/Medium/Low with the underlying data
- Portfolio role classification: Alpha source / Beta exposure / Cyclical hedge / Inflation protection / Safe haven — with specific reasoning
- Best-pairing / hedging suggestion based on the correlation findings

### Module 八: Bubble risk (泡沫与极端风险检测)

Both stock-specific and market-level bubble indicators.

- Stock-level valuation bubble signals: Forward P/E, P/S TTM, EV/FCF — each vs its own historical median, with deviation percentage and traffic-light signal
- Market-level bubble indicators: VIX level and interpretation, market-level Put/Call Ratio, margin debt trend, IPO/SPAC heat
- Tail-risk assessment: tail-risk probability (Low/Medium/High), specific black-swan scenarios unique to this stock

### Module 九: Sentiment momentum (舆情与市场情绪动量)

Retail sentiment signals and price-sentiment divergences that institutional reports miss.

- Platform sentiment thermometer: Xueqiu/Guba (China), Reddit (WSB/stocks), X/Twitter, prediction markets — each with heat level, sentiment direction, and key discussion topics
- Quantitative sentiment metrics: social-media mentions (7-day), positive-to-negative ratio, sector-level discussion rank, individual-stock discussion rank within sector
- Volume and order-flow analysis: 5-day average volume vs 20-day average (volume ratio), daily turnover in dollar terms, large-order net buy/sell direction, Dragon-Tiger-Board appearances if any
- Sentiment-price divergence signal: alignment or divergence between sentiment and price; retail vs institutional divergence level (low/high); contrarian signal trigger status
- Composite sentiment verdict for the sector, the individual stock, and the specific impact on the current rating

---

## Framework integration

Each module draws on one or more of these investment frameworks:

- **Benjamin Graham** — safety margin, Graham Number (Modules 三, 八). Intrinsic value = mathematical floor derived from earnings and book value. Buy only when price is materially below intrinsic value.
- **Warren Buffett** — moat analysis, 5-dimension competitive durability rating (Module 四). A wide moat protects returns on capital for decades; management quality (二A) determines capital allocation.
- **William O'Neil** — CAN SLIM 7-dimension scorecard, Stage Analysis, Distribution Days (Modules 六, 〇). High relative-strength names in Stage 2 with accelerating earnings are the hunting ground.
- **Mark Minervini** — Stage Analysis, Volatility Contraction Pattern (VCP) setup quality (Module 六). Timing entries at low-risk pivots reduces drawdown without reducing upside.
- **Stanley Druckenmiller** — macro regime first (Module 〇), concentration when conviction is high (Module 七). Most return comes from a few big positions; don't let diversification dilute alpha.
- **Howard Marks** — cycle positioning across 4 sub-cycles (debt, sentiment, capex, industry) in Modules 〇 and 三. At the peak of the cycle, defense; at the trough, offense.
- **Post-Earnings Announcement Drift (PEAD)** — earnings momentum via beat/miss history and estimate revisions (Module 二B). Markets systematically under-react to earnings surprises.
- **Distribution Days** — O'Neil's market-top detection mechanism (Module 〇). Cluster of high-volume down days in a major index signals institutional distribution.

---

## Cross-framework validation

The final report includes a 6-framework consensus check run after all 13 modules are complete. The table exposes whether the frameworks agree or diverge — and forces an explicit stance where they disagree.

| Framework | Conclusion | Agrees with rating? |
|---|---|---|
| Graham | Undervalued / Fair / Overvalued | Yes / No / Partial |
| Buffett | Wide moat / Narrow moat / No moat | Yes / No / Partial |
| Marks cycle | Offense / Neutral / Defense | Yes / No / Partial |
| Technical (Stage + Dow) | Stage 2 up / Sideways / Stage 4 down | Yes / No / Partial |
| Management | Excellent / Adequate / Concerning | Yes / No / Partial |
| Sentiment | Supportive / Neutral / Contrarian-against | Yes / No / Partial |
| **Consensus** | **X/6 agreement — High / Medium / Low** | |

A consensus of 5-6/6 is high conviction. 3-4/6 is mixed and warrants a moderate position. Below 3/6, the bull case relies on a minority view and position size should be reduced accordingly. These scores feed directly into Module 十's Bull/Bear debate as opening context.
