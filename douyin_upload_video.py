#!/usr/bin/env python3
"""
抖音视频上传工具
使用 Playwright 复用 Chrome 配置自动上传视频

使用说明:
  python3 douyin_upload_video.py --video <视频路径>
  python3 douyin_upload_video.py --video <视频路径> --title "视频标题"
  python3 douyin_upload_video.py --dir <视频目录> --count 3
"""

import sys
import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any


class DouyinUploader:
    """抖音视频上传器"""
    
    # 上传页面 URL
    UPLOAD_URL = "https://creator.douyin.com/platform/content/video/upload"
    
    # Chrome 用户数据目录
    CHROME_USER_DATA_TEMPLATE = "/Users/{user}/Library/Application Support/Google/Chrome"
    
    def __init__(self, username: str = None):
        """
        初始化上传器
        
        Args:
            username: macOS 用户名（自动检测如果不提供）
        """
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
        """初始化浏览器"""
        print("\n" + "="*70)
        print("🚀 启动浏览器（复用 Chrome 配置）")
        print("="*70)
        
        try:
            from playwright.sync_api import sync_playwright
            
            # 启动 Playwright
            self.playwright = sync_playwright().start()
            
            print(f"\n📂 配置信息:")
            print(f"   用户数据目录: {self.user_data_dir}")
            print(f"   显示模式: {'无头模式' if headless else '可视化模式'}")
            
            # 使用 launch_persistent_context 复用 Chrome 配置
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=headless,
                timeout=60000,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
                ignore_https_errors=True,
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
    
    def _check_login_status(self) -> bool:
        """检查登录状态"""
        print("\n🔍 检查登录状态...")
        
        try:
            # 访问创作者中心
            self.page.goto("https://creator.douyin.com/creator-micro/home", wait_until="domcontentloaded")
            time.sleep(2)
            
            page_content = self.page.content()
            page_url = self.page.url
            
            # 检查是否跳转到了登录页
            if "login" in page_url.lower():
                print("❌ 未登录，需要先登录抖音")
                return False
            
            # 检查登录特征
            login_indicators = ["我的订单", "创作者中心", "消息"]
            found = [i for i in login_indicators if i in page_content]
            
            if found:
                print(f"✅ 已登录（特征: {', '.join(found)}）")
                return True
            else:
                print("⚠️ 未检测到登录特征，但继续尝试")
                return True  # 继续尝试
                
        except Exception as e:
            print(f"⚠️ 检查登录状态失败: {e}")
            return True  # 继续尝试
    
    def _upload_video(self, video_path: Path) -> bool:
        """
        上传视频文件
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            是否上传成功
        """
        print(f"\n📤 开始上传视频: {video_path.name}")
        print(f"   文件大小: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        try:
            # 访问上传页面
            print("\n🌐 访问上传页面...")
            self.page.goto(self.UPLOAD_URL, wait_until="domcontentloaded")
            time.sleep(3)
            
            # 等待页面上传区域加载
            print("⏳ 等待上传区域加载...")
            time.sleep(5)
            
            # 查找文件上传 input
            print("🔍 查找上传元素...")
            
            file_input = None
            
            # 方法1：直接查找文件上传 input
            try:
                file_input = self.page.query_selector("input[type='file']")
                if file_input:
                    print("✅ 找到文件上传 input")
            except:
                pass
            
            # 方法2：如果没找到，尝试点击上传区域
            if not file_input:
                print("⚠️ 未找到文件 input，尝试查找上传区域...")
                
                # 查找可能的上传按钮或区域
                upload_selectors = [
                    "[class*='upload']",
                    ".upload-area",
                    "[class*='drop']",
                    "text=上传视频",
                    "text=点击上传",
                ]
                
                for selector in upload_selectors:
                    try:
                        elements = self.page.query_selector_all(selector)
                        if elements:
                            print(f"   发现元素: {selector}")
                            # 尝试点击第一个可见的元素
                            for elem in elements:
                                if elem.is_visible():
                                    elem.click()
                                    time.sleep(2)
                                    # 点击后再次查找文件 input
                                    file_input = self.page.query_selector("input[type='file']")
                                    if file_input:
                                        print("✅ 点击后找到文件上传 input")
                                        break
                                    break
                        if file_input:
                            break
                    except:
                        pass
            
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
            upload_success = self._wait_for_upload_complete(timeout=300)
            
            if upload_success:
                print("✅ 视频上传完成")
            else:
                print("⚠️ 未检测到上传完成，但继续尝试")
            
            return True
            
        except Exception as e:
            print(f"❌ 上传失败: {e}")
            import traceback
            traceback.print_exc()
            self._save_screenshot("upload_error.png")
            return False
    
    def _wait_for_upload_complete(self, timeout: int = 300) -> bool:
        """
        等待上传完成
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            是否检测到上传完成
        """
        print(f"等待上传完成（超时: {timeout}秒）...")
        
        start_time = time.time()
        last_progress = -1
        
        while time.time() - start_time < timeout:
            try:
                # 获取页面内容
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
                    # 取最后一个进度
                    percent = int(progress_matches[-1])
                    if percent != last_progress and percent <= 100:
                        print(f"📊 上传进度: {percent}%")
                        last_progress = percent
                        
                    if percent >= 100:
                        print("✅ 上传进度达到 100%")
                        time.sleep(2)  # 等待后处理
                        return True
                
                # 查找进度条元素
                try:
                    progress_bar = self.page.query_selector("[class*='progress']")
                    if progress_bar and progress_bar.is_visible():
                        progress_text = progress_bar.inner_text()
                        if progress_text:
                            print(f"📊 进度: {progress_text}")
                except:
                    pass
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ 检查进度时出错: {e}")
                time.sleep(2)
        
        print(f"⚠️ 等待上传超时（{timeout}秒）")
        return False
    
    def _fill_form(self, title: str, description: str = None, topics: List[str] = None):
        """
        填写表单（标题、描述、话题）
        
        Args:
            title: 视频标题
            description: 视频描述
            topics: 话题列表
        """
        print(f"\n📝 填写表单...")
        
        time.sleep(3)  # 等待上传后的页面加载
        
        # 1. 填写标题
        if title:
            print(f"   填写标题: {title}")
            try:
                # 查找标题输入框
                title_selectors = [
                    "input[placeholder*='标题']",
                    "textarea[placeholder*='标题']",
                    "[class*='title'] input",
                    "[class*='title'] textarea",
                ]
                
                title_input = None
                for selector in title_selectors:
                    try:
                        elem = self.page.query_selector(selector)
                        if elem and elem.is_visible():
                            title_input = elem
                            print(f"✅ 找到标题输入框: {selector}")
                            break
                    except:
                        pass
                
                if title_input:
                    # 清空并填写
                    title_input.click()
                    time.sleep(0.5)
                    title_input.press("Control+a")
                    time.sleep(0.2)
                    title_input.press("Backspace")
                    time.sleep(0.2)
                    title_input.fill(title)
                    time.sleep(0.5)
                    print("✅ 标题填写完成")
                else:
                    print("⚠️ 未找到标题输入框")
                    
            except Exception as e:
                print(f"⚠️ 填写标题失败: {e}")
        
        # 2. 填写描述
        if description:
            print(f"   填写描述: {description[:30]}...")
            try:
                desc_selectors = [
                    "textarea[placeholder*='描述']",
                    "textarea[placeholder*='说点什么']",
                    "[class*='description'] textarea",
                ]
                
                desc_input = None
                for selector in desc_selectors:
                    try:
                        elem = self.page.query_selector(selector)
                        if elem and elem.is_visible():
                            desc_input = elem
                            print(f"✅ 找到描述输入框: {selector}")
                            break
                    except:
                        pass
                
                if desc_input:
                    desc_input.click()
                    time.sleep(0.5)
                    desc_input.fill(description)
                    time.sleep(0.5)
                    print("✅ 描述填写完成")
                else:
                    print("⚠️ 未找到描述输入框")
                    
            except Exception as e:
                print(f"⚠️ 填写描述失败: {e}")
        
        # 3. 添加话题
        if topics:
            print(f"   添加话题: {topics}")
            try:
                topic_selectors = [
                    "input[placeholder*='话题']",
                    "[class*='topic'] input",
                ]
                
                topic_input = None
                for selector in topic_selectors:
                    try:
                        elem = self.page.query_selector(selector)
                        if elem and elem.is_visible():
                            topic_input = elem
                            print(f"✅ 找到话题输入框: {selector}")
                            break
                    except:
                        pass
                
                if topic_input:
                    for topic in topics:
                        topic_input.fill(topic)
                        time.sleep(0.5)
                        topic_input.press("Enter")
                        time.sleep(0.5)
                    print("✅ 话题添加完成")
                else:
                    print("⚠️ 未找到话题输入框")
                    
            except Exception as e:
                print(f"⚠️ 添加话题失败: {e}")
    
    def _click_publish(self) -> bool:
        """
        点击发布按钮
        
        Returns:
            是否点击成功
        """
        print("\n🚀 点击发布按钮...")
        
        try:
            # 查找发布按钮
            publish_selectors = [
                "button:has-text('发布')",
                "button:has-text('确认')",
                "[class*='publish'] button",
                ".publish-btn",
                "button[type='submit']",
            ]
            
            publish_button = None
            for selector in publish_selectors:
                try:
                    elem = self.page.query_selector(selector)
                    if elem and elem.is_visible() and elem.is_enabled():
                        publish_button = elem
                        print(f"✅ 找到发布按钮: {selector}")
                        break
                except:
                    pass
            
            if publish_button:
                # 滚动到可见
                publish_button.scroll_into_view_if_needed()
                time.sleep(1)
                
                # 点击
                publish_button.click()
                print("✅ 已点击发布按钮")
                
                # 等待发布
                self._wait_for_publish_complete()
                
                return True
            else:
                print("❌ 未找到发布按钮")
                self._save_screenshot("publish_error.png")
                return False
                
        except Exception as e:
            print(f"❌ 点击发布按钮失败: {e}")
            self._save_screenshot("publish_error.png")
            return False
    
    def _wait_for_publish_complete(self, timeout: int = 60):
        """
        等待发布完成
        
        Args:
            timeout: 超时时间（秒）
        """
        print(f"等待发布完成（超时: {timeout}秒）...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                page_content = self.page.content()
                
                # 检查发布成功提示
                success_indicators = ["发布成功", "已发布", "success", "完成"]
                for indicator in success_indicators:
                    if indicator in page_content:
                        print(f"✅ 发布成功: {indicator}")
                        return
                
                # 检查是否跳转到新页面
                if "video" in self.page.url.lower() or "detail" in self.page.url.lower():
                    print(f"✅ 已跳转到视频详情页")
                    return
                
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ 检查发布状态时出错: {e}")
                time.sleep(1)
        
        print(f"⚠️ 等待发布超时，但可能发布中")
    
    def _save_screenshot(self, filename: str):
        """保存页面截图（用于调试）"""
        try:
            screenshot_path = f"debug_{filename}"
            self.page.screenshot(path=screenshot_path)
            print(f"📸 截图已保存: {screenshot_path}")
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
        """
        上传单个视频的完整流程
        
        Args:
            video_path: 视频文件路径
            title: 视频标题
            description: 视频描述（可选）
            topics: 话题标签列表（可选）
            headless: 是否使用无头模式
            
        Returns:
            上传结果字典
        """
        result = {
            "success": False,
            "video_path": str(video_path),
            "title": title,
            "error": None,
            "message": "",
        }
        
        try:
            # 验证视频文件
            if not video_path.exists():
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            # 检查文件格式
            video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
            if video_path.suffix.lower() not in video_extensions:
                print(f"⚠️ 警告: 视频格式 {video_path.suffix} 可能不被支持")
            
            # 初始化浏览器
            if not self._init_browser(headless=headless):
                raise Exception("浏览器启动失败")
            
            # 检查登录状态
            if not self._check_login_status():
                raise Exception("未登录抖音，请先登录")
            
            # 1. 上传视频
            if not self._upload_video(video_path):
                raise Exception("视频上传失败")
            
            # 2. 填写表单
            self._fill_form(title, description, topics)
            
            # 3. 点击发布
            if not self._click_publish():
                raise Exception("点击发布失败")
            
            # 成功
            result["success"] = True
            result["message"] = "视频上传并发布成功"
            
            print("\n" + "="*70)
            print("🎉 视频上传成功！")
            print("="*70)
            print(f"📹 视频: {video_path.name}")
            print(f"📝 标题: {title}")
            if topics:
                print(f"🏷️ 话题: {', '.join(topics)}")
            print(f"🔗 页面: {self.page.url}")
            
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
    
    def batch_upload(
        self,
        video_dir: Path,
        count: int = 1,
        title_template: str = "AI 生成的火影忍者视频 #{num}",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        批量上传视频
        
        Args:
            video_dir: 视频目录
            count: 上传数量
            title_template: 标题模板，{num} 会被替换为序号
            **kwargs: 其他参数
            
        Returns:
            上传结果列表
        """
        # 查找视频文件
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        videos = []
        
        for ext in video_extensions:
            videos.extend(video_dir.glob(f"*{ext}"))
            videos.extend(video_dir.glob(f"**/*{ext}"))
        
        # 去重并限制数量
        videos = list(set(videos))[:count]
        
        if not videos:
            raise FileNotFoundError(f"在 {video_dir} 中未找到视频文件")
        
        print(f"\n📁 找到 {len(videos)} 个视频，将上传 {len(videos)} 个")
        
        results = []
        for i, video_path in enumerate(videos, 1):
            print(f"\n{'='*70}")
            print(f"📤 上传第 {i}/{len(videos)} 个视频: {video_path.name}")
            print(f"{'='*70}")
            
            # 生成标题
            title = title_template.format(num=i)
            
            result = self.upload_video(
                video_path=video_path,
                title=title,
                **kwargs
            )
            
            results.append(result)
            
            # 上传间隔（避免被限流）
            if i < len(videos):
                print(f"\n⏳ 等待 30 秒后上传下一个视频...")
                time.sleep(30)
        
        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        
        print(f"\n" + "="*70)
        print("📊 批量上传完成")
        print("="*70)
        print(f"总数量: {len(videos)}")
        print(f"成功: {success_count}")
        print(f"失败: {len(videos) - success_count}")
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="抖音视频上传工具 - 使用 Playwright 复用 Chrome 配置",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 上传单个视频
  python3 douyin_upload_video.py --video data/videos/test.mp4 --title "我的视频"
  
  # 上传并指定描述和话题
  python3 douyin_upload_video.py \
      --video data/videos/test.mp4 \
      --title "火影忍者 AI 视频" \
      --description "这是一个测试视频" \
      --topics "#火影忍者,#动漫,#AI"
  
  # 批量上传
  python3 douyin_upload_video.py --dir data/videos --count 3 --headless
  
  # 使用无头模式
  python3 douyin_upload_video.py --video data/videos/test.mp4 --headless

注意事项:
  1. 确保 Chrome 已登录抖音
  2. 运行前关闭所有 Chrome 窗口
  3. 视频文件大小建议小于 500MB
  4. 建议每次上传间隔 30 秒以上
        """
    )
    
    # 必需参数（视频或目录）
    parser.add_argument("--video", "-v", type=str, help="视频文件路径")
    parser.add_argument("--dir", "-d", type=str, help="视频目录路径（批量上传）")
    
    # 可选参数
    parser.add_argument("--count", "-c", type=int, default=1, help="上传数量（批量上传时使用）")
    parser.add_argument("--title", "-t", type=str, default="AI 生成的火影忍者视频", help="视频标题")
    parser.add_argument("--description", type=str, help="视频描述")
    parser.add_argument("--topics", type=str, help="话题标签（逗号分隔），如 '#火影忍者,#动漫'")
    parser.add_argument("--username", "-u", type=str, help="macOS 用户名（默认自动检测）")
    parser.add_argument("--headless", action="store_true", help="使用无头模式（不显示浏览器）")
    
    args = parser.parse_args()
    
    # 验证参数
    if not args.video and not args.dir:
        print("❌ 错误: 请指定 --video 或 --dir 参数")
        print("\n使用示例:")
        print("  python3 douyin_upload_video.py --video data/videos/test.mp4")
        print("  python3 douyin_upload_video.py --dir data/videos --count 3")
        sys.exit(1)
    
    # 创建上传器
    try:
        uploader = DouyinUploader(username=args.username)
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        print("\n请确保:")
        print("  1. Google Chrome 已安装")
        print("  2. Chrome 用户数据目录存在")
        print("  3. 用户名正确")
        sys.exit(1)
    
    # 解析话题
    topics = None
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    
    try:
        if args.video:
            # 单个视频上传
            video_path = Path(args.video)
            result = uploader.upload_video(
                video_path=video_path,
                title=args.title,
                description=args.description,
                topics=topics,
                headless=args.headless
            )
            
            if result["success"]:
                print("\n✅ 视频上传成功！")
                sys.exit(0)
            else:
                print(f"\n❌ 视频上传失败: {result['error']}")
                sys.exit(1)
                
        elif args.dir:
            # 批量上传
            video_dir = Path(args.dir)
            results = uploader.batch_upload(
                video_dir=video_dir,
                count=args.count,
                title_template=args.title + " #{num}",
                description=args.description,
                topics=topics,
                headless=args.headless
            )
            
            # 统计
            success_count = sum(1 for r in results if r["success"])
            
            if success_count == len(results):
                print("\n✅ 所有视频上传成功！")
                sys.exit(0)
            else:
                print(f"\n⚠️ 部分视频上传失败: {len(results) - success_count}/{len(results)}")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 用户取消上传")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
