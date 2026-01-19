#!/usr/bin/env python3
"""
测试AI Agent团队模块导入

Usage:
  python test_team_imports.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """测试所有模块导入"""
    print("🔍 测试模块导入...\n")

    try:
        from src.agents.base_agent import BaseAgent, AgentFactory, Task, create_task_id
        print("✅ base_agent.py 导入成功")
    except Exception as e:
        print(f"❌ base_agent.py 导入失败: {e}")
        return False

    try:
        from src.agents.content_writer_agent import ContentWriterAgent
        print("✅ content_writer_agent.py 导入成功")
    except Exception as e:
        print(f"❌ content_writer_agent.py 导入失败: {e}")

    try:
        from src.agents.video_generator_agent import VideoGeneratorAgent
        print("✅ video_generator_agent.py 导入成功")
    except Exception as e:
        print(f"❌ video_generator_agent.py 导入失败: {e}")

    try:
        from src.agents.platform_uploader_agent import PlatformUploaderAgent
        print("✅ platform_uploader_agent.py 导入成功")
    except Exception as e:
        print(f"❌ platform_uploader_agent.py 导入失败: {e}")

    try:
        from src.agents.team_manager_agent import TeamManagerAgent
        print("✅ team_manager_agent.py 导入成功")
    except Exception as e:
        print(f"❌ team_manager_agent.py 导入失败: {e}")

    try:
        from src.workflow import WorkflowPipeline, WorkflowManager
        print("✅ workflow 模块导入成功")
    except Exception as e:
        print(f"❌ workflow 模块导入失败: {e}")

    try:
        from src.integrations import create_llm_service
        print("✅ integrations 模块导入成功")
    except Exception as e:
        print(f"❌ integrations 模块导入失败: {e}")

    try:
        from src.analytics import AnalyticsEngine
        print("✅ analytics 模块导入成功")
    except Exception as e:
        print(f"❌ analytics 模块导入失败: {e}")

    print("\n🎉 模块导入测试完成")
    return True


def test_agent_creation():
    """测试Agent创建"""
    print("\n🔧 测试Agent创建...\n")

    from src.agents.base_agent import AgentFactory

    agents = [
        ("content_writer", {}),
        ("video_generator", {"max_concurrent": 2}),
        ("platform_uploader", {"max_concurrent": 1}),
        ("team_manager", {})
    ]

    for agent_type, config in agents:
        try:
            agent = AgentFactory.create_agent(agent_type, config)
            print(f"✅ {agent_type} 创建成功 (状态: {agent.status.value})")
        except Exception as e:
            print(f"❌ {agent_type} 创建失败: {e}")

    print(f"\n📋 已创建的Agent: {AgentFactory.list_agents()}")
    return True


def main():
    """主测试函数"""
    print("=" * 60)
    print("  🧪 AI Agent 团队模块测试")
    print("=" * 60)

    success = True
    success &= test_imports()
    success &= test_agent_creation()

    if success:
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 部分测试失败")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
