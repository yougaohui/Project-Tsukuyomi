#!/usr/bin/env python3
"""
短视频自动化运营 Agent - 使用示例

功能：
- 多平台账号管理
- 视频内容管理
- 定时发布调度
- 数据统计分析
"""

import sys
import os
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.operations import VideoOperationsAgent, AccountManager
from src.agents.operations.video_operations_agent import Platform, PublishStrategy, PublishConfig


def example_basic_usage():
    """基础使用示例"""
    print("="*60)
    print("示例1: 基础使用")
    print("="*60)
    
    # 创建 Agent
    agent = VideoOperationsAgent()
    
    # 加载视频
    video_count = agent.load_videos(Path("data/videos"))
    print(f"加载了 {video_count} 个视频")
    
    # 查看状态
    status = agent.get_status()
    print(f"队列中视频数: {status['queue_size']}")
    print(f"总视频数: {status['stats']['total_videos']}")


def example_add_single_video():
    """添加单个视频示例"""
    print("\n" + "="*60)
    print("示例2: 添加单个视频")
    print("="*60)
    
    agent = VideoOperationsAgent()
    
    # 添加视频
    video = agent.add_video(
        file_path=Path("data/videos/test.mp4"),
        title="🎬 火影忍者 AI 生成视频",
        description="这是一个使用 AI 生成的火影忍者主题视频",
        category="动漫",
        tags=["火影忍者", "动漫", "AI"],
        topics=["#火影忍者", "#动漫", "#AI视频"]
    )
    
    if video:
        print(f"添加视频成功: {video.title}")
        print(f"视频ID: {video.id}")
        print(f"状态: {video.status.value}")


def example_publish_video():
    """发布视频示例"""
    print("\n" + "="*60)
    print("示例3: 发布视频")
    print("="*60)
    
    agent = VideoOperationsAgent()
    
    # 添加并发布视频
    video = agent.add_video(
        file_path=Path("data/videos/test.mp4"),
        title="测试视频"
    )
    
    if video:
        # 发布到抖音
        result = agent.publish_video(
            video_id=video.id,
            platform=Platform.DOUYIN,
            strategy=PublishStrategy.IMMEDIATE
        )
        
        print(f"发布结果: {result}")


def example_batch_publish():
    """批量发布示例"""
    print("\n" + "="*60)
    print("示例4: 批量发布")
    print("="*60)
    
    agent = VideoOperationsAgent()
    
    # 加载视频
    agent.load_videos(Path("data/videos"))
    
    # 批量发布
    results = agent.batch_publish(
        platform=Platform.DOUYIN,
        strategy=PublishStrategy.OPTIMAL
    )
    
    print(f"批量发布完成: {len(results)} 个视频")
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. {'成功' if result.get('success') else '失败'}")


def example_schedule():
    """定时发布示例"""
    print("\n" + "="*60)
    print("示例5: 定时发布")
    print("="*60)
    
    agent = VideoOperationsAgent()
    
    # 加载视频
    agent.load_videos(Path("data/videos"))
    
    # 调度到最佳时段发布
    count = agent.schedule_all(
        platform=Platform.DOUYIN,
        strategy=PublishStrategy.OPTIMAL
    )
    
    print(f"已调度 {count} 个视频到最佳时段")
    
    # 查看调度状态
    status = agent.get_status()
    print(f"调度状态: {status}")


def example_multi_platform():
    """多平台发布示例"""
    print("\n" + "="*60)
    print("示例6: 多平台发布")
    print("="*60)
    
    agent = VideoOperationsAgent()
    
    # 配置发布到多个平台
    config = PublishConfig(
        platforms=[Platform.DOUYIN, Platform.KUAISHOU, Platform.BILIBILI]
    )
    
    agent = VideoOperationsAgent(config=config)
    
    # 添加视频
    video = agent.add_video(
        file_path=Path("data/videos/test.mp4"),
        title="多平台发布测试"
    )
    
    if video:
        # 分散发布到所有平台
        result = agent.publish_video(
            video_id=video.id,
            strategy=PublishStrategy.DISTRIBUTED
        )
        
        print(f"发布结果: {result}")


def example_statistics():
    """统计示例"""
    print("\n" + "="*60)
    print("示例7: 数据统计")
    print("="*60)
    
    agent = VideoOperationsAgent()
    
    # 加载视频并发布一些
    agent.load_videos(Path("data/videos"))
    
    # 获取统计
    stats = agent.get_statistics()
    
    print("统计数据:")
    print(f"  总视频数: {stats['overview']['total_videos']}")
    print(f"  已发布: {stats['overview']['published_videos']}")
    print(f"  失败: {stats['overview']['failed_videos']}")
    
    if 'platforms' in stats:
        print("\n平台统计:")
        for platform, data in stats['platforms'].items():
            print(f"  {platform}: {data['success']}/{data['total']}")


def example_config():
    """配置示例"""
    print("\n" + "="*60)
    print("示例8: 配置管理")
    print("="*60)
    
    # 创建自定义配置
    config = PublishConfig(
        optimal_hours=[9, 12, 18, 20, 21],  # 黄金时段
        max_daily=5,                            # 每日最多5个
        min_interval=3600,                      # 最小间隔1小时
        auto_retry=True,                        # 自动重试
        max_retries=3,                          # 最多重试3次
        retry_interval=600                      # 重试间隔10分钟
    )
    
    agent = VideoOperationsAgent(config=config)
    
    # 导出配置
    agent.export_config(Path("agent_config.json"))
    print("配置已导出到 agent_config.json")
    
    # 导入配置
    agent.import_config(Path("agent_config.json"))
    print("配置已导入")


def main():
    """主函数"""
    print("短视频自动化运营 Agent - 使用示例\n")
    
    examples = [
        ("基础使用", example_basic_usage),
        ("添加单个视频", example_add_single_video),
        ("发布视频", example_publish_video),
        ("批量发布", example_batch_publish),
        ("定时发布", example_schedule),
        ("多平台发布", example_multi_platform),
        ("数据统计", example_statistics),
        ("配置管理", example_config),
    ]
    
    # 运行所有示例
    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"\n❌ 示例 {name} 执行失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("所有示例执行完成！")
    print("="*60)


if __name__ == "__main__":
    main()
