"""
存储管理系统
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from src.config.settings import (
    VIDEO_DIR,
    PROCESSED_DIR,
    UPLOADED_DIR,
    WATERMARK_DIR,
    MUSIC_DIR,
    TEMP_FILE_RETENTION_DAYS,
    LOGS_DIR
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StorageManager:
    """存储管理器"""

    def __init__(self):
        self.directories = {
            "videos": VIDEO_DIR,
            "processed": PROCESSED_DIR,
            "uploaded": UPLOADED_DIR,
            "watermarks": WATERMARK_DIR,
            "music": MUSIC_DIR,
            "logs": LOGS_DIR
        }

    def get_directory(self, dir_type: str) -> Path:
        """
        获取指定类型的目录路径

        Args:
            dir_type: 目录类型 (videos/processed/uploaded/watermarks/music/logs)

        Returns:
            目录路径
        """
        return self.directories.get(dir_type, VIDEO_DIR)

    def ensure_directories(self):
        """确保所有目录存在"""
        for dir_path in self.directories.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        logger.info("All directories ensured")

    def move_video_to_processed(self, source_path: Path, new_name: str = None) -> Path:
        """
        将视频移动到已处理目录

        Args:
            source_path: 源文件路径
            new_name: 新文件名

        Returns:
            目标文件路径
        """
        if new_name is None:
            new_name = source_path.name

        target_path = PROCESSED_DIR / new_name

        shutil.move(str(source_path), str(target_path))
        logger.info(f"Moved video to processed: {target_path}")

        return target_path

    def move_video_to_uploaded(self, source_path: Path, new_name: str = None) -> Path:
        """
        将视频移动到已上传目录

        Args:
            source_path: 源文件路径
            new_name: 新文件名

        Returns:
            目标文件路径
        """
        if new_name is None:
            new_name = source_path.name

        target_path = UPLOADED_DIR / new_name

        shutil.move(str(source_path), str(target_path))
        logger.info(f"Moved video to uploaded: {target_path}")

        return target_path

    def copy_file(self, source_path: Path, target_dir: Path, new_name: str = None) -> Path:
        """
        复制文件

        Args:
            source_path: 源文件路径
            target_dir: 目标目录
            new_name: 新文件名

        Returns:
            目标文件路径
        """
        if new_name is None:
            new_name = source_path.name

        target_path = target_dir / new_name

        shutil.copy2(str(source_path), str(target_path))
        logger.info(f"Copied file to: {target_path}")

        return target_path

    def delete_file(self, file_path: Path):
        """
        删除文件

        Args:
            file_path: 文件路径
        """
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")

    def list_videos(self, dir_type: str = "videos") -> List[Path]:
        """
        列出目录中的所有视频文件

        Args:
            dir_type: 目录类型

        Returns:
            视频文件路径列表
        """
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm']
        directory = self.get_directory(dir_type)

        videos = [
            file for file in directory.iterdir()
            if file.is_file() and file.suffix.lower() in video_extensions
        ]

        logger.info(f"Found {len(videos)} videos in {directory}")

        return videos

    def get_file_size(self, file_path: Path) -> int:
        """
        获取文件大小（字节）

        Args:
            file_path: 文件路径

        Returns:
            文件大小（字节）
        """
        if file_path.exists():
            return file_path.stat().st_size
        return 0

    def format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小

        Args:
            size_bytes: 字节数

        Returns:
            格式化的文件大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def clean_temp_files(self, days: int = None):
        """
        清理临时文件

        Args:
            days: 保留天数，默认使用配置值
        """
        if days is None:
            days = TEMP_FILE_RETENTION_DAYS

        cutoff_date = datetime.now() - timedelta(days=days)

        for dir_type in ["videos", "processed"]:
            directory = self.get_directory(dir_type)
            deleted_count = 0

            for file in directory.iterdir():
                if file.is_file():
                    file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        file.unlink()
                        deleted_count += 1

            logger.info(f"Cleaned {deleted_count} temporary files from {dir_type}")

    def get_disk_usage(self, dir_type: str = None) -> dict:
        """
        获取磁盘使用情况

        Args:
            dir_type: 目录类型，None 表示检查所有目录

        Returns:
            磁盘使用信息字典
        """
        if dir_type:
            directories = [self.get_directory(dir_type)]
        else:
            directories = self.directories.values()

        total_usage = 0
        usage_by_dir = {}

        for directory in directories:
            dir_size = 0
            for file in directory.rglob('*'):
                if file.is_file():
                    dir_size += file.stat().st_size

            usage_by_dir[str(directory)] = dir_size
            total_usage += dir_size

        return {
            "total": total_usage,
            "by_directory": usage_by_dir
        }

    def generate_unique_filename(self, base_name: str, extension: str = ".mp4") -> str:
        """
        生成唯一的文件名

        Args:
            base_name: 基础名称
            extension: 文件扩展名

        Returns:
            唯一的文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}{extension}"

    def check_available_space(self, required_bytes: int, dir_type: str = "videos") -> bool:
        """
        检查是否有足够的磁盘空间

        Args:
            required_bytes: 需要的字节数
            dir_type: 目录类型

        Returns:
            是否有足够空间
        """
        import shutil
        stat = shutil.disk_usage(self.get_directory(dir_type))
        return stat.free >= required_bytes
