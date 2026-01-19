#!/usr/bin/env python3
"""
修复 TaskScheduler 的延迟初始化问题
"""
import re

# 读取文件
with open('src/scheduler/task_scheduler.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改 __init__ 方法 - 将立即初始化改为延迟初始化
old_init = '''    def __init__(self):
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
            logger.info("Running in test mode, skipping Douyin upload")'''

new_init = '''    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.prompt_manager = PromptManager()
        self._video_generator = None  # 延迟初始化
        self.video_editor = VideoEditor()
        self.storage_manager = StorageManager()
        
        if not TEST_MODE:
            self.douyin_auth = DouyinAuth()
            self.douyin_uploader = DouyinUploader(self.douyin_auth)
        else:
            self.douyin_uploader = None
            logger.info("Running in test mode, skipping Douyin upload")

    @property
    def video_generator(self):
        """延迟初始化视频生成器"""
        if self._video_generator is None:
            self._video_generator = CogVideoClient()
        return self._video_generator'''

content = content.replace(old_init, new_init)

# 2. 修改 generate_videos_task 中的重复初始化
old_task = '''    def generate_videos_task(self):
        """生成视频的任务"""
        logger.info("Starting video generation task")
        
        self.video_generator = CogVideoClient()'''

new_task = '''    def generate_videos_task(self):
        """生成视频的任务"""
        logger.info("Starting video generation task")'''

content = content.replace(old_task, new_task)

# 写回文件
with open('src/scheduler/task_scheduler.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 修复完成！")
print("")
print("修改内容：")
print("  1. 将 CogVideoClient 的立即初始化改为延迟初始化")
print("  2. 添加 video_generator property")
print("  3. 移除 generate_videos_task 中的重复初始化")
print("")
print("验证修复：")
print("  python3 main.py --upload  # 应该不再要求 COGVIDEO_API_KEY")
