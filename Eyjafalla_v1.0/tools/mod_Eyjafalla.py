import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ⚙️ 全局配置 (Constants)
# 交易记录配色
# Colors of the trading record
EMOJI_CONFIGS = [
    {'Buy': '🟢', 'Sell': '🔴', 'Buy_offset': 1.05, 'Sell_offset': 1.05,
     'Profit_Color': 'rgba(76, 175, 80, 0.8)', 'Loss_Color': 'rgba(244, 67, 54, 0.8)',
     'NAV_Color': '#4CAF50'},  # 策略 1 / Strategy 1
    {'Buy': '🔵', 'Sell': '🟡', 'Buy_offset': 1.10, 'Sell_offset': 1.10,
     'Profit_Color': 'rgba(33, 150, 243, 0.8)', 'Loss_Color': 'rgba(255, 235, 59, 0.8)',
     'NAV_Color': '#2196F3'},  # 策略 2 / Strategy 2
    {'Buy': '🟣', 'Sell': '🟠', 'Buy_offset': 1.15, 'Sell_offset': 1.15,
     'Profit_Color': 'rgba(156, 39, 176, 0.8)', 'Loss_Color': 'rgba(255, 152, 0, 0.8)',
     'NAV_Color': '#9C27B0'},  # 策略 3 / Strategy 3
]

# 📍 图层1：基础K线图层 （高开低收）
# 📍 Layer1: Basic K lines (OHLC)
def _add_kline_layer(fig, df):

    fig.add_trace(go.Candlestick(
        x=df['Open Time'],
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="K line (OHLC)",
        increasing_line_color='#26A69A',
        decreasing_line_color='#EF5350'
    ), row=1, col=1)

# 📍 图层2：可选-技术指标图层
# 📍 Layer2: Techinal indicators (optional)
def _add_technical_indicators(fig, df):

    ma_cols = [c for c in df.columns if c.startswith(('MA5', 'Weekly_MA20'))]
    # 选择要显示的指标（确保featurestore.csv中有对应的列）
    # Select the indicators to be shown (make sure the certain columns exist in the featurestore.csv )

    # 2.1 均线指标 MA
    for col in ma_cols:
        fig.add_trace(go.Scatter(
            x=df['Open Time'], y=df[col],
            mode='lines', name=f"指标: {col}",
            line=dict(color='rgba(256, 256, 256, 0.5)', width=1.5)
        ), row=1, col=1)

    # 2.2 布林带指标 BOLL
    if 'BOLL_UB' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Open Time'], y=df['BOLL_UB'], mode='lines', name="BOLL UB",
            line=dict(color='rgba(255, 165, 0, 0.7)', width=1)
        ), row=1, col=1)
    if 'BOLL_LB' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Open Time'], y=df['BOLL_LB'], mode='lines', name="BOLL LB",
            fill='tonexty', fillcolor='rgba(255, 165, 0, 0.05)',
            line=dict(color='rgba(255, 165, 0, 0.7)', width=1)
        ), row=1, col=1)
    if 'BOLL_MB' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Open Time'], y=df['BOLL_MB'], mode='lines', name="BOLL MB",
            line=dict(color='rgba(255, 255, 255, 0.5)', width=1, dash='dash')
        ), row=1, col=1)
    # 如需添加自定义指标，按照类似语法续写
    # To add a customized indicator, just continue writing below

# 📍 图层3：可选-买卖点记录
# 📍 Layer3: Trading records (optional)
def _add_strategy_layers(fig, trades_list):
    if not trades_list or not isinstance(trades_list, list):
        return

    for idx, strat in enumerate(trades_list[:3]):
        strat_name = strat.get('name', f"策略_{idx + 1}")
        trade_df = strat.get('df', pd.DataFrame()).copy()
        nav_df = strat.get('nav_df', pd.DataFrame()).copy()
        emoji_cfg = EMOJI_CONFIGS[idx]

        # 3.1 绘制买卖点与盈亏连线 / Trading Spot
        if not trade_df.empty and 'Trade Time' in trade_df.columns:
            trade_df['Trade Time'] = pd.to_datetime(trade_df['Trade Time'])
            buys = trade_df[trade_df['Action'] == 'Buy']
            sells = trade_df[trade_df['Action'] == 'Sell']

            # 买入点 / Buy
            if not buys.empty:
                fig.add_trace(go.Scatter(
                    x=buys['Trade Time'], y=buys['Price'] * emoji_cfg['Buy_offset'],
                    mode='text', text=[emoji_cfg['Buy']] * len(buys), textfont=dict(size=13),
                    name=f"[{strat_name}] 买入", hovertext=[f"买入价: {p}" for p in buys['Price']]
                ), row=1, col=1)

            # 卖出点 / Sell
            if not sells.empty:
                fig.add_trace(go.Scatter(
                    x=sells['Trade Time'], y=sells['Price'] * emoji_cfg['Sell_offset'],
                    mode='text', text=[emoji_cfg['Sell']] * len(sells), textfont=dict(size=13),
                    name=f"[{strat_name}] 卖出", hovertext=[f"卖出价: {p}" for p in sells['Price']]
                ), row=1, col=1)

            # 盈亏周期 / Win or Loss
            if 'Position' in trade_df.columns:
                trade_df = trade_df.sort_values('Trade Time').reset_index(drop=True)
                p_x, p_y, l_x, l_y = [], [], [], []
                buy_record = None

                for _, row in trade_df.iterrows():
                    if row['Action'] == 'Buy':
                        buy_record = row
                    elif row['Action'] == 'Sell' and buy_record is not None:
                        is_profit = row['Position'] > buy_record['Position']
                        y_level = buy_record['Price'] * (emoji_cfg['Buy_offset'] - 0.2)
                        target_x, target_y = (p_x, p_y) if is_profit else (l_x, l_y)
                        target_x.extend([buy_record['Trade Time'], row['Trade Time'], None])
                        target_y.extend([y_level, y_level, None])
                        buy_record = None

                if p_x: fig.add_trace(go.Scatter(x=p_x, y=p_y, mode='lines', line=dict(color=emoji_cfg['Profit_Color'], width=3), name=f"[{strat_name}] 盈利"), row=1, col=1)
                if l_x: fig.add_trace(go.Scatter(x=l_x, y=l_y, mode='lines', line=dict(color=emoji_cfg['Loss_Color'], width=3), name=f"[{strat_name}] 亏损"), row=1, col=1)

        # 3.2 绘制NAV净值曲线 / NAV Curve
        if not nav_df.empty and 'NAV' in nav_df.columns:
            nav_x = pd.to_datetime(nav_df['Trade Date']) if 'Trade Date' in nav_df.columns else pd.to_datetime(nav_df.index)
            fig.add_trace(go.Scatter(
                x=nav_x, y=nav_df['NAV'], mode='lines',
                name=f"[{strat_name}] NAV", line=dict(color=emoji_cfg['NAV_Color'], width=2)
            ), row=2, col=1)


