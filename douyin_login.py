#!/usr/bin/env python3
"""
抖音 Cookie 登录脚本
使用 Playwright 实现手动登录并导出 Cookie
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ 请先安装 Playwright：")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
COOKIE_FILE = PROJECT_ROOT / "douyin_cookies.json"


class DouyinLogin:
    """抖音登录管理器"""
    
    LOGIN_URL = "https://creator.douyin.com/creator-micro/home"
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def _init_browser(self):
        """初始化浏览器"""
        print("初始化浏览器...")
        
        self.playwright = sync_playwright().start()
        
        self.browser = self.playwright.chromium.launch(
            headless=False,  # 必须用 False，让用户手动操作
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--window-size=1920,1080',
            ]
        )
        
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
        )
        
        self.page = self.context.new_page()
        self.page.set_default_timeout(0)  # 不设置超时，让用户慢慢操作
        
        print("✅ 浏览器已启动")
    
    def login(self):
        """
        引导用户登录
        
        Returns:
            dict: 登录后的 Cookie
        """
        print("\n" + "="*60)
        print("🎬 抖音登录助手")
        print("="*60)
        
        try:
            # 初始化浏览器
            self._init_browser()
            
            # 访问登录页面
            print(f"\n📍 访问登录页面...")
            self.page.goto(self.LOGIN_URL)
            
            print("\n" + "-"*60)
            print("📋 登录步骤：")
            print("-"*60)
            print("1. 如果浏览器显示登录页面，请使用手机扫码登录")
            print("2. 如果已经登录，页面会自动跳转到创作者中心")
            print("3. 登录成功后，按 Enter 键继续导出 Cookie")
            print("-"*60)
            
            # 等待用户操作
            input("\n👆 登录完成后，按 Enter 键继续...")
            
            # 检查登录状态
            print("\n🔍 检查登录状态...")
            print(f"   当前 URL: {self.page.url}")
            
            # 等待页面完全加载
            self.page.wait_for_load_state("networkidle")
            
            # 尝试获取用户信息
            try:
                # 获取页面内容，检查是否登录成功
                page_content = self.page.content()
                
                if "登录" in page_content and "手机号" in page_content:
                    print("❌ 仍未登录，请重新登录")
                    return None
                else:
                    print("✅ 登录成功！")
                    
            except Exception as e:
                print(f"⚠️ 检查登录状态时出错: {e}")
            
            # 导出 Cookie
            print("\n💾 导出 Cookie...")
            cookies = self.context.cookies()
            
            # 保存 Cookie 到文件
            cookie_data = {
                "cookies": cookies,
                "created_at": datetime.now().isoformat(),
                "url": self.LOGIN_URL,
            }
            
            with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cookie_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Cookie 已保存到: {COOKIE_FILE}")
            print(f"   共 {len(cookies)} 个 Cookie")
            
            # 打印 Cookie 摘要
            print("\n📊 Cookie 摘要：")
            for cookie in cookies[:5]:  # 只打印前5个
                print(f"   - {cookie['name']}: {cookie['value'][:20]}...")
            
            if len(cookies) > 5:
                print(f"   ... 共 {len(cookies)} 个")
            
            return cookie_data
            
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
    
    def test_cookie(self) -> bool:
        """
        测试 Cookie 是否有效
        
        Returns:
            bool: Cookie 是否有效
        """
        if not COOKIE_FILE.exists():
            print(f"❌ Cookie 文件不存在: {COOKIE_FILE}")
            return False
        
        try:
            # 加载 Cookie
            with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            cookies = cookie_data.get("cookies", [])
            created_at = cookie_data.get("created_at", "未知")
            
            print("="*60)
            print("🧪 测试 Cookie 有效性")
            print("="*60)
            
            print(f"\n📅 Cookie 创建时间: {created_at}")
            print(f"🍪 Cookie 数量: {len(cookies)}")
            
            # 使用 Playwright 测试
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = browser.new_context()
            page = context.new_page()
            
            # 添加 Cookie
            context.add_cookies(cookies)
            
            # 访问创作者中心
            page.goto("https://creator.douyin.com/creator-micro/home", wait_until="networkidle")
            
            time.sleep(2)
            
            # 检查登录状态
            if "login" in page.url.lower():
                print("\n❌ Cookie 已过期，需要重新登录")
                browser.close()
                playwright.stop()
                return False
            else:
                print("\n✅ Cookie 有效")
                print(f"   URL: {page.url}")
                print(f"   标题: {page.title()}")
            
            browser.close()
            playwright.stop()
            
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="抖音登录助手")
    parser.add_argument("--test", action="store_true", help="测试已保存的 Cookie")
    parser.add_argument("--file", type=str, help="Cookie 文件路径")
    
    args = parser.parse_args()
    
    login = DouyinLogin()
    
    if args.test:
        # 测试 Cookie
        login.COOKIE_FILE = Path(args.file) if args.file else login.COOKIE_FILE
        success = login.test_cookie()
        sys.exit(0 if success else 1)
    
    else:
        # 执行登录
        result = login.login()
        
        if result:
            print("\n" + "="*60)
            print("🎉 登录成功！")
            print("="*60)
            print("\n📝 下一步：")
            print("   1. 测试 Cookie 是否有效:")
            print(f"      python douyin_login.py --test")
            print("\n   2. 使用 Cookie 上传视频:")
            print(f"      python douyin_uploader_playwright.py --video <视频路径>")
            print("\n   3. 如果 Cookie 过期，重新运行此脚本:")
            print(f"      python douyin_login.py")
            print("="*60)
        else:
            print("\n❌ 登录失败")
            sys.exit(1)


if __name__ == "__main__":
    main()
