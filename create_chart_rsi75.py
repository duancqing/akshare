import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 使用英文标签避免字体问题
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

print("正在加载回测数据...")

# 加载回测结果
portfolio_df = pd.read_csv("回测结果_买入RSI75卖出.csv")
trade_df = pd.read_csv("交易记录_买入RSI75卖出.csv")
portfolio_df['日期'] = pd.to_datetime(portfolio_df['日期'])
trade_df['日期'] = pd.to_datetime(trade_df['日期'])

# 加载指数数据
df = pd.read_csv("931446_真实数据_20200424至今.csv")
df['日期'] = pd.to_datetime(df['日期'])
df['MA250'] = df['收盘'].rolling(window=250).mean()

# 计算RSI
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
df['RSI'] = calculate_rsi(df['收盘'])

# 买入持有基准
start_idx = 250
bh_values = 100000 * (df['收盘'].iloc[start_idx:] / df['收盘'].iloc[start_idx])

print("正在生成图表...")

# 分离买入和卖出交易
buy_trades = trade_df[trade_df['操作'] == '买入']
sell_trades = trade_df[trade_df['操作'] == '卖出']

# 创建大图
fig = plt.figure(figsize=(18, 16))
gs = fig.add_gridspec(5, 1, hspace=0.35, height_ratios=[2.5, 1.5, 1, 1, 1])

# 1. 组合市值对比（带买卖点标记）
ax1 = fig.add_subplot(gs[0])
ax1.plot(portfolio_df['日期'], portfolio_df['持仓市值'], 
         label='Buy + RSI75 Sell Strategy', linewidth=2.5, color='#2E86AB')
ax1.plot(df['日期'].iloc[start_idx:], bh_values, 
         label='Buy & Hold', linewidth=2.5, color='#A23B72', alpha=0.8)
ax1.axhline(y=100000, color='gray', linestyle='--', 
            label='Initial Capital 100K', alpha=0.6, linewidth=1.5)

# 标记买入点
if len(buy_trades) > 0:
    buy_dates = buy_trades['日期']
    buy_prices_portfolio = []
    for date in buy_dates:
        idx = portfolio_df[portfolio_df['日期'] == date].index[0]
        buy_prices_portfolio.append(portfolio_df['持仓市值'].iloc[idx])
    
    ax1.scatter(buy_dates, buy_prices_portfolio, 
                color='green', marker='^', s=150, zorder=5,
                edgecolors='black', linewidth=1.5, 
                label=f'Buy Points ({len(buy_trades)} times)')

# 标记卖出点
if len(sell_trades) > 0:
    sell_dates = sell_trades['日期']
    sell_prices_portfolio = []
    for date in sell_dates:
        idx = portfolio_df[portfolio_df['日期'] == date].index[0]
        sell_prices_portfolio.append(portfolio_df['持仓市值'].iloc[idx])
    
    ax1.scatter(sell_dates, sell_prices_portfolio, 
                color='red', marker='v', s=150, zorder=5,
                edgecolors='black', linewidth=1.5, 
                label=f'Sell Points ({len(sell_trades)} times)')

ax1.set_title('Portfolio Value Comparison (2020.4.24 - 2026.6.2)', fontsize=18, pad=20, weight='bold')
ax1.set_ylabel('Value (Yuan)', fontsize=14)
ax1.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax1.set_ylim([95000, 150000])

# 添加收益率标注
ax1.text(0.98, 0.95, 'Strategy: 7.56%\nBuy&Hold: 41.18%\nDifference: -33.62%', 
         transform=ax1.transAxes, fontsize=12,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))

# 2. 指数价格与MA250（带买卖点）
ax2 = fig.add_subplot(gs[1])
ax2.plot(df['日期'], df['收盘'], 
         label='Index Price', linewidth=2, color='#2E86AB')
ax2.plot(df['日期'], df['MA250'], 
         label='MA250 (Annual Line)', linewidth=2, color='#F18F01', alpha=0.8)

# 标记买入点价格
if len(buy_trades) > 0:
    ax2.scatter(buy_trades['日期'], buy_trades['价格'], 
                color='green', marker='^', s=100, zorder=5,
                edgecolors='black', linewidth=1.2)

# 标记卖出点价格
if len(sell_trades) > 0:
    ax2.scatter(sell_trades['日期'], sell_trades['价格'], 
                color='red', marker='v', s=100, zorder=5,
                edgecolors='black', linewidth=1.2)

ax2.set_title('Index 931446 Price & MA250 with Buy/Sell Points', fontsize=16, pad=15, weight='bold')
ax2.set_ylabel('Price', fontsize=14)
ax2.legend(loc='upper left', fontsize=11)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

# 3. RSI指标（带买卖点）
ax3 = fig.add_subplot(gs[2])
ax3.plot(df['日期'], df['RSI'], 
         label='RSI(14)', linewidth=2, color='#9467BD')
