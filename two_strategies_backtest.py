
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
print("="*80)
print("读取数据和计算指标")
print("="*80)

df = pd.read_csv('东证红利低波动指数_931446_历史数据.csv')
df['日期'] = pd.to_datetime(df['日期'])
df = df.sort_values('日期').reset_index(drop=True)

# 计算年均线(250日)
df['MA250'] = df['收盘'].rolling(window=250).mean()

# 计算RSI函数
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df['收盘'])

print(f"✅ 数据加载成功: {len(df)} 条")
print(f"日期范围: {df['日期'].min()} 至 {df['日期'].max()}")

# 回测函数
def run_backtest(data, strategy_name, buy_condition, sell_condition, initial_capital=100000):
    """
    通用回测函数
    """
    capital = initial_capital
    holdings = 0
    position = 0
    trade_records = []
    portfolio_values = []
    
    for i in range(len(data)):
        current_date = data['日期'].iloc[i]
        close_price = data['收盘'].iloc[i]
        ma250 = data['MA250'].iloc[i]
        rsi = data['RSI'].iloc[i]
        
        if i < 250 or pd.isna(ma250) or pd.isna(rsi):
            portfolio_value = capital + holdings * close_price
            portfolio_values.append({
                '日期': current_date,
                '持仓市值': portfolio_value,
                '持仓状态': position
            })
            continue
        
        prev_position = position
        
        # 检查卖出条件
        if sell_condition(data, i) and position > 0:
            capital += holdings * close_price
            trade_records.append({
                '日期': current_date,
                '操作': '卖出',
                '价格': close_price,
                '交易前状态': prev_position
            })
            holdings = 0
            position = 0
        
        # 检查买入条件
        elif buy_condition(data, i) and position == 0:
            invest_amount = capital
            new_holdings = invest_amount / close_price
            holdings += new_holdings
            capital -= invest_amount
            trade_records.append({
                '日期': current_date,
                '操作': '买入',
                '价格': close_price,
                '交易前状态': prev_position
            })
            position = 1
        
        # 更新资产价值
        portfolio_value = capital + holdings * close_price
        portfolio_values.append({
            '日期': current_date,
            '持仓市值': portfolio_value,
            '持仓状态': position
        })
    
    return pd.DataFrame(portfolio_values), pd.DataFrame(trade_records)

# 策略1: 年均线策略
def strategy1_buy(data, i):
    return data['收盘'].iloc[i] < data['MA250'].iloc[i]

def strategy1_sell(data, i):
    return data['RSI'].iloc[i] > 75

# 策略2: RSI策略
def strategy2_buy(data, i):
    return data['RSI'].iloc[i] < 30

def strategy2_sell(data, i):
    return data['RSI'].iloc[i] > 70

# 执行两个策略回测
print("\n" + "="*80)
print("开始回测策略1: 年均线策略")
print("="*80)
portfolio1, trades1 = run_backtest(df, "年均线策略", strategy1_buy, strategy1_sell)

print("\n" + "="*80)
print("开始回测策略2: RSI策略")
print("="*80)
portfolio2, trades2 = run_backtest(df, "RSI策略", strategy2_buy, strategy2_sell)

# 计算买入并持有收益
print("\n" + "="*80)
print("计算基准收益")
print("="*80)

start_idx = df[df['MA250'].notna()].index[0]
start_price = df['收盘'].iloc[start_idx]
end_price = df['收盘'].iloc[-1]
bh_return = (end_price - start_price) / start_price * 100

print(f"基准(买入持有): {bh_return:.2f}%")

# 结果分析函数
def analyze_results(portfolio_df, trade_df, strategy_name):
    final_value = portfolio_df['持仓市值'].iloc[-1]
    total_return = (final_value - 100000) / 100000 * 100
    
    cummax = portfolio_df['持仓市值'].cummax()
    drawdown = (portfolio_df['持仓市值'] - cummax) / cummax * 100
    max_dd = drawdown.min()
    
    return {
        '策略名称': strategy_name,
        '最终市值': final_value,
        '总收益率': total_return,
        '最大回撤': max_dd,
        '交易次数': len(trade_df),
        '买入次数': len(trade_df[trade_df['操作'] == '买入']),
        '卖出次数': len(trade_df[trade_df['操作'] == '卖出'])
    }

results1 = analyze_results(portfolio1, trades1, "年均线策略")
results2 = analyze_results(portfolio2, trades2, "RSI策略")

# 打印对比表格
print("\n" + "="*80)
print("策略对比结果")
print("="*80)
print(f"{'指标':<20} | {'年均线策略':<15} | {'RSI策略':<15} | {'买入持有':<15}")
print("-"*80)
print(f"{'最终市值(元)':<20} | {results1['最终市值']:>12,.2f} | {results2['最终市值']:>12,.2f} | {100000*(1+bh_return/100):>12,.2f}")
print(f"{'总收益率(%)':<20} | {results1['总收益率']:>12.2f} | {results2['总收益率']:>12.2f} | {bh_return:>12.2f}")
print(f"{'最大回撤(%)':<20} | {results1['最大回撤']:>12.2f} | {results2['最大回撤']:>12.2f} | {'N/A':<12}")
print(f"{'总交易次数':<20} | {results1['交易次数']:>12} | {results2['交易次数']:>12} | {'N/A':<12}")

# 保存详细结果
portfolio1.to_csv('回测结果_策略1_年均线.csv', index=False, encoding='utf-8-sig')
portfolio2.to_csv('回测结果_策略2_RSI.csv', index=False, encoding='utf-8-sig')
trades1.to_csv('回测结果_策略1_交易记录.csv', index=False, encoding='utf-8-sig')
trades2.to_csv('回测结果_策略2_交易记录.csv', index=False, encoding='utf-8-sig')

print("\n" + "="*80)
print("策略1交易记录 (前10条):")
print("="*80)
if len(trades1) > 0:
    print(trades1.head(10).to_string())
print("\n" + "="*80)
print("策略2交易记录 (前10条):")
print("="*80)
if len(trades2) > 0:
    print(trades2.head(10).to_string())

# 画图对比
print("\n" + "="*80)
print("生成对比图表")
print("="*80)

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 1, hspace=0.3)

ax1 = fig.add_subplot(gs[0])
ax1.plot(portfolio1['日期'], portfolio1['持仓市值'], label='策略1:年均线策略', linewidth=2)
ax1.plot(portfolio2['日期'], portfolio2['持仓市值'], label='策略2:RSI策略', linewidth=2)
ax1.axhline(y=100000, color='gray', linestyle='--', label='初始资金')
ax1.set_title('策略市值对比', fontsize=14)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)

ax2 = fig.add_subplot(gs[1])
ax2.plot(df['日期'], df['收盘'], label='指数走势', linewidth=1.2)
ax2.set_title('指数走势', fontsize=14)
ax2.legend()
ax2.grid(True, alpha=0.3)

ax3 = fig.add_subplot(gs[2])
ax3.plot(df['日期'], df['RSI'], label='RSI(14)', color='purple', linewidth=1.2)
ax3.axhline(y=75, color='red', linestyle='--', label='超买75', alpha=0.5)
ax3.axhline(y=70, color='red', linestyle=':', label='超买70', alpha=0.5)
ax3.axhline(y=30, color='green', linestyle='--', label='超卖30', alpha=0.5)
ax3.set_title('RSI指标', fontsize=14)
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('策略对比综合图.png', dpi=150, bbox_inches='tight')
print("✅ 图表已保存为: 策略对比综合图.png")
print("\n✅ 所有回测结果已保存!")
