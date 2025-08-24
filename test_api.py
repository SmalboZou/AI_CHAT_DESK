#!/usr/bin/env python3
import httpx
import asyncio
import json

async def test_siliconflow_api():
    """直接测试SiliconFlow API连接"""
    print("开始测试SiliconFlow API连接...")
    
    headers = {
        "Authorization": "Bearer sk-ktbvcjnwfqpwanmgnubayqqsxnnireapcgdbtzsmnhxmnmkg",
        "Content-Type": "application/json",
        "User-Agent": "AI-Chat-App/1.0"
    }
    
    payload = {
        "model": "THUDM/GLM-4.1V-9B-Thinking",
        "messages": [{"role": "user", "content": "Hello, this is a test"}],
        "temperature": 0.1,
        "max_tokens": 20
    }
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    
    try:
        # 配置更详细的超时和连接设置
        timeout = httpx.Timeout(
            connect=30.0,
            read=120.0,
            write=30.0,
            pool=10.0
        )
        
        print(f"请求URL: {url}")
        print(f"请求头: {headers}")
        print(f"请求体: {json.dumps(payload, indent=2)}")
        
        async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
            print("正在发送请求...")
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API调用成功!")
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print("❌ API调用失败")
                print(f"错误响应: {response.text}")
                
    except httpx.TimeoutException as e:
        print(f"❌ 请求超时: {e}")
    except httpx.ConnectError as e:
        print(f"❌ 连接错误: {e}")
    except httpx.RequestError as e:
        print(f"❌ 请求错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_siliconflow_api())