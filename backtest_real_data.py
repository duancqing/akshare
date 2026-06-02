import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("="*80)
print("使用真实的931446数据进行策略回测")
print("="*80)

# 读取真实数据
df = pd.read_csv("931446_真实历史数据.csv")
df['日期'] = pd.to_datetime(df['日期'])
df = df.sort_values('日期').reset_index(drop=True)

# 计算年均线
df['MA250'] = df['收盘'].rolling(window=250).mean()

# 计算RSI
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df['收盘'])

print(f"\n✅ 数据加载成功: {len(df)} 条")
print(f"日期范围: {df['日期'].min()} 至 {df['日期'].max()}")

# 通用回测函数
def run_backtest(data, strategy_name, buy_condition, sell_condition):
    capital = 100000
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
        
        portfolio_value = capital + holdings * close_price
        portfolio_values.append({
            '日期': current_date,
            '持仓市值': portfolio_value,
            '持仓状态': position
        })
    
    return pd.DataFrame(portfolio_values), pd.DataFrame(trade_records)

# 策略1：年均线策略
def strategy1_buy(data, i):
    return data['收盘'].iloc[i] < data['MA250'].iloc[i]
def strategy1_sell(data, i):
    return data['RSI'].iloc[i] > 75

# 策略2：RSI策略
def strategy2_buy(data, i):
    return data['RSI'].iloc[i] < 30
def strategy2_sell(data, i):
    return data['RSI'].iloc[i] > 70

print("\n正在回测策略1...")
portfolio1, trades1 = run_backtest(df, "年均线策略", strategy1_buy, strategy1_sell)

print("正在回测策略2...")
portfolio2, trades2 = run_backtest(df, "RSI策略", strategy2_buy, strategy2_sell)

# 计算买入持有收益
start_idx = df[df['MA250'].notna()].index[0]
start_price = df['收盘'].iloc[start_idx]
end_price = df['收盘'].iloc[-1]
bh_return = (end_price - start_price) / start_price * 100
final_bh_value = 100000 * (1 + bh_return/100)

# 分析结果
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
        '交易次数': len(trade_df)
    }

results1 = analyze_results(portfolio1, trades1, "年均线策略")
results2 = analyze_results(portfolio2, trades2, "RSI策略")

print("\n" + "="*80)
print("策略对比结果")
print("="*80)
print(f"{'指标':<20} | {'年均线策略':<15} | {'RSI策略':<15} | {'买入持有':<15}")
print("-"*80)
print(f"{'最终市值(元)':<20} | {results1['最终市值']:>15,.2f} | {results2['最终市值']:>15,.2f} | {final_bh_value:>15,.2f}")
print(f"{'总收益率(%)':<20} | {results1['总收益率']:>15.2f} | {results2['总收益率']:>15.2f} | {bh_return:>15.2f}")
print(f"{'最大回撤(%)':<20} | {results1['最大回撤']:>15.2f} | {results2['最大回撤']:>15.2f} | {'N/A':<15}")
print(f"{'交易次数':<20} | {results1['交易次数']:>15} | {results2['交易次数']:>15} | {'N/A':<15}")

# 保存结果
portfolio1.to_csv("回测结果_策略1_真实数据.csv", index=False, encoding='utf-8-sig')
portfolio2.to_csv("回测结果_策略2_真实数据.csv", index=False, encoding='utf-8-sig')
trades1.to_csv("回测结果_策略1_交易记录_真实数据.csv", index=False, encoding='utf-8-sig')
trades2.to_csv("回测结果_策略2_交易记录_真实数据.csv", index=False, encoding='utf-8-sig')

print("\n" + "="*80)
print("✅ 回测完成！结果已保存")
print("="*80)