ax3.axhline(y=75, color='red', linestyle='--', label='Sell Threshold 75', alpha=0.7, linewidth=2)
ax3.axhline(y=30, color='green', linestyle='--', label='Oversold 30', alpha=0.5)
ax3.axhline(y=70, color='orange', linestyle=':', label='Overbought 70', alpha=0.5)
ax3.fill_between(df['日期'], df['RSI'], 75, where=df['RSI']>75, 
                 color='red', alpha=0.3, label='RSI > 75 (Sell Zone)')

# 标记买入点RSI
if len(buy_trades) > 0:
    ax3.scatter(buy_trades['日期'], buy_trades['RSI'], 
                color='green', marker='^', s=80, zorder=5,
                edgecolors='black', linewidth=1)

# 标记卖出点RSI
if len(sell_trades) > 0:
    ax3.scatter(sell_trades['日期'], sell_trades['RSI'], 
                color='red', marker='v', s=80, zorder=5,
                edgecolors='black', linewidth=1)

ax3.set_title('RSI Indicator with Sell Signals (RSI > 75)', fontsize=16, pad=15, weight='bold')
ax3.set_ylabel('RSI', fontsize=14)
ax3.set_ylim([0, 100])
ax3.legend(loc='upper left', fontsize=10)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

# 4. 累计投入与持仓
ax4 = fig.add_subplot(gs[3])
ax4.plot(portfolio_df['日期'], portfolio_df['累计投入'], 
         label='Cumulative Investment', linewidth=2, color='#C73E1D')
ax4.plot(portfolio_df['日期'], portfolio_df['现金'], 
         label='Remaining Cash', linewidth=2, color='#3A7D44', alpha=0.7)
ax4.fill_between(portfolio_df['日期'], portfolio_df['累计投入'], 0, 
                 color='#C73E1D', alpha=0.2)

ax4.set_title('Capital Usage (Reset after each Sell)', fontsize=16, pad=15, weight='bold')
ax4.set_ylabel('Amount (Yuan)', fontsize=14)
ax4.legend(loc='upper left', fontsize=11)
ax4.grid(True, alpha=0.3, linestyle='--')
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

# 5. 回撤曲线
ax5 = fig.add_subplot(gs[4])
cummax = portfolio_df['持仓市值'].cummax()
drawdown = (portfolio_df['持仓市值'] - cummax) / cummax * 100

ax5.plot(portfolio_df['日期'], drawdown, 
         label='Strategy Drawdown', linewidth=2, color='#C73E1D')
ax5.fill_between(portfolio_df['日期'], drawdown, 0, 
                 color='#C73E1D', alpha=0.3)

max_dd = drawdown.min()
ax5.axhline(y=max_dd, color='red', linestyle=':', 
            linewidth=1.5, alpha=0.7, label=f'Max Drawdown: {max_dd:.2f}%')

ax5.set_title('Drawdown Curve', fontsize=16, pad=15, weight='bold')
ax5.set_ylabel('Drawdown (%)', fontsize=14)
ax5.legend(loc='lower left', fontsize=11)
ax5.grid(True, alpha=0.3, linestyle='--')
ax5.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax5.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

plt.tight_layout()
plt.savefig('回测对比图_买入RSI75卖出.png', dpi=150, bbox_inches='tight')
print("✅ 图表已保存: 回测对比图_买入RSI75卖出.png")

# 创建汇总表
fig2, ax = plt.subplots(figsize=(12, 5))
ax.axis('off')

summary_data = [
    ['Metric', 'Buy+RSI75 Sell', 'Buy & Hold', 'Difference'],
    ['Final Value', '107,558 Yuan', '141,178 Yuan', '-33,620 Yuan'],
    ['Return', '7.56%', '41.18%', '-33.62%'],
    ['Max Drawdown', '-3.50%', 'N/A', 'Good Control'],
    ['Buy Count', '28 times', '1 time', 'Frequent'],
    ['Sell Count', '11 times', '0 time', 'Too Early'],
    ['Cash Remaining', '38,096 Yuan', '0 Yuan', 'Not Full Position']
]

table = ax.table(cellText=summary_data, cellLoc='center', loc='center',
                 colWidths=[0.25, 0.25, 0.25, 0.25])
table.auto_set_font_size(False)
table.set_fontsize(14)
table.scale(1.2, 2.5)

# 设置表头样式
for i in range(4):
    table[(0, i)].set_facecolor('#2E86AB')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置差异列（红色表示问题）
for i in range(1, 7):
    table[(i, 3)].set_facecolor('#FFCDD2')  # 浅红色

plt.title('Backtest Summary - Strategy FAILED (2020.4.24 - 2026.6.2)', 
          fontsize=18, pad=20, weight='bold', color='red')
plt.savefig('回测结果汇总表_买入RSI75卖出.png', dpi=150, bbox_inches='tight')
print("✅ 汇总表已保存: 回测结果汇总表_买入RSI75卖出.png")

print("\n完成！图表已生成。")
print("\n⚠️ 策略表现不佳，建议不要使用RSI>75卖出条件！")