"""
平台上传Agent

负责将视频上传到各个平台（抖音、快手、小红书等）
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio

from src.agents.base_agent import BaseAgent, Task
from src.uploader.douyin_client import DouyinUploader
from src.config.settings import UPLOADED_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PlatformUploaderAgent(BaseAgent):
    """
    平台上传Agent

    负责将视频上传到各个平台
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("platform_uploader", config)

        self.douyin_uploader = DouyinUploader()
        self.supported_platforms = ["douyin"]

        self.max_concurrent_uploads = config.get("max_concurrent", 2) if config else 2
        self.auto_publish = config.get("auto_publish", True) if config else True

        logger.info(
            f"PlatformUploaderAgent initialized "
            f"(platforms: {self.supported_platforms}, "
            f"max_concurrent: {self.max_concurrent_uploads}, "
            f"auto_publish: {self.auto_publish})"
        )

    async def execute(self, task: Task) -> Dict[str, Any]:
        """
        执行上传任务

        Args:
            task: 任务数据，包含：
                - videos: 视频信息列表
                    每个元素包含: path, title, description, topics
                - platforms: 目标平台列表（可选，默认为所有平台）
                - delay: 上传间隔（秒，默认30）

        Returns:
            上传结果列表
        """
        params = task.data
        videos = params.get("videos", [])
        platforms = params.get("platforms", self.supported_platforms)
        delay = params.get("delay", 30)

        if not videos:
            raise ValueError("No videos provided")

        logger.info(f"Uploading {len(videos)} videos to {len(platforms)} platform(s)")

        results = await self._upload_videos(
            videos=videos,
            platforms=platforms,
            delay=delay
        )

        success_count = sum(1 for r in results if r.get("status") == "success")
        logger.info(f"Upload completed: {success_count}/{len(videos) * len(platforms)} successful")

        return {
            "results": results,
            "total": len(videos) * len(platforms),
            "successful": success_count,
            "failed": len(videos) * len(platforms) - success_count
        }

    async def _upload_videos(
        self,
        videos: List[Dict[str, Any]],
        platforms: List[str],
        delay: int
    ) -> List[Dict[str, Any]]:
        """
        上传多个视频

        Args:
            videos: 视频信息列表
            platforms: 平台列表
            delay: 上传间隔

        Returns:
            上传结果列表
        """
        semaphore = asyncio.Semaphore(self.max_concurrent_uploads)
        results = []

        for video_info in videos:
            for platform in platforms:
                result = await self._upload_single_video(
                    video_info=video_info,
                    platform=platform,
                    semaphore=semaphore
                )
                results.append(result)

                if delay > 0:
                    await asyncio.sleep(delay)

        return results

    async def _upload_single_video(
        self,
        video_info: Dict[str, Any],
        platform: str,
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """
        上传单个视频

        Args:
            video_info: 视频信息
            platform: 平台名称
            semaphore: 并发信号量

        Returns:
            上传结果
        """
        async with semaphore:
            video_path = Path(video_info.get("path"))
            title = video_info.get("title", "")
            description = video_info.get("description", title)
            topics = video_info.get("topics", [])

            logger.info(f"Uploading to {platform}: {video_path.name}")

            try:
                if platform == "douyin":
                    result = await asyncio.to_thread(
                        self.douyin_uploader.upload_video,
                        video_path=video_path,
                        title=title,
                        description=description,
                        topics=topics,
                        auto_publish=self.auto_publish
                    )

                    return {
                        "platform": platform,
                        "video_path": str(video_path),
                        "status": "success",
                        "result": result
                    }
                else:
                    return {
                        "platform": platform,
                        "video_path": str(video_path),
                        "status": "error",
                        "error": f"Unsupported platform: {platform}"
                    }

            except Exception as e:
                logger.error(f"Upload to {platform} failed: {str(e)}")
                return {
                    "platform": platform,
                    "video_path": str(video_path),
                    "status": "error",
                    "error": str(e)
                }

    async def upload_single_video(
        self,
        video_path: Path,
        title: str,
        description: Optional[str] = None,
        topics: Optional[List[str]] = None,
        platform: str = "douyin"
    ) -> Dict[str, Any]:
        """
        上传单个视频的便捷方法

        Args:
            video_path: 视频路径
            title: 标题
            description: 描述
            topics: 话题标签
            platform: 平台名称

        Returns:
            上传结果
        """
        task = Task(
            id=self.create_task_id(),
            type="upload_single",
            data={
                "videos": [{
                    "path": str(video_path),
                    "title": title,
                    "description": description or title,
                    "topics": topics or []
                }],
                "platforms": [platform]
            }
        )

        result = await self.execute(task)
        return result["results"][0]

    def generate_title(self, prompt: str, category: Optional[str] = None) -> str:
        """
        根据prompt生成标题

        Args:
            prompt: 提示词
            category: 类别

        Returns:
            标题
        """
        category_prefixes = {
            "character": "【角色】",
            "jutsu": "【忍术】",
            "scene": "【场景】",
            "battle": "【战斗】",
            "emotional": "【情感】"
        }

        prefix = category_prefixes.get(category, "【火影忍者】")

        prompt_clean = prompt.replace(",", " ").replace(".", " ").strip()
        words = prompt_clean.split()

        title_words = words[:8]
        title = " ".join(title_words)

        if len(title) > 30:
            title = title[:30] + "..."

        return f"{prefix} {title}"

    def generate_hashtags(self, category: Optional[str] = None) -> List[str]:
        """
        生成话题标签

        Args:
            category: 类别

        Returns:
            话题标签列表
        """
        base_tags = ["#火影忍者", "#Naruto", "#动漫"]

        category_tags = {
            "character": ["#火影忍者角色", "#动漫角色", "#忍者"],
            "jutsu": ["#火影忍术", "#忍术", "#忍界大战"],
            "scene": ["#火影场景", "#动漫风景", "#木叶村"],
            "battle": ["#火影战斗", "#忍术对决", "#热血动漫"],
            "emotional": ["#火影感动", "#动漫情感", "#羁绊"]
        }

        tags = base_tags.copy()
        if category and category in category_tags:
            tags.extend(category_tags[category])

        return tags

    def get_upload_status(self, video_path: Path) -> Dict[str, Any]:
        """
        获取视频上传状态

        Args:
            video_path: 视频路径

        Returns:
            上传状态
        """
        uploaded_path = UPLOADED_DIR / video_path.name

        return {
            "video_path": str(video_path),
            "is_uploaded": uploaded_path.exists(),
            "uploaded_at": uploaded_path.stat().st_mtime if uploaded_path.exists() else None
        }

    def list_uploaded_videos(self) -> List[Dict[str, Any]]:
        """
        列出所有已上传的视频

        Returns:
            已上传视频列表
        """
        videos = []

        if UPLOADED_DIR.exists():
            for video_file in UPLOADED_DIR.glob("*.mp4"):
                videos.append({
                    "path": str(video_file),
                    "name": video_file.name,
                    "size": video_file.stat().st_size,
                    "uploaded_at": video_file.stat().st_mtime
                })

        return videos
