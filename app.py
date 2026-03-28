"""
AlphaStream - 跨平台股票分析工具
Author: AlphaStream
Version: 1.0.0
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
    page_title="AlphaStream",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 17px;
}

.stApp {
    background: radial-gradient(ellipse 120% 80% at 20% -20%, #0f1a30 0%, #0a0e1a 45%);
    color: #d0e4f5;
}

.block-container {
    padding-top: 1.5rem !important;
    max-width: 1400px !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1220 0%, #0a0f18 100%);
    border-right: 1px solid #243552;
}
[data-testid="stSidebar"] * {
    color: #9bb8d4 !important;
    font-size: 1.02rem !important;
}
[data-testid="stSidebar"] .stMarkdown { font-size: 1rem !important; }

.alpha-header {
    font-family: 'Space Mono', monospace;
    font-size: 2.85rem;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 0.12em;
    text-shadow: 0 0 40px rgba(0,212,255,0.4);
    margin-bottom: 0.15rem;
}
.alpha-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    color: #4a6a8a;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    margin-bottom: 2.2rem;
}

.dashboard-panel {
    background: linear-gradient(145deg, rgba(15,24,37,0.95), rgba(10,14,26,0.98));
    border: 1px solid #243552;
    border-radius: 14px;
    padding: 22px 26px;
    margin: 1.25rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04);
}

.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    color: #00d4ff;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    border-bottom: 1px solid #2a4060;
    padding-bottom: 10px;
    margin: 2rem 0 1.1rem 0;
}

.tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 18px;
    margin-top: 8px;
}

.dash-card {
    background: #0c1524;
    border: 1px solid #1e3555;
    border-radius: 12px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}
.dash-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00d4ff, #0066cc, #8844ff);
}
.dash-card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #5a7a9a;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.tech-big-num {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: #e8f4ff;
    line-height: 1.1;
    margin-bottom: 6px;
}
.tech-verdict {
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 12px;
}
.tech-verdict.positive { color: #00e896; }
.tech-verdict.negative { color: #ff6b8a; }
.tech-verdict.neutral  { color: #ffcc55; }

.tech-threshold {
    font-size: 1.02rem;
    line-height: 1.65;
    color: #8ba7c4;
    border-top: 1px solid #1e3555;
    padding-top: 12px;
}
.tech-threshold b { color: #c5d8ec; }

.signal-badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 1.35rem;
    font-weight: 700;
    padding: 14px 32px;
    border-radius: 8px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 0.5rem 0;
}
.signal-strong-buy  { background: #003322; color: #00ff99; border: 1px solid #00ff99; }
.signal-buy         { background: #002211; color: #00e896; border: 1px solid #00e896; }
.signal-hold        { background: #1a1500; color: #ffcc00; border: 1px solid #ffcc00; }
.signal-watch       { background: #1a0e00; color: #ff9944; border: 1px solid #ff9944; }
.signal-sell        { background: #1a0008; color: #ff4466; border: 1px solid #ff4466; }

.ai-reasoning {
    background: #070d18;
    border: 1px solid #243552;
    border-radius: 12px;
    padding: 22px 26px;
    margin-top: 1rem;
    font-size: 1.05rem;
    line-height: 1.75;
    color: #9bb8d4;
}
.ai-reasoning b { color: #e0eef8; }

.score-row {
    display: flex;
    align-items: center;
    margin: 10px 0;
    gap: 14px;
}
.score-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    color: #6a8aaa;
    width: 160px;
    flex-shrink: 0;
}
.score-bar-bg {
    flex: 1;
    height: 10px;
    background: #1a2d42;
    border-radius: 5px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 5px;
    transition: width 0.5s ease;
}
.score-num {
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    color: #d0e4f5;
    width: 48px;
    text-align: right;
}

div[data-testid="metric-container"] {
    background: #0c1524 !important;
    border: 1px solid #1e3555 !important;
    border-radius: 10px !important;
    padding: 16px 18px !important;
}
div[data-testid="metric-container"] label { font-size: 1rem !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.45rem !important; }

.stSelectbox label, .stTextInput label {
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem !important;
    letter-spacing: 0.12em;
    color: #6a8aaa !important;
    text-transform: uppercase;
}
.stButton > button {
    background: linear-gradient(135deg, #003355, #006699);
    color: #00d4ff;
    border: 1px solid #006699;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 1rem !important;
    letter-spacing: 0.12em;
    width: 100%;
    padding: 12px 14px;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #004466, #0088bb);
    border-color: #00d4ff;
    box-shadow: 0 0 20px rgba(0,212,255,0.25);
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# MODULE 1: DATA FETCHING
# ═════════════════════════════════════════════

@st.cache_data(ttl=300)
def fetch_price_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """獲取股票歷史價格 (OHLCV)"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)
        return df
    except Exception as e:
        st.error(f"價格數據獲取失敗: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def fetch_fundamentals(ticker: str) -> dict:
    """獲取基本面數據"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        def safe_get(key, default="N/A"):
            val = info.get(key, default)
            return val if val not in [None, 0, ""] else "N/A"

        # 殖利率換算為百分比
        div_yield = info.get("dividendYield")
        div_yield_str = f"{div_yield*100:.2f}%" if div_yield else "N/A"

        # 淨資產報酬率 ROE
        roe = info.get("returnOnEquity")
        roe_str = f"{roe*100:.2f}%" if roe else "N/A"

        # 毛利率
        gross_margin = info.get("grossMargins")
        gm_str = f"{gross_margin*100:.2f}%" if gross_margin else "N/A"

        return {
            "name":          safe_get("longName", ticker),
            "sector":        safe_get("sector"),
            "market_cap":    info.get("marketCap"),
            "pe_ratio":      safe_get("trailingPE"),
            "forward_pe":    safe_get("forwardPE"),
            "eps":           safe_get("trailingEps"),
            "roe":           roe_str,
            "gross_margin":  gm_str,
            "div_yield":     div_yield_str,
            "52w_high":      safe_get("fiftyTwoWeekHigh"),
            "52w_low":       safe_get("fiftyTwoWeekLow"),
            "current_price": safe_get("currentPrice"),
            "currency":      safe_get("currency", "USD"),
            "beta":          safe_get("beta"),
            "volume":        safe_get("volume"),
        }
    except Exception as e:
        return {"name": ticker, "error": str(e)}


# ═════════════════════════════════════════════
# MODULE 1b: 台股大盤 / 台指期 / 法人籌碼（FinMind 公開 API）
# ═════════════════════════════════════════════

FINMIND_DATA_URL = "https://api.finmindtrade.com/api/v4/data"


def _ssl_context() -> ssl.SSLContext:
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


@st.cache_data(ttl=300)
def finmind_fetch(dataset: str, data_id: str = "", start_date: str = "", end_date: str = "") -> dict:
    params = {"dataset": dataset}
    if data_id:
        params["data_id"] = data_id
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    q = urllib.parse.urlencode(params)
    url = f"{FINMIND_DATA_URL}?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "AlphaStream/1.0"})
    try:
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=35) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        return {"msg": str(e), "data": []}


def parse_tw_stock_id(ticker: str) -> str | None:
    t = ticker.strip().upper()
    if t.endswith(".TWO"):
        return t[: -len(".TWO")]
    if t.endswith(".TW"):
        return t[: -len(".TW")]
    return None


@st.cache_data(ttl=300)
def fetch_tx_near_month_series(days: int = 45) -> pd.DataFrame:
    """台指期 TX：每日取成交量最大契約視為近月主力，取結算價。"""
    end = datetime.now().date()
    start = end - timedelta(days=days)
    j = finmind_fetch(
        "TaiwanFuturesDaily",
        data_id="TX",
        start_date=start.isoformat(),
        end_date=end.isoformat(),
    )
    if j.get("msg") != "success" or not j.get("data"):
        return pd.DataFrame()
    raw = pd.DataFrame(j["data"])
    if raw.empty:
        return pd.DataFrame()
    raw["volume"] = pd.to_numeric(raw["volume"], errors="coerce").fillna(0)
    raw["settlement_price"] = pd.to_numeric(raw["settlement_price"], errors="coerce")
    raw = raw[(raw["settlement_price"] > 0) & (raw["volume"] > 0)]
    if raw.empty:
        return pd.DataFrame()
    idx = raw.groupby("date")["volume"].idxmax()
    out = raw.loc[idx, ["date", "contract_date", "settlement_price", "volume", "close"]].copy()
    out["date"] = pd.to_datetime(out["date"]).dt.tz_localize(None)
    return out.sort_values("date").reset_index(drop=True)


@st.cache_data(ttl=300)
def fetch_twii_series(days: int = 45) -> pd.DataFrame:
    t = yf.Ticker("^TWII")
    df = t.history(start=datetime.now().date() - timedelta(days=days + 7))
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.reset_index()
    col = "Date" if "Date" in df.columns else df.columns[0]
    df["date"] = pd.to_datetime(df[col]).dt.tz_localize(None).dt.normalize()
    df["spot_close"] = df["Close"].astype(float)
    return df[["date", "spot_close"]].sort_values("date")


def build_tw_macro_merge(fut_df: pd.DataFrame, spot_df: pd.DataFrame) -> pd.DataFrame:
    if fut_df.empty or spot_df.empty:
        return pd.DataFrame()

    # ── 修正：統一轉為不帶時區的 datetime64[ns]，避免 tz-aware vs tz-naive merge 錯誤 ──
    def _to_naive(series: pd.Series) -> pd.Series:
        s = pd.to_datetime(series)
        if s.dt.tz is not None:
            s = s.dt.tz_convert("UTC").dt.tz_localize(None)
        return s.dt.normalize()

    fut_df = fut_df.copy()
    spot_df = spot_df.copy()
    fut_df["date"]  = _to_naive(fut_df["date"])
    spot_df["date"] = _to_naive(spot_df["date"])

    m = pd.merge(fut_df, spot_df, on="date", how="inner")
    if m.empty:
        return pd.DataFrame()
    m["fut_settle"] = m["settlement_price"].astype(float)
    m["basis"] = m["fut_settle"] - m["spot_close"]
    m["basis_pct"] = (m["basis"] / m["spot_close"]) * 100.0
    return m


def interpret_tw_macro(merged: pd.DataFrame) -> dict:
    out = {
        "ok": False,
        "text": "無法取得加權指數或台指期資料，請稍後再試。",
        "bias_class": "neutral",
        "latest": None,
        "merged": merged,
    }
    if merged is None or merged.empty:
        return out
    last = merged.iloc[-1]
    bp = float(last["basis_pct"])
    if bp > 0.12:
        bias, bcls = "偏多（正向價差）", "positive"
        hint = "期貨結算價高於現貨加權，常解讀為市場對後市相對樂觀（正向價差／Contango 於指數期貨語境）。"
    elif bp < -0.12:
        bias, bcls = "偏空／保守（逆價差）", "negative"
        hint = "期貨低於現貨（逆價差），常與避險、保守預期或短線調節有關，需搭配量能與趨勢判讀。"
    else:
        bias, bcls = "中性（期現貨接近）", "neutral"
        hint = "價差不大，未呈現明顯正向或逆價差訊號。"

    trend_note = ""
    if len(merged) >= 6:
        recent = merged.tail(5)["basis_pct"].mean()
        prior = merged.iloc[-10:-5]["basis_pct"].mean() if len(merged) >= 10 else None
        if prior is not None:
            if recent > prior + 0.05:
                trend_note = "近五日平均價差較前一週擴張，正向情緒略增溫。"
            elif recent < prior - 0.05:
                trend_note = "近五日平均價差較前一週收斂或轉負，保守意味略升。"

    out.update(
        {
            "ok": True,
            "bias_class": bcls,
            "latest": last,
            "text": f"{bias} — {hint} {trend_note}".strip(),
        }
    )
    return out


def build_tw_macro_chart(merged: pd.DataFrame) -> go.Figure:
    _bg, _paper, _grid, _txt, _accent = "#0a0e1a", "#0d1220", "#1a2d42", "#8ba7c4", "#00d4ff"
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=merged["date"],
            y=merged["spot_close"],
            name="加權指數 ^TWII 收盤",
            line=dict(color="#00d4ff", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=merged["date"],
            y=merged["fut_settle"],
            name="台指期 TX（近月成交量最大）結算",
            line=dict(color="#ffcc55", width=2),
        )
    )
    fig.update_layout(
        height=420,
        plot_bgcolor=_bg,
        paper_bgcolor=_paper,
        font=dict(family="Space Mono, monospace", color=_txt, size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(gridcolor=_grid, showgrid=True),
        yaxis=dict(gridcolor=_grid, showgrid=True, tickformat=","),
        title=dict(
            text="大盤現貨 vs 台指期（近月）",
            font=dict(size=15, color=_accent),
            x=0.01,
        ),
    )
    return fig


@st.cache_data(ttl=600)
def fetch_institutional_finmind(stock_id: str, days: int = 20) -> pd.DataFrame:
    end = datetime.now().date()
    start = end - timedelta(days=days + 10)
    j = finmind_fetch(
        "TaiwanStockInstitutionalInvestorsBuySell",
        data_id=stock_id,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
    )
    if j.get("msg") != "success" or not j.get("data"):
        return pd.DataFrame()
    return pd.DataFrame(j["data"])


def pivot_institutional_daily(inst: pd.DataFrame) -> pd.DataFrame:
    if inst.empty:
        return inst
    rows = []
    for d, g in inst.groupby("date"):
        nets: dict[str, int] = {}
        for _, r in g.iterrows():
            nm = str(r["name"])
            buy = int(float(r["buy"])) if pd.notna(r["buy"]) else 0
            sell = int(float(r["sell"])) if pd.notna(r["sell"]) else 0
            nets[nm] = buy - sell
        foreign = nets.get("Foreign_Investor", 0)
        trust = nets.get("Investment_Trust", 0)
        dealer = nets.get("Dealer_self", 0) + nets.get("Dealer_Hedging", 0)
        total = foreign + trust + dealer
        rows.append(
            {
                "date": pd.to_datetime(d),
                "外資淨額（股）": foreign,
                "投信淨額（股）": trust,
                "自營商淨額（股）": dealer,
                "三大法人淨額（股）": total,
            }
        )
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def compute_chip_score(daily: pd.DataFrame) -> tuple[float, list[str]]:
    """依法人淨買賣超方向與規模給籌碼分 -10～+10（僅輔助）。"""
    reasons: list[str] = []
    if daily.empty:
        return 0.0, ["尚無法人買賣資料。"]
    tail = daily.tail(5)
    sum5 = int(tail["三大法人淨額（股）"].sum())
    last_net = int(daily.iloc[-1]["三大法人淨額（股）"])

    mag = min(5, int(math.log10(abs(sum5) + 10) - 2)) if sum5 != 0 else 0
    mag = max(0, mag)

    if sum5 > 0:
        chip = 2 + mag
        reasons.append(
            f"近約 {len(tail)} 個交易日三大法人累計淨買超 {sum5:+,} 股（約 {sum5/1000:,.1f} 張），籌碼偏多解讀。"
        )
    elif sum5 < 0:
        chip = -(2 + mag)
        reasons.append(
            f"近約 {len(tail)} 個交易日三大法人累計淨賣超 {sum5:+,} 股（約 {sum5/1000:,.1f} 張），籌碼偏空解讀。"
        )
    else:
        chip = 0
        reasons.append("近五日三大法人淨額合計接近零，籌碼中性。")

    if last_net > 0:
        reasons.append(f"最新一日三大法人合計淨買超 {last_net:+,} 股。")
    elif last_net < 0:
        reasons.append(f"最新一日三大法人合計淨賣超 {last_net:+,} 股。")

    if last_net > 0 and sum5 > 0:
        chip = min(10, chip + 1)
    elif last_net < 0 and sum5 < 0:
        chip = max(-10, chip - 1)

    chip_f = float(max(-10, min(10, chip)))
    return chip_f, reasons


def build_chip_bar_figure(daily: pd.DataFrame) -> go.Figure:
    _bg, _paper, _grid, _txt, _accent = "#0a0e1a", "#0d1220", "#1a2d42", "#8ba7c4", "#00d4ff"
    fig = go.Figure()
    x = daily["date"]
    fig.add_trace(
        go.Bar(x=x, y=daily["外資淨額（股）"], name="外資", marker_color="#00d4ff")
    )
    fig.add_trace(
        go.Bar(x=x, y=daily["投信淨額（股）"], name="投信", marker_color="#ffcc55")
    )
    fig.add_trace(
        go.Bar(x=x, y=daily["自營商淨額（股）"], name="自營商", marker_color="#aa88ff")
    )
    fig.update_layout(
        barmode="relative",
        height=400,
        plot_bgcolor=_bg,
        paper_bgcolor=_paper,
        font=dict(family="Space Mono, monospace", color=_txt, size=12),
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
        margin=dict(l=0, r=0, t=36, b=0),
        title=dict(text="三大法人買賣超（股）", font=dict(size=14, color=_accent), x=0.01),
        xaxis=dict(gridcolor=_grid),
        yaxis=dict(gridcolor=_grid, tickformat=","),
    )
    return fig


# ═════════════════════════════════════════════
# MODULE 2: TECHNICAL ANALYSIS
# ═════════════════════════════════════════════

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    計算技術指標：
    - MA 20 / 50 / 200
    - MACD (12,26,9) — 標準定義
    - RSI (14) — Wilder smoothing
    - Bollinger Bands (20, 2σ)
    """
    if df.empty or len(df) < 30:
        return df

    close = df["Close"]

    # ── Moving Averages ──
    df["MA20"]  = close.rolling(20).mean()
    df["MA50"]  = close.rolling(50).mean()
    df["MA200"] = close.rolling(200).mean()

    # ── MACD (12-26-9) ──
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"]        = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"]   = df["MACD"] - df["MACD_Signal"]

    # ── RSI (14) — Wilder's smoothing ──
    delta  = close.diff()
    gain   = delta.clip(lower=0)
    loss   = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=13, adjust=False).mean()
    avg_loss = loss.ewm(com=13, adjust=False).mean()
    rs       = avg_gain / avg_loss.replace(0, float("nan"))
    df["RSI"] = 100 - (100 / (1 + rs))

    # ── Bollinger Bands (20, ±2σ) ──
    std20        = close.rolling(20).std()
    df["BB_Mid"] = df["MA20"]
    df["BB_Up"]  = df["MA20"] + 2 * std20
    df["BB_Lo"]  = df["MA20"] - 2 * std20

    return df


