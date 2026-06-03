import pandas as pd
import numpy as np

print("="*80)
print("回测：下穿年均线买入+RSI>75卖出")
print("="*80)

# 加载真实历史数据
df = pd.read_csv("931446_真实数据_20200424至今.csv")
df['日期'] = pd.to_datetime(df['日期'])

print(f"\n数据范围: {df['日期'].min()} 至 {df['日期'].max()}")
print(f"数据行数: {len(df)}")

# 计算年均线MA250
df['MA250'] = df['收盘'].rolling(window=250).mean()

# 计算RSI(14天)
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df['收盘'])

# 检测下穿信号
df['下穿信号'] = (df['收盘'].shift(1) > df['MA250'].shift(1)) & (df['收盘'] < df['MA250'])

print("\n技术指标计算完成")

# 回测参数
initial_capital = 100000  # 初始资金10万
buy_amount_fixed = 10000  # 每次固定买入1万元
max_buy_count = 10        # 最多买入10次
rsi_sell_threshold = 75   # RSI卖出阈值

# 回测逻辑
capital = initial_capital
holdings = 0  # 持有指数点数
total_invested = 0  # 累计投入资金
buy_count = 0  # 买入次数计数器
portfolio_values = []
trade_records = []

print("\n策略参数:")
print(f"  买入条件: K线下穿年均线MA250")
print(f"  每次买入: 固定{buy_amount_fixed}元")
print(f"  最多买入: {max_buy_count}次")
print(f"  卖出条件: RSI > {rsi_sell_threshold} (全仓卖出)")
print(f"  总投入上限: {buy_amount_fixed * max_buy_count}元")

print("\n开始回测...")

for i in range(len(df)):
    current_date = df['日期'].iloc[i]
    close_price = df['收盘'].iloc[i]
    ma250 = df['MA250'].iloc[i]
    rsi = df['RSI'].iloc[i]
    down_cross = df['下穿信号'].iloc[i]
    
    # 前250天没有MA250和RSI数据
    if i < 250 or pd.isna(ma250) or pd.isna(rsi):
        portfolio_value = capital + holdings * close_price
        portfolio_values.append({
            '日期': current_date,
            '持仓市值': portfolio_value,
            '现金': capital,
            '持仓点数': holdings,
            '累计投入': total_invested,
            '买入次数': buy_count
        })
        continue
    
    # 优先检查卖出条件：RSI > 75，全仓卖出
    if rsi > rsi_sell_threshold and holdings > 0:
        # 全仓卖出
        sell_amount = holdings * close_price
        capital += sell_amount
        trade_records.append({
            '日期': current_date,
            '操作': '卖出',
            '价格': close_price,
            '卖出金额': sell_amount,
            '卖出点数': holdings,
            '剩余现金': capital,
            'RSI': rsi,
            'MA250': ma250
        })
        holdings = 0
        total_invested = 0
        buy_count = 0  # 重置买入次数，允许重新买入
    
    # 检测下穿买入信号
    # 条件：有下穿信号 + 未达到最大买入次数 + 有足够现金
    elif down_cross and buy_count < max_buy_count and capital >= buy_amount_fixed:
        # 固定买入1万元
        buy_points = buy_amount_fixed / close_price
        holdings += buy_points
        capital -= buy_amount_fixed
        total_invested += buy_amount_fixed
        buy_count += 1
        
        trade_records.append({
            '日期': current_date,
            '操作': '买入',
            '价格': close_price,
            '买入金额': buy_amount_fixed,
            '买入点数': buy_points,
            '剩余现金': capital,
            '累计持仓点数': holdings,
            '累计投入': total_invested,
            '买入次数': buy_count,
            'RSI': rsi,
            'MA250': ma250
        })
    
    # 更新资产价值
    portfolio_value = capital + holdings * close_price
    portfolio_values.append({
        '日期': current_date,
        '持仓市值': portfolio_value,
        '现金': capital,
        '持仓点数': holdings,
        '累计投入': total_invested,
        '买入次数': buy_count
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

print(f"\n回测结果:")
print(f"  初始资金: {initial_capital:,.2f} 元")
print(f"  最终市值: {final_value:,.2f} 元")
print(f"  剩余现金: {final_cash:,.2f} 元")
print(f"  持仓市值: {final_holdings_value:,.2f} 元")
print(f"  总收益率: {total_return:.2f}%")
print(f"  最大回撤: {max_drawdown:.2f}%")

print(f"\n基准对比:")
print(f"  买入持有收益率: {bh_return:.2f}%")
print(f"  买入持有最终市值: {bh_value:,.2f} 元")

# 统计交易次数
buy_trades = trade_df[trade_df['操作'] == '买入']
sell_trades = trade_df[trade_df['操作'] == '卖出']

print(f"\n交易统计:")
print(f"  总交易次数: {len(trade_df)} 次")
print(f"  买入次数: {len(buy_trades)} 次")
print(f"  卖出次数: {len(sell_trades)} 次")

# 保存结果
portfolio_df.to_csv("回测结果_买入RSI75卖出.csv", index=False, encoding='utf-8-sig')
trade_df.to_csv("交易记录_买入RSI75卖出.csv", index=False, encoding='utf-8-sig')

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
print(f"{'指标':<20} {'买入+RSI75卖出':>15} {'买入持有':>15}")
print("-"*50)
print(f"{'最终市值(元)':<20} {final_value:>15,.2f} {bh_value:>15,.2f}")
print(f"{'收益率(%)':<20} {total_return:>15.2f} {bh_return:>15.2f}")
print(f"{'最大回撤(%)':<20} {max_drawdown:>15.2f} {'N/A':>15}")
print(f"{'买入次数':<20} {len(buy_trades):>15} {'1':>15}")
print(f"{'卖出次数':<20} {len(sell_trades):>15} {'0':>15}")