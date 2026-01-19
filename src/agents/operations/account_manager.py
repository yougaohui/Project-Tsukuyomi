#!/usr/bin/env python3
"""
多平台账号管理器

功能：
- 平台账号配置管理
- Cookie/Token 管理
- 账号状态监控
- 多账号轮询
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class Platform(Enum):
    """支持的平台"""
    DOUYIN = "douyin"
    KUAISHOU = "kuaishou"
    BILIBILI = "bilibili"
    XIAOHONGSHU = "xiaohongshu"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


class AccountStatus(Enum):
    """账号状态"""
    ACTIVE = "active"        # 正常
    EXPIRED = "expired"      # 已过期
    LOCKED = "locked"        # 被锁定
    DISABLED = "disabled"    # 已禁用
    PENDING = "pending"      # 待验证


@dataclass
class AccountConfig:
    """账号配置"""
    platform: Platform
    account_id: str
    nickname: str
    cookie: str = ""
    token: str = ""
    refresh_token: str = ""
    status: AccountStatus = AccountStatus.ACTIVE
    last_verified: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    daily_limit: int = 10  # 每日发布限制
    published_today: int = 0
    rate_limit: int = 100  # 频率限制
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """检查账号是否有效"""
        if self.status != AccountStatus.ACTIVE:
            return False
        
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        
        return True
    
    def can_publish(self) -> bool:
        """检查是否可以发布"""
        return (
            self.is_valid() and 
            self.published_today < self.daily_limit
        )
    
    def increment_publish_count(self):
        """增加发布计数"""
        self.published_today += 1
    
    def reset_daily_count(self):
        """重置每日发布计数"""
        self.published_today = 0


class AccountManager:
    """多平台账号管理器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化
        
        Args:
            config_file: 配置文件路径
        """
        self.accounts: Dict[str, AccountConfig] = {}  # platform_account_id -> config
        self.platforms: Dict[Platform, List[AccountConfig]] = {}
        
        # 加载配置
        if config_file:
            self.load_config(config_file)
        
        logger.info("AccountManager 初始化完成")
    
    def add_account(
        self,
        platform: Platform,
        account_id: str,
        nickname: str,
        cookie: str = "",
        token: str = "",
        daily_limit: int = 10,
        **kwargs
    ) -> AccountConfig:
        """添加账号"""
        key = f"{platform.value}_{account_id}"
        
        account = AccountConfig(
            platform=platform,
            account_id=account_id,
            nickname=nickname,
            cookie=cookie,
            token=token,
            daily_limit=daily_limit,
            **kwargs
        )
        
        self.accounts[key] = account
        
        # 添加到平台列表
        if platform not in self.platforms:
            self.platforms[platform] = []
        self.platforms[platform].append(account)
        
        logger.info(f"添加账号: {platform.value} - {nickname}")
        return account
    
    def get_account(self, platform: Platform, account_id: str = None) -> Optional[AccountConfig]:
        """
        获取账号
        
        Args:
            platform: 平台
            account_id: 账号ID（None则返回第一个可用账号）
            
        Returns:
            AccountConfig 或 None
        """
        if platform not in self.platforms:
            return None
        
        accounts = self.platforms[platform]
        
        if not accounts:
            return None
        
        # 如果没有指定账号，返回第一个可用的
        if not account_id:
            for account in accounts:
                if account.can_publish():
                    return account
            return accounts[0]  # 返回第一个（即使不可用）
        
        # 查找指定账号
        for account in accounts:
            if account.account_id == account_id:
                return account
        
        return None
    
    def get_available_account(self, platform: Platform) -> Optional[AccountConfig]:
        """获取可用账号（支持轮询）"""
        if platform not in self.platforms:
            return None
        
        accounts = self.platforms[platform]
        
        # 查找可用的账号
        for account in accounts:
            if account.can_publish():
                return account
        
        return None
    
    def verify_account(self, platform: Platform, account_id: str = None) -> bool:
        """验证账号"""
        account = self.get_account(platform, account_id)
        if not account:
            return False
        
        # TODO: 实现实际的验证逻辑
        # 检查 Cookie/Token 是否有效
        
        account.last_verified = datetime.now()
        return account.is_valid()
    
    def update_cookie(self, platform: Platform, account_id: str, cookie: str):
        """更新 Cookie"""
        account = self.get_account(platform, account_id)
        if account:
            account.cookie = cookie
            account.last_verified = datetime.now()
            logger.info(f"更新 Cookie: {platform.value} - {account_id}")
    
    def increment_publish_count(self, platform: Platform, account_id: str):
        """增加发布计数"""
        account = self.get_account(platform, account_id)
        if account:
            account.increment_publish_count()
    
    def reset_daily_counts(self):
        """重置所有账号的每日发布计数"""
        for account in self.accounts.values():
            account.reset_daily_count()
        logger.info("已重置所有账号的每日发布计数")
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """获取所有账号信息"""
        return [
            {
                'platform': acc.platform.value,
                'account_id': acc.account_id,
                'nickname': acc.nickname,
                'status': acc.status.value,
                'can_publish': acc.can_publish(),
                'published_today': acc.published_today,
                'daily_limit': acc.daily_limit
            }
            for acc in self.accounts.values()
        ]
    
    def load_config(self, config_file: str):
        """从文件加载配置"""
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for account_data in data.get('accounts', []):
                platform = Platform(account_data['platform'])
                self.add_account(
                    platform=platform,
                    account_id=account_data['account_id'],
                    nickname=account_data['nickname'],
                    cookie=account_data.get('cookie', ''),
                    token=account_data.get('token', ''),
                    daily_limit=account_data.get('daily_limit', 10)
                )
            
            logger.info(f"从 {config_file} 加载了 {len(self.accounts)} 个账号")
            
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
    
    def save_config(self, config_file: str):
        """保存配置到文件"""
        import json
        
        data = {
            'accounts': [
                {
                    'platform': acc.platform.value,
                    'account_id': acc.account_id,
                    'nickname': acc.nickname,
                    'cookie': acc.cookie,
                    'token': acc.token,
                    'daily_limit': acc.daily_limit,
                    'status': acc.status.value
                }
                for acc in self.accounts.values()
            ]
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置已保存到 {config_file}")
