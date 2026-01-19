#!/usr/bin/env python3
import os
import sys
import time
import requests

def main():
    api_key = None
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("COGVIDEO_API_KEY="):
                    api_key = line.split("=", 1)[0].strip()
                    break
    except:
        pass
    
    if not api_key:
        print("No API Key")
        sys.exit(1)
    
    prompt = "Naruto Uzumaki using Rasengan, dynamic anime style, epic battle scene"
    
    base_url = "https://api.z.ai"
    endpoints = ["/v1/videos/generations", "/videos/generations"]
    
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
    
    for i, endpoint in enumerate(endpoints, 1):
        url = base_url + endpoint
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"Endpoint {i}: {url}")
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                print(f"Success! Response: {r.text[:200]}")
                time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
