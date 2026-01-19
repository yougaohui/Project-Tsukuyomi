#!/usr/bin/env python3
"""
简化版视频生成脚本 - 直接使用 requests
"""
import os
import sys
import time
import requests

def generate_video_simple(api_key: str, prompt: str):
    """生成视频 - 简化版"""
    # 根据文档，尝试正确的 endpoint
    base_url = "https://api.z.ai"
    endpoints_to_try = [
        "/v1/videos/generations",
        "/videos/generations", 
        "/v1/video/generations",
        "/video/generations"
    ]
    
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
    print("📡 CogVideoX-3 视频生成")
    print("=" * 60)
    print(f"Prompt: {prompt[:60]}...")
    print("")
    
    for i, endpoint_path in enumerate(endpoints_to_try, 1):
        url = base_url + endpoint_path
        print(f"[{i}/{len(endpoints_to_try)}] 测试 endpoint: {url}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("id", "")
                status = data.get("status", "")
                
                print(f"  Status: {response.status_code}")
                print(f"  Task ID: {task_id}")
                print(f"  Status: {status}")
                print("")
                
                if status == "success" or status == "succeeded" or status == "pending" or status == "processing":
                    print(f"  Response: {str(data)[:100]}...")
                    print("")
                    print("✅ 请求成功！")
                    print("")
                    return {
                        "task_id": task_id,
                        "status": status,
                        "endpoint": url
                    }
                elif status == "failed":
                    error = data.get("error", "Unknown error")
                    print(f"  ❌ 生成失败: {error}")
                    return None
                else:
                    print(f"  Response: {str(data)[:100]}...")
            
            elif response.status_code == 401:
                print(f"  ❌ 认证失败 (401)")
                print("     API Key 无效或已过期")
                return None
            elif response.status_code == 403:
                print(f"  ❌ 权限拒绝 (403)")
                print("     账户余额不足或没有视频生成权限")
                return None
            elif response.status_code == 404:
                print(f"  ❌ API 不存在 (404)")
                print("     Endpoint: {url}")
                return None
            else:
                print(f"  ⚠️  HTTP {response.status_code}")
                print(f"  Response: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print(f"  ❌ 请求超时")
        except Exception as e:
            print(f"  ❌ 错误: {str(e)[:50]}")
    
    print("")
    print("=" * 60)
    print("❌ 所有 endpoint 测试失败")
    print("=" * 60)
    print("")
    print("💡 请检查:")
    print("   1. API Key 是否正确（以 sk- 开头）")
    print("   2. 网络连接是否正常")
    print("   3. 访问 https://z.ai/console 查看账号状态")
    print("=" * 60)
    
    return None

def check_simple(api_key: str, task_id: str):
    """简化版检查结果"""
    base_url = "https://api.z.ai"
    endpoints_to_try = [
        "/v1/videos/",
        "/videos/", 
        "/v1/video/",
        "/video/"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for endpoint_path in endpoints_to_try:
        url = f"{base_url}{endpoint_path}{task_id}"
        print(f"测试: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "")
                
                print(f"  Status: {status}")
                
                if status == "succeeded" or status == "success":
                    output = data.get("output", {})
                    video_url = output.get("video_url", "")
                    
                    if video_url:
                        print("")
                        print("=" * 60)
                        print("✅ 视频生成完成！")
                        print("=" * 60)
                        print(f"🎬 视频下载链接:")
                        print(f"   {video_url}")
                        print("")
                        print("💡 在浏览器中打开此链接")
                        print("💡 或使用以下命令下载:")
                        print(f"   curl -o video.mp4 \"{video_url}\"")
                        return data
                    else:
                        print("  未找到视频 URL")
                        print(f"  完整响应: {str(data)[:200]}")
                
                elif status == "failed":
                    error = data.get("error", "Unknown")
                    print(f"  ❌ 视频生成失败: {error}")
                elif status == "processing":
                    print("  ⏳ 仍在处理中...")
                else:
                    print(f"  Status: {status}")
                    print(f"  响应: {str(data)[:100]}...")
                
                return data
            elif response.status_code == 401:
                print("  ❌ 认证失败")
            elif response.status_code == 404:
                print("  ❌ Task 不存在")
            elif response.status_code == 403:
                print("  ❌ 权限不足")
            else:
                print(f"  HTTP {response.status_code}")
                print(f"  {response.text[:100]}...")
        
        except Exception as e:
            print(f"  错误: {str(e)[:30]}")
    
    return None

def main():
    """主函数"""
    print("=" * 60)
    print("🎬 火影忍者视频生成器 - 简化版")
    print("=" * 60)
    print("")
    
    # 读取 API Key
    api_key = None
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("COGVIDEO_API_KEY="):
                    api_key = line.split("=", 1)[0].strip()
                    break
    except Exception as e:
        print(f"读取 .env 失败: {e}")
    
    if not api_key:
        print("❌ 未找到 API Key")
        sys.exit(1)
    
    print(f"✅ API Key: {api_key[:20]}...")
    print("")
    
    # 火影忍者 Prompts
    prompts = {
        1: "Naruto Uzumaki using Rasengan, dynamic anime style, epic battle scene with blue chakra energy",
        2: "Sasuke Uchiha using Chidori, lightning effects, intense battle scene with red lightning",
        3: "Kakashi Hatake reading Make-Out Tactics, peaceful forest background, anime style",
        4: "Konohagakure village at sunset, peaceful atmosphere, anime landscape style",
        5: "Team 7 fighting together, coordinated attacks, dynamic action anime style"
    }
    
    print("📋 火影忍者主题 Prompt:")
    print("")
    for num, prompt in prompts.items():
        print(f"   {num}. {prompt[:60]}...")
    print("")
    
    # 选择 Prompt
    print("请选择一个 Prompt (1-5, 直接回车选择第1个): ")
    choice = sys.stdin.readline().strip()
    
    if not choice:
        choice = "1"
    
    try:
        prompt_num = int(choice)
        if prompt_num < 1 or prompt_num > 5:
            print("❌ 无效选择，使用默认第1个")
            prompt_num = 1
    except ValueError:
        print("❌ 无效输入，使用默认第1个")
        prompt_num = 1
    
    selected_prompt = prompts[prompt_num]
    
    print("")
    print(f"✅ 已选择 Prompt {prompt_num}")
    print(f"   {selected_prompt}")
    print("")
    print("=" * 60)
    print("📡 开始生成视频...")
    print("=" * 60)
    print("")
    
    # 生成视频
    result = generate_video_simple(api_key, selected_prompt)
    
    if result and result.get("task_id"):
        task_id = result["task_id"]
        print("")
        print("=" * 60)
        print("⏳ 等待 30 秒后检查结果...")
        print("=" * 60)
        print("")
        
        time.sleep(30)
        
        # 检查结果
        for i in range(10):
            print(f"[{i+1}/10] 检查生成状态...")
            check_result(api_key, task_id)
            
            data = check_result(api_key, task_id)
            if data:
                status = data.get("status", "")
                
                if status == "succeeded":
                    print("")
                    print("🎉 视频生成成功！")
                    break
                elif status == "failed":
                    print("")
                    print("❌ 视频生成失败")
                    break
                elif status == "processing":
                    time.sleep(15)
                else:
                    time.sleep(15)
            else:
                time.sleep(15)
        
        print("")
        print("=" * 60)
        print("✅ 测试完成")
        print("=" * 60)
    
    else:
        print("")
        print("❌ 视频生成失败")
        print("   请检查:")
        print("     1. API Key 是否正确")
        print("     2. 网络连接")
        print("     3. 账户余额")

if __name__ == "__main__":
    main()
