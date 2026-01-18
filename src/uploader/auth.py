"""
抖音认证管理
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
import requests

from src.config.settings import (
    DOUYIN_COOKIE,
    DOUYIN_USER_ID,
    DOUYIN_API_BASE,
    LOGS_DIR
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DouyinAuth:
    """抖音认证管理器"""

    def __init__(self, cookie: str = None, user_id: str = None):
        self.cookie = cookie or DOUYIN_COOKIE
        self.user_id = user_id or DOUYIN_USER_ID

        if not self.cookie:
            raise ValueError("DOUYIN_COOKIE is required")

        self.headers = {
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://creator.douyin.com/",
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def test_auth(self) -> bool:
        """
        测试认证是否有效

        Returns:
            认证是否有效
        """
        try:
            url = f"{DOUYIN_API_BASE}/creator-micro/home"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                logger.info("Authentication test successful")
                return True
            else:
                logger.warning(f"Authentication test failed with status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Authentication test error: {str(e)}")
            return False

    def get_user_info(self) -> Dict[str, Any]:
        """
        获取用户信息

        Returns:
            用户信息字典
        """
        try:
            url = f"{DOUYIN_API_BASE}/creator-micro/home"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                raise RuntimeError(f"Failed to get user info: {response.status_code}")

            data = response.json()
            logger.info("User info retrieved successfully")

            return data

        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
            raise

    def save_cookie(self, path: Path = None):
        """
        保存 Cookie 到文件

        Args:
            path: 保存路径
        """
        if path is None:
            path = LOGS_DIR / "cookie.json"

        cookie_data = {
            "cookie": self.cookie,
            "user_id": self.user_id
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cookie_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Cookie saved to {path}")

    @classmethod
    def load_cookie(cls, path: Path = None) -> 'DouyinAuth':
        """
        从文件加载 Cookie

        Args:
            path: Cookie 文件路径

        Returns:
            DouyinAuth 实例
        """
        if path is None:
            path = LOGS_DIR / "cookie.json"

        if not path.exists():
            raise FileNotFoundError(f"Cookie file not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)

        return cls(
            cookie=cookie_data.get("cookie"),
            user_id=cookie_data.get("user_id")
        )

    def update_cookie(self, new_cookie: str):
        """
        更新 Cookie

        Args:
            new_cookie: 新的 Cookie
        """
        self.cookie = new_cookie
        self.headers["Cookie"] = new_cookie
        self.session.headers["Cookie"] = new_cookie

        logger.info("Cookie updated")
