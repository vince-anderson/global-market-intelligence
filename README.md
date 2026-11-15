# Global Market Intelligence

面向全球金融市场的开源投资研究辅助系统，使用 **Python + Streamlit + Plotly**。深色宽屏终端，支持真实美股 / ETF 日线，以及明确分开的离线模拟模式。

## 当前能力

- 默认真实数据模式：SPY、QQQ、DIA、IWM 市场总览，股票 / ETF 观察列表和 Plotly 走势图。
- 预设 20 个候选代码；支持输入 AAPL、AMD、VOO、BRK-B 等代码扩展观察列表。
- 图表按 30 / 90 / 180 / 365 **自然日**筛选实际交易日记录；新上市资产可能不足完整区间。
- 显示数据来源、日线记录日期和时间、抓取时间（UTC+8）、交易所、币种及数据源报告的延迟。
- 数据请求失败会明确报错；不会偷偷回退到模拟数据。部分失败时保留其他资产的有效数据。
- 加密货币、代币化美股、全球宏观和量化研究仅保留导航与单独的模拟演示，尚未接入真实数据或回测。

## 数据从哪里来？

本版本使用 **Yahoo Finance 公开 chart 接口**获取美元计价美国股票 / ETF 的日线，不需要 API 密钥。它是**聚合源和非官方公开接口，不是交易所一手数据接口**，可能延迟、限流、更改格式或停止服务；不提供服务等级保证。本项目未与 Yahoo 建立合作关系。

