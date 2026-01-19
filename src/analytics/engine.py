"""
数据分析模块

提供视频性能分析和优化建议
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsEngine:
    """
    数据分析引擎

    分析视频性能数据并提供优化建议
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path("data/analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.prompt_performance_file = self.data_dir / "prompt_performance.json"
        self.video_stats_file = self.data_dir / "video_stats.json"

        self.prompt_performance = self._load_data(self.prompt_performance_file, {})
        self.video_stats = self._load_data(self.video_stats_file, {})

        logger.info(f"AnalyticsEngine initialized (data_dir: {self.data_dir})")

    def _load_data(self, file_path: Path, default: Any) -> Any:
        """加载数据"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load data from {file_path}: {str(e)}")
        return default

    def _save_data(self, file_path: Path, data: Any):
        """保存数据"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save data to {file_path}: {str(e)}")

    def record_video_performance(
        self,
        video_id: str,
        prompt: str,
        platform: str,
        metrics: Dict[str, Any]
    ):
        """
        记录视频性能数据

        Args:
            video_id: 视频ID
            prompt: 提示词
            platform: 平台
            metrics: 性能指标（views, likes, comments, shares）
        """
        if video_id not in self.video_stats:
            self.video_stats[video_id] = {
                "prompt": prompt,
                "platform": platform,
                "metrics": [],
                "first_published": None,
                "last_updated": None
            }

        self.video_stats[video_id]["metrics"].append({
            **metrics,
            "timestamp": datetime.now().isoformat()
        })

        if not self.video_stats[video_id]["first_published"]:
            self.video_stats[video_id]["first_published"] = datetime.now().isoformat()

        self.video_stats[video_id]["last_updated"] = datetime.now().isoformat()

        self._save_data(self.video_stats_file, self.video_stats)

        logger.info(f"Recorded performance for video {video_id}")

    def analyze_prompt_performance(self, prompt: str) -> Dict[str, Any]:
        """
        分析提示词性能

        Args:
            prompt: 提示词

        Returns:
            分析结果
        """
        matching_videos = [
            (vid_id, data)
            for vid_id, data in self.video_stats.items()
            if data.get("prompt") == prompt
        ]

        if not matching_videos:
            return {
                "prompt": prompt,
                "video_count": 0,
                "avg_performance": None,
                "recommendation": "No data available"
            }

        total_views = sum(
            max(m.get("views", 0) for m in video["metrics"])
            for _, video in matching_videos
        )

        total_likes = sum(
            max(m.get("likes", 0) for m in video["metrics"])
            for _, video in matching_videos
        )

        total_comments = sum(
            max(m.get("comments", 0) for m in video["metrics"])
            for _, video in matching_videos
        )

        video_count = len(matching_videos)
        avg_views = total_views / video_count
        avg_likes = total_likes / video_count
        avg_comments = total_comments / video_count

        avg_engagement = 0.0
        if avg_views > 0:
            avg_engagement = ((avg_likes + avg_comments) / avg_views) * 100

        recommendation = "Continue using this prompt"
        if avg_engagement > 5:
            recommendation = "High performing prompt, generate similar content"
        elif avg_engagement < 1:
            recommendation = "Low performing prompt, consider changing style"

        return {
            "prompt": prompt,
            "video_count": video_count,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_engagement_rate": avg_engagement,
            "recommendation": recommendation
        }

    def get_top_performing_prompts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取表现最好的提示词

        Args:
            limit: 返回数量限制

        Returns:
            提示词列表（按表现排序）
        """
        prompt_performances = {}

        for video_id, data in self.video_stats.items():
            prompt = data.get("prompt")
            if not prompt:
                continue

            if prompt not in prompt_performances:
                prompt_performances[prompt] = {
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "video_count": 0
                }

            latest_metrics = data["metrics"][-1] if data["metrics"] else {}

            prompt_performances[prompt]["views"] += latest_metrics.get("views", 0)
            prompt_performances[prompt]["likes"] += latest_metrics.get("likes", 0)
            prompt_performances[prompt]["comments"] += latest_metrics.get("comments", 0)
            prompt_performances[prompt]["video_count"] += 1

        ranked_prompts = sorted(
            [
                {
                    "prompt": prompt,
                    "total_views": perf["views"],
                    "total_likes": perf["likes"],
                    "total_comments": perf["comments"],
                    "video_count": perf["video_count"],
                    "avg_engagement_rate": (
                        ((perf["likes"] + perf["comments"]) / perf["views"] * 100)
                        if perf["views"] > 0 else 0
                    )
                }
                for prompt, perf in prompt_performances.items()
            ],
            key=lambda x: x["avg_engagement_rate"],
            reverse=True
        )

        return ranked_prompts[:limit]

    def get_platform_stats(self) -> Dict[str, Any]:
        """
        获取平台统计

        Returns:
            平台统计数据
        """
        stats = {}

        for video_id, data in self.video_stats.items():
            platform = data.get("platform", "unknown")
            latest_metrics = data["metrics"][-1] if data["metrics"] else {}

            if platform not in stats:
                stats[platform] = {
                    "video_count": 0,
                    "total_views": 0,
                    "total_likes": 0,
                    "total_comments": 0
                }

            stats[platform]["video_count"] += 1
            stats[platform]["total_views"] += latest_metrics.get("views", 0)
            stats[platform]["total_likes"] += latest_metrics.get("likes", 0)
            stats[platform]["total_comments"] += latest_metrics.get("comments", 0)

        for platform in stats:
            video_count = stats[platform]["video_count"]
            stats[platform]["avg_views"] = (
                stats[platform]["total_views"] / video_count
                if video_count > 0 else 0
            )
            stats[platform]["avg_engagement_rate"] = (
                ((stats[platform]["total_likes"] + stats[platform]["total_comments"]) /
                 stats[platform]["total_views"] * 100)
                if stats[platform]["total_views"] > 0 else 0
            )

        return stats

    def generate_report(self) -> Dict[str, Any]:
        """
        生成分析报告

        Returns:
            分析报告
        """
        return {
            "generated_at": datetime.now().isoformat(),
            "total_videos": len(self.video_stats),
            "top_prompts": self.get_top_performing_prompts(5),
            "platform_stats": self.get_platform_stats(),
            "summary": {
                "total_views": sum(
                    data["metrics"][-1].get("views", 0)
                    for data in self.video_stats.values()
                    if data["metrics"]
                ),
                "total_likes": sum(
                    data["metrics"][-1].get("likes", 0)
                    for data in self.video_stats.values()
                    if data["metrics"]
                ),
                "total_comments": sum(
                    data["metrics"][-1].get("comments", 0)
                    for data in self.video_stats.values()
                    if data["metrics"]
                )
            }
        }
