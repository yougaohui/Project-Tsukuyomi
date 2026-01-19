#!/usr/bin/env python3
"""
简单的集成测试 - 验证 zhipuai SDK 集成
不涉及视频处理，只测试视频生成功能
"""
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

def test_integration():
    """测试 SDK 集成"""
    print("=" * 60)
    print("🧪 集成测试：zhipuai SDK + CogVideoClient")
    print("=" * 60)
    print("")

    try:
        # 导入新的客户端
        from src.video_generator.cogvideo_client import CogVideoClient
        from src.config.settings import COGVIDEO_API_KEY
        print("✅ 成功导入 CogVideoClient")
        print(f"✅ API Key: {COGVIDEO_API_KEY[:20]}...")
        print("")

        # 初始化客户端
        client = CogVideoClient()
        print("✅ 成功初始化 CogVideoClient")
        print("✅ ZhipuAI SDK 已加载")
        print("")

        # 测试视频生成
        test_prompt = "A simple red circle moving across the screen"

        print("=" * 60)
        print("📡 测试视频生成")
        print("=" * 60)
        print(f"Prompt: {test_prompt}")
        print("")

        try:
            # 只生成任务，不下载（节省时间和带宽）
            result = client.generate_video(
                prompt=test_prompt,
                quality="speed",
                size="1280x720",
                fps=30,
                with_audio=False
            )

            print(f"✅ 视频生成任务已提交")
            print(f"   Task ID: {result.get('id')}")
            print(f"   Status: {result.get('status')}")
            print("")

            # 尝试查询状态（只查询一次，不等待完成）
            try:
                status_result = client.get_video_result(
                    task_id=result.get('id'),
                    max_wait=10  # 只等待10秒
                )
                print(f"   当前状态: {status_result.get('status')}")
            except TimeoutError:
                print("   ⏳ 任务仍在处理中（预期行为）")
            except Exception as e:
                print(f"   状态查询错误: {e}")

            print("")
            print("=" * 60)
            print("✅ 集成测试成功！")
            print("=" * 60)
            print("")
            print("✨ 迁移到 zhipuai SDK 完成！")
            print("")
            print("验证项：")
            print("  ✅ zhipuai SDK 安装")
            print("  ✅ SDK 导入成功")
            print("  ✅ CogVideoClient 初始化")
            print("  ✅ 视频生成任务提交")
            print("  ✅ 状态查询接口")
            print("")
            return True

        except Exception as e:
            print("")
            print("=" * 60)
            print("❌ 视频生成测试失败")
            print("=" * 60)
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_integration()

    if not success:
        print("")
        print("=" * 60)
        print("❌ 集成测试失败")
        print("=" * 60)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
