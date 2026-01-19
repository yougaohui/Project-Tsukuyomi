#!/usr/bin/env python3
"""
测试智谱AI官方SDK - zhipuai
使用官方SDK测试视频生成功能
"""
import os
import sys
import time
from pathlib import Path

def test_sdk():
    """测试 zhipuai SDK"""
    print("=" * 60)
    print("🧪 测试智谱AI官方 SDK")
    print("=" * 60)
    print("")

    # 读取 API Key
    api_key = None
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("COGVIDEO_API_KEY="):
                    api_key = line.split("=",1)[1].strip()
                    break
    except FileNotFoundError:
        print("❌ .env 文件不存在")
        return False
    except Exception as e:
        print(f"❌ 读取 .env 失败: {e}")
        return False

    if not api_key:
        print("❌ 未找到 COGVIDEO_API_KEY")
        return False

    print(f"✅ API Key: {api_key[:20]}...")
    print("")

    # 导入 SDK
    try:
        from zhipuai import ZhipuAI
        print("✅ 成功导入 zhipuai SDK")
    except ImportError as e:
        print(f"❌ 未安装 zhipuai SDK: {e}")
        print("   请运行: pip install zhipuai")
        return False

    # 初始化客户端
    try:
        client = ZhipuAI(api_key=api_key)
        print("✅ 成功初始化客户端")
    except Exception as e:
        print(f"❌ 初始化客户端失败: {e}")
        return False

    print("")

    # 测试视频生成
    print("=" * 60)
    print("📡 测试视频生成")
    print("=" * 60)
    print("")

    test_prompt = "A cat playing with a ball in a sunny garden"

    print(f"Prompt: {test_prompt}")
    print("")

    try:
        # 提交生成任务
        response = client.videos.generations(
            model="cogvideox-3",
            prompt=test_prompt,
            quality="speed",  # 使用 speed 模式更快
            with_audio=False,
            size="1280x720",
            fps=30
        )

        print(f"✅ 任务已提交")
        print(f"   Task ID: {response.id}")
        print("")

        # 轮询等待结果
        task_id = response.id
        max_wait = 300  # 5分钟
        poll_interval = 5
        start_time = time.time()

        print("⏳ 等待生成完成...")
        print("")

        while time.time() - start_time < max_wait:
            result = client.videos.retrieve_videos_result(id=task_id)
            status = result.task_status

            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}s] 状态: {status}")

            if status == "SUCCESS":
                print("")
                print("✅ 视频生成成功！")
                print("")

                video_url = result.video_result[0].url
                cover_url = result.video_result[0].cover_image_url

                print(f"视频 URL: {video_url}")
                print(f"封面 URL: {cover_url}")
                print("")

                return True

            elif status == "FAIL":
                print("")
                print("❌ 视频生成失败")
                print(f"错误: {result}")
                return False

            time.sleep(poll_interval)

        print("")
        print("⏰ 超时：视频生成时间超过5分钟")
        return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_sdk()

    print("")
    print("=" * 60)
    if success:
        print("✅ SDK 测试成功！")
    else:
        print("❌ SDK 测试失败")
    print("=" * 60)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
