"""
文案策划Agent

负责生成火影忍者主题的视频提示词（Prompt）
"""
import random
from typing import Any, Dict, List, Optional

from src.agents.base_agent import BaseAgent, Task
from src.video_generator.prompt_manager import PromptManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ContentWriterAgent(BaseAgent):
    """
    文案策划Agent

    负责生成火影忍者主题的视频提示词
    支持使用LLM智能生成和现有Prompt库两种模式
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("content_writer", config)

        self.prompt_manager = PromptManager()
        self.use_llm = config.get("use_llm", False) if config else False
        self.llm_config = config.get("llm_config", {}) if config else {}

        logger.info(f"ContentWriterAgent initialized (use_llm: {self.use_llm})")

    async def execute(self, task: Task) -> Dict[str, Any]:
        """
        执行文案生成任务

        Args:
            task: 任务数据，包含生成参数
                - count: 生成数量
                - category: 类别（可选）
                - theme: 主题（可选）
                - style: 风格（可选）
                - use_llm: 是否使用LLM（可选，覆盖默认配置）

        Returns:
            生成的提示词列表
        """
        params = task.data
        count = params.get("count", 1)
        category = params.get("category")
        theme = params.get("theme")
        style = params.get("style")
        use_llm = params.get("use_llm", self.use_llm)

        logger.info(f"Generating {count} prompts (category: {category}, use_llm: {use_llm})")

        prompts = []

        if use_llm:
            prompts = await self._generate_with_llm(
                count=count,
                theme=theme,
                style=style,
                category=category
            )
        else:
            prompts = await self._generate_from_library(
                count=count,
                category=category,
                theme=theme
            )

        logger.info(f"Generated {len(prompts)} prompts successfully")

        return {
            "prompts": prompts,
            "method": "llm" if use_llm else "library",
            "count": len(prompts)
        }

    async def _generate_from_library(
        self,
        count: int,
        category: Optional[str] = None,
        theme: Optional[str] = None
    ) -> List[str]:
        """
        从现有Prompt库生成提示词

        Args:
            count: 生成数量
            category: 类别
            theme: 主题

        Returns:
            提示词列表
        """
        prompts = []

        if theme:
            for i in range(count):
                parts = []

                if theme:
                    parts.append(theme)

                parts.extend([
                    "anime style",
                    "high quality",
                    "epic",
                    "dramatic lighting"
                ])

                prompt = ", ".join(parts)
                prompts.append(prompt)
        else:
            prompts = self.prompt_manager.get_multiple_prompts(count, category)

        return prompts

    async def _generate_with_llm(
        self,
        count: int,
        theme: Optional[str] = None,
        style: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[str]:
        """
        使用LLM智能生成提示词

        Args:
            count: 生成数量
            theme: 主题
            style: 风格
            category: 类别

        Returns:
            提示词列表
        """
        logger.info("Using LLM to generate prompts")

        if not self.llm_config:
            logger.warning("LLM config not provided, falling back to library")
            return await self._generate_from_library(count, category, theme)

        try:
            llm_service = self._get_llm_service()

            prompt_templates = self._get_prompt_templates(theme, category, count)

            prompts = []
            for template in prompt_templates:
                response = await llm_service.generate(
                    prompt=template,
                    max_tokens=200
                )
                prompts.append(response.strip())

            return prompts

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}, falling back to library")
            return await self._generate_from_library(count, category, theme)

    def _get_llm_service(self):
        """获取LLM服务实例"""
        llm_type = self.llm_config.get("type", "openai")

        if llm_type == "openai":
            from src.integrations.llm_service import OpenAIService
            return OpenAIService(api_key=self.llm_config.get("api_key"))
        elif llm_type == "zhipuai":
            from src.integrations.llm_service import ZhipuAIService
            return ZhipuAIService(api_key=self.llm_config.get("api_key"))
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

    def _get_prompt_templates(
        self,
        theme: Optional[str],
        category: Optional[str],
        count: int
    ) -> List[str]:
        """
        获取LLM提示词模板

        Args:
            theme: 主题
            category: 类别
            count: 数量

        Returns:
            提示词模板列表
        """
        base_prompt = "Generate a detailed, creative prompt for an anime-style video about Naruto."

        if category:
            category_prompts = {
                "character": "Focus on a specific character showing their personality and abilities.",
                "jutsu": "Describe a ninja performing a powerful jutsu technique.",
                "scene": "Describe a beautiful, atmospheric location from the Naruto world.",
                "battle": "Describe an intense, epic battle scene.",
                "emotional": "Describe an emotional, character-driven moment."
            }
            base_prompt += f" {category_prompts.get(category, '')}"

        if theme:
            base_prompt += f" The theme is: {theme}."

        base_prompt += " Include details about: visual style, lighting, camera angles, and atmosphere. Return only the prompt text."

        return [base_prompt] * count

    async def optimize_prompt(
        self,
        prompt: str,
        feedback: Optional[str] = None
    ) -> str:
        """
        根据反馈优化提示词

        Args:
            prompt: 原始提示词
            feedback: 反馈信息

        Returns:
            优化后的提示词
        """
        if not feedback:
            return prompt

        logger.info(f"Optimizing prompt based on feedback: {feedback}")

        if self.use_llm:
            try:
                llm_service = self._get_llm_service()

                optimization_prompt = f"""
                Original prompt: {prompt}
                Feedback: {feedback}

                Rewrite the prompt to address the feedback while maintaining the original intent.
                Return only the optimized prompt.
                """

                optimized = await llm_service.generate(
                    prompt=optimization_prompt,
                    max_tokens=200
                )

                return optimized.strip()

            except Exception as e:
                logger.error(f"LLM optimization failed: {str(e)}")

        return prompt

    async def analyze_performance(self, prompt: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析提示词性能

        Args:
            prompt: 提示词
            metrics: 性能指标（播放量、点赞数等）

        Returns:
            分析结果
        """
        logger.info(f"Analyzing performance for prompt: {prompt[:50]}...")

        analysis = {
            "prompt": prompt,
            "metrics": metrics,
            "score": 0.0,
            "recommendations": []
        }

        views = metrics.get("views", 0)
        likes = metrics.get("likes", 0)
        comments = metrics.get("comments", 0)

        if views > 0:
            engagement_rate = (likes + comments) / views
            analysis["score"] = engagement_rate * 100

            if engagement_rate > 0.1:
                analysis["recommendations"].append("High engagement, consider generating similar prompts")
            elif engagement_rate < 0.02:
                analysis["recommendations"].append("Low engagement, try different style or category")

        return analysis

    def get_categories(self) -> List[str]:
        """获取所有提示词类别"""
        return self.prompt_manager.get_all_categories()

    def get_prompt_count(self, category: Optional[str] = None) -> int:
        """获取提示词数量"""
        return self.prompt_manager.get_prompt_count(category)

    def get_multiple_prompts(self, count: int, category: Optional[str] = None) -> List[str]:
        """
        获取多个随机提示词

        Args:
            count: 数量
            category: 类别

        Returns:
            提示词列表
        """
        actual_category = category if category else None
        return self.prompt_manager.get_multiple_prompts(count, actual_category)

    def get_random_prompt(self, category: Optional[str] = None) -> str:
        """
        获取随机提示词

        Args:
            category: 类别

        Returns:
            随机提示词
        """
        return self.prompt_manager.get_random_prompt(category)

    def generate_title(self, prompt: str, category: Optional[str] = None) -> str:
        """
        根据提示词生成标题

        Args:
            prompt: 提示词
            category: 类别

        Returns:
            标题
        """
        category_prefixes = {
            "character": "【角色】",
            "jutsu": "【忍术】",
            "scene": "【场景】",
            "battle": "【战斗】",
            "emotional": "【情感】"
        }

        prefix = category_prefixes.get(category, "【火影忍者】")

        prompt_clean = prompt.replace(",", " ").replace(".", " ").strip()
        words = prompt_clean.split()

        title_words = words[:8]
        title = " ".join(title_words)

        if len(title) > 30:
            title = title[:30] + "..."

        return f"{prefix} {title}"

    def generate_hashtags(self, category: Optional[str] = None) -> List[str]:
        """
        生成话题标签

        Args:
            category: 类别

        Returns:
            话题标签列表
        """
        base_tags = ["#火影忍者", "#Naruto", "#动漫"]

        category_tags = {
            "character": ["#火影忍者角色", "#动漫角色", "#忍者"],
            "jutsu": ["#火影忍术", "#忍术", "#忍界大战"],
            "scene": ["#火影场景", "#动漫风景", "#木叶村"],
            "battle": ["#火影战斗", "#忍术对决", "#热血动漫"],
            "emotional": ["#火影感动", "#动漫情感", "#羁绊"]
        }

        tags = base_tags.copy()
        if category and category in category_tags:
            tags.extend(category_tags[category])

        return tags
