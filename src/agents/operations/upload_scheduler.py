#!/usr/bin/env python3
"""
上传调度器

功能：
- 定时发布任务管理
- 发布频率控制
- 任务队列管理
- 失败重试
"""

import sys
from pathlib import Path
import time
import logging
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"      # 待执行
    SCHEDULED = "scheduled"  # 已调度
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"       # 失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class PublishTask:
    """发布任务"""
    task_id: str
    video_id: str
    platform: str
    scheduled_time: datetime
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None
    callback_args: tuple = field(default_factory=tuple)
    callback_kwargs: dict = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'video_id': self.video_id,
            'platform': self.platform,
            'scheduled_time': self.scheduled_time.isoformat(),
            'status': self.status.value,
            'retry_count': self.retry_count,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }


class PublishConfig:
    """发布配置"""
    def __init__(
        self,
        max_concurrent: int = 3,
        check_interval: int = 60,
        optimal_hours: List[int] = None,
        max_daily: int = 3,
        min_interval: int = 1800,
        auto_retry: bool = True,
        max_retries: int = 3,
        retry_interval: int = 300
    ):
        self.max_concurrent = max_concurrent
        self.check_interval = check_interval
        self.optimal_hours = optimal_hours or [9, 12, 18, 20, 21]
        self.max_daily = max_daily
        self.min_interval = min_interval
        self.auto_retry = auto_retry
        self.max_retries = max_retries
        self.retry_interval = retry_interval


class UploadScheduler:
    """上传调度器"""
    
    def __init__(self, config = None):
        """
        初始化调度器
        
        Args:
            config: 发布配置 (可以是 PublishConfig 或其他兼容配置)
        """
        self.config = config or PublishConfig()
        
        # 任务队列
        self.task_queue: Queue = Queue()
        self.scheduled_tasks: Dict[str, PublishTask] = {}
        
        # 状态
        self.is_running = False
        self.last_check = datetime.now()
        
        # 线程池 - 灵活获取 max_concurrent
        max_workers = getattr(self.config, 'max_concurrent', 3)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 调度线程
        self.scheduler_thread: Optional[threading.Thread] = None
        
        logger.info("UploadScheduler 初始化完成")
    
    def schedule(
        self,
        video_info,
        platform: str,
        scheduled_time: datetime = None,
        callback: Callable = None,
        *callback_args,
        **callback_kwargs
    ) -> str:
        """
        调度一个发布任务
        
        Args:
            video_info: 视频信息
            platform: 发布平台
            scheduled_time: 调度时间（None表示立即）
            callback: 完成后回调
            callback_args: 回调参数
            callback_kwargs: 回调关键字参数
            
        Returns:
            任务ID
        """
        # 生成任务ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{video_info.id}"
        
        # 确定调度时间
        if not scheduled_time:
            scheduled_time = datetime.now()
        
        # 创建任务
        task = PublishTask(
            task_id=task_id,
            video_id=video_info.id,
            platform=platform,
            scheduled_time=scheduled_time,
            callback=callback,
            callback_args=callback_args,
            callback_kwargs=callback_kwargs
        )
        
        # 如果是立即执行，加入队列
        if scheduled_time <= datetime.now():
            self.task_queue.put(task)
            task.status = TaskStatus.PENDING
            logger.info(f"添加任务到队列: {task_id}")
        else:
            # 延迟执行，添加到调度字典
            self.scheduled_tasks[task_id] = task
            task.status = TaskStatus.SCHEDULED
            logger.info(f"调度任务: {task_id} @ {scheduled_time}")
        
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.scheduled_tasks:
            task = self.scheduled_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            del self.scheduled_tasks[task_id]
            logger.info(f"取消任务: {task_id}")
            return True
        return False
    
    def process_queue(self):
        """处理任务队列"""
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                
                if task.status == TaskStatus.CANCELLED:
                    continue
                
                # 执行任务
                task.status = TaskStatus.RUNNING
                success = self._execute_task(task)
                
                if success:
                    task.status = TaskStatus.COMPLETED
                    logger.info(f"任务完成: {task_id}")
                else:
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = TaskStatus.PENDING
                        # 重新加入队列（延迟重试）
                        if self.config.auto_retry:
                            retry_time = datetime.now() + timedelta(
                                seconds=self.config.retry_interval
                            )
                            self.schedule(
                                task.video_id,
                                task.platform,
                                scheduled_time=retry_time
                            )
                    else:
                        task.status = TaskStatus.FAILED
                        logger.error(f"任务失败: {task_id} - {task.error_message}")
                
                # 执行回调
                if task.callback and task.status == TaskStatus.COMPLETED:
                    try:
                        task.callback(*task.callback_args, **task.callback_kwargs)
                    except Exception as e:
                        logger.error(f"回调执行失败: {e}")
                
            except Empty:
                break
            except Exception as e:
                logger.error(f"处理任务队列失败: {e}")
    
    def _execute_task(self, task: PublishTask) -> bool:
        """执行单个任务（模板方法）"""
        try:
            # TODO: 实现实际的发布逻辑
            # 这里应该调用平台的发布API
            
            # 模拟执行
            time.sleep(1)
            
            logger.info(f"执行任务: {task.task_id} - {task.platform}")
            
            return True  # 返回成功/失败
            
        except Exception as e:
            task.error_message = str(e)
            logger.error(f"执行任务失败: {task.task_id} - {e}")
            return False
    
    def check_scheduled_tasks(self):
        """检查定时任务"""
        now = datetime.now()
        
        # 检查是否有任务需要执行
        for task_id, task in list(self.scheduled_tasks.items()):
            if task.status == TaskStatus.SCHEDULED and task.scheduled_time <= now:
                # 加入执行队列
                del self.scheduled_tasks[task_id]
                self.task_queue.put(task)
                task.status = TaskStatus.PENDING
                logger.info(f"触发定时任务: {task_id}")
    
    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已在运行")
            return
        
        self.is_running = True
        
        # 启动调度线程
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True
        )
        self.scheduler_thread.start()
        
        logger.info("UploadScheduler 已启动")
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("UploadScheduler 已停止")
    
    def _scheduler_loop(self):
        """调度主循环"""
        while self.is_running:
            try:
                # 检查定时任务
                self.check_scheduled_tasks()
                
                # 处理队列
                self.process_queue()
                
                # 等待
                time.sleep(self.config.check_interval)
                
            except Exception as e:
                logger.error(f"调度循环出错: {e}")
                time.sleep(5)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            'pending_count': self.task_queue.qsize(),
            'scheduled_count': len(self.scheduled_tasks),
            'is_running': self.is_running,
            'last_check': self.last_check.isoformat()
        }
    
    def get_scheduled_tasks(self) -> List[Dict]:
        """获取所有定时任务"""
        return [
            task.to_dict()
            for task in self.scheduled_tasks.values()
            if task.status == TaskStatus.SCHEDULED
        ]
