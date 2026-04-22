---
description: "将当前对话中的个股分析结果生成投行级 HTML 研报。可在 /analyze 完成后独立调用，或用 /analyze TICKER --html 自动触发。"
---

# 投行级 HTML 研报生成器

> 将当前对话中已完成的个股分析（通常来自 `/analyze`）转化为一份可交付的 Goldman Sachs 风格 HTML 研报。

## 使用方式

```
/report                    ← 自动检测当前对话中分析过的股票
/report NVDA               ← 指定股票代码
/report NVDA --ft          ← 指定风格（ft / mckinsey / economist / swiss / stamen / fathom / sagmeister / takram / irma-boom / build）
/report NVDA --silent      ← 静默模式：生成文件但不自动打开浏览器（由 /analyze --silent 自动传入）
```

## 前置条件

**必须在当前对话中已经存在该股票的完整分析数据**（来自 `/analyze` 或手动分析）。如果没有，提示用户先执行 `/analyze [TICKER]`。

需要的数据清单（从对话上下文中提取）：
- [ ] 基本面数据（营收/EPS/毛利率等）
- [ ] 盈利质量检验（现金流/净利润比、应计比率、应收周转、FCF Yield）
- [ ] 管理层质量评估（CEO/CFO履历、资本配置、内部人持股、指引命中率）
- [ ] 盈利模型与预期追踪（预期修正动量、Beat/Miss历史、敏感性分析）
- [ ] 估值数据（PE/PS/DCF/Graham Number/反向DCF/SOTP）
- [ ] 竞争对手可比数据
- [ ] 护城河评估
- [ ] 供给侧分析（产能管线、矿石品位、环保约束、地缘供应风险）
- [ ] 周期定位
- [ ] 技术面关键价位
- [ ] 资产负债表深度分析（净负债/EBITDA、利息覆盖、债务到期、信用评级）
- [ ] 跨资产相关性与因子暴露（相关性矩阵、因子暴露、组合角色）
- [ ] 压力测试矩阵（4+场景 × EPS/目标价影响）
- [ ] 舆情与市场情绪动量（雪球/股吧/Reddit/X/Polymarket + 券商成交量/大单）
- [ ] 综合评分卡（14维度）
- [ ] 多框架交叉验证结论（6框架）
- [ ] 最终评级（BUY/NEUTRAL/SELL）

缺失任何一项时，在报告中标注「数据待补充」而非编造。

## 风格系统

### 默认风格：Goldman Sachs 投行报告

**设计哲学**：Tables are king — 数据表格承载分析，图表辅助，评级判断最先呈现。

**色板**：
```
Header/表头:    #00338D (GS深蓝)
强调金:         #D4AF37 (Investment Thesis, Base Case)
负面红:         #C62828
正向绿:         #2E7D32
页面背景:       #F8F9FA
卡片/表格:      #FFFFFF
边框:           #DEE2E6
斑马纹行:       #FAFBFC
Bottom Line:   #F0F4F8
```

### 可选风格

| 标记 | 风格 | 一句话感觉 |
|------|------|-----------|
| `--ft` | Financial Times | 三文鱼粉的温暖权威，衬线标题 |
| `--mckinsey` | McKinsey | 深蓝结构化，Exhibit编号 |
| `--economist` | The Economist | 红线杂志密度，editorial标题 |
| `--swiss` | Swiss/NZZ | 黑白极简，极端字号对比 |
| `--stamen` | Stamen Design | 赭石+鼠尾草绿，地形层叠 |
| `--fathom` | Fathom | 海军蓝科学期刊，Figure编号 |
| `--sagmeister` | Sagmeister & Walsh | 99%克制+1%色彩爆发 |
| `--takram` | Takram | 日式轻量，柔和科技感 |
| `--irma-boom` | Irma Boom | 铁锈红+暮粉，编辑叙事 |
| `--build` | Build | 200字重+70%留白，奢侈品气质 |

## 基础布局契约（所有风格必须遵守）

