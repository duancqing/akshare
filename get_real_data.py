
import akshare as ak
import pandas as pd
from datetime import datetime

print("="*80)
print("尝试获取真实可用的指数数据")
print("="*80)

# 先搜索一下可用的指数
print("\n1. 搜索红利相关指数...")
try:
    # 用东方财富的数据源
    print("\n尝试从东方财富获取指数列表...")
    index_df = ak.index_stock_cons_sina(symbol="sh000001")
    print("成功获取指数样本数据")
except Exception as e:
    print(f"东方财富数据获取失败: {e}")

# 尝试获取上证指数作为对比
print("\n2. 获取上证指数(000001)作为参考...")
try:
    zz_index = ak.stock_zh_index_daily(symbol="sh000001")
    print(f"上证指数数据获取成功: {len(zz_index)} 条")
    print(f"日期范围: {zz_index.index[0]} 至 {zz_index.index[-1]}")
    print("\n最近5条:")
    print(zz_index.tail())
except Exception as e:
    print(f"上证指数获取失败: {e}")

# 尝试搜索931446在其他来源
print("\n3. 尝试多种数据源获取931446...")

# 方法1: 新浪财经
try:
    print("\n尝试新浪财经数据源...")
    sina_data = ak.stock_zh_index_daily(symbol="sz931446")
    print(f"新浪财经获取成功: {len(sina_data)} 条")
except Exception as e:
    print(f"新浪财经获取失败: {e}")

# 方法2: 东方财富
try:
    print("\n尝试东方财富数据源获取指数历史...")
    em_data = ak.index_zh_a_hist(symbol="931446", period="daily", start_date="20200101", end_date="20231231")
    print(f"东方财富获取成功: {len(em_data)} 条")
except Exception as e:
    print(f"东方财富获取失败: {e}")

print("\n" + "="*80)
print("结论")
print("="*80)
print("当前系统时间: ", datetime.now())
