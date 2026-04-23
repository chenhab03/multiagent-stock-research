---
description: 一键全面个股深度研究 — 整合 trading-ideas + Financial Services Plugins + Trading Skills
argument-hint: "[TICKER]"
---

# 🔬 全面个股深度研究

你是一位顶级买方投研分析师（15年 Goldman Sachs 从业经验）。收到一个股票代码后，按以下 **13 个模块** 依次执行完整分析。所有输出使用中文（金融术语保留英文缩写）。

---

## 执行流程

### 输出路径（智能 fallback，v1.1.1）

本命令写报告时，`{RESEARCH_OUTPUT_DIR}` 占位符按以下优先级解析（找到第一个存在的目录就用）：

1. `$RESEARCH_OUTPUT_DIR` 环境变量（若已设置且非空）
2. `~/Dropbox/project/Documents/投研报告/`（中文 Dropbox 约定）
3. `~/Dropbox/project/投研报告/`
4. `~/Dropbox/equity-research/`（英文 Dropbox 约定）
5. 最终 fallback: `~/equity-research/`（不存在则自动创建）

**Python 代码块里先用这个 helper 解析**（任何写文件或调用 Glob 前执行一次）：
```python
import os
def resolve_output_dir():
    env = os.environ.get("RESEARCH_OUTPUT_DIR", "").strip()
    if env: return os.path.expanduser(env)
    home = os.path.expanduser("~")
    for p in [f"{home}/Dropbox/project/Documents/投研报告/",
              f"{home}/Dropbox/project/投研报告/",
              f"{home}/Dropbox/equity-research/"]:
        if os.path.isdir(p): return p
    default = f"{home}/equity-research/"
    os.makedirs(default, exist_ok=True)
    return default

OUTPUT_DIR = resolve_output_dir()   # 之后所有 {RESEARCH_OUTPUT_DIR} 等价于 OUTPUT_DIR
```

**使用 Glob 工具时**（如 Module 10 Step 0），按顺序尝试上面 5 个路径，找到有历史报告的第一个就用：
```
Glob({RESEARCH_OUTPUT_DIR}/*{TICKER}*研报*.html)
→ 实际相当于对 resolve_output_dir() 返回的路径跑 glob
```

### 🌐 语言设定 (v1.0.4)

**默认输出语言：简体中文**（金融术语保留英文缩写如 P/E、EBITDA、DCF、EPS）。

**如果 `$ARGUMENTS` 包含 `--lang en`（强制 ENGLISH_MODE=true）**：**整个报告全部英文**，无任何中文残留。

#### ENGLISH_MODE 下的强制翻译清单（不可漏项）：

**14 维度评分卡 dimension 名称强制英译**：
| 中文 | English |
|---|---|
| 大盘环境 | Macro Environment |
| 基本面质量 | Fundamentals Quality |
| 管理层质量 | Management Quality |
| 盈利预期动量 | Earnings Estimate Momentum |
| 估值吸引力 | Valuation Attractiveness |
| 增长前景 | Growth Outlook |
| 竞争优势 | Competitive Advantage (Moat) |
| 技术面 | Technicals |
| 催化剂密度 | Catalyst Density |
| 机构/期权信号 | Institutional / Options Signal |
| 周期位置 | Cycle Position |
| 资产负债表健康度 | Balance Sheet Health |
| 舆情/情绪动量 | Sentiment Momentum |
| 风险回报比 | Risk/Reward |
| 综合评分 | Composite Score |
| 维度加权平均 | 14-dimension weighted average |
| 辩论调整 | Debate Adjustment |
| HOLD_passive 惩罚 | HOLD_passive Penalty |
| 综合评分（辩论调整后） | Composite Score (Post-Debate) |
| 评级 | Rating |
| 确信度 | Confidence |
| 目标价 | Target Price |
| 时间框架 | Time Horizon |
| 上行空间 | Upside |
| 建议仓位 | Suggested Position Size |
| 止损位 | Stop-Loss |
| 风险收益比 | Risk/Reward Ratio |
| 仓位调整规则 | Position Adjustment Rule |

**模块标题强制英译**：
| 中文 | English |
|---|---|
| 大盘环境评估 | Macro Environment |
| 执行摘要 | Executive Summary |
| 基本面分析 | Fundamental Analysis |
| 管理层质量评估 | Management Quality |
| 盈利模型与预期追踪 | Earnings Model & Estimate Tracking |
| 估值分析 | Valuation |
| 行业与竞争格局 | Industry & Competitive Landscape |
| 催化剂与投资论题 | Catalysts & Investment Thesis |
| 技术面与市场信号 | Technicals & Market Signals |
| 风险管理与仓位建议 | Risk Management & Sizing |
| 资产负债表深度分析 | Balance Sheet Deep-Dive |
| 跨资产相关性与因子暴露 | Cross-Asset Correlations & Factor Exposure |
| 泡沫与极端风险检测 | Bubble & Tail Risk Detection |
| 舆情与市场情绪动量 | Sentiment & Market Momentum |
| 多空辩论与终审裁决 | Bull vs Bear Debate & Final Verdict |

**辩论 subagent 派发规则（ENGLISH_MODE）**：
- 派发 Bull/Bear/Judge subagent 时，**必须在其 prompt 最顶端加入**：
  > ```
  > ⚠️ LANGUAGE REQUIREMENT: Respond in English only. All thesis claims, data citations, rebuttals, closing arguments, verdict reasoning, and JSON field values must be in English. Financial term abbreviations (P/E, EBITDA, DCF) stay as-is. Do NOT mix in Chinese text.
  > ```
- Bull/Bear/Judge 的 JSON 输出（thesis claim、data、rebuttal text、winner_reasons、unresolved_risks 等所有字符串字段）全部英文。
- Judge 的 "核心分歧矩阵" bull_view / bear_view / judge_reasoning 全部英文。

**模块十渲染 markdown 的 section 标题强制英译**：
| 中文 | English |
|---|---|
| 历史判断对账表 | Prior Call Review |
| 关键反思 | Key Reflections |
| 🥊 辩论 Transcript 精华 | 🥊 Debate Transcript Summary |
| 🐂 多头 Top 3 | 🐂 Bull Top 3 |
| 🐻 空头 Top 3 | 🐻 Bear Top 3 |
| 反驳结果 | Rebuttal Outcomes |
| 终陈 | Closing Statements |
| 🏆 Judge 终审 | 🏆 Judge Verdict |
| 核心分歧表 | Key Disagreements |
| ⚠️ 未被反驳的风险 | ⚠️ Unresolved Risks |
| 对评分卡的影响 | Scorecard Adjustments |

**Investment Thesis / Bottom Line / 建议操作 table rows 全部英文**。

**Disclaimer 英文**：
> "For research and educational use only. Not investment advice. Past performance does not guarantee future results. Consult a licensed professional before making any investment decisions."

金融术语保留原样：P/E, EBITDA, DCF, EPS, FCF, ROE, ROIC, WACC, CAGR, YoY, QoQ, LTM, Beat/Miss, BUY/SELL/HOLD_active/HOLD_passive, bull/bear thesis 等。
公司名称、ticker 保留大写原样。

### 输入解析
- 从 `$ARGUMENTS` 提取股票代码（如 AAPL、NVDA、DUOL）
- 支持逗号分隔的多股票批量模式（如 `AAPL,NVDA,TSLA` 或 `AAPL, NVDA, TSLA`）
- 如果未提供，询问用户要分析哪只股票
- 可选标志：
  - `--html` — 分析完成后自动生成 HTML 研报
  - `--silent` — 静默模式：不在控制台输出 Markdown 分析内容，仅生成 HTML 文件到目标目录
  - `--html --silent` — 批量静默模式（推荐搭配多股票使用）
  - `--quick` — 跳过模块十辩论（快速筛查模式），成本降回原始 ~80k tokens
  - `--lang en` — 输出英文研报（默认中文）；金融术语保留缩写（DCF/P/E/EBITDA 等）

### 批量模式执行逻辑
当输入包含多个股票代码时（逗号分隔）：
1. 解析出所有股票代码列表和标志（`--html`、`--silent`、`--quick`）
2. **逐一执行**每只股票的完整分析流程（数据采集 → 13模块分析 → 评分卡）
3. 如含 `--html`：每完成一只股票的分析，立即生成对应 HTML 研报
4. 如含 `--silent`：
   - **不输出** Markdown 分析内容到控制台（跳过所有 `print`/文本输出）
   - 仅在每只股票完成时输出一行进度：`✅ [N/总数] [TICKER] 研报已生成 → [文件路径]`
   - 全部完成后输出汇总表：

```
📊 批量分析完成
| # | 股票 | 评级 | 目标价 | 综合评分 | 文件 |
|---|------|------|--------|---------|------|
| 1 | AAPL | BUY  | $xxx   | xx/100  | ✅   |
| 2 | NVDA | HOLD | $xxx   | xx/100  | ✅   |
...
```

5. 如不含 `--silent`（仅 `--html`）：正常输出每只股票的完整 Markdown 分析 + 生成 HTML

### 第零步：结构化数据采集（最高优先级，必须先执行）

**在任何分析开始前，根据股票市场类型调用对应数据源，获取价格、基本面、分析师数据。**

**数据来源优先级（三层）：**
1. **FSP Skills**（最优先，仅美股/港股尝试）：`equity-research:earnings-analysis`、`financial-analysis:dcf-model`、`financial-analysis:comps-analysis` 等 — 官方专业级分析框架，有内置数据访问能力
2. **结构化 API**（补充）：yfinance / akshare / TuShare / Finnhub — 补充 FSP 不覆盖的数据（A股全部、内部人交易、资金流向、港股分析师预测等）
3. **WebSearch**（最后兜底）：仅用于前两层无法覆盖的定性信息（新闻/舆情/竞争格局描述等）

> **执行顺序**：美股/港股先调用 FSP Skills → 再运行 API 脚本补充缺口 → 最后按需 WebSearch。A股跳过 FSP，直接从第2层开始。

#### 市场识别规则