def get_technical_signals(df: pd.DataFrame) -> dict:
    """提取最新一根 K 棒的技術訊號"""
    if df.empty:
        return {}
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last

    signals = {}

    # RSI signal
    rsi = last.get("RSI", 50)
    if isinstance(rsi, float):
        if rsi >= 70:
            signals["rsi"] = ("超買", "negative", rsi)
        elif rsi <= 30:
            signals["rsi"] = ("超賣", "positive", rsi)
        else:
            signals["rsi"] = ("中性", "neutral", rsi)

    # MACD crossover
    macd_now  = last.get("MACD",        0)
    sig_now   = last.get("MACD_Signal", 0)
    macd_prev = prev.get("MACD",        0)
    sig_prev  = prev.get("MACD_Signal", 0)
    if macd_now > sig_now and macd_prev <= sig_prev:
        signals["macd"] = ("黃金交叉", "positive")
    elif macd_now < sig_now and macd_prev >= sig_prev:
        signals["macd"] = ("死亡交叉", "negative")
    elif macd_now > sig_now:
        signals["macd"] = ("多頭排列", "positive")
    else:
        signals["macd"] = ("空頭排列", "negative")

    # MA trend
    close = last.get("Close", 0)
    ma20  = last.get("MA20",  None)
    ma50  = last.get("MA50",  None)
    ma200 = last.get("MA200", None)
    above_count = sum([
        close > ma20  if ma20  else False,
        close > ma50  if ma50  else False,
        close > ma200 if ma200 else False,
    ])
    signals["ma_trend"] = above_count  # 0-3

    return signals


