#!/usr/bin/env python3
"""
API 测试脚本 - 修复版
"""
import os
import sys
import requests

def test_api(api_key: str):
    """测试 API 连接"""
    # 尝试多个可能的 endpoint
    endpoints = [
        "https://api.z.ai/v1/videos",
        "https://api.z.ai/v1/models",
        "https://open.bigmodel.cn/api/paas/v4/models"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("=" * 60)
    print("🧪 CogVideoX-3 API 连接测试")
    print("=" * 60)
    print("")
    print(f"API Key: {api_key[:20]}...")
    print("")
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"[{i}/{len(endpoints)}] 测试 endpoint: {endpoint}")
        print("")
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=15)
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("  ✅ 成功！")
                
                try:
                    data = response.json()
                    print(f"  Response: {str(data)[:200]}...")
                    
                    # 尝试解析模型列表
                    if "data" in data:
                        models = data.get("data", [])
                        print("")
                        print("  📋 可用模型:")
                        for model in models[:5]:  # 只显示前5个
                            model_id = model.get("id", "")
                            name = model.get("name", "")
                            print(f"     - {model_id}: {name}")
                        if len(models) > 5:
                            print(f"     ... 还有 {len(models) - 5} 个模型")
                except:
                    pass
                
                print("")
                print("✅ 此 endpoint 可用！")
                return endpoint
            elif response.status_code == 401:
                print("  ❌ 认证失败 (401)")
                print("     可能原因：")
                print("     1. API Key 无效或已过期")
                print("     2. API Key 格式不正确")
            elif response.status_code == 403:
                print("  ❌ 权限不足 (403)")
                print("     API Key 可能没有视频生成权限")
            elif response.status_code == 404:
                print("  ❌ 端点不存在 (404)")
            else:
                print(f"  ❌ 请求失败")
                
        except requests.exceptions.Timeout:
            print("  ❌ 请求超时")
        except Exception as e:
            print(f"  ❌ 错误: {str(e)[:100]}")
        
        print("")
    
    print("=" * 60)
    print("❌ 所有 endpoint 均测试失败")
    print("")
    print("💡 请检查:")
    print("   1. API Key 是否正确（以 sk- 开头）")
    print("   2. 网络连接是否正常")
    print("   3. 访问 https://z.ai/console 查看账号状态")
    print("=" * 60)
    
    return None

def main():
    """主函数"""
    print("=" * 60)
    print("🎬 火影忍者视频生成系统 - API 测试")
    print("=" * 60)
    print("")
    
    api_key = os.getenv("COGVIDEO_API_KEY")
    
    if api_key:
        print("✅ 从环境变量读取 API Key")
    else:
        print("⚠️  未检测到环境变量 COGVIDEO_API_KEY")
        print("   临时从 .env 文件读取...")
        
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("COGVIDEO_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        print(f"✅ 从 .env 读取成功")
                        break
        except FileNotFoundError:
            print("❌ .env 文件不存在")
        except Exception as e:
            print(f"❌ 读取 .env 失败: {str(e)}")
    
    if not api_key:
        print("")
        print("💡 请设置 API Key:")
        print("   1. 将 API Key 添加到 .env 文件")
        print("   2. 或者设置环境变量 COGVIDEO_API_KEY")
        print("")
        return
    
    print(f"API Key: {api_key[:20]}...")
    print("")
    print("=" * 60)
    
    test_api(api_key)

if __name__ == "__main__":
    main()