```css
html { background: [与body背景色一致]; }
body {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 48px;
  font-family: 'Helvetica Neue', Arial, "PingFang SC", sans-serif;
}
```

- `margin: 0 auto` — 浏览器居中
- html/body 背景色一致 — 无色差
- 辅助文字 ≥ 10pt
- 表格必须有斑马纹
- 标题用结论句式（如「安全边际不足，等待回调」而非「估值分析」）

## 核心原则：HTML 必须包含 Markdown 报告的 100% 内容

**绝不允许 HTML 版本比 Markdown 版本少任何模块或数据。** HTML 是 Markdown 的「可视化升级版」，内容只多不少。

遍历 `/analyze` 输出的全部 13 个模块（〇到九 + 二A/二B/七A/七B）+ 评分卡 + 建议操作，逐一转化为 HTML 区块。如果 Markdown 中有的数据，HTML 中必须有对应的表格/段落。

---

## 报告结构（21 个区块，按顺序生成，与 /analyze 模块一一对应）

### 1. Header + Rating Strip（评级条）
```
[深蓝Header]
  左: [TICKER] — 深度研究报告
  右: 日期
[Rating Strip]
  评级徽章 BUY(绿)/NEUTRAL(金)/SELL(红)
  目标价 $X | 上行空间 X% | 确信度 高/中/低 | 时间框架
```

### 2. KPI 指标面板（5 格并排）
```
| 当前价格 | 安全边际% | 护城河评级 | 综合评分/100 | 风险收益比 |
```
每格包含：大号数值 + 小字标签 + 变化方向箭头

### 3. Investment Thesis 框
4px 金色左边框 `#D4AF37`，浅灰背景 `#F4F6F9`：
- 🟢 3 条核心多头逻辑
- 🔴 3 条核心空头逻辑

### 4. 大盘环境评估（对应模块〇）
**必须包含以下全部子表格**：
- 宏观体制判断（Risk-On/Off + 依据）
- 市场广度健康度表（>200日占比/新高新低/涨跌线/广度评分）
- 市场顶部概率（Distribution Days/领涨股/防御板块/综合评分）
- 霍华德·马克斯周期定位表（行业周期/情绪/信贷/资本开支 4维度）
- 对该股的影响判断（顺风/逆风/中性）

### 5. 执行摘要（对应模块一）
一段话核心投资逻辑，包含评级、目标价、确信度。

### 6. 基本面分析（对应模块二）
**必须包含**：
- 财务数据表（营收/EPS/毛利率/经营利润率/FCF/资产负债率 + 同比 + 预估）
- 产量/业务指标表（公司特有KPI + YoY + 驱动因素）
- 管理层指引段落
- 盈后动量评分表（如有，5因子评分；无则标注N/A）
- **盈利质量检验子表**（P2）：
  - 现金流/净利润比（≥1.0 绿 / 0.7-1.0 金 / <0.7 红）
  - 应计比率（低=优 / 中 / 高=劣）
  - 应收账款周转率 + YoY 变化
  - CapEx/折旧比率
  - FCF Yield + 行业对比
  - 综合盈利质量评级徽章（高/中/低）

### 6A. 管理层质量评估（对应模块二A，P0）
**必须包含**：
- 管理层履历表（CEO/CFO/COO + 任期 + 背景 + 关键成就）
- 资本配置记录表（近3-5年 + 并购/回购/分红/研发 + ROI评估 + 评级）
- 内部人持股对齐表（管理层持股% + 近12月增减持 + 信号判断）
- 指引命中率段落（历史指引 vs 实际 + 可信度评级）
- 继任风险评估（关键人物依赖度 + 梯队深度 + 风险等级徽章）
- 综合管理层质量评分（/10）