def technical_digest_html(df: pd.DataFrame) -> str:
    """儀表板用：標示最新數值並附帶慣用門檻說明（教育用途，非投資建議）。"""
    if df.empty or len(df) < 2:
        return '<p style="color:#6a8aaa;font-size:1.05rem;">資料不足，無法解讀技術指標。</p>'

    last = df.iloc[-1]
    prev = df.iloc[-2]

    def _f(x, nd=4):
        try:
            v = float(x)
            if pd.isna(v):
                return None
            return round(v, nd)
        except (TypeError, ValueError):
            return None

    # ── RSI ──
    rsi_v = _f(last.get("RSI"), 1)
    if rsi_v is None:
        rsi_card = '<div class="dash-card"><div class="dash-card-title">RSI (14)</div><p class="tech-threshold">尚無有效 RSI 數值。</p></div>'
    else:
        if rsi_v >= 70:
            v_cls, v_txt = "negative", "偏短線過熱（超買）"
        elif rsi_v <= 30:
            v_cls, v_txt = "positive", "跌深反彈契機（超賣）"
        else:
            v_cls, v_txt = "neutral", "中性區間"
        rsi_card = f"""
        <div class="dash-card">
          <div class="dash-card-title">RSI (14)</div>
          <div class="tech-big-num">RSI = {rsi_v:.1f}</div>
          <div class="tech-verdict {v_cls}">{v_txt}</div>
          <div class="tech-threshold">
            <b>怎麼看：</b>RSI 在 <b>70 以上</b> 常視為<b>超買</b>（上漲動能過強、短線易回檔，偏多屬「追價風險高」）。<b>30 以下</b> 常視為<b>超賣</b>（賣壓釋放後較易出現反彈）。<b>30～70</b> 之間多列為中性，需搭配趨勢與其他指標。
          </div>
        </div>"""

    # ── MACD ──
    m = _f(last.get("MACD"), 4)
    s = _f(last.get("MACD_Signal"), 4)
    h = _f(last.get("MACD_Hist"), 4)
    mp, sp = _f(prev.get("MACD"), 4), _f(prev.get("MACD_Signal"), 4)
    if m is None or s is None or h is None:
        macd_card = '<div class="dash-card"><div class="dash-card-title">MACD (12,26,9)</div><p class="tech-threshold">尚無有效 MACD 數值。</p></div>'
    else:
        cross = ""
        if mp is not None and sp is not None:
            if m > s and mp <= sp:
                cross = "本棒出現 <b>黃金交叉</b>（MACD 上穿訊號線），常解讀為動能轉多。"
            elif m < s and mp >= sp:
                cross = "本棒出現 <b>死亡交叉</b>（MACD 下穿訊號線），常解讀為動能轉空。"
        hist_note = (
            f"柱狀圖（Histogram）= <b>{h:+.4f}</b>：&gt;0 表示 MACD 在訊號線之上，偏多動能；&lt;0 表示偏空動能。"
        )
        v_cls = "positive" if h > 0 else ("negative" if h < 0 else "neutral")
        v_txt = "柱狀為正（偏多動能）" if h > 0 else ("柱狀為負（偏空動能）" if h < 0 else "柱狀接近零軸")
        macd_card = f"""
        <div class="dash-card">
          <div class="dash-card-title">MACD (12, 26, 9)</div>
          <div class="tech-big-num" style="font-size:1.35rem;">MACD = {m:.4f} ｜ Signal = {s:.4f}</div>
          <div class="tech-verdict {v_cls}">{v_txt}</div>
          <div class="tech-threshold">{hist_note}{(" " + cross) if cross else ""}</div>
        </div>"""

    # ── 布林 + 均線 ──
    close = _f(last.get("Close"), 2)
    ma20 = _f(last.get("MA20"), 2)
    ma50 = _f(last.get("MA50"), 2)
    ma200 = _f(last.get("MA200"), 2)
    bu, bl = _f(last.get("BB_Up"), 2), _f(last.get("BB_Lo"), 2)
    lines = []
    if close is not None:
        lines.append(f"收盤 <b>{close:.2f}</b>")
    if all(x is not None for x in (close, bu, bl)):
        if close >= bu:
            pos = "貼近或站上<b>上軌</b>，波動偏大、易過熱；短線偏「注意回檔」。"
        elif close <= bl:
            pos = "貼近或觸及<b>下軌</b>，常與超賣／反彈觀察一併看。"
        else:
            pos = "介於上下軌之間，屬常態波動區。"
        lines.append(f"布林：上軌 {bu:.2f} ／ 下軌 {bl:.2f} — {pos}")
    ma_parts = []
    for label, mv in [("MA20", ma20), ("MA50", ma50), ("MA200", ma200)]:
        if mv is not None and close is not None:
            ma_parts.append(f"{label}={mv:.2f}（收盤{'站上' if close > mv else '站下'}）")
    if ma_parts:
        lines.append("均線：" + "；".join(ma_parts) + "。站上越多條長天期均線，多頭結構通常較完整；反之為偏空結構。")

    trend_card = f"""
    <div class="dash-card">
      <div class="dash-card-title">價格 · 布林 · 均線</div>
      <div class="tech-threshold" style="border-top:none;padding-top:0;font-size:1.05rem;">
        {"<br><br>".join(lines) if lines else "指標尚未就緒。"}
      </div>
    </div>"""

    return f'<div class="tech-grid">{rsi_card}{macd_card}{trend_card}</div>'