| 输入格式 | 市场 | 数据源 |
|---------|------|--------|
| 6位纯数字，如 `600519`、`002415` | A股 | TuShare（主） + akshare（补充） |
| 数字+`.SS`/`.SZ`，如 `600519.SS` | A股 | TuShare（主） + akshare（补充，去掉后缀） |
| 数字+`.HK`，如 `0700.HK`、`9988.HK` | 港股 | yfinance + akshare + TuShare（北向资金） |
| 纯字母，如 `NVDA`、`AAPL` | 美股 | yfinance（主） + Finnhub（补充） |

#### API 密钥（通过环境变量配置）

```python
import os
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
FINNHUB_TOKEN = os.environ.get("FINNHUB_TOKEN", "")
if not TUSHARE_TOKEN:
    print("⚠️  Set TUSHARE_TOKEN env var for A-share analyst data (https://tushare.pro)")
if not FINNHUB_TOKEN:
    print("⚠️  Set FINNHUB_TOKEN env var for US insider/institutional data (https://finnhub.io)")
```

---


> ⚠️ **A 股主数据源**：先跑 **TuShare** 拉全 PE_TTM/PB/PS_TTM、分析师一致预期、券商评级、主力资金流、机构持仓。TuShare 失败或缺字段时再用 akshare 补。**不要反过来。**

#### A股 → TuShare（**主数据源**：实时行情 + 分析师预测 + 券商评级 + 资金流 + 机构持仓）

```python
import os
import tushare as ts

TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# ts_code 格式：000001.SZ 或 600519.SH
ts_code = f"{ticker}.{'SH' if ticker.startswith('6') else 'SZ'}"
today   = datetime.today().strftime('%Y%m%d')

# ── 6. TuShare：每日行情基本面（PE/PB/市净率/换手率/市值）──
# 官方指标，更精准；彻底替代 akshare spot 中可能不准确的字段
try:
    daily = pro.daily_basic(ts_code=ts_code, trade_date=today,
                            fields='ts_code,trade_date,close,pe,pe_ttm,pb,ps,ps_ttm,'
                                   'dv_ratio,total_mv,circ_mv,turnover_rate,turnover_rate_f,free_share')
    if daily.empty:  # 非交易日，取最新
        daily = pro.daily_basic(ts_code=ts_code, start_date='20240101', end_date=today,
                                fields='ts_code,trade_date,close,pe,pe_ttm,pb,ps,ps_ttm,'
                                       'dv_ratio,total_mv,circ_mv,turnover_rate,turnover_rate_f,free_share')
        daily = daily.head(1)
    row_ts = daily.iloc[0]
    pe_ttm_ts     = row_ts.get('pe_ttm')   # TTM 市盈率（优先级 > akshare 动态PE）
    pb_ts         = row_ts.get('pb')       # 市净率
    ps_ttm_ts     = row_ts.get('ps_ttm')  # TTM 市销率
    total_mv_ts   = row_ts.get('total_mv')   # 总市值（万元）
    circ_mv_ts    = row_ts.get('circ_mv')    # 流通市值（万元）
    turnover_ts   = row_ts.get('turnover_rate')
    dv_ratio_ts   = row_ts.get('dv_ratio')  # 股息率
except Exception as e:
    print(f"TuShare daily_basic 失败: {e}")

# ── 7. TuShare：分析师盈利预测（一致预期 EPS/营收）──
try:
    forecast_df = pro.forecast(ts_code=ts_code, period='', ann_date='')
    # 包含：net_profit_min/max/avg（预测净利润）、sales_forcast（营收预测）、eps
    if not forecast_df.empty:
        latest_fc = forecast_df.head(5)
        print("\n=== 分析师盈利预测（最新5条）===")
        print(latest_fc[['ann_date','period','type','net_profit_min','net_profit_max','eps','sales_forecast']].to_string())
except Exception as e:
    print(f"TuShare forecast 失败: {e}")

# ── 8. TuShare：券商评级汇总 ──
try:
    rating_df = pro.rating(ts_code=ts_code, start_date=(datetime.today() - timedelta(days=180)).strftime('%Y%m%d'),
                           end_date=today)
    # 包含：brokername（券商）、rating（评级：买入/增持/中性/减持）、target_price（目标价）
    if not rating_df.empty:
        rating_summary = {
            "count": len(rating_df),
            "target_mean": rating_df['target_price'].dropna().astype(float).mean(),
            "target_high": rating_df['target_price'].dropna().astype(float).max(),
            "target_low":  rating_df['target_price'].dropna().astype(float).min(),
            "ratings":     rating_df['rating'].value_counts().to_dict(),
        }
        print("\n=== 券商评级汇总（近180天）===")
        print(rating_summary)
        print(rating_df[['ann_date','brokername','rating','target_price']].head(10).to_string())
    else:
        rating_summary = {}
except Exception as e:
    rating_summary = {}
    print(f"TuShare rating 失败: {e}")

# ── 9. TuShare：个股资金流向（主力净买入）──
try:
    mf = pro.moneyflow(ts_code=ts_code, start_date=(datetime.today() - timedelta(days=30)).strftime('%Y%m%d'),
                       end_date=today)
    # 包含：buy_lg_amount/sell_lg_amount（大单）、buy_md_amount/sell_md_amount（中单）
    if not mf.empty:
        mf['net_main'] = mf['buy_lg_amount'] - mf['sell_lg_amount']
        mf_30d_net = mf['net_main'].sum()  # 30日主力净买入（万元）
        mf_5d_net  = mf['net_main'].head(5).sum()  # 5日净买入
        print(f"\n=== 资金流向（万元）: 30日主力净={mf_30d_net:.0f}，5日主力净={mf_5d_net:.0f} ===")
except Exception as e:
    print(f"TuShare moneyflow 失败: {e}")

# ── 10. TuShare：机构持仓（季报）──
try:
    inst = pro.top_inst(ts_code=ts_code, trade_date='')
    if not inst.empty:
        print("\n=== 主要机构持仓 ===")
        print(inst[['quarter','inst_name','hold_ratio']].head(10).to_string())
except Exception as e:
    print(f"TuShare top_inst 失败: {e}")
```

**注意：FSP Skills 不支持 A 股，第一步直接跳过，所有基本面数据来自上方 akshare + TuShare 脚本。**

---

#### A股 → akshare（补充数据：基本面详表 / 年度财务摘要 / 个股信息）

```python
import akshare as ak
from datetime import datetime, timedelta
import json

ticker = "TICKER_HERE"  # 6位纯数字，如 600519

# ── 1. 实时行情（含 PE、PB、市值、换手率）──
spot = ak.stock_zh_a_spot_em()
row = spot[spot['代码'] == ticker].iloc[0]
price        = row['最新价']
pe_dynamic   = row['市盈率-动态']
pb           = row['市净率']
market_cap   = row['总市值'] / 1e8        # 亿元
float_cap    = row['流通市值'] / 1e8
turnover_rate = row['换手率']             # %
change_pct   = row['涨跌幅']             # %
chg_60d      = row['60日涨跌幅']
chg_ytd      = row['年初至今涨跌幅']

# ── 2. 52周价格区间 + 均线 ──
end_d   = datetime.today().strftime('%Y%m%d')
start_d = (datetime.today() - timedelta(days=365)).strftime('%Y%m%d')
hist = ak.stock_zh_a_hist(symbol=ticker, period="daily",
                           start_date=start_d, end_date=end_d, adjust="qfq")
high_52w     = hist['最高'].max()
low_52w      = hist['最低'].min()
latest_close = hist['收盘'].iloc[-1]
latest_date  = str(hist['日期'].iloc[-1])
ma50         = hist['收盘'].tail(50).mean()
ma200        = hist['收盘'].tail(200).mean() if len(hist) >= 200 else None
pct_from_high = (latest_close - high_52w) / high_52w * 100  # 距高点跌幅

# ── 3. 年度财务摘要（近5年）──
# 含：净利润/营收/EPS/ROE/销售毛利率/资产负债率/每股经营现金流
fin = ak.stock_financial_abstract_ths(symbol=ticker, indicator='按年度')
fin_recent = fin.tail(5)  # 最近5年

# ── 4. 详细利润表（最新年/季报）──
try:
    prefix = 'sh' if ticker.startswith('6') else 'sz'
    profit_df = ak.stock_financial_report_sina(stock=f'{prefix}{ticker}', symbol='利润表')
    latest_profit = profit_df.iloc[0]   # 最新期
    revenue      = latest_profit.get('营业总收入')
    net_profit   = latest_profit.get('净利润')
    gross_margin_val = latest_profit.get('营业总收入', 0) - latest_profit.get('营业成本', 0)
    eps_basic    = latest_profit.get('基本每股收益')
except Exception as e:
    print(f"利润表获取失败: {e}")

# ── 5. 个股基本信息（行业、总股本）──
basic = ak.stock_individual_info_em(symbol=ticker)
info_dict = dict(zip(basic['item'], basic['value']))
industry   = info_dict.get('行业', '')
total_shares = info_dict.get('总股本', '')
company_name = info_dict.get('股票简称', ticker)

# ── 输出摘要 ──
print(json.dumps({
    "ticker": ticker, "name": company_name, "market": "CN",
    "price": price, "date": latest_date,
    "change_pct": change_pct, "chg_60d": chg_60d, "chg_ytd": chg_ytd,
    "high_52w": high_52w, "low_52w": low_52w, "pct_from_high": round(pct_from_high, 1),
    "ma50": round(ma50, 2), "ma200": round(ma200, 2) if ma200 else None,
    "pe_dynamic": pe_dynamic, "pb": pb,
    "market_cap_bn_cny": round(market_cap, 1),
    "float_cap_bn_cny": round(float_cap, 1),
    "turnover_rate": turnover_rate,
    "industry": industry, "total_shares": total_shares,
}, ensure_ascii=False, indent=2))
print("\n=== 近5年财务摘要 ===")
print(fin_recent[['报告期','营业总收入','净利润','基本每股收益','销售毛利率','净资产收益率','资产负债率']].to_string())
```

#### 港股 → yfinance（基本面）+ akshare（分析师预测）

