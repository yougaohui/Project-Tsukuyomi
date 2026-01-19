#!/usr/bin/env python3
"""
短视频自动化运营 Agent
专业级的短视频自动化运营系统

功能特性：
- 🤖 智能调度：定时发布、频率控制、黄金时段
- 📊 多平台支持：抖音、快手、B站、小红书
- 📁 内容管理：视频整理、分类、排序
- 🔄 自动化流程：上传、发布、互动
- 📈 数据统计：播放量、点赞、评论分析
- ⚡ 错误处理：自动重试、异常恢复
- 🎯 发布策略：标签优化、话题选择、描述生成
"""

import sys
import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

# 导入子模块
from .account_manager import AccountManager, AccountConfig
from .upload_scheduler import UploadScheduler, PublishConfig

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import (
    VIDEO_DIR, PROCESSED_DIR, UPLOADED_DIR,
    LOG_LEVEL, LOGS_DIR
)
from src.utils.logger import setup_logger

logger = setup_logger("video_operations", LOG_LEVEL)


class Platform(Enum):
    """支持的短视频平台"""
    DOUYIN = "douyin"           # 抖音
    KUAISHOU = "kuaishou"       # 快手
    BILIBILI = "bilibili"       # B站
    XIAOHONGSHU = "xiaohongshu" # 小红书
    INSTAGRAM = "instagram"     # Instagram
    TIKTOK = "tiktok"           # TikTok


class VideoStatus(Enum):
    """视频状态"""
    PENDING = "pending"         # 待处理
    PROCESSING = "processing"   # 处理中
    UPLOADING = "uploading"     # 上传中
    UPLOADED = "uploaded"       # 已上传
    PUBLISHED = "published"     # 已发布
    FAILED = "failed"           # 失败
    SCHEDULED = "scheduled"     # 已调度


class PublishStrategy(Enum):
    """发布策略"""
    IMMEDIATE = "immediate"     # 立即发布
    SCHEDULED = "scheduled"     # 定时发布
    OPTIMAL = "optimal"         # 最佳时段
    DISTRIBUTED = "distributed" # 分散发布


@dataclass
class VideoInfo:
    """视频信息"""
    id: str
    title: str
    description: str
    file_path: Path
    duration: int  # 时长（秒）
    size: int      # 文件大小（字节）
    category: str = ""
    tags: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    status: VideoStatus = VideoStatus.PENDING
    platform: Optional[Platform] = None
    scheduled_time: Optional[datetime] = None
    published_time: Optional[datetime] = None
    video_id: Optional[str] = None  # 平台返回的视频ID
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_path': str(self.file_path),
            'duration': self.duration,
            'size': self.size,
            'category': self.category,
            'tags': self.tags,
            'topics': self.topics,
            'status': self.status.value,
            'platform': self.platform.value if self.platform else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'published_time': self.published_time.isoformat() if self.published_time else None,
            'video_id': self.video_id,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VideoInfo':
        """从字典创建"""
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            file_path=Path(data['file_path']),
            duration=data['duration'],
            size=data['size'],
            category=data.get('category', ''),
            tags=data.get('tags', []),
            topics=data.get('topics', []),
            status=VideoStatus(data['status']),
            platform=Platform(data['platform']) if data.get('platform') else None,
            scheduled_time=datetime.fromisoformat(data['scheduled_time']) if data.get('scheduled_time') else None,
            published_time=datetime.fromisoformat(data['published_time']) if data.get('published_time') else None,
            video_id=data.get('video_id'),
            error_message=data.get('error_message'),
            retry_count=data.get('retry_count', 0),
            metadata=data.get('metadata', {})
        )


@dataclass
class PublishConfig:
    """发布配置"""
    strategy: PublishStrategy = PublishStrategy.OPTIMAL
    platforms: List[Platform] = field(default_factory=lambda: [Platform.DOUYIN])
    optimal_hours: List[int] = field(default_factory=lambda: [9, 12, 18, 20, 21])  # 黄金时段
    max_daily_publish: int = 3  # 每日最大发布数
    min_interval: int = 1800    # 最小间隔（30分钟）
    auto_retry: bool = True
    max_retries: int = 3
    retry_interval: int = 300   # 重试间隔（5分钟）
    auto_tags: bool = True
    auto_topics: bool = True


