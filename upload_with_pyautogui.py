#!/usr/bin/env python3
"""
抖音视频上传工具 - 使用 PyAutoGUI 模拟真实鼠标键盘操作

使用说明:
  1. 先打开抖音创作者中心并登录
  2. 打开上传页面
  3. 运行此脚本
  4. 脚本会自动点击上传按钮，选择文件，填写信息

注意事项:
  - 需要将浏览器窗口放在屏幕左上角
  - 需要调整坐标以匹配你的屏幕分辨率
  - 建议在 1920x1080 分辨率下使用
"""

import sys
import time
import os
from pathlib import Path

try:
    import pyautogui
    import pyperclip
except ImportError:
    print("❌ 请先安装依赖:")
    print("   pip install pyautogui pyperclip")
    sys.exit(1)

# PyAutoGUI 配置
pyautogui.FAILSAFE = True  # 启用安全保护（将鼠标移到左上角可停止）
pyautogui.PAUSE = 0.5  # 操作间隔（秒）


class DouyinUploaderPyAutoGUI:
    """使用 PyAutoGUI 模拟上传"""
    
    def __init__(self):
        """初始化"""
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"📺 屏幕分辨率: {self.screen_width}x{self.screen_height}")
        
        # 抖音上传页面元素位置（需要根据实际情况调整）
        # 这些坐标假设浏览器窗口在 (0, 0)，分辨率为 1920x1080
        self.upload_button_pos = (500, 400)  # 上传按钮位置
        self.title_input_pos = (400, 200)    # 标题输入框位置
        self.publish_button_pos = (800, 700) # 发布按钮位置
        
        print("✅ 初始化完成")
    
    def click(self, x, y, clicks=1):
        """点击指定位置"""
        print(f"🖱️ 点击 ({x}, {y})")
        pyautogui.click(x=x, y=y, clicks=clicks)
        time.sleep(0.5)
    
    def double_click(self, x, y):
        """双击"""
        print(f"🖱️ 双击 ({x}, {y})")
        pyautogui.doubleClick(x=x, y=y)
        time.sleep(0.5)
    
    def type_text(self, text):
        """输入文字（使用剪贴板）"""
        print(f"⌨️ 输入: {text}")
        pyperclip.copy(text)
        pyautogui.hotkey('command', 'v')  # macOS 粘贴
        time.sleep(0.5)
    
    def press_key(self, key):
        """按键"""
        print(f"⌨️ 按键: {key}")
        pyautogui.press(key)
        time.sleep(0.3)
    
    def wait_for_window(self, title_keyword, timeout=10):
        """等待窗口出现"""
        print(f"⏳ 等待窗口: {title_keyword}")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查当前活动窗口
            try:
                active_window = pyautogui.getActiveWindowTitle()
                if active_window and title_keyword in active_window:
                    print(f"✅ 找到窗口: {active_window}")
                    return True
            except:
                pass
            
            time.sleep(1)
        
        print("⚠️ 未找到指定窗口，继续...")
        return False
    
    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: str = None,
        topics: list = None
    ):
        """
        上传视频
        
        注意：这是一个半自动化的脚本，需要用户配合完成某些步骤
        """
        print("\n" + "="*70)
        print("🎬 PyAutoGUI 视频上传流程")
        print("="*70)
        
        if not video_path.exists():
            print(f"❌ 视频文件不存在: {video_path}")
            return False
        
        print(f"\n📹 视频: {video_path.name}")
        print(f"📝 标题: {title}")
        
        # 步骤说明
        print("\n📋 操作步骤:")
        print("  1. 确保抖音创作者中心已打开")
        print("  2. 脚本将自动执行以下操作:")
        print("     - 点击上传按钮")
        print("     - 选择视频文件")
        print("     - 填写标题")
        print("     - 点击发布")
        print("\n💡 提示:")
        print("  - 将浏览器窗口放在屏幕左上角")
        print("  - 按 Ctrl+C 可随时停止")
        print("  - 如果坐标不准确，需要手动调整")
        
        # 等待用户准备
        print("\n👇 请将浏览器窗口放在屏幕左上角")
        print("   然后按 Enter 继续..."
        input()
        
        try:
            # 步骤 1：点击上传区域
            print("\n📤 步骤 1: 点击上传区域")
            self.click(*self.upload_button_pos)
            
            # 步骤 2：等待文件选择器打开
            print("\n📁 步骤 2: 选择视频文件")
            print("   等待文件选择器...")
            time.sleep(2)
            
            # 使用快捷键打开文件选择器（如果需要）
            # pyautogui.hotkey('command', 'o')
            # time.sleep(1)
            
            # 步骤 3：输入文件路径
            print(f"\n🔧 步骤 3: 输入文件路径")
            print("   请在文件选择器中导航到:")
            print(f"   {video_path}")
            print("   然后按 Enter 继续...")
            input()
            
            # 步骤 4：填写标题
            print(f"\n📝 步骤 4: 填写标题")
            print("   点击标题输入框...")
            self.click(*self.title_input_pos)
            time.sleep(0.5)
            
            # 全选并删除现有内容
            pyautogui.hotkey('command', 'a')
            time.sleep(0.2)
            pyautogui.press('backspace')
            time.sleep(0.2)
            
            # 输入标题
            self.type_text(title)
            
            # 步骤 5：添加话题（如果需要）
            if topics:
                print(f"\n🏷️ 步骤 5: 添加话题")
                for topic in topics:
                    print(f"   添加: {topic}")
                    # 这里需要找到话题输入框的位置
                    # 暂时跳过
                    time.sleep(0.5)
            
            # 步骤 6：点击发布
            print(f"\n🚀 步骤 6: 点击发布按钮")
            self.click(*self.publish_button_pos)
            
            print("\n✅ 自动操作完成！")
            print("   请在浏览器中确认上传状态")
            
            return True
            
        except KeyboardInterrupt:
            print("\n👋 用户取消操作")
            return False
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            return False
    
    def find_and_click_button(self, button_text, timeout=10):
        """
        查找并点击包含指定文字的按钮
        使用图像识别（需要先截图保存按钮图片）
        """
        print(f"🔍 查找按钮: {button_text}")
        
        # 尝试使用图像识别
        button_image = f"buttons/{button_text}.png"
        
        if Path(button_image).exists():
            try:
                # 查找按钮位置
                location = pyautogui.locateOnScreen(button_image, confidence=0.8)
                
                if location:
                    center = pyautogui.center(location)
                    print(f"✅ 找到按钮: {button_text} at {center}")
                    self.click(*center)
                    return True
                else:
                    print(f"❌ 未找到按钮: {button_text}")
                    return False
                    
            except Exception as e:
                print(f"❌ 图像识别失败: {e}")
                return False
        else:
            print(f"❌ 按钮图片不存在: {button_image}")
            print("💡 请先截图保存按钮图片到 buttons/ 目录")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="抖音视频上传工具 - 使用 PyAutoGUI 模拟鼠标键盘操作",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 上传视频
  python3 upload_with_pyautogui.py --video test.mp4 --title "我的视频"

注意事项:
  - 需要安装: pip install pyautogui pyperclip
  - 需要将浏览器窗口放在屏幕左上角
  - 需要根据屏幕分辨率调整坐标
  - 需要手动选择文件（在文件选择器中）
        """
    )
    
    parser.add_argument("--video", "-v", type=str, required=True, help="视频文件路径")
    parser.add_argument("--title", "-t", type=str, default="AI 生成的视频", help="视频标题")
    parser.add_argument("--description", type=str, help="视频描述")
    parser.add_argument("--topics", type=str, help="话题标签（逗号分隔）")
    
    args = parser.parse_args()
    
    # 解析话题
    topics = None
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    
    # 创建上传器
    uploader = DouyinUploaderPyAutoGUI()
    
    # 上传视频
    result = uploader.upload_video(
        video_path=Path(args.video),
        title=args.title,
        description=args.description,
        topics=topics
    )
    
    if result:
        print("\n✅ 脚本执行完成！")
        print("   请在浏览器中确认上传状态")
    else:
        print("\n❌ 脚本执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
