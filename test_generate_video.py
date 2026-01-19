#!/usr/bin/env python3
"""
简化版视频生成测试脚本
"""
import os
import json
import requests
from pathlib import Path

class SimpleVideoGenerator:
    """简化的视频生成器"""
    
    def __init__(self):
        self.api_key = os.getenv("COGVIDEO_API_KEY", "")
        self.base_url = "https://api.z.ai/v1/videos"
        
        if not self.api_key:
            print("❌ 错误：未设置 COGVIDEO_API_KEY 环境变量")
            print("   请先配置 API Key：")
            print("   1. 访问 https://z.ai/manage-apikey/apikey-list")
            print("   2. 注册并创建 API Key")
            print("   3. 将 API Key 添加到 .env 文件")
            print("")
            print("   .env 文件内容：")
            print("   COGVIDEO_API_KEY=your-api-key-here")
            exit(1)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_video(self, prompt: str):
        """生成视频"""
        payload = {
            "model": "cogvideox-3",
            "prompt": prompt,
            "quality": "quality",
            "size": "1920x1080",
            "fps": 30,
            "with_audio": True
        }
        
        print(f"📡 发送请求到 API...")
        print(f"   Prompt: {prompt[:100]}...")
        print("")
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ API 请求失败：HTTP {response.status_code}")
                print(f"   响应内容：{response.text[:200]}")
                return None
            
            data = response.json()
            task_id = data.get("id")
            
            print(f"✅ 视频生成任务已创建")
            print(f"   Task ID: {task_id}")
            print(f"   Status: {data.get('status', 'unknown')}")
            print("")
            
            return data
            
        except requests.exceptions.Timeout:
            print("❌ 请求超时，请稍后重试")
            return None
        except Exception as e:
            print(f"❌ 生成失败：{str(e)}")
            return None
    
    def check_result(self, task_id: str):
        """检查生成结果"""
        url = f"{self.base_url}/{task_id}"
        
        print(f"⏳ 检查生成结果...")
        print(f"   Task ID: {task_id}")
        print("")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ 查询失败：HTTP {response.status_code}")
                return None
            
            data = response.json()
            status = data.get("status", "unknown")
            
            print(f"   当前状态: {status}")
            
            if status == "succeeded":
                print(f"✅ 视频生成完成！")
                
                output = data.get("output", {})
                video_url = output.get("video_url")
                
                if video_url:
                    print(f"   视频 URL: {video_url}")
                    print("")
                    print("🎉 成功！视频已生成，可以下载。")
                else:
                    print("❌ 未找到视频 URL")
                
                return data
            
            elif status == "failed":
                error = data.get("error", "未知错误")
                print(f"❌ 视频生成失败：{error}")
            
            elif status == "processing":
                print("   ⏳ 视频正在生成中，请稍后检查...")
            
            return data
            
        except Exception as e:
            print(f"❌ 查询失败：{str(e)}")
            return None

def main():
    """主函数"""
    print("=" * 60)
    print("火影忍者视频生成测试")
    print("=" * 60)
    print("")
    
    # 火影忍者主题 Prompts
    prompts = [
        "Naruto Uzumaki using Rasengan, dynamic anime style, epic battle scene",
        "Sasuke Uchiha using Chidori, lightning effects, intense battle",
        "Kakashi Hatake reading his orange book, peaceful forest background",
        "Konohagakure village at sunset, anime landscape style"
    ]
    
    print("📋 可用的 Prompt：")
    for i, prompt in enumerate(prompts, 1):
        print(f"   {i}. {prompt[:60]}...")
    print("")
    
    # 选择 Prompt
    choice = input("请选择一个 Prompt (1-4，直接回车选择第1个): ").strip()
    
    if not choice:
        choice = "1"
    
    try:
        prompt_index = int(choice) - 1
        if prompt_index < 0 or prompt_index >= len(prompts):
            prompt_index = 0
    except ValueError:
        prompt_index = 0
    
    selected_prompt = prompts[prompt_index]
    
    print("")
    print(f"✅ 已选择：Prompt {prompt_index + 1}")
    print("")
    
    # 初始化生成器
    generator = SimpleVideoGenerator()
    
    # 生成视频
    result = generator.generate_video(selected_prompt)
    
    if not result:
        print("")
        print("❌ 视频生成失败，请检查：")
        print("   1. API Key 是否正确")
        print("   2. 网络连接是否正常")
        print("   3. 账户余额是否充足")
        print("")
        exit(1)
    
    task_id = result.get("id")
    
    print("")
    print("=" * 60)
    print("等待生成...")
    print("=" * 60)
    print("")
    
    # 轮询检查结果（最多检查 20 次，每次间隔 15 秒）
    import time
    max_attempts = 20
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"[{attempt}/{max_attempts}] 检查中...")
        
        result = generator.check_result(task_id)
        
        if result:
            status = result.get("status", "")
            
            if status == "succeeded":
                print("")
                break
            elif status == "failed":
                print("")
                exit(1)
            elif status == "processing":
                time.sleep(15)
            else:
                print(f"   未知状态: {status}")
                time.sleep(15)
        else:
            time.sleep(15)
    
    if attempt >= max_attempts:
        print("")
        print("⏰ 超过最大等待时间，可能需要更长时间生成")
        print("   您可以稍后手动查询结果")

if __name__ == "__main__":
    main()
