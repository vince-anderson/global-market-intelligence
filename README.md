# Global Market Intelligence

面向全球金融市场的开源投资研究辅助系统。使用 **Python + Streamlit + Plotly**，当前为第一阶段的深色、宽屏研究终端原型。

> **全部行情均为模拟数据，不是实时行情或真实历史数据。** 不接入付费行情 API、交易账户，也不提供下单功能。带 `-DEMO` 的代币代码完全虚构，不表示可交易产品。

## 本地运行

推荐 Python **3.12**（云端与 CI 的验证版本）。在项目根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

仅部署应用可安装 `requirements.txt`。无需 API 密钥、数据库或其他后台服务。通过终端提示的地址访问本地应用。

## 当前功能

- 4 个市场总览指标、10 个模拟资产的可选观察列表。
- Plotly 价格图表：资产切换、30 / 90 / 180 / 365 自然日窗口、悬停和缩放。
- 美股、代币化美股、加密货币、全球宏观、量化研究工作区导航。
- 空观察列表提示、数据来源提示、会话内状态和专业深色主题。

宏观区仅展示黄金和美债 ETF 的模拟价格作为宏观资产代理，不包含真实经济指标。量化区暂为研究入口，未实现回测或因子分析。模块卡片的“规划”内容尚未实现。

## 模拟数据约定

`DemoMarketDataProvider` 通过每个资产的 SHA-256 种子生成 520 个自然日的随机价格路径，固定结束于 **2026-01-30**。重复运行得到相同数据，不随当前时间变化。周末也有模拟价格；不模拟交易所日历、交易时段、分红拆股、成交量、价差或交易成本。

总览、观察列表和图表共享同一数据源；模拟日变化为最后两个自然日价格的百分比变化。全部价格标注为 USD；数值不应用于投资、产品定价或策略收益评估。

## 目录结构

```text
app.py                        # Streamlit 入口与页面编排
market_intelligence/
  data/
    models.py                 # Asset 模型、MarketDataProvider 协议
    demo.py                   # 确定性模拟数据，无网络调用
  research/
    modules.py                # 五大领域注册表及后续能力描述
  ui/
    charts.py                 # 不依赖 Streamlit 会话的 Plotly 图表
    styles.py                 # 本地终端视觉样式
.streamlit/config.toml        # 深色主题及无界面服务器配置
.github/workflows/tests.yml   # Python 3.12 CI
requirements.txt              # 应用直接依赖的固定版本
requirements-dev.txt          # 测试依赖
 tests/                       # 数据、图表与 Streamlit 交互测试
```

扩展时在 `data/` 添加实现 `MarketDataProvider` 的提供者，将 API 认证、限流、缓存、时区和数据来源标识封装在数据层；不要在界面组件中直接调用 API。研究功能可按领域扩展到 `research/equities/`、`tokenized/`、`crypto/`、`macro/`、`quant/`，有实际代码时再创建目录。当前不创建空模块或伪造已完成功能。

## 测试与启动验证

```bash
python -m pytest -q
python -m streamlit run app.py --server.headless true --server.port 8501
# 在另一个终端检查服务健康：
curl --fail http://127.0.0.1:8501/_stcore/health
```

测试覆盖所有资产的模拟数据一致性、涨跌幅计算、图表窗口、首页渲染、空观察列表、全部工作区和模块按钮导航。Streamlit AppTest 会执行应用及交互；健康检查只证明服务器正常响应，不能代替页面测试。

## 部署到 Streamlit Community Cloud

1. 将此功能分支的 PR 审核合并到 GitHub `main`（也可先部署功能分支测试）。
2. 登录 [Streamlit Community Cloud](https://share.streamlit.io/)，授权访问该 GitHub 仓库。
3. 选择 **Create app**，仓库选择 `vince-anderson/global-market-intelligence`，分支选择 `main` 或待测试的功能分支，入口填 `app.py`。
4. 在高级设置中选择 **Python 3.12**；本阶段不需要填写任何 Secrets。
5. 点击 **Deploy**。平台会安装根目录 `requirements.txt`，并使用 `.streamlit/config.toml` 主题配置。
6. 打开部署页面，确认“模拟数据 · 非实时行情”提示、4 个总览指标、观察列表、图表和导航；切换资产和区间，检查日志无异常。

以上为部署说明，仓库代码不会自动创建或发布云应用。Community Cloud 的运行资源和服务条款以平台当前说明为准。

## 密钥与本地数据

`.gitignore` 排除 `.env` 系列、Streamlit Secrets、私钥、虚拟环境、缓存及 `data/local/`、`data/private/`、`data/raw/`、`local_data/`。不要提交账户、持仓或个人数据。将未来的云端密钥保存在 Community Cloud Secrets；不要写入代码或 README。忽略规则不能移除已经被 Git 跟踪的敏感文件。

本项目是研究辅助工具，不构成投资建议。