```python
import yfinance as yf
import akshare as ak
import json

ticker_yf = "TICKER_HERE"   # 带 .HK，如 0700.HK
ticker_ak = ticker_yf.split('.')[0].zfill(5)  # akshare 用5位代码，如 00700

# ── 1. yfinance：价格 + 完整基本面 ──
stock = yf.Ticker(ticker_yf)
info  = stock.info
hist  = stock.history(period="1y")

price        = hist['Close'].iloc[-1]
high_52w     = hist['High'].max()
low_52w      = hist['Low'].min()
pct_from_high = (price - high_52w) / high_52w * 100
ma50         = hist['Close'].tail(50).mean()
ma200        = hist['Close'].tail(200).mean() if len(hist) >= 200 else None

# 基本面字段
fundamental = {k: info.get(k) for k in [
    'shortName', 'sector', 'industry',
    'trailingPE', 'forwardPE', 'priceToBook', 'enterpriseToEbitda', 'enterpriseToRevenue',
    'trailingEps', 'forwardEps', 'earningsGrowth', 'revenueGrowth',
    'grossMargins', 'operatingMargins', 'profitMargins',
    'totalDebt', 'totalCash', 'freeCashflow', 'operatingCashflow',
    'debtToEquity', 'returnOnEquity', 'returnOnAssets',
    'marketCap', 'enterpriseValue',
    'heldPercentInstitutions', 'heldPercentInsiders', 'beta',
] if info.get(k) is not None}

# ── 2. akshare：分析师评级 + 目标价 ──
try:
    forecasts = ak.stock_hk_profit_forecast_et(symbol=ticker_ak)
    # 包含：证券商、评级、目标价、每股盈利预测
    analyst_summary = {
        "count": len(forecasts),
        "targets": forecasts['目标价'].dropna().tolist(),
        "target_mean": forecasts['目标价'].dropna().mean(),
        "ratings": forecasts['评级'].value_counts().to_dict(),
    }
except Exception as e:
    analyst_summary = {"error": str(e)}

print(json.dumps({
    "ticker": ticker_yf, "market": "HK",
    "price": round(price, 3), "high_52w": round(high_52w, 3), "low_52w": round(low_52w, 3),
    "pct_from_high": round(pct_from_high, 1),
    "ma50": round(ma50, 3), "ma200": round(ma200, 3) if ma200 else None,
    **fundamental,
    "analyst": analyst_summary,
}, ensure_ascii=False, indent=2))
```

**FSP Skills 可尝试调用（大型港股如腾讯/阿里可能有数据），失败时直接用上方数据，不降级 WebSearch。**

---

#### 港股 → TuShare（北向资金 + 港股通持仓）

```python
import os
import tushare as ts
from datetime import datetime, timedelta

TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# ts_code 格式：00700.HK（5位股票代码 + .HK）
ticker_hk = "TICKER_HERE"  # 如 0700.HK
ts_code = ticker_hk.split('.')[0].zfill(5) + '.HK'  # → 00700.HK
today   = datetime.today().strftime('%Y%m%d')
d30_ago = (datetime.today() - timedelta(days=30)).strftime('%Y%m%d')

# ── 1. TuShare：港股通每日持股（北向资金持仓量）──
# 仅适用于沪港通/深港通标的（腾讯、阿里、美团等主要港股均在列）
try:
    hk_hold = pro.hk_hold(code=ts_code, start_date=d30_ago, end_date=today)
    if not hk_hold.empty:
        latest_hold  = hk_hold.iloc[0]
        hold_vol     = latest_hold.get('vol')          # 持股量（股）
        hold_ratio   = latest_hold.get('ratio')        # 占流通股比例（%）
        hold_date    = latest_hold.get('trade_date')
        # 趋势：对比30天前
        hold_30d_ago = hk_hold.iloc[-1].get('vol') if len(hk_hold) > 1 else None
        hold_chg_30d = ((hold_vol - hold_30d_ago) / hold_30d_ago * 100) if hold_30d_ago else None
        print(f"\n=== 港股通持仓（{hold_date}）===")
        print(f"持股量: {hold_vol:,.0f} 股 | 占流通股: {hold_ratio:.2f}%")
        if hold_chg_30d is not None:
            direction = "↑增持" if hold_chg_30d > 0 else "↓减持"
            print(f"30日变动: {hold_chg_30d:+.1f}% ({direction})")
    else:
        print("港股通持仓: 该股不在沪深港通标的范围内")
except Exception as e:
    print(f"TuShare hk_hold 失败: {e}")

# ── 2. TuShare：港股通十大成交股（确认个股是否活跃）──
try:
    # market_type: 1=沪港通(北向), 2=深港通(北向)；用两个合并更全
    top10_sh = pro.hsgt_top10(trade_date=today, market_type='1')
    top10_sz = pro.hsgt_top10(trade_date=today, market_type='2')
    top10_all = []
    for df in [top10_sh, top10_sz]:
        if not df.empty:
            match = df[df['ts_code'] == ts_code]
            if not match.empty:
                top10_all.append(match.iloc[0])
    if top10_all:
        row_t10 = top10_all[0]
        print(f"\n=== 港股通十大成交 ({today}) ===")
        print(f"买入金额: {row_t10.get('buy_amount', 0):.1f}亿 | 卖出金额: {row_t10.get('sell_amount', 0):.1f}亿 | 净买入: {row_t10.get('net_amount', 0):.1f}亿")
    else:
        print(f"今日未上榜港股通十大成交（{today}）")
except Exception as e:
    print(f"TuShare hsgt_top10 失败: {e}")

# ── 3. TuShare：沪深港通资金流向汇总（大盘北向整体方向，辅助判断港股情绪）──
try:
    hsgt_flow = pro.moneyflow_hsgt(trade_date=today)
    if hsgt_flow.empty:  # 非交易日取最新
        hsgt_flow = pro.moneyflow_hsgt(start_date=d30_ago, end_date=today)
        hsgt_flow = hsgt_flow.head(5)
    print(f"\n=== 北向资金流向（近5日）===")
    for _, r in hsgt_flow.iterrows():
        net = r.get('north_money', 0)
        print(f"  {r.get('trade_date')}: 北向净买入 {net:.1f}亿（{'流入↑' if net > 0 else '流出↓'}）")
except Exception as e:
    print(f"TuShare moneyflow_hsgt 失败: {e}")
```

**注意：TuShare 港股通数据仅覆盖沪深港通标的（约300-500只港股），小市值港股无数据时跳过此节。**

---

#### 美股 → yfinance（完整数据）

```python
import yfinance as yf
import json

ticker = "TICKER_HERE"
stock = yf.Ticker(ticker)
info  = stock.info
hist  = stock.history(period="1y")

price        = hist['Close'].iloc[-1]
high_52w     = hist['High'].max()
low_52w      = hist['Low'].min()
pct_from_high = (price - high_52w) / high_52w * 100
ma50         = hist['Close'].tail(50).mean()
ma200        = hist['Close'].tail(200).mean() if len(hist) >= 200 else None

print(json.dumps({
    "ticker": ticker, "market": "US",
    "price": round(price, 2), "high_52w": round(high_52w, 2), "low_52w": round(low_52w, 2),
    "pct_from_high": round(pct_from_high, 1),
    "ma50": round(ma50, 2), "ma200": round(ma200, 2) if ma200 else None,
    **{k: info.get(k) for k in [
        'shortName', 'sector', 'industry',
        'trailingPE', 'forwardPE', 'priceToBook', 'enterpriseToEbitda', 'enterpriseToRevenue',
        'trailingEps', 'forwardEps', 'earningsGrowth', 'revenueGrowth',
        'grossMargins', 'operatingMargins', 'profitMargins',
        'totalDebt', 'totalCash', 'freeCashflow', 'returnOnEquity',
        'marketCap', 'enterpriseValue', 'beta',
        'targetMeanPrice', 'recommendationKey', 'numberOfAnalystOpinions',
        'heldPercentInsiders', 'heldPercentInstitutions',
    ] if info.get(k) is not None},
}, ensure_ascii=False, indent=2))
```

#### 美股补充 → Finnhub（内部人交易 + 分析师评级趋势 + 历史 EPS Beat/Miss）

```python
import os
import finnhub

FINNHUB_TOKEN = os.environ.get("FINNHUB_TOKEN", "")
fc = finnhub.Client(api_key=FINNHUB_TOKEN)

# ── 补充1. 分析师评级趋势（近12个月，每月 Buy/Hold/Sell 家数）──
try:
    rec = fc.recommendation_trends(ticker)
    # 格式: [{period, strongBuy, buy, hold, sell, strongSell}, ...]
    if rec:
        latest_rec = rec[0]  # 最新月份
        total_analysts = sum([
            latest_rec.get('strongBuy', 0), latest_rec.get('buy', 0),
            latest_rec.get('hold', 0), latest_rec.get('sell', 0), latest_rec.get('strongSell', 0)
        ])
        buy_count  = latest_rec.get('strongBuy', 0) + latest_rec.get('buy', 0)
        sell_count = latest_rec.get('sell', 0) + latest_rec.get('strongSell', 0)
        hold_count = latest_rec.get('hold', 0)
        print(f"\n=== Finnhub 分析师评级 ({latest_rec['period']}) ===")
        print(f"买入: {buy_count}, 持有: {hold_count}, 卖出: {sell_count}, 总计: {total_analysts}")
        # 趋势（对比上月）
        if len(rec) > 1:
            prev = rec[1]
            prev_buy = prev.get('strongBuy', 0) + prev.get('buy', 0)
            print(f"vs 上月买入: {prev_buy} → {'↑上调' if buy_count > prev_buy else '↓下调' if buy_count < prev_buy else '→持平'}")
except Exception as e:
    print(f"Finnhub recommendation_trends 失败: {e}")

# ── 补充2. 历史 EPS Beat/Miss（近8季度）──
try:
    surprises = fc.company_earnings(ticker, limit=8)
    # 格式: [{period, actual, estimate, surprise, surprisePercent}, ...]
    if surprises:
        print("\n=== 历史 EPS Beat/Miss（近8季度）===")
        beat_count = sum(1 for s in surprises if s.get('surprise', 0) > 0)
        for s in surprises:
            direction = "✅ Beat" if s.get('surprise', 0) > 0 else "❌ Miss"
            print(f"  {s.get('period')}: 预期={s.get('estimate')}, 实际={s.get('actual')}, "
                  f"偏差={s.get('surprisePercent', 0):.1f}%  {direction}")
        print(f"  Beat Rate: {beat_count}/8 = {beat_count/8*100:.0f}%")
except Exception as e:
    print(f"Finnhub company_earnings 失败: {e}")

# ── 补充3. 内部人交易（近90天）──
try:
    from datetime import timedelta
    insider = fc.stock_insider_transactions(
        ticker,
        (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d'),
        datetime.today().strftime('%Y-%m-%d')
    )
    if insider and insider.get('data'):
        txns = insider['data']
        buys  = [t for t in txns if t.get('transactionCode') in ('P', 'A')]  # Purchase/Award
        sells = [t for t in txns if t.get('transactionCode') == 'S']          # Sale
        net_shares = sum(t.get('share', 0) for t in buys) - sum(t.get('share', 0) for t in sells)
        print(f"\n=== 内部人交易（近90天）===")
        print(f"买入交易: {len(buys)}笔, 卖出交易: {len(sells)}笔, 净股数: {net_shares:+,}")
        for t in txns[:5]:  # 最近5条
            print(f"  {t.get('transactionDate')} | {t.get('name')} ({t.get('officerTitle', 'N/A')}) "
                  f"| {t.get('transactionCode')} {t.get('share', 0):,}股 @ ${t.get('price', 0):.2f}")
except Exception as e:
    print(f"Finnhub insider_transactions 失败: {e}")

# ── 补充4. 近期重要新闻（最新5条）──
try:
    from datetime import timedelta
    news = fc.company_news(
        ticker,
        _from=(datetime.today() - timedelta(days=14)).strftime('%Y-%m-%d'),
        to=datetime.today().strftime('%Y-%m-%d')
    )
    if news:
        print(f"\n=== 最新新闻（{len(news)}条，展示前5）===")
        for n in news[:5]:
            import datetime as dt
            ts_time = dt.datetime.fromtimestamp(n.get('datetime', 0)).strftime('%Y-%m-%d')
            print(f"  [{ts_time}] {n.get('headline')}  ({n.get('source')})")
except Exception as e:
    print(f"Finnhub company_news 失败: {e}")
```

