#!/usr/bin/env python3
"""
示例脚本：生成单个视频
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.video_generator.cogvideo_client import CogVideoClient
from src.video_generator.prompt_manager import PromptManager
from src.video_processor.editor import VideoEditor
from src.utils.logger import setup_logger, get_logger
from src.utils.storage import StorageManager

setup_logger("example_generate", "INFO")
logger = get_logger(__name__)


def main():
    """主函数"""
    print("=" * 50)
    print("火影忍者视频生成示例")
    print("=" * 50 + "\n")

    prompt_manager = PromptManager()
    video_generator = CogVideoClient()
    video_editor = VideoEditor()
    storage_manager = StorageManager()

    storage_manager.ensure_directories()

    prompt = prompt_manager.get_random_prompt(category="battle")
    print(f"使用 Prompt：\n{prompt}\n")

    try:
        video_path = video_generator.generate_video_and_download(
            prompt=prompt,
            quality="quality",
            size="1920x1080",
            fps=30
        )

        print(f"✅ 视频已生成：{video_path}")
        print(f"   文件大小：{storage_manager.format_file_size(storage_manager.get_file_size(video_path))}")

        processed_path = video_editor.process_video(
            video_path=video_path,
            crop=True,
            add_watermark_flag=True,
            add_music_flag=True,
            subtitle_text="火影忍者精彩时刻"
        )

        print(f"✅ 视频已处理：{processed_path}")

        print("\n" + "=" * 50)
        print("完成！")
        print("=" * 50 + "\n")

    except Exception as e:
        logger.error(f"生成失败：{str(e)}")
        print(f"❌ 生成失败：{str(e)}")


if __name__ == "__main__":
    main()
