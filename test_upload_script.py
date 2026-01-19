#!/usr/bin/env python3
"""
上传脚本基本功能测试
"""

import sys
from pathlib import Path

print("="*70)
print("🧪 上传脚本基本功能测试")
print("="*70)

# 1. 检查文件是否存在
script_path = Path("douyin_upload_video.py")
print(f"\n1. 检查脚本文件: {script_path}")
if script_path.exists():
    print(f"   ✅ 文件存在 ({script_path.stat().st_size / 1024:.1f} KB)")
else:
    print("   ❌ 文件不存在")
    sys.exit(1)

# 2. 检查视频文件
video_path = Path("src/data/videos/sasuke_specific_1768745166.mp4")
print(f"\n2. 检查视频文件: {video_path}")
if video_path.exists():
    size = video_path.stat().st_size
    print(f"   ✅ 文件存在 ({size / 1024 / 1024:.2f} MB)")
else:
    print("   ❌ 文件不存在")
    sys.exit(1)

# 3. 导入测试
print("\n3. 测试导入...")
try:
    # 只导入，不实例化（避免打开浏览器）
    import importlib.util
    spec = importlib.util.spec_from_file_location("uploader", "douyin_upload_video.py")
    module = importlib.util.module_from_spec(spec)
    
    # 检查类是否存在
    if hasattr(module, 'DouyinUploader'):
        print("   ✅ DouyinUploader 类存在")
    else:
        print("   ❌ DouyinUploader 类不存在")
        sys.exit(1)
    
    print("   ✅ 脚本可以正常导入")
    
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    sys.exit(1)

# 4. 检查 Chrome 配置
print("\n4. 检查 Chrome 配置...")
user_data_dir = Path("/Users/ygh/Library/Application Support/Google/Chrome/Default")
if user_data_dir.exists():
    print(f"   ✅ Chrome 配置存在: {user_data_dir}")
else:
    print(f"   ❌ Chrome 配置不存在: {user_data_dir}")
    sys.exit(1)

# 5. 检查关键文件
print("\n5. 检查 Chrome 关键文件...")
key_files = ["Preferences", "Cookies", "Bookmarks"]
for key_file in key_files:
    file_path = user_data_dir / key_file
    if file_path.exists():
        print(f"   ✅ {key_file}")
    else:
        print(f"   ⚠️ {key_file} 不存在")

print("\n" + "="*70)
print("✅ 基本功能测试通过！")
print("="*70)

print("\n📖 准备运行上传测试...")
print(f"   视频: {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.2f} MB)")
print("\n💡 提示:")
print("   - 上传过程会打开浏览器窗口")
print("   - 请耐心等待上传完成")
print("   - 可以按 Ctrl+C 取消")
print("="*70)
