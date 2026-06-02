import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("策略回测：K线下穿年均线买入20%，不卖出")
print("="*80)

# 加载真实历史数据
df = pd.read_csv("931446_真实完整历史数据.csv")
df['日期'] = pd.to_datetime(df['日期'])
df = df[df['日期'] <= '2023-12-31'].reset_index(drop=True)

print(f"\n数据范围: {df['日期'].min()} 至 {df['日期'].max()}")
print(f"数据行数: {len(df)}")

# 计算年均线MA250
df['MA250'] = df['收盘'].rolling(window=250).mean()

# 检测下穿信号：前一天收盘价在MA250上方，当天收盘价在MA250下方
df['上穿'] = (df['收盘'].shift(1) > df['MA250'].shift(1)) & (df['收盘'] < df['MA250'])
df['下穿信号'] = df['上穿']  # 重命名更清晰

print("\n技术指标计算完成")

# 回测参数
initial_capital = 100000  # 初始资金10万
buy_percentage = 0.20     # 每次买入20%仓位

# 回测逻辑
capital = initial_capital
holdings = 0  # 持有指数点数
total_invested = 0  # 累计投入资金
buy_count = 0  # 买入次数
portfolio_values = []
trade_records = []

print("\n开始回测...")

for i in range(len(df)):
    current_date = df['日期'].iloc[i]
    close_price = df['收盘'].iloc[i]
    ma250 = df['MA250'].iloc[i]
    down_cross = df['下穿信号'].iloc[i]
    
    # 前250天没有MA250数据
    if i < 250 or pd.isna(ma250):
        portfolio_value = capital + holdings * close_price
        portfolio_values.append({
            '日期': current_date,
            '持仓市值': portfolio_value,
            '现金': capital,
            '持仓点数': holdings,
            '累计投入': total_invested
        })
        continue
    
    # 检测下穿买入信号
    if down_cross and capital > 0:
        # 计算买入金额（当前现金的20%）
        buy_amount = capital * buy_percentage
        if buy_amount > 0:
            # 买入指数点数
            buy_points = buy_amount / close_price
            holdings += buy_points
            capital -= buy_amount
            total_invested += buy_amount
            buy_count += 1
            
            trade_records.append({
                '日期': current_date,
                '操作': '买入',
                '价格': close_price,
                '买入金额': buy_amount,
                '买入点数': buy_points,
                '买入比例': '20%',
                '剩余现金': capital,
                '累计持仓点数': holdings,
                'MA250': ma250
            })
    
    # 更新资产价值
    portfolio_value = capital + holdings * close_price
    portfolio_values.append({
        '日期': current_date,
        '持仓市值': portfolio_value,
        '现金': capital,
        '持仓点数': holdings,
        '累计投入': total_invested
    })

# 转换为DataFrame
portfolio_df = pd.DataFrame(portfolio_values)
trade_df = pd.DataFrame(trade_records)

# 计算结果
final_value = portfolio_df['持仓市值'].iloc[-1]
final_cash = portfolio_df['现金'].iloc[-1]
final_holdings_value = portfolio_df['持仓点数'].iloc[-1] * df['收盘'].iloc[-1]
total_return = (final_value - initial_capital) / initial_capital * 100

# 计算最大回撤
cummax = portfolio_df['持仓市值'].cummax()
drawdown = (portfolio_df['持仓市值'] - cummax) / cummax * 100
max_drawdown = drawdown.min()

# 买入持有基准
start_idx = 250
start_price = df['收盘'].iloc[start_idx]
end_price = df['收盘'].iloc[-1]
bh_return = (end_price - start_price) / start_price * 100
bh_value = initial_capital * (end_price / start_price)

print("\n" + "="*80)
print("回测结果")
print("="*80)

print(f"\n策略参数:")
print(f"  买入条件: K线下穿年均线MA250")
print(f"  买入比例: 每次买入当前现金的20%")
print(f"  卖出条件: 无（一直持有）")

print(f"\n回测结果:")
print(f"  初始资金: {initial_capital:,.2f} 元")
print(f"  最终市值: {final_value:,.2f} 元")
print(f"  剩余现金: {final_cash:,.2f} 元")
print(f"  持仓市值: {final_holdings_value:,.2f} 元")
print(f"  累计投入: {total_invested:,.2f} 元")
print(f"  买入次数: {buy_count} 次")
print(f"  总收益率: {total_return:.2f}%")
print(f"  最大回撤: {max_drawdown:.2f}%")

print(f"\n基准对比:")
print(f"  买入持有收益率: {bh_return:.2f}%")
print(f"  买入持有最终市值: {bh_value:,.2f} 元")

print(f"\n资金使用效率:")
print(f"  现金使用比例: {(initial_capital - final_cash) / initial_capital * 100:.2f}%")

# 保存结果
portfolio_df.to_csv("回测结果_下穿年均线买入20%_不卖出.csv", index=False, encoding='utf-8-sig')
trade_df.to_csv("交易记录_下穿年均线买入20%_不卖出.csv", index=False, encoding='utf-8-sig')

print("\n" + "="*80)
print("交易记录详情")
print("="*80)
if len(trade_df) > 0:
    print(trade_df.to_string())
else:
    print("无交易记录")

print("\n✅ 回测完成！结果已保存")

# 创建对比表格
print("\n" + "="*80)
print("策略对比汇总")
print("="*80)
print(f"{'指标':<20} {'下穿买入20%':>15} {'买入持有':>15}")
print("-"*50)
print(f"{'最终市值(元)':<20} {final_value:>15,.2f} {bh_value:>15,.2f}")
print(f"{'收益率(%)':<20} {total_return:>15.2f} {bh_return:>15.2f}")
print(f"{'最大回撤(%)':<20} {max_drawdown:>15.2f} {'N/A':>15}")
print(f"{'买入次数':<20} {buy_count:>15} {'1':>15}")
print(f"{'现金使用率(%)':<20} {(initial_capital-final_cash)/initial_capital*100:>15.2f} {'100':>15}")