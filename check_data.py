
import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('东证红利低波动指数_931446_历史数据.csv')
df['日期'] = pd.to_datetime(df['日期'])

print("="*80)
print("数据基本信息")
print("="*80)
print(f"数据行数: {len(df)}")
print(f"日期范围: {df['日期'].min()} 至 {df['日期'].max()}")
print(f"指数代码: {df['指数代码'].iloc[0]}")
print(f"指数名称: {df['指数中文全称'].iloc[0]}")

print("\n" + "="*80)
print("数据完整性检查")
print("="*80)

# 检查重复日期
duplicates = df[df.duplicated('日期')]
if len(duplicates) > 0:
    print(f"⚠️ 发现 {len(duplicates)} 条重复日期:")
    print(duplicates['日期'].head(10).tolist())
else:
    print("✅ 日期没有重复")

# 检查价格异常
print("\n价格统计:")
price_cols = ['开盘', '最高', '最低', '收盘']
print(df[price_cols].describe())

# 检查最高是否低于最低
invalid_prices = df[df['最高'] < df['最低']]
if len(invalid_prices) > 0:
    print(f"\n⚠️ 发现 {len(invalid_prices)} 条记录最高价格低于最低价格!")
else:
    print("\n✅ 最高价格始终高于最低价格")

# 检查最近的数据
print("\n" + "="*80)
print("最近10条记录")
print("="*80)
print(df.tail(10).to_string())

# 检查交易日历
print("\n" + "="*80)
print("日期连续性检查")
print("="*80)

# 按日期排序
df_sorted = df.sort_values('日期').reset_index(drop=True)

# 计算相邻日期的间隔
df_sorted['日期间隔'] = df_sorted['日期'].diff().dt.days
print("\n日期间隔统计:")
print(df_sorted['日期间隔'].describe())

# 检查间隔异常大的日期
large_gaps = df_sorted[df_sorted['日期间隔'] > 14]
if len(large_gaps) > 0:
    print(f"\n⚠️ 发现 {len(large_gaps)} 个间隔超过2周的日期:")
    for idx, row in large_gaps.iterrows():
        prev_date = df_sorted.iloc[idx-1]['日期']
        curr_date = row['日期']
        print(f"  {prev_date} -> {curr_date}: 间隔 {row['日期间隔']} 天")
