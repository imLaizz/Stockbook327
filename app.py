"""
AlphaStream - 跨平台股票分析工具
Author: AlphaStream
Version: 1.2.0
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import math
import urllib.error
import urllib.parse
import urllib.request
import ssl
import warnings

try:
    import certifi
except ImportError:
    certifi = None

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AlphaStream", page_icon="📈",
    layout="wide", initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# VERSION
# ─────────────────────────────────────────────
CURRENT_VERSION = "v1.2"
VERSION_HISTORY = [
    ("v1.2", "2026-03-28", "導入 AlphaInsight AI 診斷系統、版本修訂控制模組。"),
    ("v1.1", "2026-03-27", "修復 Datetime 時區合併錯誤 (ValueError)、優化 Plotly 圖表效能。"),
    ("v1.0", "2026-01-01", "ALPHASTREAM 基礎版本上線，支援台股數據抓取。"),
]

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
TW_POPULAR = [
    ("手動輸入","__manual__"),
    ("2330 台積電","2330.TW"),("2454 聯發科","2454.TW"),("2317 鴻海","2317.TW"),
    ("2308 台達電","2308.TW"),("2382 廣達","2382.TW"),("2303 聯電","2303.TW"),
    ("2412 中華電","2412.TW"),("2881 富邦金","2881.TW"),("2882 國泰金","2882.TW"),
    ("2886 兆豐金","2886.TW"),("3008 大立光","3008.TW"),("6505 台塑化","6505.TW"),
    ("1301 台塑","1301.TW"),("2002 中鋼","2002.TW"),("2609 陽明","2609.TW"),
    ("2615 萬海","2615.TW"),("2603 長榮","2603.TW"),
    ("0050 元大台灣50","0050.TW"),("0056 元大高股息","0056.TW"),
]

TW_NAMES: dict[str, str] = {
    "2330":"台灣積體電路製造","2454":"聯發科技","2303":"聯華電子","2344":"華邦電子",
    "3034":"聯詠科技","2379":"瑞昱半導體","3711":"日月光投控","2408":"南亞科技",
    "2449":"京元電子","6770":"力積電","2337":"旺宏電子","2317":"鴻海精密工業",
    "2308":"台達電子","2382":"廣達電腦","2357":"華碩電腦","2353":"宏碁",
    "2376":"技嘉科技","3008":"大立光電","2395":"研華科技","2301":"光寶科技",
    "2356":"英業達","2324":"仁寶電腦","2327":"國巨","3231":"緯創資通",
    "3037":"欣興電子","6415":"矽力-KY","2881":"富邦金控","2882":"國泰金控",
    "2886":"兆豐金控","2884":"玉山金控","2885":"元大金控","2887":"台新金控",
    "2888":"新光金控","2891":"中信金控","2892":"第一金控","5880":"合庫金控",
    "2883":"開發金控","2890":"永豐金控","2412":"中華電信","3045":"台灣大哥大",
    "4904":"遠傳電信","1301":"台塑","1303":"南亞塑膠","1326":"台化",
    "6505":"台塑石化","2002":"中國鋼鐵","1101":"台灣水泥","1102":"亞洲水泥",
    "1216":"統一企業","2609":"陽明海運","2615":"萬海航運","2603":"長榮海運",
    "2610":"中華航空","2618":"長榮航空","0050":"元大台灣50","0056":"元大高股息",
    "00878":"國泰永續高股息","00881":"國泰台灣5G+","006208":"富邦台50",
}

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;font-size:17px;}
.stApp{background:radial-gradient(ellipse 120% 80% at 20% -20%,#0f1a30 0%,#0a0e1a 45%);color:#d0e4f5;}
.block-container{padding-top:1.5rem !important;max-width:1440px !important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1220 0%,#0a0f18 100%);border-right:1px solid #243552;}
[data-testid="stSidebar"] *{color:#9bb8d4 !important;font-size:1.02rem !important;}

/* AlphaInsight */
.insight-banner{border-radius:14px;padding:22px 28px;margin:0 0 1.5rem 0;border:1px solid;position:relative;overflow:hidden;}
.insight-banner.bullish{background:linear-gradient(135deg,#002d1a,#001a10);border-color:#00e896;}
.insight-banner.neutral{background:linear-gradient(135deg,#1a1400,#0e0c00);border-color:#ffcc00;}
.insight-banner.bearish{background:linear-gradient(135deg,#2a0010,#180008);border-color:#ff4466;}
.insight-title{font-family:'Space Mono',monospace;font-size:1.45rem;font-weight:700;letter-spacing:0.08em;margin-bottom:10px;}
.insight-title.bullish{color:#00ff99;}
.insight-title.neutral{color:#ffcc00;}
.insight-title.bearish{color:#ff4466;}
.insight-comment{font-size:1.05rem;line-height:1.75;color:#c5d8ec;}
.insight-scores{display:flex;gap:12px;flex-wrap:wrap;margin-top:16px;}
.insight-score-pill{font-family:'Space Mono',monospace;font-size:0.82rem;padding:5px 14px;border-radius:20px;letter-spacing:0.08em;}
.pill-pos{background:rgba(0,232,150,0.15);color:#00e896;border:1px solid #00e896;}
.pill-neg{background:rgba(255,68,102,0.15);color:#ff6b8a;border:1px solid #ff4466;}
.pill-neu{background:rgba(255,204,85,0.12);color:#ffcc55;border:1px solid #ffcc44;}

/* Header */
.alpha-header{font-family:'Space Mono',monospace;font-size:2.85rem;font-weight:700;color:#00d4ff;letter-spacing:0.12em;text-shadow:0 0 40px rgba(0,212,255,0.4);margin-bottom:0.15rem;}
.alpha-subtitle{font-family:'Space Mono',monospace;font-size:0.95rem;color:#4a6a8a;letter-spacing:0.28em;text-transform:uppercase;margin-bottom:2.2rem;}

/* Panels */
.dashboard-panel{background:linear-gradient(145deg,rgba(15,24,37,0.95),rgba(10,14,26,0.98));border:1px solid #243552;border-radius:14px;padding:22px 26px;margin:1.25rem 0;box-shadow:0 8px 32px rgba(0,0,0,0.35);}
.section-header{font-family:'Space Mono',monospace;font-size:0.95rem;color:#00d4ff;letter-spacing:0.25em;text-transform:uppercase;border-bottom:1px solid #2a4060;padding-bottom:10px;margin:2rem 0 1.1rem 0;}

/* KPI */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:1rem;}
.kpi-card{background:#0c1524;border:1px solid #1e3555;border-radius:12px;padding:18px 20px;position:relative;overflow:hidden;}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#00d4ff,#0066cc,#8844ff);}
.kpi-label{font-family:'Space Mono',monospace;font-size:0.72rem;color:#5a7a9a;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:8px;}
.kpi-value{font-family:'Space Mono',monospace;font-size:1.75rem;font-weight:700;color:#e8f4ff;line-height:1.1;}
.kpi-sub{font-size:0.88rem;color:#6a8aaa;margin-top:5px;}

/* KD */
.kd-badge{display:inline-flex;align-items:center;gap:8px;font-family:'Space Mono',monospace;font-size:0.88rem;padding:6px 14px;border-radius:20px;letter-spacing:0.08em;font-weight:700;margin:3px 4px 3px 0;}
.kd-overbought{background:rgba(255,68,102,0.18);color:#ff6b8a;border:1px solid #ff4466;}
.kd-oversold{background:rgba(0,232,150,0.15);color:#00e896;border:1px solid #00e896;}
.kd-neutral{background:rgba(255,204,85,0.12);color:#ffcc55;border:1px solid #ffcc44;}
.kd-bar-wrap{background:#0d1a2a;border:1px solid #1e3555;border-radius:10px;padding:14px 18px;margin:8px 0;}
.kd-bar-label{font-family:'Space Mono',monospace;font-size:0.78rem;color:#6a8aaa;letter-spacing:0.14em;display:flex;justify-content:space-between;margin-bottom:7px;}
.kd-bar-track{width:100%;height:10px;background:#1a2d42;border-radius:5px;overflow:hidden;position:relative;}
.kd-bar-fill{height:100%;border-radius:5px;}
.kd-zone-mark{position:absolute;top:0;bottom:0;width:2px;background:rgba(255,255,255,0.15);}

/* Tech */
.tech-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:8px;}
.dash-card{background:#0c1524;border:1px solid #1e3555;border-radius:12px;padding:20px 22px;position:relative;overflow:hidden;}
.dash-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#00d4ff,#0066cc,#8844ff);}
.dash-card-title{font-family:'Space Mono',monospace;font-size:0.78rem;color:#5a7a9a;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:10px;}
.tech-big-num{font-family:'Space Mono',monospace;font-size:2.4rem;font-weight:700;color:#e8f4ff;line-height:1.1;margin-bottom:6px;}
.tech-verdict{font-size:1.15rem;font-weight:600;margin-bottom:12px;}
.tech-verdict.positive{color:#00e896;}.tech-verdict.negative{color:#ff6b8a;}.tech-verdict.neutral{color:#ffcc55;}
.tech-threshold{font-size:1.02rem;line-height:1.65;color:#8ba7c4;border-top:1px solid #1e3555;padding-top:12px;}
.tech-threshold b{color:#c5d8ec;}

/* Signal */
.signal-badge{display:inline-block;font-family:'Space Mono',monospace;font-size:1.35rem;font-weight:700;padding:14px 32px;border-radius:8px;letter-spacing:0.12em;text-transform:uppercase;margin:0.5rem 0;}
.signal-strong-buy{background:#003322;color:#00ff99;border:1px solid #00ff99;}
.signal-buy{background:#002211;color:#00e896;border:1px solid #00e896;}
.signal-hold{background:#1a1500;color:#ffcc00;border:1px solid #ffcc00;}
.signal-watch{background:#1a0e00;color:#ff9944;border:1px solid #ff9944;}
.signal-sell{background:#1a0008;color:#ff4466;border:1px solid #ff4466;}

.ai-reasoning{background:#070d18;border:1px solid #243552;border-radius:12px;padding:22px 26px;margin-top:1rem;font-size:1.05rem;line-height:1.75;color:#9bb8d4;}
.ai-reasoning b{color:#e0eef8;}
.score-row{display:flex;align-items:center;margin:10px 0;gap:14px;}
.score-label{font-family:'Space Mono',monospace;font-size:0.95rem;color:#6a8aaa;width:160px;flex-shrink:0;}
.score-bar-bg{flex:1;height:10px;background:#1a2d42;border-radius:5px;overflow:hidden;}
.score-bar-fill{height:100%;border-radius:5px;}
.score-num{font-family:'Space Mono',monospace;font-size:0.95rem;color:#d0e4f5;width:48px;text-align:right;}

.chip-summary-row{display:flex;align-items:center;gap:14px;padding:10px 0;border-bottom:1px solid #1a2d42;}
.chip-summary-row:last-child{border-bottom:none;}
.chip-name{font-family:'Space Mono',monospace;font-size:0.82rem;color:#6a8aaa;width:90px;flex-shrink:0;}
.chip-streak{font-size:0.98rem;color:#c5d8ec;flex:1;}
.chip-net{font-family:'Space Mono',monospace;font-size:1.0rem;font-weight:700;min-width:120px;text-align:right;}
.chip-net.pos{color:#00e896;}.chip-net.neg{color:#ff4466;}.chip-net.neu{color:#ffcc55;}

div[data-testid="metric-container"]{background:#0c1524 !important;border:1px solid #1e3555 !important;border-radius:10px !important;padding:16px 18px !important;}
div[data-testid="metric-container"] label{font-size:1rem !important;}
div[data-testid="metric-container"] [data-testid="stMetricValue"]{font-size:1.45rem !important;}
.stSelectbox label,.stTextInput label{font-family:'Space Mono',monospace;font-size:0.82rem !important;letter-spacing:0.12em;color:#6a8aaa !important;text-transform:uppercase;}
.stButton>button{background:linear-gradient(135deg,#003355,#006699);color:#00d4ff;border:1px solid #006699;border-radius:8px;font-family:'Space Mono',monospace;font-size:1rem !important;letter-spacing:0.12em;width:100%;padding:12px 14px;transition:all 0.2s ease;}
.stButton>button:hover{background:linear-gradient(135deg,#004466,#0088bb);border-color:#00d4ff;box-shadow:0 0 20px rgba(0,212,255,0.25);}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# MODULE 1: DATA
# ═══════════════════════════════════════════

@st.cache_data(ttl=300)
def fetch_price_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty: return pd.DataFrame()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df
    except Exception as e:
        st.error(f"價格數據獲取失敗: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def fetch_fundamentals(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info
        def sg(k, d="N/A"):
            v = info.get(k, d); return v if v not in [None, 0, ""] else "N/A"
        dy  = info.get("dividendYield")
        roe = info.get("returnOnEquity")
        gm  = info.get("grossMargins")
        return {
            "name": sg("longName", ticker), "sector": sg("sector"),
            "market_cap": info.get("marketCap"), "pe_ratio": sg("trailingPE"),
            "forward_pe": sg("forwardPE"), "eps": sg("trailingEps"),
            "roe":         f"{roe*100:.2f}%" if roe else "N/A",
            "gross_margin":f"{gm*100:.2f}%"  if gm  else "N/A",
            "div_yield":   f"{dy*100:.2f}%"  if dy  else "N/A",
            "52w_high": sg("fiftyTwoWeekHigh"), "52w_low": sg("fiftyTwoWeekLow"),
            "current_price": sg("currentPrice"), "currency": sg("currency","USD"),
            "beta": sg("beta"), "volume": sg("volume"),
        }
    except Exception as e:
        return {"name": ticker, "error": str(e)}


def parse_tw_stock_id(ticker: str) -> str | None:
    t = ticker.strip().upper()
    if t.endswith(".TWO"): return t[:-4]
    if t.endswith(".TW"):  return t[:-3]
    return None


def resolve_display_name(ticker: str, fundamentals: dict) -> str:
    sid = parse_tw_stock_id(ticker)
    if sid and sid in TW_NAMES: return TW_NAMES[sid]
    n = fundamentals.get("name","")
    return n if n and n != ticker else ticker


# ═══════════════════════════════════════════
# MODULE 1b: FINMIND
# ═══════════════════════════════════════════

FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"

def _ssl_ctx():
    return ssl.create_default_context(cafile=certifi.where()) if certifi else ssl.create_default_context()

@st.cache_data(ttl=300)
def finmind_fetch(dataset, data_id="", start_date="", end_date=""):
    p = {"dataset": dataset}
    if data_id:    p["data_id"]    = data_id
    if start_date: p["start_date"] = start_date
    if end_date:   p["end_date"]   = end_date
    url = FINMIND_URL + "?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers={"User-Agent":"AlphaStream/1.2"})
    try:
        with urllib.request.urlopen(req, context=_ssl_ctx(), timeout=35) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"msg": str(e), "data": []}


@st.cache_data(ttl=300)
def fetch_tx_near_month_series(days=45):
    end = datetime.now().date(); start = end - timedelta(days=days)
    j = finmind_fetch("TaiwanFuturesDaily","TX",start.isoformat(),end.isoformat())
    if j.get("msg") != "success" or not j.get("data"): return pd.DataFrame()
    raw = pd.DataFrame(j["data"])
    raw["volume"]           = pd.to_numeric(raw["volume"],           errors="coerce").fillna(0)
    raw["settlement_price"] = pd.to_numeric(raw["settlement_price"], errors="coerce")
    raw = raw[(raw["settlement_price"]>0)&(raw["volume"]>0)]
    if raw.empty: return pd.DataFrame()
    idx = raw.groupby("date")["volume"].idxmax()
    out = raw.loc[idx,["date","contract_date","settlement_price","volume","close"]].copy()
    out["date"] = pd.to_datetime(out["date"]).dt.tz_localize(None)
    return out.sort_values("date").reset_index(drop=True)


@st.cache_data(ttl=300)
def fetch_twii_series(days=45):
    df = yf.Ticker("^TWII").history(start=datetime.now().date()-timedelta(days=days+7))
    if df is None or df.empty: return pd.DataFrame()
    df = df.reset_index()
    col = "Date" if "Date" in df.columns else df.columns[0]
    df["date"]       = pd.to_datetime(df[col]).dt.tz_localize(None).dt.normalize()
    df["spot_close"] = df["Close"].astype(float)
    return df[["date","spot_close"]].sort_values("date")


def build_tw_macro_merge(fut_df, spot_df):
    if fut_df.empty or spot_df.empty: return pd.DataFrame()
    def _naive(s):
        s = pd.to_datetime(s)
        if s.dt.tz is not None: s = s.dt.tz_convert("UTC").dt.tz_localize(None)
        return s.dt.normalize()
    f2 = fut_df.copy();  f2["date"]  = _naive(f2["date"])
    s2 = spot_df.copy(); s2["date"]  = _naive(s2["date"])
    m = pd.merge(f2, s2, on="date", how="inner")
    if m.empty: return pd.DataFrame()
    m["fut_settle"] = m["settlement_price"].astype(float)
    m["basis"]      = m["fut_settle"] - m["spot_close"]
    m["basis_pct"]  = m["basis"] / m["spot_close"] * 100.0
    return m


def interpret_tw_macro(merged):
    out = {"ok":False,"text":"無法取得大盤或台指期資料。","bias_class":"neutral","latest":None,"merged":merged}
    if merged is None or merged.empty: return out
    last = merged.iloc[-1]; bp = float(last["basis_pct"])
    if   bp >  0.12: bias,bcls="偏多（正向價差）","positive"; hint="期貨高於現貨加權，市場對後市相對樂觀。"
    elif bp < -0.12: bias,bcls="偏空／保守（逆價差）","negative"; hint="期貨低於現貨（逆價差），保守預期或短線調節。"
    else:            bias,bcls="中性（期現貨接近）","neutral";   hint="價差不大，未呈現明顯訊號。"
    trend_note = ""
    if len(merged)>=6:
        rec = merged.tail(5)["basis_pct"].mean()
        pri = merged.iloc[-10:-5]["basis_pct"].mean() if len(merged)>=10 else None
        if pri is not None:
            if   rec>pri+0.05: trend_note="近五日平均價差擴張，正向情緒略增溫。"
            elif rec<pri-0.05: trend_note="近五日平均價差收斂或轉負，保守意味略升。"
    out.update({"ok":True,"bias_class":bcls,"latest":last,"text":f"{bias} — {hint} {trend_note}".strip()})
    return out


def build_tw_macro_chart(merged):
    C={"bg":"#0a0e1a","paper":"#0d1220","grid":"#1a2d42","txt":"#8ba7c4","acc":"#00d4ff"}
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged["date"],y=merged["spot_close"],name="加權指數 ^TWII",line=dict(color="#00d4ff",width=2)))
    fig.add_trace(go.Scatter(x=merged["date"],y=merged["fut_settle"],name="台指期 TX（近月）",line=dict(color="#ffcc55",width=2)))
    fig.update_layout(height=420,plot_bgcolor=C["bg"],paper_bgcolor=C["paper"],
        font=dict(family="Space Mono, monospace",color=C["txt"],size=13),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        margin=dict(l=0,r=0,t=40,b=0),
        xaxis=dict(gridcolor=C["grid"],showgrid=True),
        yaxis=dict(gridcolor=C["grid"],showgrid=True,tickformat=","),
        title=dict(text="大盤現貨 vs 台指期（近月）",font=dict(size=15,color=C["acc"]),x=0.01))
    return fig


@st.cache_data(ttl=600)
def fetch_institutional_finmind(stock_id, days=20):
    end = datetime.now().date(); start = end - timedelta(days=days+10)
    j = finmind_fetch("TaiwanStockInstitutionalInvestorsBuySell",stock_id,start.isoformat(),end.isoformat())
    if j.get("msg")!="success" or not j.get("data"): return pd.DataFrame()
    return pd.DataFrame(j["data"])


def pivot_institutional_daily(inst):
    if inst.empty: return inst
    rows=[]
    for d,g in inst.groupby("date"):
        nets={}
        for _,r in g.iterrows():
            buy  = int(float(r["buy"]))  if pd.notna(r["buy"])  else 0
            sell = int(float(r["sell"])) if pd.notna(r["sell"]) else 0
            nets[str(r["name"])] = buy-sell
        fo=nets.get("Foreign_Investor",0); tr=nets.get("Investment_Trust",0)
        de=nets.get("Dealer_self",0)+nets.get("Dealer_Hedging",0)
        rows.append({"date":pd.to_datetime(d),"外資淨額（股）":fo,"投信淨額（股）":tr,"自營商淨額（股）":de,"三大法人淨額（股）":fo+tr+de})
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def compute_chip_score(daily):
    reasons=[]
    if daily.empty: return 0.0,["尚無法人買賣資料。"]
    tail=daily.tail(5); sum5=int(tail["三大法人淨額（股）"].sum()); last_net=int(daily.iloc[-1]["三大法人淨額（股）"])
    mag=max(0,min(5,int(math.log10(abs(sum5)+10)-2))) if sum5!=0 else 0
    if   sum5>0: chip=2+mag;  reasons.append(f"近5日三大法人累計淨買超 {sum5:+,} 股，籌碼偏多。")
    elif sum5<0: chip=-(2+mag);reasons.append(f"近5日三大法人累計淨賣超 {sum5:+,} 股，籌碼偏空。")
    else:        chip=0;      reasons.append("近五日三大法人淨額接近零，籌碼中性。")
    if last_net>0:   reasons.append(f"最新一日三大法人淨買超 {last_net:+,} 股。")
    elif last_net<0: reasons.append(f"最新一日三大法人淨賣超 {last_net:+,} 股。")
    if   last_net>0 and sum5>0: chip=min(10,chip+1)
    elif last_net<0 and sum5<0: chip=max(-10,chip-1)
    return float(max(-10,min(10,chip))),reasons


def build_chip_bar_figure(daily):
    C={"bg":"#0a0e1a","paper":"#0d1220","grid":"#1a2d42","txt":"#8ba7c4","acc":"#00d4ff"}
    fig=go.Figure()
    x=daily["date"]
    fig.add_trace(go.Bar(x=x,y=daily["外資淨額（股）"],   name="外資",   marker_color="#00d4ff"))
    fig.add_trace(go.Bar(x=x,y=daily["投信淨額（股）"],   name="投信",   marker_color="#ffcc55"))
    fig.add_trace(go.Bar(x=x,y=daily["自營商淨額（股）"], name="自營商", marker_color="#aa88ff"))
    fig.update_layout(barmode="relative",height=400,plot_bgcolor=C["bg"],paper_bgcolor=C["paper"],
        font=dict(family="Space Mono, monospace",color=C["txt"],size=12),
        legend=dict(orientation="h",y=1.02,x=1,xanchor="right",yanchor="bottom"),
        margin=dict(l=0,r=0,t=36,b=0),
        title=dict(text="三大法人買賣超（股）",font=dict(size=14,color=C["acc"]),x=0.01),
        xaxis=dict(gridcolor=C["grid"]),yaxis=dict(gridcolor=C["grid"],tickformat=","))
    return fig


def summarize_chip(daily):
    if daily.empty: return []
    results=[]
    for label,col in [("外資","外資淨額（股）"),("投信","投信淨額（股）"),("自營商","自營商淨額（股）")]:
        tail=list(reversed(daily.tail(10)[col].tolist()))
        if not tail: results.append({"name":label,"streak_text":"無資料","net5":0}); continue
        direction=1 if tail[0]>0 else (-1 if tail[0]<0 else 0)
        count=0
        for v in tail:
            if (direction==1 and v>0) or (direction==-1 and v<0): count+=1
            else: break
        net5=int(sum(daily.tail(5)[col]))
        if   direction==1  and count>=2: streak="連續 "+str(count)+" 日<b style='color:#00e896'>買超</b>"
        elif direction==-1 and count>=2: streak="連續 "+str(count)+" 日<b style='color:#ff6b8a'>賣超</b>"
        elif direction==1:               streak="最新一日<b style='color:#00e896'>買超</b>"
        elif direction==-1:              streak="最新一日<b style='color:#ff6b8a'>賣超</b>"
        else:                            streak="無明顯方向"
        results.append({"name":label,"streak_text":streak,"net5":net5})
    return results


# ═══════════════════════════════════════════
# MODULE 2: INDICATORS
# ═══════════════════════════════════════════

def compute_indicators(df):
    if df.empty or len(df)<30: return df
    c=df["Close"]
    df["MA20"]=c.rolling(20).mean(); df["MA50"]=c.rolling(50).mean(); df["MA200"]=c.rolling(200).mean()
    e12=c.ewm(span=12,adjust=False).mean(); e26=c.ewm(span=26,adjust=False).mean()
    df["MACD"]=e12-e26; df["MACD_Signal"]=df["MACD"].ewm(span=9,adjust=False).mean(); df["MACD_Hist"]=df["MACD"]-df["MACD_Signal"]
    d=c.diff(); ag=d.clip(lower=0).ewm(com=13,adjust=False).mean(); al=(-d).clip(lower=0).ewm(com=13,adjust=False).mean()
    df["RSI"]=100-(100/(1+ag/al.replace(0,float("nan"))))
    lmin=df["Low"].rolling(9).min(); hmax=df["High"].rolling(9).max()
    rsv=(c-lmin)/(hmax-lmin+1e-9)*100
    df["K"]=rsv.ewm(com=2,adjust=False).mean(); df["D"]=df["K"].ewm(com=2,adjust=False).mean()
    s20=c.rolling(20).std(); df["BB_Mid"]=df["MA20"]; df["BB_Up"]=df["MA20"]+2*s20; df["BB_Lo"]=df["MA20"]-2*s20
    return df


def get_technical_signals(df):
    if df.empty: return {}
    last=df.iloc[-1]; prev=df.iloc[-2] if len(df)>1 else last
    sig={}
    rsi=last.get("RSI",50)
    if isinstance(rsi,float):
        if   rsi>=70: sig["rsi"]=("超買","negative",rsi)
        elif rsi<=30: sig["rsi"]=("超賣","positive",rsi)
        else:         sig["rsi"]=("中性","neutral",rsi)
    mn,sn=last.get("MACD",0),last.get("MACD_Signal",0)
    mp,sp=prev.get("MACD",0),prev.get("MACD_Signal",0)
    if   mn>sn and mp<=sp: sig["macd"]=("黃金交叉","positive")
    elif mn<sn and mp>=sp: sig["macd"]=("死亡交叉","negative")
    elif mn>sn:            sig["macd"]=("多頭排列","positive")
    else:                  sig["macd"]=("空頭排列","negative")
    cl=last.get("Close",0)
    sig["ma_trend"]=sum([bool(cl>last.get("MA20")) if last.get("MA20") else False,
                         bool(cl>last.get("MA50")) if last.get("MA50") else False,
                         bool(cl>last.get("MA200")) if last.get("MA200") else False])
    return sig


# ═══════════════════════════════════════════
# MODULE 3: ALPHAINSIGHT AI
# ═══════════════════════════════════════════

def compute_alphainsight(df, fundamentals, chip_daily):
    score=0
    bd={"趨勢 Trend":0,"動能 Momentum":0,"價值 Value":0,"籌碼 Chips":0}

    def fv(x):
        try: v=float(x); return None if v!=v else v
        except: return None

    if not df.empty and len(df)>=2:
        last=df.iloc[-1]; prev=df.iloc[-2]

        # Trend: 收盤 > MA20
        cl=fv(last.get("Close")); ma20=fv(last.get("MA20"))
        if cl is not None and ma20 is not None:
            t=1 if cl>ma20 else -1; bd["趨勢 Trend"]+=t; score+=t

        # Momentum: KD超賣 / MACD紅柱增加
        k=fv(last.get("K"))
        if k is not None:
            if   k<20: bd["動能 Momentum"]+=1; score+=1
            elif k>80: bd["動能 Momentum"]-=1; score-=1
        hn=fv(last.get("MACD_Hist")); hp=fv(prev.get("MACD_Hist"))
        if hn is not None and hp is not None and hn>0 and hn>hp:
            bd["動能 Momentum"]+=1; score+=1

        # Value: PE / ROE
        pe=fv(fundamentals.get("pe_ratio","N/A"))
        if pe is not None:
            if   pe<15: bd["價值 Value"]+=1; score+=1
            elif pe>40: bd["價值 Value"]-=1; score-=1
        try:
            roe=float(str(fundamentals.get("roe","N/A")).replace("%",""))
            if roe>10: bd["價值 Value"]+=1; score+=1
        except: pass

        # Chips
        if not chip_daily.empty:
            last_net=int(chip_daily.iloc[-1]["三大法人淨額（股）"])
            sum5=int(chip_daily.tail(5)["三大法人淨額（股）"].sum())
            if last_net>0: bd["籌碼 Chips"]+=1; score+=1
            if sum5<0:     bd["籌碼 Chips"]-=1; score-=1

    if   score>=2: verdict,cls,icon="強勢偏多 — 建議分批佈局","bullish","🟢"
    elif score>=0: verdict,cls,icon="中性觀望 — 等待趨勢確認","neutral","🟡"
    else:          verdict,cls,icon="弱勢偏空 — 建議減倉避險","bearish","🔴"

    rsi_v=fv(df.iloc[-1].get("RSI")) if not df.empty else None
    pe_v=fv(fundamentals.get("pe_ratio","N/A"))
    chip_hint=""
    if not chip_daily.empty:
        ln=int(chip_daily.iloc[-1]["三大法人淨額（股）"])
        chip_hint="法人最新一日淨買超，籌碼面支撐。" if ln>0 else "法人最新一日淨賣超，籌碼面偏空。"
    rsi_hint=""
    if rsi_v is not None:
        if   rsi_v>=70: rsi_hint=f"RSI={rsi_v:.0f} 已進入超買區，短線追價需謹慎。"
        elif rsi_v<=30: rsi_hint=f"RSI={rsi_v:.0f} 跌入超賣區，留意技術反彈機會。"
        else:           rsi_hint=f"RSI={rsi_v:.0f} 處於中性區間，動能無極端訊號。"
    pe_hint=""
    if pe_v is not None:
        if   pe_v<15: pe_hint=f"本益比 {pe_v:.1f} 偏低，估值具安全邊際。"
        elif pe_v>40: pe_hint=f"本益比 {pe_v:.1f} 偏高，留意估值修正風險。"
        else:         pe_hint=f"本益比 {pe_v:.1f} 合理，估值中性。"
    comment=" ".join(filter(None,[rsi_hint,pe_hint,chip_hint])) or "數據尚不完整，待各指標就緒後再判讀。"

    return {"score":score,"verdict":verdict,"cls":cls,"icon":icon,"comment":comment,"breakdown":bd}


def render_alphainsight_banner(insight):
    cls=insight["cls"]; score=insight["score"]
    pills=""
    for dim,val in insight["breakdown"].items():
        if   val>0: pcls="pill-pos"; sign="+"
        elif val<0: pcls="pill-neg"; sign=""
        else:       pcls="pill-neu"; sign=""
        pills+='<span class="insight-score-pill '+pcls+'">'+dim+" "+sign+str(val)+"</span>"
    total_sign="+" if score>0 else ""
    html=(
        '<div class="insight-banner '+cls+'">'
        '<div class="insight-title '+cls+'">'+insight["icon"]+"  "+insight["verdict"]
        +'<span style="font-size:1rem;color:#6a8aaa;margin-left:18px;font-weight:400;">總分 '+total_sign+str(score)+"</span></div>"
        '<div class="insight-comment">'+insight["comment"]+"</div>"
        '<div class="insight-scores">'+pills+"</div></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# MODULE 4: CHART
# ═══════════════════════════════════════════

CL={
    "bg":"#0a0e1a","paper":"#0d1220","grid":"#1a2d42","text":"#8ba7c4",
    "cup":"#ff4466","cdn":"#00e896","ma20":"#00d4ff","ma50":"#ffcc00","ma200":"#ff6699","bb":"#3a6080",
    "macd":"#00d4ff","sig":"#ffcc00","hp":"#ff4466","hn":"#00e896",
    "rsi":"#cc88ff","kl":"#ff9944","dl":"#aa88ff",
    "vu":"rgba(255,68,102,0.4)","vd":"rgba(0,232,150,0.4)",
}

def build_chart(df, ticker):
    fig=make_subplots(rows=4,cols=1,shared_xaxes=True,vertical_spacing=0.025,
                      row_heights=[0.52,0.14,0.17,0.17],subplot_titles=("","Volume","MACD","RSI & KD"))
    fig.add_trace(go.Candlestick(x=df.index,open=df["Open"],high=df["High"],low=df["Low"],close=df["Close"],
        name="OHLC",increasing_line_color=CL["cup"],decreasing_line_color=CL["cdn"],
        increasing_fillcolor=CL["cup"],decreasing_fillcolor=CL["cdn"],line_width=1),row=1,col=1)
    for c,col,n in [("MA20",CL["ma20"],"MA 20"),("MA50",CL["ma50"],"MA 50"),("MA200",CL["ma200"],"MA 200")]:
        if c in df.columns:
            fig.add_trace(go.Scatter(x=df.index,y=df[c],name=n,line=dict(color=col,width=1.5),opacity=0.85),row=1,col=1)
    if "BB_Up" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["BB_Up"],name="BB Upper",line=dict(color=CL["bb"],width=1,dash="dot"),opacity=0.6),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["BB_Lo"],name="BB Lower",line=dict(color=CL["bb"],width=1,dash="dot"),fill="tonexty",fillcolor="rgba(58,96,128,0.08)",opacity=0.6),row=1,col=1)
    vc=[CL["vu"] if c>=o else CL["vd"] for c,o in zip(df["Close"],df["Open"])]
    fig.add_trace(go.Bar(x=df.index,y=df["Volume"],name="Volume",marker_color=vc,showlegend=False),row=2,col=1)
    if "MACD" in df.columns:
        hc=[CL["hp"] if v>=0 else CL["hn"] for v in df["MACD_Hist"].fillna(0)]
        fig.add_trace(go.Bar(x=df.index,y=df["MACD_Hist"],name="Histogram",marker_color=hc,showlegend=False),row=3,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["MACD"],name="MACD",line=dict(color=CL["macd"],width=1.5)),row=3,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["MACD_Signal"],name="Signal",line=dict(color=CL["sig"],width=1.5,dash="dash")),row=3,col=1)
    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["RSI"],name="RSI",line=dict(color=CL["rsi"],width=1.5)),row=4,col=1)
        for l,d in [(70,"dot"),(50,"longdash"),(30,"dot")]:
            fig.add_hline(y=l,line_dash=d,line_color=CL["grid"],line_width=1,row=4,col=1)
    if "K" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["K"],name="K",line=dict(color=CL["kl"],width=1.5)),row=4,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["D"],name="D",line=dict(color=CL["dl"],width=1.5,dash="dash")),row=4,col=1)
        for l in [80,20]: fig.add_hline(y=l,line_dash="dot",line_color="#2a4060",line_width=1,row=4,col=1)
    fig.update_layout(height=860,plot_bgcolor=CL["bg"],paper_bgcolor=CL["paper"],
        font=dict(family="Space Mono, monospace",color=CL["text"],size=14),
        xaxis_rangeslider_visible=False,
        legend=dict(bgcolor="rgba(0,0,0,0)",bordercolor=CL["grid"],borderwidth=1,font=dict(size=12)),
        margin=dict(l=0,r=0,t=36,b=0),hovermode="x unified",
        hoverlabel=dict(bgcolor="#0d1220",bordercolor=CL["grid"],font=dict(family="Space Mono",size=13)),
        title=dict(text="<b>"+ticker+"</b>  Interactive Chart",font=dict(size=17,color=CL["ma20"]),x=0.01))
    for i in range(1,5):
        fig.update_xaxes(gridcolor=CL["grid"],gridwidth=1,showgrid=True,zeroline=False,row=i,col=1)
        fig.update_yaxes(gridcolor=CL["grid"],gridwidth=1,showgrid=True,zeroline=False,row=i,col=1)
    return fig


# ═══════════════════════════════════════════
# MODULE 5: DECISION ENGINE
# ═══════════════════════════════════════════

def compute_decision(df, fundamentals, chip_score=None, chip_reasons=None):
    reasons=[]; ts=0; fs=0; chip_reasons=chip_reasons or []
    sig=get_technical_signals(df) if not df.empty else {}

    rd=sig.get("rsi")
    if rd:
        _,tone,val=rd
        if   tone=="positive": ts+=4; reasons.append(f"RSI={val:.1f} 超賣區（≤30），偏多")
        elif tone=="negative": ts-=3; reasons.append(f"RSI={val:.1f} 超買區（≥70），偏保守")
        else: reasons.append(f"RSI={val:.1f} 中性區（30～70）")

    md=sig.get("macd")
    if md:
        lbl,tone=md; d=3 if "交叉" in lbl else 2
        ts+=d if tone=="positive" else -d; reasons.append(f"MACD {lbl}")

    mc=sig.get("ma_trend",1)
    if   mc==3: ts+=3; reasons.append("收盤站上 MA20/50/200，強勢多頭")
    elif mc==2: ts+=1; reasons.append("收盤站上兩條均線，偏多")
    elif mc==0: ts-=3; reasons.append("收盤跌破三條均線，偏空")

    if not df.empty and "K" in df.columns and len(df)>1:
        l=df.iloc[-1]; p=df.iloc[-2]
        try:
            kf=float(l.get("K")); df2=float(l.get("D")); kp=float(p.get("K")); dp=float(p.get("D"))
            if   kf>df2 and kp<=dp: ts+=2; reasons.append("KD 黃金交叉，偏多")
            elif kf<df2 and kp>=dp: ts-=2; reasons.append("KD 死亡交叉，偏空")
            elif kf<=20: ts+=1; reasons.append(f"KD K={kf:.1f} 超賣，關注反彈")
            elif kf>=80: ts-=1; reasons.append(f"KD K={kf:.1f} 超買，注意回檔")
        except: pass

    ts=max(-10,min(10,ts))

    try:
        pe=float(fundamentals.get("pe_ratio","N/A"))
        if   pe<0:  fs-=3; reasons.append(f"PE={pe:.1f} 虧損中")
        elif pe<15: fs+=4; reasons.append(f"PE={pe:.1f} 低估值")
        elif pe<25: fs+=2; reasons.append(f"PE={pe:.1f} 合理估值")
        elif pe<40: fs-=1; reasons.append(f"PE={pe:.1f} 略高估值")
        else:       fs-=3; reasons.append(f"PE={pe:.1f} 高估值，注意下修")
    except: reasons.append("PE 數據不可用")

    try:
        rv=float(str(fundamentals.get("roe","N/A")).replace("%",""))
        if   rv>20: fs+=3; reasons.append(f"ROE={rv:.1f}% 優質盈利能力")
        elif rv>10: fs+=1; reasons.append(f"ROE={rv:.1f}% 一般盈利能力")
        else:       fs-=1; reasons.append(f"ROE={rv:.1f}% 盈利能力偏弱")
    except: pass

    try:
        dv=float(str(fundamentals.get("div_yield","N/A")).replace("%",""))
        if   dv>=3: fs+=2; reasons.append(f"殖利率={dv:.2f}% 高股息")
        elif dv>0:  fs+=1
    except: pass

    fs=max(-10,min(10,fs))
    for cr in chip_reasons: reasons.append("籌碼："+cr)

    if chip_score is None:
        comp=ts*(40/75)+fs*(35/75)
    else:
        comp=ts*0.40+fs*0.35+max(-10,min(10,float(chip_score)))*0.25

    if   comp>=4.5: sig2,scls="強力買入","signal-strong-buy"
    elif comp>=2.0: sig2,scls="買入","signal-buy"
    elif comp>=-1.0:sig2,scls="持有","signal-hold"
    elif comp>=-3.0:sig2,scls="觀望","signal-watch"
    else:           sig2,scls="賣出","signal-sell"

    return {"signal":sig2,"signal_class":scls,"composite":round(comp,2),
            "tech_score":ts,"fund_score":fs,"reasons":reasons,"chip_score":chip_score}


# ═══════════════════════════════════════════
# HTML HELPERS
# ═══════════════════════════════════════════

def fmt_market_cap(val):
    if val is None or val=="N/A": return "N/A"
    try:
        v=float(val)
        if v>=1e12: return f"{v/1e12:.2f}T"
        if v>=1e9:  return f"{v/1e9:.2f}B"
        if v>=1e6:  return f"{v/1e6:.2f}M"
        return f"{v:,.0f}"
    except: return "N/A"


def score_to_bar(score, mx=10):
    pct=max(0,min(100,(score+mx)/(2*mx)*100))
    color="#00e896" if score>=2 else ("#ffcc00" if score>=-1 else "#ff4466")
    sign="+" if score>=0 else ""
    return (
        '<div class="score-row">'
        '<div class="score-bar-bg"><div class="score-bar-fill" style="width:'+str(round(pct,1))+'%;background:'+color+';"></div></div>'
        '<div class="score-num">'+sign+str(round(score,1))+'</div>'
        '</div>'
    )


def kpi_dashboard_html(df, fundamentals):
    if df.empty: return ""
    last=df.iloc[-1]; prev=df.iloc[-2] if len(df)>1 else last
    def fv(x,nd=2):
        try: v=float(x); return None if v!=v else round(v,nd)
        except: return None

    cl=fv(last.get("Close")); pv=fv(prev.get("Close"))
    rsi=fv(last.get("RSI"),1); k=fv(last.get("K"),1); ma20=fv(last.get("MA20"))
    vol=last.get("Volume"); cur=fundamentals.get("currency","USD")

    if cl and pv:
        chg=cl-pv; pct=chg/pv*100; sgn="+" if chg>=0 else ""
        pc="#ff4466" if chg>=0 else "#00e896"
        chg_s=sgn+str(round(chg,2))+" ("+sgn+str(round(pct,2))+"%)"
    else: pc="#e8f4ff"; chg_s="—"

    if rsi is not None:
        if   rsi>=70: rc,rl="#ff6b8a","超買"
        elif rsi<=30: rc,rl="#00e896","超賣"
        else:         rc,rl="#ffcc55","中性"
        rs=str(round(rsi,1))
    else: rc,rl,rs="#8ba7c4","N/A","N/A"

    if k is not None:
        if   k>=80: kc,kl="#ff6b8a","超買"
        elif k<=20: kc,kl="#00e896","超賣"
        else:       kc,kl="#ffcc55","中性"
        ks=str(round(k,1))
    else: kc,kl,ks="#8ba7c4","N/A","N/A"

    if ma20 and cl and isinstance(cl,float):
        diff=cl-ma20; dp=diff/ma20*100; s2="+" if diff>=0 else ""
        mc="#ff4466" if diff>=0 else "#00e896"
        ml="站上 MA20" if diff>=0 else "跌破 MA20"
        ms=s2+str(round(dp,2))+"% vs MA20="+str(round(ma20,2))
    else: mc,ml,ms="#8ba7c4","N/A","—"

    vs=f"{int(vol):,}" if vol and vol!="N/A" else "N/A"

    def card(lbl,val_h,sub_h="",unit_h=""):
        return (
            '<div class="kpi-card"><div class="kpi-label">'+lbl+'</div>'
            '<div class="kpi-value">'+val_h+unit_h+'</div>'
            +('<div class="kpi-sub">'+sub_h+'</div>' if sub_h else '')
            +'</div>'
        )

    cl_s=f"{cl:,.2f}" if isinstance(cl,float) else "N/A"
    uspan='<span style="font-size:0.75rem;color:#5a7a9a;margin-left:4px;">'+cur+'</span>'
    return (
        '<div class="kpi-grid">'
        +card("最新收盤",cl_s,'<span style="color:'+pc+';">'+chg_s+'</span>',uspan)
        +card("RSI (14)",rs,'<span style="color:'+rc+';">'+rl+'</span>')
        +card("KD — K 值",ks,'<span style="color:'+kc+';">'+kl+'</span>')
        +card("MA20 位置",'<span style="color:'+mc+';">'+ml+'</span>','<span style="color:'+mc+';font-size:0.85rem;">'+ms+'</span>')
        +card("成交量",vs)
        +'</div>'
    )


def kd_status_html(df):
    if df.empty or "K" not in df.columns: return '<p style="color:#6a8aaa;">KD 尚未就緒。</p>'
    last=df.iloc[-1]; prev=df.iloc[-2] if len(df)>1 else last
    def fv(x):
        try: v=float(x); return None if v!=v else round(v,1)
        except: return None
    k=fv(last.get("K")); d=fv(last.get("D")); kp=fv(prev.get("K")); dp=fv(prev.get("D"))
    if k is None or d is None: return '<p style="color:#6a8aaa;">KD 值尚無資料。</p>'
    if   k>=80: st2,scls,ico="超買區（K≥80）","kd-overbought","🔴"
    elif k<=20: st2,scls,ico="超賣區（K≤20）","kd-oversold","🟢"
    else:       st2,scls,ico="中性區間","kd-neutral","🟡"
    cross=""
    if kp is not None and dp is not None:
        if   k>d and kp<=dp: cross='<span class="kd-badge kd-oversold" style="font-size:0.82rem;">▲ 黃金交叉</span>'
        elif k<d and kp>=dp: cross='<span class="kd-badge kd-overbought" style="font-size:0.82rem;">▼ 死亡交叉</span>'
    def bc(v): return "#ff4466" if v>=80 else ("#00e896" if v<=20 else "#ffcc55")
    def bar(lbl,val):
        pct=str(round(min(100,max(0,val)),1)); c=bc(val)
        return (
            '<div class="kd-bar-wrap"><div class="kd-bar-label"><span>'+lbl+'</span>'
            '<span style="color:'+c+';font-weight:700;">'+str(round(val,1))+'</span></div>'
            '<div class="kd-bar-track"><div class="kd-bar-fill" style="width:'+pct+'%;background:'+c+';"></div>'
            '<div class="kd-zone-mark" style="left:20%;"></div>'
            '<div class="kd-zone-mark" style="left:80%;"></div></div></div>'
        )
    badge='<div style="margin-bottom:10px;"><span class="kd-badge '+scls+'">'+ico+' '+st2+'</span>'+cross+'</div>'
    hint='<div style="font-size:0.88rem;color:#5a7a9a;margin-top:10px;line-height:1.6;"><b style="color:#8ba7c4;">怎麼看：</b> K≥80 超買、K≤20 超賣。K 上穿 D 黃金交叉（偏多）；K 下穿 D 死亡交叉（偏空）。採 9 日 KD。</div>'
    return badge+bar("K 值（快線）",k)+bar("D 值（慢線）",d)+hint


def technical_digest_html(df):
    if df.empty or len(df)<2: return '<p style="color:#6a8aaa;font-size:1.05rem;">資料不足，無法解讀技術指標。</p>'
    last=df.iloc[-1]; prev=df.iloc[-2]
    def fv(x,nd=4):
        try: v=float(x); return None if v!=v else round(v,nd)
        except: return None

    rv=fv(last.get("RSI"),1)
    if rv is None:
        rc='<div class="dash-card"><div class="dash-card-title">RSI (14)</div><p class="tech-threshold">尚無有效 RSI 數值。</p></div>'
    else:
        if   rv>=70: vc,vt="negative","偏短線過熱（超買）"
        elif rv<=30: vc,vt="positive","跌深反彈契機（超賣）"
        else:        vc,vt="neutral","中性區間"
        rc=(
            '<div class="dash-card"><div class="dash-card-title">RSI (14)</div>'
            '<div class="tech-big-num">RSI = '+str(round(rv,1))+'</div>'
            '<div class="tech-verdict '+vc+'">'+vt+'</div>'
            '<div class="tech-threshold"><b>怎麼看：</b>RSI <b>70+</b> 超買；<b>30-</b> 超賣；<b>30～70</b> 中性。</div></div>'
        )

    m=fv(last.get("MACD"),4); s=fv(last.get("MACD_Signal"),4); h=fv(last.get("MACD_Hist"),4)
    mp=fv(prev.get("MACD"),4); sp=fv(prev.get("MACD_Signal"),4)
    if m is None or s is None or h is None:
        mc='<div class="dash-card"><div class="dash-card-title">MACD (12,26,9)</div><p class="tech-threshold">尚無有效 MACD 數值。</p></div>'
    else:
        cross=""
        if mp is not None and sp is not None:
            if   m>s and mp<=sp: cross="本棒出現 <b>黃金交叉</b>（MACD 上穿訊號線），動能轉多。"
            elif m<s and mp>=sp: cross="本棒出現 <b>死亡交叉</b>（MACD 下穿訊號線），動能轉空。"
        vc="positive" if h>0 else ("negative" if h<0 else "neutral")
        vt="柱狀為正（偏多動能）" if h>0 else ("柱狀為負（偏空動能）" if h<0 else "接近零軸")
        hs="+" if h>=0 else ""; cp=(" — "+cross) if cross else ""
        mc=(
            '<div class="dash-card"><div class="dash-card-title">MACD (12, 26, 9)</div>'
            '<div class="tech-big-num" style="font-size:1.35rem;">MACD='+str(round(m,4))+' ｜ Signal='+str(round(s,4))+'</div>'
            '<div class="tech-verdict '+vc+'">'+vt+'</div>'
            '<div class="tech-threshold">Hist=<b>'+hs+str(round(h,4))+'</b>'+cp+'</div></div>'
        )

    cl=fv(last.get("Close"),2); ma20=fv(last.get("MA20"),2)
    ma50=fv(last.get("MA50"),2); ma200=fv(last.get("MA200"),2)
    bu=fv(last.get("BB_Up"),2); bl=fv(last.get("BB_Lo"),2)
    lines=[]
    if cl: lines.append("收盤 <b>"+str(round(cl,2))+"</b>")
    if all(x is not None for x in (cl,bu,bl)):
        if   cl>=bu: pos="貼近<b>上軌</b>，注意過熱回檔。"
        elif cl<=bl: pos="觸及<b>下軌</b>，關注超賣反彈。"
        else:        pos="介於上下軌之間，常態波動。"
        lines.append("布林：上軌 "+str(round(bu,2))+" ／ 下軌 "+str(round(bl,2))+" — "+pos)
    mps=[lbl+"="+str(round(mv,2))+"（"+("站上" if cl>mv else "站下")+"）"
         for lbl,mv in [("MA20",ma20),("MA50",ma50),("MA200",ma200)] if mv and cl]
    if mps: lines.append("均線：" + "；".join(mps) + "。")
    lh="<br><br>".join(lines) if lines else "指標尚未就緒。"
    tc=(
        '<div class="dash-card"><div class="dash-card-title">價格 · 布林 · 均線</div>'
        '<div class="tech-threshold" style="border-top:none;padding-top:0;font-size:1.05rem;">'+lh+'</div></div>'
    )
    return '<div class="tech-grid">'+rc+mc+tc+'</div>'


# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════

with st.sidebar:
    st.markdown(
        '<div style="font-family:Space Mono,monospace;font-size:1.55rem;font-weight:700;color:#00d4ff;letter-spacing:0.12em;margin-bottom:0.25rem;">'
        '📈 ALPHA<span style="color:#ff6b8a;">STREAM</span></div>'
        '<div style="font-family:Space Mono,monospace;font-size:0.82rem;color:#5a7a9a;letter-spacing:0.22em;margin-bottom:0.25rem;">QUANT ANALYSIS TERMINAL</div>'
        '<div style="font-family:Space Mono,monospace;font-size:0.80rem;color:#00d4ff;letter-spacing:0.1em;margin-bottom:1.5rem;">當前系統版本：'+CURRENT_VERSION+'</div>',
        unsafe_allow_html=True,
    )

    tw_labels  = [i[0] for i in TW_POPULAR]
    tw_tickers = {i[0]:i[1] for i in TW_POPULAR}
    sel_lbl    = st.selectbox("熱門台股快選", tw_labels, index=0)
    sel_pre    = tw_tickers[sel_lbl]

    if sel_pre == "__manual__":
        ticker_input = st.text_input("TICKER SYMBOL", value="AAPL", placeholder="e.g. AAPL / 2330.TW").strip().upper()
    else:
        ticker_input = sel_pre
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.88rem;color:#00d4ff;margin-top:4px;margin-bottom:8px;">▶ '+ticker_input+'</div>', unsafe_allow_html=True)

    period_map   = {"1 個月":"1mo","3 個月":"3mo","6 個月":"6mo","1 年":"1y","2 年":"2y"}
    period_label = st.selectbox("分析週期", list(period_map.keys()), index=3)
    period       = period_map[period_label]

    st.markdown("---")
    run = st.button("🔍  開始分析", use_container_width=True)
    st.markdown("---")
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.82rem;color:#3a5080;line-height:1.75;letter-spacing:0.04em;">⚠ 本工具僅供學術研究與個人參考，不構成任何投資建議。<br><br>數據來源：Yahoo Finance · FinMind</div>', unsafe_allow_html=True)

    with st.sidebar.expander("📋 版本更新日誌"):
        for ver,date,desc in VERSION_HISTORY:
            st.markdown(
                '<div style="margin-bottom:10px;font-size:0.92rem;">'
                '<span style="font-family:Space Mono,monospace;color:#00d4ff;">'+ver+'</span>'
                '<span style="color:#5a7a9a;"> ('+date+')</span><br>'
                '<span style="color:#9bb8d4;">'+desc+'</span></div>',
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════

st.markdown(
    '<div class="alpha-header">📡 ALPHASTREAM</div>'
    '<div class="alpha-subtitle">Quantitative Stock Analysis Terminal · '+CURRENT_VERSION+'</div>',
    unsafe_allow_html=True,
)

if not run:
    st.markdown('<div style="text-align:center;padding:72px 0;color:#5a7a9a;font-family:Space Mono,monospace;font-size:1.25rem;letter-spacing:0.12em;">← 在左側選擇或輸入股票代號，點擊「開始分析」</div>', unsafe_allow_html=True)
    st.stop()

tw_stock_id: str | None       = None
chip_score_param: float | None = None
chip_reasons_param: list[str]  = []
chip_daily   = pd.DataFrame()
merged_macro = pd.DataFrame()
macro_ctx: dict = {"ok":False,"text":"尚未載入。"}

with st.spinner("載入中…"):
    df_raw       = fetch_price_history(ticker_input, period)
    fundamentals = fetch_fundamentals(ticker_input)
    company_name = resolve_display_name(ticker_input, fundamentals)
    fut_df       = fetch_tx_near_month_series(50)
    spot_df      = fetch_twii_series(50)
    merged_macro = build_tw_macro_merge(fut_df, spot_df)
    macro_ctx    = interpret_tw_macro(merged_macro)
    tw_stock_id  = parse_tw_stock_id(ticker_input)
    if tw_stock_id:
        inst_raw   = fetch_institutional_finmind(tw_stock_id, days=25)
        chip_daily = pivot_institutional_daily(inst_raw)
        if not chip_daily.empty:
            chip_score_param, chip_reasons_param = compute_chip_score(chip_daily)
        else:
            chip_reasons_param = ["FinMind 尚無此股近日三大法人買賣明細。"]

if df_raw.empty:
    st.error(f"找不到 **{ticker_input}** 的數據。台股請加 `.TW`，例如 `2330.TW`。")
    st.stop()

df       = compute_indicators(df_raw.copy())
decision = compute_decision(df, fundamentals, chip_score=chip_score_param,
                            chip_reasons=(chip_reasons_param if tw_stock_id else []))
insight  = compute_alphainsight(df, fundamentals, chip_daily)

# ── Section 0: AlphaInsight AI ──
st.markdown('<div class="section-header">🧠 AlphaInsight AI 綜合診斷</div>', unsafe_allow_html=True)
render_alphainsight_banner(insight)

# ── Section 1: 大盤 vs 台指期 ──
st.markdown('<div class="section-header">台股大盤 · 加權指數 vs 台指期（TX 近月）</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
if macro_ctx.get("ok") and macro_ctx.get("latest") is not None:
    lat=macro_ctx["latest"]; bcls=macro_ctx.get("bias_class","neutral")
    bt="偏多解讀" if bcls=="positive" else ("偏空／保守解讀" if bcls=="negative" else "中性解讀")
    bcolor="#00e896" if bcls=="positive" else ("#ff6b8a" if bcls=="negative" else "#ffcc55")
    ds=pd.Timestamp(lat["date"]).strftime("%Y-%m-%d")
    st.markdown(
        '<div style="font-size:1.15rem;line-height:1.7;color:#c5d8ec;margin-bottom:14px;">'
        '<b style="color:'+bcolor+';font-size:1.25rem;">'+bt+'</b> — '+macro_ctx["text"]+'</div>'
        '<div style="font-family:Space Mono,monospace;font-size:1.02rem;color:#8ba7c4;margin-bottom:8px;">'
        '資料日 <b>'+ds+'</b>｜加權收盤 <b>'+f"{float(lat['spot_close']):,.2f}"+'</b>'
        '｜台指期結算 <b>'+f"{float(lat['fut_settle']):,.2f}"+'</b>'
        '｜價差 <b>'+f"{float(lat['basis']):+,.2f}"+'</b>（<b>'+f"{float(lat['basis_pct']):+.3f}"+'%</b>）</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(build_tw_macro_chart(merged_macro), use_container_width=True, config={"displayModeBar":True})
else:
    st.warning(macro_ctx.get("text","無法載入大盤／期貨資料。"))
st.markdown("</div>", unsafe_allow_html=True)

# ── Section 2: 標題 + KPI ──
currency=fundamentals.get("currency","USD")
kpi_html=kpi_dashboard_html(df, fundamentals)
st.markdown(
    '<div class="dashboard-panel" style="margin-top:0;">'
    '<div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:12px;margin-bottom:0.4rem;">'
    '<div style="font-family:Space Mono,monospace;font-size:2.2rem;font-weight:700;color:#e8f4ff;">'+company_name+'</div>'
    '<div style="font-family:Space Mono,monospace;font-size:1.1rem;color:#4a7a9a;letter-spacing:0.1em;">'+ticker_input+'</div>'
    '</div>'
    '<div style="font-size:1.05rem;color:#6a8aaa;margin-bottom:1rem;">'
    +fundamentals.get("sector","—")+" &nbsp;·&nbsp; 市值 "+fmt_market_cap(fundamentals.get("market_cap"))+" &nbsp;·&nbsp; "+currency+
    '</div>'+kpi_html+'</div>',
    unsafe_allow_html=True,
)

# ── Section 3: 基本面 ──
st.markdown('<div class="section-header">基本面指標</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
cols=st.columns(6)
for col,(lbl,val) in zip(cols,[
    ("PE (TTM)",fundamentals.get("pe_ratio","N/A")),("Forward PE",fundamentals.get("forward_pe","N/A")),
    ("EPS",fundamentals.get("eps","N/A")),("ROE",fundamentals.get("roe","N/A")),
    ("殖利率",fundamentals.get("div_yield","N/A")),("Beta",fundamentals.get("beta","N/A")),
]):
    with col: st.metric(lbl,val)
cols2=st.columns(4)
for col,(lbl,val) in zip(cols2,[
    ("52W 高",fundamentals.get("52w_high","N/A")),("52W 低",fundamentals.get("52w_low","N/A")),
    ("毛利率",fundamentals.get("gross_margin","N/A")),
    ("成交量",f"{fundamentals.get('volume','N/A'):,}" if isinstance(fundamentals.get("volume"),int) else fundamentals.get("volume","N/A")),
]):
    with col: st.metric(lbl,val)
st.markdown("</div>", unsafe_allow_html=True)

# ── Section 4: 籌碼面 ──
if tw_stock_id:
    st.markdown('<div class="section-header">籌碼面 · 三大法人買賣超（FinMind）</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    st.caption(f"證券代號：**{tw_stock_id}**（單位：股；1 張 ≈ 1,000 股）")
    if not chip_daily.empty:
        sums=summarize_chip(chip_daily); rows_h=""
        for s in sums:
            net=s["net5"]; nc="pos" if net>0 else ("neg" if net<0 else "neu"); ns="+" if net>0 else ""
            rows_h+=('<div class="chip-summary-row"><div class="chip-name">'+s["name"]+'</div>'
                     '<div class="chip-streak">'+s["streak_text"]+'</div>'
                     '<div class="chip-net '+nc+'">近5日 '+ns+f"{net:,}"+' 股</div></div>')
        st.markdown('<div style="background:#070d18;border:1px solid #1e3555;border-radius:10px;padding:14px 20px;margin-bottom:16px;">'+rows_h+'</div>', unsafe_allow_html=True)
        st.plotly_chart(build_chip_bar_figure(chip_daily.tail(30)), use_container_width=True, config={"displayModeBar":True})
        with st.expander("📋 查看近期原始明細（近 12 個交易日）"):
            t=chip_daily.tail(12).iloc[::-1].copy()
            for c in t.columns:
                if "股" in c: t[c]=t[c].apply(lambda x:f"{int(x):+,}")
            t["date"]=t["date"].dt.strftime("%Y-%m-%d")
            st.dataframe(t, use_container_width=True, hide_index=True)
        if chip_score_param is not None:
            st.success(f"籌碼模型分數（納入綜合決策權重 25%）：**{chip_score_param:+.1f}**／10")
    else:
        st.info(chip_reasons_param[0] if chip_reasons_param else "尚無法人籌碼資料。")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Section 5: 圖表 ──
st.markdown('<div class="section-header">技術分析圖表</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-panel" style="padding-bottom:12px;">', unsafe_allow_html=True)
st.plotly_chart(build_chart(df, ticker_input), use_container_width=True, config={"displayModeBar":True})
st.markdown("</div>", unsafe_allow_html=True)

# ── Section 6: 技術解讀 + KD ──
st.markdown('<div class="section-header">技術指標解讀</div>', unsafe_allow_html=True)
_th=technical_digest_html(df); _kh=kd_status_html(df)
cl,cr=st.columns([3,2])
with cl:
    st.markdown('<div class="dashboard-panel" style="height:100%;">'+_th+'</div>', unsafe_allow_html=True)
with cr:
    st.markdown(
        '<div class="dashboard-panel" style="height:100%;">'
        '<div class="dash-card-title" style="font-family:Space Mono,monospace;font-size:0.78rem;color:#5a7a9a;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:12px;">KD 指標（9 日隨機）</div>'
        +_kh+'</div>',
        unsafe_allow_html=True,
    )

# ── Section 7: 綜合決策 ──
dt="綜合決策（技術 + 基本面 + 籌碼）" if decision.get("chip_score") is not None else "綜合決策（技術 + 基本面）"
st.markdown('<div class="section-header">'+dt+'</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
st.markdown('<div style="margin:0.5rem 0 1.2rem 0;"><span class="signal-badge '+decision["signal_class"]+'">'+decision["signal"]+'</span></div>', unsafe_allow_html=True)

if decision.get("chip_score") is None:
    si=[(f"技術面 ×{40/75*100:.1f}%",decision["tech_score"]),(f"基本面 ×{35/75*100:.1f}%",decision["fund_score"]),("綜合得分",decision["composite"])]
    fn="綜合評分 = 技術面×(40÷75) + 基本面×(35÷75)。單項約 -10～+10，僅供參考。"
else:
    si=[("技術面 ×40%",decision["tech_score"]),("基本面 ×35%",decision["fund_score"]),
        ("籌碼（法人）×25%",float(decision["chip_score"])),("綜合得分",decision["composite"])]
    fn="台股含籌碼：綜合 = 技術×40% + 基本面×35% + 籌碼×25%。籌碼依三大法人淨買賣超估算，僅供參考。"

for lbl,sc in si:
    st.markdown('<div class="score-row"><div class="score-label">'+lbl+'</div>'+score_to_bar(sc)+'</div>', unsafe_allow_html=True)

rh="".join('<div style="margin:6px 0;">• '+r+'</div>' for r in decision["reasons"])
st.markdown('<div class="ai-reasoning"><b>分析依據：</b><div style="margin-top:10px;">'+rh+'</div><div style="margin-top:14px;font-size:0.95rem;color:#5a7a9a;border-top:1px solid #243552;padding-top:12px;">'+fn+'</div></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ──
st.markdown(
    '<div style="margin-top:3rem;text-align:center;font-family:Space Mono,monospace;font-size:0.88rem;color:#3a5080;letter-spacing:0.1em;">'
    'ALPHASTREAM '+CURRENT_VERSION+' &nbsp;·&nbsp; 數據來源：Yahoo Finance · FinMind'
    ' &nbsp;·&nbsp; 最後更新：'+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+
    ' &nbsp;·&nbsp; ⚠ 本工具不構成投資建議</div>',
    unsafe_allow_html=True,
)
