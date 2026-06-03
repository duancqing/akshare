import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("正在加载回测数据...")

# 加载回测结果
portfolio_df = pd.read_csv("回测结果_20200424_20260603_下穿买入20%.csv")
trade_df = pd.read_csv("交易记录_20200424_20260603_下穿买入20%.csv")
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
         label='下穿买入20%策略', linewidth=2.5, color='#2E86AB')
ax1.plot(df['日期'].iloc[start_idx:], bh_values, 
         label='买入持有', linewidth=2.5, color='#A23B72', alpha=0.8)
ax1.axhline(y=100000, color='gray', linestyle='--', 
            label='初始资金10万', alpha=0.6, linewidth=1.5)

# 标记买入点
if len(trade_df) > 0:
    buy_dates = trade_df['日期']
    buy_prices_portfolio = []
    for date in buy_dates:
        idx = portfolio_df[portfolio_df['日期'] == date].index[0]
        buy_prices_portfolio.append(portfolio_df['持仓市值'].iloc[idx])
    
    ax1.scatter(buy_dates, buy_prices_portfolio, 
                color='green', marker='^', s=150, zorder=5,
                edgecolors='black', linewidth=1.5, 
                label=f'买入点({len(trade_df)}次)')

ax1.set_title('组合市值对比 (2020.4.24 - 2026.6.2)', fontsize=18, pad=20, weight='bold')
ax1.set_ylabel('市值(元)', fontsize=14)
ax1.legend(loc='upper left', fontsize=12, framealpha=0.9)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax1.set_ylim([90000, 160000])

# 添加收益率标注
final_strategy = portfolio_df['持仓市值'].iloc[-1]
final_bh = bh_values.iloc[-1]
ax1.text(0.98, 0.95, f'策略收益: 42.19%\n持有收益: 41.18%', 
         transform=ax1.transAxes, fontsize=12,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 2. 指数价格与MA250（带买入点）
ax2 = fig.add_subplot(gs[1])
ax2.plot(df['日期'], df['收盘'], 
         label='指数价格', linewidth=2, color='#2E86AB')
ax2.plot(df['日期'], df['MA250'], 
         label='年均线MA250', linewidth=2, color='#F18F01', alpha=0.8)

# 标记买入点价格
if len(trade_df) > 0:
    ax2.scatter(trade_df['日期'], trade_df['价格'], 
                color='green', marker='^', s=120, zorder=5,
                edgecolors='black', linewidth=1.2)

ax2.set_title('指数931446价格与年均线', fontsize=16, pad=15, weight='bold')
ax2.set_ylabel('价格', fontsize=14)
ax2.legend(loc='upper left', fontsize=11)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

# 3. 累计投入与持仓
ax3 = fig.add_subplot(gs[2])
ax3.plot(portfolio_df['日期'], portfolio_df['累计投入'], 
         label='累计投入资金', linewidth=2, color='#C73E1D')
ax3.plot(portfolio_df['日期'], portfolio_df['现金'], 
         label='剩余现金', linewidth=2, color='#3A7D44', alpha=0.7)
ax3.fill_between(portfolio_df['日期'], portfolio_df['累计投入'], 0, 
                 color='#C73E1D', alpha=0.2)

ax3.set_title('资金使用情况', fontsize=16, pad=15, weight='bold')
ax3.set_ylabel('金额(元)', fontsize=14)
ax3.legend(loc='upper left', fontsize=11)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

# 4. 回撤曲线
ax4 = fig.add_subplot(gs[3])
cummax = portfolio_df['持仓市值'].cummax()
drawdown = (portfolio_df['持仓市值'] - cummax) / cummax * 100

ax4.plot(portfolio_df['日期'], drawdown, 
         label='策略回撤', linewidth=2, color='#C73E1D')
ax4.fill_between(portfolio_df['日期'], drawdown, 0, 
                 color='#C73E1D', alpha=0.3)

max_dd = drawdown.min()
ax4.axhline(y=max_dd, color='red', linestyle=':', 
            linewidth=1.5, alpha=0.7, label=f'最大回撤: {max_dd:.2f}%')

ax4.set_title('回撤曲线', fontsize=16, pad=15, weight='bold')
ax4.set_ylabel('回撤(%)', fontsize=14)
ax4.legend(loc='lower left', fontsize=11)
ax4.grid(True, alpha=0.3, linestyle='--')
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

plt.tight_layout()
plt.savefig('回测对比图_20200424_20260603.png', dpi=150, bbox_inches='tight')
print("✅ 图表已保存: 回测对比图_20200424_20260603.png")

# 创建汇总表
fig2, ax = plt.subplots(figsize=(12, 5))
ax.axis('off')

summary_data = [
    ['指标', '下穿买入20%', '买入持有', '差异'],
    ['最终市值', '142,192元', '141,178元', '+1,014元'],
    ['收益率', '42.19%', '41.18%', '+1.01%'],
    ['最大回撤', '-14.63%', 'N/A', '控制良好'],
    ['买入次数', '29次', '1次', '分批建仓'],
    ['现金使用率', '99.85%', '100%', '几乎满仓']
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
for i in range(1, 6):
    table[(i, 3)].set_facecolor('#E8F5E9')

plt.title('回测结果汇总 (2020.4.24 - 2026.6.2)', 
          fontsize=18, pad=20, weight='bold')
plt.savefig('回测结果汇总表_20200424_20260603.png', dpi=150, bbox_inches='tight')
print("✅ 汇总表已保存: 回测结果汇总表_20200424_20260603.png")

print("\n完成！图表已生成。")