"""
LLM服务集成

支持多种大语言模型服务（OpenAI、智谱AI等）
"""
from abc import ABC, abstractmethod
from typing import Optional
import httpx
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseLLMService(ABC):
    """LLM服务基类"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            max_tokens: 最大token数

        Returns:
            生成的文本
        """
        pass


class OpenAIService(BaseLLMService):
    """OpenAI GPT服务"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key)
        self.model = model

        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info(f"OpenAI service initialized (model: {model})")
        except ImportError:
            logger.warning("OpenAI package not installed, install with: pip install openai")
            raise

    async def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """
        使用OpenAI生成文本

        Args:
            prompt: 提示词
            max_tokens: 最大token数

        Returns:
            生成的文本
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise


class ZhipuAIService(BaseLLMService):
    """智谱AI GLM服务"""

    def __init__(self, api_key: str, model: str = "glm-4"):
        super().__init__(api_key)
        self.model = model

        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=api_key)
            logger.info(f"ZhipuAI service initialized (model: {model})")
        except ImportError:
            logger.warning("ZhipuAI package not installed, install with: pip install zhipuai")
            raise

    async def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """
        使用智谱AI生成文本

        Args:
            prompt: 提示词
            max_tokens: 最大token数

        Returns:
            生成的文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"ZhipuAI generation failed: {str(e)}")
            raise


class MockLLMService(BaseLLMService):
    """
    Mock LLM服务（用于测试）

    返回简单的模拟响应
    """

    def __init__(self, api_key: str = "mock"):
        super().__init__(api_key)
        logger.info("Mock LLM service initialized")

    async def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """
        生成模拟响应

        Args:
            prompt: 提示词
            max_tokens: 最大token数

        Returns:
            模拟的文本
        """
        import random

        mock_responses = [
            "Epic anime scene with dramatic lighting and intense action",
            "Beautiful Naruto character with glowing chakra effects",
            "Intense battle scene with jutsu explosions",
            "Emotional character moment with sunset background",
            "Powerful ninja showcasing their unique abilities"
        ]

        return random.choice(mock_responses)


def create_llm_service(service_type: str, api_key: Optional[str] = None) -> BaseLLMService:
    """
    创建LLM服务实例

    Args:
        service_type: 服务类型 (openai, zhipuai, mock)
        api_key: API密钥

    Returns:
        LLM服务实例
    """
    if service_type == "openai":
        if not api_key:
            raise ValueError("OpenAI API key is required")
        return OpenAIService(api_key)
    elif service_type == "zhipuai":
        if not api_key:
            raise ValueError("ZhipuAI API key is required")
        return ZhipuAIService(api_key)
    elif service_type == "mock":
        return MockLLMService()
    else:
        raise ValueError(f"Unsupported service type: {service_type}")
