"""Registry of research domains; each can gain its own provider and tools later."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchModule:
    key: str
    name: str
    description: str
    next_steps: str


MODULES = (
    ResearchModule("equities", "美股", "上市公司与指数研究", "财报、估值、行业比较与公司事件"),
    ResearchModule("tokenized", "代币化美股", "探索股票的代币化表达", "发行方、托管结构、流动性与跟踪偏差"),
    ResearchModule("crypto", "加密货币", "数字资产与市场结构", "链上指标、交易场所与资金费率"),
    ResearchModule("macro", "全球宏观", "跨资产宏观研究", "经济数据、利率曲线、汇率与发布日历"),
    ResearchModule("quant", "量化研究", "可复现的策略研究工作区", "因子分析、含成本回测与样本外检验"),
)
MODULE_BY_NAME = {module.name: module for module in MODULES}
