#!/usr/bin/env python3
"""
抖音视频上传助手
半自动化工具：手动选择文件 + 脚本辅助填写

使用流程:
  1. 在浏览器中打开抖音创作者中心上传页面
  2. 手动选择视频文件
  3. 运行此脚本，脚本会辅助填写信息
  4. 脚本完成后，手动点击发布
"""

import sys
import time
from pathlib import Path
from typing import Optional, List
import pyperclip  # 用于剪贴板操作


class UploadAssistant:
    """上传助手 - 辅助填写信息"""
    
    def __init__(self):
        """初始化"""
        print("🎬 抖音视频上传助手")
        print("="*60)
        print("流程:")
        print("  1. 在浏览器中打开上传页面")
        print("  2. 手动选择视频文件")
        print("  3. 运行此脚本辅助填写")
        print("  4. 手动点击发布")
        print("="*60)
        
        try:
            import pyautogui
            self.has_pyautogui = True
            print("✅ PyAutoGUI 已安装")
        except ImportError:
            self.has_pyautogui = False
            print("⚠️ PyAutoGUI 未安装，将使用剪贴板方式")
    
    def copy_to_clipboard(self, text: str):
        """复制到剪贴板"""
        try:
            pyperclip.copy(text)
            print(f"📋 已复制到剪贴板: {text[:30]}...")
            return True
        except Exception as e:
            print(f"❌ 复制失败: {e}")
            return False
    
    def find_browser_window(self, browser_name: str = "Chrome") -> bool:
        """查找浏览器窗口"""
        print(f"\n🔍 查找 {browser_name} 窗口...")
        
        try:
            import pyautogui
            
            # 尝试查找浏览器窗口
            windows = []
            for window in pyautogui.getAllWindows():
                if browser_name.lower() in window.title.lower():
                    windows.append(window)
            
            if windows:
                print(f"✅ 找到 {len(windows)} 个 {browser_name} 窗口")
                # 激活最后一个窗口
                windows[-1].activate()
                return True
            else:
                print(f"❌ 未找到 {browser_name} 窗口")
                return False
                
        except Exception as e:
            print(f"⚠️ 查找窗口失败: {e}")
            return False
    
    def fill_title(self, title: str) -> bool:
        """填写标题"""
        print(f"\n📝 填写标题: {title}")
        
        # 复制标题到剪贴板
        if not self.copy_to_clipboard(title):
            return False
        
        # 尝试使用 PyAutoGUI
        if self.has_pyautogui:
            try:
                import pyautogui
                
                # 查找标题输入框（需要用户先点击）
                print("👆 请点击标题输入框...")
                input("   然后按 Enter 继续...")
                
                # 全选并粘贴
                pyautogui.hotkey('command', 'a')
                time.sleep(0.2)
                pyautogui.hotkey('command', 'v')
                time.sleep(0.5)
                
                print("✅ 标题填写完成")
                return True
                
            except Exception as e:
                print(f"⚠️ PyAutoGUI 方式失败: {e}")
        
        # 备用方式：提示用户
        print("\n💡 备用方式:")
        print("   1. 点击标题输入框")
        print("   2. 按 Cmd+V 粘贴")
        print(f"   标题: {title}")
        
        return True
    
    def fill_topics(self, topics: List[str]) -> bool:
        """填写话题"""
        print(f"\n🏷️ 话题列表:")
        for i, topic in enumerate(topics, 1):
            print(f"   {i}. {topic}")
        
        # 复制第一个话题
        if topics:
            self.copy_to_clipboard(topics[0])
        
        print("\n💡 操作提示:")
        print("   1. 点击话题输入框")
        print("   2. 按 Cmd+V 粘贴第一个话题")
        print("   3. 按 Enter 添加")
        print("   4. 重复添加其他话题")
        
        return True
    
    def wait_for_upload(self, timeout: int = 120) -> bool:
        """等待上传完成"""
        print(f"\n⏳ 等待上传完成（超时: {timeout}秒）...")
        
        print("💡 请在浏览器中查看上传进度")
        print("   上传完成后，按 Enter 继续...")
        input()
        
        return True
    
    def click_publish_button(self) -> bool:
        """提示点击发布按钮"""
        print("\n🚀 发布前检查:")
        print("   ✅ 视频已上传")
        print("   ✅ 标题已填写（如果需要）")
        print("   ✅ 话题已添加（如果需要）")
        
        print("\n👇 最后一步:")
        print("   请手动点击页面上的【发布】按钮")
        
        return True
    
    def run(
        self,
        title: str,
        topics: Optional[List[str]] = None,
        wait_upload: bool = True
    ):
        """运行助手流程"""
        print("\n" + "="*60)
        print("🎬 开始辅助流程")
        print("="*60)
        
        # 步骤 1: 填写标题
        if title:
            self.fill_title(title)
        
        # 步骤 2: 填写话题
        if topics:
            self.fill_topics(topics)
        
        # 步骤 3: 等待上传
        if wait_upload:
            self.wait_for_upload()
        
        # 步骤 4: 点击发布
        self.click_publish_button()
        
        print("\n" + "="*60)
        print("✅ 辅助流程完成！")
        print("="*60)
        print("\n📋 后续步骤:")
        print("   1. 检查所有信息是否正确")
        print("   2. 点击【发布】按钮")
        print("   3. 在抖音中确认发布状态")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="抖音视频上传助手 - 辅助填写信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本使用
  python3 upload_assistant.py --title "我的视频"

  # 添加话题
  python3 upload_assistant.py \
      --title "火影忍者 AI 视频" \
      --topics "#火影忍者,#动漫,#AI"

  # 不等待上传（如果已经上传完成）
  python3 upload_assistant.py \
      --title "测试视频" \
      --nowait

工作流程:
  1. 在浏览器中打开抖音上传页面
  2. 手动选择视频文件
  3. 运行此脚本辅助填写信息
  4. 手动点击发布按钮
        """
    )
    
    parser.add_argument("--title", "-t", type=str, required=True, help="视频标题")
    parser.add_argument("--topics", type=str, help="话题标签（逗号分隔）")
    parser.add_argument("--nowait", action="store_true", help="不等待上传完成")
    parser.add_argument("--browser", type=str, default="Chrome", help="浏览器名称")
    
    args = parser.parse_args()
    
    # 解析话题
    topics = None
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    
    # 创建助手
    assistant = UploadAssistant()
    
    # 运行
    assistant.run(
        title=args.title,
        topics=topics,
        wait_upload=not args.nowait
    )


if __name__ == "__main__":
    main()