# ═════════════════════════════════════════════
# MODULE 3: CHART
# ═════════════════════════════════════════════

COLORS = {
    "bg":          "#0a0e1a",
    "paper":       "#0d1220",
    "grid":        "#1a2d42",
    "text":        "#8ba7c4",
    "candle_up":   "#00e896",
    "candle_down": "#ff4466",
    "ma20":        "#00d4ff",
    "ma50":        "#ffcc00",
    "ma200":       "#ff6699",
    "bb":          "#3a6080",
    "macd":        "#00d4ff",
    "signal":      "#ffcc00",
    "hist_pos":    "#00e896",
    "hist_neg":    "#ff4466",
    "rsi":         "#cc88ff",
    "volume_up":   "rgba(0,232,150,0.4)",
    "volume_down": "rgba(255,68,102,0.4)",
}


def build_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """繪製完整的 K 線 + 技術指標複合圖"""
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=[0.52, 0.16, 0.16, 0.16],
        subplot_titles=("", "Volume", "MACD", "RSI (14)"),
    )

    # ── Candlestick ──
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        name="OHLC",
        increasing_line_color=COLORS["candle_up"],
        decreasing_line_color=COLORS["candle_down"],
        increasing_fillcolor=COLORS["candle_up"],
        decreasing_fillcolor=COLORS["candle_down"],
        line_width=1,
    ), row=1, col=1)

    # ── Moving Averages ──
    for col, color, name in [
        ("MA20",  COLORS["ma20"],  "MA 20"),
        ("MA50",  COLORS["ma50"],  "MA 50"),
        ("MA200", COLORS["ma200"], "MA 200"),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[col], name=name,
                line=dict(color=color, width=1.5),
                opacity=0.85,
            ), row=1, col=1)

    # ── Bollinger Bands ──
    if "BB_Up" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_Up"],
            name="BB Upper", line=dict(color=COLORS["bb"], width=1, dash="dot"),
            opacity=0.6,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_Lo"],
            name="BB Lower", line=dict(color=COLORS["bb"], width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(58,96,128,0.08)",
            opacity=0.6,
        ), row=1, col=1)

    # ── Volume ──
    colors_vol = [
        COLORS["volume_up"] if c >= o else COLORS["volume_down"]
        for c, o in zip(df["Close"], df["Open"])
    ]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        name="Volume", marker_color=colors_vol,
        showlegend=False,
    ), row=2, col=1)

    # ── MACD ──
    if "MACD" in df.columns:
        hist_colors = [
            COLORS["hist_pos"] if v >= 0 else COLORS["hist_neg"]
            for v in df["MACD_Hist"].fillna(0)
        ]
        fig.add_trace(go.Bar(
            x=df.index, y=df["MACD_Hist"],
            name="MACD Histogram", marker_color=hist_colors, showlegend=False,
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MACD"],
            name="MACD", line=dict(color=COLORS["macd"], width=1.5),
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MACD_Signal"],
            name="Signal", line=dict(color=COLORS["signal"], width=1.5, dash="dash"),
        ), row=3, col=1)

    # ── RSI ──
    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["RSI"],
            name="RSI", line=dict(color=COLORS["rsi"], width=1.5),
        ), row=4, col=1)
        for lvl, dash in [(70, "dot"), (50, "longdash"), (30, "dot")]:
            fig.add_hline(
                y=lvl, line_dash=dash,
                line_color=COLORS["grid"], line_width=1,
                row=4, col=1,
            )

    # ── Layout ──
    fig.update_layout(
        height=820,
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["paper"],
        font=dict(family="Space Mono, monospace", color=COLORS["text"], size=14),
        xaxis_rangeslider_visible=False,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=COLORS["grid"],
            borderwidth=1,
            font=dict(size=12),
        ),
        margin=dict(l=0, r=0, t=36, b=0),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0d1220",
            bordercolor=COLORS["grid"],
            font=dict(family="Space Mono", size=13),
        ),
        title=dict(
            text=f"<b>{ticker}</b>  Interactive Chart",
            font=dict(size=17, color=COLORS["ma20"]),
            x=0.01,
        ),
    )

    for i in range(1, 5):
        fig.update_xaxes(
            gridcolor=COLORS["grid"], gridwidth=1,
            showgrid=True, zeroline=False,
            row=i, col=1,
        )
        fig.update_yaxes(
            gridcolor=COLORS["grid"], gridwidth=1,
            showgrid=True, zeroline=False,
            row=i, col=1,
        )

    return fig