**将以上脚本输出的数据作为全局上下文贯穿所有后续模块。若脚本调用失败，在报告中标注后用 WebSearch 补充，但 WebSearch 仅作最后手段。**

---

### 第一步：显式调用 FSP Skills（仅适用于美股）

> ⚠️ **市场限制：FSP Skills 主要覆盖美股。A股直接跳过此步骤；港股可尝试调用，失败时直接用第零步数据。**

**在生成报告前，必须先通过 `Skill` 工具显式调用以下官方 FSP Skills，获取结构化分析输入。FSP Skill 的优先级高于 WebSearch。**

#### FSP Skill 调用清单（并行触发，等待所有结果）

| Skill 名称 | 调用目的 | 对应报告模块 | 美股 | 港股 | A股 |
|-----------|---------|------------|------|------|-----|
| `equity-research:earnings-analysis` | 财报 Beat/Miss、EPS/营收 vs 预期、季度历史 | 模块二、二B | ✅ | ⚠️尝试 | ❌跳过 |
| `financial-analysis:comps-analysis` | 可比公司估值倍数（EV/Rev、EV/EBITDA、P/E） | 模块三 | ✅ | ⚠️尝试 | ❌跳过 |
| `financial-analysis:dcf-model` | DCF 三情景内在价值、WACC、反向 DCF | 模块三 | ✅ | ⚠️尝试 | ❌跳过 |
| `financial-analysis:competitive-analysis` | 竞争定位矩阵、护城河评估 | 模块四 | ✅ | ⚠️尝试 | ❌跳过 |
| `equity-research:catalysts` | 催化剂日历 | 模块五 | ✅ | ⚠️尝试 | ❌跳过 |
| `equity-research:thesis` | 投资论题（多头/空头逻辑） | 模块五 | ✅ | ⚠️尝试 | ❌跳过 |

**调用方式**（美股必须调用，港股尝试调用）：
```
Skill("equity-research:earnings-analysis", "[TICKER]")
Skill("financial-analysis:comps-analysis", "[TICKER]")
Skill("financial-analysis:dcf-model", "[TICKER]")
Skill("financial-analysis:competitive-analysis", "[TICKER]")
Skill("equity-research:catalysts", "[TICKER]")
Skill("equity-research:thesis", "[TICKER]")
```

#### DCF 和 Comps Skills 的特殊处理

`dcf-model` 和 `comps-analysis` 默认生成 Excel 文件。在 `/analyze` 上下文中：
- **必须同时输出内嵌的结构化摘要**（估值表格、三情景数值、可比倍数）供 Markdown 报告内嵌使用
- **如带 `--html` 参数**，额外将 Excel 文件保存至 `{RESEARCH_OUTPUT_DIR}`：
  - `[TICKER]-DCF-YYYYMMDD.xlsx`
  - `[TICKER]-Comps-YYYYMMDD.xlsx`
- 在报告中注明"详细模型见附件 Excel"

#### 各市场数据来源分工

| 数据模块 | 美股 | 港股 | A股 |
|---------|------|------|-----|
| 价格/技术面 | yfinance | yfinance | akshare + TuShare daily_basic |
| 估值倍数 (PE/PB/PS) | yfinance | yfinance | TuShare daily_basic（主）+ akshare spot（辅） |
| 财报 EPS/营收 | **FSP `earnings-analysis`**（主）→ Finnhub beat/miss（补） | yfinance earnings | akshare 财务摘要 + TuShare forecast |
| 分析师评级/目标价 | **FSP**（主）→ Finnhub `recommendation_trends`（补） | akshare `stock_hk_profit_forecast_et` | TuShare `rating` → WebSearch |
| 内部人交易 | Finnhub `insider_transactions` | yfinance | TuShare → WebSearch |
| DCF 模型 | **FSP `dcf-model`**（主框架）→ yfinance FCF（数据补充） | yfinance FCF 自建 | TuShare/akshare FCF 自建 |
| 可比估值 Comps | **FSP `comps-analysis`**（主框架）→ yfinance（数据补充） | yfinance | akshare/TuShare 自建 |
| 竞争格局 | **FSP `competitive-analysis`**（主）→ WebSearch（补） | WebSearch | WebSearch |
| 催化剂 | **FSP `catalysts`**（主）→ Finnhub 新闻（补） | WebSearch | WebSearch |
| 机构持仓 | yfinance `heldPercentInstitutions` | yfinance | TuShare `top_inst` |
| 北向资金/港股通 | — | TuShare `hk_hold` + `hsgt_top10` + `moneyflow_hsgt` | — |
| 资金流向 | — | — | TuShare `moneyflow` |
| 最新新闻 | Finnhub `company_news` | WebSearch | WebSearch |

#### WebSearch 仅用于以下定性数据（所有市场）

1. `"[股票名/TICKER] 下跌原因 催化剂 最新新闻 [当前年份]"` → 近期催化剂/新闻
2. `"[股票名/TICKER] 内部人 增减持 高管买卖 [当前年份]"` → 内部人交易
3. `"[股票名/TICKER] 期权流 Put/Call 隐含波动率 [当前年份]"` → 期权信号（美股）
4. `"[股票名/TICKER] 雪球 股吧 讨论 情绪 [当前年份]"` → 舆情/情绪
5. `"[大盘指数] 市场广度 宏观环境 [当前年份]"` → 大盘环境
6. `"[股票名/TICKER] 竞争对手 护城河 行业格局 [当前年份]"` → 竞争定性（A股/港股）

---

### 第二步：生成综合报告

用采集到的数据，生成以下完整报告。每个模块标注了数据来源对应的 skill/plugin。

---

# 📊 $ARGUMENTS — 全面深度研究报告

## 〇、大盘环境评估
> 来源: `macro-regime-detector` + `market-breadth-analyzer` + `market-top-detector` + `market-environment-analysis`

在分析个股前，先评估当前大盘所处环境。

### 宏观体制判断
- **当前体制**: [Risk-On 扩张 / Risk-Off 收缩 / 过渡期]
- **判断依据**: [yield curve、信用利差、RSP/SPY 集中度、equity-bond 相关性]

### 市场广度健康度
| 指标 | 数值 | 信号 |
|------|------|------|
| 标普500 >200日均线占比 | [X]% | [健康/警告/危险] |
| 新高-新低差值 | [X] | [正面/负面] |
| 涨跌线趋势 | [上升/下降/背离] | [确认/警告] |
| 广度综合评分 | [X]/100 | [具体评级] |

### 市场顶部概率
- **Distribution Days (近25个交易日)**: [X] 天
- **领涨股恶化程度**: [低/中/高]
- **防御型板块轮动**: [未出现/早期/明显]
- **顶部风险综合评分**: [X]/100 ([绿灯/黄灯/红灯])

### 全球风险偏好
- **Risk-On / Risk-Off 判断**: [X]
- [美元、VIX、信用利差、大宗商品、新兴市场的综合方向]

### 霍华德·马克斯周期定位
用《周期》框架判断该股所处行业的周期位置：

| 维度 | 当前状态 | 判断依据 |
|------|---------|---------|
| 行业周期阶段 | [早期/中期成长/过热/衰退] | [渗透率、资本开支增速、新进入者数量] |
| 市场情绪位置 | [恐慌/谨慎/乐观/狂热] | [PE/PS 当前值 vs 5年分位数: [X]%] |
| 信贷周期信号 | [宽松/收紧/拐点] | [信用利差、银行放贷标准变化] |
| 资本开支周期 | [扩张/见顶/收缩/触底] | [行业 CapEx 同比增速、产能利用率] |

**马克斯视角风险评估**: [当前周期位置意味着什么 — 是该"进攻"还是"防守"？]

**对 $ARGUMENTS 的影响**: [当前大盘环境对该股是顺风/逆风/中性，以及原因]

---

## 一、执行摘要
> 来源: `trading-ideas` + `Skill("equity-research:initiate")`

**评级**: [买入/持有/卖出] | **目标价**: $[X] ([X]% 上行/下行空间) | **时间框架**: [X]个月

[一段话总结：公司做什么、核心投资逻辑、当前机会或风险、风险收益比评价]

**确信度**: [高/中/低]

---

