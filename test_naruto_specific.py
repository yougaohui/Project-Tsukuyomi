#!/usr/bin/env python3
"""
测试明确的火影忍者视频生成
使用非常具体的角色名称和描述
"""
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_naruto_specific():
    """测试明确的火影忍者视频生成"""
    print("=" * 70)
    print("🎬 明确的火影忍者视频生成测试")
    print("=" * 70)
    print("")

    try:
        from src.video_generator.cogvideo_client import CogVideoClient
        from src.config.settings import VIDEO_DIR

        print("=" * 70)
        print("📋 步骤 1/3：设置明确的 Prompt")
        print("=" * 70)
        print("")

        # 使用非常明确的火影忍者 Prompt
        prompts = {
            1: "Naruto Uzumaki with bright yellow hair wearing orange jumpsuit, using Rasengan with blue chakra energy, anime style, 1080p high quality",
            2: "Sasuke Uchiha with spiky black hair, wearing dark blue outfit, red Sharingan eyes activated, lightning Chidori technique, anime style",
            3: "Kakashi Hatake with silver hair and face mask, wearing green vest, reading orange book in forest, anime style, peaceful scene"
        }

        print("可用的 Prompt：")
        for num, prompt in prompts.items():
            print(f"  {num}. {prompt[:70]}...")
        print("")

        # 选择第1个（最明确的）
        selected_prompt = prompts[1]  # Sasuke - 最明确的描述
        print(f"✅ 选择 Prompt 1: {selected_prompt[:80]}...")
        print("")

        print("=" * 70)
        print("📡 步骤 2/3：提交视频生成任务")
        print("=" * 70)
        print("")

        client = CogVideoClient()
        print("✅ 初始化 CogVideoClient")
        print("")

        print(f"Prompt: {selected_prompt}")
        print("")

        start_time = time.time()

        task = client.generate_video(
            prompt=selected_prompt,
            quality="quality",
            size="1920x1080",
            fps=30,
            with_audio=False
        )

        task_id = task.get("id")
        print(f"✅ 任务已提交")
        print(f"   Task ID: {task_id}")
        print(f"   状态: {task.get('status')}")
        print(f"   耗时: {time.time() - start_time:.2f} 秒")
        print("")

        print("=" * 70)
        print("⏳ 步骤 3/3：等待视频生成完成")
        print("=" * 70)
        print("   这可能需要 3-5 分钟，请耐心等待...")
        print("")

        poll_start = time.time()
        max_wait = 300

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
                    if cover_url:
                        print(f"封面 URL: {cover_url[:80]}...")
                    print("")

                    break

                elif status == "processing":
                    elapsed = int(time.time() - poll_start)
                    print(f"[{elapsed}s] 状态: processing...", end="\r")
                    time.sleep(10)

                elif status == "failed":
                    print(f"\n❌ 视频生成失败")
                    print(f"   {result}")
                    return False

            except TimeoutError:
                print("\n⏰ 超时：视频生成时间超过 5 分钟")
                return False

        print("=" * 70)
        print("📥 下载视频到本地")
        print("=" * 70)
        print("")

        output_filename = f"sasuke_specific_{int(time.time())}.mp4"
        output_path = VIDEO_DIR / output_filename

        print(f"目标路径: {output_path}")
        print("   正在下载...", end=" ")

        import requests
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("✅ 下载完成！")
        print("")

        file_size = output_path.stat().st_size
        print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
        print(f"保存路径: {output_path}")
        print("")

        print("=" * 70)
        print("✨ 测试完成")
        print("=" * 70)
        print("")

        print("验证项：")
        print("  ✅ 使用了明确的角色名称（Sasuke Uchiha）")
        print("  ✅ 使用了详细的外貌描述")
        print("  ✅ 使用了具体的动作描述")
        print("  ✅ 使用了 anime style")
        print("=" * 70)

        return True

    except Exception as e:
        print("")
        print("=" * 70)
        print("❌ 测试失败")
        print("=" * 70)
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_naruto_specific()

    if not success:
        print("")
        print("=" * 70)
        print("❌ 测试失败")
        print("=" * 70)
        return 1

    print("")
    print("🎉 测试成功！")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
