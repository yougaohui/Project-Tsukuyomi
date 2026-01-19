#!/usr/bin/env python3
"""
抖音视频上传脚本（使用保存的 Cookie）
基于 Playwright 实现
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ 请先安装 Playwright：")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
COOKIE_FILE = PROJECT_ROOT / "douyin_cookies.json"


class DouyinUploaderWithLogin:
    """抖音视频上传器（使用登录后的 Cookie）"""
    
    UPLOAD_URL = "https://creator.douyin.com/platform/content/video/upload"
    HOME_URL = "https://creator.douyin.com/creator-micro/home"
    
    def __init__(self, cookie_file: Path = None):
        """
        初始化上传器
        
        Args:
            cookie_file: Cookie 文件路径
        """
        self.cookie_file = cookie_file or COOKIE_FILE
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        if not self.cookie_file.exists():
            raise FileNotFoundError(f"Cookie 文件不存在: {self.cookie_file}")
    
    def _load_cookies(self) -> list:
        """加载 Cookie"""
        if not self.cookie_file.exists():
            raise FileNotFoundError(f"Cookie 文件不存在: {self.cookie_file}")
        
        with open(self.cookie_file, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
        
        cookies = cookie_data.get("cookies", [])
        created_at = cookie_data.get("created_at", "")
        
        # 检查 Cookie 是否过期（超过 7 天）
        if created_at:
            try:
                created_time = datetime.fromisoformat(created_at)
                if datetime.now() - created_time > timedelta(days=7):
                    print("⚠️ Cookie 已超过 7 天，可能需要重新登录")
            except:
                pass
        
        print(f"✅ 加载了 {len(cookies)} 个 Cookie")
        return cookies
    
    def _init_browser(self):
        """初始化浏览器"""
        logger.info("初始化浏览器...")
        
        self.playwright = sync_playwright().start()
        
        self.browser = self.playwright.chromium.launch(
            headless=False,  # 用 False 可以看到上传过程
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080',
            ]
        )
        
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
        )
        
        self.page = self.context.new_page()
        self.page.set_default_timeout(60000)
        self.page.set_default_navigation_timeout(60000)
        
        logger.info("浏览器初始化完成")
    
    def _check_login_status(self) -> bool:
        """检查登录状态"""
        logger.info("检查登录状态...")
        
        try:
            self.page.goto(self.HOME_URL, wait_until="networkidle")
            time.sleep(3)
            
            if "login" in self.page.url.lower():
                logger.warning("⚠️ 需要重新登录")
                return False
            
            logger.info("✅ 登录状态正常")
            return True
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False
    
    def _upload_video(self, video_path: Path) -> bool:
        """上传视频文件"""
        logger.info(f"上传视频: {video_path.name}")
        
        try:
            # 查找文件上传 input
            file_input = self.page.query_selector("input[type='file']")
            
            if file_input:
                absolute_path = str(video_path.resolve())
                logger.info(f"设置文件路径: {absolute_path}")
                file_input.set_input_files(absolute_path)
                logger.info("✅ 视频文件已设置")
                
                # 等待上传
                self._wait_for_upload_complete()
                return True
            else:
                logger.error("❌ 未找到文件上传元素")
                return False
                
        except Exception as e:
            logger.error(f"❌ 视频上传失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _wait_for_upload_complete(self, timeout: int = 180):
        """等待视频上传完成"""
        logger.info("等待视频上传完成...")
        
        start_time = time.time()
        last_progress = -1
        
        while time.time() - start_time < timeout:
            try:
                # 检查进度
                page_content = self.page.content()
                
                # 检查上传完成提示
                if "上传成功" in page_content or "complete" in page_content.lower():
                    logger.info("✅ 视频上传完成")
                    time.sleep(3)
                    return
                
                # 检查进度百分比
                import re
                progress_matches = re.findall(r'(\d+)%', page_content)
                
                if progress_matches:
                    # 取最后一个进度
                    percent = int(progress_matches[-1])
                    if percent != last_progress and percent <= 100:
                        logger.info(f"上传进度: {percent}%")
                        last_progress = percent
                        
                    if percent >= 100:
                        logger.info("✅ 视频上传完成")
                        time.sleep(3)
                        return
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"等待上传时出错: {e}")
                raise
        
        logger.warning("⚠️ 上传超时，但继续执行...")
        time.sleep(3)
    
    def _fill_form(self, title: str, description: str = None, topics: list = None):
        """填写表单"""
        time.sleep(3)  # 等待上传完成后的页面加载
        
        # 填写标题
        if title:
            logger.info(f"填写标题: {title}")
            title_input = self.page.query_selector("input[placeholder*='标题']")
            if title_input:
                title_input.click()
                time.sleep(0.3)
                title_input.press("Control+a")
                time.sleep(0.2)
                title_input.press("Backspace")
                time.sleep(0.2)
                title_input.fill(title)
                time.sleep(0.3)
                logger.info("✅ 标题填写完成")
        
        # 填写描述
        if description:
            logger.info(f"填写描述: {description[:30]}...")
            desc_input = self.page.query_selector("textarea[placeholder*='描述']")
            if desc_input:
                desc_input.click()
                time.sleep(0.3)
                desc_input.fill(description)
                time.sleep(0.3)
                logger.info("✅ 描述填写完成")
        
        # 添加话题
        if topics:
            logger.info(f"添加话题: {topics}")
            for topic in topics:
                topic_input = self.page.query_selector("input[placeholder*='话题']")
                if topic_input:
                    topic_input.fill(topic)
                    time.sleep(0.3)
                    topic_input.press("Enter")
                    time.sleep(0.3)
    
    def _click_publish(self) -> bool:
        """点击发布按钮"""
        logger.info("点击发布按钮...")
        
        try:
            # 查找发布按钮
            publish_button = self.page.query_selector("button:has-text('发布')")
            
            if publish_button and publish_button.is_visible() and publish_button.is_enabled():
                publish_button.scroll_into_view_if_needed()
                time.sleep(0.5)
                publish_button.click()
                logger.info("✅ 已点击发布按钮")
                
                # 等待发布
                self._wait_for_publish_complete()
                return True
            else:
                logger.error("❌ 未找到发布按钮")
                return False
                
        except Exception as e:
            logger.error(f"❌ 点击发布按钮失败: {e}")
            return False
    
    def _wait_for_publish_complete(self, timeout: int = 60):
        """等待发布完成"""
        logger.info("等待发布完成...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                page_content = self.page.content()
                
                # 检查发布成功提示
                if "发布成功" in page_content or "已发布" in page_content:
                    logger.info("✅ 视频发布成功")
                    return
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"等待发布时出错: {e}")
                raise
        
        logger.warning("⚠️ 发布可能还在进行中")
    
    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: Optional[str] = None,
        topics: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        上传视频的完整流程
        
        Args:
            video_path: 视频文件路径
            title: 视频标题
            description: 视频描述（可选）
            topics: 话题标签列表（可选）
            
        Returns:
            上传结果字典
        """
        result = {
            "success": False,
            "video_path": str(video_path),
            "title": title,
            "error": None,
        }
        
        try:
            # 加载 Cookie
            cookies = self._load_cookies()
            
            # 初始化浏览器
            self._init_browser()
            
            # 设置 Cookie
            self.context.add_cookies(cookies)
            
            # 检查登录状态
            if not self._check_login_status():
                raise Exception("Cookie 已过期，需要重新运行 douyin_login.py 登录")
            
            # 访问上传页面
            logger.info("访问上传页面...")
            self.page.goto(self.UPLOAD_URL, wait_until="networkidle", timeout=60000)
            time.sleep(5)
            
            if "login" in self.page.url.lower():
                raise Exception("Cookie 已过期，需要重新登录")
            
            # 1. 上传视频
            if not self._upload_video(video_path):
                raise Exception("视频上传失败")
            
            # 2. 填写表单
            self._fill_form(title, description, topics)
            
            # 3. 点击发布
            if not self._click_publish():
                raise Exception("点击发布失败")
            
            result["success"] = True
            result["message"] = "视频上传并发布成功"
            logger.info("🎉 视频上传流程完成！")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ 上传失败: {e}")
            
        finally:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        
        return result


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="抖音视频上传工具（使用登录后的 Cookie）")
    parser.add_argument("--video", "-v", type=str, required=True, help="视频文件路径")
    parser.add_argument("--title", "-t", type=str, default="AI 生成的火影忍者视频", help="视频标题")
    parser.add_argument("--description", type=str, help="视频描述")
    parser.add_argument("--topics", type=str, default="#火影忍者,#动漫,#AI视频", help="话题标签（逗号分隔）")
    parser.add_argument("--cookie", type=str, help="Cookie 文件路径")
    
    args = parser.parse_args()
    
    try:
        # 创建上传器
        cookie_file = Path(args.cookie) if args.cookie else COOKIE_FILE
        uploader = DouyinUploaderWithLogin(cookie_file=cookie_file)
        
        # 准备参数
        topics = [t.strip() for t in args.topics.split(",")] if args.topics else None
        video_path = Path(args.video)
        
        if not video_path.exists():
            print(f"❌ 视频文件不存在: {video_path}")
            sys.exit(1)
        
        # 执行上传
        result = uploader.upload_video(
            video_path=video_path,
            title=args.title,
            description=args.description,
            topics=topics
        )
        
        if result["success"]:
            print("\n" + "="*60)
            print("✅ 视频上传成功！")
            print("="*60)
            print(f"📹 视频: {result['video_path']}")
            print(f"📝 标题: {result['title']}")
        else:
            print("\n" + "="*60)
            print("❌ 视频上传失败！")
            print("="*60)
            print(f"错误: {result['error']}")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("\n请先运行登录脚本:")
        print("   python douyin_login.py")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 用户取消上传")
    except Exception as e:
        print(f"\n❌ 出错: {e}")


if __name__ == "__main__":
    main()
