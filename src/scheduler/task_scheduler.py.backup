"""
任务调度器 - 使用 APScheduler 管理定时任务
"""
from datetime import datetime
from typing import Callable, Optional
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.config.settings import (
    SCHEDULER_ENABLED,
    GENERATE_SCHEDULE,
    UPLOAD_SCHEDULE,
    TASK_CHECK_INTERVAL,
    MAX_GENERATIONS_PER_RUN,
    TEST_MODE,
    LOG_LEVEL
)
from src.video_generator.cogvideo_client import CogVideoClient
from src.video_generator.prompt_manager import PromptManager
from src.video_processor.editor import VideoEditor
from src.uploader.douyin_client import DouyinUploader
from src.uploader.auth import DouyinAuth
from src.utils.logger import get_logger
from src.utils.storage import StorageManager

logger = get_logger(__name__)


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.prompt_manager = PromptManager()
        self.video_generator = CogVideoClient()
        self.video_editor = VideoEditor()
        self.storage_manager = StorageManager()

        if not TEST_MODE:
            self.douyin_auth = DouyinAuth()
            self.douyin_uploader = DouyinUploader(self.douyin_auth)
        else:
            self.douyin_uploader = None
            logger.info("Running in test mode, skipping Douyin upload")

    def add_cron_job(
        self,
        func: Callable,
        hour: int,
        minute: int = 0,
        job_id: str = None
    ):
        """
        添加定时任务

        Args:
            func: 要执行的函数
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            job_id: 任务 ID
        """
        trigger = CronTrigger(hour=hour, minute=minute)

        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=f"Task at {hour:02d}:{minute:02d}"
        )

        logger.info(f"Added cron job: {job_id} at {hour:02d}:{minute:02d}")

    def add_interval_job(
        self,
        func: Callable,
        minutes: int,
        job_id: str = None
    ):
        """
        添加间隔任务

        Args:
            func: 要执行的函数
            minutes: 间隔分钟数
            job_id: 任务 ID
        """
        trigger = IntervalTrigger(minutes=minutes)

        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=f"Interval job every {minutes} minutes"
        )

        logger.info(f"Added interval job: {job_id} every {minutes} minutes")

    def generate_videos_task(self):
        """生成视频的任务"""
        logger.info("=" * 50)
        logger.info("Starting video generation task")
        logger.info("=" * 50)

        try:
            num_videos = min(3, MAX_GENERATIONS_PER_RUN)

            prompts = self.prompt_manager.get_multiple_prompts(
                count=num_videos,
                category="battle"
            )

            logger.info(f"Generating {len(prompts)} videos")

            video_paths = self.video_generator.generate_multiple_videos(
                prompts=prompts
            )

            logger.info(f"Successfully generated {len(video_paths)} videos")

            for i, video_path in enumerate(video_paths):
                logger.info(f"Processing video {i + 1}/{len(video_paths)}")

                processed_path = self.video_editor.process_video(
                    video_path=video_path,
                    crop=True,
                    add_watermark_flag=True,
                    add_music_flag=True,
                    subtitle_text=f"火影忍者精彩时刻 #{i+1}"
                )

                self.storage_manager.move_video_to_processed(
                    processed_path,
                    f"naruto_{i+1}.mp4"
                )

        except Exception as e:
            logger.error(f"Video generation task failed: {str(e)}")

    def upload_videos_task(self):
        """上传视频的任务"""
        if TEST_MODE:
            logger.info("Test mode enabled, skipping upload task")
            return

        logger.info("=" * 50)
        logger.info("Starting video upload task")
        logger.info("=" * 50)

        try:
            auth_test = self.douyin_auth.test_auth()
            if not auth_test:
                logger.error("Authentication failed, cannot upload videos")
                return

            video_paths = self.storage_manager.list_videos("processed")
            if not video_paths:
                logger.info("No videos to upload")
                return

            video_info_list = []

            for i, video_path in enumerate(video_paths[:3]):
                prompt = self.prompt_manager.get_random_prompt()

                video_info = {
                    'video_path': video_path,
                    'title': f"火影忍者精彩时刻 {datetime.now().strftime('%Y%m%d')}#{i+1}",
                    'description': f"{prompt}\n\n🔥 AI 生成视频，原创二创内容\n⚡️ 每日更新精彩内容\n💖 点赞关注不迷路",
                    'topics': ["#火影忍者", "#动漫", "#AI视频", "#二次元"]
                }

                video_info_list.append(video_info)

            logger.info(f"Uploading {len(video_info_list)} videos")

            results = self.douyin_uploader.upload_multiple_videos(
                video_info_list=video_info_list,
                delay=30
            )

            success_count = sum(1 for r in results if r.get("status") != "failed")
            logger.info(f"Successfully uploaded {success_count}/{len(video_info_list)} videos")

        except Exception as e:
            logger.error(f"Video upload task failed: {str(e)}")

    def maintenance_task(self):
        """维护任务：清理临时文件"""
        logger.info("=" * 50)
        logger.info("Starting maintenance task")
        logger.info("=" * 50)

        try:
            self.storage_manager.clean_temp_files()
            logger.info("Maintenance task completed")

        except Exception as e:
            logger.error(f"Maintenance task failed: {str(e)}")

    def setup_scheduled_jobs(self):
        """设置所有定时任务"""
        if not SCHEDULER_ENABLED:
            logger.info("Scheduler is disabled")
            return

        for time_str in GENERATE_SCHEDULE:
            hour, minute = map(int, time_str.split(":"))
            self.add_cron_job(
                self.generate_videos_task,
                hour=hour,
                minute=minute,
                job_id=f"generate_{time_str}"
            )

        for time_str in UPLOAD_SCHEDULE:
            hour, minute = map(int, time_str.split(":"))
            self.add_cron_job(
                self.upload_videos_task,
                hour=hour,
                minute=minute,
                job_id=f"upload_{time_str}"
            )

        maintenance_time = "03:00"
        hour, minute = map(int, maintenance_time.split(":"))
        self.add_cron_job(
            self.maintenance_task,
            hour=hour,
            minute=minute,
            job_id="maintenance"
        )

        logger.info("All scheduled jobs configured")

    def run_immediate_generate(self, count: int = 3):
        """
        立即执行生成任务

        Args:
            count: 生成视频数量
        """
        logger.info(f"Running immediate generation for {count} videos")

        original_limit = MAX_GENERATIONS_PER_RUN

        import src.config.settings as settings
        settings.MAX_GENERATIONS_PER_RUN = count

        try:
            self.generate_videos_task()
        finally:
            settings.MAX_GENERATIONS_PER_RUN = original_limit

    def run_immediate_upload(self):
        """立即执行上传任务"""
        logger.info("Running immediate upload")

        self.upload_videos_task()

    def start(self):
        """启动调度器"""
        logger.info("=" * 50)
        logger.info("Starting Task Scheduler")
        logger.info("=" * 50)

        self.setup_scheduled_jobs()

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()

    def print_scheduled_jobs(self):
        """打印所有已安排的任务"""
        jobs = self.scheduler.get_jobs()

        if not jobs:
            print("No scheduled jobs")
            return

        print("\n" + "=" * 50)
        print("Scheduled Jobs")
        print("=" * 50)

        for job in jobs:
            print(f"\nJob ID: {job.id}")
            print(f"Name: {job.name}")
            print(f"Next Run: {job.next_run_time}")
            print(f"Trigger: {job.trigger}")

        print("\n" + "=" * 50 + "\n")