# ═════════════════════════════════════════════
# MODULE 4: AI DECISION ENGINE
# ═════════════════════════════════════════════

def compute_decision(
    df: pd.DataFrame,
    fundamentals: dict,
    chip_score: float | None = None,
    chip_reasons: list[str] | None = None,
) -> dict:
    """
    綜合評分：預設為技術 + 基本面；台股可併入籌碼（法人）分數。
    無籌碼時：技術 40/75、基本面 35/75。
    有籌碼時：技術 40%、基本面 35%、籌碼 25%（各約 -10～+10）。
    """
    reasons = []
    tech_score = 0  # -10 ~ +10
    fund_score = 0
    chip_reasons = chip_reasons or []

    signals = get_technical_signals(df) if not df.empty else {}

    # ── Technical ──
    rsi_data = signals.get("rsi")
    if rsi_data:
        _label, tone, val = rsi_data
        if tone == "positive":
            tech_score += 4
            reasons.append(
                f"RSI = {val:.1f} — 超賣區（≤30 常視為跌深反彈觀察區），模型給分偏多"
            )
        elif tone == "negative":
            tech_score -= 3
            reasons.append(
                f"RSI = {val:.1f} — 超買區（≥70 常視為短線過熱），模型給分偏保守"
            )
        else:
            reasons.append(
                f"RSI = {val:.1f} — 中性區（約 30～70）；未觸及極端超買／超賣"
            )

    macd_data = signals.get("macd")
    if macd_data:
        label, tone = macd_data
        if tone == "positive":
            tech_score += 3 if "交叉" in label else 2
        else:
            tech_score -= 3 if "交叉" in label else 2
        reasons.append(f"MACD {label}")

    ma_count = signals.get("ma_trend", 1)
    if ma_count == 3:
        tech_score += 3
        reasons.append("收盤價站上 MA20/50/200，強勢多頭格局")
    elif ma_count == 2:
        tech_score += 1
        reasons.append("收盤價站上兩條均線，偏多格局")
    elif ma_count == 0:
        tech_score -= 3
        reasons.append("收盤價跌破三條均線，偏空格局")

    tech_score = max(-10, min(10, tech_score))

    # ── Fundamental (35%) ──
    pe = fundamentals.get("pe_ratio", "N/A")
    try:
        pe_val = float(pe)
        if pe_val < 0:
            fund_score -= 3
            reasons.append(f"PE={pe_val:.1f} — 負值（虧損中），基本面疑慮")
        elif pe_val < 15:
            fund_score += 4
            reasons.append(f"PE={pe_val:.1f} — 低估值，具安全邊際")
        elif pe_val < 25:
            fund_score += 2
            reasons.append(f"PE={pe_val:.1f} — 合理估值")
        elif pe_val < 40:
            fund_score -= 1
            reasons.append(f"PE={pe_val:.1f} — 略高估值")
        else:
            fund_score -= 3
            reasons.append(f"PE={pe_val:.1f} — 高估值，需留意下修風險")
    except (ValueError, TypeError):
        reasons.append("PE 數據不可用")

    roe_str = fundamentals.get("roe", "N/A")
    try:
        roe_val = float(roe_str.replace("%", ""))
        if roe_val > 20:
            fund_score += 3
            reasons.append(f"ROE={roe_val:.1f}% — 優質盈利能力")
        elif roe_val > 10:
            fund_score += 1
            reasons.append(f"ROE={roe_val:.1f}% — 一般盈利能力")
        else:
            fund_score -= 1
            reasons.append(f"ROE={roe_val:.1f}% — 盈利能力偏弱")
    except (ValueError, AttributeError):
        pass

    div_str = fundamentals.get("div_yield", "N/A")
    try:
        div_val = float(div_str.replace("%", ""))
        if div_val >= 3:
            fund_score += 2
            reasons.append(f"殖利率={div_val:.2f}% — 高股息，防禦性佳")
        elif div_val > 0:
            fund_score += 1
    except (ValueError, AttributeError):
        pass

    fund_score = max(-10, min(10, fund_score))

    for cr in chip_reasons:
        reasons.append(f"籌碼：{cr}")

    if chip_score is None:
        w_tech, w_fund = 40 / 75, 35 / 75
        composite = tech_score * w_tech + fund_score * w_fund
    else:
        cs = max(-10, min(10, float(chip_score)))
        composite = tech_score * 0.40 + fund_score * 0.35 + cs * 0.25

    if composite >= 4.5:
        signal, signal_class = "強力買入", "signal-strong-buy"
    elif composite >= 2.0:
        signal, signal_class = "買入", "signal-buy"
    elif composite >= -1.0:
        signal, signal_class = "持有", "signal-hold"
    elif composite >= -3.0:
        signal, signal_class = "觀望", "signal-watch"
    else:
        signal, signal_class = "賣出", "signal-sell"

    out = {
        "signal": signal,
        "signal_class": signal_class,
        "composite": round(composite, 2),
        "tech_score": tech_score,
        "fund_score": fund_score,
        "reasons": reasons,
        "chip_score": chip_score,
    }
    return out


