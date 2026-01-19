#!/usr/bin/env python3
"""
完整工作流演示

Usage:
  python3 demo_workflow.py
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents.content_writer_agent import ContentWriterAgent
from src.agents.team_manager_agent import TeamManagerAgent
from src.integrations import create_llm_service
from src.analytics import AnalyticsEngine


async def demo_full_workflow():
    """
    演示完整工作流
    
    流程: 生成Prompt -> 生成标题/标签 -> 记录数据 -> 生成报告
    """
    print("\n" + "=" * 70)
    print("  🚀 AI Agent 团队完整工作流演示")
    print("=" * 70)
    
    # 阶段1: 文案策划Agent
    print("\n📝 阶段1: 文案策划Agent工作")
    print("-" * 50)
    
    writer = ContentWriterAgent()
    
    # 获取3个战斗类Prompt
    prompts = writer.get_multiple_prompts(3, 'battle')
    print(f"✅ 获取到 {len(prompts)} 个战斗场景Prompt:")
    
    for i, prompt in enumerate(prompts, 1):
        title = writer.generate_title(prompt, category='battle')
        tags = writer.generate_hashtags(category='battle')
        print(f"\n  [{i}] Prompt: {prompt[:60]}...")
        print(f"      标题: {title}")
        print(f"      标签: {tags[0]}, {tags[1]}, {tags[2]}...")
    
    # 阶段2: LLM服务演示
    print("\n\n🤖 阶段2: LLM服务演示")
    print("-" * 50)
    
    llm = create_llm_service('mock')
    response = await llm.generate("Create a Naruto video prompt")
    print(f"✅ LLM生成结果:")
    print(f"   {response}")
    
    # 阶段3: 数据分析演示
    print("\n\n📊 阶段3: 数据分析演示")
    print("-" * 50)
    
    analytics = AnalyticsEngine()
    
    # 模拟记录一些视频数据
    for i in range(1, 4):
        analytics.record_video_performance(
            video_id=f'demo_{i:03d}',
            prompt=prompts[i-1],
            platform='douyin',
            metrics={
                'views': 1000 * i,
                'likes': 50 * i,
                'comments': 10 * i,
                'shares': 5 * i
            }
        )
    
    print(f"✅ 记录了 3 个演示视频数据")
    
    # 生成分析报告
    report = analytics.generate_report()
    print(f"\n📈 分析报告:")
    print(f"   总视频数: {report['total_videos']}")
    print(f"   总播放量: {report['summary']['total_views']}")
    print(f"   总点赞数: {report['summary']['total_likes']}")
    print(f"   总评论数: {report['summary']['total_comments']}")
    
    # 平台统计
    platform_stats = analytics.get_platform_stats()
    print(f"\n📱 平台统计:")
    for platform, stats in platform_stats.items():
        print(f"   {platform}:")
        print(f"      视频数: {stats['video_count']}")
        print(f"      平均播放: {stats['avg_views']:.0f}")
        print(f"      平均互动率: {stats['avg_engagement_rate']:.2f}%")
    
    # 阶段4: 团队管理演示
    print("\n\n👥 阶段4: 团队管理Agent演示")
    print("-" * 50)
    
    manager = TeamManagerAgent()
    status = manager.get_team_status()
    
    print(f"✅ 团队状态:")
    print(f"   已注册Agent数: {len(status['agents'])}")
    print(f"   Agent列表: {list(status['agents'].keys())}")
    
    # 生成团队报告
    report = manager.generate_report()
    print(f"\n📋 团队报告:")
    print(f"   总工作流执行: {report['total_workflows']}")
    print(f"   成功率: {report['success_rate']:.1f}%")
    
    print("\n" + "=" * 70)
    print("  🎉 工作流演示完成!")
    print("=" * 70)
    
    print("\n💡 下一步操作:")
    print("   1. 配置API密钥 (.env)")
    print("   2. 运行完整工作流:")
    print("      python3 team_workflow.py --full --count 3")
    print("   3. 查看团队状态:")
    print("      python3 team_workflow.py --status")
    print("   4. 只生成视频:")
    print("      python3 team_workflow.py --generate --count 5 --category battle")


def main():
    """主函数"""
    print("\n🚀 启动AI Agent团队演示...\n")
    
    try:
        asyncio.run(demo_full_workflow())
    except KeyboardInterrupt:
        print("\n\n👋 演示被中断")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