## 二、基本面分析
> 来源: `Skill("equity-research:earnings-analysis")` 输出 + `earnings-trade-analyzer`

### 最新财报
| 指标 | 实际值 | 一致预期 | 超预期/不及 |
|------|--------|----------|------------|
| 营收 | $[X] | $[X] | [+/-X%] |
| EPS | $[X] | $[X] | [+/-$X] |
| 毛利率 | [X]% | [X]% | [+/-Xbps] |
| 经营利润率 | [X]% | — | [趋势] |

### 关键业务指标
- [公司特有的 KPI，如 DAU、ARR、同店销售等，附带 YoY/QoQ 变化]

### 管理层指引
- [下季度/全年指引 vs 市场预期]

### 盈后动量评分 (Earnings-Trade Analyzer)
如该股近期刚发布财报，提供以下 5 因子评分：

| 因子 | 评分 | 说明 |
|------|------|------|
| Gap Size（缺口幅度） | [X]/20 | [具体%] |
| Pre-Earnings Trend（财报前趋势） | [X]/20 | [上升/下降/横盘] |
| Volume Trend（成交量趋势） | [X]/20 | [放量/缩量] |
| MA200 Position（200日均线位置） | [X]/20 | [上方/下方] |
| MA50 Position（50日均线位置） | [X]/20 | [上方/下方] |
| **综合评分** | **[X]/100** | **等级: [A/B/C/D]** |

*如该股非近期财报周期，标注"N/A — 距上次财报已超过 [X] 周"并跳过此节。*

### 盈利质量检验 (P2 改进)
| 指标 | 数值 | 信号 |
|------|------|------|
| 经营现金流/净利润 | [X]x | [>0.8 健康 / <0.8 ⚠️ 利润质量存疑] |
| 应计利润比率 (Accrual Ratio) | [X]% | [<10% 优秀 / >20% 警告 — 可能粉饰] |
| 应收账款周转天数趋势 | [X]天 (YoY [+/-X]天) | [稳定/恶化 — 是否塞渠道] |
| CapEx/折旧比率 | [X]x | [>1.5x 积极扩张 / <0.8x 吃老本] |
| 自由现金流收益率 (FCF Yield) | [X]% | [>5% 有吸引力 / <2% 昂贵] |

---

## 二A、管理层质量评估 (P0 新增)
> "We back jockeys, not horses." — 管理层是长期回报的最大变量。

### 核心管理团队
| 姓名 | 职位 | 任期 | 背景 |
|------|------|------|------|
| [CEO] | CEO | [X]年 | [行业老兵/空降/创始人] |
| [CFO] | CFO | [X]年 | [背景] |
| [关键人物] | [职位] | [X]年 | [背景] |

### 资本配置战绩
| 维度 | 评估 | 依据 |
|------|------|------|
| 并购 ROI | [增值/持平/毁值] | [过去5年主要并购案例及回报] |
| 有机增长投入 | [高效/一般/低效] | [R&D/CapEx 转化为收入增长的效率] |
| 股东回报 | [优秀/一般/差] | [分红+回购占FCF比例，vs同行] |
| 资产负债管理 | [保守/平衡/激进] | [杠杆水平变化趋势] |

### 管理层利益一致性
| 指标 | 数值 | 信号 |
|------|------|------|
| 管理层持股比例 | [X]% | [Skin in the game 程度] |
| 近12个月增减持 | [净增/净减 $X] | [用脚投票方向] |
| 薪酬结构 | [股权:现金 = X:Y] | [激励是否与股东一致] |
| 对标指标 | [ROE/EPS/TSR/其他] | [是否鼓励长期价值创造] |

### 指引兑现率 (Guidance Hit Rate)
| 财年 | 管理层指引 | 实际值 | 兑现 |
|------|-----------|--------|------|
| [上一年] | [营收/EPS 指引] | [实际] | [✅ 达成 / ❌ 未达 / 🎯 超额] |
| [前年] | [指引] | [实际] | [评价] |

### 继任者风险评估
- **关键人物依赖度**: [高/中/低] — [是否有灵魂人物？年龄？继任计划？]
- **管理层深度**: [深/浅] — [二号人物能否平稳接班？]

**管理层综合评级**: [A/B/C/D] — [一句话总结]

---

## 二B、盈利模型与预期追踪 (P0 新增)
> 来源: `Skill("equity-research:earnings-analysis")` + `Skill("equity-research:model-update")`
> 市场交易的是预期差，不是已知数据。

### 一致预期修正趋势 (Estimate Revision Momentum)
| 指标 | 90天前 | 当前 | 变化方向 | 信号 |
|------|--------|------|---------|------|
| 当季 EPS 一致预期 | $[X] | $[X] | [↑上调/↓下调/→持平] | [正面/负面] |
| 下季 EPS 一致预期 | $[X] | $[X] | [方向] | [信号] |
| 全年 EPS 一致预期 | $[X] | $[X] | [方向] | [信号] |
| 上调/下调分析师比例 | — | [X]上调/[Y]下调 | — | [净上调=正面] |

### 历史 Beat/Miss 记录
| 季度 | EPS 预期 | EPS 实际 | 超预期% | 营收 Beat/Miss |
|------|---------|---------|---------|---------------|
| [最近Q] | $[X] | $[X] | [+/-X%] | [Beat/Miss X%] |
| [前1Q] | $[X] | $[X] | [+/-X%] | [Beat/Miss] |
| [前2Q] | $[X] | $[X] | [+/-X%] | [Beat/Miss] |
| [前3Q] | $[X] | $[X] | [+/-X%] | [Beat/Miss] |
| **8季度 Beat Rate** | | | **[X]/8** | **[X]/8** |

### 关键敏感性分析
*对于资源/周期型公司，必须测试商品价格敏感性；对于科技型公司，测试用户增长/ARPU 敏感性。*

| 变量 | 变动幅度 | 对 EPS 的影响 | 对目标价的影响 |
|------|---------|-------------|-------------|
| [核心商品价格/关键KPI] +10% | [描述] | [+/-$X] ([+/-X%]) | [+/-$X] |
| [核心商品价格/关键KPI] -10% | [描述] | [+/-$X] ([+/-X%]) | [+/-$X] |
| [第二变量] +/-[X]% | [描述] | [影响] | [影响] |
| [汇率] +/-10% | [描述] | [影响] | [影响] |

### 卖方一致评级汇总
| 指标 | 数值 |
|------|------|
| 强烈买入 | [X] 家 |
| 买入 | [X] 家 |
| 持有 | [X] 家 |
| 卖出 | [X] 家 |
| 一致目标价 | $[X] (区间 $[低]-$[高]) |
| vs 当前股价 | [上行/下行 X%] |

---

## 三、估值分析
> 来源: `Skill("financial-analysis:dcf-model")` + `Skill("financial-analysis:comps-analysis")` + 格雷厄姆安全边际框架
> 注：DCF 和 Comps Skills 默认生成 Excel 模型；此处使用其内嵌摘要输出。带 `--html` 时同步保存 Excel 文件。

### 可比公司分析
| 公司 | 市值 | EV/Revenue | EV/EBITDA | P/E | 营收增速 |
|------|------|-----------|-----------|-----|---------|
| **$ARGUMENTS** | | | | | |
| [可比公司1] | | | | | |
| [可比公司2] | | | | | |
| [可比公司3] | | | | | |
| **中位数** | | | | | |

### 格雷厄姆安全边际估值
| 指标 | 数值 | 说明 |
|------|------|------|
| Graham Number | $[X] | √(22.5 × EPS × BVPS) |
| 当前股价 | $[X] | |
| Graham 安全边际 | [X]% | (Graham Number - 股价) / Graham Number |

*注：Graham Number 适用于盈利稳定的成熟公司。对于高成长型公司，Graham Number 可能低估内在价值，需结合 DCF 综合判断。*

### DCF 内在价值估算
基于 [增长假设] 和 [WACC]%:

| 情景 | 增长率假设 | DCF 内在价值 | vs 当前股价 | 安全边际 |
|------|-----------|-------------|-----------|---------|
| 保守 | [X]% | $[X] | [折价/溢价 X%] | [X]% |
| 中性 | [X]% | $[X] | [折价/溢价 X%] | [X]% |
| 乐观 | [X]% | $[X] | [折价/溢价 X%] | [X]% |

**综合估值判断**: [格雷厄姆视角: 买入/持有/卖出] — [依据安全边际百分比说明理由]

### 反向 DCF — 市场隐含了什么？(P0 新增)
| 指标 | 数值 | 解读 |
|------|------|------|
| 当前股价 | $[X] | |
| 隐含永续增长率 | [X]% | [市场在price-in多少增长？合理/过于乐观/保守] |
| 隐含 5年 CAGR | [X]% | [vs 历史实际增长率 [X]%，差距多大] |
| **结论** | | **[市场已经定价了[X]情景，当前买入意味着你在赌...]** |

### SOTP 分部估值 (P0 新增)
*将公司拆分为各业务板块/资产分别估值后加总。适用于多业务线公司、综合矿企、控股集团等。*

| 业务板块 | 估值方法 | 估值 | 占比 | 说明 |
|----------|---------|------|------|------|
| [板块A] | [EV/EBITDA Xx] | $[X]亿 | [X]% | [可比公司/倍数依据] |
| [板块B] | [DCF/NAV] | $[X]亿 | [X]% | [假设] |
| [板块C] | [P/E Xx] | $[X]亿 | [X]% | [假设] |
| 净负债 | 账面 | -$[X]亿 | | |
| **SOTP 总计** | | **$[X]亿** | | |
| **SOTP 每股价值** | | **$[X]** | | **vs 当前$[X] = [折价/溢价 X%]** |

*对于矿业/资源公司，额外提供 NAV（净资产价值）估值和 EV/Reserve（储量估值）对比。*

### 情景分析
| 情景 | 目标价 | 概率 | 核心假设 |
|------|--------|------|---------|
| 乐观 | $[X] | [X]% | [假设] |
| 基准 | $[X] | [X]% | [假设] |
| 悲观 | $[X] | [X]% | [假设] |

---

## 四、行业与竞争格局
> 来源: `Skill("financial-analysis:competitive-analysis")` + `Skill("equity-research:sector")` + `theme-detector`

