import urllib.request
import os

# 下载SimHei字体
font_url = "https://raw.githubusercontent.com/StellarCN/scp_zh/master/fonts/SimHei.ttf"
font_path = "/workspace/SimHei.ttf"

print("正在下载中文字体...")
try:
    urllib.request.urlretrieve(font_url, font_path)
    print(f"✅ 字体下载成功: {font_path}")
    print(f"文件大小: {os.path.getsize(font_path)} bytes")
except Exception as e:
    print(f"❌ 字体下载失败: {e}")
    
    # 尝试备用链接
    backup_urls = [
        "http://129.204.193.216:8001/simhei.ttf",
        "https://cdn.jsdelivr.net/gh/AmphibiaWeb/amphibiaweb-assets@master/fonts/SimHei.ttf"
    ]
    
    for url in backup_urls:
        try:
            print(f"尝试备用链接: {url}")
            urllib.request.urlretrieve(url, font_path)
            print(f"✅ 字体下载成功: {font_path}")
            break
        except Exception as e2:
            print(f"失败: {e2}")
            continue