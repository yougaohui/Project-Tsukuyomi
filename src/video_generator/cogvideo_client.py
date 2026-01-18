"""
CogVideoX-3 视频生成客户端 - 使用智谱AI官方SDK
"""
import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from zhipuai import ZhipuAI

from src.config.settings import (
    COGVIDEO_API_KEY,
    COGVIDEO_MODEL,
    COGVIDEO_DEFAULT_QUALITY,
    COGVIDEO_DEFAULT_SIZE,
    COGVIDEO_DEFAULT_FPS,
    COGVIDEO_WITH_AUDIO,
    COGVIDEO_GENERATION_TIMEOUT,
    COGVIDEO_RETRIEVE_TIMEOUT,
    COGVIDEO_MAX_RETRIES,
    VIDEO_DIR
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CogVideoClient:
    """CogVideoX-3 API 客户端 - 使用官方SDK"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or COGVIDEO_API_KEY

        if not self.api_key:
            raise ValueError("COGVIDEO_API_KEY is required")

        # 初始化智谱AI客户端
        self.client = ZhipuAI(api_key=self.api_key)
        logger.info("Initialized ZhipuAI client successfully")

    def generate_video(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        quality: str = COGVIDEO_DEFAULT_QUALITY,
        size: str = COGVIDEO_DEFAULT_SIZE,
        fps: int = COGVIDEO_DEFAULT_FPS,
        with_audio: bool = COGVIDEO_WITH_AUDIO
    ) -> Dict[str, Any]:
        """
        生成视频

        Args:
            prompt: 文本提示词
            image_url: 图片URL（图生视频）
            quality: 质量模式 (quality/speed)
            size: 视频分辨率 (1920x1080, 3840x2160)
            fps: 帧率 (30/60)
            with_audio: 是否包含音频

        Returns:
            生成任务的响应数据
        """
        logger.info(f"Starting video generation with prompt: {prompt[:100]}...")

        try:
            # 使用 SDK 提交视频生成任务
            response = self.client.videos.generations(
                model=COGVIDEO_MODEL,
                prompt=prompt,
                image_url=image_url,
                quality=quality,
                size=size,
                fps=fps,
                with_audio=with_audio
            )

            logger.info(f"Video generation started, task ID: {response.id}")

            return {
                "id": response.id,
                "status": "processing"
            }

        except Exception as e:
            logger.error(f"Failed to start video generation: {str(e)}")
            raise RuntimeError(f"Failed to generate video: {str(e)}")

    def get_video_result(self, task_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """
        获取视频生成结果（轮询）

        Args:
            task_id: 生成任务ID
            max_wait: 最大等待时间（秒）

        Returns:
            生成结果数据
        """
        logger.info(f"Checking video result for task {task_id}")

        start_time = time.time()
        poll_interval = 5  # 每5秒检查一次

        while time.time() - start_time < max_wait:
            try:
                result = self.client.videos.retrieve_videos_result(id=task_id)

                status = result.task_status
                logger.info(f"Video generation status: {status}")

                if status == "SUCCESS":
                    logger.info(f"Video generation completed for task {task_id}")

                    # 获取视频URL
                    video_url = result.video_result[0].url
                    cover_url = result.video_result[0].cover_image_url

                    return {
                        "status": "succeeded",
                        "output": {
                            "video_url": video_url,
                            "cover_image_url": cover_url
                        }
                    }

                elif status == "FAIL":
                    error_msg = str(result)
                    logger.error(f"Video generation failed: {error_msg}")
                    raise RuntimeError(f"Video generation failed: {error_msg}")

                elif status == "PROCESSING":
                    logger.info("Video is still processing, waiting...")
                    time.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error checking result: {str(e)}")
                time.sleep(poll_interval)

        raise TimeoutError(f"Video generation timed out after {max_wait} seconds")

    def generate_video_and_download(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        quality: str = COGVIDEO_DEFAULT_QUALITY,
        size: str = COGVIDEO_DEFAULT_SIZE,
        fps: int = COGVIDEO_DEFAULT_FPS,
        with_audio: bool = COGVIDEO_WITH_AUDIO,
        output_dir: Optional[Path] = None,
        filename: Optional[str] = None
    ) -> Path:
        """
        生成视频并下载到本地

        Args:
            prompt: 文本提示词
            image_url: 图片URL
            quality: 质量模式
            size: 视频分辨率
            fps: 帧率
            with_audio: 是否包含音频
            output_dir: 输出目录
            filename: 输出文件名

        Returns:
            下载的视频文件路径
        """
        if output_dir is None:
            output_dir = VIDEO_DIR

        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = int(time.time())
            filename = f"video_{timestamp}.mp4"

        output_path = output_dir / filename

        logger.info(f"Generating video to {output_path}")

        # 提交生成任务
        task = self.generate_video(
            prompt=prompt,
            image_url=image_url,
            quality=quality,
            size=size,
            fps=fps,
            with_audio=with_audio
        )

        task_id = task.get("id")
        if not task_id:
            raise ValueError("No task ID in response")

        # 轮询等待生成完成
        result = self.get_video_result(task_id)

        video_url = result.get("output", {}).get("video_url")
        if not video_url:
            raise ValueError("No video URL in response")

        # 下载视频
        logger.info(f"Downloading video from {video_url}")

        import requests
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Video downloaded successfully to {output_path}")
        return output_path

    def generate_multiple_videos(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[Path]:
        """
        批量生成多个视频

        Args:
            prompts: 提示词列表
            **kwargs: 其他参数

        Returns:
            生成的视频文件路径列表
        """
        video_paths = []

        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"Generating video {i + 1}/{len(prompts)}")

                video_path = self.generate_video_and_download(
                    prompt=prompt,
                    **kwargs
                )

                video_paths.append(video_path)

            except Exception as e:
                logger.error(f"Failed to generate video {i + 1}: {str(e)}")
                continue

        return video_paths
