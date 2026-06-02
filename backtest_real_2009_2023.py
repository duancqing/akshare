import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("使用真实历史数据(2009-2023)进行策略回测")
print("="*80)

# 读取真实数据，只使用到2023年的部分
df = pd.read_csv("931446_真实完整历史数据.csv")
df['日期'] = pd.to_datetime(df['日期'])

# 只保留到2023年12月31日的真实数据
df = df[df['日期'] <= '2023-12-31'].reset_index(drop=True)

print(f"\n✅ 使用真实历史数据")
print(f"数据行数: {len(df)}")
print(f"日期范围: {df['日期'].min()} 至 {df['日期'].max()}")

# 计算技术指标
df['MA250'] = df['收盘'].rolling(window=250).mean()

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df['收盘'])

print(f"\n技术指标已计算完成")

# 回测函数
def run_backtest(data, buy_condition, sell_condition):
    capital = 100000
    holdings = 0
    position = 0
    trades = []
    portfolio = []
    
    for i in range(len(data)):
        date = data['日期'].iloc[i]
        price = data['收盘'].iloc[i]
        ma250 = data['MA250'].iloc[i]
        rsi = data['RSI'].iloc[i]
        
        # 前250天没有指标数据
        if i < 250 or pd.isna(ma250) or pd.isna(rsi):
            value = capital + holdings * price
            portfolio.append({'日期': date, '市值': value, '持仓': position})
            continue
        
        # 卖出
        if sell_condition(data, i) and position > 0:
            capital += holdings * price
            trades.append({'日期': date, '操作': '卖出', '价格': price})
            holdings = 0
            position = 0
        
        # 买入
        elif buy_condition(data, i) and position == 0:
            holdings = capital / price
            capital = 0
            trades.append({'日期': date, '操作': '买入', '价格': price})
            position = 1
        
        value = capital + holdings * price
        portfolio.append({'日期': date, '市值': value, '持仓': position})
    
    return pd.DataFrame(portfolio), pd.DataFrame(trades)

# 策略1：年均线策略（价格<MA250买入，RSI>75卖出）
print("\n正在回测策略1：年均线策略...")
portfolio1, trades1 = run_backtest(
    df,
    lambda d, i: d['收盘'].iloc[i] < d['MA250'].iloc[i],
    lambda d, i: d['RSI'].iloc[i] > 75
)

# 策略2：RSI策略（RSI<30买入，RSI>70卖出）
print("正在回测策略2：RSI策略...")
portfolio2, trades2 = run_backtest(
    df,
    lambda d, i: d['RSI'].iloc[i] < 30,
    lambda d, i: d['RSI'].iloc[i] > 70
)

# 买入持有基准
start_idx = 250
start_price = df['收盘'].iloc[start_idx]
end_price = df['收盘'].iloc[-1]
bh_return = (end_price - start_price) / start_price * 100
bh_value = 100000 * (end_price / start_price)

# 分析结果
def analyze(portfolio, trades, name):
    final = portfolio['市值'].iloc[-1]
    return_pct = (final - 100000) / 100000 * 100
    cummax = portfolio['市值'].cummax()
    max_dd = ((portfolio['市值'] - cummax) / cummax * 100).min()
    return {
        '策略': name,
        '最终市值': final,
        '收益率': return_pct,
        '最大回撤': max_dd,
        '交易次数': len(trades)
    }

r1 = analyze(portfolio1, trades1, '年均线策略')
r2 = analyze(portfolio2, trades2, 'RSI策略')

print("\n" + "="*80)
print("回测结果对比（真实数据2009-2023）")
print("="*80)
print(f"{'指标':<20} {'年均线策略':>15} {'RSI策略':>15} {'买入持有':>15}")
print("-"*75)
print(f"{'最终市值(元)':<20} {r1['最终市值']:>15,.2f} {r2['最终市值']:>15,.2f} {bh_value:>15,.2f}")
print(f"{'收益率(%)':<20} {r1['收益率']:>15.2f} {r2['收益率']:>15.2f} {bh_return:>15.2f}")
print(f"{'最大回撤(%)':<20} {r1['最大回撤']:>15.2f} {r2['最大回撤']:>15.2f} {'N/A':>15}")
print(f"{'交易次数':<20} {r1['交易次数']:>15} {r2['交易次数']:>15} {'N/A':>15}")

# 保存结果
portfolio1.to_csv("真实数据_策略1年均线.csv", index=False, encoding='utf-8-sig')
portfolio2.to_csv("真实数据_策略2RSI.csv", index=False, encoding='utf-8-sig')
trades1.to_csv("真实数据_策略1交易记录.csv", index=False, encoding='utf-8-sig')
trades2.to_csv("真实数据_策略2交易记录.csv", index=False, encoding='utf-8-sig')

print("\n✅ 回测完成！结果已保存")
print("="*80)