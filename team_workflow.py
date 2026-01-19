#!/usr/bin/env python3
"""
团队工作流入口

AI Agent团队的统一入口点
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents.base_agent import AgentFactory
from src.agents.team_manager_agent import TeamManagerAgent
from src.utils.logger import setup_logger, get_logger

logger = get_logger(__name__)


async def run_full_workflow(
    count: int = 3,
    category: str = None,
    platforms: list = None,
    theme: str = None
):
    """
    运行完整工作流

    Args:
        count: 视频数量
        category: 类别
        platforms: 目标平台
        theme: 主题
    """
    print("\n" + "=" * 60)
    print("  🚀 启动 AI Agent 团队工作流")
    print("=" * 60)
    print(f"\n📋 配置:")
    print(f"   - 视频数量: {count}")
    print(f"   - 类别: {category or '随机'}")
    print(f"   - 平台: {platforms or ['抖音']}")
    print(f"   - 主题: {theme or '无'}")
    print()

    team_manager = TeamManagerAgent()

    result = await team_manager.run_full_workflow(
        count=count,
        category=category,
        platforms=platforms,
        theme=theme
    )

    print("\n" + "=" * 60)
    print("  📊 工作流执行结果")
    print("=" * 60)

    if result.get("status") == "completed":
        print("\n✅ 工作流执行成功!")
        print(f"\n📈 统计数据:")
        print(f"   - 提示词生成: {result.get('stages', {}).get('prompts', {}).get('count', 0)} 个")
        print(f"   - 视频生成: {result.get('stages', {}).get('videos', {}).get('successful', 0)}/{result.get('stages', {}).get('videos', {}).get('total', 0)} 个")
        if 'uploads' in result.get('stages', {}):
            print(f"   - 视频上传: {result.get('stages', {}).get('uploads', {}).get('successful', 0)}/{result.get('stages', {}).get('uploads', {}).get('total', 0)} 个")
    else:
        print(f"\n❌ 工作流执行失败: {result.get('error')}")

    return result


async def show_team_status():
    """显示团队状态"""
    print("\n" + "=" * 60)
    print("  👥 AI Agent 团队状态")
    print("=" * 60)

    team_manager = TeamManagerAgent()
    status = team_manager.get_team_status()

    print(f"\n🤖 已注册的 Agent:")
    for agent_type, agent_status in status.get("agents", {}).items():
        print(f"   - {agent_type}: {agent_status['status']}")

    print(f"\n📊 性能指标:")
    for agent_type, agent_status in status.get("agents", {}).items():
        metrics = agent_status.get("metrics", {})
        print(f"   {agent_type}:")
        print(f"      - 已完成任务: {metrics.get('completed_tasks', 0)}")
        print(f"      - 失败任务: {metrics.get('failed_tasks', 0)}")
        print(f"      - 成功率: {metrics.get('success_rate', '0%')}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Agent 团队工作流",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行完整工作流（生成3个视频并上传到抖音）
  python team_workflow.py --full --count 3

  # 只生成视频
  python team_workflow.py --generate --count 5 --category battle

  # 查看团队状态
  python team_workflow.py --status
        """
    )

    parser.add_argument(
        '--full',
        action='store_true',
        help='运行完整工作流（生成提示词 -> 生成视频 -> 上传视频）'
    )

    parser.add_argument(
        '--generate',
        action='store_true',
        help='只运行生成工作流（生成提示词 -> 生成视频）'
    )

    parser.add_argument(
        '--upload',
        action='store_true',
        help='只运行上传工作流'
    )

    parser.add_argument(
        '--count',
        type=int,
        default=3,
        help='生成视频数量（默认: 3）'
    )

    parser.add_argument(
        '--category',
        type=str,
        choices=['character', 'jutsu', 'scene', 'battle', 'emotional'],
        help='视频类别'
    )

    parser.add_argument(
        '--platforms',
        type=str,
        nargs='+',
        default=['douyin'],
        help='目标平台（默认: douyin）'
    )

    parser.add_argument(
        '--theme',
        type=str,
        help='视频主题'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='显示团队状态'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )

    args = parser.parse_args()

    if args.debug:
        setup_logger("main", "DEBUG")
        logger.setLevel("DEBUG")

    if args.status:
        asyncio.run(show_team_status())

    elif args.full:
        asyncio.run(run_full_workflow(
            count=args.count,
            category=args.category,
            platforms=args.platforms,
            theme=args.theme
        ))

    elif args.generate:
        team_manager = TeamManagerAgent()
        result = asyncio.run(team_manager._run_generate_workflow(
            count=args.count,
            category=args.category,
            theme=args.theme
        ))
        print(f"生成工作流完成: {result}")

    elif args.upload:
        print("请提供要上传的视频路径列表")
        print("用法: python team_workflow.py --upload --videos <path1> <path2>")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