class VideoOperationsAgent:
    """
    短视频自动化运营 Agent
    
    核心功能：
    - 视频内容管理
    - 多平台账号管理
    - 智能调度发布
    - 数据统计分析
    - 自动化运维
    """
    
    def __init__(
        self,
        config: Optional[PublishConfig] = None,
        account_manager: Optional[AccountManager] = None,
        scheduler: Optional[UploadScheduler] = None
    ):
        """
        初始化 VideoOperationsAgent
        
        Args:
            config: 发布配置
            account_manager: 账号管理器
            scheduler: 调度器
        """
        self.config = config or PublishConfig()
        self.account_manager = account_manager or AccountManager()
        self.scheduler = scheduler or UploadScheduler(self.config)
        
        # 视频库
        self.video_queue: List[VideoInfo] = []
        self.video_history: List[VideoInfo] = []
        
        # 统计数据
        self.stats = {
            'total_videos': 0,
            'published_videos': 0,
            'failed_videos': 0,
            'total_publishes': 0,
            'platform_stats': {},
            'daily_stats': {}
        }
        
        # 状态
        self.is_running = False
        self.last_update = datetime.now()
        
        logger.info("VideoOperationsAgent 初始化完成")
        logger.info(f"配置: {self.config}")
    
    def load_videos(self, directory: Path = None) -> int:
        """
        加载视频到队列
        
        Args:
            directory: 视频目录
            
        Returns:
            加载的视频数量
        """
        video_dir = directory or VIDEO_DIR
        
        if not video_dir.exists():
            logger.warning(f"视频目录不存在: {video_dir}")
            return 0
        
        # 支持的视频格式
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        
        # 查找视频
        videos = []
        for ext in video_extensions:
            videos.extend(video_dir.glob(f"**/*{ext}"))
        
        # 去重
        videos = list(set(videos))
        
        logger.info(f"找到 {len(videos)} 个视频文件")
        
        # 创建 VideoInfo
        for video_path in videos:
            video_info = self._create_video_info(video_path)
            if video_info:
                self.video_queue.append(video_info)
                self.stats['total_videos'] += 1
        
        logger.info(f"加载了 {len(self.video_queue)} 个视频到队列")
        return len(self.video_queue)
    
    def _create_video_info(self, file_path: Path) -> Optional[VideoInfo]:
        """创建视频信息对象"""
        try:
            # 获取文件信息
            stat = file_path.stat()
            
            # 生成唯一ID
            video_id = f"vid_{int(stat.st_mtime)}_{file_path.stem}"
            
            # 创建 VideoInfo
            video_info = VideoInfo(
                id=video_id,
                title=file_path.stem,
                description="",
                file_path=file_path,
                duration=0,  # TODO: 获取视频时长
                size=stat.st_size,
                status=VideoStatus.PENDING
            )
            
            return video_info
            
        except Exception as e:
            logger.error(f"创建视频信息失败: {file_path} - {e}")
            return None
    
    def add_video(
        self,
        file_path: Path,
        title: str,
        description: str = "",
        category: str = "",
        tags: List[str] = None,
        topics: List[str] = None,
        scheduled_time: Optional[datetime] = None
    ) -> Optional[VideoInfo]:
        """
        添加单个视频到队列
        
        Args:
            file_path: 视频文件路径
            title: 标题
            description: 描述
            category: 分类
            tags: 标签
            topics: 话题
            scheduled_time: 定时发布时间
            
        Returns:
            VideoInfo 对象
        """
        if not file_path.exists():
            logger.error(f"视频文件不存在: {file_path}")
            return None
        
        # 创建视频信息
        video_info = self._create_video_info(file_path)
        if not video_info:
            return None
        
        # 设置属性
        video_info.title = title
        video_info.description = description
        video_info.category = category
        video_info.tags = tags or []
        video_info.topics = topics or []
        video_info.scheduled_time = scheduled_time
        
        # 根据调度策略设置状态
        if scheduled_time:
            video_info.status = VideoStatus.SCHEDULED
        else:
            video_info.status = VideoStatus.PENDING
        
        # 添加到队列
        self.video_queue.append(video_info)
        self.stats['total_videos'] += 1
        
        logger.info(f"添加视频到队列: {title}")
        return video_info
    
    def publish_video(
        self,
        video_id: str,
        platform: Platform = Platform.DOUYIN,
        strategy: PublishStrategy = None
    ) -> Dict[str, Any]:
        """
        发布单个视频
        
        Args:
            video_id: 视频ID
            platform: 发布平台
            strategy: 发布策略
            
        Returns:
            发布结果
        """
        strategy = strategy or PublishStrategy.IMMEDIATE
        
        # 查找视频
        video = self._find_video_by_id(video_id)
        if not video:
            return {'success': False, 'error': '视频不存在'}
        
        logger.info(f"开始发布视频: {video.title} -> {platform.value}")
        
        try:
            # 更新状态
            video.status = VideoStatus.UPLOADING
            
            # 获取平台配置
            account = self.account_manager.get_account(platform)
            if not account:
                raise Exception(f"未配置 {platform.value} 账号")
            
            # 根据策略处理
            if strategy == PublishStrategy.IMMEDIATE:
                # 立即发布
                result = self._publish_to_platform(video, platform)
                
            elif strategy == PublishStrategy.SCHEDULED:
                # 定时发布
                if not video.scheduled_time:
                    video.scheduled_time = datetime.now() + timedelta(hours=1)
                self.scheduler.schedule(video, platform)
                result = {'success': True, 'message': '已添加到定时队列'}
                
            elif strategy == PublishStrategy.OPTIMAL:
                # 最佳时段发布
                optimal_time = self._get_optimal_publish_time()
                video.scheduled_time = optimal_time
                self.scheduler.schedule(video, platform)
                result = {'success': True, 'message': f'已调度到最佳时段: {optimal_time}'}
                
            elif strategy == PublishStrategy.DISTRIBUTED:
                # 分散发布
                result = self._publish_distributed(video)
            else:
                raise Exception(f"不支持的发布策略: {strategy}")
            
            # 更新统计数据
            if result.get('success'):
                video.status = VideoStatus.PUBLISHED
                video.published_time = datetime.now()
                video.platform = platform
                self.stats['published_videos'] += 1
                self._update_platform_stats(platform, True)
            else:
                video.status = VideoStatus.FAILED
                video.error_message = result.get('error')
                self.stats['failed_videos'] += 1
                self._update_platform_stats(platform, False)
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"发布视频失败: {video.title} - {error_msg}")
            
            video.status = VideoStatus.FAILED
            video.error_message = error_msg
            self.stats['failed_videos'] += 1
            
            # 自动重试
            if self.config.auto_retry and video.retry_count < self.config.max_retries:
                video.retry_count += 1
                video.status = VideoStatus.PENDING
                logger.info(f"安排重试 ({video.retry_count}/{self.config.max_retries})")
                return self.publish_video(video_id, platform, strategy)
            
            return {'success': False, 'error': error_msg}
    
    def _publish_to_platform(
        self,
        video: VideoInfo,
        platform: Platform
    ) -> Dict[str, Any]:
        """发布视频到指定平台"""
        logger.info(f"上传视频到 {platform.value}: {video.title}")
        
        # TODO: 实现具体的上传逻辑
        # 这里可以调用各个平台的上传API
        
        # 模拟上传过程
        time.sleep(2)  # 模拟上传时间
        
        # 返回成功结果（实际应该调用平台API）
        return {
            'success': True,
            'platform': platform.value,
            'video_id': f"{platform.value}_{video.id}",
            'published_time': datetime.now().isoformat(),
            'message': f'成功发布到 {platform.value}'
        }
    
    def _publish_distributed(self, video: VideoInfo) -> Dict[str, Any]:
        """分散发布到多个平台"""
        results = []
        
        for platform in self.config.platforms:
            if platform == video.platform:
                continue  # 跳过已发布的平台
            
            result = self._publish_to_platform(video, platform)
            results.append({
                'platform': platform.value,
                'success': result.get('success', False),
                'message': result.get('message', '')
            })
        
        return {
            'success': True,
            'distributed_results': results,
            'message': f'分散发布完成，共 {len(results)} 个平台'
        }
    
    def batch_publish(
        self,
        video_ids: List[str] = None,
        platform: Platform = Platform.DOUYIN,
        strategy: PublishStrategy = None
    ) -> List[Dict[str, Any]]:
        """
        批量发布视频
        
        Args:
            video_ids: 视频ID列表（None表示发布所有待发布视频）
            platform: 发布平台
            strategy: 发布策略
            
        Returns:
            发布结果列表
        """
        strategy = strategy or PublishStrategy.OPTIMAL
        
        # 确定要发布的视频
        if video_ids:
            videos = [self._find_video_by_id(vid) for vid in video_ids]
            videos = [v for v in videos if v]  # 过滤None
        else:
            videos = [v for v in self.video_queue if v.status == VideoStatus.PENDING]
        
        if not videos:
            logger.warning("没有可发布的视频")
            return []
        
        logger.info(f"开始批量发布 {len(videos)} 个视频")
        
        # 并发发布（限制并发数）
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.publish_video, v.id, platform, strategy): v
                for v in videos
            }
            
            for future in as_completed(futures):
                video = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'video_id': video.id,
                        'success': False,
                        'error': str(e)
                    })
        
        # 统计结果
        success_count = sum(1 for r in results if r.get('success'))
        logger.info(f"批量发布完成: {success_count}/{len(results)} 成功")
        
        return results
    
    def schedule_all(
        self,
        platform: Platform = Platform.DOUYIN,
        strategy: PublishStrategy = PublishStrategy.OPTIMAL
    ) -> int:
        """
        将所有待发布视频调度到最佳时段
        
        Args:
            platform: 发布平台
            strategy: 调度策略
            
        Returns:
            调度的视频数量
        """
        scheduled_count = 0
        
        for video in self.video_queue:
            if video.status == VideoStatus.PENDING:
                # 计算最佳发布时间
                if strategy == PublishStrategy.OPTIMAL:
                    optimal_time = self._get_optimal_publish_time()
                    video.scheduled_time = optimal_time
                else:
                    video.scheduled_time = datetime.now() + timedelta(hours=scheduled_count * 2)
                
                # 添加到调度器
                self.scheduler.schedule(video, platform)
                video.status = VideoStatus.SCHEDULED
                scheduled_count += 1
        
        logger.info(f"已调度 {scheduled_count} 个视频到发布队列")
        return scheduled_count
    
    def _get_optimal_publish_time(self) -> datetime:
        """获取最佳发布时间"""
        now = datetime.now()
        
        # 查找下一个黄金时段
        for hour in self.config.optimal_hours:
            if hour > now.hour:
                optimal = now.replace(
                    hour=hour,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                return optimal
        
        # 如果今天时段已过，返回明天第一个时段
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(
            hour=self.config.optimal_hours[0],
            minute=0,
            second=0,
            microsecond=0
        )
    
    def _find_video_by_id(self, video_id: str) -> Optional[VideoInfo]:
        """根据ID查找视频"""
        for video in self.video_queue:
            if video.id == video_id:
                return video
        return None
    
    def _update_platform_stats(self, platform: Platform, success: bool):
        """更新平台统计数据"""
        platform_name = platform.value
        
        if platform_name not in self.stats['platform_stats']:
            self.stats['platform_stats'][platform_name] = {
                'total': 0,
                'success': 0,
                'failed': 0
            }
        
        self.stats['platform_stats'][platform_name]['total'] += 1
        if success:
            self.stats['platform_stats'][platform_name]['success'] += 1
        else:
            self.stats['platform_stats'][platform_name]['failed'] += 1
    
    def get_status(self) -> Dict[str, Any]:
        """获取 Agent 状态"""
        return {
            'is_running': self.is_running,
            'queue_size': len(self.video_queue),
            'history_size': len(self.video_history),
            'stats': self.stats,
            'config': {
                'strategy': self.config.strategy.value,
                'platforms': [p.value for p in self.config.platforms],
                'optimal_hours': self.config.optimal_hours,
                'max_daily_publish': self.config.max_daily_publish,
                'auto_retry': self.config.auto_retry,
                'max_retries': self.config.max_retries
            },
            'last_update': self.last_update.isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取详细统计信息"""
        return {
            'overview': self.stats,
            'platforms': self.stats['platform_stats'],
            'video_queue': [v.to_dict() for v in self.video_queue],
            'recentublished': [
                v.to_dict() for v in self.video_history[-10:]
                if v.status == VideoStatus.PUBLISHED
            ]
        }
    
    def export_config(self, file_path: Path):
        """导出配置"""
        config_data = {
            'publish_config': {
                'strategy': self.config.strategy.value,
                'platforms': [p.value for p in self.config.platforms],
                'optimal_hours': self.config.optimal_hours,
                'max_daily_publish': self.config.max_daily_publish,
                'min_interval': self.config.min_interval,
                'auto_retry': self.config.auto_retry,
                'max_retries': self.config.max_retries,
                'retry_interval': self.config.retry_interval
            },
            'accounts': self.account_manager.get_all_accounts(),
            'scheduled_videos': [
                {
                    'video_id': v.id,
                    'scheduled_time': v.scheduled_time.isoformat() if v.scheduled_time else None,
                    'platform': v.platform.value if v.platform else None
                }
                for v in self.video_queue
                if v.status == VideoStatus.SCHEDULED
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置已导出到: {file_path}")
    
    def import_config(self, file_path: Path):
        """导入配置"""
        if not file_path.exists():
            logger.error(f"配置文件不存在: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 恢复配置
        if 'publish_config' in config_data:
            pc = config_data['publish_config']
            self.config.strategy = PublishStrategy(pc.get('strategy', 'optimal'))
            self.config.optimal_hours = pc.get('optimal_hours', [9, 12, 18, 20, 21])
            self.config.max_daily_publish = pc.get('max_daily_publish', 3)
            self.config.auto_retry = pc.get('auto_retry', True)
            self.config.max_retries = pc.get('max_retries', 3)
        
        logger.info(f"配置已导入: {file_path}")
        return True
    
    def start(self):
        """启动 Agent"""
        if self.is_running:
            logger.warning("Agent 已在运行中")
            return
        
        self.is_running = True
        self.last_update = datetime.now()
        
        logger.info("短视频运营 Agent 已启动")
        
        # 启动调度器
        self.scheduler.start()
    
    def stop(self):
        """停止 Agent"""
        self.is_running = False
        
        # 停止调度器
        self.scheduler.stop()
        
        # 保存状态
        self.last_update = datetime.now()
        
        logger.info("短视频运营 Agent 已停止")
    
    def run_once(self):
        """运行一次（用于测试）"""
        self.start()
        
        # 处理调度队列中的视频
        self.scheduler.process_queue()
        
        self.stop()


def main():
    """主函数 - 测试运行"""
    import argparse
    
    parser = argparse.ArgumentParser(description="短视频自动化运营 Agent")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--export", type=str, help="导出配置到文件")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--stats", action="store_true", help="显示统计")
    parser.add_argument("--load", type=str, help="加载视频目录")
    parser.add_argument("--publish", type=str, help="发布视频（视频ID，多个用逗号分隔）")
    parser.add_argument("--schedule", action="store_true", help="调度所有待发布视频")
    parser.add_argument("--run-once", action="store_true", help="运行一次后退出")
    
    args = parser.parse_args()
    
    # 创建 Agent
    agent = VideoOperationsAgent()
    
    try:
        # 加载配置
        if args.config:
            agent.import_config(Path(args.config))
        
        # 加载视频
        if args.load:
            agent.load_videos(Path(args.load))
        
        # 显示状态
        if args.status:
            status = agent.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # 显示统计
        if args.stats:
            stats = agent.get_statistics()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        # 发布视频
        if args.publish:
            video_ids = args.publish.split(',')
            results = agent.batch_publish(video_ids)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # 调度视频
        if args.schedule:
            count = agent.schedule_all()
            print(f"已调度 {count} 个视频")
        
        # 运行一次
        if args.run_once:
            agent.run_once()
        
        # 导出配置
        if args.export:
            agent.export_config(Path(args.export))
        
        # 默认：显示状态
        if not any([args.config, args.export, args.status, args.stats, 
                   args.load, args.publish, args.schedule, args.run_once]):
            status = agent.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
    
    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.error(f"运行失败: {e}")
        raise


if __name__ == "__main__":
    main()
