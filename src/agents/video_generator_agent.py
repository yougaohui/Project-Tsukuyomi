"""
视频生成Agent

负责调用AI生成视频，并进行质量检测和后处理
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio

from src.agents.base_agent import BaseAgent, Task
from src.video_generator.cogvideo_client import CogVideoClient
from src.video_processor.editor import VideoEditor
from src.config.settings import (
    COGVIDEO_DEFAULT_QUALITY,
    COGVIDEO_DEFAULT_SIZE,
    COGVIDEO_DEFAULT_FPS,
    COGVIDEO_WITH_AUDIO,
    VIDEO_DIR,
    PROCESSED_DIR
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoGeneratorAgent(BaseAgent):
    """
    视频生成Agent

    负责使用CogVideoX-3生成视频，并进行质量检测和后处理
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("video_generator", config)

        self.video_client = CogVideoClient()
        self.video_editor = VideoEditor()

        self.max_concurrent_generations = config.get("max_concurrent", 3) if config else 3
        self.enable_post_process = config.get("enable_post_process", True) if config else True
        self.enable_quality_check = config.get("enable_quality_check", True) if config else True

        logger.info(
            f"VideoGeneratorAgent initialized "
            f"(max_concurrent: {self.max_concurrent_generations}, "
            f"post_process: {self.enable_post_process}, "
            f"quality_check: {self.enable_quality_check})"
        )

    async def execute(self, task: Task) -> Dict[str, Any]:
        """
        执行视频生成任务

        Args:
            task: 任务数据，包含：
                - prompts: 提示词列表
                - output_dir: 输出目录（可选）
                - skip_existing: 是否跳过已存在（可选）
                - config: 生成配置（可选）

        Returns:
            生成的视频信息列表
        """
        params = task.data
        prompts = params.get("prompts", [])
        output_dir = Path(params.get("output_dir", VIDEO_DIR))
        skip_existing = params.get("skip_existing", False)
        gen_config = params.get("config", {})

        if not prompts:
            raise ValueError("No prompts provided")

        logger.info(f"Generating {len(prompts)} videos")

        results = await self._generate_videos(
            prompts=prompts,
            output_dir=output_dir,
            skip_existing=skip_existing,
            config=gen_config
        )

        success_count = sum(1 for r in results if r.get("status") == "success")
        logger.info(f"Video generation completed: {success_count}/{len(prompts)} successful")

        return {
            "results": results,
            "total": len(prompts),
            "successful": success_count,
            "failed": len(prompts) - success_count
        }

    async def _generate_videos(
        self,
        prompts: List[str],
        output_dir: Path,
        skip_existing: bool,
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        批量生成视频

        Args:
            prompts: 提示词列表
            output_dir: 输出目录
            skip_existing: 是否跳过已存在
            config: 生成配置

        Returns:
            生成结果列表
        """
        semaphore = asyncio.Semaphore(self.max_concurrent_generations)
        results = []

        tasks = [
            self._generate_single_video(
                prompt=prompt,
                index=i,
                output_dir=output_dir,
                skip_existing=skip_existing,
                config=config,
                semaphore=semaphore
            )
            for i, prompt in enumerate(prompts)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "index": i,
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        return processed_results

    async def _generate_single_video(
        self,
        prompt: str,
        index: int,
        output_dir: Path,
        skip_existing: bool,
        config: Dict[str, Any],
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """
        生成单个视频

        Args:
            prompt: 提示词
            index: 索引
            output_dir: 输出目录
            skip_existing: 是否跳过已存在
            config: 生成配置
            semaphore: 并发信号量

        Returns:
            生成结果
        """
        async with semaphore:
            logger.info(f"[{index + 1}] Generating video for prompt: {prompt[:50]}...")

            try:
                output_dir.mkdir(parents=True, exist_ok=True)

                filename = f"video_{index + 1}.mp4"
                output_path = output_dir / filename

                if skip_existing and output_path.exists():
                    logger.info(f"[{index + 1}] Video already exists, skipping")
                    return {
                        "index": index,
                        "status": "skipped",
                        "path": str(output_path),
                        "prompt": prompt
                    }

                video_path = await asyncio.to_thread(
                    self.video_client.generate_video_and_download,
                    prompt=prompt,
                    output_dir=output_dir,
                    filename=filename,
                    quality=config.get("quality", COGVIDEO_DEFAULT_QUALITY),
                    size=config.get("size", COGVIDEO_DEFAULT_SIZE),
                    fps=config.get("fps", COGVIDEO_DEFAULT_FPS),
                    with_audio=config.get("with_audio", COGVIDEO_WITH_AUDIO)
                )

                if self.enable_quality_check:
                    quality_passed = await asyncio.to_thread(
                        self._check_video_quality,
                        video_path
                    )

                    if not quality_passed:
                        return {
                            "index": index,
                            "status": "failed",
                            "prompt": prompt,
                            "error": "Quality check failed"
                        }

                processed_path = video_path
                if self.enable_post_process:
                    processed_path = await asyncio.to_thread(
                        self._post_process_video,
                        video_path
                    )

                logger.info(f"[{index + 1}] Video generated successfully")

                return {
                    "index": index,
                    "status": "success",
                    "path": str(processed_path),
                    "prompt": prompt,
                    "original_path": str(video_path),
                    "post_processed": self.enable_post_process
                }

            except Exception as e:
                logger.error(f"[{index + 1}] Failed to generate video: {str(e)}")
                return {
                    "index": index,
                    "status": "error",
                    "prompt": prompt,
                    "error": str(e)
                }

    def _check_video_quality(self, video_path: Path) -> bool:
        """
        检查视频质量

        Args:
            video_path: 视频路径

        Returns:
            是否通过质量检查
        """
        try:
            import moviepy.editor as mp
            video = mp.VideoFileClip(str(video_path))

            duration = video.duration
            fps = video.fps

            video.close()

            if duration < 1.0:
                logger.warning(f"Video too short: {duration}s")
                return False

            if fps < 10:
                logger.warning(f"Video fps too low: {fps}")
                return False

            return True

        except Exception as e:
            logger.error(f"Quality check failed: {str(e)}")
            return False

    def _post_process_video(self, video_path: Path) -> Path:
        """
        后处理视频

        Args:
            video_path: 原始视频路径

        Returns:
            处理后的视频路径
        """
        try:
            PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

            output_filename = video_path.stem + "_processed.mp4"
            output_path = PROCESSED_DIR / output_filename

            logger.info(f"Post-processing video: {video_path.name}")

            self.video_editor.process_video(
                input_path=video_path,
                output_path=output_path
            )

            logger.info(f"Video processed successfully: {output_filename}")

            return output_path

        except Exception as e:
            logger.error(f"Post-processing failed: {str(e)}")
            return video_path

    async def generate_single_video(
        self,
        prompt: str,
        output_dir: Optional[Path] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成单个视频的便捷方法

        Args:
            prompt: 提示词
            output_dir: 输出目录
            **kwargs: 其他参数

        Returns:
            生成结果
        """
        task = Task(
            id=self.create_task_id(),
            type="generate_single",
            data={
                "prompts": [prompt],
                "output_dir": output_dir or VIDEO_DIR,
                "config": kwargs
            }
        )

        return await self.execute(task)
