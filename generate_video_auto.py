#!/usr/bin/env python3
"""
完全自动化的视频生成脚本 - 无需任何用户交互
专为 OpenCode 和 CI/CD 环境设计
"""
import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# 项目根目录
BASE_DIR = Path(__file__).parent


class AutoConfig:
    """自动化配置管理"""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.data_dir = BASE_DIR / "data" / "videos"
        self.output_dir = BASE_DIR / "data" / "processed"
        self.logs_dir = BASE_DIR / "logs"
        
        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_api_key(self) -> str:
        """获取 API Key - 多种来源"""
        # 1. 环境变量
        api_key = os.getenv("COGVIDEO_API_KEY")
        if api_key:
            return api_key
        
        # 2. .env 文件
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("COGVIDEO_API_KEY="):
                        return line.split("=", 1)[1].strip()
        
        raise ValueError(
            "未找到 API Key。请设置环境变量 COGVIDEO_API_KEY "
            "或在 .env 文件中配置 COGVIDEO_API_KEY=your-key"
        )
    
    def get_default_prompts(self) -> List[str]:
        """获取默认的火影忍者 Prompts"""
        return [
            "Naruto Uzumaki using Rasengan, dynamic anime style, epic battle scene with blue chakra energy",
            "Sasuke Uchiha using Chidori, lightning effects, intense battle scene with sharingan activated",
            "Team 7 fighting together, coordinated attacks, dynamic action anime style",
            "Konohagakure village at sunset, peaceful anime landscape with warm colors",
            "Hatake Kakashi reading Icha Icha Paradise, serene forest background",
            "Sakura Haruno using Cherry Blossom Impact, beautiful pink flower petals",
            "Itachi Uchiha using Amaterasu, black flames, mysterious atmosphere",
            "Jiraiya using Sage Mode, gathering natural energy, mountain landscape"
        ]
    
    def get_output_filename(self, prompt: str, index: int) -> str:
        """生成输出文件名"""
        # 从 prompt 提取关键词
        words = prompt.split()[:5]
        keywords = "_".join([w.lower().replace(",", "") for w in words])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"video_{timestamp}_{index}_{keywords[:50]}.mp4"


