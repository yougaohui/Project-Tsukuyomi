# 火影忍者视频自动生成与上传系统

使用 CogVideoX-3 AI 模型自动生成火影忍者主题短视频，并自动上传到抖音平台的自动化系统。

## ✨ 功能特性

- 🎬 **AI 视频生成**：使用 CogVideoX-3 模型根据文本描述自动生成高质量视频
- 🎭 **火影忍者主题**：内置丰富的火影忍者 Prompt 库，涵盖角色、技能、场景、战斗、情感等
- ✂️ **智能视频处理**：自动裁剪、添加水印、字幕、背景音乐
- 📤️ **抖音自动上传**：支持 Cookie 认证，自动发布到抖音平台
- ⏰ **定时任务调度**：可配置视频生成和上传的定时任务
- 📊 **存储管理**：自动管理视频文件，清理临时文件
- 🎨 **自定义 Prompt**：支持自定义 Prompt，生成个性化内容

## 📋 系统要求

- Python 3.8+
- FFmpeg（用于视频处理）
- 8GB+ RAM（推荐）
- 稳定网络连接

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下信息：

```bash
# CogVideoX-3 API Key（必填）
# 获取方式：访问 https://z.ai/manage-apikey/apikey-list
COGVIDEO_API_KEY=your-api-key-here

# 抖音 Cookie（必填，用于上传）
# 获取方式：登录 https://creator.douyin.com，在浏览器开发者工具中获取 Cookie
DOUYIN_COOKIE=your-douyin-cookie-here

# 日志级别（可选）
LOG_LEVEL=INFO

# 调试模式（可选）
DEBUG=False

# 测试模式（可选，启用后不上传）
TEST_MODE=True
```

### 3. 获取抖音 Cookie

1. 访问 https://creator.douyin.com 并登录
2. 按 F12 打开开发者工具
3. 切换到 Network 标签
4. 刷新页面，找到任意请求
5. 在请求头中找到 `Cookie` 字段，复制完整内容
6. 粘贴到 `.env` 文件中的 `DOUYIN_COOKIE`

### 4. 运行示例

#### 生成单个视频

```bash
python examples/generate_single.py
```

#### 测试 Prompt 系统

```bash
python examples/test_prompts.py
```

#### 上传视频到抖音

```bash
python examples/upload_video.py
```

## 📖 使用指南

### 启动定时调度器

自动在配置的时间生成和上传视频：

```bash
python main.py --schedule
```

默认配置：
- 视频生成：上午 10:00 和下午 15:00
- 视频上传：晚上 20:00
- 系统维护：凌晨 03:00

可在 `src/config/settings.py` 中修改时间配置。

### 立即生成视频

```bash
# 生成3个视频（默认）
python main.py --generate

# 生成指定数量的视频
python main.py --generate --count 5
```

### 立即上传视频

```bash
python main.py --upload
```

### 查看已安排的任务

```bash
python main.py --list-jobs
```

### 启用调试模式

```bash
python main.py --debug --generate
```

## 📂 项目结构

```
Project-Tsukuyomi/
├── src/                        # 源代码
│   ├── config/                  # 配置模块
│   │   ├── settings.py         # 全局配置
│   │   └── prompts.py          # Prompt 模板
│   ├── video_generator/         # 视频生成模块
│   │   ├── cogvideo_client.py   # CogVideoX-3 客户端
│   │   └── prompt_manager.py    # Prompt 管理器
│   ├── video_processor/          # 视频处理模块
│   │   └── editor.py          # MoviePy 编辑器
│   ├── uploader/                # 上传模块
│   │   ├── auth.py             # 认证管理
│   │   └── douyin_client.py    # 抖音客户端
│   ├── scheduler/               # 调度模块
│   │   └── task_scheduler.py   # 任务调度器
│   └── utils/                  # 工具模块
│       ├── logger.py            # 日志系统
│       └── storage.py          # 存储管理
├── examples/                   # 示例脚本
│   ├── generate_single.py      # 生成单个视频
│   ├── upload_video.py        # 上传视频
│   └── test_prompts.py       # 测试 Prompt
├── data/                       # 数据目录
│   ├── videos/               # 原始视频
│   ├── processed/            # 处理后视频
│   ├── uploaded/             # 已上传视频
│   ├── watermarks/           # 水印素材
│   └── music/               # 背景音乐
├── logs/                       # 日志文件
├── main.py                     # 主程序入口
├── requirements.txt            # 依赖列表
├── .env.example               # 环境变量模板
└── README.md                  # 本文档
```

## ⚙️ 配置说明

### 视频生成配置

在 `src/config/settings.py` 中配置：

```python
# 视频分辨率（支持：1920x1080, 3840x2160）
COGVIDEO_DEFAULT_SIZE = "1920x1080"

# 帧率（30/60）
COGVIDEO_DEFAULT_FPS = 30

# 质量模式（quality/speed）
COGVIDEO_DEFAULT_QUALITY = "quality"

# 是否包含音频
COGVIDEO_WITH_AUDIO = True
```