### 行业定位
- 所属行业/赛道、行业增速、渗透率
- 行业周期阶段（早期/成长/成熟/衰退）

### 巴菲特护城河分析
逐项评估该公司的持久竞争壁垒：

| 护城河维度 | 评分 (1-10) | 具体表现 |
|-----------|------------|---------|
| 品牌/无形资产 | [X] | [品牌认知度、专利、许可证、定价权] |
| 转换成本 | [X] | [客户迁移到竞品的实际成本和摩擦] |
| 网络效应 | [X] | [用户/开发者生态的正反馈循环强度] |
| 成本优势 | [X] | [规模经济、独占资源、流程优势] |
| 有效规模 | [X] | [市场容量是否天然限制新进入者] |
| **护城河综合评级** | **[宽/窄/无]** | **[一句话总结理由]** |

**护城河趋势**: [扩大/稳定/收窄] — [依据]

### vs 主要竞争对手的差异化定位
- [与具体竞品的对比分析]

### 当前热门主题关联 (Theme Detector)
| 主题 | 热度 | $ARGUMENTS 关联度 | 影响方向 |
|------|------|------------------|---------|
| [如 AI 基础设施] | 🔥🔥🔥 | 高/中/低 | 正面/负面 |
| [如 降息周期] | 🔥🔥 | 高/中/低 | 正面/负面 |
| [如 去全球化] | 🔥 | 高/中/低 | 正面/负面 |

### 供给侧分析 (P2 改进)
*对于周期型/资源型行业，供给分析与需求同等重要。*

| 供给因素 | 当前状态 | 趋势 | 对价格的影响 |
|----------|---------|------|------------|
| 新建产能 Pipeline | [X万吨/年 未来3年] | [增加/持平/减少] | [供给压力/缓解] |
| 现有矿山品位趋势 | [下降/稳定/提升] | [长期恶化/稳定] | [隐性供给收缩] |
| 环保审批约束 | [宽松/收紧/极严] | [趋紧] | [抑制新增供给] |
| 废料回收率 | [X]% | [提升/稳定] | [边际供给补充] |
| 地缘导致的供给中断 | [无/低风险/高风险] | [描述] | [短期价格冲击] |

*对于科技/消费行业，替换为：竞品推出节奏、替代技术成熟度、行业标准变迁。*

### 行业风险
- [监管变化、技术替代、新进入者威胁]

---

## 五、催化剂与投资论题
> 来源: `Skill("equity-research:catalysts")` + `Skill("equity-research:thesis")` + `scenario-analyzer`

### 近期催化剂（0-6个月）
- [具体事件+日期：财报、产品发布、监管决定、回购]

### 中期催化剂（6-24个月）
- [战略举措、市场扩张、新业务线]

### 投资论题
**核心多头逻辑**:
1. [论点1]
2. [论点2]
3. [论点3]

**核心空头逻辑**:
1. [风险1]
2. [风险2]
3. [风险3]

### 18个月情景推演 (Scenario Analyzer)
基于当前最重要的催化剂，推演三条路径：

| 路径 | 概率 | 12个月后价格区间 | 关键假设 |
|------|------|-----------------|---------|
| 乐观路径 | [X]% | $[X]-$[Y] | [1次影响 → 2次影响 → 3次影响] |
| 基准路径 | [X]% | $[X]-$[Y] | [链条描述] |
| 悲观路径 | [X]% | $[X]-$[Y] | [链条描述] |

---

## 六、技术面与市场信号
> 来源: `/trading-ideas` 技术部分 + `institutional-flow-tracker` + `options-strategy-advisor`

### 价格结构
| 指标 | 数值 |
|------|------|
| 当前价格 | $[X] |
| 52周最高 | $[X] |
| 52周最低 | $[X] |
| 距高点跌幅 | [X]% |
| RSI (14) | [X] |
| 50日均线 | $[X] |
| 200日均线 | $[X] |

### 关键技术位
- **支撑位**: $[X], $[X]
- **阻力位**: $[X], $[X]
- **趋势**: [上升/下降/横盘]
- **Stage 分析**: [Stage 1 蓄力 / Stage 2 上升 / Stage 3 顶部 / Stage 4 下降]

### 道氏理论趋势确认
| 维度 | 判断 | 依据 |
|------|------|------|
| 主要趋势 (Primary) | [牛市/熊市/盘整] | [更高的高点+更高的低点 / 更低的低点+更低的高点] |
| 次要趋势 (Secondary) | [回调/反弹/延续] | [当前处于主要趋势中的什么阶段] |
| 成交量确认 | [确认/背离] | [价量关系是否支持趋势判断] |

### 机构资金流向 (13F Deep Dive)
| 季度 | 增持机构数 | 减持机构数 | 净变化 | 代表性机构 |
|------|-----------|-----------|--------|-----------|
| 最新季度 | [X] | [X] | [净增/净减] | [机构名+动作] |
| 上季度 | [X] | [X] | [净增/净减] | [机构名+动作] |

**Smart Money 信号**: [聪明钱是在积累还是派发？]

### 内部人交易
- [近期内部人买卖：人名、职位、金额、日期]
- [回购计划及执行进度]

### 期权市场深度分析 (Options Strategy Advisor)
| 指标 | 数值 | 信号 |
|------|------|------|
| Put/Call Ratio | [X] | [偏多/偏空/中性] |
| 30天隐含波动率 (IV30) | [X]% | [高于/低于历史均值] |
| IV Rank (52周) | [X]% | [便宜/正常/昂贵] |
| 异常活动 | [描述最近的大单] | [方向性判断] |

**期权策略建议** (基于当前 IV 环境):
- 看多: [具体策略，如 Bull Call Spread $X/$Y，到期日] — 最大风险 $[X]，最大收益 $[Y]
- 看空: [具体策略] — 最大风险 $[X]，最大收益 $[Y]
- 中性: [具体策略，如 Iron Condor] — 适用于 [条件]

---

## 六C、衍生品与流向情报 (v1.1 新增)

**市场分支执行**：

### 美股 / 港股大型 ticker
调用 options-strategy-advisor skill 的 flow_analyzer 脚本：
```bash
python3 ~/.claude/skills/options-strategy-advisor/scripts/flow_analyzer.py {TICKER} --expiries 3
```
数据源: CBOE delayed quotes (免费，无 token)，返回真实 OI / volume / IV / Greeks。

提取并报告：
- **Put/Call ratio** (OI 和 volume 两口径)
- **Max Pain** 点位 + 距离现价百分比
- **IV 期限结构** (近 3 个到期日的 ATM IV)
- **IV Skew** (OTM put IV vs OTM call IV)
- **Top OI strikes** (call/put 各前 3 — 支撑/阻力代理)
- **GEX 估算** (; 正=dealer 压制波动, 负=dealer 放大波动)
- **定性解读**（来自 flow_analyzer 的 interpretation 字段）

对辩论的用途: Bull 可引用 "P/C 0.65 看多定位"；Bear 可引用 "GEX -bn 负 gamma 放大下跌"。

### A 股 (6 位数字 ticker)
调用 a-share-flow-analyzer skill：
```bash
python3 ~/.claude/skills/a-share-flow-analyzer/scripts/flow_analyzer.py {TICKER} --lookback 60
```
数据源: TuShare Pro (需 TUSHARE_TOKEN env var)。

提取并报告：
- **融资余额** + 60 日变化% + 52 周分位
- **融资净买入 5/20 日** (亿元)
- **融券余额** (通常很小，突增时警惕)
- **龙虎榜近 30 日上榜次数** + 机构/游资净买入对比
- **主力资金 5/20 日净流入** (亿元)
- **大单占比** (>0.3 为显著机构参与)

对辩论的用途: Bull 可引用 "20日融资净买入+73亿，机构持续加仓"；Bear 可引用 "融资余额52周80%分位过热"。

### 港股小票 / 无期权覆盖 ticker
报告："该股票无期权数据且非 A 股标的，流向情报不可用。可用模块九(舆情)和模块六(技术面)作为替代。"

### 整体衍生品/流向评分
基于上述信号给出 1-10 打分，纳入综合评分卡新增的 "衍生品/流向" 维度（如果存在）。

---

## 七、风险管理与仓位建议
> 来源: `position-sizer` + `/trading-ideas` 风控部分

### 风险评估
| 风险类型 | 具体风险 | 影响程度 |
|----------|---------|---------|
| 公司层面 | [X] | 高/中/低 |
| 行业层面 | [X] | 高/中/低 |
| 宏观层面 | [X] | 高/中/低 |

### 科学仓位计算 (Position Sizer)
假设账户总值 $100,000、单笔最大风险 1%:

| 方法 | 建议股数 | 仓位金额 | 占比 |
|------|---------|---------|------|
| 固定风险法 (止损距离) | [X] 股 | $[X] | [X]% |
| ATR 法 (2x ATR止损) | [X] 股 | $[X] | [X]% |
| Kelly Criterion | [X] 股 | $[X] | [X]% |
| **建议采用** | **[X] 股** | **$[X]** | **[X]%** |

*用户可根据自身账户规模等比例调整。*

### 交易计划
- **入场策略**: [一次性/分批/等回调到 $X]
- **止损位**: $[X] ([X]% 下行) — 依据: [技术位/ATR/前低]
- **目标位 1**: $[X] ([X]% 上行) — 减仓 [X]%
- **目标位 2**: $[X] ([X]% 上行) — 清仓
- **风险收益比**: [X]:1
- **持有期预期**: [X]-[X] 个月

### 压力测试矩阵 (P2 改进)
| 场景 | 变量 | 对营收的影响 | 对EPS的影响 | 对目标价的影响 |
|------|------|------------|-----------|-------------|
| [核心商品/KPI -20%] | [描述] | [X%] | [$X / X%] | [$X] |
| [美元/人民币 +10%] | [描述] | [X%] | [$X / X%] | [$X] |
| [多因子同时恶化] | [金铜同跌+美元走强+矿权费翻倍 等] | [X%] | [$X / X%] | [$X] |
| [黑天鹅情景] | [核心矿山停产3个月] | [X%] | [$X / X%] | [$X] |

---

## 七A、资产负债表深度分析 (P1 新增)
> 来源: 财报数据 + 信用评级机构

