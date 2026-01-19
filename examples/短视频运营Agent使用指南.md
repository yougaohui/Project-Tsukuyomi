# 短视频自动化运营 Agent 使用指南

## 📋 目录

- [简介](#简介)
- [功能特性](#功能特性)
- [安装依赖](#安装依赖)
- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [使用示例](#使用示例)
- [配置文件](#配置文件)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 🎯 简介

短视频自动化运营 Agent 是一个专业级的短视频自动化运营系统，支持多平台账号管理、智能调度发布、数据统计分析等功能。

### 适用场景

- ✅ 短视频创作者（抖音、快手、B站等）
- ✅ MCN 机构（批量运营多个账号）
- ✅ 内容运营团队（定时发布、内容管理）
- ✅ 个人博主（自动化运维）

---

## ✨ 功能特性

### 🤖 智能调度
- 定时发布（指定时间）
- 最佳时段发布（黄金时段自动选择）
- 分散发布（多平台同步发布）
- 频率控制（避免限流）

### 📊 多平台支持
- 抖音（douyin）
- 快手（kuaishou）
- B站（bilibili）
- 小红书（xiaohongshu）
- TikTok（tiktok）
- Instagram（instagram）

### 📁 内容管理
- 视频文件管理
- 分类和标签
- 发布历史记录
- 状态跟踪

### 📈 数据统计
- 发布统计（成功/失败）
- 平台分布
- 每日趋势
- 失败分析

### ⚡ 自动化运维
- 自动重试（失败自动重试）
- 异常恢复（错误处理）
- 任务队列（可靠的任务管理）
- 定时任务（调度发布）

---

## 📦 安装依赖

```bash
# 核心依赖（Python 3.8+）
pip install -r requirements.txt

# 主要依赖：
# - requests: HTTP 请求
# - python-dotenv: 环境变量
# - APScheduler: 定时任务
# - loguru: 日志系统
```

---

## 🚀 快速开始

### 1. 准备配置文件

创建 `agent_config.json`：

```json
{
  "publish_config": {
    "strategy": "optimal",
    "platforms": ["douyin"],
    "optimal_hours": [9, 12, 18, 20, 21],
    "max_daily_publish": 5,
    "auto_retry": true,
    "max_retries": 3
  },
  "accounts": [
    {
      "platform": "douyin",
      "account_id": "your_id",
      "nickname": "你的抖音号",
      "cookie": "你的Cookie"
    }
  ]
}
```

### 2. 基础使用

```python
from src.agents.operations import VideoOperationsAgent
from src.agents.operations.video_operations_agent import Platform

# 创建 Agent
agent = VideoOperationsAgent()

# 加载视频
agent.load_videos(Path("data/videos"))

# 发布视频
agent.publish_video(
    video_id="vid_xxx",
    platform=Platform.DOUYIN
)
```

### 3. 命令行使用

```bash
# 查看状态
python -m examples.短视频运营Agent使用示例.py --status

# 加载视频并发布
python -m examples.短视频运营Agent使用示例.py --load data/videos --publish vid_xxx

# 定时发布
python -m examples.短视频运营Agent使用示例.py --schedule
```

---

## 📖 核心概念

### VideoInfo（视频信息）

```python
@dataclass
class VideoInfo:
    id: str                    # 唯一标识
    title: str                 # 标题
    description: str           # 描述
    file_path: Path           # 文件路径
    duration: int             # 时长（秒）
    size: int                # 文件大小
    category: str = ""        # 分类
    tags: List[str] = []     # 标签
    topics: List[str] = []   # 话题
    status: VideoStatus       # 状态
```

### PublishStrategy（发布策略）

```python
class PublishStrategy(Enum):
    IMMEDIATE = "immediate"    # 立即发布
    SCHEDULED = "scheduled"    # 定时发布
    OPTIMAL = "optimal"        # 最佳时段发布
    DISTRIBUTED = "distributed" # 分散发布
```

### VideoStatus（视频状态）

```python
class VideoStatus(Enum):
    PENDING = "pending"       # 待处理
    PROCESSING = "processing" # 处理中
    UPLOADING = "uploading"   # 上传中
    UPLOADED = "uploaded"     # 已上传
    PUBLISHED = "published"   # 已发布
    FAILED = "failed"         # 失败
    SCHEDULED = "scheduled"   # 已调度
```

---

## 💡 使用示例

### 示例 1: 加载并发布视频

```python
from pathlib import Path
from src.agents.operations import VideoOperationsAgent
from src.agents.operations.video_operations_agent import Platform

# 创建 Agent
agent = VideoOperationsAgent()

# 加载视频目录
agent.load_videos(Path("data/videos"))

# 发布第一个视频
if agent.video_queue:
    video = agent.video_queue[0]
    result = agent.publish_video(
        video_id=video.id,
        platform=Platform.DOUYIN
    )
    print(result)
```

### 示例 2: 定时发布到最佳时段

```python
agent = VideoOperationsAgent()
agent.load_videos(Path("data/videos"))

# 调度到最佳时段发布
agent.schedule_all(
    platform=Platform.DOUYIN,
    strategy=PublishStrategy.OPTIMAL
)
```

### 示例 3: 批量发布

```python
agent = VideoOperationsAgent()
agent.load_videos(Path("data/videos"))

# 批量发布到多个平台
results = agent.batch_publish(
    video_ids=None,  # None 表示发布所有待发布视频
    platform=Platform.DOUYIN,
    strategy=PublishStrategy.OPTIMAL
)
print(f"成功: {sum(1 for r in results if r['success'])}/{len(results)}")
```

### 示例 4: 查看统计数据

```python
agent = VideoOperationsAgent()
agent.load_videos(Path("data/videos"))

# 获取统计
stats = agent.get_statistics()
print(json.dumps(stats, indent=2, ensure_ascii=False))
```

---

## ⚙️ 配置文件

### 结构说明

```json
{
  "publish_config": {
    "strategy": "optimal",           // 发布策略
    "platforms": ["douyin"],         // 目标平台
    "optimal_hours": [9, 12, 18, 20, 21],  // 黄金时段
    "max_daily_publish": 5,          // 每日最大发布数
    "min_interval": 3600,            // 最小间隔（秒）
    "auto_retry": true,              // 自动重试
    "max_retries": 3,                // 最大重试次数
    "retry_interval": 600            // 重试间隔（秒）
  },
  "accounts": [
    {
      "platform": "douyin",          // 平台
      "account_id": "xxx",           // 账号ID
      "nickname": "名称",            // 昵称
      "cookie": "xxx",               // Cookie
      "token": "",                  // Token（可选）
      "daily_limit": 10             // 每日发布上限
    }
  ]
}
```

### 平台配置

每个平台需要配置：
- **Cookie 认证**：复制浏览器中的 Cookie
- **Token 认证**：使用 OAuth 2.0 获取的 Token
- **每日限制**：避免触发平台限流

---

## 🎯 最佳实践

### 1. 发布频率控制

```python
# 推荐配置
config = PublishConfig(
    max_daily=5,              # 每天最多5个
    min_interval=3600,         # 间隔至少1小时
    optimal_hours=[9, 12, 18, 20, 21]  // 黄金时段
)
```

### 2. 标签优化

```python
video = agent.add_video(
    file_path=Path("video.mp4"),
    title="精彩内容",
    tags=["热门", "推荐", "最新"],
    topics=["#热门", "#推荐"]
)
```

### 3. 定时发布

```python
from datetime import datetime, timedelta

# 发布到明天晚上8点
scheduled_time = datetime.now().replace(hour=20, minute=0) + timedelta(days=1)

agent.add_video(
    file_path=Path("video.mp4"),
    title="定时发布",
    scheduled_time=scheduled_time
)
```

### 4. 多平台同步

```python
# 创建支持多平台的配置
config = PublishConfig(
    platforms=[Platform.DOUYIN, Platform.KUAISHOU, Platform.BILIBILI]
)

agent = VideoOperationsAgent(config=config)

# 分散发布
agent.publish_video(
    video_id="xxx",
    strategy=PublishStrategy.DISTRIBUTED
)
```

---

## ❓ 常见问题

### Q1: Cookie 如何获取？

1. 打开抖音创作者中心
2. 按 F12 打开开发者工具
3. 复制 Request Headers 中的 Cookie
4. 粘贴到配置文件中

### Q2: 发布失败怎么办？

- **自动重试**：配置 `auto_retry: true`
- **手动重试**：调用 `publish_video` 方法
- **检查日志**：查看 `logs/` 目录下的日志文件

### Q3: 如何避免限流？

- 控制发布频率（`max_daily`）
- 使用最佳时段（`optimal_hours`）
- 间隔发布（`min_interval`）

### Q4: 支持哪些平台？

当前支持：
- 抖音（douyin）
- 快手（kuaishou）
- B站（bilibili）
- 小红书（xiaohongshu）

计划支持：
- TikTok
- Instagram
- YouTube

### Q5: 如何查看运行状态？

```python
agent = VideoOperationsAgent()
status = agent.get_status()
print(json.dumps(status, indent=2))
```

---

## 📚 相关文档

- [API 文档](#)
- [配置文件说明](#)
- [最佳实践指南](#)
- [常见问题解答](#)

---

**版本**: 1.0.0  
**更新时间**: 2024-01-19  
**作者**: AI Assistant
