from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import httpx
import asyncio

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="AI Chat API",
    description="AI聊天桌面应用后端API",
    version="1.0.0"
)

# 配置CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class ChatMessage(BaseModel):
    role: str  # 'user' 或 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2048

class ChatResponse(BaseModel):
    message: ChatMessage
    usage: Optional[dict] = None

class APIConfig(BaseModel):
    provider: str
    api_key: str
    base_url: str
    model: str

# API配置存储（生产环境中应该使用数据库）
api_configs = {}

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "AI Chat API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": "2025-08-23T19:30:00Z"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天请求"""
    try:
        # 根据provider选择相应的API配置
        config = get_api_config(request.provider)
        
        # 详细的配置验证和日志记录
        print(f"\n=== 聊天请求调试信息 ===")
        print(f"Provider: {request.provider}")
        print(f"Model: {request.model}")
        print(f"API Key存在: {'是' if config.get('api_key') else '否'}")
        print(f"API Key长度: {len(config.get('api_key', ''))}")
        print(f"Base URL: {config.get('base_url')}")
        print(f"消息数量: {len(request.messages)}")
        
        # 如果是演示模式，直接调用演示API
        if request.provider == "demo":
            print(f"使用演示模式...")
            response = await call_demo_api(request, config)
            print(f"演示模式响应成功，响应长度: {len(response.message.content)}")
            return response
        
        # 验证配置
        if not config.get('api_key'):
            error_msg = f"未配置{request.provider}的API密钥，请先在设置中配置或选择演示模式"
            print(f"错误: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 验证API密钥格式
        api_key = config.get('api_key', '')
        if request.provider == "openai" and not api_key.startswith('sk-'):
            error_msg = "OpenAI API密钥格式不正确，应该以'sk-'开头"
            print(f"错误: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        if request.provider == "anthropic" and not api_key.startswith('sk-ant-'):
            error_msg = "Anthropic API密钥格式不正确，应该以'sk-ant-'开头"
            print(f"错误: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        print(f"开始调用 {request.provider} API...")
        
        if request.provider == "openai":
            response = await call_openai_api(request, config)
        elif request.provider == "anthropic":
            response = await call_anthropic_api(request, config)
        elif request.provider == "demo":
            response = await call_demo_api(request, config)
        else:
            response = await call_custom_api(request, config)
        
        print(f"API调用成功，响应长度: {len(response.message.content)}")
        return response
    
    except HTTPException as e:
        print(f"HTTP异常: {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        error_msg = f"聊天请求失败: {str(e)}"
        print(f"未知错误: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/config")
async def save_config(config: APIConfig):
    """保存API配置"""
    try:
        api_configs[config.provider] = config.dict()
        return {"message": "配置保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")

@app.get("/api/config/{provider}")
async def get_config(provider: str):
    """获取API配置"""
    config = api_configs.get(provider)
    if not config:
        # 从环境变量获取默认配置
        config = get_default_config(provider)
    
    # 不返回敏感的API密钥
    safe_config = config.copy()
    if "api_key" in safe_config:
        safe_config["api_key"] = "***" if safe_config["api_key"] else ""
    
    return safe_config

@app.post("/api/test-connection")
async def test_connection(config: APIConfig):
    """测试API连接"""
    try:
        print(f"\n=== 连接测试调试信息 ===")
        print(f"Provider: {config.provider}")
        print(f"API Key: {config.api_key[:10]}..." if config.api_key and len(config.api_key) > 10 else f"API Key: {config.api_key}")
        print(f"Base URL: {config.base_url}")
        print(f"Model: {config.model}")
        
        # 如果是演示模式，直接返回成功
        if config.provider == "demo":
            print("使用演示模式进行连接测试")
            await asyncio.sleep(0.5)  # 模拟轻微延迟
            return {
                "status": "success", 
                "message": "演示模式连接测试成功", 
                "response": "演示模式已准备就绪，可以开始使用聊天功能。"
            }
        
        # 创建一个简单的测试请求
        test_request = ChatRequest(
            messages=[ChatMessage(role="user", content="Hello, this is a connection test.")],
            provider=config.provider,
            model=config.model,
            temperature=0.1,
            max_tokens=50
        )
        
        # 使用传入的配置进行测试
        test_config = {
            "api_key": config.api_key,
            "base_url": config.base_url,
            "model": config.model
        }
        
        if config.provider == "openai":
            response = await call_openai_api(test_request, test_config)
            return {"status": "success", "message": "OpenAI连接测试成功", "response": response.message.content[:100]}
        elif config.provider == "anthropic":
            response = await call_anthropic_api(test_request, test_config)
            return {"status": "success", "message": "Anthropic连接测试成功", "response": response.message.content[:100]}
        else:
            response = await call_custom_api(test_request, test_config)
            return {"status": "success", "message": "自定API连接测试成功", "response": response.message.content[:100]}
    
    except HTTPException as e:
        print(f"连接测试HTTP异常: {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        error_msg = f"连接测试失败: {str(e)}"
        print(f"连接测试未知异常: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

def get_api_config(provider: str) -> dict:
    """获取API配置"""
    if provider in api_configs:
        return api_configs[provider]
    
    return get_default_config(provider)

def get_default_config(provider: str) -> dict:
    """从环境变量获取默认配置"""
    if provider == "openai":
        return {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "model": "gpt-3.5-turbo"
        }
    elif provider == "anthropic":
        return {
            "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
            "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            "model": "claude-3-sonnet-20240229"
        }
    elif provider == "demo":
        return {
            "api_key": "demo_key",
            "base_url": "demo",
            "model": "demo-model"
        }
    else:
        return {
            "api_key": os.getenv("CUSTOM_API_KEY", ""),
            "base_url": os.getenv("CUSTOM_BASE_URL", ""),
            "model": "gpt-3.5-turbo"
        }

async def call_openai_api(request: ChatRequest, config: dict) -> ChatResponse:
    """调用OpenAI API"""
    if not config.get('api_key'):
        raise HTTPException(status_code=400, detail="未配置OpenAI API密钥")
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": request.model,
        "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens
    }
    
    try:
        # 配置代理和超时
        proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
        timeout = httpx.Timeout(60.0)
        
        if proxy:
            async with httpx.AsyncClient(timeout=timeout, proxy=proxy) as client:
                response = await client.post(
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=payload
                )
        else:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=payload
                )
        
        if response.status_code != 200:
            error_detail = f"OpenAI API错误 (状态码: {response.status_code})"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_detail = f"OpenAI API错误: {error_data['error'].get('message', '未知错误')}"
                    # 特别处理401错误
                    if response.status_code == 401:
                        error_detail += " - 请检查API密钥是否正确、有效且有余额"
                print(f"OpenAI API详细错误: {error_data}")
            except:
                error_detail = f"OpenAI API错误: HTTP {response.status_code}"
                if response.status_code == 401:
                    error_detail += " - 认证失败，请检查API密钥"
            
            print(f"OpenAI API错误详情: {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
        data = response.json()
        
        if 'choices' not in data or len(data['choices']) == 0:
            raise HTTPException(status_code=500, detail="OpenAI API返回了无效的响应")
        
        message_content = data["choices"][0]["message"]["content"]
        
        return ChatResponse(
            message=ChatMessage(role="assistant", content=message_content),
            usage=data.get("usage")
        )
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求OpenAI API失败: {str(e)}")

async def call_anthropic_api(request: ChatRequest, config: dict) -> ChatResponse:
    """调用Anthropic API"""
    if not config.get('api_key'):
        raise HTTPException(status_code=400, detail="未配置Anthropic API密钥")
    
    headers = {
        "x-api-key": config['api_key'],
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    # 转换消息格式为Anthropic格式
    anthropic_messages = []
    system_message = ""
    
    for msg in request.messages:
        if msg.role == "system":
            system_message = msg.content
        elif msg.role in ["user", "assistant"]:
            anthropic_messages.append({
                "role": msg.role,
                "content": msg.content
            })
    
    payload = {
        "model": request.model,
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "messages": anthropic_messages
    }
    
    # 如果有系统消息，添加到payload中
    if system_message:
        payload["system"] = system_message
    
    try:
        # 配置代理和超时
        proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
        timeout = httpx.Timeout(60.0)
        
        if proxy:
            async with httpx.AsyncClient(timeout=timeout, proxy=proxy) as client:
                response = await client.post(
                    f"{config['base_url']}/v1/messages",
                    headers=headers,
                    json=payload
                )
        else:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{config['base_url']}/v1/messages",
                    headers=headers,
                    json=payload
                )
        
        if response.status_code != 200:
            error_detail = f"Anthropic API错误 (状态码: {response.status_code})"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_detail = f"Anthropic API错误: {error_data['error'].get('message', '未知错误')}"
                    # 特别处理401错误
                    if response.status_code == 401:
                        error_detail += " - 请检查API密钥是否正确且有效"
                print(f"Anthropic API详细错误: {error_data}")
            except:
                error_detail = f"Anthropic API错误: HTTP {response.status_code}"
                if response.status_code == 401:
                    error_detail += " - 认证失败，请检查API密钥格式"
            
            print(f"Anthropic API错误详情: {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
        data = response.json()
        
        if 'content' not in data or len(data['content']) == 0:
            raise HTTPException(status_code=500, detail="Anthropic API返回了无效的响应")
        
        # Anthropic返回的content是一个数组，获取第一个text内容
        message_content = data["content"][0]["text"]
        
        return ChatResponse(
            message=ChatMessage(role="assistant", content=message_content),
            usage=data.get("usage")
        )
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求Anthropic API失败: {str(e)}")

async def call_demo_api(request: ChatRequest, config: dict) -> ChatResponse:
    """演示API - 返回模拟回复"""
    import random
    
    # 模拟一些延迟
    await asyncio.sleep(1)
    
    # 获取用户最后一条消息
    user_message = request.messages[-1].content if request.messages else "你好"
    
    # 预定义一些模拟回复
    demo_responses = [
        f"你好！我是演示AI助手。我收到了你的消息：\"{user_message}\"。这是一个模拟回复，用于测试应用功能。",
        f"非常感谢你的问题：\"{user_message}\"。作为演示模式，我可以告诉你，这个应用的聊天功能工作正常！要使用真实的AI，请配置真实的API密钥。",
        f"我正在演示模式下运行。你问了：\"{user_message}\"。如果这是真实的AI服务，我会给出更加智能和有用的回答。现在你可以体验应用的界面和基本功能。",
        f"欢迎使用AI聊天应用！你刚才说：\"{user_message}\"。这是演示模式的回复。在真实模式下，AI会根据你的问题提供更加个性化和准确的答案。",
        f"你好！我正在演示模式下工作。对于你的输入\"{user_message}\"，在真实环境下，我能够：\n1. 回答各种问题\n2. 协助写作和编程\n3. 分析和解决问题\n4. 进行创意讨论\n\n请配置真实的API密钥来解锁完整功能！"
    ]
    
    # 随机选择一个回复
    response_content = random.choice(demo_responses)
    
    return ChatResponse(
        message=ChatMessage(role="assistant", content=response_content),
        usage={
            "prompt_tokens": len(user_message),
            "completion_tokens": len(response_content),
            "total_tokens": len(user_message) + len(response_content)
        }
    )

async def call_custom_api(request: ChatRequest, config: dict) -> ChatResponse:
    if not config.get('api_key'):
        raise HTTPException(status_code=400, detail="未配置自定义API密钥")
    
    if not config.get('base_url'):
        raise HTTPException(status_code=400, detail="未配置自定义API地址")
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": request.model,
        "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens
    }
    
    try:
        # 尝试使用标准的OpenAI兼容端点
        base_url = config['base_url'].rstrip('/')
        if not base_url.endswith('/chat/completions'):
            api_url = f"{base_url}/chat/completions"
        else:
            api_url = base_url
        
        # 配置代理和超时
        proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
        timeout = httpx.Timeout(60.0)
        
        if proxy:
            async with httpx.AsyncClient(timeout=timeout, proxy=proxy) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
        else:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
        
        if response.status_code != 200:
            error_detail = f"自定义API错误 (状态码: {response.status_code})"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_detail = f"自定义API错误: {error_data['error'].get('message', '未知错误')}"
                elif 'message' in error_data:
                    error_detail = f"自定义API错误: {error_data['message']}"
                
                # 特别处理401错误
                if response.status_code == 401:
                    error_detail += " - 认证失败，请检查API密钥和Base URL是否正确"
                
                print(f"自定义API详细错误: {error_data}")
            except:
                error_detail = f"自定义API错误: HTTP {response.status_code}"
                if response.status_code == 401:
                    error_detail += " - 认证失败，请检查API密钥、Base URL和认证方式"
            
            print(f"自定义API错误详情: {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
        data = response.json()
        
        # 支持多种响应格式
        message_content = ""
        
        if 'choices' in data and len(data['choices']) > 0:
            # OpenAI兼容格式
            choice = data['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                message_content = choice['message']['content']
            elif 'text' in choice:
                message_content = choice['text']
        elif 'content' in data:
            # 直接内容格式
            if isinstance(data['content'], list) and len(data['content']) > 0:
                message_content = data['content'][0].get('text', str(data['content']))
            else:
                message_content = str(data['content'])
        elif 'response' in data:
            # 另一种常见格式
            message_content = str(data['response'])
        else:
            raise HTTPException(status_code=500, detail="自定义API返回了无法识别的响应格式")
        
        if not message_content:
            raise HTTPException(status_code=500, detail="自定义API返回了空的响应内容")
        
        return ChatResponse(
            message=ChatMessage(role="assistant", content=message_content),
            usage=data.get("usage")
        )
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求自定义API失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )