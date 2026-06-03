import pandas as pd

print("="*80)
print("分析买入次数过多的原因")
print("="*80)

# 读取交易记录
trades = pd.read_csv("交易记录_20200424_20260603_下穿买入20%.csv")

print(f"\n总买入次数: {len(trades)} 次")
print(f"初始资金: 100,000 元")

print("\n买入金额递减分析:")
print("-"*80)
print(f"{'次数':<6} {'日期':<12} {'买入金额':<12} {'剩余现金':<12} {'买入占比':<10}")
print("-"*80)

for i, row in trades.iterrows():
    print(f"{i+1:<6} {row['日期']:<12} {row['买入金额']:>10,.2f} {row['剩余现金']:>10,.2f} {row['买入比例']:<10}")

print("\n" + "="*80)
print("问题分析")
print("="*80)

print("\n⚠️ 策略设计问题：每次买入的是【当前现金的20%】，而不是【初始资金的20%】")

print("\n计算逻辑:")
print("  第1次买入: 100,000 × 20% = 20,000元，剩余80,000元")
print("  第2次买入: 80,000 × 20% = 16,000元，剩余64,000元")
print("  第3次买入: 64,000 × 20% = 12,800元，剩余51,200元")
print("  第4次买入: 51,200 × 20% = 10,240元，剩余40,960元")
print("  ...")
print("  第29次买入: 193.43 × 20% = 38.69元，剩余154.74元")

print("\n这种设计会导致:")
print("  1. ✅ 每次买入金额递减（符合风险控制）")
print("  2. ❌ 可以无限买入（只要有现金剩余）")
print("  3. ❌ 后期买入金额过小（第29次仅38.69元）")
print("  4. ❌ 实际仓位控制不明确")

print("\n" + "="*80)
print("改进建议")
print("="*80)

print("\n方案1: 每次买入【初始资金的固定比例】")
print("  例如: 每次买入初始资金的20% = 20,000元")
print("  最多买入5次，总仓位100%")

print("\n方案2: 设置最小买入金额")
print("  例如: 最小买入金额 = 1,000元")
print("  当剩余现金 < 5,000元时停止买入")

print("\n方案3: 设置最大买入次数")
print("  例如: 最多买入5次")

print("\n方案4: 设置仓位上限")
print("  例如: 总仓位不超过80%")

print("\n" + "="*80)
print("当前策略的资金使用效率")
print("="*80)

initial = 100000
final_cash = trades['剩余现金'].iloc[-1]
total_invested = initial - final_cash

print(f"\n初始资金: {initial:,.2f} 元")
print(f"最终剩余现金: {final_cash:,.2f} 元")
print(f"累计投入: {total_invested:,.2f} 元")
print(f"资金使用率: {total_invested/initial*100:.2f}%")

print(f"\n平均每次买入金额: {total_invested/len(trades):,.2f} 元")
print(f"最大单次买入: {trades['买入金额'].max():,.2f} 元")
print(f"最小单次买入: {trades['买入金额'].min():,.2f} 元")

print("\n✅ 结论: 策略设计需要优化，避免后期买入金额过小")