- 数据参考页面：[Yahoo Finance](https://finance.yahoo.com/)。
- 若需要交易所原始行情或有保证的实时服务，应评估 [Nasdaq 数据产品](https://www.nasdaq.com/solutions/data) 或有授权的数据服务及其市场覆盖、费用和展示许可。
- 公司公告与财报的一手来源是 [SEC EDGAR](https://www.sec.gov/edgar)，与行情接口是两类数据，本版尚未接入。
- 免费可访问不等于获得公开展示或再分发许可。公开或商业展示前，请确认所选数据提供方的适用条款与许可；可在数据适配层更换为获授权的数据源。

**“真实”不等于“实时”。** 此页面展示最新可用日线，最后一条可能是仍在交易中的当日日线。休市、周末、节假日或停牌时，记录日期可能早于今天。日线时间戳不是逐笔报价时间；获取时间只是应用成功请求数据的时间，不能用来冒充行情更新时间。数据源未披露延迟时明确显示“未披露”。

价格采用数据源返回的日线 `close`，本系统不另做复权。变化为最后两条有效日线价格的百分比变化，不包含分红收益，不是包含分红的总回报；不包含盘前盘后行情。缺失、非正或非有限价格会被剔除，不会填充或伪造价格。最后记录超过 4 个自然日时提示核查；该提示不是交易日历判断。

## 自动同步：不用手工修改价格

1. 页面打开时，应用从数据源获取行情；相同代码组合的成功结果缓存最多 **300 秒**，跨会话复用。
2. “每 5 分钟自动检查”默认开启。网页保持活跃连接时，Streamlit fragment 每 300 秒刷新数据区；关闭开关后仍可通过交互重新检查已到期的缓存。
3. “立即刷新行情”清除当前代码组合的缓存并重新请求，可能受上游限流影响。
4. 所有资产请求失败时不缓存该错误；部分成功的批次（含失败提示）缓存最多 300 秒，下一次到期或手动刷新再试失败资产。
5. Community Cloud 应用休眠、网页关闭或没有活跃会话时，不保证后台持续获取。重新打开页面后恢复获取；本版没有定时入库、历史快照存储或后台任务。

**行情更新不需要 Git 提交或重新部署。** 代码更新则需要 PR 合并到 Community Cloud 绑定的分支，平台通常会自动重新部署。

## 本地运行

推荐 Python **3.12**（CI 验证版本）。在项目根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

仅部署应用可安装 `requirements.txt`。不需要数据库、交易账户或付费 API。受限网络需允许 HTTPS 到 `query1.finance.yahoo.com`，保留 TLS 校验。如果上游拒绝访问或限流，请查看页面错误提示，不要将演示行情当作真实数据。

## 目录结构

```text
app.py                        # 页面编排、模式选择及模块导航
market_intelligence/
  data/
    models.py                 # 基础资产模型与模拟提供者协议
    demo.py                   # 确定性离线模拟数据
    yahoo.py                  # 真实日线适配、校验、来源时间和批量请求
  research/modules.py         # 五大领域注册表与规划
  ui/
    live.py                   # 真实美股 / ETF 工作区、缓存与刷新
    demo.py                   # 用户明确选中的模拟工作区
    charts.py                 # 独立 Plotly 图表，区分真实 / 模拟标签
    styles.py                 # 本地终端样式
.streamlit/config.toml        # 深色主题及无界面服务器配置
.github/workflows/tests.yml   # Python 3.12 CI
requirements.txt              # 应用直接依赖的固定版本
requirements-dev.txt          # 测试依赖
tests/                        # 数据适配、图表和 Streamlit 交互测试
```

真实适配器返回带来源时间和价格序列的 `MarketSeries`；未来可新增提供者，将认证、限流、交易所时区和许可要求封装在数据层。HTTP 请求不放在界面里，缓存与页面刷新由界面层管理。模拟协议保留兼容，不把模拟记录混入真实数据集。

## 模拟模式

侧栏明确选择“模拟演示”后才使用模拟价格。`DemoMarketDataProvider` 以各资产 SHA-256 种子生成 520 个自然日价格，固定结束于 **2026-01-30**，不代表真实历史、交易时段、交易日历或当前行情。带 `-DEMO` 的代币代码为虚构产品标识。宏观区仅展示 ETF 模拟代理，量化区未实现回测。

## 测试与联网验证

```bash
python -m pytest -q
python -m pip check
python -m streamlit run app.py --server.headless true --server.port 8501
# 另一个终端：
curl --fail http://127.0.0.1:8501/_stcore/health
# 实际数据源连通性与结构检查（需要出网，失败会返回非零状态）：
python scripts/check_market_data.py
```

自动测试使用明确的人工 HTTP fixtures，检查数据校验、来源时间、限流、错误处理、部分失败、缓存和手动刷新、添加代码、空观察列表、模拟隔离及模块导航，不依赖公网也不消耗上游配额。**离线测试通过不代表真实数据源联网验证通过。** 使用上面的独立检查检查实际端点；不更改预期价格或忽略请求失败来让它通过。

## 部署到 Streamlit Community Cloud

1. 审核合并 PR 到应用绑定的 GitHub 分支（通常 `main`）；已有应用通常会自动重新部署。如未更新，在 Manage app 检查构建日志或重启应用。
2. 新建部署时登录 [Community Cloud](https://share.streamlit.io/)，选择 `vince-anderson/global-market-intelligence`、目标分支和入口 `app.py`。
3. 高级设置选择 **Python 3.12**；此数据源不需要 Secrets。平台安装根目录 `requirements.txt`。
4. 确认页面为“真实美股 / ETF”模式，检查资产数据、来源、日线日期与抓取时间；切换图表区间、添加代码并测试刷新。
5. 若显示请求失败 / 限流，检查云端日志及上游可用性。开发环境的网络配置不会自动改变 Community Cloud 的网络环境；必须在部署端独立验证。

本代码不会自动创建、发布或修改你的 Community Cloud 应用设置。当前不接入交易账户，不提供下单功能，也不构成投资建议。

## 密钥与本地数据

`.gitignore` 排除 `.env` 系列、Streamlit Secrets、私钥、虚拟环境、缓存及 `data/local/`、`data/private/`、`data/raw/`、`local_data/`。不要提交持仓、账户或个人数据。未来密钥放入 Community Cloud Secrets，不写入代码；忽略规则不能移除已被 Git 跟踪的敏感文件。