### 6B. 盈利模型与预期追踪（对应模块二B，P0）
**必须包含**：
- 预期修正动量表（EPS/营收 + 90天修正方向 + 幅度 + 修正比率 + 动量信号灯）
- 8季度 Beat/Miss 历史表（季度 + 预期EPS + 实际EPS + 惊喜% + 股价反应 + 热力色彩编码）
- 敏感性分析表（关键变量 ±10%/±20% → EPS影响 + 目标价影响）
- 卖方一致预期汇总段落（覆盖家数 + 评级分布 + 目标价范围 + 中位数）

### 7. 估值分析（对应模块三）
**必须包含**：
- 可比公司表（4-5家，含 PE/PS/PEG/EV/EBITDA + 行业中位数行）
- Graham Number + 安全边际行（含适用性注释）
- DCF 三场景表（保守/中性/乐观 + 假设参数 + 安全边际%）
  - Base Case 用金色边框高亮
- **反向DCF子表**（P0）：
  - 当前股价隐含增长率 + 合理性判断
  - 隐含增长率 vs 历史增速 vs 行业增速对比行
  - 结论段落（市场预期是否过高/过低）
- **SOTP 分部估值子表**（P0，适用多业务线/资源公司）：
  - 各业务分部/矿区（收入/EBITDA/适用倍数/估值 + 方法论）
  - NAV 汇总行（资源公司用储量×价格-成本法）
  - 合计 vs 当前市值 + 折溢价%
- 情景分析表（乐观/基准/悲观 + 目标价 + 概率 + 核心假设）

### 8. 行业与竞争格局（对应模块四）
**必须包含**：
- 行业定位段落（赛道/增速/渗透率/周期阶段）
- 巴菲特护城河5维度评分表 + 综合评级徽章（宽=绿/窄=金/无=红）
- 护城河趋势判断
- 主题关联表（主题/热度/关联度/影响方向）
- **供给侧分析子区块**（P2）：
  - 新产能管线表（项目/产能/投产时间/影响评估）
  - 矿石品位/资源质量趋势段落（适用资源股）
  - 环保/ESG约束段落（碳税/排放/合规成本）
  - 废料回收/替代供应段落
  - 地缘政治供应中断风险表（地区/风险事件/概率/影响）
- 行业风险段落

### 9. 催化剂与投资论题（对应模块五）
**必须包含**：
- 近期催化剂列表（0-6个月，含日期）
- 中期催化剂列表（6-24个月）
- 18个月情景推演表（乐观/基准/悲观路径 + 概率 + 价格区间 + 因果链）

### 10. 技术面与市场信号（对应模块六）
**必须包含**：
- 价格结构表（当前价/52周高低/RSI/均线）
- 关键技术位段落（支撑/阻力/趋势/Stage）
- 道氏理论趋势确认表（主要趋势/次要趋势/成交量确认）
- 技术面 SVG 价位图（当前价+支撑+阻力+Stage标注+道氏箭头）
- 机构资金流向表（季度/增减持/代表机构 + Smart Money信号）
- 内部人交易段落
- 期权市场分析表（P/C Ratio/IV30/IV Rank/异常活动 + 策略建议）

### 11. 风险管理与仓位建议（对应模块七）
**必须包含**：
- 风险评估表（公司/行业/宏观层面 + 具体风险 + 影响程度徽章）
- 仓位计算表（固定风险法/ATR法/Kelly + 股数/金额/占比）
- 交易计划段落（入场策略/止损位/目标位1&2/风险收益比/持有期）

### 11A. 资产负债表深度分析（对应模块七A，P1）
**必须包含**：
- 杠杆与偿债能力表：
  - 净负债/EBITDA（≤1.5x 绿 / 1.5-3x 金 / >3x 红）
  - 利息覆盖倍数（≥5x 绿 / 3-5x 金 / <3x 红）
  - 流动比率 / 速动比率
- 债务到期日历表（年份 + 到期金额 + 利率 + 再融资风险评级）
- 信用评级段落（当前评级 + 展望 + 与同行对比）
- 外汇敞口表（货币 + 收入占比 + 成本占比 + 净敞口 + 对冲状态）
- 综合资产负债表健康评分（/10）

