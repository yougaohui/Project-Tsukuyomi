#!/usr/bin/env python3
"""
抖音视频上传助手（简易版）
无需安装额外依赖，使用系统剪贴板辅助

使用流程：
  1. 在浏览器中打开抖音创作者中心上传页面
  2. 手动选择视频文件
  3. 运行此脚本
  4. 脚本会帮你准备好要填写的内容
  5. 你只需要点击输入框并粘贴
"""

import sys
import time
from pathlib import Path
import subprocess  # 用于剪贴板操作


class SimpleUploadHelper:
    """简易上传助手"""
    
    def __init__(self):
        """初始化"""
        self.title = ""
        self.topics = []
        
        # 检测操作系统
        self.is_mac = sys.platform == "darwin"
        self.is_windows = sys.platform == "win32"
        
        print("🎬 抖音视频上传助手（简易版）")
        print("="*60)
        print("特点：")
        print("  ✅ 无需安装额外依赖")
        print("  ✅ 使用系统剪贴板")
        print("  ✅ 简单可靠")
        print("="*60)
    
    def copy_to_clipboard(self, text: str) -> bool:
        """复制到剪贴板"""
        try:
            if self.is_mac:
                # macOS 使用 pbcopy
                process = subprocess.Popen(
                    ["pbcopy"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=text.encode("utf-8"))
            elif self.is_windows:
                # Windows 使用 clip
                process = subprocess.Popen(
                    ["clip"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=text.encode("utf-8"))
            else:
                # Linux 使用 xclip 或 xsel
                try:
                    subprocess.run(
                        ["xclip", "-selection", "clipboard"],
                        input=text.encode("utf-8"),
                        check=True
                    )
                except:
                    subprocess.run(
                        ["xsel", "--clipboard", "--input"],
                        input=text.encode("utf-8"),
                        check=True
                    )
            
            print(f"📋 已复制: {text[:40]}...")
            return True
            
        except Exception as e:
            print(f"❌ 复制失败: {e}")
            return False
    
    def copy_title(self, title: str):
        """准备标题"""
        print(f"\n📝 标题: {title}")
        self.title = title
        return self.copy_to_clipboard(title)
    
    def copy_topics(self, topics: list):
        """准备话题"""
        if not topics:
            print("\n🏷️ 无话题")
            return
        
        print(f"\n🏷️ 话题列表:")
        for i, topic in enumerate(topics, 1):
            print(f"   {i}. {topic}")
        
        # 复制第一个话题
        print(f"\n💡 操作提示:")
        print(f"   第一个话题已复制到剪贴板: {topics[0]}")
        self.copy_to_clipboard(topics[0])
        
        # 保存所有话题
        self.topics = topics
    
    def show_instructions(self):
        """显示操作说明"""
        print("\n" + "="*60)
        print("📋 操作步骤")
        print("="*60)
        
        print("""
1️⃣  【已经完成】在浏览器中上传页面选择了视频文件

2️⃣  【现在进行】填写标题
    - 点击标题输入框
    - 按 Cmd+V (Mac) 或 Ctrl+V (Windows) 粘贴
    - 标题: {title}

3️⃣  【选择进行】添加话题（如果需要）
    - 点击话题输入框
    - 按 Cmd+V 粘贴第一个话题: {first_topic}
    - 按 Enter 添加
    - 重复添加其他话题

4️⃣  【最后】检查并点击发布按钮
        """.format(
            title=self.title,
            first_topic=self.topics[0] if self.topics else "无"
        ))
        
        print("="*60)
    
    def run(self, title: str, topics: list = None):
        """运行助手"""
        print(f"\n🎯 准备上传视频")
        print(f"   标题: {title}")
        if topics:
            print(f"   话题: {', '.join(topics)}")
        
        # 复制标题
        self.copy_title(title)
        
        # 复制话题
        if topics:
            self.copy_topics(topics)
        
        # 显示说明
        self.show_instructions()
        
        print("\n✅ 已准备就绪！")
        print("   现在切换到浏览器，完成以下操作：")
        print("   1. 点击标题输入框，粘贴标题")
        print("   2. 点击话题输入框，添加话题")
        print("   3. 点击发布按钮")
        print("\n💡 提示：标题和话题已复制到剪贴板，可以直接粘贴")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="抖音视频上传助手（简易版）- 无需安装依赖",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本使用
  python3 simple_upload_helper.py --title "我的视频"

  # 添加话题
  python3 simple_upload_helper.py \
      --title "火影忍者 AI 视频" \
      --topics "#火影忍者,#动漫,#AI"

工作流程:
  1. 在浏览器中打开抖音创作者中心上传页面
  2. 手动选择视频文件
  3. 运行此脚本
  4. 脚本准备好要填写的内容
  5. 你只需要点击输入框并粘贴
        """
    )
    
    parser.add_argument("--title", "-t", type=str, required=True, help="视频标题")
    parser.add_argument("--topics", type=str, help="话题标签（逗号分隔）")
    
    args = parser.parse_args()
    
    # 解析话题
    topics = None
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    
    # 创建助手并运行
    helper = SimpleUploadHelper()
    helper.run(title=args.title, topics=topics)


if __name__ == "__main__":
    main()
