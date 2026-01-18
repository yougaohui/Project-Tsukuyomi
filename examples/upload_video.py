#!/usr/bin/env python3
"""
示例脚本：上传视频到抖音
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.uploader.auth import DouyinAuth
from src.uploader.douyin_client import DouyinUploader
from src.utils.logger import setup_logger, get_logger

setup_logger("example_upload", "INFO")
logger = get_logger(__name__)


def main():
    """主函数"""
    print("=" * 50)
    print("上传视频到抖音示例")
    print("=" * 50 + "\n")

    video_path = input("请输入视频路径：").strip()
    video_path = Path(video_path)

    if not video_path.exists():
        print(f"❌ 文件不存在：{video_path}")
        return

    title = input("请输入视频标题：").strip()
    description = input("请输入视频描述（可选，按回车跳过）：").strip() or None

    try:
        auth = DouyinAuth()

        print("\n测试认证...")
        if not auth.test_auth():
            print("❌ 认证失败，请检查 Cookie")
            return

        print("✅ 认证成功\n")

        uploader = DouyinUploader(auth)

        result = uploader.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            topics=["#火影忍者", "#动漫", "#AI视频"],
            auto_publish=True
        )

        print("\n" + "=" * 50)
        print("上传成功！")
        print("=" * 50)
        print(f"视频 ID：{result.get('video_id')}")
        print(f"状态：{result.get('status')}")
        print("\n")

    except Exception as e:
        logger.error(f"上传失败：{str(e)}")
        print(f"❌ 上传失败：{str(e)}")


if __name__ == "__main__":
    main()