# ═════════════════════════════════════════════
# HELPER: Format numbers
# ═════════════════════════════════════════════

def fmt_market_cap(val) -> str:
    if val is None or val == "N/A":
        return "N/A"
    try:
        v = float(val)
        if v >= 1e12:
            return f"{v/1e12:.2f}T"
        if v >= 1e9:
            return f"{v/1e9:.2f}B"
        if v >= 1e6:
            return f"{v/1e6:.2f}M"
        return f"{v:,.0f}"
    except (ValueError, TypeError):
        return "N/A"


def score_to_bar(score: float, max_score: float = 10) -> str:
    """生成評分橫條 HTML"""
    pct = max(0, min(100, (score + max_score) / (2 * max_score) * 100))
    if score >= 2:
        color = "#00e896"
    elif score >= -1:
        color = "#ffcc00"
    else:
        color = "#ff4466"
    return f"""
    <div class="score-row">
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width:{pct}%; background:{color};"></div>
      </div>
      <div class="score-num">{score:+.1f}</div>
    </div>"""


# ═════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="font-family:'Space Mono',monospace; font-size:1.55rem; font-weight:700;
         color:#00d4ff; letter-spacing:0.12em; margin-bottom:0.25rem;">
        📈 ALPHA<span style="color:#ff6b8a;">STREAM</span>
    </div>
    <div style="font-family:'Space Mono',monospace; font-size:0.82rem; color:#5a7a9a;
         letter-spacing:0.22em; margin-bottom:1.5rem;">QUANT ANALYSIS TERMINAL</div>
    """, unsafe_allow_html=True)

    ticker_input = st.text_input(
        "TICKER SYMBOL",
        value="AAPL",
        placeholder="e.g. AAPL / 2330.TW",
        help="美股直接輸入代號，台股需加 .TW（例：2330.TW）",
    ).strip().upper()

    period_map = {
        "1 個月": "1mo",
        "3 個月": "3mo",
        "6 個月": "6mo",
        "1 年":   "1y",
        "2 年":   "2y",
    }
    period_label = st.selectbox("分析週期", list(period_map.keys()), index=3)
    period = period_map[period_label]

    st.markdown("---")
    run = st.button("🔍  開始分析", use_container_width=True)

    st.markdown("""
    <div style="margin-top:2rem; font-family:'Space Mono',monospace; font-size:0.82rem;
         color:#3a5080; line-height:1.75; letter-spacing:0.04em;">
    ⚠ 本工具僅供學術研究與個人參考，不構成任何投資建議。<br><br>
    數據來源：Yahoo Finance · FinMind（台股大盤／期貨／法人）
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════
# MAIN LAYOUT
# ═════════════════════════════════════════════