class VideoGenerator:
    """自动化视频生成器"""
    
    def __init__(self, config: AutoConfig):
        self.config = config
        self.base_url = "https://api.z.ai/v1/videos"
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        self.log_file = self.config.logs_dir / f"generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def _log(self, message: str):
        """日志记录"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        print(message)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    
    def generate_video(self, prompt: str, index: int) -> Optional[str]:
        """生成单个视频"""
        self._log(f"\n{'='*60}")
        self._log(f"开始生成视频 {index + 1}")
        self._log(f"{'='*60}")
        self._log(f"Prompt: {prompt[:100]}...")
        
        payload = {
            "model": "cogvideox-3",
            "prompt": prompt,
            "quality": "quality",
            "size": "1920x1080",
            "fps": 30,
            "with_audio": True
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                self._log(f"❌ API 请求失败：HTTP {response.status_code}")
                self._log(f"   响应：{response.text[:200]}")
                return None
            
            data = response.json()
            task_id = data.get("id")
            
            self._log(f"✅ 任务创建成功")
            self._log(f"   Task ID: {task_id}")
            self._log(f"   Status: {data.get('status', 'unknown')}")
            
            return task_id
            
        except Exception as e:
            self._log(f"❌ 生成失败：{str(e)}")
            return None
    
    def check_result(self, task_id: str, max_wait: int = 300) -> Optional[str]:
        """检查生成结果"""
        url = f"{self.base_url}/{task_id}"
        waited = 0
        check_interval = 15
        
        while waited < max_wait:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    self._log(f"❌ 查询失败：HTTP {response.status_code}")
                    return None
                
                data = response.json()
                status = data.get("status", "unknown")
                
                if status == "succeeded":
                    output = data.get("output", {})
                    video_url = output.get("video_url")
                    self._log(f"✅ 生成成功")
                    self._log(f"   视频 URL: {video_url}")
                    return video_url
                
                elif status == "failed":
                    error = data.get("error", "未知错误")
                    self._log(f"❌ 生成失败：{error}")
                    return None
                
                elif status == "processing":
                    self._log(f"[{waited}s] 状态: {status} - 等待中...")
                    time.sleep(check_interval)
                    waited += check_interval
                else:
                    self._log(f"[{waited}s] 未知状态: {status}")
                    time.sleep(check_interval)
                    waited += check_interval
                    
            except Exception as e:
                self._log(f"❌ 查询失败：{str(e)}")
                time.sleep(check_interval)
                waited += check_interval
        
        self._log(f"⏰ 超时：已等待 {max_wait} 秒")
        return None
    
    def download_video(self, video_url: str, output_path: Path) -> bool:
        """下载视频"""
        self._log(f"\n下载视频到：{output_path}")
        
        try:
            response = requests.get(video_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 显示进度
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self._log(f"   下载进度: {progress:.1f}%")
            
            self._log(f"✅ 下载完成")
            return True
            
        except Exception as e:
            self._log(f"❌ 下载失败：{str(e)}")
            return False
    
    def generate_batch(
        self, 
        count: int, 
        prompts: Optional[List[str]] = None,
        download: bool = True
    ) -> List[str]:
        """批量生成视频"""
        self._log(f"\n{'#'*60}")
        self._log(f"开始批量生成 {count} 个视频")
        self._log(f"{'#'*60}")
        
        if prompts is None:
            prompts = self.config.get_default_prompts()
        
        generated_files = []
        
        for i in range(min(count, len(prompts))):
            prompt = prompts[i]
            
            # 生成视频
            task_id = self.generate_video(prompt, i)
            if not task_id:
                continue
            
            # 检查结果
            video_url = self.check_result(task_id)
            if not video_url:
                continue
            
            # 下载视频
            if download:
                output_filename = self.config.get_output_filename(prompt, i)
                output_path = self.config.output_dir / output_filename
                
                if self.download_video(video_url, output_path):
                    generated_files.append(str(output_path))
            else:
                generated_files.append(video_url)
        
        self._log(f"\n{'#'*60}")
        self._log(f"批量生成完成")
        self._log(f"成功生成: {len(generated_files)}/{count} 个视频")
        self._log(f"{'#'*60}\n")
        
        return generated_files


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="自动化视频生成脚本 - 完全无交互",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=1,
        help='生成视频数量'
    )
    
    parser.add_argument(
        '--prompt', '-p',
        type=str,
        default=None,
        help='自定义 Prompt（覆盖默认 Prompts）'
    )
    
    parser.add_argument(
        '--no-download',
        action='store_true',
        help='不下载视频，只返回 URL'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=None,
        help='输出目录（默认：data/processed）'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='静默模式（只输出错误）'
    )
    
    args = parser.parse_args()
    
    # 初始化配置
    try:
        config = AutoConfig()
        
        if args.output_dir:
            config.output_dir = args.output_dir
            config.output_dir.mkdir(parents=True, exist_ok=True)
    
    except ValueError as e:
        print(f"❌ 配置错误：{e}", file=sys.stderr)
        sys.exit(1)
    
    # 初始化生成器
    generator = VideoGenerator(config)
    
    # 准备 Prompts
    if args.prompt:
        prompts = [args.prompt]
    else:
        prompts = config.get_default_prompts()
    
    # 生成视频
    generated_files = generator.generate_batch(
        count=args.count,
        prompts=prompts,
        download=not args.no_download
    )
    
    # 输出结果
    if not args.quiet:
        print(f"\n{'='*60}")
        print(f"✅ 自动化生成完成")
        print(f"{'='*60}")
        print(f"\n生成的视频文件：")
        for i, file_path in enumerate(generated_files, 1):
            print(f"  {i}. {file_path}")
        print(f"\n日志文件：{generator.log_file}")
    
    # 返回状态码
    sys.exit(0 if generated_files else 1)


if __name__ == "__main__":
    main()
