"""
AI Agent基类和核心模块

该模块定义了所有Agent的基类，提供统一的接口和功能
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgentStatus(Enum):
    """Agent状态枚举"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    PAUSED = "paused"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Task:
    """任务数据结构"""
    id: str
    type: str
    data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "priority": self.priority.name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }


@dataclass
class AgentMetrics:
    """Agent性能指标"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_task_duration: float = 0.0
    total_duration: float = 0.0

    def update_success(self, duration: float):
        """更新成功任务指标"""
        self.total_tasks += 1
        self.completed_tasks += 1
        self.total_duration += duration
        self.avg_task_duration = self.total_duration / self.completed_tasks

    def update_failure(self):
        """更新失败任务指标"""
        self.total_tasks += 1
        self.failed_tasks += 1

    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100


class BaseAgent(ABC):
    """
    Agent基类

    所有Agent都必须继承此类，实现核心的execute方法
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化Agent

        Args:
            name: Agent名称
            config: 配置字典
        """
        self.name = name
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()
        self.current_task: Optional[Task] = None
        self._task_queue: asyncio.Queue = asyncio.Queue()

        logger.info(f"Agent '{self.name}' initialized")

    @abstractmethod
    async def execute(self, task: Task) -> Any:
        """
        执行任务的核心方法，子类必须实现

        Args:
            task: 要执行的任务

        Returns:
            执行结果
        """
        pass

    async def process_task(self, task: Task) -> Any:
        """
        处理单个任务的完整流程

        Args:
            task: 要处理的任务

        Returns:
            处理结果
        """
        self.status = AgentStatus.BUSY
        self.current_task = task
        task.status = "processing"
        task.started_at = datetime.now()

        start_time = datetime.now()

        try:
            logger.info(f"Agent '{self.name}' executing task {task.id}")

            result = await self.execute(task)

            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = result

            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.update_success(duration)

            logger.info(f"Task {task.id} completed successfully in {duration:.2f}s")

            return result

        except Exception as e:
            logger.error(f"Task {task.id} failed: {str(e)}")

            task.status = "failed"
            task.completed_at = datetime.now()
            task.error = str(e)

            self.metrics.update_failure()

            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = "retrying"
                logger.warning(f"Retrying task {task.id} (attempt {task.retry_count}/{task.max_retries})")
                await asyncio.sleep(2 ** task.retry_count)
                return await self.process_task(task)
            else:
                self.status = AgentStatus.ERROR
                raise

        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None

    async def add_task(self, task: Task):
        """
        添加任务到队列

        Args:
            task: 要添加的任务
        """
        await self._task_queue.put(task)
        logger.debug(f"Task {task.id} added to queue for agent '{self.name}'")

    async def get_task(self) -> Optional[Task]:
        """
        从队列获取任务

        Returns:
            任务对象或None
        """
        try:
            return await asyncio.wait_for(self._task_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None

    async def run(self):
        """
        持续运行Agent，处理队列中的任务
        """
        logger.info(f"Agent '{self.name}' started")

        while True:
            if self.status == AgentStatus.PAUSED:
                await asyncio.sleep(1)
                continue

            task = await self.get_task()
            if task:
                await self.process_task(task)

    def pause(self):
        """暂停Agent"""
        self.status = AgentStatus.PAUSED
        logger.info(f"Agent '{self.name}' paused")

    def resume(self):
        """恢复Agent"""
        if self.status == AgentStatus.PAUSED:
            self.status = AgentStatus.IDLE
            logger.info(f"Agent '{self.name}' resumed")

    def get_status(self) -> Dict[str, Any]:
        """
        获取Agent状态信息

        Returns:
            状态字典
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "metrics": {
                "total_tasks": self.metrics.total_tasks,
                "completed_tasks": self.metrics.completed_tasks,
                "failed_tasks": self.metrics.failed_tasks,
                "success_rate": f"{self.metrics.get_success_rate():.2f}%",
                "avg_task_duration": f"{self.metrics.avg_task_duration:.2f}s"
            },
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "queue_size": self._task_queue.qsize()
        }

    async def shutdown(self):
        """关闭Agent"""
        logger.info(f"Agent '{self.name}' shutting down")
        self.status = AgentStatus.PAUSED

        while not self._task_queue.empty():
            try:
                task = self._task_queue.get_nowait()
                logger.warning(f"Task {task.id} cancelled during shutdown")
            except asyncio.QueueEmpty:
                break


class AgentFactory:
    """
    Agent工厂类

    负责创建和管理各种Agent实例
    """

    _agents: Dict[str, BaseAgent] = {}

    @classmethod
    def create_agent(cls, agent_type: str, config: Optional[Dict[str, Any]] = None) -> BaseAgent:
        """
        创建Agent实例

        Args:
            agent_type: Agent类型 (content_writer, video_generator, platform_uploader, team_manager)
            config: 配置字典

        Returns:
            Agent实例
        """
        if agent_type in cls._agents:
            return cls._agents[agent_type]

        from .content_writer_agent import ContentWriterAgent
        from .video_generator_agent import VideoGeneratorAgent
        from .platform_uploader_agent import PlatformUploaderAgent
        from .team_manager_agent import TeamManagerAgent

        agent_classes = {
            "content_writer": ContentWriterAgent,
            "video_generator": VideoGeneratorAgent,
            "platform_uploader": PlatformUploaderAgent,
            "team_manager": TeamManagerAgent
        }

        if agent_type not in agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent = agent_classes[agent_type](config=config)
        cls._agents[agent_type] = agent

        logger.info(f"Created agent of type '{agent_type}'")
        return agent

    @classmethod
    def get_agent(cls, agent_type: str) -> Optional[BaseAgent]:
        """
        获取已创建的Agent实例

        Args:
            agent_type: Agent类型

        Returns:
            Agent实例或None
        """
        return cls._agents.get(agent_type)

    @classmethod
    def list_agents(cls) -> List[str]:
        """
        列出所有已创建的Agent

        Returns:
            Agent类型列表
        """
        return list(cls._agents.keys())

    @classmethod
    async def shutdown_all(cls):
        """关闭所有Agent"""
        for agent in cls._agents.values():
            await agent.shutdown()
        cls._agents.clear()
        logger.info("All agents shut down")


def create_task_id() -> str:
    """生成唯一的任务ID"""
    import uuid
    return str(uuid.uuid4())