### 视频处理配置

```python
# 水印配置
WATERMARK_ENABLED = True
WATERMARK_POSITION = ("right", "bottom")
WATERMARK_OPACITY = 0.7

# 字幕配置
SUBTITLE_ENABLED = True
SUBTITLE_FONT_SIZE = 50
SUBTITLE_COLOR = "white"

# 视频裁剪
VIDEO_CROP_ENABLED = True
VIDEO_MAX_DURATION = 60  # 最长60秒
VIDEO_MIN_DURATION = 15  # 最短15秒

# 背景音乐
MUSIC_ENABLED = True
MUSIC_VOLUME = 0.3
```

### 任务调度配置

```python
# 视频生成时间
GENERATE_SCHEDULE = [
    "10:00",  # 上午10点
    "15:00",  # 下午3点
]

# 视频发布时间
UPLOAD_SCHEDULE = [
    "20:00",  # 晚上8点
]
```

## 💰 成本估算

| 项目 | 成本 | 说明 |
|------|------|------|
| **CogVideoX-3 API** | $0.2/视频 | 每个视频生成成本 |
| **云存储** | ¥10-50/月 | 存储视频素材 |
| **服务器** | ¥50-200/月 | 运行自动化脚本 |
| **总计** | ¥60-270/月 | 根据视频数量调整 |

## ⚠️ 注意事项

### 版权与合规

1. **火影忍者版权问题**：
   - AI生成二创内容可能涉及版权风险
   - 建议添加原创声明
   - 避免使用角色真实名称（可使用替代描述）

2. **抖音平台规则**：
   - 遵守内容审核规则
   - 避免频繁发布（防止被限流）
   - 合理设置发布频率

### 技术风险

1. **API 限制**：
   - CogVideoX-3 可能有调用频率限制
   - 抖音 API 可能有每日上传限制
   - 需要做好限流和重试机制

2. **稳定性**：
   - Cookie 可能会过期，需要定期更新
   - 网络问题导致上传失败
   - 视频生成可能失败或质量不稳定

### 建议配置

- 测试模式先开启，验证 Prompt 效果
- 初期设置较低的生成频率（每天1-2个视频）
- 定期检查日志，监控系统运行状态
- 定期备份上传的视频文件

## 🔧 故障排除

### Cookie 失效

**问题**：上传时提示认证失败

**解决**：
1. 重新登录 https://creator.douyin.com
2. 重新获取 Cookie
3. 更新 `.env` 文件

### 视频生成失败

**问题**：生成视频时出现错误

**解决**：
1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看日志文件 `logs/app.log`
4. 尝试简化 Prompt

### 视频处理失败

**问题**：处理视频时出错

**解决**：
1. 确认已安装 FFmpeg：`ffmpeg -version`
2. 安装 MoviePy：`pip install moviepy`
3. 检查视频文件是否损坏

### 抖音上传失败

**问题**：上传到抖音时失败

**解决**：
1. 验证 Cookie 有效性
2. 检查视频是否符合抖音要求（大小、时长）
3. 查看日志了解具体错误

## 📚 相关文档

- **CogVideoX-3 官方文档**：https://docs.z.ai/guides/video/cogvideox-3
- **MoviePy 文档**：https://zulko.github.io/moviepy/
- **APScheduler 文档**：https://apscheduler.readthedocs.io/
- **抖音开放平台**：https://developer.open-douyin.com/
- **Z.AI 开放平台**：https://z.ai/manage-apikey/apikey-list

## 🤝 扩展功能建议

1. **AI 辅助 Prompt 生成**：使用 GPT-4 自动生成多样化的火影忍者 Prompt
2. **多平台发布**：同时支持快手、小红书、B站等平台
3. **数据分析**：统计视频播放量、点赞数，优化发布策略
4. **社区功能**：允许用户提交 Prompt 创意
5. **模板系统**：提供不同风格的视频模板

## 📝 更新日志

### v1.0.0 (2026-01-18)

- ✅ 实现基础视频生成功能
- ✅ 实现视频处理（裁剪、水印、字幕、音乐）
- ✅ 实现抖音自动上传
- ✅ 实现任务调度系统
- ✅ 内置 50+ 火影忍者 Prompt
- ✅ 完整的日志和存储管理

## 📄 许可证

本项目仅供学习和研究使用。使用者需自行承担使用本系统产生的内容责任。

**重要提示**：
- 使用前请了解相关版权法律法规
- AI 生成内容的版权归属需明确声明
- 遵守抖音平台的社区准则和内容规范

## 🙏 致谢

- CogVideoX-3 模型：Z.AI
- MoviePy：Zulko
- APScheduler：Alex Grönholm
- 火影忍者：岸本齐史

## 📧 联系与支持

如有问题或建议，欢迎提 Issue 或 Pull Request。

---

**⚡ 开始创作你的火影忍者视频之旅吧！**
