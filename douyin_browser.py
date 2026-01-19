#!/usr/bin/env python3
"""
抖音浏览器登录工具
使用 Playwright 复用已有的 Chrome 浏览器配置

使用说明:
  python3 douyin_browser.py              # 可视化模式
  python3 douyin_browser.py --headless   # 无头模式（不显示浏览器）
  python3 douyin_browser.py --url <网址>  # 访问特定页面
"""

import sys
import os
import time
from pathlib import Path


class DouyinBrowser:
    """抖音浏览器管理器 - 复用 Chrome 配置"""
    
    # macOS Chrome 用户数据目录模板
    CHROME_USER_DATA_TEMPLATE = "/Users/{user}/Library/Application Support/Google/Chrome"
    
    # 抖音网址
    DOUYIN_URL = "https://www.douyin.com/"
    CREATOR_URL = "https://creator.douyin.com/"
    
    def __init__(self, username: str = None):
        """
        初始化浏览器管理器
        
        Args:
            username: 你的 macOS 用户名（用于构建 Chrome 用户数据目录）
                     如果不提供，会自动从系统获取
        """
        # 如果未提供用户名，自动从系统获取
        if username is None:
            username = os.environ.get("USER") or os.environ.get("USERNAME")
            if username is None:
                import getpass
                username = getpass.getuser()
        
        # 构建完整的用户数据目录路径（使用 Default Profile）
        self.user_data_dir = self.CHROME_USER_DATA_TEMPLATE.format(user=username) + "/Default"
        
        # 验证路径
        if not Path(self.user_data_dir).exists():
            # 尝试查找其他 Profile
            base_dir = self.CHROME_USER_DATA_TEMPLATE.format(user=username)
            if Path(base_dir).exists():
                # 查找 Default 或其他 Profile
                for profile in ["Default", "Profile 1", "Profile 2"]:
                    test_path = Path(base_dir) / profile
                    if test_path.exists():
                        self.user_data_dir = str(test_path)
                        print(f"⚠️ 使用 Profile: {profile}")
                        break
                else:
                    # 使用第一个存在的子目录
                    profiles = list(Path(base_dir).glob("Profile *"))
                    if profiles:
                        self.user_data_dir = str(profiles[0])
                        print(f"⚠️ 使用 Profile: {profiles[0].name}")
                    else:
                        raise FileNotFoundError(f"Chrome 用户数据目录不存在: {self.user_data_dir}")
            else:
                raise FileNotFoundError(f"Chrome 用户数据目录不存在: {self.user_data_dir}")
        
        print(f"✅ Chrome 用户数据目录: {self.user_data_dir}")
        
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def launch_browser(self, headless: bool = False):
        """启动浏览器（复用已有配置）"""
        print("\n" + "="*60)
        print("🚀 启动 Chrome 浏览器（复用已有配置）")
        print("="*60)
        
        try:
            from playwright.sync_api import sync_playwright
            
            # 启动 Playwright
            self.playwright = sync_playwright().start()
            
            print(f"\n📂 使用配置:")
            print(f"   用户数据目录: {self.user_data_dir}")
            print(f"   显示模式: {'无头模式' if headless else '可视化模式'}")
            
            # 使用 launch_persistent_context 复用 Chrome 配置
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,  # 必需参数：用户数据目录
                headless=headless,                 # 是否无头模式
                timeout=30000,                     # 超时时间（毫秒）
                viewport={'width': 1920, 'height': 1080},  # 视口大小
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',  # User-Agent
                locale='zh-CN',                     # 语言区域
                ignore_https_errors=True,           # 忽略 HTTPS 错误
            )
            
            # 创建页面
            self.page = self.context.new_page()
            
            print(f"\n✅ 浏览器启动成功！")
            
            return True
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def visit_douyin(self, url: str = None):
        """访问抖音网站"""
        target_url = url or self.DOUYIN_URL
        
        print("\n" + "="*60)
        print(f"🌐 访问: {target_url}")
        print("="*60)
        
        try:
            self.page.goto(target_url)
            
            # 等待页面加载
            self.page.wait_for_load_state("domcontentloaded")
            time.sleep(3)
            
            final_url = self.page.url
            title = self.page.title()
            
            print(f"\n📊 页面信息:")
            print(f"   最终 URL: {final_url}")
            print(f"   页面标题: {title}")
            
            if "抖音" in title or "douyin" in final_url.lower():
                print(f"\n✅ 成功访问抖音！")
                return True
            else:
                print(f"\n⚠️ 警告：页面标题不包含 '抖音'，可能访问失败")
                return False
                
        except Exception as e:
            print(f"❌ 访问失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_login_status(self) -> dict:
        """检查登录状态"""
        print("\n" + "="*60)
        print("🔍 检查登录状态")
        print("="*60)
        
        result = {
            "is_logged_in": False,
            "username": None,
            "cookie_count": 0,
            "message": "",
        }
        
        try:
            page_content = self.page.content()
            page_url = self.page.url
            
            cookies = self.context.cookies()
            result["cookie_count"] = len(cookies)
            
            # 检查登录状态
            if "login" in page_url.lower():
                result["message"] = "需要登录"
                print(f"   状态: 需要登录")
                return result
            
            # 检查登录特征
            login_indicators = [
                "我的订单",      # 订单入口
                "创作者中心",    # 创作者入口
                "消息",          # 消息入口
            ]
            
            found_indicators = []
            for indicator in login_indicators:
                if indicator in page_content:
                    found_indicators.append(indicator)
            
            if found_indicators:
                result["is_logged_in"] = True
                result["message"] = f"已登录，发现特征: {', '.join(found_indicators)}"
                print(f"   状态: ✅ 已登录")
                print(f"   特征: {', '.join(found_indicators)}")
            else:
                result["message"] = "未检测到登录状态"
                print(f"   状态: ⚠️ 未检测到登录状态")
            
            print(f"\n🍪 Cookie 信息:")
            print(f"   数量: {len(cookies)}")
            
            # 打印部分 Cookie
            for cookie in cookies[:5]:
                name = cookie['name']
                value = cookie['value']
                display_value = value[:10] + "***" if len(value) > 10 else value
                print(f"   - {name}: {display_value}")
            
            if len(cookies) > 5:
                print(f"   ... 共 {len(cookies)} 个 Cookie")
            
            return result
            
        except Exception as e:
            print(f"❌ 检查登录状态失败: {e}")
            result["message"] = f"检查失败: {str(e)}"
            return result
    
    def close(self):
        """关闭浏览器"""
        print("\n" + "="*60)
        print("👋 关闭浏览器")
        print("="*60)
        
        try:
            if self.context:
                self.context.close()
                print("✅ 浏览器上下文已关闭")
            
            if self.playwright:
                self.playwright.stop()
                print("✅ Playwright 已停止")
                
        except Exception as e:
            print(f"❌ 关闭浏览器时出错: {e}")
    
    def run_full_flow(self, headless: bool = False):
        """运行完整流程"""
        try:
            if not self.launch_browser(headless=headless):
                return False
            
            if not self.visit_douyin():
                return False
            
            login_status = self.check_login_status()
            
            print("\n" + "="*60)
            print("📋 流程完成")
            print("="*60)
            print(f"登录状态: {login_status['message']}")
            print(f"Cookie 数量: {login_status['cookie_count']}")
            
            return login_status["is_logged_in"]
            
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作")
            return False
        except Exception as e:
            print(f"\n❌ 流程执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="抖音浏览器登录工具 - 复用 Chrome 配置",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用自动检测的用户名（可视化模式）
  python3 douyin_browser.py
  
  # 指定用户名
  python3 douyin_browser.py --username myname
  
  # 使用无头模式（不显示浏览器，适合测试）
  python3 douyin_browser.py --headless
  
  # 访问特定页面
  python3 douyin_browser.py --url https://creator.douyin.com/

注意事项:
  1. 确保 Google Chrome 已安装且之前已登录抖音
  2. 运行脚本前请关闭所有 Chrome 窗口
  3. 如果遇到权限问题，检查 Chrome 配置目录权限
        """
    )
    
    parser.add_argument("--username", "-u", type=str, 
                       help="你的 macOS 用户名（默认自动检测）")
    parser.add_argument("--headless", action="store_true", 
                       help="使用无头模式（不显示浏览器窗口）")
    parser.add_argument("--url", type=str, default="https://www.douyin.com/", 
                       help="要访问的网址（默认: https://www.douyin.com/）")
    
    args = parser.parse_args()
    
    # 创建浏览器实例
    browser = DouyinBrowser(username=args.username)
    
    try:
        # 启动浏览器
        if not browser.launch_browser(headless=args.headless):
            print("❌ 浏览器启动失败")
            sys.exit(1)
        
        # 访问抖音
        if not browser.visit_douyin(url=args.url):
            print("❌ 访问抖音失败")
            sys.exit(1)
        
        # 检查登录状态
        login_status = browser.check_login_status()
        
        print("\n" + "="*60)
        print("🎉 完成！")
        print("="*60)
        
        if login_status["is_logged_in"]:
            print("✅ 成功登录抖音！")
        else:
            print("⚠️ 未检测到登录状态，请手动登录抖音")
        
        print(f"\n📊 信息汇总:")
        print(f"   - Cookie 数量: {login_status['cookie_count']}")
        print(f"   - 页面标题: {browser.page.title()}")
        print(f"   - 页面 URL: {browser.page.url}")
        
        # 如果不是无头模式，保持浏览器打开
        if not args.headless:
            print("\n" + "="*60)
            print("💡 提示：")
            print("   浏览器窗口将保持打开，你可以手动操作")
            print("   按 Ctrl+C 关闭浏览器")
            print("="*60)
            
            # 保持浏览器打开
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n👋 收到中断信号，正在关闭...")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        browser.close()


if __name__ == "__main__":
    main()
