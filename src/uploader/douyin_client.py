"""
抖音视频上传客户端
"""
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import requests

from src.config.settings import (
    DOUYIN_API_BASE,
    DOUYIN_VIDEO_MAX_SIZE,
    DOUYIN_VIDEO_MAX_DURATION,
    DOUYIN_VIDEO_MIN_DURATION,
    UPLOADED_DIR
)
from src.uploader.auth import DouyinAuth
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DouyinUploader:
    """抖音视频上传器"""

    def __init__(self, auth: DouyinAuth = None):
        if auth is None:
            auth = DouyinAuth()

        self.auth = auth
        self.session = auth.session
        self.base_url = DOUYIN_API_BASE

    def _get_file_md5(self, file_path: Path) -> str:
        """
        计算文件 MD5

        Args:
            file_path: 文件路径

        Returns:
            MD5 字符串
        """
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def _validate_video(self, video_path: Path) -> bool:
        """
        验证视频是否符合要求

        Args:
            video_path: 视频路径

        Returns:
            是否符合要求
        """
        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            return False

        file_size = video_path.stat().st_size
        if file_size > DOUYIN_VIDEO_MAX_SIZE:
            logger.error(f"Video too large: {file_size} > {DOUYIN_VIDEO_MAX_SIZE}")
            return False

        try:
            import moviepy.editor as mp
            video = mp.VideoFileClip(str(video_path))
            duration = video.duration
            video.close()

            if duration > DOUYIN_VIDEO_MAX_DURATION:
                logger.error(f"Video too long: {duration}s > {DOUYIN_VIDEO_MAX_DURATION}s")
                return False

            if duration < DOUYIN_VIDEO_MIN_DURATION:
                logger.error(f"Video too short: {duration}s < {DOUYIN_VIDEO_MIN_DURATION}s")
                return False

        except Exception as e:
            logger.warning(f"Failed to check video duration: {str(e)}")

        return True

    def _get_upload_params(self, video_path: Path) -> Dict[str, Any]:
        """
        获取上传参数

        Args:
            video_path: 视频路径

        Returns:
            上传参数字典
        """
        try:
            url = f"{self.base_url}/web/api/media/upload/auth/"
            response = self.session.post(url, timeout=10)

            if response.status_code != 200:
                raise RuntimeError(f"Failed to get upload params: {response.status_code}")

            data = response.json()
            logger.info("Upload params retrieved")
            return data

        except Exception as e:
            logger.error(f"Failed to get upload params: {str(e)}")
            raise

    def _upload_to_tos(self, video_path: Path, upload_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        上传视频到 TOS 存储

        Args:
            video_path: 视频路径
            upload_params: 上传参数

        Returns:
            上传结果
        """
        try:
            tos_url = upload_params.get("upload_url")
            tos_token = upload_params.get("upload_token")

            if not tos_url or not tos_token:
                raise ValueError("Invalid upload parameters")

            file_size = video_path.stat().st_size

            with open(video_path, 'rb') as f:
                files = {'video': (video_path.name, f, 'video/mp4')}
                data = {
                    'upload_token': tos_token,
                }

                headers = {
                    'Content-Length': str(file_size)
                }

                response = requests.post(
                    tos_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=300
                )

            response.raise_for_status()
            result = response.json()

            logger.info(f"Video uploaded to TOS: {result.get('video_id')}")
            return result

        except Exception as e:
            logger.error(f"Failed to upload to TOS: {str(e)}")
            raise

    def _update_video_info(
        self,
        video_id: str,
        title: str,
        description: str = None,
        topics: list = None
    ) -> Dict[str, Any]:
        """
        更新视频信息

        Args:
            video_id: 视频 ID
            title: 标题
            description: 描述
            topics: 话题标签

        Returns:
            更新结果
        """
        try:
            url = f"{self.base_url}/web/api/media/publish/update/"

            payload = {
                'video_id': video_id,
                'text': description or title,
            }

            if topics:
                payload['hashtags'] = topics

            response = self.session.post(url, json=payload, timeout=10)

            if response.status_code != 200:
                raise RuntimeError(f"Failed to update video info: {response.status_code}")

            data = response.json()
            logger.info(f"Video info updated: {video_id}")
            return data

        except Exception as e:
            logger.error(f"Failed to update video info: {str(e)}")
            raise

    def _publish_video(self, video_id: str) -> Dict[str, Any]:
        """
        发布视频

        Args:
            video_id: 视频 ID

        Returns:
            发布结果
        """
        try:
            url = f"{self.base_url}/web/api/media/publish/publish/"

            payload = {
                'video_id': video_id
            }

            response = self.session.post(url, json=payload, timeout=10)

            if response.status_code != 200:
                raise RuntimeError(f"Failed to publish video: {response.status_code}")

            data = response.json()
            logger.info(f"Video published: {video_id}")
            return data

        except Exception as e:
            logger.error(f"Failed to publish video: {str(e)}")
            raise

    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: str = None,
        topics: list = None,
        auto_publish: bool = True
    ) -> Dict[str, Any]:
        """
        上传视频的完整流程

        Args:
            video_path: 视频路径
            title: 视频标题
            description: 视频描述
            topics: 话题标签列表
            auto_publish: 是否自动发布

        Returns:
            上传结果
        """
        logger.info(f"Starting upload process for: {video_path.name}")

        if not self._validate_video(video_path):
            raise ValueError("Video validation failed")

        upload_params = self._get_upload_params(video_path)
        tos_result = self._upload_to_tos(video_path, upload_params)

        video_id = tos_result.get("video_id")
        if not video_id:
            raise ValueError("No video ID in upload result")

        update_result = self._update_video_info(
            video_id,
            title,
            description,
            topics
        )

        if auto_publish:
            publish_result = self._publish_video(video_id)

            uploaded_path = UPLOADED_DIR / video_path.name
            import shutil
            shutil.move(str(video_path), str(uploaded_path))

            return {
                "video_id": video_id,
                "upload_result": tos_result,
                "update_result": update_result,
                "publish_result": publish_result,
                "status": "published"
            }

        return {
            "video_id": video_id,
            "upload_result": tos_result,
            "update_result": update_result,
            "status": "draft"
        }

    def upload_multiple_videos(
        self,
        video_info_list: list,
        delay: int = 30
    ) -> list:
        """
        批量上传多个视频

        Args:
            video_info_list: 视频信息列表，每个元素包含 (video_path, title, description, topics)
            delay: 上传间隔（秒）

        Returns:
            上传结果列表
        """
        results = []

        for i, video_info in enumerate(video_info_list):
            try:
                logger.info(f"Uploading video {i + 1}/{len(video_info_list)}")

                result = self.upload_video(**video_info)
                results.append(result)

                if i < len(video_info_list) - 1:
                    logger.info(f"Waiting {delay}s before next upload...")
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"Failed to upload video {i + 1}: {str(e)}")
                results.append({
                    "error": str(e),
                    "status": "failed"
                })

        return results
