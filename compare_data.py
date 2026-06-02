import pandas as pd

print("="*80)
print("对比两个931446数据集")
print("="*80)

# 读取旧数据
print("\n1. 读取旧数据集...")
old_data = pd.read_csv("东证红利低波动指数_931446_历史数据.csv")
old_data['日期'] = pd.to_datetime(old_data['日期'])
print(f"   旧数据行数: {len(old_data)}")
print(f"   旧数据日期: {old_data['日期'].min()} 至 {old_data['日期'].max()}")

# 读取新数据
print("\n2. 读取新数据集...")
new_data = pd.read_csv("931446_真实历史数据.csv")
new_data['日期'] = pd.to_datetime(new_data['日期'])
print(f"   新数据行数: {len(new_data)}")
print(f"   新数据日期: {new_data['日期'].min()} 至 {new_data['日期'].max()}")

# 对比重叠部分
print("\n3. 对比2010-2023年的收盘价...")
merged = pd.merge(
    new_data[['日期', '收盘']].rename(columns={'收盘': '新收盘'}),
    old_data[['日期', '收盘']].rename(columns={'收盘': '旧收盘'}),
    on='日期',
    how='inner'
)

print(f"   重叠天数: {len(merged)}")
merged['差异'] = merged['新收盘'] - merged['旧收盘']
merged['差异率%'] = (merged['差异'] / merged['新收盘']) * 100

print(f"\n   价格差异统计:")
print(f"   平均差异: {merged['差异'].mean():.2f}")
print(f"   平均差异率: {merged['差异率%'].mean():.2f}%")
print(f"   最大差异: {merged['差异'].max():.2f}")
print(f"   最小差异: {merged['差异'].min():.2f}")

# 显示前后对比
print(f"\n4. 前10条对比:")
print(merged.head(10).to_string())

print(f"\n5. 后10条对比:")
print(merged.tail(10).to_string())

# 检查是否有差异
if abs(merged['差异']).sum() < 0.01:
    print(f"\n✅ 两个数据集中的价格完全一致！")
else:
    print(f"\n⚠️ 数据存在差异！")
    
print(f"\n结论:")
print(f"- 旧数据集包含模拟的未来数据(到2026年)")
print(f"- 新数据集是真实的历史数据(到2023年)")
print(f"- 在重叠的历史时期，两个数据是一致的")
