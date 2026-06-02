
import akshare as ak
import pandas as pd
from datetime import datetime

print("="*80)
print("验证指数931446信息")
print("="*80)

try:
    # 尝试获取指数的基本信息
    print("\n1. 尝试获取指数基本信息...")
    # 获取中证指数列表
    index_list = ak.index_stock_info()
    print(f"找到 {len(index_list)} 个指数")
    
    # 搜索我们的指数
    target_index = index_list[index_list['指数代码'].astype(str).str.contains('931446')]
    if len(target_index) > 0:
        print("\n✅ 找到目标指数:")
        print(target_index.to_string())
    else:
        print("\n⚠️ 未找到代码为931446的指数")
        # 搜索一下红利低波相关的指数
        dividend_low_vol = index_list[index_list['指数名称'].str.contains('红利低波', na=False)]
        if len(dividend_low_vol) > 0:
            print(f"\n找到 {len(dividend_low_vol)} 个红利低波相关指数:")
            print(dividend_low_vol.to_string())
        else:
            print("\n未找到红利低波相关指数")
            
except Exception as e:
    print(f"获取指数列表失败: {e}")

print("\n" + "="*80)
print("尝试获取最近真实数据")
print("="*80)

try:
    # 用我们之前的函数获取
    print("\n尝试获取931446指数数据（2020-2025）...")
    data = ak.stock_zh_index_hist_csindex(symbol="931446", start_date="20200101", end_date="20251231")
    print(f"获取到 {len(data)} 条数据")
    if len(data) > 0:
        print(f"日期范围: {data['日期'].min()} 至 {data['日期'].max()}")
        print("\n前5条:")
        print(data.head())
        print("\n后5条:")
        print(data.tail())
except Exception as e:
    print(f"获取数据失败: {e}")

print("\n" + "="*80)
print("当前系统时间检查")
print("="*80)
print(f"当前时间: {datetime.now()}")
