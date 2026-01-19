#!/usr/bin/env python3
"""
短视频运营 Agent - 快速使用示例
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path('/Users/ygh/StudioProjects/Project-Tsukuyomi')
sys.path.insert(0, str(project_root))

from src.agents.operations.video_operations_agent import (
    VideoOperationsAgent,
    Platform,
    PublishStrategy,
    VideoStatus
)
from src.agents.operations.account_manager import (
    AccountManager,
    AccountConfig,
    AccountStatus,
    Platform as AccountPlatform
)
import tempfile
import os
from datetime import datetime


def example_1_basic_usage():
    print('
' + '='*60)
    print('📖 示例1: 基本使用')
    print('='*60)
    
    agent = VideoOperationsAgent()
    count = agent.load_videos()
    print(f'加载了 {count} 个视频')
    status = agent.get_status()
    print(f'当前队列: {status["queue_size"]} 个视频')


def example_2_add_video():
    print('
' + '='*60)
    print('📖 示例2: 添加视频')
    print('='*60)
    
    agent = VideoOperationsAgent()
    
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        temp_file = Path(f.name)
        f.write(b'fake video content')
    
    try:
        video = agent.add_video(
            file_path=temp_file,
            title='测试视频 - 火影忍者',
            description='测试描述',
            topics=['#测试', '#火影忍者']
        )
        
        if video:
            print(f'✅ 视频添加成功: {video.title}')
            print(f'   话题: {video.topics}')
    finally:
        if temp_file.exists():
            os.unlink(temp_file)


def main():
    print('
' + '='*60)
    print('🎬 短视频运营 Agent - 快速使用示例')
    print('='*60)
    
    try:
        example_1_basic_usage()
        example_2_add_video()
        
        print('
' + '='*60)
        print('🎉 示例运行完成！')
        print('='*60)
        
    except Exception as e:
        print(f'
❌ 错误: {e}')


if __name__ == '__main__':
    main()
