import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

# 1. 페이지 설정 및 테마 최적화
st.set_page_config(layout="wide", page_title="Asset Flow Canvas")

# ==========================================
# [신규 추가] 팀 전용 보안 암호 시스템
# ==========================================
TEAM_PASSWORD = "jsgglobal"  # 이 부분에 원하시는 팀 전용 암호를 설정하세요!
entered_password = st.sidebar.text_input("🔒 시스템 접속 암호", type="password")

if entered_password != TEAM_PASSWORD:
    st.title("🔒 Asset Flow Canvas (보안 시스템)")
    st.warning("이 시스템은 인가된 팀원만 접근할 수 있습니다. 좌측 사이드바에 암호를 입력해 주세요.")
    st.stop()  # 암호가 틀리면 여기서 코드 실행을 완전히 멈추고 아래 화면을 그리지 않습니다!
# ==========================================

st.markdown("""
    <style>
    .main { background-color: #f8fafc; color: #000000; }
    h1, h2, h3, p, span, div, label, li { 
        color: #000000 !important; 
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    }
    div[data-testid="stSidebar"] { 
        background-color: #ffffff; 
        border-right: 1px solid #e2e8f0; 
    }
    .stDataFrame { border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Asset Flow Canvas: Strategic Intelligence")

# 2. 11개 섹터 정의 및 색상 맵핑
sector_map = {
    'Technology': {'ticker': 'XLK', 'color': 'rgba(31, 119, 180, 0.8)'},
    'Energy': {'ticker': 'XLE', 'color': 'rgba(255, 127, 14, 0.8)'},
    'Financials': {'ticker': 'XLF', 'color': 'rgba(44, 160, 44, 0.8)'},
    'Health Care': {'ticker': 'XLV', 'color': 'rgba(214, 39, 40, 0.8)'},
    'Industrials': {'ticker': 'XLI', 'color': 'rgba(148, 103, 189, 0.8)'},
    'Materials': {'ticker': 'XLB', 'color': 'rgba(140, 86, 75, 0.8)'},
    'Cons Disc': {'ticker': 'XLY', 'color': 'rgba(227, 119, 194, 0.8)'},
    'Cons Staples': {'ticker': 'XLP', 'color': 'rgba(127, 127, 127, 0.8)'},
    'Real Estate': {'ticker': 'XLRE', 'color': 'rgba(188, 189, 34, 0.8)'},
    'Utilities': {'ticker': 'XLU', 'color': 'rgba(23, 190, 207, 0.8)'},
    'Communication': {'ticker': 'XLC', 'color': 'rgba(31, 119, 180, 0.8)'}
}

stock_map = {
    'Technology': ['AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL'],
    'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
    'Financials': ['JPM', 'BAC', 'GS', 'MS', 'WFC'],
    'Health Care': ['UNH', 'JNJ', 'LLY', 'ABBV', 'MRK'],
    'Industrials': ['CAT', 'HON', 'GE', 'UPS', 'LMT'],
    'Materials': ['LIN', 'SHW', 'NEM', 'APD', 'FCX'],
    'Cons Disc': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE'],
    'Cons Staples': ['WMT', 'PG', 'KO', 'PEP', 'COST'],
    'Real Estate': ['PLD', 'AMT', 'EQIX', 'CCI', 'PSA'],
    'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP'],
    'Communication': ['GOOGL', 'META', 'NFLX', 'TMUS', 'DIS']
}

# 3. 왼쪽 영역 (사이드바)
with st.sidebar:
    # 문구 변경 적용
    st.header("🔍 Sector Money Flow Canvas 조회 기간")
    start_date = st.date_input("시작일", date.today() - timedelta(days=60))
    end_date = st.date_input("종료일", date.today())
    
    st.divider()
    
    st.header("🎯 섹터별 수혜주 필터")
    selected_sector = st.selectbox("수동으로 조회할 섹터를 선택하세요", list(sector_map.keys()))
    
    st.divider()
    
    st.header("📈 주단위 흐름 설정")
    weekly_months = st.slider("추세 조회 기간 (개월)", min_value=1, max_value=12, value=6, step=1)

# 4. 데이터 엔진
@st.cache_data
def get_performance(tickers, start, end):
    df = yf.download(tickers, start=start, end=end, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df = df['Close']
    if df.empty or len(df) < 2:
        return pd.Series(0, index=tickers)
    returns = ((df.iloc[-1] - df.iloc[0]) / df.iloc[0]) * 100
    return returns.fillna(0)

all_sector_tickers = [v['ticker'] for v in sector_map.values()]
sector_performance = get_performance(all_sector_tickers, start_date, end_date)

# 5. 메인 레이아웃 구성
col_left, col_right = st.columns([1.2, 2.3])

with col_left:
    st.subheader("📋 전체 섹터 요약")
    summary_data = []
    for name, info in sector_map.items():
        perf = sector_performance.get(info['ticker'], 0)
        summary_data.append({'섹터명': name, '수익률(%)': float(perf)})
    
    summary_df = pd.DataFrame(summary_data).sort_values(by='수익률(%)', ascending=False)
    st.dataframe(
        summary_df.style.format({'수익률(%)': '{:+.2f}%'}).background_gradient(cmap='RdYlGn', subset=['수익률(%)']),
        hide_index=True, use_container_width=True, height=350
    )
    
    st.divider()
    
    st.subheader(f"💎 {selected_sector} 수혜 종목 (수동)")
    target_stocks = stock_map[selected_sector]
    stock_performance = get_performance(target_stocks, start_date, end_date)
    
    perf_list = []
    for t in target_stocks:
        val = stock_performance.get(t, 0)
        perf_list.append({'티커': t, '기간 수익률': float(val)})
        
    stock_df = pd.DataFrame(perf_list).sort_values(by='기간 수익률', ascending=False)
    st.dataframe(
        stock_df.style.format({'기간 수익률': '{:+.2f}%'}).background_gradient(cmap='RdYlGn', subset=['기간 수익률']),
        hide_index=True, use_container_width=True
    )

with col_right:
    st.subheader("🌊 Sector Money Flow Canvas")
    
    # [설명 링크 복구] 차트 해석 가이드
    with st.expander("💡 차트 해석 및 활용 가이드 (클릭하여 읽기)", expanded=False):
        st.markdown("""
        **1. 자금의 방향: Flow IN vs Flow OUT**
        * **Sector Flow IN:** 분석 기간 동안 수익률이 (+)인 섹터들로, 시장의 자금이 유입되는 '주도 섹터'를 의미합니다.
        * **Sector Flow OUT:** 분석 기간 동안 수익률이 (-)인 섹터들로, 현재 자금이 빠져나가는 '소외 섹터'를 뜻합니다.
        **2. 선의 굵기:** 섹터의 수익률 절댓값을 의미하며, 선이 굵을수록 해당 섹터의 거래 대금이 강력하게 쏠려 있음을 나타냅니다.
        """)
    
    labels = list(sector_map.keys()) + ["Sector Flow IN", "Sector Flow OUT"]
    node_colors = [v['color'] for v in sector_map.values()] + ['rgba(0, 51, 102, 0.9)', 'rgba(153, 0, 0, 0.9)']
    
    sources, targets, values, link_colors = [], [], [], []
    for i, (name, info) in enumerate(sector_map.items()):
        val = sector_performance.get(info['ticker'], 0)
        sources.append(i)
        targets.append(11 if val >= 0 else 12)
        values.append(abs(val) + 0.5) 
        link_colors.append(info['color'].replace('0.8)', '0.3)'))

    fig = go.Figure(data=[go.Sankey(
        node = dict(pad = 25, thickness = 30, line = dict(color = "black", width = 1), label = labels, color = node_colors),
        link = dict(source = sources, target = targets, value = values, color = link_colors)
    )])
    fig.update_layout(
        font=dict(size=16, color="black"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=450, margin=dict(t=30, b=30, l=10, r=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader(f"📅 주단위 머니 Flow 히트맵 (최근 {weekly_months}개월)")
    
    hist_start = date.today() - timedelta(days=weekly_months * 30)
    hist_df = yf.download(all_sector_tickers, start=hist_start, end=date.today(), auto_adjust=True)
    if isinstance(hist_df.columns, pd.MultiIndex):
        hist_df = hist_df['Close']
    
    weekly_price = hist_df.resample('W').last()
    weekly_flow_df = (weekly_price.pct_change() * 100).dropna()
    
    heatmap_df = weekly_flow_df.rename(columns={info['ticker']: name for name, info in sector_map.items()}).T
    
    fig_heat = px.imshow(
        heatmap_df,
        labels=dict(x="주차", y="섹터", color="수익률(%)"),
        x=[d.strftime('%Y-%m-%d') for d in heatmap_df.columns],
        y=heatmap_df.index,
        color_continuous_scale='RdBu_r', 
        aspect="auto"
    )
    fig_heat.update_layout(height=400, margin=dict(t=30, b=30, l=10, r=10))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()

    st.subheader("🔥 AI 자동 스크리닝: 자금 쏠림 1위 섹터 타깃")
    max_sector = max(sector_map.keys(), key=lambda k: abs(sector_performance.get(sector_map[k]['ticker'], 0)))
    max_perf = sector_performance.get(sector_map[max_sector]['ticker'], 0)
    st.markdown(f"현재 자금이 가장 강하게 쏠리는 섹터는 **{max_sector} (수익률 {max_perf:+.2f}%)** 입니다.")
    
    top_stocks = stock_map[max_sector]
    top_stock_performance = get_performance(top_stocks, start_date, end_date)
    
    top_perf_list = []
    for t in top_stocks:
        val = top_stock_performance.get(t, 0)
        top_perf_list.append({'티커': t, '기간 수익률': float(val)})
        
    top_stock_df = pd.DataFrame(top_perf_list).sort_values(by='기간 수익률', ascending=False)
    st.dataframe(
        top_stock_df.style.format({'기간 수익률': '{:+.2f}%'}).background_gradient(cmap='RdYlGn', subset=['기간 수익률']),
        hide_index=True, use_container_width=True
    )
