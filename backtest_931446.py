import pandas as pd
import numpy as np
from datetime import datetime

# 读取数据
print("="*60)
print("正在读取历史数据...")
data = pd.read_csv("东证红利低波动指数_931446_历史数据.csv")
data['日期'] = pd.to_datetime(data['日期'])
data = data.sort_values('日期').reset_index(drop=True)
print(f"✅ 数据读取成功，共 {len(data)} 条数据")
print(f"数据日期范围: {data['日期'].iloc[0]} 至 {data['日期'].iloc[-1]}")

# 计算年均线（250日）
print("\n正在计算技术指标...")
data['MA250'] = data['收盘'].rolling(window=250).mean()

# 计算RSI (14日)
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

data['RSI'] = calculate_rsi(data['收盘'])
print("✅ 技术指标计算完成")

# 显示数据前几行（包含指标）
print("\n数据预览（前10行）:")
print(data[['日期', '收盘', 'MA250', 'RSI']].head(10))

# 回测设置
initial_capital = 100000  # 初始资金10万
print("\n" + "="*60)
print(f"开始回测 - 初始资金: {initial_capital:,} 元")
print("="*60)

# 初始化回测变量
capital = initial_capital
holdings = 0  # 持有指数点数价值
position = 0  # 0空仓，0.5半仓，1全仓
trade_records = []
portfolio_values = []

# 回测循环
for i in range(len(data)):
    current_date = data['日期'].iloc[i]
    close_price = data['收盘'].iloc[i]
    ma250 = data['MA250'].iloc[i]
    rsi = data['RSI'].iloc[i]
    
    # 跳过前250天（需要MA250和RSI数据）
    if i < 250 or pd.isna(ma250) or pd.isna(rsi):
        portfolio_value = capital + holdings * close_price
        portfolio_values.append({
            '日期': current_date,
            '持仓市值': portfolio_value,
            '现金': capital,
            '持仓点数': holdings,
            '持仓状态': position
        })
        continue
    
    # 当前资产价值
    portfolio_value = capital + holdings * close_price
    
    # 记录之前的持仓状态
    prev_position = position
    
    # 策略逻辑
    # RSI > 70: 全仓卖出
    if rsi > 70 and position > 0:
        # 全仓卖出
        capital += holdings * close_price
        trade_records.append({
            '日期': current_date,
            '操作': '卖出',
            '价格': close_price,
            'RSI': rsi,
            'MA250': ma250,
            '交易前状态': prev_position
        })
        holdings = 0
        position = 0
    
    # RSI < 35: 全仓买入
    elif rsi < 35:
        if position < 1:
            if position == 0.5:
                # 半仓转全仓，追加50%
                invest_amount = capital * 0.5
            else:
                # 空仓转全仓，投入100%
                invest_amount = capital
            
            if invest_amount > 0:
                new_holdings = invest_amount / close_price
                holdings += new_holdings
                capital -= invest_amount
                trade_records.append({
                    '日期': current_date,
                    '操作': '买入',
                    '价格': close_price,
                    'RSI': rsi,
                    'MA250': ma250,
                    '交易前状态': prev_position
                })
                position = 1
    
    # 价格低于年均线: 买入50%
    elif close_price < ma250 and position == 0:
        invest_amount = capital * 0.5
        if invest_amount > 0:
            new_holdings = invest_amount / close_price
            holdings += new_holdings
            capital -= invest_amount
            trade_records.append({
                '日期': current_date,
                '操作': '买入',
                '价格': close_price,
                'RSI': rsi,
                'MA250': ma250,
                '交易前状态': prev_position
            })
            position = 0.5
    
    # 更新资产价值
    portfolio_value = capital + holdings * close_price
    portfolio_values.append({
        '日期': current_date,
        '持仓市值': portfolio_value,
        '现金': capital,
        '持仓点数': holdings,
        '持仓状态': position
    })

# 转换为DataFrame
portfolio_df = pd.DataFrame(portfolio_values)
trade_df = pd.DataFrame(trade_records)

# 计算回测结果
print("\n" + "="*60)
print("回测结果统计")
print("="*60)

final_value = portfolio_df['持仓市值'].iloc[-1]
total_return = (final_value - initial_capital) / initial_capital * 100

print(f"初始资金: {initial_capital:,.2f} 元")
print(f"最终市值: {final_value:,.2f} 元")
print(f"总收益率: {total_return:.2f}%")

# 计算买入并持有收益
buy_and_hold_return = (data['收盘'].iloc[-1] - data['收盘'].iloc[250]) / data['收盘'].iloc[250] * 100
print(f"买入并持有收益率: {buy_and_hold_return:.2f}%")

# 计算最大回撤
def calculate_max_drawdown(prices):
    cummax = prices.cummax()
    drawdown = (prices - cummax) / cummax * 100
    max_drawdown = drawdown.min()
    return max_drawdown, drawdown

max_dd, drawdown_series = calculate_max_drawdown(portfolio_df['持仓市值'])
print(f"最大回撤: {max_dd:.2f}%")

# 计算年化收益率
days = (portfolio_df['日期'].iloc[-1] - portfolio_df['日期'].iloc[0]).days
years = days / 365.25
annual_return = ((final_value / initial_capital) ** (1 / years) - 1) * 100
print(f"年化收益率: {annual_return:.2f}%")

# 计算年收益率
portfolio_df['年份'] = portfolio_df['日期'].dt.year
yearly_returns = []
for year in portfolio_df['年份'].unique():
    year_data = portfolio_df[portfolio_df['年份'] == year]
    year_start = year_data['持仓市值'].iloc[0]
    year_end = year_data['持仓市值'].iloc[-1]
    year_return = (year_end - year_start) / year_start * 100
    yearly_returns.append({
        '年份': year,
        '期初市值': year_start,
        '期末市值': year_end,
        '年度收益率': year_return
    })

yearly_df = pd.DataFrame(yearly_returns)
print("\n年度收益率:")
print(yearly_df[['年份', '年度收益率']].to_string(index=False))

# 交易记录
print("\n" + "="*60)
print(f"交易记录（共 {len(trade_df)} 次交易）:")
print("="*60)
if len(trade_df) > 0:
    print(trade_df.to_string(index=False))

# 保存结果
portfolio_df.to_csv("回测结果_组合市值.csv", index=False, encoding='utf-8-sig')
if len(trade_df) > 0:
    trade_df.to_csv("回测结果_交易记录.csv", index=False, encoding='utf-8-sig')
yearly_df.to_csv("回测结果_年度收益率.csv", index=False, encoding='utf-8-sig')

print("\n✅ 回测结果已保存！")
print("- 回测结果_组合市值.csv")
print("- 回测结果_交易记录.csv")
print("- 回测结果_年度收益率.csv")
