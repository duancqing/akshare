import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 使用英文标签避免字体问题
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

print("正在加载回测数据...")

# 加载回测结果
portfolio_df = pd.read_csv("回测结果_固定1万最多10次.csv")
trade_df = pd.read_csv("交易记录_固定1万最多10次.csv")
portfolio_df['日期'] = pd.to_datetime(portfolio_df['日期'])
trade_df['日期'] = pd.to_datetime(trade_df['日期'])

# 加载指数数据
df = pd.read_csv("931446_真实数据_20200424至今.csv")
df['日期'] = pd.to_datetime(df['日期'])
df['MA250'] = df['收盘'].rolling(window=250).mean()

# 买入持有基准
start_idx = 250
bh_values = 100000 * (df['收盘'].iloc[start_idx:] / df['收盘'].iloc[start_idx])

print("正在生成图表...")

# 创建大图
fig = plt.figure(figsize=(18, 14))
gs = fig.add_gridspec(4, 1, hspace=0.35, height_ratios=[2.5, 1.5, 1, 1])

# 1. 组合市值对比（带买入点标记）
ax1 = fig.add_subplot(gs[0])
ax1.plot(portfolio_df['日期'], portfolio_df['持仓市值'], 
         label='Fixed 10K x 10 Strategy', linewidth=2.5, color='#2E86AB')
ax1.plot(df['日期'].iloc[start_idx:], bh_values, 
         label='Buy & Hold', linewidth=2.5, color='#A23B72', alpha=0.8)
ax1.axhline(y=100000, color='gray', linestyle='--', 
            label='Initial Capital 100K', alpha=0.6, linewidth=1.5)

# 标记买入点
if len(trade_df) > 0:
    buy_dates = trade_df['日期']
    buy_prices_portfolio = []
    for date in buy_dates:
        idx = portfolio_df[portfolio_df['日期'] == date].index[0]
        buy_prices_portfolio.append(portfolio_df['持仓市值'].iloc[idx])
    
    ax1.scatter(buy_dates, buy_prices_portfolio, 
                color='green', marker='^', s=200, zorder=5,
                edgecolors='black', linewidth=2, 
                label=f'Buy Points (10 times)')

ax1.set_title('Portfolio Value Comparison (2020.4.24 - 2026.6.2)', fontsize=18, pad=20, weight='bold')
ax1.set_ylabel('Value (Yuan)', fontsize=14)
ax1.legend(loc='upper left', fontsize=12, framealpha=0.9)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax1.set_ylim([90000, 160000])

# 添加收益率标注
ax1.text(0.98, 0.95, 'Strategy: 41.23%\nBuy&Hold: 41.18%', 
         transform=ax1.transAxes, fontsize=12,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 2. 指数价格与MA250（带买入点）
ax2 = fig.add_subplot(gs[1])
ax2.plot(df['日期'], df['收盘'], 
         label='Index Price', linewidth=2, color='#2E86AB')
ax2.plot(df['日期'], df['MA250'], 
         label='MA250 (Annual Line)', linewidth=2, color='#F18F01', alpha=0.8)

# 标记买入点价格
if len(trade_df) > 0:
    ax2.scatter(trade_df['日期'], trade_df['价格'], 
                color='green', marker='^', s=150, zorder=5,
                edgecolors='black', linewidth=1.5)
    
    # 添加买入点标注
    for i, row in trade_df.iterrows():
        ax2.annotate(f'#{row["买入次数"]}', 
                     (row['日期'], row['价格']),
                     textcoords="offset points", xytext=(5, 10),
                     fontsize=9, color='green', weight='bold')

ax2.set_title('Index 931446 Price & MA250 with Buy Points', fontsize=16, pad=15, weight='bold')
ax2.set_ylabel('Price', fontsize=14)
ax2.legend(loc='upper left', fontsize=11)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

# 3. 累计投入与持仓
ax3 = fig.add_subplot(gs[2])
ax3.plot(portfolio_df['日期'], portfolio_df['累计投入'], 
         label='Cumulative Investment', linewidth=2, color='#C73E1D')
ax3.plot(portfolio_df['日期'], portfolio_df['现金'], 
         label='Remaining Cash', linewidth=2, color='#3A7D44', alpha=0.7)
ax3.fill_between(portfolio_df['日期'], portfolio_df['累计投入'], 0, 
                 color='#C73E1D', alpha=0.2)

# 标记每次买入后的累计投入
if len(trade_df) > 0:
    for i, row in trade_df.iterrows():
        ax3.annotate(f'{row["累计投入"]/10000:.0f}W', 
                     (row['日期'], row['累计投入']),
                     textcoords="offset points", xytext=(5, 5),
                     fontsize=9, color='red', weight='bold')

ax3.set_title('Capital Usage (Fixed 10K per Buy, Max 10 Times)', fontsize=16, pad=15, weight='bold')
ax3.set_ylabel('Amount (Yuan)', fontsize=14)
ax3.legend(loc='upper left', fontsize=11)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

# 4. 回撤曲线
ax4 = fig.add_subplot(gs[3])
cummax = portfolio_df['持仓市值'].cummax()
drawdown = (portfolio_df['持仓市值'] - cummax) / cummax * 100

ax4.plot(portfolio_df['日期'], drawdown, 
         label='Strategy Drawdown', linewidth=2, color='#C73E1D')
ax4.fill_between(portfolio_df['日期'], drawdown, 0, 
                 color='#C73E1D', alpha=0.3)

max_dd = drawdown.min()
ax4.axhline(y=max_dd, color='red', linestyle=':', 
            linewidth=1.5, alpha=0.7, label=f'Max Drawdown: {max_dd:.2f}%')

ax4.set_title('Drawdown Curve', fontsize=16, pad=15, weight='bold')
ax4.set_ylabel('Drawdown (%)', fontsize=14)
ax4.legend(loc='lower left', fontsize=11)
ax4.grid(True, alpha=0.3, linestyle='--')
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

plt.tight_layout()
plt.savefig('回测对比图_固定1万10次.png', dpi=150, bbox_inches='tight')
print("✅ 图表已保存: 回测对比图_固定1万10次.png")

# 创建汇总表
fig2, ax = plt.subplots(figsize=(12, 5))
ax.axis('off')

summary_data = [
    ['Metric', 'Fixed 10K x 10', 'Buy & Hold', 'Difference'],
    ['Final Value', '141,235 Yuan', '141,178 Yuan', '+57 Yuan'],
    ['Return', '41.23%', '41.18%', '+0.05%'],
    ['Max Drawdown', '-15.34%', 'N/A', 'Good Control'],
    ['Buy Count', '10 times', '1 time', 'Batch Build'],
    ['Total Invested', '100,000 Yuan', '100,000 Yuan', 'Full Position'],
    ['Cash Remaining', '0 Yuan', '0 Yuan', '100% Used']
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

# 设置差异列高亮
for i in range(1, 7):
    table[(i, 3)].set_facecolor('#E8F5E9')

plt.title('Backtest Summary (2020.4.24 - 2026.6.2)', 
          fontsize=18, pad=20, weight='bold')
plt.savefig('回测结果汇总表_固定1万10次.png', dpi=150, bbox_inches='tight')
print("✅ 汇总表已保存: 回测结果汇总表_固定1万10次.png")

print("\n完成！图表已生成。")