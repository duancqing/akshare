import akshare as ak
import pandas as pd
from datetime import datetime

print("="*80)
print("获取真实的931446指数数据（2020.4.24至今）")
print("="*80)

# 获取真实当前日期
real_now = datetime.now()
print(f"\n系统当前时间: {real_now}")

# 从中证指数官网获取真实数据
print("\n正在从中证指数官网API获取最新真实数据...")

try:
    # 获取从2020年4月24日到当前真实日期的数据
    start_date = "20200424"
    end_date = real_now.strftime("%Y%m%d")
    
    print(f"获取数据范围: {start_date} 至 {end_date}")
    
    real_data = ak.stock_zh_index_hist_csindex(
        symbol="931446",
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"\n✅ 成功获取真实数据！")
    print(f"数据行数: {len(real_data)}")
    print(f"日期范围: {real_data['日期'].min()} 至 {real_data['日期'].max()}")
    
    # 显示最新数据
    print(f"\n最新5条数据:")
    print(real_data.tail(5).to_string())
    
    # 检查数据是否真实
    print(f"\n数据验证:")
    print(f"指数代码: {real_data['指数代码'].iloc[0]}")
    print(f"指数名称: {real_data['指数中文全称'].iloc[0]}")
    print(f"起始点位(2020-04-24): {real_data['收盘'].iloc[0]}")
    print(f"最新点位: {real_data['收盘'].iloc[-1]}")
    
    # 保存真实数据
    filename = "931446_真实数据_20200424至今.csv"
    real_data.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n✅ 真实数据已保存至: {filename}")
    
    # 计算这段时间的收益率
    start_price = real_data['收盘'].iloc[0]
    end_price = real_data['收盘'].iloc[-1]
    total_return = (end_price - start_price) / start_price * 100
    print(f"\n这段时间买入持有收益率: {total_return:.2f}%")
    
except Exception as e:
    print(f"\n❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()
    
    # 如果失败，尝试获取到2024年底
    print("\n尝试获取到2024年底的数据...")
    try:
        real_data = ak.stock_zh_index_hist_csindex(
            symbol="931446",
            start_date="20200424",
            end_date="20241231"
        )
        print(f"✅ 成功获取数据: {len(real_data)} 条")
        print(f"日期范围: {real_data['日期'].min()} 至 {real_data['日期'].max()}")
        real_data.to_csv("931446_真实数据_20200424_2024.csv", index=False, encoding='utf-8-sig')
        print("✅ 已保存至: 931446_真实数据_20200424_2024.csv")
    except Exception as e2:
        print(f"❌ 再次失败: {e2}")