# 📍 图层4：可选-市场状态背景图层
# 📍 Layer4: Market State (Chaos or Order) (optional)
def _add_hmm_background(fig, df):
    if 'Market State' not in df.columns:
        return

    print("  └─ [图层] 渲染背景色块...")
    state_colors = {0: 'rgba(244, 67, 54, 0.12)', 1: 'rgba(76, 175, 80, 0.12)'}
    df['state_block'] = (df['Market State'] != df['Market State'].shift()).cumsum()

    for _, block in df.groupby('state_block'):
        st_val = block['Market State'].iloc[0]
        if st_val in state_colors:
            fig.add_vrect(
                x0=str(block['Open Time'].iloc[0]), x1=str(block['Open Time'].iloc[-1]),
                fillcolor=state_colors[st_val], opacity=1.0, layer="below", line_width=0,
                row="all", col="all"
            )

# 🚀 模块 2: 主调度器 (Orchestrator)
def plot_layered_kline(df_kline, trades_list=None, output_html="backtest_report_v2.html", title="量化多图层可视化"):
    print(f"📊 正在生成多图层可视化报表: {title}...")

    # 1. 全局数据预处理
    df_kline = df_kline.copy()
    df_kline['Open Time'] = pd.to_datetime(df_kline['Open Time'])

    has_nav = False
    if trades_list:
        for strat in trades_list:

            if not strat.get('nav_df', pd.DataFrame()).empty:
                has_nav = True
                break

    # 动态配置画布行数与高度比例
    plot_rows = 2 if has_nav else 1
    plot_heights = [0.75, 0.25] if has_nav else [1.0]

    # 2. 初始化子图画布
    fig = make_subplots(
        rows=plot_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=plot_heights
    )

    # 3. 乐高式图层拼装 (按层级依次渲染)
    _add_kline_layer(fig, df_kline)
    _add_technical_indicators(fig, df_kline)
    _add_strategy_layers(fig, trades_list)
    _add_hmm_background(fig, df_kline)

    # 4. 全局样式设置
    fig.update_layout(
        title=title,
        template="plotly_dark",
        xaxis_rangeslider_visible=not has_nav,
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0.5)"),
        margin=dict(l=40, r=40, t=50, b=40)
    )

    # 5. 输出文件
    fig.write_html(output_html)
    print(f"✅ 图层整合完毕！HTML 已生成: {output_html}")


def draw_kline(kline_csv_path, strategies_config, output_html="KlineNAVTrade.html",
                                 title="Quant_Backtesting_Visiual(Eyjafalla_v1.0)"):

    print(f"📂 开始读取主数据源: {kline_csv_path}")
    if not os.path.exists(kline_csv_path):
        raise FileNotFoundError(f"找不到 K 线主数据文件: {kline_csv_path}")

    df_kline = pd.read_csv(kline_csv_path)

    trades_list = []

    # 自动解析策略文件夹
    for strat in strategies_config:
        strat_name = strat.get('name', '未命名策略')
        folder_path = strat.get('folder', '')

        # 默认约定的文件名
        trade_csv = os.path.join(folder_path,"trade.csv")
        nav_csv = os.path.join(folder_path,"nav.csv")

        # 构建给绘图核心的数据字典
        strat_dict = {'name': strat_name, 'df': pd.DataFrame(), 'nav_df': pd.DataFrame()}

        # 尝试加载trade.csv (买卖点)
        if os.path.exists(trade_csv):
            strat_dict['df'] = pd.read_csv(trade_csv)
            print(f"  ├─ 载入买卖点: [{strat_name}] -> {trade_csv}")
        else:
            print(f"  ├─ ⚠️ 未找到买卖点: [{strat_name}] -> {trade_csv} (跳过)")

        # 尝试加载 nav.csv (净值曲线，可选)
        if os.path.exists(nav_csv):
            strat_dict['nav_df'] = pd.read_csv(nav_csv)
            print(f"  ├─ 载入净值: [{strat_name}] -> {nav_csv}")
        else:
            print(f"  ├─ ⚠️ 未找到净值数据: [{strat_name}] ")

        trades_list.append(strat_dict)

    print("-" * 40)
    # 调用绘图核心
    plot_layered_kline(
        df_kline=df_kline,
        trades_list=trades_list,
        output_html=output_html,
        title=title
    )

    return os.path.abspath(output_html)
