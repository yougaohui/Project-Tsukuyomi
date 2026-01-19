#!/usr/bin/env python3
"""
完整流程测试：视频生成 + 下载
不包含视频处理（水印、裁剪等），只测试核心功能
"""
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_full_flow():
    """测试完整的视频生成和下载流程"""
    print("=" * 60)
    print("🎬 完整流程测试：生成 + 下载")
    print("=" * 60)
    print("")

    try:
        from src.video_generator.cogvideo_client import CogVideoClient
        from src.config.settings import (
            COGVIDEO_API_KEY,
            VIDEO_DIR,
            COGVIDEO_DEFAULT_QUALITY,
            COGVIDEO_DEFAULT_SIZE,
            COGVIDEO_DEFAULT_FPS,
            COGVIDEO_WITH_AUDIO
        )
        print("✅ 成功导入模块")
        print(f"✅ API Key: {COGVIDEO_API_KEY[:20]}...")
        print("")

        client = CogVideoClient()
        print("✅ 初始化 CogVideoClient")
        print("")

        test_prompt = "A beautiful sunset over the ocean with seagulls flying"

        print("=" * 60)
        print("📡 步骤 1/2：生成视频")
        print("=" * 60)
        print(f"Prompt: {test_prompt}")
        print("")

        task = client.generate_video(
            prompt=test_prompt,
            quality="speed",
            size="1280x720",
            fps=30,
            with_audio=False
        )

        task_id = task.get('id')
        print(f"✅ 任务已提交")
        print(f"   Task ID: {task_id}")
        print("")

        print("=" * 60)
        print("⏳ 步骤 2/2：等待并下载")
        print("=" * 60)
        print("   这可能需要 1-5 分钟...")
        print("")

        timestamp = int(time.time())
        video_path = client.generate_video_and_download(
            prompt=test_prompt,
            quality="speed",
            size="1280x720",
            fps=30,
            with_audio=False,
            output_dir=VIDEO_DIR,
            filename=f"test_video_{timestamp}.mp4"
        )

        print("")
        print("=" * 60)
        print("✅ 完整流程测试成功！")
        print("=" * 60)
        print("")
        print(f"✨ 视频已生成并下载到:")
        print(f"   {video_path}")
        print("")

        if video_path.exists():
            file_size = video_path.stat().st_size
            print(f"📊 文件大小: {file_size / 1024 / 1024:.2f} MB")
        else:
            print("⚠️ 警告：文件不存在")
            return False

        print("")
        print("=" * 60)
        print("验证项：")
        print("  ✅ zhipuai SDK 集成")
        print("  ✅ 视频生成任务提交")
        print("  ✅ 状态轮询")
        print("  ✅ 视频下载")
        print("  ✅ 文件保存")
        print("=" * 60)

        return True

    except Exception as e:
        print("")
        print("=" * 60)
        print("❌ 流程测试失败")
        print("=" * 60)
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_full_flow()

    if not success:
        print("")
        print("=" * 60)
        print("❌ 测试失败")
        print("=" * 60)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
