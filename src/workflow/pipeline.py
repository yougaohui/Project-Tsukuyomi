"""
工作流编排模块

提供高级的工作流编排和任务管理功能
"""
from typing import Any, Dict, List, Optional
import asyncio

from src.agents.base_agent import AgentFactory, Task, create_task_id
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowPipeline:
    """
    工作流流水线

    负责执行定义好的工作流步骤
    """

    def __init__(self, name: str):
        self.name = name
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, step_name: str, agent_type: str, task_data: Dict[str, Any]):
        """
        添加工作流步骤

        Args:
            step_name: 步骤名称
            agent_type: Agent类型
            task_data: 任务数据
        """
        self.steps.append({
            "name": step_name,
            "agent_type": agent_type,
            "task_data": task_data
        })

        logger.debug(f"Added step '{step_name}' to pipeline '{self.name}'")

    async def execute(self) -> Dict[str, Any]:
        """
        执行工作流

        Returns:
            执行结果
        """
        logger.info(f"Starting pipeline: {self.name}")

        result = {
            "pipeline": self.name,
            "steps": [],
            "status": "success"
        }

        for i, step in enumerate(self.steps):
            logger.info(f"Executing step {i + 1}/{len(self.steps)}: {step['name']}")

            try:
                step_result = await self._execute_step(step)
                result["steps"].append({
                    **step,
                    "status": "success",
                    "result": step_result
                })
            except Exception as e:
                logger.error(f"Step '{step['name']}' failed: {str(e)}")
                result["steps"].append({
                    **step,
                    "status": "error",
                    "error": str(e)
                })
                result["status"] = "failed"
                break

        logger.info(f"Pipeline '{self.name}' completed with status: {result['status']}")

        return result

    async def _execute_step(self, step: Dict[str, Any]) -> Any:
        """
        执行单个步骤

        Args:
            step: 步骤信息

        Returns:
            执行结果
        """
        agent = AgentFactory.get_agent(step["agent_type"])
        if not agent:
            agent = AgentFactory.create_agent(step["agent_type"])

        task = Task(
            id=create_task_id(),
            type=step["name"],
            data=step["task_data"]
        )

        return await agent.process_task(task)


class WorkflowManager:
    """
    工作流管理器

    管理和执行多个工作流
    """

    def __init__(self):
        self.pipelines: Dict[str, WorkflowPipeline] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def create_pipeline(self, name: str) -> WorkflowPipeline:
        """
        创建新的工作流流水线

        Args:
            name: 流水线名称

        Returns:
            WorkflowPipeline实例
        """
        pipeline = WorkflowPipeline(name)
        self.pipelines[name] = pipeline
        logger.info(f"Created pipeline: {name}")
        return pipeline

    def get_pipeline(self, name: str) -> Optional[WorkflowPipeline]:
        """
        获取已创建的流水线

        Args:
            name: 流水线名称

        Returns:
            WorkflowPipeline实例或None
        """
        return self.pipelines.get(name)

    async def execute_pipeline(self, name: str) -> Dict[str, Any]:
        """
        执行指定名称的流水线

        Args:
            name: 流水线名称

        Returns:
            执行结果
        """
        pipeline = self.get_pipeline(name)
        if not pipeline:
            raise ValueError(f"Pipeline '{name}' not found")

        result = await pipeline.execute()

        self.execution_history.append({
            "pipeline": name,
            "result": result,
            "timestamp": str(asyncio.get_event_loop().time())
        })

        return result

    async def create_and_run_full_workflow(self) -> Dict[str, Any]:
        """
        创建并运行完整工作流

        Returns:
            执行结果
        """
        pipeline = self.create_pipeline("full_workflow")

        pipeline.add_step(
            step_name="generate_prompts",
            agent_type="content_writer",
            task_data={"count": 3}
        )

        pipeline.add_step(
            step_name="generate_videos",
            agent_type="video_generator",
            task_data={"prompts": "{{prev.prompts}}"}
        )

        pipeline.add_step(
            step_name="upload_videos",
            agent_type="platform_uploader",
            task_data={"platforms": ["douyin"]}
        )

        return await self.execute_pipeline("full_workflow")

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取执行历史

        Args:
            limit: 限制数量

        Returns:
            历史记录列表
        """
        return self.execution_history[-limit:]

    def clear_history(self):
        """清空执行历史"""
        self.execution_history.clear()
        logger.info("Workflow execution history cleared")


class AsyncTaskQueue:
    """
    异步任务队列

    管理异步任务的队列和执行
    """

    def __init__(self, max_workers: int = 5):
        self.queue = asyncio.Queue()
        self.max_workers = max_workers
        self.workers: List[asyncio.Task] = []
        self.is_running = False

    async def put(self, task: Task):
        """
        添加任务到队列

        Args:
            task: 任务对象
        """
        await self.queue.put(task)
        logger.debug(f"Task {task.id} added to queue")

    async def get(self) -> Optional[Task]:
        """
        从队列获取任务

        Returns:
            任务对象或None
        """
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None

    async def start(self):
        """启动任务队列处理器"""
        if self.is_running:
            logger.warning("Task queue already running")
            return

        self.is_running = True
        logger.info(f"Starting task queue with {self.max_workers} workers")

        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)

    async def stop(self):
        """停止任务队列处理器"""
        logger.info("Stopping task queue")

        self.is_running = False

        for worker in self.workers:
            worker.cancel()

        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

        logger.info("Task queue stopped")

    async def _worker(self, worker_name: str):
        """
        工作协程

        Args:
            worker_name: 工作协程名称
        """
        logger.info(f"Worker {worker_name} started")

        while self.is_running:
            task = await self.get()
            if task:
                try:
                    agent_type = task.data.get("agent_type")
                    agent = AgentFactory.get_agent(agent_type)

                    if agent:
                        await agent.process_task(task)
                    else:
                        logger.warning(f"Agent {agent_type} not found for task {task.id}")

                except Exception as e:
                    logger.error(f"Worker {worker_name} error: {str(e)}")

        logger.info(f"Worker {worker_name} stopped")

    def size(self) -> int:
        """获取队列大小"""
        return self.queue.qsize()


def create_full_workflow_pipeline() -> WorkflowPipeline:
    """
    创建完整的视频生成工作流

    Returns:
        WorkflowPipeline实例
    """
    pipeline = WorkflowPipeline("ninja_video_full")

    pipeline.add_step(
        step_name="generate_prompts",
        agent_type="content_writer",
        task_data={
            "count": 3,
            "category": "battle",
            "theme": "epic anime battle scene"
        }
    )

    pipeline.add_step(
        step_name="generate_videos",
        agent_type="video_generator",
        task_data={"skip_existing": True}
    )

    return pipeline


def create_upload_pipeline(video_paths: List[str]) -> WorkflowPipeline:
    """
    创建上传工作流

    Args:
        video_paths: 视频路径列表

    Returns:
        WorkflowPipeline实例
    """
    pipeline = WorkflowPipeline("ninja_video_upload")

    pipeline.add_step(
        step_name="upload_videos",
        agent_type="platform_uploader",
        task_data={
            "videos": video_paths,
            "platforms": ["douyin"]
        }
    )

    return pipeline
