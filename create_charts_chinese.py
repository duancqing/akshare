import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("正在加载回测数据...")

# 加载回测结果
portfolio1 = pd.read_csv("真实数据_策略1年均线.csv")
portfolio2 = pd.read_csv("真实数据_策略2RSI.csv")
portfolio1['日期'] = pd.to_datetime(portfolio1['日期'])
portfolio2['日期'] = pd.to_datetime(portfolio2['日期'])

# 加载指数数据
df = pd.read_csv("931446_真实完整历史数据.csv")
df['日期'] = pd.to_datetime(df['日期'])
df = df[df['日期'] <= '2023-12-31']

# 计算技术指标
df['MA250'] = df['收盘'].rolling(window=250).mean()
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

# 创建图表
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(4, 1, hspace=0.35, height_ratios=[2, 1, 1, 1])

# 1. 组合市值对比
ax1 = fig.add_subplot(gs[0])
ax1.plot(portfolio1['日期'], portfolio1['市值'], label='策略1: 年均线策略', linewidth=2, color='blue')
ax1.plot(portfolio2['日期'], portfolio2['市值'], label='策略2: RSI策略', linewidth=2, color='orange')
ax1.plot(df['日期'].iloc[start_idx:], bh_values, label='买入持有', linewidth=2, color='green', alpha=0.7)
ax1.axhline(y=100000, color='gray', linestyle='--', label='初始资金', alpha=0.5)
ax1.set_title('组合市值对比 (2009-2023)', fontsize=16, pad=20)
ax1.set_ylabel('市值(元)', fontsize=12)
ax1.legend(loc='best', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax1.xaxis.set_major_locator(mdates.YearLocator(2))

# 2. 指数价格与MA250
ax2 = fig.add_subplot(gs[1])
ax2.plot(df['日期'], df['收盘'], label='指数价格', linewidth=1.5, color='blue')
ax2.plot(df['日期'], df['MA250'], label='年均线MA250', linewidth=1.5, color='red', alpha=0.7)
ax2.set_title('指数931446价格与年均线', fontsize=14, pad=15)
ax2.set_ylabel('价格', fontsize=12)
ax2.legend(loc='best', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax2.xaxis.set_major_locator(mdates.YearLocator(2))

# 3. RSI指标
ax3 = fig.add_subplot(gs[2])
ax3.plot(df['日期'], df['RSI'], label='RSI(14天)', linewidth=1.5, color='purple')
ax3.axhline(y=75, color='red', linestyle='--', label='超买线75', alpha=0.5)
ax3.axhline(y=70, color='red', linestyle=':', label='超买线70', alpha=0.5)
ax3.axhline(y=30, color='green', linestyle='--', label='超卖线30', alpha=0.5)
ax3.set_title('RSI指标', fontsize=14, pad=15)
ax3.set_ylabel('RSI值', fontsize=12)
ax3.set_ylim(0, 100)
ax3.legend(loc='best', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax3.xaxis.set_major_locator(mdates.YearLocator(2))

# 4. 回撤对比
ax4 = fig.add_subplot(gs[3])
cummax1 = portfolio1['市值'].cummax()
drawdown1 = (portfolio1['市值'] - cummax1) / cummax1 * 100
cummax2 = portfolio2['市值'].cummax()
drawdown2 = (portfolio2['市值'] - cummax2) / cummax2 * 100

ax4.plot(portfolio1['日期'], drawdown1, label='策略1回撤', linewidth=1.5, color='blue')
ax4.plot(portfolio2['日期'], drawdown2, label='策略2回撤', linewidth=1.5, color='orange')
ax4.fill_between(portfolio1['日期'], drawdown1, 0, color='blue', alpha=0.2)
ax4.fill_between(portfolio2['日期'], drawdown2, 0, color='orange', alpha=0.2)
ax4.set_title('回撤对比', fontsize=14, pad=15)
ax4.set_ylabel('回撤(%)', fontsize=12)
ax4.legend(loc='best', fontsize=10)
ax4.grid(True, alpha=0.3)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax4.xaxis.set_major_locator(mdates.YearLocator(2))

plt.tight_layout()
plt.savefig('回测对比图_中文版.png', dpi=150, bbox_inches='tight')
print("✅ 图表已保存: 回测对比图_中文版.png")

# 创建汇总表
fig2, ax = plt.subplots(figsize=(12, 5))
ax.axis('off')

summary_data = [
    ['指标', '年均线策略', 'RSI策略', '买入持有'],
    ['最终市值(元)', '175,587', '163,065', '264,143'],
    ['收益率(%)', '75.59%', '63.07%', '164.14%'],
    ['最大回撤(%)', '-32.07%', '-29.12%', 'N/A'],
    ['交易次数', '95', '81', 'N/A']
]

table = ax.table(cellText=summary_data, cellLoc='center', loc='center',
                 colWidths=[0.25, 0.25, 0.25, 0.25])
table.auto_set_font_size(False)
table.set_fontsize(14)
table.scale(1.2, 2)

# 设置表头样式
for i in range(4):
    table[(0, i)].set_facecolor('#4472C4')
    table[(0, i)].set_text_props(weight='bold', color='white')

plt.title('回测结果汇总 (2009-2023)', fontsize=18, pad=20)
plt.savefig('回测结果汇总表_中文版.png', dpi=150, bbox_inches='tight')
print("✅ 汇总表已保存: 回测结果汇总表_中文版.png")

print("\n完成！中文图表已生成。")