### 杠杆与偿债能力
| 指标 | 数值 | 行业中位数 | 信号 |
|------|------|-----------|------|
| 净负债/EBITDA | [X]x | [X]x | [健康/警告/危险] |
| 利息覆盖倍数 (EBITDA/利息) | [X]x | [X]x | [安全/需关注] |
| 资产负债率 | [X]% | [X]% | [保守/适中/激进] |
| 流动比率 | [X] | [X] | [充裕/紧张] |
| 速动比率 | [X] | [X] | [充裕/紧张] |

### 债务到期时间表
| 到期年份 | 金额 | 占总债务比 | 再融资风险 |
|----------|------|-----------|----------|
| [今年] | $[X]亿 | [X]% | [低/中/高] |
| [明年] | $[X]亿 | [X]% | [低/中/高] |
| [后年] | $[X]亿 | [X]% | [低/中/高] |
| [3年以上] | $[X]亿 | [X]% | — |

### 信用评级
| 评级机构 | 当前评级 | 展望 | 最近变动 |
|----------|---------|------|---------|
| [穆迪/标普/中诚信] | [评级] | [正面/稳定/负面] | [日期+变动] |

### 外币敞口
- **海外收入占比**: [X]%
- **主要币种暴露**: [USD/CDF/ARS 等]
- **汇率每波动10%对净利润的影响**: [+/-X%]

---

## 七B、跨资产相关性与因子暴露 (P1 新增)
> 来源: 量化数据分析

### 相关性矩阵（60日滚动）
| 资产 | 相关系数 | 信号 |
|------|---------|------|
| 基准指数 (沪深300/S&P500) | [X] | [Beta = X] |
| [核心商品1: 黄金/原油等] | [X] | [高度相关/弱相关/负相关] |
| [核心商品2: 铜/锂等] | [X] | [高度相关/弱相关/负相关] |
| 美元指数 (DXY) | [X] | [通常负相关 — 验证] |
| 10年期国债收益率 | [X] | [对利率的敏感度] |

### 因子暴露 (Style Factor Exposure)
| 因子 | 暴露度 | 说明 |
|------|--------|------|
| Value | [高/中/低] | [PE/PB 处于什么分位] |
| Growth | [高/中/低] | [营收/EPS增速排名] |
| Momentum | [高/中/低] | [6/12个月相对收益] |
| Quality | [高/中/低] | [ROE/盈利稳定性/资产负债表] |
| Size | [大盘/中盘/小盘] | [市值排名] |
| Volatility | [高波/中波/低波] | [实现波动率 vs 行业] |

### 组合角色定位
- **该股在组合中扮演什么角色**: [Alpha来源 / Beta敞口 / 周期对冲 / 通胀保护 / 避险资产]
- **最佳配对/对冲标的**: [基于相关性分析的建议]

---

## 八、泡沫与极端风险检测
> 来源: `us-market-bubble-detector` (市场级) + 个股层面延伸

### 估值泡沫信号
| 指标 | 当前值 | 历史中位数 | 偏离度 | 信号 |
|------|--------|-----------|--------|------|
| Forward P/E | [X]x | [X]x | [+/-X]% | [正常/警告/危险] |
| P/S (TTM) | [X]x | [X]x | [+/-X]% | [正常/警告/危险] |
| EV/FCF | [X]x | [X]x | [+/-X]% | [正常/警告/危险] |

### 市场级泡沫指标
- **VIX**: [X] ([正常/偏低自满/偏高恐慌])
- **Put/Call Ratio (市场级)**: [X] ([正常/极端乐观/极端悲观])
- **Margin Debt 趋势**: [上升/下降/历史高位]
- **IPO/SPAC 热度**: [冷淡/正常/过热]

### 极端风险评估
- **尾部风险概率**: [低/中/高] — [依据]
- **黑天鹅暴露**: [该股特有的尾部风险场景]

---

## 九、舆情与市场情绪动量 (P3 新增)
> 来源: WebSearch（Reddit, X/Twitter, 股吧, 雪球, Polymarket 等） + `agent-reach`
> 目的: 捕捉「散户情绪拐点」和「信息不对称信号」— 机构报告不会告诉你的东西。

### 板块情绪温度计
| 平台 | 所属板块热度 | 个股热度 | 情绪倾向 | 关键话题 |
|------|------------|---------|---------|---------|
| 雪球/股吧 (中国) | [🔥-🔥🔥🔥] | [🔥-🔥🔥🔥] | [极度看多/偏多/中性/偏空/极度看空] | [热门讨论主题] |
| Reddit (WSB/stocks) | [🔥-🔥🔥🔥] | [🔥-🔥🔥🔥] | [情绪] | [热门帖子摘要] |
| X/Twitter | [🔥-🔥🔥🔥] | [🔥-🔥🔥🔥] | [情绪] | [KOL观点/热门推文] |
| Polymarket/预测市场 | — | [如有相关合约] | [隐含概率] | [具体合约及赔率] |

### 量化情绪指标
| 指标 | 数值 | 历史分位 | 信号 |
|------|------|---------|------|
| 社交媒体提及量 (7日) | [X] 条 | [X]% 分位 | [正常/异常放大] |
| 情绪正负比 | [X]:[Y] | — | [偏多/偏空/中性] |
| 板块讨论热度排名 | 第[X]名/[N]个板块 | — | [领先/中等/冷门] |
| 个股讨论热度排名 | 第[X]名/板块内[N]只 | — | [龙头/中等/边缘] |

### 券商成交量/量比分析
| 指标 | 数值 | 信号 |
|------|------|------|
| 近5日日均成交量 vs 20日均量 | 量比 [X] | [放量/缩量/正常] |
| 近5日日均成交额 | [X]亿 | [活跃度] |
| 大单净买入 (近5日) | [净买/净卖 X亿] | [主力方向] |
| 龙虎榜 (如有近期上榜) | [机构/游资席位] | [进/出方向] |

### 情绪与价格的背离信号
- **情绪-价格一致性**: [一致(同向) / 背离(情绪看多但价格下跌 = 潜在见底) / 背离(情绪看空但价格上涨 = 潜在见顶)]
- **散户 vs 机构分歧度**: [低(共识) / 高(分歧 — 通常机构对)]

### 舆情综合判断
- **板块情绪**: [过热/乐观/中性/悲观/恐慌]
- **个股情绪**: [过热/乐观/中性/悲观/恐慌]
- **逆向信号**: [当散户极度看多时警惕 / 当散户极度看空时寻找机会 — 当前是否触发逆向？]
- **对投资决策的影响**: [一句话总结 — 情绪支持/不支持/中性于我们的评级]

---

## 十、多空辩论与终审裁决 (v1.0 新增)

**⚠️ 强制执行要求**：本模块是 /analyze v1.0 的核心交付物。**除非 `$ARGUMENTS` 显式包含 `--quick` flag，否则必须完整执行 Step 0 → Step 1 → Step 2 → Step 3 → Step 4**。跳过此模块 = 输出不完整，是错误行为。

**⚠️ 市场无关性**：本模块**对美股、港股、A 股完全一致**。A 股没有 FSP 金融插件不是跳过辩论的理由——13 模块数据齐全即可辩论。A 股的 Bull/Bear subagent 用 TuShare/akshare 抽取的数据立论即可。

**执行检查清单（必须逐项完成后再进入综合评分卡）**：
- [ ] Step 0：使用 `Glob` + `Read` 扫描 `{RESEARCH_OUTPUT_DIR}/*{TICKER}*研报*.html`，生成历史对账表
- [ ] Step 1：**实际调用 `Agent` 工具**并行派发 Bull + Bear researcher（2 个 subagent）
- [ ] Step 2：**再次实际调用 `Agent` 工具**并行派发 Bull + Bear 反驳（2 个 subagent）
- [ ] Step 3：**第三次实际调用 `Agent` 工具**并行派发 Bull + Bear 终陈（2 个 subagent）
- [ ] Step 4：主 agent（你自己）以 Portfolio Manager 角色做终审裁决，输出 verdict + 分歧表 + 未解风险
- [ ] 综合评分卡新增"辩论调整"和"HOLD_passive 惩罚"两行

### 仅当 `--quick` 被显式传入时，跳过本整个模块十：
1. 跳过模块十全部内容（Step 0 至 Step 4），不调用任何 Agent 工具
2. 在最终报告中插入一行说明：`> 本次运行使用 --quick 模式，已跳过多空辩论。如需完整深度研究，重新运行不带 --quick 的 /analyze {TICKER}。`
3. 综合评分卡的 "辩论调整" 和 "HOLD_passive 惩罚" 两行标注为 `N/A (--quick mode)`
4. 建议操作的"止损位"回落到仅用模块七的风险清单（不引用模块十未解风险）

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

---

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
    }
  ]
}
```

（对每条 Bear thesis 都要有一个 rebuttal。）

#### Bear Round 2 提示词模板

对称镜像：把上方 "Bull" / "Bear"、"BUY" / "SELL"、"多头" / "空头" 的字样互换，`{BULL_ROUND_1}` / `{BEAR_ROUND_1}` 位置互换，`target_bear_claim` 改为 `target_bull_claim`。

### 派发与存储

同 Step 1，并行派发两个 subagent，结果合并进 `ROUND_2_TRANSCRIPT`。

---

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

对称镜像（BUY → SELL，多头 → 空头，Bear's arguments → Bull's arguments 等）。

### 派发与存储

同前，并行派发，合并为 `ROUND_3_TRANSCRIPT`。

### Step 4 — Judge 终审裁决

**主 agent 直接完成，不派发 subagent**（Judge 需要看所有 context，放在主 agent 里更方便）。

你现在切换到 Portfolio Manager 视角，对三轮辩论做裁决。

#### 可用信息（已在你的 context 里）
- 13 模块完整分析
- 历史判断对账
- ROUND_1_TRANSCRIPT / ROUND_2_TRANSCRIPT / ROUND_3_TRANSCRIPT

#### Hold 规则 D（重要 — 不允许和稀泥式 Hold）

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

#### 裁决输出（严格 JSON）

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
    }
  ],
  "winner_reasons": ["胜方胜在哪"],
  "loser_fatal_flaws": ["败方致命伤是什么"],
  "unresolved_risks": [
    "（Bear 提出但 Bull 未能反驳的风险 — 这些将成为止损/减仓触发条件）"
  ],
  "scorecard_adjustments": {
    "基本面质量": "+1",
    "估值吸引力": "-2"
  },
  "hold_reason": "（如果 verdict 是 HOLD_active 或 HOLD_passive，说明具体理由）",
  "confidence_in_verdict": 1-10
}
```