### 11B. 跨资产相关性与因子暴露（对应模块七B，P1）
**必须包含**：
- 相关性矩阵表（该股 vs 大盘指数/行业ETF/大宗商品/美元/利率 + 30日/90日/1年相关系数 + 热力色彩）
- 因子暴露表（Value/Growth/Momentum/Quality/Size/Volatility + 暴露度 + 行业对比 + 信号判断）
- 组合角色段落（作为Alpha来源/Beta替代/对冲工具的适配评估）

### 11C. 压力测试矩阵（P2）
**必须包含**：
- 压力测试表（≥4场景，每场景含）：
  - 场景名称（如「商品价格暴跌30%」「人民币贬值15%」「多因子叠加」「黑天鹅」）
  - 触发条件
  - EPS影响%
  - 目标价影响
  - 发生概率
  - 风险等级徽章（高=红/中=金/低=绿）
- 关键阈值段落（公司能承受的最大不利变动）

### 12. 泡沫与极端风险（对应模块八）
**必须包含**：
- 估值泡沫信号表（Forward PE/PS/EV/FCF + 当前值 vs 历史中位数 + 偏离度 + 信号灯）
- 市场级泡沫指标段落（VIX/P/C Ratio/Margin Debt/IPO热度）
- 极端风险评估（尾部风险概率 + 黑天鹅暴露）

### 12A. 舆情与市场情绪动量（对应模块九，P3）
**必须包含**：
- 平台舆情汇总表：
  | 平台 | 情绪倾向 | 热度 | 关键观点 | 信号判断 |
  - 雪球/股吧/Reddit/X/Polymarket（各一行）
- 量化情绪指标表：
  - 散户情绪指数（看多/看空比例 + 7日变化）
  - 机构情绪指标（大单净买入/卖出 + 龙虎榜 + 融资融券余额变化）
  - 搜索热度趋势（百度指数/Google Trends + 30日变化%）
- 券商成交量分析子表：
  - 量比（当日/5日/20日均量比）
  - 大单流向（超大单/大单/中单/小单净买入）
  - 北向资金持仓变化（A股专用）
- 情绪-价格背离信号段落（情绪极端时的反向信号提示）
- 综合舆情动量评分（/10）

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