st.markdown("""
<div class="alpha-header">📡 ALPHASTREAM</div>
<div class="alpha-subtitle">Quantitative Stock Analysis Terminal · v1.0</div>
""", unsafe_allow_html=True)

if not run:
    st.markdown("""
    <div style="text-align:center; padding:72px 0; color:#5a7a9a;
         font-family:'Space Mono',monospace; font-size:1.25rem; letter-spacing:0.12em;">
        ← 在左側輸入股票代號，點擊「開始分析」
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Fetch all data ───
tw_stock_id = None
chip_score_param: float | None = None
chip_reasons_param: list[str] = []
chip_daily = pd.DataFrame()
merged_macro = pd.DataFrame()
macro_ctx: dict = {"ok": False, "text": "尚未載入。"}

with st.spinner("載入中…"):
    df_raw = fetch_price_history(ticker_input, period)
    fundamentals = fetch_fundamentals(ticker_input)
    company_name = fundamentals.get("name", ticker_input)
    fut_df = fetch_tx_near_month_series(50)
    spot_df = fetch_twii_series(50)
    merged_macro = build_tw_macro_merge(fut_df, spot_df)
    macro_ctx = interpret_tw_macro(merged_macro)

    tw_stock_id = parse_tw_stock_id(ticker_input)
    if tw_stock_id:
        inst_raw = fetch_institutional_finmind(tw_stock_id, days=25)
        chip_daily = pivot_institutional_daily(inst_raw)
        if not chip_daily.empty:
            chip_score_param, chip_reasons_param = compute_chip_score(chip_daily)
        else:
            chip_reasons_param = ["FinMind 尚無此股近日三大法人買賣明細（或資料尚未更新）。"]

if df_raw.empty:
    st.error(f"找不到 **{ticker_input}** 的數據，請確認代號是否正確。台股請加 `.TW`，例如 `2330.TW`。")
    st.stop()

df = compute_indicators(df_raw.copy())
decision = compute_decision(
    df,
    fundamentals,
    chip_score=chip_score_param,
    chip_reasons=(chip_reasons_param if tw_stock_id else []),
)

# ─────────────────────────────────────────────
# SECTION 0: 台股大盤（加權）vs 台指期
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">台股大盤 · 加權指數 vs 台指期（TX 近月）</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
if macro_ctx.get("ok") and macro_ctx.get("latest") is not None:
    lat = macro_ctx["latest"]
    bcls = macro_ctx.get("bias_class", "neutral")
    bias_title = (
        "偏多解讀" if bcls == "positive" else ("偏空／保守解讀" if bcls == "negative" else "中性解讀")
    )
    badge_color = "#00e896" if bcls == "positive" else ("#ff6b8a" if bcls == "negative" else "#ffcc55")
    d_str = pd.Timestamp(lat["date"]).strftime("%Y-%m-%d")
    st.markdown(
        f"""
        <div style="font-size:1.15rem; line-height:1.7; color:#c5d8ec; margin-bottom:14px;">
          <b style="color:{badge_color}; font-size:1.25rem;">{bias_title}</b>
          — {macro_ctx["text"]}
        </div>
        <div style="font-family:'Space Mono',monospace; font-size:1.02rem; color:#8ba7c4; margin-bottom:8px;">
          資料日 <b>{d_str}</b>｜加權收盤 <b>{float(lat["spot_close"]):,.2f}</b>
          ｜台指期（近月）結算 <b>{float(lat["fut_settle"]):,.2f}</b>
          ｜價差 <b>{float(lat["basis"]):+,.2f}</b> 點（<b>{float(lat["basis_pct"]):+.3f}%</b>）
        </div>
        <div style="font-size:0.98rem; color:#6a8aaa; margin-bottom:12px;">
          說明：台指期採 FinMind「TX」每日成交量最大契約作為近月代表；現貨為 Yahoo <b>^TWII</b> 收盤。實務仍須搭配量能、事件與國際盤。
        </div>
        """,
        unsafe_allow_html=True,
    )
    fig_m = build_tw_macro_chart(merged_macro)
    st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": True})
else:
    st.warning(macro_ctx.get("text", "無法載入大盤／期貨資料。"))
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION A: HEADER + PRICE
# ─────────────────────────────────────────────
currency = fundamentals.get("currency", "USD")
cur_price = fundamentals.get("current_price", "N/A")

try:
    last_close  = float(df["Close"].iloc[-1])
    prev_close  = float(df["Close"].iloc[-2])
    chg         = last_close - prev_close
    chg_pct     = chg / prev_close * 100
    chg_sign    = "+" if chg >= 0 else ""
    chg_color   = "#00e896" if chg >= 0 else "#ff4466"
    price_str   = f"{last_close:,.2f}"
    chg_str     = f"{chg_sign}{chg:.2f} ({chg_sign}{chg_pct:.2f}%)"
except Exception:
    price_str = str(cur_price)
    chg_str   = ""
    chg_color = "#8ba7c4"

st.markdown(f"""
<div class="dashboard-panel" style="margin-top:0;">
<div style="display:flex; flex-wrap:wrap; align-items:baseline; gap:20px; margin-bottom:0.5rem;">
  <div style="font-family:'Space Mono',monospace; font-size:2.75rem; font-weight:700; color:#e8f4ff;">
    {price_str}
    <span style="font-size:1.1rem; color:#6a8aaa; margin-left:6px;">{currency}</span>
  </div>
  <div style="font-family:'Space Mono',monospace; font-size:1.35rem; color:{chg_color};">
    {chg_str}
  </div>
</div>
<div style="font-family:'IBM Plex Sans',sans-serif; font-size:1.1rem; color:#8ba7c4;
     letter-spacing:0.04em; margin-bottom:0.2rem;">
  {company_name} &nbsp;·&nbsp; {fundamentals.get('sector','—')} &nbsp;·&nbsp;
  市值 {fmt_market_cap(fundamentals.get('market_cap'))}
</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION B: FUNDAMENTAL METRICS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">基本面指標</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)

m_cols = st.columns(6)
metrics = [
    ("PE (TTM)",    fundamentals.get("pe_ratio",   "N/A")),
    ("Forward PE",  fundamentals.get("forward_pe", "N/A")),
    ("EPS",         fundamentals.get("eps",        "N/A")),
    ("ROE",         fundamentals.get("roe",        "N/A")),
    ("殖利率",       fundamentals.get("div_yield",  "N/A")),
    ("Beta",        fundamentals.get("beta",       "N/A")),
]
for col, (label, val) in zip(m_cols, metrics):
    with col:
        st.metric(label, val)

m_cols2 = st.columns(4)
metrics2 = [
    ("52W 高",  fundamentals.get("52w_high", "N/A")),
    ("52W 低",  fundamentals.get("52w_low",  "N/A")),
    ("毛利率",   fundamentals.get("gross_margin", "N/A")),
    ("成交量",   f"{fundamentals.get('volume','N/A'):,}" if isinstance(fundamentals.get("volume"), int) else fundamentals.get("volume","N/A")),
]
for col, (label, val) in zip(m_cols2, metrics2):
    with col:
        st.metric(label, val)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION B2: 籌碼面（三大法人）— 僅 .TW / .TWO
# ─────────────────────────────────────────────
if tw_stock_id:
    st.markdown('<div class="section-header">籌碼面 · 三大法人買賣超（FinMind）</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    st.caption(f"證券代號：**{tw_stock_id}**（上市櫃法人買進／賣出／淨額單位：股；1 張 ≈ 1,000 股）")
    if not chip_daily.empty:
        show_tbl = chip_daily.tail(12).iloc[::-1].copy()
        for c in show_tbl.columns:
            if "股" in c:
                show_tbl[c] = show_tbl[c].apply(lambda x: f"{int(x):+,}")
        show_tbl["date"] = show_tbl["date"].dt.strftime("%Y-%m-%d")
        st.dataframe(show_tbl, use_container_width=True, hide_index=True)
        fig_chip = build_chip_bar_figure(chip_daily.tail(30))
        st.plotly_chart(fig_chip, use_container_width=True, config={"displayModeBar": True})
        if chip_score_param is not None:
            st.success(
                f"籌碼模型分數（納入綜合決策權重 25%）：**{chip_score_param:+.1f}**／10"
            )
    else:
        st.info(chip_reasons_param[0] if chip_reasons_param else "尚無法人籌碼資料。")
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION C: CHART
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">技術分析圖表</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-panel" style="padding-bottom:12px;">', unsafe_allow_html=True)
fig = build_chart(df, ticker_input)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION D: 技術指標解讀（數值 + 門檻說明）
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">技術指標解讀</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-panel">' + technical_digest_html(df) + "</div>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# SECTION E: 綜合決策
# ─────────────────────────────────────────────
dec_title = (
    "綜合決策（技術 + 基本面 + 籌碼）"
    if decision.get("chip_score") is not None
    else "綜合決策（技術 + 基本面）"
)
st.markdown(f'<div class="section-header">{dec_title}</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)

st.markdown(f"""
<div style="margin:0.5rem 0 1.2rem 0;">
  <span class="signal-badge {decision['signal_class']}">{decision['signal']}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin:0.5rem 0;'>", unsafe_allow_html=True)
if decision.get("chip_score") is None:
    score_items = [
        (f"技術面 ×{40/75*100:.1f}%", decision["tech_score"]),
        (f"基本面 ×{35/75*100:.1f}%", decision["fund_score"]),
        ("綜合得分", decision["composite"]),
    ]
    formula_note = "綜合評分 = 技術面×(40÷75) + 基本面×(35÷75)。單項約 -10～+10，僅供參考。"
else:
    score_items = [
        ("技術面 ×40%", decision["tech_score"]),
        ("基本面 ×35%", decision["fund_score"]),
        ("籌碼（法人）×25%", float(decision["chip_score"])),
        ("綜合得分", decision["composite"]),
    ]
    formula_note = "台股含籌碼：綜合 = 技術×40% + 基本面×35% + 籌碼×25%。籌碼依三大法人淨買賣超方向與規模估算，僅供參考。"

for label, score in score_items:
    st.markdown(f"""
    <div class="score-row">
      <div class="score-label">{label}</div>
      {score_to_bar(score)}
    </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

reasons_html = "".join(f"<div style='margin:6px 0;'>• {r}</div>" for r in decision["reasons"])
st.markdown(f"""
<div class="ai-reasoning">
  <b>分析依據：</b>
  <div style="margin-top:10px;">{reasons_html}</div>
  <div style="margin-top:14px; font-size:0.95rem; color:#5a7a9a; border-top:1px solid #243552; padding-top:12px;">
    {formula_note}
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div style="margin-top:3rem; text-align:center; font-family:'Space Mono',monospace;
     font-size:0.88rem; color:#3a5080; letter-spacing:0.1em;">
  ALPHASTREAM v1.0 &nbsp;·&nbsp; 數據來源：Yahoo Finance · FinMind &nbsp;·&nbsp;
  最後更新：{last_update} &nbsp;·&nbsp; ⚠ 本工具不構成投資建議
</div>
""", unsafe_allow_html=True)
