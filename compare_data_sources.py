import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties, fontManager
import os

print("="*80)
print("从东方财富获取931446指数数据并对比")
print("="*80)

# 查找系统中可用的字体
print("\n查找可用字体...")
font_dirs = ['/usr/share/fonts', '/usr/local/share/fonts', '/root/.local/share/fonts']
available_fonts = []

for font_dir in font_dirs:
    if os.path.exists(font_dir):
        for root, dirs, files in os.walk(font_dir):
            for file in files:
                if file.endswith('.ttf') or file.endswith('.otf'):
                    font_path = os.path.join(root, file)
                    available_fonts.append(font_path)
                    print(f"找到字体: {file}")

# 尝试从东方财富获取数据
print("\n" + "="*80)
print("从东方财富获取数据")
print("="*80)

try:
    # 方法1: 使用index_zh_a_hist获取东方财富数据
    print("\n尝试方法1: index_zh_a_hist...")
    df_em = ak.index_zh_a_hist(symbol="931446", period="daily", 
                                start_date="20200424", end_date="20240101")
    print(f"✅ 东方财富数据获取成功！")
    print(f"数据行数: {len(df_em)}")
    print(f"日期范围: {df_em['日期'].min()} 至 {df_em['日期'].max()}")
    
    # 保存东方财富数据
    df_em.to_csv("东方财富_931446数据.csv", index=False, encoding='utf-8-sig')
    print("已保存: 东方财富_931446数据.csv")
    
except Exception as e:
    print(f"方法1失败: {e}")
    
    try:
        # 方法2: 使用stock_zh_index_daily
        print("\n尝试方法2: stock_zh_index_daily...")
        df_em = ak.stock_zh_index_daily(symbol="sz931446")
        print(f"✅ 数据获取成功！")
        print(f"数据行数: {len(df_em)}")
        df_em.to_csv("东方财富_931446数据.csv", index=False, encoding='utf-8-sig')
    except Exception as e2:
        print(f"方法2也失败: {e2}")
        df_em = None

# 加载中证指数官网数据
print("\n" + "="*80)
print("加载中证指数官网数据对比")
print("="*80)

df_csindex = pd.read_csv("931446_真实数据_20200424至今.csv")
df_csindex['日期'] = pd.to_datetime(df_csindex['日期'])

print(f"中证指数数据行数: {len(df_csindex)}")
print(f"日期范围: {df_csindex['日期'].min()} 至 {df_csindex['日期'].max()}")

# 对比数据
if df_em is not None and len(df_em) > 0:
    print("\n" + "="*80)
    print("数据对比")
    print("="*80)
    
    df_em['日期'] = pd.to_datetime(df_em['日期'])
    
    # 合并数据进行对比
    merged = pd.merge(
        df_csindex[['日期', '收盘']].rename(columns={'收盘': '中证指数'}),
        df_em[['日期', '收盘']].rename(columns={'收盘': '东方财富'}),
        on='日期',
        how='inner'
    )
    
    if len(merged) > 0:
        merged['差异'] = merged['中证指数'] - merged['东方财富']
        merged['差异率%'] = (merged['差异'] / merged['中证指数']) * 100
        
        print(f"\n重叠数据行数: {len(merged)}")
        print(f"\n差异统计:")
        print(f"平均差异: {merged['差异'].mean():.2f}")
        print(f"平均差异率: {merged['差异率%'].mean():.2f}%")
        print(f"最大差异: {merged['差异'].max():.2f}")
        print(f"最小差异: {merged['差异'].min():.2f}")
        
        # 显示对比数据
        print(f"\n数据对比示例:")
        print(merged.head(10).to_string())
        
        # 判断数据是否一致
        if abs(merged['差异'].mean()) < 1:
            print("\n✅ 两个数据源的数据基本一致！")
        else:
            print(f"\n⚠️ 数据存在差异，平均差异: {merged['差异'].mean():.2f}")
    
    # 创建对比图
    print("\n" + "="*80)
    print("生成对比图表")
    print("="*80)
    
    # 使用DejaVu Sans字体（系统中有）
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图表
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    # 子图1: 价格对比
    ax1 = axes[0]
    ax1.plot(df_csindex['日期'], df_csindex['收盘'], 
             label='CS Index Official', linewidth=2, color='#2E86AB')
    ax1.plot(df_em['日期'], df_em['收盘'], 
             label='East Money', linewidth=2, color='#A23B72', alpha=0.7)
    ax1.set_title('Index 931446 Price Comparison', fontsize=16, weight='bold')
    ax1.set_ylabel('Price', fontsize=14)
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    
    # 子图2: 差异曲线
    ax2 = axes[1]
    if len(merged) > 0:
        ax2.plot(merged['日期'], merged['差异'], 
                 label='Difference', linewidth=2, color='#C73E1D')
        ax2.fill_between(merged['日期'], merged['差异'], 0, 
                         color='#C73E1D', alpha=0.3)
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax2.set_title('Price Difference (CS Index - East Money)', fontsize=16, weight='bold')
        ax2.set_ylabel('Difference', fontsize=14)
        ax2.legend(fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    
    plt.tight_layout()
    plt.savefig('数据源对比图.png', dpi=150, bbox_inches='tight')
    print("✅ 对比图已保存: 数据源对比图.png")
    
else:
    print("\n⚠️ 东方财富数据获取失败，无法对比")
    print("可能原因: 网络代理问题或API限制")

# 显示中证指数数据的详细信息
print("\n" + "="*80)
print("中证指数数据详情")
print("="*80)
print(f"指数代码: {df_csindex['指数代码'].iloc[0]}")
print(f"指数名称: {df_csindex['指数中文全称'].iloc[0]}")
print(f"数据来源: 中证指数官网 (akshare.stock_zh_index_hist_csindex)")
print(f"\n最近5天数据:")
print(df_csindex[['日期', '开盘', '最高', '最低', '收盘']].tail(5).to_string())

print("\n✅ 数据验证完成！")