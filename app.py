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
import requests
from datetime import datetime, timedelta
import urllib.parse
import feedparser
import warnings
import time

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

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Dark terminal background ── */
.stApp {
    background: #0a0e1a;
    color: #c8d8e8;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1220;
    border-right: 1px solid #1e2d45;
}
[data-testid="stSidebar"] * {
    color: #8ba7c4 !important;
}

/* ── Main header ── */
.alpha-header {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 0.15em;
    text-shadow: 0 0 30px rgba(0,212,255,0.35);
    margin-bottom: 0.1rem;
}
.alpha-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #3a6080;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin: 1.2rem 0;
}
.metric-card {
    background: #0f1825;
    border: 1px solid #1a2d42;
    border-radius: 8px;
    padding: 14px 18px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d4ff, #0066cc);
}
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #3a6080;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.35rem;
    font-weight: 700;
    color: #e0f0ff;
}
.metric-value.positive { color: #00e896; }
.metric-value.negative { color: #ff4466; }
.metric-value.neutral  { color: #ffcc00; }

/* ── Section headers ── */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #00d4ff;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    border-bottom: 1px solid #1a2d42;
    padding-bottom: 8px;
    margin: 1.8rem 0 1rem 0;
}

/* ── Signal badge ── */
.signal-badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 12px 28px;
    border-radius: 6px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0.5rem 0;
}
.signal-strong-buy  { background: #003322; color: #00ff99; border: 1px solid #00ff99; }
.signal-buy         { background: #002211; color: #00e896; border: 1px solid #00e896; }
.signal-hold        { background: #1a1500; color: #ffcc00; border: 1px solid #ffcc00; }
.signal-watch       { background: #1a0e00; color: #ff9944; border: 1px solid #ff9944; }
.signal-sell        { background: #1a0008; color: #ff4466; border: 1px solid #ff4466; }

/* ── News item ── */
.news-item {
    background: #0f1825;
    border: 1px solid #1a2d42;
    border-left: 3px solid #00d4ff;
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.news-title {
    font-size: 0.9rem;
    color: #c8d8e8;
    margin-bottom: 4px;
}
.news-meta {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #3a6080;
    letter-spacing: 0.05em;
}
.news-link {
    color: #00d4ff;
    text-decoration: none;
}
.news-link:hover { text-decoration: underline; }

/* ── AI reasoning box ── */
.ai-reasoning {
    background: #080e18;
    border: 1px solid #1e3050;
    border-radius: 8px;
    padding: 18px 22px;
    margin-top: 1rem;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #8ba7c4;
}
.ai-reasoning b { color: #c8d8e8; }

/* ── Score bar ── */
.score-row {
    display: flex;
    align-items: center;
    margin: 6px 0;
    gap: 10px;
}
.score-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #3a6080;
    width: 100px;
    flex-shrink: 0;
}
.score-bar-bg {
    flex: 1;
    height: 6px;
    background: #1a2d42;
    border-radius: 3px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}
.score-num {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #c8d8e8;
    width: 35px;
    text-align: right;
}

/* ── Streamlit overrides ── */
div[data-testid="metric-container"] {
    background: #0f1825;
    border: 1px solid #1a2d42;
    border-radius: 8px;
    padding: 12px 16px;
}
.stSelectbox label, .stTextInput label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: #3a6080 !important;
    text-transform: uppercase;
}
.stButton > button {
    background: linear-gradient(135deg, #003355, #006699);
    color: #00d4ff;
    border: 1px solid #006699;
    border-radius: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    width: 100%;
    padding: 10px;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #004466, #0088bb);
    border-color: #00d4ff;
    box-shadow: 0 0 15px rgba(0,212,255,0.2);
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


def fetch_news_rss(ticker: str, company_name: str = "", max_items: int = 5) -> list:
    """透過 Google News RSS 抓取新聞（免 API Key）"""
    query = company_name if company_name and company_name != ticker else ticker
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(url)
        news = []
        for entry in feed.entries[:max_items]:
            published = ""
            if hasattr(entry, "published"):
                try:
                    dt = datetime(*entry.published_parsed[:6])
                    published = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    published = entry.get("published", "")
            news.append({
                "title": entry.get("title", "No title"),
                "link":  entry.get("link", "#"),
                "published": published,
                "source": entry.get("source", {}).get("title", "Google News"),
            })
        return news
    except Exception as e:
        return [{"title": f"新聞抓取失敗: {e}", "link": "#", "published": "", "source": ""}]


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
        height=760,
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["paper"],
        font=dict(family="Space Mono, monospace", color=COLORS["text"], size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=COLORS["grid"],
            borderwidth=1,
            font=dict(size=10),
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0d1220",
            bordercolor=COLORS["grid"],
            font=dict(family="Space Mono", size=11),
        ),
        title=dict(
            text=f"<b>{ticker}</b>  Interactive Chart",
            font=dict(size=13, color=COLORS["ma20"]),
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
    news: list,
) -> dict:
    """
    綜合評分系統
    技術面 40% + 基本面 35% + 消息面 25%
    返回信號、各分面得分與文字說明
    """
    reasons = []
    tech_score  = 0   # -10 ~ +10
    fund_score  = 0
    news_score  = 0

    signals = get_technical_signals(df) if not df.empty else {}

    # ── Technical (40%) ──
    rsi_data = signals.get("rsi")
    if rsi_data:
        label, tone, val = rsi_data
        if tone == "positive":
            tech_score += 4
            reasons.append(f"RSI={val:.1f} — 超賣區間，潛在反彈機會")
        elif tone == "negative":
            tech_score -= 3
            reasons.append(f"RSI={val:.1f} — 超買區間，注意短線回調風險")
        else:
            reasons.append(f"RSI={val:.1f} — 中性區間")

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

    # ── News Sentiment (25%) — keyword heuristic ──
    POSITIVE_KW = ["surge", "beat", "record", "growth", "profit", "upgrade",
                   "rally", "gain", "strong", "buy", "outperform", "launch",
                   "partnership", "deal", "innovation"]
    NEGATIVE_KW = ["drop", "fall", "loss", "miss", "cut", "downgrade",
                   "recall", "lawsuit", "fraud", "crash", "decline",
                   "layoff", "bankruptcy", "concern", "risk", "sell"]

    pos_count = neg_count = 0
    for item in news:
        title_lower = item.get("title", "").lower()
        pos_count += sum(1 for k in POSITIVE_KW if k in title_lower)
        neg_count += sum(1 for k in NEGATIVE_KW if k in title_lower)

    net = pos_count - neg_count
    if net >= 3:
        news_score = 4
        reasons.append(f"近期新聞正面情緒主導（+{pos_count} / -{neg_count}）")
    elif net >= 1:
        news_score = 2
        reasons.append(f"近期新聞略偏正面（+{pos_count} / -{neg_count}）")
    elif net == 0:
        news_score = 0
        reasons.append("近期新聞情緒中性")
    elif net >= -2:
        news_score = -2
        reasons.append(f"近期新聞略偏負面（+{pos_count} / -{neg_count}）")
    else:
        news_score = -4
        reasons.append(f"近期新聞負面情緒主導（+{pos_count} / -{neg_count}）")

    news_score = max(-10, min(10, news_score))

    # ── Composite Score ──
    composite = tech_score * 0.40 + fund_score * 0.35 + news_score * 0.25
    # composite range roughly -10 ~ +10

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

    return {
        "signal":       signal,
        "signal_class": signal_class,
        "composite":    round(composite, 2),
        "tech_score":   tech_score,
        "fund_score":   fund_score,
        "news_score":   news_score,
        "reasons":      reasons,
    }


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
    <div style="font-family:'Space Mono',monospace; font-size:1.3rem; font-weight:700;
         color:#00d4ff; letter-spacing:0.15em; margin-bottom:0.2rem;">
        📈 ALPHA<span style="color:#ff4466;">STREAM</span>
    </div>
    <div style="font-family:'Space Mono',monospace; font-size:0.6rem; color:#3a6080;
         letter-spacing:0.3em; margin-bottom:1.5rem;">QUANT ANALYSIS TERMINAL</div>
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
    <div style="margin-top:2rem; font-family:'Space Mono',monospace; font-size:0.58rem;
         color:#1e2d45; line-height:1.8; letter-spacing:0.05em;">
    ⚠ 本工具僅供學術研究<br>
    與個人參考，不構成<br>
    任何投資建議。<br><br>
    數據來源：Yahoo Finance<br>
    Google News RSS
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
    <div style="text-align:center; padding:60px 0; color:#1e2d45;
         font-family:'Space Mono',monospace; font-size:0.9rem; letter-spacing:0.2em;">
        ← 在左側輸入股票代號，點擊「開始分析」
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Fetch all data ───
with st.spinner("載入中…"):
    df_raw      = fetch_price_history(ticker_input, period)
    fundamentals = fetch_fundamentals(ticker_input)
    company_name = fundamentals.get("name", ticker_input)
    news_list   = fetch_news_rss(ticker_input, company_name)

if df_raw.empty:
    st.error(f"找不到 **{ticker_input}** 的數據，請確認代號是否正確。台股請加 `.TW`，例如 `2330.TW`。")
    st.stop()

df = compute_indicators(df_raw.copy())
decision = compute_decision(df, fundamentals, news_list)

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
<div style="display:flex; align-items:baseline; gap:16px; margin-bottom:0.4rem;">
  <div style="font-family:'Space Mono',monospace; font-size:2rem; font-weight:700; color:#e0f0ff;">
    {price_str}
    <span style="font-size:0.85rem; color:#3a6080; margin-left:4px;">{currency}</span>
  </div>
  <div style="font-family:'Space Mono',monospace; font-size:1rem; color:{chg_color};">
    {chg_str}
  </div>
</div>
<div style="font-family:'Space Mono',monospace; font-size:0.75rem; color:#3a6080;
     letter-spacing:0.1em; margin-bottom:1.2rem;">
  {company_name} &nbsp;·&nbsp; {fundamentals.get('sector','—')} &nbsp;·&nbsp;
  市值 {fmt_market_cap(fundamentals.get('market_cap'))}
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION B: FUNDAMENTAL METRICS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">基本面指標</div>', unsafe_allow_html=True)

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

# ─────────────────────────────────────────────
# SECTION C: CHART
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">技術分析圖表</div>', unsafe_allow_html=True)
fig = build_chart(df, ticker_input)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

# ─────────────────────────────────────────────
# SECTION D: NEWS + DECISION (side by side)
# ─────────────────────────────────────────────
col_news, col_decision = st.columns([1.1, 0.9], gap="large")

with col_news:
    st.markdown('<div class="section-header">最新消息面</div>', unsafe_allow_html=True)
    if news_list:
        for item in news_list:
            src = f"· {item['source']}" if item.get("source") else ""
            pub = item.get("published", "")
            st.markdown(f"""
            <div class="news-item">
              <div class="news-title">
                <a href="{item['link']}" target="_blank" class="news-link">{item['title']}</a>
              </div>
              <div class="news-meta">{pub} {src}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#3a6080; font-size:0.85rem;">無法獲取新聞資料。</div>', unsafe_allow_html=True)

with col_decision:
    st.markdown('<div class="section-header">AI 綜合決策</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin:0.5rem 0 1rem 0;">
      <span class="signal-badge {decision['signal_class']}">{decision['signal']}</span>
    </div>
    """, unsafe_allow_html=True)

    # Score bars
    st.markdown("<div style='margin:0.5rem 0;'>", unsafe_allow_html=True)
    for label, score in [
        ("技術面 ×40%", decision["tech_score"]),
        ("基本面 ×35%", decision["fund_score"]),
        ("消息面 ×25%", decision["news_score"]),
        ("綜合得分",    decision["composite"]),
    ]:
        st.markdown(f"""
        <div class="score-row">
          <div class="score-label" style="font-family:'Space Mono',monospace; font-size:0.62rem;
               color:#3a6080; width:90px; flex-shrink:0;">{label}</div>
          {score_to_bar(score)}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Reasoning
    reasons_html = "".join(f"<div>• {r}</div>" for r in decision["reasons"])
    st.markdown(f"""
    <div class="ai-reasoning">
      <b>分析依據：</b>
      <div style="margin-top:8px; font-size:0.83rem; line-height:1.9;">{reasons_html}</div>
      <div style="margin-top:12px; font-size:0.72rem; color:#1e3050; border-top:1px solid #1e3050; padding-top:8px;">
        綜合評分 = 技術×0.4 + 基本面×0.35 + 消息×0.25 ｜ 範圍 -10 ~ +10
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div style="margin-top:3rem; text-align:center; font-family:'Space Mono',monospace;
     font-size:0.6rem; color:#1a2d42; letter-spacing:0.15em;">
  ALPHASTREAM v1.0 &nbsp;·&nbsp; 數據來源：Yahoo Finance / Google News &nbsp;·&nbsp;
  最後更新：{last_update} &nbsp;·&nbsp; ⚠ 本工具不構成投資建議
</div>
""", unsafe_allow_html=True)
