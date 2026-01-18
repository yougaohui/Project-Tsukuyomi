#!/usr/bin/env python3
"""
火影忍者视频自动生成与上传系统
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scheduler.task_scheduler import TaskScheduler
from src.video_generator.cogvideo_client import CogVideoClient
from src.video_generator.prompt_manager import PromptManager
from src.video_processor.editor import VideoEditor
from src.utils.logger import setup_logger, get_logger
from src.config.settings import TEST_MODE, DEBUG

logger = get_logger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="火影忍者视频自动生成与上传系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动定时调度器
  python main.py --schedule

  # 立即生成3个视频
  python main.py --generate --count 3

  # 立即上传视频
  python main.py --upload

  # 测试 Prompt 系统
  python main.py --test-prompts
        """
    )

    parser.add_argument(
        '--schedule',
        action='store_true',
        help='启动定时调度器'
    )

    parser.add_argument(
        '--generate',
        action='store_true',
        help='立即生成视频'
    )

    parser.add_argument(
        '--upload',
        action='store_true',
        help='立即上传视频'
    )

    parser.add_argument(
        '--count',
        type=int,
        default=3,
        help='生成视频数量（默认：3）'
    )

    parser.add_argument(
        '--test-prompts',
        action='store_true',
        help='测试 Prompt 系统'
    )

    parser.add_argument(
        '--list-jobs',
        action='store_true',
        help='列出所有已安排的任务'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )

    args = parser.parse_args()

    if args.debug:
        import src.config.settings as settings
        settings.DEBUG = True
        setup_logger("main", "DEBUG")
        logger.info("Debug mode enabled")

    if args.test_prompts:
        test_prompts()

    elif args.list_jobs:
        list_jobs()

    elif args.schedule:
        run_scheduler()

    elif args.generate:
        run_generate(args.count)

    elif args.upload:
        run_upload()

    else:
        parser.print_help()


def test_prompts():
    """测试 Prompt 系统"""
    print("\n" + "=" * 50)
    print("测试 Prompt 系统")
    print("=" * 50 + "\n")

    prompt_manager = PromptManager()

    print(f"总共有 {prompt_manager.get_prompt_count()} 个 Prompt\n")

    categories = prompt_manager.get_all_categories()
    print("分类：")
    for category in categories:
        count = prompt_manager.get_prompt_count(category)
        print(f"  - {category}: {count} 个")

    print("\n随机 Prompt 示例：\n")

    for _ in range(5):
        prompt = prompt_manager.get_random_prompt()
        print(f"  - {prompt[:100]}...")

    print("\n自定义 Prompt 示例：\n")

    custom_prompt = prompt_manager.get_custom_prompt(
        character="Naruto Uzumaki",
        action="using Rasengan",
        style="epic anime style",
        background="Konohagakure village"
    )
    print(f"  - {custom_prompt}")

    print("\n" + "=" * 50 + "\n")


def list_jobs():
    """列出所有已安排的任务"""
    scheduler = TaskScheduler()
    scheduler.print_scheduled_jobs()


def run_scheduler():
    """运行调度器"""
    print("\n" + "=" * 50)
    print("启动火影忍者视频自动生成系统")
    print("=" * 50 + "\n")

    if TEST_MODE:
        print("⚠️  测试模式已启用，视频不会被上传到抖音\n")

    print("按 Ctrl+C 停止系统\n")

    try:
        scheduler = TaskScheduler()
        scheduler.start()
    except KeyboardInterrupt:
        print("\n\n系统已停止")


def run_generate(count: int):
    """运行视频生成"""
    print(f"\n生成 {count} 个视频...\n")

    try:
        scheduler = TaskScheduler()
        scheduler.run_immediate_generate(count)
        print("\n✅ 视频生成完成！")
    except Exception as e:
        print(f"\n❌ 生成失败：{str(e)}")


def run_upload():
    """运行视频上传"""
    print("\n上传视频到抖音...\n")

    if TEST_MODE:
        print("⚠️  测试模式已启用，无法上传到抖音")
        return

    try:
        scheduler = TaskScheduler()
        scheduler.run_immediate_upload()
        print("\n✅ 视频上传完成！")
    except Exception as e:
        print(f"\n❌ 上传失败：{str(e)}")


if __name__ == "__main__":
    main()
