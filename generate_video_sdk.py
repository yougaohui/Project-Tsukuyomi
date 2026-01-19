#!/usr/bin/env python3
"""
使用官方 Z.ai SDK 生成视频的脚本
"""
import os
import time

try:
    from zhipuai import ZhipuAI
except ImportError:
    print("⚠️ zhipuai SDK 未安装")
    print("正在安装 zhipuai...")
    import subprocess
    subprocess.run(["python3", "-m", "pip", "install", "--trusted-host", "pypi.org", "--trusted-host", "files.pythonhosted.org", "zhipuai"], check=True)
    from zhipuai import ZhipuAI

def generate_video_with_sdk(prompt: str, api_key: str):
    """使用 SDK 生成视频"""
    print("=" * 60)
    print("📡 使用智谱AI官方SDK生成视频")
    print("=" * 60)
    print("")
    print(f"Prompt: {prompt}")
    print("")
    
    client = ZhipuAI(api_key=api_key)
    
    print("⏳ 正在调用 CogVideoX-3 API...")
    print("   可能需要 1-5 分钟...")
    print("")
    
    try:
        response = client.videos.generations(
            model="cogvideox-3",
            prompt=prompt,
            quality="quality",
            size="1920x1080",
            fps=30,
            with_audio=True
        )
        
        print("=" * 60)
        print("✅ 生成请求已提交")
        print("=" * 60)
        print("")
        print(f"Task ID: {response.id}")
        print(f"Status: {response.status}")
        print("")
        
        return response
        
    except Exception as e:
        print("=" * 60)
        print("❌ 生成失败")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("")
        return None

def check_result(api_key: str, task_id: str, max_wait: int = 300):
    """检查生成结果"""
    print("=" * 60)
    print("⏳ 检查生成状态")
    print("=" * 60)
    print("")
    
    client = ZhipuAI(api_key=api_key)
    
    waited = 0
    check_interval = 15
    
    while waited < max_wait:
        try:
            result = client.videos.retrieve_videos_result(id=task_id)
            
            status = result.status
            
            print(f"[{waited}s] Status: {status}")
            
            if status == "succeeded":
                print("")
                print("=" * 60)
                print("✅ 视频生成完成！")
                print("=" * 60)
                print("")
                
                output = result.output
                video_url = output.video_url if hasattr(output, 'video_url') else None
                
                if video_url:
                    print(f"🎬 视频下载链接:")
                    print(f"   {video_url}")
                    print("")
                    print("💡 您可以在浏览器中打开此链接")
                    print("💡 或使用以下命令下载:")
                    print(f"   curl -o video.mp4 \"{video_url}\"")
                else:
                    print("❌ 未找到视频 URL")
                
                return result
            
            elif status == "failed":
                print("")
                print("=" * 60)
                print("❌ 视频生成失败")
                print("=" * 60)
                print("")
                print(f"Error: {result.error}")
                return result
            
            elif status == "processing":
                print("   ⏳ 仍在生成中...")
                pass
            else:
                print(f"   ⚠️ 未知状态: {status}")
            
            time.sleep(check_interval)
            waited += check_interval
            
        except Exception as e:
            print(f"   检查失败: {str(e)}")
        
        if waited >= max_wait:
            print("")
            print("=" * 60)
            print("⏰ 已达到最大等待时间")
            print("=" * 60)
            print("")
            print("💡 视频可能仍在生成中")
            print(f"Task ID: {task_id}")
            print("   您可以稍后手动查询结果")

def main():
    """主函数"""
    print("=" * 60)
    print("🎬 火影忍者视频生成器")
    print("=" * 60)
    print("")
    
    # 获取 API Key
    api_key = os.getenv("COGVIDEO_API_KEY")
    
    if not api_key:
        print("❌ 未找到 COGVIDEO_API_KEY 环境变量")
        print("")
        print("正在尝试从 .env 文件读取...")
        
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("COGVIDEO_API_KEY="):
                        api_key = line.split("=", 1)[0].strip()
                        print("✅ 从 .env 读取成功")
                        break
        except FileNotFoundError:
            print("❌ .env 文件不存在")
            exit(1)
    
    if not api_key:
        print("💡 无法获取 API Key，请:")
        print("   1. 设置环境变量: export COGVIDEO_API_KEY=your-key")
        print("   2. 或确保 .env 文件包含 COGVIDEO_API_KEY=your-key")
        exit(1)
    
    print(f"✅ API Key: {api_key[:20]}...")
    print("")
    
    # 火影忍者 Prompts
    prompts = [
        "Naruto Uzumaki using Rasengan, dynamic anime style, epic battle scene with blue chakra energy",
        "Sasuke Uchiha using Chidori, lightning effects, intense battle scene with sharingan activated",
        "Team 7 fighting together, coordinated attacks, dynamic action anime style",
        "Konohagakure village at sunset, peaceful anime landscape with warm colors",
        "Hatake Kakashi reading Icha Icha Paradise, serene forest background"
    ]
    
    print("📋 可用 Prompt:")
    print("")
    for i, prompt in enumerate(prompts, 1):
        print(f"   {i}. {prompt[:60]}...")
    print("")
    
    # 选择 Prompt
    choice = input("请选择一个 Prompt (1-5): ").strip()
    
    try:
        prompt_index = int(choice) - 1
        if prompt_index < 0 or prompt_index >= len(prompts):
            print("❌ 无效的选择")
            exit(1)
    except ValueError:
        print("❌ 请输入有效的数字")
        exit(1)
    
    selected_prompt = prompts[prompt_index]
    
    print("")
    print("=" * 60)
    print(f"✅ 已选择 Prompt {prompt_index + 1}")
    print(f"   {selected_prompt[:80]}...")
    print("=" * 60)
    print("")
    
    # 生成视频
    response = generate_video_with_sdk(selected_prompt, api_key)
    
    if not response or not response.id:
        print("❌ 视频生成失败，请检查:")
        print("   1. API Key 是否正确")
        print("   2. 网络连接是否正常")
        print("   3. 账户余额是否充足")
        exit(1)
    
    # 等待生成
    print("")
    print("=" * 60)
    print("⏳ 等待视频生成完成...")
    print("=" * 60)
    print("   (可能需要 1-5 分钟)")
    print("")
    
    # 查询结果
    result = check_result(api_key, response.id)
    
    print("")
    print("=" * 60)
    print("✅ 视频生成流程完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
