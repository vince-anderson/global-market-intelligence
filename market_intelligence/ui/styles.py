"""Local styling; no external fonts, assets, or scripts are requested."""

TERMINAL_CSS = """
<style>
.block-container {max-width: 1600px; padding-top: 2rem; padding-bottom: 3rem;}
[data-testid="stSidebar"] {border-right: 1px solid #223047;}
h1 {font-size: 2.35rem !important; letter-spacing: -.06rem;}
h2 {font-size: 1.15rem !important; letter-spacing: .015rem;}
h3 {font-size: 1rem !important;}
.eyebrow {color: #39d7bc; font: 600 .72rem monospace; letter-spacing: .18rem;}
.subtitle {color: #91a1b7; margin: -.4rem 0 1.4rem; font-size: .95rem;}
.demo-badge {display: inline-block; color: #f1bd68; background: #2a2318;
 border: 1px solid #594323; border-radius: 5px; padding: .3rem .7rem;
 font: 600 .76rem monospace; margin-bottom: .7rem;}
[data-testid="stMetric"] {background: #111a29; border: 1px solid #223047;
 border-radius: 9px; padding: 1rem;}
[data-testid="stMetricLabel"] {color: #91a1b7;}
[data-testid="stMetricValue"] {font-size: 1.65rem; font-family: monospace;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 9px;}
</style>
"""
