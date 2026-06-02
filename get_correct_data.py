import akshare as ak
import pandas as pd
from datetime import datetime

print("="*80)
print("获取真实的931446中证东方红红利低波动指数数据")
print("="*80)

try:
    # 使用正确的指数代码931446获取数据
    print("\n正在获取931446指数数据...")
    data = ak.stock_zh_index_hist_csindex(
        symbol="931446",
        start_date="20100101",
        end_date="20231231"  # 使用真实的历史数据范围
    )
    
    print(f"\n✅ 成功获取数据！")
    print(f"数据行数: {len(data)}")
    if len(data) > 0:
        print(f"日期范围: {data['日期'].min()} 至 {data['日期'].max()}")
        print(f"\n前10条数据:")
        print(data.head(10).to_string())
        
        print(f"\n后10条数据:")
        print(data.tail(10).to_string())
        
        # 保存数据
        data.to_csv("931446_真实历史数据.csv", index=False, encoding='utf-8-sig')
        print(f"\n✅ 真实数据已保存至: 931446_真实历史数据.csv")
        
except Exception as e:
    print(f"\n❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()