### 13. ECharts 交互图表区

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
```

生成以下图表（至少6张）：
- **综合评分雷达图**：14 维度评分卡可视化（新增：管理层质量/盈利预期动量/资产负债表健康度/舆情动量）
- **DCF 情景柱状图**：保守/中性/乐观 + 反向DCF隐含增长率标记线 + 当前股价标记线
- **多框架交叉验证热力图**：6 框架 × 结论矩阵（新增：管理层/资本配置、舆情/散户情绪）
- **产量/增长对比图**：各产品线 YoY 增速
- **压力测试影响瀑布图**：各场景对目标价的影响（ECharts waterfall）
- **舆情情绪仪表盘**：多平台情绪热力图 + 情绪-价格走势叠加
- 可选：SOTP 分部估值饼图、债务到期日历柱状图、因子暴露蛛网图、估值历史分位图

ECharts 色板（GS 风格）：
```javascript
['#00338D', '#5B9BD5', '#D4AF37', '#2E7D32', '#C62828', '#A5A5A5']
```

### 14. 综合评分卡 + 多框架交叉验证 + 建议操作
**必须包含**：
- 14 维度评分表（色彩编码：≥8 绿 / 5-7 金 / <5 红 + 框架来源 + 一句话备注）：
  1. 盈利增长质量（格雷厄姆）
  2. 估值吸引力（格雷厄姆）
  3. 安全边际（格雷厄姆）
  4. 护城河强度（巴菲特）
  5. 管理层质量（巴菲特）— **新增 P0**
  6. 周期定位（马克斯）
  7. 风险收益不对称性（马克斯）
  8. 技术面趋势（O'Neil/道氏）
  9. 机构资金流向（O'Neil）
  10. 催化剂密度（综合）
  11. 盈利预期动量（综合）— **新增 P0**
  12. 资产负债表健康度（综合）— **新增 P1**
  13. 盈利质量（综合）— **新增 P2**
  14. 舆情/情绪动量（综合）— **新增 P3**
- 6 框架交叉验证表：
  1. 格雷厄姆价值框架 + 结论 + 信号灯
  2. 巴菲特质量框架 + 结论 + 信号灯
  3. 马克斯周期框架 + 结论 + 信号灯
  4. 技术面/O'Neil框架 + 结论 + 信号灯
  5. 管理层/资本配置框架 + 结论 + 信号灯 — **新增**
  6. 舆情/散户情绪框架 + 结论 + 信号灯 — **新增**

**新增渲染要求（v1.0）**：

在综合评分卡的最后一行（综合评分 X/10）**之下**新增两行 row（HTML `<tr>`）：
- `辩论调整` — 显示各维度的调整值（来自 Judge 的 scorecard_adjustments）
- `综合评分（辩论调整后）` — 加粗、字号 1.3rem、背景色 #F5F5DC（米色强调）

如果 --quick 模式或 Judge verdict 为 `HOLD_passive`，额外显示：
- HOLD_passive 时：新增一行 `HOLD 惩罚 −1` 并相应调整最终分
- --quick 时：两行均显示 `N/A (--quick mode)`

- 建议操作汇总表（评级/确信度/目标价/时间框架/上行空间/建议仓位/入场区间/止损位/风险收益比）

**新增渲染要求（v1.0）**：

- **止损位** 说明需 append: "触发条件: [列 2-3 条来自模块十未被反驳的风险]"
- 新增一行表格 **仓位调整规则**: 
  - verdict=HOLD_passive → "正常仓位的 50%（被动 Hold 惩罚）"
  - verdict=HOLD_active → "正常仓位（主动 Hold，等待 [catalyst]）"
  - verdict=BUY/SELL → "正常仓位"

### 15. Bottom Line + 页脚
- Bottom Line Strip：3px 深蓝左边框 + 浅灰蓝背景，一句话最终结论 + 适合投资者类型
- 页脚：
```html
<footer>
  <p>⚠️ 免责声明: 本分析仅供教育和研究用途，不构成投资建议。</p>
  <p>由 Claude Code 全面深度研究系统生成 · [日期]</p>
  <p>数据来源: [列出实际使用的数据源]</p>
</footer>
<p style="position:fixed;bottom:2pt;right:12pt;font-size:6.5pt;color:#BBB;">
  Ctrl/Cmd + P 导出PDF
</p>
```

## 文件输出

- 保存路径：`{RESEARCH_OUTPUT_DIR}/[TICKER]-研报-YYYYMMDD.html`
- **`--silent` 模式**（由 `/analyze --silent` 传入）：
  - **不执行** `open` 命令，不自动打开浏览器
  - 仅输出一行进度：`✅ TICKER 研报已生成 → [完整路径]`
- **普通模式**（无 `--silent`）：
  - **生成完成后，必须自动用 `open` 命令在浏览器中打开**：
    ```bash
    open "{RESEARCH_OUTPUT_DIR}/[TICKER]-研报-YYYYMMDD.html"
    ```
  - 打开后告知用户：
    1. 文件完整路径
    2. 「已在浏览器中自动打开」
    3. 「Ctrl/Cmd+P 可导出 PDF」

## 设计红线

- 所有文字中文（金融术语保留英文缩写）
- 标题用结论句式
- 表格必须有斑马纹 + hover 态
- 辅助文字 ≥ 10pt
- **数据必须来自当前对话中的分析结果，绝不编造**
- 缺失数据标注「数据待补充」
- 图表标题、图例、页脚全部中文
- Y 轴基线从 0 开始（除非明确标注非零基线）
- 颜色语义一致：红=风险/负面，绿=正向/安全，金=关注/中性