（key_disagreements 数组 3-5 条核心分歧即可。）

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
```

**重要**：这段渲染完后，报告才能接着走 `## 📋 综合评分卡` 区块。综合评分卡里的"综合评分"一行必须应用 Judge 的 `scorecard_adjustments`。如果 verdict 是 `HOLD_passive`，综合评分额外 -1 分。

---

## 📋 综合评分卡

| 维度 | 评分 (1-10) | 框架来源 | 备注 |
|------|------------|---------|------|
| 大盘环境 | [X] | 宏观体制 + 马克斯周期 | [一句话 — 来自模块〇] |
| 基本面质量 | [X] | 财报 + 盈利质量 | [一句话 — 含盈利质量信号] |
| 管理层质量 | [X] | 管理层评估 (P0) | [评级 A/B/C/D + 关键风险] |
| 盈利预期动量 | [X] | 盈利模型 (P0) | [上调/下调趋势 + Beat Rate] |
| 估值吸引力 | [X] | Graham + DCF + 反向DCF + SOTP | [SOTP vs 市价 + 隐含增长率] |
| 增长前景 | [X] | 基本面 + 供给侧 | [一句话] |
| 竞争优势 | [X] | 巴菲特护城河 | [宽/窄/无 + 一句话] |
| 技术面 | [X] | Stage + 道氏理论 | [一句话] |
| 催化剂密度 | [X] | 催化剂分析 | [一句话] |
| 机构/期权信号 | [X] | 13F + 期权 | [一句话] |
| 周期位置 | [X] | 马克斯周期思维 | [行业周期阶段 + 进攻/防守] |
| 资产负债表健康度 | [X] | 信用分析 (P1) | [净负债/EBITDA + 信用评级] |
| 舆情/情绪动量 | [X] | 舆情分析 (P3) | [板块+个股情绪 + 逆向信号] |
| 风险回报比 | [X] | 综合 + 压力测试 | [一句话] |
| **综合评分** | **[X]/10** | | **14维度加权平均** |
| **辩论调整** | [见模块十 scorecard_adjustments] | Bull/Bear Debate | 从模块十 Judge 的 scorecard_adjustments 应用调整 |
| **HOLD_passive 惩罚** | [−1 如适用] | Hold Rule D | 仅当 verdict=HOLD_passive 时 -1；否则 0 |
| **综合评分（辩论调整后）** | **[X]/10** | | **14 维度 + 辩论调整** |

### 多框架交叉验证
| 框架 | 结论 | 一致性 |
|------|------|--------|
| 格雷厄姆（价值/安全边际） | [低估/合理/高估] | |
| 巴菲特（护城河/品质） | [优质/一般/劣质] | |
| 马克斯（周期/情绪） | [进攻/中性/防守] | |
| 技术面（Stage + 道氏） | [上升/横盘/下降] | |
| 管理层/资本配置 (P0) | [优秀/合格/堪忧] | |
| 舆情/散户情绪 (P3) | [支持/中性/逆向] | |
| **框架共识** | **[X/6 一致看多/看空/分歧]** | **[高/中/低]** |

> 💡 如需 CAN SLIM 七维度详细评分，请运行 `/canslim-screener $ARGUMENTS`

---

## 建议操作

| 指标 | 值 |
|------|-----|
| **评级** | [买入/持有/卖出] |
| **确信度** | [高/中/低] |
| **目标价** | $[X] |
| **时间框架** | [X] 个月 |
| **上行空间** | [X]% |
| **建议仓位** | [X]%-[Y]% |
| **止损位** | $[X] — 触发条件：[从模块十未被反驳的风险清单中选 2-3 条最具体的作为监测点] |
| **风险收益比** | [X]:1 |
| **仓位调整规则** | [正常仓位 / HOLD_passive → 正常仓位的 50% / HOLD_active → 正常仓位] |

---

**⚠️ 免责声明**: 本分析仅供教育和研究用途，不构成投资建议。过往表现不保证未来收益。投资有风险，入市需谨慎。请在做出投资决策前咨询持牌专业人士。

*由 Claude Code 全面深度研究系统生成*

---

## 质量标准

### 必须包含：

**原有核心要求：**
- 所有财务数据必须有具体数字和百分比
- 目标价必须有上行/下行空间计算
- 可比公司至少 3-4 家，附带完整估值倍数
- 格雷厄姆 Graham Number 和安全边际百分比（对盈利公司）
- DCF 必须有保守/中性/乐观三个场景及安全边际
- 巴菲特护城河 5 维度评分 + 宽/窄/无 综合评级
- 马克斯周期定位 4 维度（行业周期/情绪/信贷/资本开支）
- 技术面必须有具体支撑/阻力位、Stage 判断和道氏理论确认
- 内部人交易必须有人名和金额
- 13F 机构流向必须有具体机构名和增减持方向
- 期权分析必须有 IV Rank、Put/Call Ratio 和具体策略建议
- 仓位计算必须有固定风险法和 ATR 法两种
- 大盘环境必须有广度评分和顶部概率

**P0 新增要求（管理层+盈利模型+估值深度）：**
- 管理层评估必须有 CEO/CFO 履历、资本配置战绩、持股/增减持、指引兑现率、继任者风险
- 盈利模型必须有90天预期修正趋势、8季度Beat/Miss记录、关键敏感性分析
- 估值必须有反向DCF（隐含增长率）和 SOTP 分部估值
- 卖方一致评级汇总必须有买入/持有/卖出家数和目标价区间

**P1 新增要求（资产负债表+跨资产）：**
- 资产负债表必须有净负债/EBITDA、利息覆盖倍数、债务到期时间表、信用评级
- 跨资产相关性必须有 Beta、核心商品相关系数、因子暴露（Value/Growth/Momentum/Quality）
- 组合角色定位（Alpha来源/Beta敞口/周期对冲 等）

**P2 改进要求：**
- 基本面必须有盈利质量检验（现金流/净利润、应计利润比率、应收账款周转天数）
- 行业必须有供给侧分析（新建产能/品位趋势/环保约束）
- 风险必须有压力测试矩阵（至少4个场景 + 对EPS和目标价的影响）

**P3 新增要求（舆情情绪动量）：**
- 板块/个股在雪球/股吧/Reddit/X 的情绪温度（看多/看空/中性）
- 量化情绪指标（社交提及量、情绪正负比、热度排名）
- 券商成交量量比 + 大单方向 + 龙虎榜（如有）
- 情绪-价格背离信号 + 逆向投资判断

**综合评分卡 14 个维度全部填写**
**多框架交叉验证表 6 框架全部填写**（格雷厄姆/巴菲特/马克斯/技术面/管理层/舆情）

### 输出要求：
- 全部使用中文，金融术语保留英文缩写
- 表格格式统一、对齐
- 数据标注来源时间（YoY、QoQ、LTM 等）
- 情景分析必须有概率权重
- 盈后评分仅在近期有财报时展示，否则标注 N/A

---

## HTML 投行研报输出（可选）

> 当 `$ARGUMENTS` 包含 `--html` 时自动启用，或用户在 Markdown 报告完成后手动执行 `/report [TICKER]`。

### 触发条件
- `$ARGUMENTS` 中包含 `--html`（如 `/analyze NVDA --html`）
- 则在 Markdown 分析完成后，**自动追加 HTML 报告生成阶段**

### HTML 报告生成规范

**核心原则：HTML 必须包含前序 Markdown 报告的 100% 内容，一个模块都不能少。**

> 🚨 **绝对禁止**：不得用 `Write` / `Edit` 工具直接生成 HTML 文件。必须且只能通过以下方式调用 `report` skill。绕过此步骤会导致深色主题/样式错误。

执行 `--html` 时，**必须用 `Skill` 工具显式调用 `report` skill**。**关键：如果 `$ARGUMENTS` 包含 `--lang en`，必须把该 flag 一并透传给 `/report`，否则 HTML 会退回中文**。

| 模式 | 调用方式 |
|------|---------|
| 普通 | `Skill("report", "TICKER")` |
| 静默 | `Skill("report", "TICKER --silent")` |
| 英文 | `Skill("report", "TICKER --lang en")` |
| 英文+静默 | `Skill("report", "TICKER --silent --lang en")` |

示例：
- `/analyze 002851 --html --silent` → `Skill("report", "002851 --silent")`
- `/analyze AAPL --html --lang en` → `Skill("report", "AAPL --lang en")`
- `/analyze NVDA --html --silent --lang en` → `Skill("report", "NVDA --silent --lang en")`

`report` skill 包含完整的 Goldman Sachs 风格规范（色板 `#00338D`、21个区块结构、评级条、KPI 面板、ECharts 图表等）。直接写 HTML 会导致样式不符合投行标准（历史教训：2026-04-14 生成了黑色主题报告）。

### 文件输出
- 保存路径：`{RESEARCH_OUTPUT_DIR}/[TICKER]-研报-YYYYMMDD.html`（从 $ARGUMENTS 中提取纯股票代码作为文件名）
- **`--silent` 模式下**：`report` skill 生成文件后**不自动打开浏览器**；仅输出一行进度：
  ```
  ✅ [N/总数] TICKER 研报已生成 → /路径/TICKER-研报-YYYYMMDD.html
  ```
- **非 `--silent` 模式下**：`report` skill 生成文件后自动 `open` 打开浏览器，并告知用户完整路径 + Ctrl/Cmd+P 可导出 PDF

### 使用示例

```
/analyze NVDA                          ← 单股 Markdown 分析
/analyze NVDA --html                   ← 单股 Markdown + HTML 研报（自动打开）
/analyze AAPL,NVDA,TSLA --html         ← 批量分析 + HTML（逐一输出 + 打开）
/analyze AAPL,NVDA,TSLA --html --silent ← 批量静默（无控制台输出，直接生成文件）
```
