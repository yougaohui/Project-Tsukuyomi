"""
团队管理Agent

负责协调整个AI Agent团队的工作流
"""
from typing import Any, Dict, List, Optional
import asyncio
from datetime import datetime

from src.agents.base_agent import BaseAgent, Task, AgentFactory, create_task_id
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TeamManagerAgent(BaseAgent):
    """
    团队管理Agent

    负责协调各个Agent的工作，管理任务流程
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("team_manager", config)

        self.workflow_history: List[Dict[str, Any]] = []
        self.enable_analytics = config.get("enable_analytics", True) if config else True

        logger.info("TeamManagerAgent initialized")

    async def execute(self, task: Task) -> Dict[str, Any]:
        """
        执行团队管理任务

        Args:
            task: 任务数据，包含：
                - workflow_type: 工作流类型
                - params: 工作流参数

        Returns:
            工作流执行结果
        """
        workflow_type = task.data.get("workflow_type", "full")
        params = task.data.get("params", {})

        logger.info(f"Executing workflow: {workflow_type}")

        if workflow_type == "full":
            result = await self._run_full_workflow(**params)
        elif workflow_type == "generate_only":
            result = await self._run_generate_workflow(**params)
        elif workflow_type == "upload_only":
            result = await self._run_upload_workflow(**params)
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        await self._record_workflow(workflow_type, params, result)

        return result

    async def _run_full_workflow(
        self,
        count: int = 3,
        category: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        theme: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        运行完整工作流：生成提示词 -> 生成视频 -> 上传视频

        Args:
            count: 视频数量
            category: 类别
            platforms: 目标平台
            theme: 主题
            **kwargs: 其他参数

        Returns:
            工作流结果
        """
        logger.info(f"Starting full workflow: {count} videos")

        workflow_result = {
            "workflow_type": "full",
            "started_at": datetime.now().isoformat(),
            "stages": {}
        }

        try:
            stage1_result = await self._stage1_generate_prompts(
                count=count,
                category=category,
                theme=theme
            )
            workflow_result["stages"]["prompts"] = stage1_result

            stage2_result = await self._stage2_generate_videos(
                prompts=stage1_result["prompts"],
                **kwargs
            )
            workflow_result["stages"]["videos"] = stage2_result

            if platforms:
                stage3_result = await self._stage3_upload_videos(
                    videos=stage2_result["results"],
                    platforms=platforms,
                    category=category
                )
                workflow_result["stages"]["uploads"] = stage3_result

            workflow_result["status"] = "completed"
            workflow_result["completed_at"] = datetime.now().isoformat()

            logger.info("Full workflow completed successfully")

        except Exception as e:
            logger.error(f"Full workflow failed: {str(e)}")
            workflow_result["status"] = "failed"
            workflow_result["error"] = str(e)
            workflow_result["completed_at"] = datetime.now().isoformat()

        return workflow_result

    async def _run_generate_workflow(
        self,
        count: int = 3,
        category: Optional[str] = None,
        theme: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        运行生成工作流：生成提示词 -> 生成视频

        Args:
            count: 视频数量
            category: 类别
            theme: 主题
            **kwargs: 其他参数

        Returns:
            工作流结果
        """
        logger.info(f"Starting generate workflow: {count} videos")

        workflow_result = {
            "workflow_type": "generate_only",
            "started_at": datetime.now().isoformat(),
            "stages": {}
        }

        try:
            stage1_result = await self._stage1_generate_prompts(
                count=count,
                category=category,
                theme=theme
            )
            workflow_result["stages"]["prompts"] = stage1_result

            stage2_result = await self._stage2_generate_videos(
                prompts=stage1_result["prompts"],
                **kwargs
            )
            workflow_result["stages"]["videos"] = stage2_result

            workflow_result["status"] = "completed"
            workflow_result["completed_at"] = datetime.now().isoformat()

            logger.info("Generate workflow completed successfully")

        except Exception as e:
            logger.error(f"Generate workflow failed: {str(e)}")
            workflow_result["status"] = "failed"
            workflow_result["error"] = str(e)
            workflow_result["completed_at"] = datetime.now().isoformat()

        return workflow_result

    async def _run_upload_workflow(
        self,
        video_paths: List[str],
        category: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        运行上传工作流：上传视频

        Args:
            video_paths: 视频路径列表
            category: 类别
            platforms: 目标平台
            **kwargs: 其他参数

        Returns:
            工作流结果
        """
        logger.info(f"Starting upload workflow: {len(video_paths)} videos")

        workflow_result = {
            "workflow_type": "upload_only",
            "started_at": datetime.now().isoformat(),
            "stages": {}
        }

        try:
            videos = [{
                "path": path,
                "title": self._get_video_title(path, category),
                "description": "",
                "topics": []
            } for path in video_paths]

            stage3_result = await self._stage3_upload_videos(
                videos=videos,
                platforms=platforms or ["douyin"],
                category=category
            )
            workflow_result["stages"]["uploads"] = stage3_result

            workflow_result["status"] = "completed"
            workflow_result["completed_at"] = datetime.now().isoformat()

            logger.info("Upload workflow completed successfully")

        except Exception as e:
            logger.error(f"Upload workflow failed: {str(e)}")
            workflow_result["status"] = "failed"
            workflow_result["error"] = str(e)
            workflow_result["completed_at"] = datetime.now().isoformat()

        return workflow_result

    async def _stage1_generate_prompts(
        self,
        count: int,
        category: Optional[str],
        theme: Optional[str]
    ) -> Dict[str, Any]:
        """
        阶段1：生成提示词

        Args:
            count: 数量
            category: 类别
            theme: 主题

        Returns:
            阶段结果
        """
        logger.info("Stage 1: Generating prompts")

        content_writer = AgentFactory.get_agent("content_writer")
        if not content_writer:
            content_writer = AgentFactory.create_agent("content_writer")

        task = Task(
            id=create_task_id(),
            type="generate_prompts",
            data={
                "count": count,
                "category": category,
                "theme": theme
            }
        )

        result = await content_writer.process_task(task)

        return {
            "status": "success",
            "prompts": result["prompts"],
            "count": len(result["prompts"]),
            "method": result["method"]
        }

    async def _stage2_generate_videos(
        self,
        prompts: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        阶段2：生成视频

        Args:
            prompts: 提示词列表
            **kwargs: 其他参数

        Returns:
            阶段结果
        """
        logger.info("Stage 2: Generating videos")

        video_generator = AgentFactory.get_agent("video_generator")
        if not video_generator:
            video_generator = AgentFactory.create_agent("video_generator")

        task = Task(
            id=create_task_id(),
            type="generate_videos",
            data={
                "prompts": prompts,
                "config": kwargs
            }
        )

        result = await video_generator.process_task(task)

        return {
            "status": "success",
            "results": result["results"],
            "total": result["total"],
            "successful": result["successful"],
            "failed": result["failed"]
        }

    async def _stage3_upload_videos(
        self,
        videos: List[Dict[str, Any]],
        platforms: List[str],
        category: Optional[str]
    ) -> Dict[str, Any]:
        """
        阶段3：上传视频

        Args:
            videos: 视频信息列表
            platforms: 平台列表
            category: 类别

        Returns:
            阶段结果
        """
        logger.info(f"Stage 3: Uploading videos to {len(platforms)} platform(s)")

        uploader = AgentFactory.get_agent("platform_uploader")
        if not uploader:
            uploader = AgentFactory.create_agent("platform_uploader")

        for video in videos:
            video["topics"] = uploader.generate_hashtags(category)

        task = Task(
            id=create_task_id(),
            type="upload_videos",
            data={
                "videos": videos,
                "platforms": platforms,
                "delay": 30
            }
        )

        result = await uploader.process_task(task)

        return {
            "status": "success",
            "results": result["results"],
            "total": result["total"],
            "successful": result["successful"],
            "failed": result["failed"]
        }

    def _get_video_title(self, video_path: str, category: Optional[str]) -> str:
        """获取视频标题"""
        filename = video_path.split("/")[-1].replace(".mp4", "")
        return f"【火影忍者】{filename}"

    async def _record_workflow(
        self,
        workflow_type: str,
        params: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """记录工作流执行历史"""
        if not self.enable_analytics:
            return

        record = {
            "workflow_type": workflow_type,
            "params": params,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

        self.workflow_history.append(record)

        if len(self.workflow_history) > 100:
            self.workflow_history = self.workflow_history[-100:]

    def get_team_status(self) -> Dict[str, Any]:
        """
        获取团队状态

        Returns:
            团队状态信息
        """
        status = {
            "team_manager": self.get_status(),
            "agents": {}
        }

        for agent_type in AgentFactory.list_agents():
            agent = AgentFactory.get_agent(agent_type)
            if agent:
                status["agents"][agent_type] = agent.get_status()

        status["workflow_history"] = {
            "total": len(self.workflow_history),
            "recent": self.workflow_history[-5:] if self.workflow_history else []
        }

        return status

    def generate_report(self) -> Dict[str, Any]:
        """
        生成团队报告

        Returns:
            报告数据
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_workflows": len(self.workflow_history),
            "by_type": {},
            "success_rate": 0.0,
            "agent_metrics": {}
        }

        for workflow in self.workflow_history:
            wf_type = workflow["workflow_type"]
            if wf_type not in report["by_type"]:
                report["by_type"][wf_type] = {"total": 0, "successful": 0}

            report["by_type"][wf_type]["total"] += 1
            if workflow["result"].get("status") == "completed":
                report["by_type"][wf_type]["successful"] += 1

        total_completed = sum(
            wf["result"].get("status") == "completed"
            for wf in self.workflow_history
        )

        if self.workflow_history:
            report["success_rate"] = (total_completed / len(self.workflow_history)) * 100

        for agent_type in AgentFactory.list_agents():
            agent = AgentFactory.get_agent(agent_type)
            if agent:
                report["agent_metrics"][agent_type] = agent.get_status()

        return report

    async def run_full_workflow(
        self,
        count: int = 3,
        category: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        theme: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        运行完整工作流的便捷方法

        Args:
            count: 视频数量
            category: 类别
            platforms: 目标平台
            theme: 主题
            **kwargs: 其他参数

        Returns:
            工作流结果
        """
        task = Task(
            id=create_task_id(),
            type="full_workflow",
            data={
                "workflow_type": "full",
                "params": {
                    "count": count,
                    "category": category,
                    "platforms": platforms,
                    "theme": theme,
                    **kwargs
                }
            }
        )

        return await self.execute(task)
