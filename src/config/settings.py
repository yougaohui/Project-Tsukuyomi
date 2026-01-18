"""
全局配置文件
"""
import os
from pathlib import Path
from typing import List

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# ==================== CogVideoX-3 配置 ====================
COGVIDEO_API_KEY = os.getenv("COGVIDEO_API_KEY", "")
COGVIDEO_MODEL = "cogvideox-3"
COGVIDEO_DEFAULT_QUALITY = "quality"  # quality / speed
COGVIDEO_DEFAULT_SIZE = "1920x1080"  # 支持最高4K
COGVIDEO_DEFAULT_FPS = 30  # 30 / 60
COGVIDEO_WITH_AUDIO = True

# 生成超时时间（秒）
COGVIDEO_GENERATION_TIMEOUT = 600  # 10分钟
COGVIDEO_RETRIEVE_TIMEOUT = 60  # 1分钟
COGVIDEO_MAX_RETRIES = 3

# ==================== 抖音配置 ====================
DOUYIN_COOKIE = os.getenv("DOUYIN_COOKIE", "")
DOUYIN_USER_ID = os.getenv("DOUYIN_USER_ID", "")
DOUYIN_API_BASE = "https://creator.douyin.com"

# 上传配置
DOUYIN_VIDEO_MAX_SIZE = 500 * 1024 * 1024  # 500MB
DOUYIN_VIDEO_MAX_DURATION = 15 * 60  # 15分钟
DOUYIN_VIDEO_MIN_DURATION = 3  # 3秒

# 话题标签
DOUYIN_DEFAULT_TOPICS = [
    "#火影忍者",
    "#动漫",
    "#AI视频",
    "#二次元"
]

# 默认视频描述模板
DOUYIN_DEFAULT_DESCRIPTION = """
{prompt}

🔥 AI 生成视频，原创二创内容
⚡️ 每日更新精彩内容
💖 点赞关注不迷路
"""

# ==================== 路径配置 ====================
DATA_DIR = BASE_DIR / "data"
VIDEO_DIR = DATA_DIR / "videos"  # 生成的原始视频
PROCESSED_DIR = DATA_DIR / "processed"  # 处理后的视频
UPLOADED_DIR = DATA_DIR / "uploaded"  # 已上传的视频
WATERMARK_DIR = DATA_DIR / "watermarks"  # 水印素材
MUSIC_DIR = DATA_DIR / "music"  # 背景音乐
LOGS_DIR = BASE_DIR / "logs"

# 确保目录存在
for dir_path in [VIDEO_DIR, PROCESSED_DIR, UPLOADED_DIR, WATERMARK_DIR, MUSIC_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ==================== 视频处理配置 ====================
# 水印配置
WATERMARK_ENABLED = True
WATERMARK_POSITION = ("right", "bottom")  # 位置
WATERMARK_OPACITY = 0.7  # 透明度 0-1
WATERMARK_DURATION = 5  # 水印显示时长（秒），None表示全程显示

# 字幕配置
SUBTITLE_ENABLED = True
SUBTITLE_FONT_SIZE = 50
SUBTITLE_COLOR = "white"
SUBTITLE_POSITION = "center"

# 视频裁剪配置
VIDEO_CROP_ENABLED = True
VIDEO_MAX_DURATION = 60  # 最长60秒
VIDEO_MIN_DURATION = 15  # 最短15秒

# 背景音乐配置
MUSIC_ENABLED = True
MUSIC_VOLUME = 0.3  # 背景音乐音量 0-1
MUSIC_FADE_DURATION = 2  # 淡入淡出时长（秒）

# ==================== 调度配置 ====================
SCHEDULER_ENABLED = True

# 视频生成时间（支持多个时间点）
GENERATE_SCHEDULE = [
    "10:00",  # 上午10点
    "15:00",  # 下午3点
]

# 视频发布时间（支持多个时间点）
UPLOAD_SCHEDULE = [
    "20:00",  # 晚上8点
]

# 任务执行间隔（秒）
TASK_CHECK_INTERVAL = 60

# ==================== 日志配置 ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志文件
LOG_FILE = LOGS_DIR / "app.log"
LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 5

# ==================== 错误处理配置 ====================
# 最大重试次数
MAX_RETRIES = 3

# 重试间隔（秒）
RETRY_INTERVAL = 5

# 错误通知配置
ERROR_NOTIFICATION_ENABLED = False
ERROR_NOTIFICATION_EMAIL = os.getenv("ERROR_NOTIFICATION_EMAIL", "")

# ==================== 性能配置 ====================
# 并发生成视频数量（限制）
MAX_CONCURRENT_GENERATIONS = 2

# 并发上传数量（限制）
MAX_CONCURRENT_UPLOADS = 1

# 临时文件清理（天）
TEMP_FILE_RETENTION_DAYS = 7

# ==================== 开发配置 ====================
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 测试模式（不上传，只生成）
TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"

# 生成数量限制（测试用）
MAX_GENERATIONS_PER_RUN = 1 if TEST_MODE else 10

# ==================== 成本控制 ====================
# 每日最大生成数量限制
MAX_DAILY_GENERATIONS = 20

# 每日最大上传数量限制
MAX_DAILY_UPLOADS = 20

# 生成成本阈值（美元）
DAILY_COST_LIMIT = 10.0
