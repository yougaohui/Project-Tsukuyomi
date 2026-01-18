"""
示例：运行团队工作流

Usage:
  python examples/run_team_workflow.py
"""
import asyncio
from src.agents.base_agent import AgentFactory
from src.agents.team_manager_agent import TeamManagerAgent


async def main():
    print("🚀 启动 AI Agent 团队演示\n")

    team_manager = TeamManagerAgent()

    result = await team_manager.run_full_workflow(
        count=2,
        category="battle",
        platforms=["douyin"]
    )

    print(f"\n✅ 工作流完成: {result['status']}")


if __name__ == "__main__":
    asyncio.run(main())
