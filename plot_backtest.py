import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
print("正在读取数据...")
data = pd.read_csv("东证红利低波动指数_931446_历史数据.csv")
data['日期'] = pd.to_datetime(data['日期'])
data = data.sort_values('日期').reset_index(drop=True)

# 计算MA250和RSI(24天)
data['MA250'] = data['收盘'].rolling(window=250).mean()

def calculate_rsi(prices, period=24):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

data['RSI'] = calculate_rsi(data['收盘'])

# 读取回测结果
portfolio_df = pd.read_csv("回测结果_组合市值_RSI24.csv")
portfolio_df['日期'] = pd.to_datetime(portfolio_df['日期'])
trade_df = pd.read_csv("回测结果_交易记录_RSI24.csv")
trade_df['日期'] = pd.to_datetime(trade_df['日期'])

print("数据读取完成！")

# 分离买入和卖出记录
buy_trades = trade_df[trade_df['操作'] == '买入']
sell_trades = trade_df[trade_df['操作'] == '卖出']

# 创建大图
fig = plt.figure(figsize=(18, 16))
gs = fig.add_gridspec(4, 1, hspace=0.35, height_ratios=[2, 1, 1, 1])

# 1. K线图（上半部分，用简单OHLC线表示）
ax1 = fig.add_subplot(gs[0])
dates = data['日期']
closes = data['收盘']

# 画出收盘价和年均线
ax1.plot(dates, closes, label='收盘价', linewidth=1.2, color='#1f77b4')
ax1.plot(dates, data['MA250'], label='MA250', linewidth=1.5, color='#ff7f0e', alpha=0.8)

# 标记买入点（用绿色三角）
if len(buy_trades) > 0:
    buy_dates = buy_trades['日期']
    buy_prices = buy_trades['价格']
    ax1.scatter(buy_dates, buy_prices, color='green', marker='^', s=120, zorder=5, 
                edgecolors='black', linewidth=1.5, label='买入')

# 标记卖出点（用红色三角）
if len(sell_trades) > 0:
    sell_dates = sell_trades['日期']
    sell_prices = sell_trades['价格']
    ax1.scatter(sell_dates, sell_prices, color='red', marker='v', s=120, zorder=5,
                edgecolors='black', linewidth=1.5, label='卖出')

