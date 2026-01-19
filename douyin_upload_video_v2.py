#!/usr/bin/env python3
"""
抖音视频上传工具 v2
使用隐藏自动化特征的 Playwright 复用 Chrome 配置

修复验证码检测问题
"""

import sys
import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any


class DouyinUploaderV2:
    """抖音视频上传器 v2（修复验证码问题）"""
    
    # 上传页面 URL
    UPLOAD_URL = "https://creator.douyin.com/platform/content/video/upload"
    
    # Chrome 用户数据目录
    CHROME_USER_DATA_TEMPLATE = "/Users/{user}/Library/Application Support/Google/Chrome"
    
    def __init__(self, username: str = None):
        """初始化上传器"""
        # 获取用户名
        if username is None:
            username = os.environ.get("USER") or os.environ.get("USERNAME")
            if username is None:
                import getpass
                username = getpass.getuser()
        
        # 构建 Chrome 用户数据目录路径
        self.user_data_dir = self.CHROME_USER_DATA_TEMPLATE.format(user=username)
        
        # 验证路径
        if not Path(self.user_data_dir).exists():
            raise FileNotFoundError(f"Chrome 用户数据目录不存在: {self.user_data_dir}")
        
        print(f"✅ Chrome 用户数据目录: {self.user_data_dir}")
        
        self.playwright = None
        self.context = None
        self.page = None
    
    def _init_browser(self, headless: bool = False):
        """初始化浏览器（隐藏自动化特征）"""
        print("\n" + "="*70)
        print("🚀 启动浏览器（隐藏自动化特征）")
        print("="*70)
        
        try:
            from playwright.sync_api import sync_playwright
            
            self.playwright = sync_playwright().start()
            
            print(f"\n📂 配置信息:")
            print(f"   用户数据目录: {self.user_data_dir}")
            print(f"   显示模式: {'无头模式' if headless else '可视化模式'}")
            
            # 使用 launch_persistent_context，隐藏自动化特征
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=headless,
                timeout=60000,
                viewport={'width': 1920, 'height': 1080},
                # 隐藏自动化特征的参数
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
                ignore_https_errors=True,
                # 禁用自动化检测
                java_script_enabled=True,
                bypass_csp=True,
            )
            
            # 隐藏 webdriver 属性
            self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                });
            """)
            
            # 创建页面
            self.page = self.context.new_page()
            
            # 再次隐藏 webdriver
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            print(f"\n✅ 浏览器启动成功！")
            print(f"   自动化特征已隐藏")
            
            return True
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_login_status(self) -> bool:
        """检查登录状态"""
        print("\n🔍 检查登录状态...")
        
        try:
            # 先访问首页
            self.page.goto("https://www.douyin.com/", wait_until="domcontentloaded")
            time.sleep(3)
            
            # 检查是否需要验证码
            page_content = self.page.content()
            if "验证码" in page_content or "拼图" in page_content or "滑动" in page_content:
                print("⚠️ 检测到验证码验证！")
                print("   请在浏览器中完成验证，然后按 Enter 继续...")
                input()
                time.sleep(2)
            
            # 检查是否登录
            login_indicators = ["我的订单", "创作者中心", "消息"]
            found = [i for i in login_indicators if i in page_content]
            
            if found:
                print(f"✅ 已登录（特征: {', '.join(found)}）")
                return True
            else:
                print("⚠️ 未检测到登录特征，尝试访问创作者中心...")
                self.page.goto("https://creator.douyin.com/", wait_until="domcontentloaded")
                time.sleep(3)
                
                if "login" in self.page.url.lower():
                    print("❌ 未登录，需要先登录抖音")
                    return False
                else:
                    print("✅ 可能已登录（访问创作者中心成功）")
                    return True
                
        except Exception as e:
            print(f"⚠️ 检查登录状态失败: {e}")
            return True
    
    def _upload_video(self, video_path: Path) -> bool:
        """上传视频文件"""
        print(f"\n📤 开始上传视频: {video_path.name}")
        
        try:
            # 访问上传页面
            print("\n🌐 访问上传页面...")
            self.page.goto(self.UPLOAD_URL, wait_until="domcontentloaded")
            time.sleep(5)
            
            # 查找文件上传 input
            print("🔍 查找上传元素...")
            file_input = self.page.query_selector("input[type='file']")
            
            if not file_input:
                print("❌ 未找到文件上传元素")
                self._save_screenshot("upload_error.png")
                return False
            
            # 设置文件
            print(f"\n📁 设置视频文件...")
            absolute_path = str(video_path.resolve())
            file_input.set_input_files(absolute_path)
            print("✅ 文件已设置")
            
            # 等待上传完成
            print("\n⏳ 等待视频上传...")
            upload_success = self._wait_for_upload_complete(timeout=180)
            
            if upload_success:
                print("✅ 视频上传完成")
            else:
                print("⚠️ 未检测到上传完成，继续尝试...")
            
            return True
            
        except Exception as e:
            print(f"❌ 上传失败: {e}")
            self._save_screenshot("upload_error.png")
            return False
    
    def _wait_for_upload_complete(self, timeout: int = 180) -> bool:
        """等待上传完成"""
        print(f"等待上传完成（超时: {timeout}秒）...")
        
        start_time = time.time()
        last_progress = -1
        
        while time.time() - start_time < timeout:
            try:
                page_content = self.page.content()
                
                # 检查上传成功提示
                success_indicators = ["上传成功", "上传完成", "complete", "success"]
                for indicator in success_indicators:
                    if indicator.lower() in page_content.lower():
                        print(f"✅ 检测到上传完成: {indicator}")
                        return True
                
                # 查找进度百分比
                import re
                progress_matches = re.findall(r'(\d+)%', page_content)
                
                if progress_matches:
                    percent = int(progress_matches[-1])
                    if percent != last_progress and percent <= 100:
                        print(f"📊 上传进度: {percent}%")
                        last_progress = percent
                        
                    if percent >= 100:
                        print("✅ 上传进度达到 100%")
                        time.sleep(2)
                        return True
                
                time.sleep(2)
                
            except Exception as e:
                time.sleep(2)
        
        return False
    
    def _fill_form(self, title: str, description: str = None, topics: List[str] = None):
        """填写表单"""
        print(f"\n📝 填写表单...")
        
        time.sleep(3)
        
        # 填写标题
        if title:
            print(f"   填写标题: {title}")
            try:
                title_selectors = [
                    "input[placeholder*='标题']",
                    "textarea[placeholder*='标题']",
                ]
                
                for selector in title_selectors:
                    elem = self.page.query_selector(selector)
                    if elem and elem.is_visible():
                        elem.click()
                        time.sleep(0.5)
                        elem.press("Control+a")
                        time.sleep(0.2)
                        elem.press("Backspace")
                        time.sleep(0.2)
                        elem.fill(title)
                        time.sleep(0.5)
                        print("✅ 标题填写完成")
                        break
                else:
                    print("⚠️ 未找到标题输入框")
                    
            except Exception as e:
                print(f"⚠️ 填写标题失败: {e}")
        
        # 添加话题
        if topics:
            print(f"   添加话题: {topics}")
            try:
                topic_selectors = ["input[placeholder*='话题']"]
                
                for selector in topic_selectors:
                    elem = self.page.query_selector(selector)
                    if elem and elem.is_visible():
                        for topic in topics:
                            elem.fill(topic)
                            time.sleep(0.5)
                            elem.press("Enter")
                            time.sleep(0.5)
                        print("✅ 话题添加完成")
                        break
                else:
                    print("⚠️ 未找到话题输入框")
                    
            except Exception as e:
                print(f"⚠️ 添加话题失败: {e}")
    
    def _click_publish(self) -> bool:
        """点击发布按钮"""
        print("\n🚀 点击发布按钮...")
        
        try:
            publish_selectors = [
                "button:has-text('发布')",
                "button:has-text('确认')",
                "[class*='publish'] button",
            ]
            
            for selector in publish_selectors:
                elem = self.page.query_selector(selector)
                if elem and elem.is_visible() and elem.is_enabled():
                    elem.scroll_into_view_if_needed()
                    time.sleep(1)
                    elem.click()
                    print("✅ 已点击发布按钮")
                    self._wait_for_publish_complete()
                    return True
            
            print("❌ 未找到发布按钮")
            self._save_screenshot("publish_error.png")
            return False
            
        except Exception as e:
            print(f"❌ 点击发布按钮失败: {e}")
            self._save_screenshot("publish_error.png")
            return False
    
    def _wait_for_publish_complete(self, timeout: int = 60):
        """等待发布完成"""
        print(f"等待发布完成（超时: {timeout}秒）...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                page_content = self.page.content()
                
                success_indicators = ["发布成功", "已发布", "success"]
                for indicator in success_indicators:
                    if indicator in page_content:
                        print(f"✅ 发布成功: {indicator}")
                        return
                
                time.sleep(1)
                
            except Exception as e:
                time.sleep(1)
        
        print("⚠️ 等待发布超时")
    
    def _save_screenshot(self, filename: str):
        """保存页面截图"""
        try:
            self.page.screenshot(path=f"debug_{filename}")
            print(f"📸 截图已保存: debug_{filename}")
        except Exception as e:
            print(f"⚠️ 保存截图失败: {e}")
    
    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: Optional[str] = None,
        topics: Optional[List[str]] = None,
        headless: bool = False
    ) -> Dict[str, Any]:
        """上传单个视频的完整流程"""
        result = {
            "success": False,
            "video_path": str(video_path),
            "title": title,
            "error": None,
            "message": "",
        }
        
        try:
            if not video_path.exists():
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            if not self._init_browser(headless=headless):
                raise Exception("浏览器启动失败")
            
            if not self._check_login_status():
                raise Exception("未登录抖音")
            
            if not self._upload_video(video_path):
                raise Exception("视频上传失败")
            
            self._fill_form(title, description, topics)
            
            if not self._click_publish():
                raise Exception("点击发布失败")
            
            result["success"] = True
            result["message"] = "视频上传并发布成功"
            
            print("\n" + "="*70)
            print("🎉 视频上传成功！")
            print("="*70)
            
        except Exception as e:
            result["error"] = str(e)
            result["message"] = f"上传失败: {str(e)}"
            print(f"\n❌ 上传失败: {e}")
            
        finally:
            if self.context:
                self.context.close()
                print("\n👋 浏览器已关闭")
            
            if self.playwright:
                self.playwright.stop()
        
        return result


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="抖音视频上传工具 v2（修复验证码问题）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--video", "-v", type=str, required=True, help="视频文件路径")
    parser.add_argument("--title", "-t", type=str, default="AI 生成的火影忍者视频", help="视频标题")
    parser.add_argument("--topics", type=str, help="话题标签（逗号分隔）")
    parser.add_argument("--username", "-u", type=str, help="macOS 用户名")
    parser.add_argument("--headless", action="store_true", help="使用无头模式")
    
    args = parser.parse_args()
    
    # 解析话题
    topics = None
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    
    # 创建上传器
    try:
        uploader = DouyinUploaderV2(username=args.username)
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    
    # 上传视频
    video_path = Path(args.video)
    result = uploader.upload_video(
        video_path=video_path,
        title=args.title,
        topics=topics,
        headless=args.headless
    )
    
    if result["success"]:
        print("\n✅ 视频上传成功！")
        sys.exit(0)
    else:
        print(f"\n❌ 视频上传失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
