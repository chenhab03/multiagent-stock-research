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
| Self-reflection | yes — reads own past reports | no |
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
| `/analyze TICKER --lang en` | Output the report in English (default: 中文) |
| `/analyze T1,T2,T3 --html --silent` | Batch mode |
| `/report TICKER` | Regenerate HTML from latest analysis |

### Sample output

A real rendered report is at [`samples/AAPL-sample-report.html`](samples/AAPL-sample-report.html). Open it in a browser to see the full Goldman-Sachs-style layout, including Module 10 debate (Bull/Bear columns, core disagreement matrix, unresolved risks, composite scorecard with debate adjustments).

> Quick preview without cloning: https://raw.githack.com/chenhab03/multiagent-stock-research/main/samples/AAPL-sample-report.html

**English sample report** (generated with \`--lang en\`): [`samples/AAPL-sample-english.html`](samples/AAPL-sample-english.html) — preview: https://raw.githack.com/chenhab03/multiagent-stock-research/main/samples/AAPL-sample-english.html

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

| | multiagent-stock-research | TradingAgents |
|---|---|---|
| 分析深度 | 13 个模块 | 4 个分析师角色 |
| 辩论轮数 | 3 轮（开场 / 反驳 / 终陈） | 可配置，默认 1 轮 |
| 市场覆盖 | 美股 + 港股 + A 股 | 仅美股 |
| 自我反思 | 有 — 读取自身过往报告 | 无 |
| 输出格式 | 高盛风格 HTML + 评分卡 + 止损触发条件 | 交易决策字符串 |
| 方法论框架 | 格雷厄姆 / 巴菲特 / 欧尼尔 / 米纳维尼 / 德鲁肯米勒 / 马克斯 | 通用 LLM 提示词 |
| 安装方式 | 1 个 shell 脚本，无需 Python 环境 | Python 包 + Docker |
| 运行时依赖 | 无（仅 Claude Code） | LangGraph + 多个 LLM SDK |

### 快速开始

```bash
# 1. 克隆
git clone https://github.com/YOUR_USER/multiagent-stock-research
cd multiagent-stock-research

# 2. 安装
./install.sh

# 3. 配置（加到 ~/.zshrc 或 ~/.bashrc）
export TUSHARE_TOKEN="..."      # A 股分析师数据 — https://tushare.pro
export FINNHUB_TOKEN="..."      # 美股内部人/机构数据 — https://finnhub.io
export RESEARCH_OUTPUT_DIR="$HOME/equity-research"   # 可选，默认 ~/equity-research

# 4. 在 Claude Code 中使用
/analyze NVDA --html
```

### 命令参数

| 命令 | 行为 |
|---|---|
| `/analyze TICKER` | 完整 13 模块 + 辩论，Markdown 输出 |
| `/analyze TICKER --html` | 同上并生成 HTML 研报 |
| `/analyze TICKER --silent` | 静默模式，不输出 Markdown，仅进度行 |
| `/analyze TICKER --quick` | 跳过模块十辩论（快速筛查模式） |
| `/analyze TICKER --lang en` | 输出英文研报（默认中文） |
| `/analyze T1,T2,T3 --html --silent` | 批量静默模式 |
| `/report TICKER` | 从最新分析重新生成 HTML |

### 示例报告

真实研报样本：[`samples/AAPL-sample-report.html`](samples/AAPL-sample-report.html)，浏览器打开可看完整高盛风格布局，含 Module 10 辩论区（多空 Top 3、核心分歧矩阵、未解风险、含辩论调整的评分卡）。

> 不克隆也能预览：https://raw.githack.com/chenhab03/multiagent-stock-research/main/samples/AAPL-sample-report.html

**英文版 sample**（\`--lang en\` 生成）：[`samples/AAPL-sample-english.html`](samples/AAPL-sample-english.html) — 预览: https://raw.githack.com/chenhab03/multiagent-stock-research/main/samples/AAPL-sample-english.html

### 方法论

详见 [docs/methodology.md](docs/methodology.md)。

核心框架集成：
- **格雷厄姆（Graham）** — 安全边际、Graham Number
- **巴菲特（Buffett）** — 护城河 5 维度评分
- **欧尼尔（O'Neil）** — CAN SLIM 7 维度评分卡
- **米纳维尼（Minervini）** — Stage 分析 + VCP（波动收缩形态）
- **德鲁肯米勒（Druckenmiller）** — 宏观 + 集中持仓
- **马克斯（Marks）** — 周期定位（债务周期 / 情绪周期 / 资本开支周期）

### License

MIT

### 免责声明

仅供研究和教育用途。**不构成投资建议。** 过往业绩不保证未来收益，投资前请咨询持牌专业人士。