ax1.set_title('东证红利低波动指数(931446) - K线图与交易信号', fontsize=16, pad=20)
ax1.set_ylabel('价格', fontsize=12)
ax1.legend(loc='best', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax1.xaxis.set_major_locator(mdates.YearLocator())

# 2. 组合市值图
ax2 = fig.add_subplot(gs[1])
initial_capital = 100000
ax2.plot(portfolio_df['日期'], portfolio_df['持仓市值'], label='组合市值', linewidth=2, color='#2ca02c')
ax2.axhline(y=initial_capital, color='gray', linestyle='--', label='初始资金')

# 计算并标记最终收益率
final_value = portfolio_df['持仓市值'].iloc[-1]
total_return = (final_value - initial_capital) / initial_capital * 100
ax2.scatter(portfolio_df['日期'].iloc[-1], final_value, color='purple', s=100, zorder=5,
            label=f'最终收益: {total_return:.2f}%')

ax2.set_title('组合市值变化', fontsize=14, pad=15)
ax2.set_ylabel('市值', fontsize=12)
ax2.legend(loc='best', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax2.xaxis.set_major_locator(mdates.YearLocator())

# 3. RSI图
ax3 = fig.add_subplot(gs[2])
ax3.plot(dates, data['RSI'], label='RSI(24天)', color='#9467bd', linewidth=1.2)
ax3.axhline(y=70, color='red', linestyle='--', label='超买线(70)')
ax3.axhline(y=35, color='green', linestyle='--', label='超卖线(35)')
ax3.axhline(y=50, color='gray', linestyle=':', linewidth=0.8)

# 在RSI图上也标记买卖点
if len(buy_trades) > 0:
    ax3.scatter(buy_dates, buy_trades['RSI'], color='green', marker='^', s=80, zorder=5,
                edgecolors='black', linewidth=1.2)
if len(sell_trades) > 0:
    ax3.scatter(sell_dates, sell_trades['RSI'], color='red', marker='v', s=80, zorder=5,
                edgecolors='black', linewidth=1.2)

ax3.set_title('RSI(24天)指标', fontsize=14, pad=15)
ax3.set_ylabel('RSI值', fontsize=12)
ax3.set_ylim([0, 100])
ax3.legend(loc='best', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax3.xaxis.set_major_locator(mdates.YearLocator())

# 4. 回撤图
ax4 = fig.add_subplot(gs[3])
cummax = portfolio_df['持仓市值'].cummax()
drawdown = (portfolio_df['持仓市值'] - cummax) / cummax * 100
ax4.plot(portfolio_df['日期'], drawdown, color='#d62728', linewidth=1.5)
ax4.fill_between(portfolio_df['日期'], drawdown, 0, color='#d62728', alpha=0.3)

max_dd = drawdown.min()
ax4.axhline(y=max_dd, color='red', linestyle=':', label=f'最大回撤: {max_dd:.2f}%')

ax4.set_title('回撤曲线', fontsize=14, pad=15)
ax4.set_xlabel('日期', fontsize=12)
ax4.set_ylabel('回撤(%)', fontsize=12)
ax4.legend(loc='best', fontsize=10)
ax4.grid(True, alpha=0.3)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax4.xaxis.set_major_locator(mdates.YearLocator())

plt.tight_layout()
plt.savefig('回测结果综合图.png', dpi=150, bbox_inches='tight')
print("✅ 回测结果综合图已保存为：回测结果综合图.png")

# 再创建一个只包含最近几年的详细图
print("\n正在创建最近5年的详细图...")
latest_data = data[data['日期'] >= (datetime.now() - pd.Timedelta(days=365*5))]
latest_portfolio = portfolio_df[portfolio_df['日期'] >= (datetime.now() - pd.Timedelta(days=365*5))]
latest_buy = buy_trades[buy_trades['日期'] >= (datetime.now() - pd.Timedelta(days=365*5))]
latest_sell = sell_trades[sell_trades['日期'] >= (datetime.now() - pd.Timedelta(days=365*5))]

fig2 = plt.figure(figsize=(18, 12))
gs2 = fig2.add_gridspec(3, 1, hspace=0.3, height_ratios=[2, 1, 1])

ax2_1 = fig2.add_subplot(gs2[0])
ax2_1.plot(latest_data['日期'], latest_data['收盘'], label='收盘价', linewidth=1.2, color='#1f77b4')
ax2_1.plot(latest_data['日期'], latest_data['MA250'], label='MA250', linewidth=1.5, color='#ff7f0e', alpha=0.8)

if len(latest_buy) > 0:
    ax2_1.scatter(latest_buy['日期'], latest_buy['价格'], color='green', marker='^', s=150, zorder=5,
                  edgecolors='black', linewidth=1.5, label='买入')
if len(latest_sell) > 0:
    ax2_1.scatter(latest_sell['日期'], latest_sell['价格'], color='red', marker='v', s=150, zorder=5,
                  edgecolors='black', linewidth=1.5, label='卖出')

ax2_1.set_title('东证红利低波动指数 - 最近5年K线图与交易信号', fontsize=16, pad=20)
ax2_1.set_ylabel('价格', fontsize=12)
ax2_1.legend(loc='best', fontsize=10)
ax2_1.grid(True, alpha=0.3)
ax2_1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2_1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

ax2_2 = fig2.add_subplot(gs2[1])
ax2_2.plot(latest_portfolio['日期'], latest_portfolio['持仓市值'], label='组合市值', linewidth=2, color='#2ca02c')
ax2_2.axhline(y=initial_capital, color='gray', linestyle='--', label='初始资金')
ax2_2.set_title('组合市值变化 - 最近5年', fontsize=14, pad=15)
ax2_2.set_ylabel('市值', fontsize=12)
ax2_2.legend(loc='best', fontsize=10)
ax2_2.grid(True, alpha=0.3)
ax2_2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2_2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

ax2_3 = fig2.add_subplot(gs2[2])
ax2_3.plot(latest_data['日期'], latest_data['RSI'], label='RSI(24天)', color='#9467bd', linewidth=1.2)
ax2_3.axhline(y=70, color='red', linestyle='--', label='超买线(70)')
ax2_3.axhline(y=35, color='green', linestyle='--', label='超卖线(35)')

if len(latest_buy) > 0:
    ax2_3.scatter(latest_buy['日期'], latest_buy['RSI'], color='green', marker='^', s=100, zorder=5,
                  edgecolors='black', linewidth=1.2)
if len(latest_sell) > 0:
    ax2_3.scatter(latest_sell['日期'], latest_sell['RSI'], color='red', marker='v', s=100, zorder=5,
                  edgecolors='black', linewidth=1.2)

ax2_3.set_title('RSI(24天)指标 - 最近5年', fontsize=14, pad=15)
ax2_3.set_xlabel('日期', fontsize=12)
ax2_3.set_ylabel('RSI值', fontsize=12)
ax2_3.set_ylim([0, 100])
ax2_3.legend(loc='best', fontsize=10)
ax2_3.grid(True, alpha=0.3)
ax2_3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2_3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

plt.tight_layout()
plt.savefig('回测结果最近5年.png', dpi=150, bbox_inches='tight')
print("✅ 最近5年详细图已保存为：回测结果最近5年.png")

# 打印交易统计
print("\n" + "="*60)
print("交易统计")
print("="*60)
print(f"总交易次数: {len(trade_df)}")
print(f"买入次数: {len(buy_trades)}")
print(f"卖出次数: {len(sell_trades)}")
print(f"\n最终市值: {final_value:,.2f}")
print(f"总收益率: {total_return:.2f}%")
print(f"最大回撤: {max_dd:.2f}%")
