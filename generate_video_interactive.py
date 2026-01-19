#!/usr/bin/env python3
"""
交互式视频生成脚本
可以直接输入 API Key 进行测试
"""
import os
import sys
import requests
from pathlib import Path

def generate_video(api_key: str, prompt: str):
    """生成视频"""
    base_url = "https://api.z.ai/v1/videos"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "cogvideox-3",
        "prompt": prompt,
        "quality": "quality",
        "size": "1920x1080",
        "fps": 30,
        "with_audio": True
    }
    
    print("=" * 60)
    print("📡 发送视频生成请求到 CogVideoX-3 API")
    print("=" * 60)
    print(f"Prompt: {prompt}")
    print("")
    
    try:
        response = requests.post(base_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ API 请求失败")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return None
        
        data = response.json()
        task_id = data.get("id")
        status = data.get("status", "unknown")
        
        print(f"✅ 视频生成任务已创建")
        print(f"Task ID: {task_id}")
        print(f"Status: {status}")
        print("")
        print("⏳ 等待视频生成...")
        print("提示: 通常需要 1-5 分钟")
        print("")
        
        return task_id
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return None

def check_result(api_key: str, task_id: str, max_wait: int = 300):
    """检查生成结果"""
    import time
    base_url = "https://api.z.ai/v1/videos"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    url = f"{base_url}/{task_id}"
    
    wait_time = 0
    check_interval = 15  # 每 15 秒检查一次
    
    while wait_time < max_wait:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ 查询失败: HTTP {response.status_code}")
                return None
            
            data = response.json()
            status = data.get("status", "unknown")
            
            print(f"[{wait_time}s] 状态: {status}", end='\r')
            
            if status == "succeeded":
                print("")  # 换行
                print("✅ 视频生成完成！")
                print("")
                
                output = data.get("output", {})
                video_url = output.get("video_url")
                
                if video_url:
                    print(f"🎬 视频下载链接:")
                    print(f"   {video_url}")
                    print("")
                    print("💡 提示: 您可以在浏览器中打开此链接下载视频")
                    print("💡 提示: 或者使用以下命令下载:")
                    print(f"   curl -o video.mp4 \"{video_url}\"")
                else:
                    print("❌ 未找到视频 URL")
                
                return data
            
            elif status == "failed":
                print("")  # 换行
                print("❌ 视频生成失败")
                
                error = data.get("error", "未知错误")
                print(f"错误信息: {error}")
                return None
            
            elif status == "processing":
                # 继续等待
                pass
            else:
                print(f"⚠️ 未知状态: {status}")
                pass
        
        except Exception as e:
            print(f"❌ 查询失败: {str(e)}")
        
        if wait_time >= max_wait - check_interval:
            print("")
            print("⏰ 已达到最大等待时间")
            break
        
        time.sleep(check_interval)
        wait_time += check_interval
    
    print("")
    print("⏰ 超时: 视频生成时间过长")
    print("💡 您可以稍后使用 Task ID 手动查询结果")
    print(f"Task ID: {task_id}")
    print("")
    
    return None

def main():
    """主函数"""
    print("=" * 60)
    print("🎬 火影忍者视频生成器 - CogVideoX-3")
    print("=" * 60)
    print("")
    
    # 获取 API Key
    api_key = os.getenv("COGVIDEO_API_KEY")
    
    if api_key:
        print("✅ 检测到环境变量中的 API Key")
        print(f"Key: {api_key[:20]}...")
    else:
        print("⚠️ 未检测到 API Key")
        print("")
        print("请选择输入方式:")
        print("1. 输入 API Key")
        print("2. 稍后（结束程序）")
        
        choice = input("请选择 (1/2): ").strip()
        
        if choice == "2":
            print("")
            print("再见！")
            sys.exit(0)
        
        api_key = input("请输入您的 Z.AI API Key: ").strip()
        
        if not api_key:
            print("")
            print("❌ API Key 不能为空")
            sys.exit(1)
    
    print("")
    
    # 火影忍者 Prompts
    prompts = {
        1: "Naruto Uzumaki using Rasengan, dynamic anime style, epic battle scene with blue chakra energy",
        2: "Sasuke Uchiha using Chidori, lightning effects, intense battle scene",
        3: "Konohagakure village at sunset, peaceful atmosphere, anime landscape style",
        4: "Team 7 fighting together, coordinated attacks, dynamic action anime style",
        5: "Hatake Kakashi reading Icha Icha Paradise, peaceful forest background"
    }
    
    print("📋 火影忍者主题 Prompt:")
    print("")
    for num, prompt in prompts.items():
        print(f"   {num}. {prompt[:70]}...")
    print("")
    
    # 选择 Prompt
    choice = input("请选择一个 Prompt (1-5): ").strip()
    
    try:
        prompt_num = int(choice)
        if prompt_num < 1 or prompt_num > 5:
            print("")
            print("❌ 无效的选择，请输入 1-5 之间的数字")
            sys.exit(1)
    except ValueError:
        print("")
        print("❌ 请输入有效的数字")
        sys.exit(1)
    
    selected_prompt = prompts[prompt_num]
    
    print("")
    print("=" * 60)
    print(f"✅ 已选择 Prompt {prompt_num}")
    print(f"   {selected_prompt}")
    print("=" * 60)
    print("")
    
    # 生成视频
    task_id = generate_video(api_key, selected_prompt)
    
    if not task_id:
        print("")
        print("❌ 视频生成任务创建失败")
        sys.exit(1)
    
    # 等待并检查结果
    print("")
    print("📥 检查生成状态中...")
    print("   (每 15 秒检查一次，最多等待 5 分钟)")
    print("")
    
    check_result(api_key, task_id)
    
    print("")
    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
