"""
CogVideoX-3 视频生成客户端
"""
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests

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
    """CogVideoX-3 API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or COGVIDEO_API_KEY

        if not self.api_key:
            raise ValueError("COGVIDEO_API_KEY is required")

        self.base_url = "https://api.z.ai/v1/videos"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_video(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        quality: str = COGVIDEO_DEFAULT_QUALITY,
        size: str = COGVIDEO_DEFAULT_SIZE,
        fps: int = COGVIDEO_DEFAULT_FPS,
        with_audio: bool = COGVIDEO_WITH_AUDIO
    ) -> Dict[str, Any]:
        """
        生成视频

        Args:
            prompt: 文本提示词
            image_url: 单个图片URL（图生视频）
            image_urls: 图片URL列表（首尾帧生成）
            quality: 质量模式 (quality/speed)
            size: 视频分辨率 (1920x1080, 3840x2160)
            fps: 帧率 (30/60)
            with_audio: 是否包含音频

        Returns:
            生成任务的响应数据
        """
        payload = {
            "model": COGVIDEO_MODEL,
            "prompt": prompt,
            "quality": quality,
            "size": size,
            "fps": fps,
            "with_audio": with_audio
        }

        if image_url:
            payload["image_url"] = image_url

        if image_urls:
            payload["image_url"] = image_urls

        logger.info(f"Starting video generation with prompt: {prompt[:100]}...")

        for attempt in range(COGVIDEO_MAX_RETRIES):
            try:
                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=self.headers,
                    timeout=COGVIDEO_GENERATION_TIMEOUT
                )
                response.raise_for_status()

                data = response.json()
                logger.info(f"Video generation started, task ID: {data.get('id')}")
                return data

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{COGVIDEO_MAX_RETRIES}")
                if attempt < COGVIDEO_MAX_RETRIES - 1:
                    time.sleep(5)
                else:
                    raise

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < COGVIDEO_MAX_RETRIES - 1:
                    time.sleep(5)
                else:
                    raise RuntimeError(f"Failed to generate video after {COGVIDEO_MAX_RETRIES} attempts: {str(e)}")

    def get_video_result(self, task_id: str) -> Dict[str, Any]:
        """
        获取视频生成结果

        Args:
            task_id: 生成任务ID

        Returns:
            生成结果数据
        """
        url = f"{self.base_url}/{task_id}"

        logger.info(f"Checking video result for task {task_id}")

        for attempt in range(COGVIDEO_MAX_RETRIES):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=COGVIDEO_RETRIEVE_TIMEOUT
                )
                response.raise_for_status()

                data = response.json()
                status = data.get("status", "unknown")

                logger.info(f"Video generation status: {status}")

                if status == "succeeded":
                    logger.info(f"Video generation completed for task {task_id}")
                    return data
                elif status == "failed":
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"Video generation failed: {error_msg}")
                    raise RuntimeError(f"Video generation failed: {error_msg}")
                elif status == "processing":
                    logger.info("Video is still processing, waiting...")
                    time.sleep(10)
                else:
                    logger.warning(f"Unknown status: {status}")
                    time.sleep(10)

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to check result on attempt {attempt + 1}: {str(e)}")
                if attempt < COGVIDEO_MAX_RETRIES - 1:
                    time.sleep(5)
                else:
                    raise

        raise TimeoutError("Video generation timed out")

    def generate_video_and_download(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
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
            image_url: 单个图片URL
            image_urls: 图片URL列表（首尾帧）
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

        task = self.generate_video(
            prompt=prompt,
            image_url=image_url,
            image_urls=image_urls,
            quality=quality,
            size=size,
            fps=fps,
            with_audio=with_audio
        )

        task_id = task.get("id")
        if not task_id:
            raise ValueError("No task ID in response")

        result = self.get_video_result(task_id)

        video_url = result.get("output", {}).get("video_url")
        if not video_url:
            raise ValueError("No video URL in response")

        logger.info(f"Downloading video from {video_url}")

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
