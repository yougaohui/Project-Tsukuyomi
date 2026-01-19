#!/usr/bin/env python3
"""
抖音 PC 端视频上传自动化脚本
使用 Playwright 实现
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ 请先安装 Playwright：")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.config.settings import (
    DOUYIN_COOKIE,
    VIDEO_DIR,
    UPLOADED_DIR,
    LOGS_DIR
)
from src.utils.logger import setup_logger, get_logger

setup_logger("douyin_uploader", "INFO")
logger = get_logger(__name__)


class DouyinUploaderPlaywright:
    """抖音视频上传器 - 使用 Playwright"""
    
    UPLOAD_URL = "https://creator.douyin.com/platform/content/video/upload"
    HOME_URL = "https://creator.douyin.com/creator-micro/home"
    
    def __init__(self, cookie: Optional[str] = None):
        """
        初始化上传器
        """
        self.cookie = cookie or DOUYIN_COOKIE
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        if not self.cookie:
            raise ValueError("DOUYIN_COOKIE is required")
    
    def _init_browser(self):
        """初始化浏览器"""
        logger.info("初始化浏览器...")
        
        self.playwright = sync_playwright().start()
        
        # 启动浏览器
        self.browser = self.playwright.chromium.launch(
            headless=True,  # 先用 headless 模式
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )
        
        # 创建浏览器上下文
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
        )
        
        # 创建页面
        self.page = self.context.new_page()
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(60000)
        
        logger.info("浏览器初始化完成")
    
    def _set_cookies(self):
        """设置 Cookie"""
        logger.info("设置抖音 Cookie...")
        
        try:
            cookies = self._parse_cookie_string(self.cookie)
            self.context.add_cookies(cookies)
            logger.info(f"✅ Cookie 设置成功，共 {len(cookies)} 个")
            return True
        except Exception as e:
            logger.error(f"❌ Cookie 设置失败: {e}")
            return False
    
    def _parse_cookie_string(self, cookie_string: str) -> list:
        """解析 Cookie 字符串"""
        cookies = []
        try:
            for item in cookie_string.split(';'):
                item = item.strip()
                if '=' in item:
                    key, value = item.split('=', 1)
                    cookies.append({
                        'name': key.strip(),
                        'value': value.strip(),
                        'domain': '.douyin.com',
                        'path': '/',
                    })
            return cookies
        except Exception as e:
            logger.error(f"Cookie 解析失败: {e}")
            return []
    
    def _check_login_status(self) -> bool:
        """检查登录状态"""
        logger.info("检查登录状态...")
        
        try:
            self.page.goto(self.HOME_URL, wait_until="networkidle")
            time.sleep(2)
            
            # 检查 URL
            if "login" in self.page.url.lower():
                logger.warning("⚠️ 需要登录")
                return False
            
            # 尝试访问上传页面验证
            self.page.goto(self.UPLOAD_URL, wait_until="networkidle")
            time.sleep(2)
            
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
            file_input = None
            upload_selectors = [
                "input[type='file']",
                "input[type='file'][accept*='video']",
            ]
            
            for selector in upload_selectors:
                try:
                    file_input = self.page.query_selector(selector)
                    if file_input:
                        logger.info(f"找到上传元素: {selector}")
                        break
                except:
                    pass
            
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
            return False
    
    def _wait_for_upload_complete(self, timeout: int = 120):
        """等待视频上传完成"""
        logger.info("等待视频上传完成...")
        
        start_time = time.time()
        last_progress = -1
        
        while time.time() - start_time < timeout:
            try:
                # 检查进度
                progress_selectors = [
                    "[class*='progress']",
                    ".progress-bar",
                ]
                
                for selector in progress_selectors:
                    try:
                        progress_element = self.page.query_selector(selector)
                        if progress_element:
                            progress_text = progress_element.inner_text()
                            if '%' in progress_text:
                                percent = int(progress_text.replace('%', '').strip())
                                if percent != last_progress and percent <= 100:
                                    logger.info(f"上传进度: {percent}%")
                                    last_progress = percent
                                    
                                if percent >= 100:
                                    logger.info("✅ 视频上传完成")
                                    time.sleep(2)
                                    return
                    except:
                        pass
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"等待上传时出错: {e}")
                raise
        
        logger.warning("⚠️ 上传超时，但继续执行...")
        time.sleep(3)
    
    def _fill_title(self, title: str) -> bool:
        """填写视频标题"""
        logger.info(f"填写标题: {title}")
        
        try:
            title_selectors = [
                "input[placeholder*='标题']",
                "textarea[placeholder*='标题']",
                "input[maxlength*='30']",
            ]
            
            title_input = None
            for selector in title_selectors:
                try:
                    title_input = self.page.query_selector(selector)
                    if title_input and title_input.is_visible():
                        logger.info(f"找到标题输入框: {selector}")
                        break
                except:
                    pass
            
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
                return True
            else:
                logger.warning("⚠️ 未找到标题输入框")
                return False
                
        except Exception as e:
            logger.error(f"❌ 填写标题失败: {e}")
            return False
    
    def _fill_description(self, description: str) -> bool:
        """填写视频描述"""
        logger.info(f"填写描述: {description[:30]}...")
        
        try:
            desc_selectors = [
                "textarea[placeholder*='描述']",
                "textarea[placeholder*='说点什么']",
            ]
            
            desc_input = None
            for selector in desc_selectors:
                try:
                    desc_input = self.page.query_selector(selector)
                    if desc_input and desc_input.is_visible():
                        logger.info(f"找到描述输入框: {selector}")
                        break
                except:
                    pass
            
            if desc_input:
                desc_input.click()
                time.sleep(0.3)
                desc_input.fill(description)
                time.sleep(0.3)
                logger.info("✅ 描述填写完成")
                return True
            else:
                logger.warning("⚠️ 未找到描述输入框")
                return False
                
        except Exception as e:
            logger.error(f"❌ 填写描述失败: {e}")
            return False
    
    def _add_topics(self, topics: list) -> bool:
        """添加话题标签"""
        if not topics:
            return True
        
        logger.info(f"添加话题: {topics}")
        
        try:
            topic_selectors = [
                "input[placeholder*='话题']",
                ".topic-input",
            ]
            
            topic_input = None
            for selector in topic_selectors:
                try:
                    topic_input = self.page.query_selector(selector)
                    if topic_input and topic_input.is_visible():
                        logger.info(f"找到话题输入框: {selector}")
                        break
                except:
                    pass
            
            if topic_input:
                for topic in topics:
                    topic_input.fill(topic)
                    time.sleep(0.3)
                    topic_input.press("Enter")
                    time.sleep(0.3)
                logger.info("✅ 话题添加完成")
                return True
            else:
                logger.warning("⚠️ 未找到话题输入框")
                return False
                
        except Exception as e:
            logger.error(f"❌ 添加话题失败: {e}")
            return False
    
    def _click_publish(self) -> bool:
        """点击发布按钮"""
        logger.info("点击发布按钮...")
        
        try:
            publish_selectors = [
                "button:has-text('发布')",
                "button:has-text('确认')",
                "[class*='publish'] button",
                ".publish-btn",
            ]
            
            publish_button = None
            for selector in publish_selectors:
                try:
                    publish_button = self.page.query_selector(selector)
                    if publish_button and publish_button.is_visible() and publish_button.is_enabled():
                        logger.info(f"找到发布按钮: {selector}")
                        break
                except:
                    pass
            
            if publish_button:
                publish_button.scroll_into_view_if_needed()
                time.sleep(0.5)
                publish_button.click()
                logger.info("✅ 已点击发布按钮")
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
                success_selectors = [
                    "text=发布成功",
                    "text=已发布",
                    "[class*='success']",
                ]
                
                for selector in success_selectors:
                    try:
                        success_element = self.page.query_selector(selector)
                        if success_element and success_element.is_visible():
                            logger.info("✅ 视频发布成功")
                            return
                    except:
                        pass
                
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
        topics: Optional[list] = None,
        check_cookie: bool = True
    ) -> Dict[str, Any]:
        """
        上传视频的完整流程
        """
        result = {
            "success": False,
            "video_path": str(video_path),
            "title": title,
            "error": None,
        }
        
        try:
            # 初始化浏览器
            self._init_browser()
            
            # 设置 Cookie
            if not self._set_cookies():
                raise Exception("Cookie 设置失败")
            
            # 检查登录状态
            if check_cookie and not self._check_login_status():
                raise Exception("Cookie 已过期或无效，请重新获取")
            
            # 访问上传页面
            logger.info("访问上传页面...")
            self.page.goto(self.UPLOAD_URL, wait_until="networkidle", timeout=60000)
            time.sleep(3)
            
            if "login" in self.page.url.lower():
                raise Exception("Cookie 已过期，需要重新登录")
            
            # 1. 上传视频
            if not self._upload_video(video_path):
                raise Exception("视频上传失败")
            
            # 2. 填写标题
            if title:
                self._fill_title(title)
            
            # 3. 填写描述
            if description:
                self._fill_description(description)
            
            # 4. 添加话题
            if topics:
                self._add_topics(topics)
            
            # 5. 点击发布
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
    
    parser = argparse.ArgumentParser(description="抖音视频上传工具")
    parser.add_argument("--video", "-v", type=str, help="视频文件路径")
    parser.add_argument("--dir", "-d", type=str, help="视频目录路径")
    parser.add_argument("--count", "-c", type=int, default=1, help="上传数量")
    parser.add_argument("--title", "-t", type=str, default="AI 生成的火影忍者视频", help="视频标题")
    parser.add_argument("--description", type=str, help="视频描述")
    parser.add_argument("--topics", type=str, default="#火影忍者,#动漫,#AI视频", help="话题标签")
    
    args = parser.parse_args()
    
    try:
        uploader = DouyinUploaderPlaywright()
        
        kwargs = {
            "title": args.title,
            "description": args.description,
            "topics": [t.strip() for t in args.topics.split(",")] if args.topics else None,
        }
        
        if args.video:
            video_path = Path(args.video)
            if not video_path.exists():
                print(f"❌ 视频文件不存在: {video_path}")
                sys.exit(1)
            
            result = uploader.upload_video(video_path, **kwargs)
            
            if result["success"]:
                print("✅ 视频上传成功！")
            else:
                print(f"❌ 视频上传失败: {result['error']}")
                
        elif args.dir:
            video_dir = Path(args.dir)
            videos = list(video_dir.glob("*.mp4"))[:args.count]
            
            if not videos:
                print(f"❌ 在 {video_dir} 中未找到视频文件")
                sys.exit(1)
            
            for i, video_path in enumerate(videos, 1):
                print(f"\n上传第 {i}/{len(videos)} 个: {video_path.name}")
                result = uploader.upload_video(video_path, **kwargs)
                
                if result["success"]:
                    print("✅ 成功")
                else:
                    print(f"❌ 失败: {result['error']}")
                
                if i < len(videos):
                    time.sleep(30)
            
            print(f"\n🎉 完成: 成功 {sum(1 for v in videos if Path(v).exists())}/{len(videos)}")
        else:
            # 默认从配置目录
            videos = list(VIDEO_DIR.glob("*.mp4"))
            if not videos:
                print(f"❌ 在 {VIDEO_DIR} 中未找到视频文件")
                sys.exit(1)
            
            result = uploader.upload_video(videos[0], **kwargs)
            
            if result["success"]:
                print("✅ 视频上传成功！")
            else:
                print(f"❌ 视频上传失败: {result['error']}")
                
    except KeyboardInterrupt:
        print("\n👋 用户取消")
    except Exception as e:
        print(f"❌ 出错: {e}")


if __name__ == "__main__":
    main()
