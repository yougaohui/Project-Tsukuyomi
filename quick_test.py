#!/usr/bin/env python3
"""快速 API 测试脚本 - 直接从 .env 读取"""
import os

# 读取 API Key
with open(".env", "r") as f:
    for line in f:
        if line.startswith("COGVIDEO_API_KEY="):
            api_key = line.split("=", 1)[1].strip()
            break

if not api_key:
    print("❌ 未找到 API Key")
    exit(1)

print("=" * 60)
print("🧪 CogVideoX-3 API 测试")
print("=" * 60)
print(f"API Key: {api_key[:20]}...")
print("")

import requests

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("📡 测试 API 端点...")
print("")

endpoints = [
    "https://api.z.ai/v1/videos",
    "https://api.z.ai/v1/models"
]

for endpoint in endpoints:
    print(f"测试: {endpoint}")
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✅ 成功 (HTTP {response.status_code})")
            
            try:
                data = response.json()
                print(f"  响应: {str(data)[:100]}...")
                
                if "data" in data:
                    models = data.get("data", [])
                    if models:
                        print(f"  📊 找到 {len(models)} 个模型")
                        for model in models[:3]:
                            mid = model.get("id", "")
                            name = model.get("name", "Unknown")
                            print(f"     - {mid}: {name}")
            except:
                pass
        elif response.status_code == 401:
            print(f"  ❌ 认证失败 (HTTP {response.status_code})")
            print(f"     可能原因：API Key 无效")
        elif response.status_code == 403:
            print(f"  ❌ 权限不足 (HTTP {response.status_code})")
            print(f"     可能原因：需要视频生成权限")
        else:
            print(f"  ⚠️  其他状态 (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"  ❌ 错误: {str(e)[:50]}")
    
    print("")

print("=" * 60)
print("✅ API 测试完成")
print("=" * 60)
