#!/usr/bin/env python3
"""
完整端到端测试
使用项目的完整流程：PromptManager + CogVideoClient
"""
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_e2e_flow():
    """测试完整的端到端流程"""
    print("=" * 70)
    print("🎬 完整端到端流程测试")
    print("=" * 70)
    print("")

    try:
        from src.video_generator.cogvideo_client import CogVideoClient
        from src.video_generator.prompt_manager import PromptManager
        from src.config.settings import (
            COGVIDEO_API_KEY,
            VIDEO_DIR,
            COGVIDEO_DEFAULT_QUALITY,
            COGVIDEO_DEFAULT_SIZE,
            COGVIDEO_DEFAULT_FPS,
            COGVIDEO_WITH_AUDIO
        )

        print("=" * 70)
        print("📋 步骤 1/5：初始化组件")
        print("=" * 70)
        print("")

        client = CogVideoClient()
        print("✅ CogVideoClient 初始化成功")

        prompt_manager = PromptManager()
        print("✅ PromptManager 初始化成功")
        print(f"✅ Prompt 库总数: {prompt_manager.get_prompt_count()}")
        print("")

        print("=" * 70)
        print("🎭 步骤 2/5：获取火影忍者 Prompt")
        print("=" * 70)
        print("")

        available_categories = prompt_manager.get_all_categories()
        print("可用分类：")
        for category in available_categories:
            count = prompt_manager.get_prompt_count(category)
            print(f"  - {category}: {count} 个 Prompt")
        print("")

        prompt = prompt_manager.get_random_prompt(category="battle")
        print(f"✅ 选择的 Prompt: {prompt[:80]}...")
        print("")

        print("=" * 70)
        print("📡 步骤 3/5：提交视频生成任务")
        print("=" * 70)
        print("")

        print(f"Prompt: {prompt}")
        print(f"质量: {COGVIDEO_DEFAULT_QUALITY}")
        print(f"分辨率: {COGVIDEO_DEFAULT_SIZE}")
        print(f"帧率: {COGVIDEO_DEFAULT_FPS}")
        print(f"音频: {COGVIDEO_WITH_AUDIO}")
        print("")

        start_time = time.time()

        task = client.generate_video(
            prompt=prompt,
            quality=COGVIDEO_DEFAULT_QUALITY,
            size=COGVIDEO_DEFAULT_SIZE,
            fps=COGVIDEO_DEFAULT_FPS,
            with_audio=COGVIDEO_WITH_AUDIO
        )

        task_id = task.get("id")
        print(f"✅ 任务已提交")
        print(f"   Task ID: {task_id}")
        print(f"   状态: {task.get('status')}")
        print(f"   耗时: {time.time() - start_time:.2f} 秒")
        print("")

        print("=" * 70)
        print("⏳ 步骤 4/5：等待视频生成完成")
        print("=" * 70)
        print("   这可能需要 1-5 分钟，请耐心等待...")
        print("")

        poll_start = time.time()
        max_wait = 300  # 5 分钟

        while time.time() - poll_start < max_wait:
            try:
                result = client.get_video_result(task_id, max_wait=max_wait)
                status = result.get("status")

                if status == "succeeded":
                    print("")
                    print("✅ 视频生成成功！")
                    print("")

                    video_url = result.get("output", {}).get("video_url")
                    cover_url = result.get("output", {}).get("cover_image_url")

                    print(f"视频 URL: {video_url[:80]}...")
                    print(f"封面 URL: {cover_url[:80] if cover_url else 'N/A'}...")
                    print("")

                    break

                elif status == "processing":
                    elapsed = int(time.time() - poll_start)
                    print(f"[{elapsed}s] 状态: processing...", end="\r")
                    time.sleep(5)

                else:
                    print(f"\n❌ 未知状态: {status}")
                    return False

            except TimeoutError:
                print("\n⏰ 超时：视频生成时间超过 5 分钟")
                return False

        print("=" * 70)
        print("📥 步骤 5/5：下载视频到本地")
        print("=" * 70)
        print("")

        output_filename = f"naruto_e2e_{int(time.time())}.mp4"
        output_path = VIDEO_DIR / output_filename

        print(f"目标路径: {output_path}")
        print("   正在下载...", end=" ")

        download_start = time.time()

        video_url = result.get("output", {}).get("video_url")
        import requests
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 8192

            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                downloaded += len(chunk)
                percent = (downloaded / total_size) * 100
                print(f"\r   下载进度: {percent:.1f}% ({downloaded / 1024 / 1024:.2f} MB)", end="")

        download_time = time.time() - download_start
        print(f"\n   ✅ 下载完成！")
        print(f"   耗时: {download_time:.2f} 秒")
        print("")

        print("=" * 70)
        print("✅ 端到端流程测试成功！")
        print("=" * 70)
        print("")

        file_size = output_path.stat().st_size
        total_time = time.time() - start_time

        print("📊 测试统计：")
        print(f"  - 总耗时: {total_time / 60:.2f} 分钟")
        print(f"  - 文件大小: {file_size / 1024 / 1024:.2f} MB")
        print(f"  - 下载速度: {file_size / 1024 / 1024 / download_time:.2f} MB/s")
        print(f"  - 保存路径: {output_path}")
        print("")

        print("=" * 70)
        print("✨ 验证项：")
        print("  ✅ PromptManager 工作正常")
        print("  ✅ CogVideoClient 工作正常")
        print("  ✅ API Key 有效")
        print("  ✅ 任务提交成功")
        print("  ✅ 状态轮询正常")
        print("  ✅ 视频下载成功")
        print("  ✅ 文件保存成功")
        print("=" * 70)

        return True

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        print("")
        print("=" * 70)
        print("❌ 端到端测试失败")
        print("=" * 70)
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_e2e_flow()

    if not success:
        print("")
        print("=" * 70)
        print("❌ 测试失败")
        print("=" * 70)
        return 1

    print("")
    print("🎉 所有测试通过！")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
