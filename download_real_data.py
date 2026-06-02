import akshare as ak
import pandas as pd
from datetime import datetime

print("="*80)
print("下载931446中证东方红红利低波动指数真实历史数据")
print("="*80)

# 获取真实数据（从基日2009-12-31到现在）
print("\n正在从中证指数官网获取真实数据...")

# 使用正确的日期范围：从基日开始到当前真实日期
today = datetime.now().strftime("%Y%m%d")
print(f"当前真实日期: {datetime.now()}")
print(f"获取数据范围: 20091231 至 {today}")

try:
    # 获取完整历史数据
    real_data = ak.stock_zh_index_hist_csindex(
        symbol="931446",
        start_date="20091231",  # 从基日开始
        end_date=today  # 到当前真实日期
    )
    
    print(f"\n✅ 成功获取真实数据！")
    print(f"数据行数: {len(real_data)}")
    print(f"日期范围: {real_data['日期'].min()} 至 {real_data['日期'].max()}")
    
    # 显示数据概况
    print(f"\n数据概况:")
    print(f"指数代码: {real_data['指数代码'].iloc[0]}")
    print(f"指数名称: {real_data['指数中文全称'].iloc[0]}")
    print(f"起始点位: {real_data['收盘'].iloc[0]}")
    print(f"最新点位: {real_data['收盘'].iloc[-1]}")
    
    # 计算收益率
    total_return = (real_data['收盘'].iloc[-1] - real_data['收盘'].iloc[0]) / real_data['收盘'].iloc[0] * 100
    print(f"总收益率: {total_return:.2f}%")
    
    # 显示前5条和后5条
    print(f"\n前5条数据:")
    print(real_data.head(5).to_string())
    
    print(f"\n后5条数据:")
    print(real_data.tail(5).to_string())
    
    # 保存真实数据
    filename = "931446_真实完整历史数据.csv"
    real_data.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n✅ 真实数据已保存至: {filename}")
    
    # 同时保存Excel格式
    excel_filename = "931446_真实完整历史数据.xlsx"
    real_data.to_excel(excel_filename, index=False)
    print(f"✅ Excel格式已保存至: {excel_filename}")
    
except Exception as e:
    print(f"\n❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()
    
    # 如果失败，尝试获取到2024年底的数据
    print("\n尝试获取到2024年底的数据...")
    try:
        real_data = ak.stock_zh_index_hist_csindex(
            symbol="931446",
            start_date="20091231",
            end_date="20241231"
        )
        print(f"✅ 成功获取数据: {len(real_data)} 条")
        print(f"日期范围: {real_data['日期'].min()} 至 {real_data['日期'].max()}")
        real_data.to_csv("931446_真实历史数据_2024.csv", index=False, encoding='utf-8-sig')
        print("✅ 已保存至: 931446_真实历史数据_2024.csv")
    except Exception as e2:
        print(f"❌ 再次失败: {e2}")