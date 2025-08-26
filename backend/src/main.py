from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
import os
from dotenv import load_dotenv
import httpx
import asyncio
import json
import logging

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
    stream: bool = False
    api_config: Optional[dict] = None

class ChatResponse(BaseModel):
    message: ChatMessage
    usage: Optional[dict] = None

class APIConfig(BaseModel):
    provider: str
    api_key: str
    base_url: str
    model: str

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = ""
    description: str = ""
    type: str = "chat"

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

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
    """处理聊天请求 - 非流式"""
    if request.stream:
        raise HTTPException(status_code=400, detail="请使用 /api/chat/stream 端点进行流式请求")
    
    # 原有的非流式处理逻辑
    return await _process_chat_request(request)

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """处理流式聊天请求"""
    if not request.stream:
        request.stream = True
    
    async def generate_stream():
        try:
            async for chunk in _process_streaming_chat(request):
                if chunk:
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            error_chunk = {
                "error": True,
                "message": str(e)
            }
            yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

async def _process_chat_request(request: ChatRequest) -> ChatResponse:
    """处理聊天请求"""
    try:
        # 根据provider选择相应的API配置
        config = get_api_config(request.provider, request.api_config)
        
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

async def _process_streaming_chat(request: ChatRequest) -> AsyncGenerator[dict, None]:
    """处理流式聊天请求"""
    try:
        # 根据provider选择相应的API配置
        config = get_api_config(request.provider, request.api_config)
        
        print(f"\n=== 流式聊天请求调试信息 ===")
        print(f"Provider: {request.provider}")
        print(f"Model: {request.model}")
        print(f"API Key存在: {'是' if config.get('api_key') else '否'}")
        print(f"Base URL: {config.get('base_url')}")
        print(f"消息数量: {len(request.messages)}")
        
        # 如果是演示模式，调用演示流式API
        if request.provider == "demo":
            print(f"使用演示模式流式输出...")
            async for chunk in call_demo_streaming_api(request, config):
                yield chunk
            return
        
        # 验证配置
        if not config.get('api_key'):
            error_msg = f"未配置{request.provider}的API密钥，请先在设置中配置或选择演示模式"
            print(f"错误: {error_msg}")
            yield {"error": True, "message": error_msg}
            return
        
        print(f"开始流式调用 {request.provider} API...")
        
        if request.provider == "openai":
            async for chunk in call_openai_streaming_api(request, config):
                yield chunk
        elif request.provider == "anthropic":
            async for chunk in call_anthropic_streaming_api(request, config):
                yield chunk
        else:
            async for chunk in call_custom_streaming_api(request, config):
                yield chunk
                
    except Exception as e:
        error_msg = f"流式聊天请求失败: {str(e)}"
        print(f"流式处理错误: {error_msg}")
        yield {"error": True, "message": error_msg}

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
        
        # 添加网络诊断
        if config.provider == "custom":
            try:
                import socket
                from urllib.parse import urlparse
                
                # 解析URL获取主机名和端口
                parsed_url = urlparse(config.base_url)
                hostname = parsed_url.hostname
                port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
                
                print(f"正在测试到 {hostname}:{port} 的网络连接...")
                
                # 测试TCP连接
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((hostname, port))
                sock.close()
                
                if result != 0:
                    print(f"TCP连接失败: {hostname}:{port}")
                    raise HTTPException(
                        status_code=503, 
                        detail=f"无法连接到服务器 {hostname}:{port}，请检查网络连接和服务器状态"
                    )
                else:
                    print(f"TCP连接成功: {hostname}:{port}")
                    
            except Exception as e:
                print(f"网络诊断失败: {e}")
        
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

@app.post("/api/models")
async def get_models(config: APIConfig) -> ModelsResponse:
    """获取可用模型列表"""
    try:
        print(f"\n=== 获取模型列表调试信息 ===")
        print(f"Provider: {config.provider}")
        print(f"API Key存在: {'是' if config.api_key else '否'}")
        print(f"Base URL: {config.base_url}")
        
        # 演示模式返回模拟模型列表
        if config.provider == "demo":
            print("使用演示模式获取模型列表")
            demo_models = [
                ModelInfo(
                    id="demo-gpt-3.5-turbo",
                    description="演示版 GPT-3.5 Turbo 模型",
                    type="chat"
                ),
                ModelInfo(
                    id="demo-gpt-4",
                    description="演示版 GPT-4 模型",
                    type="chat"
                ),
                ModelInfo(
                    id="demo-claude-3",
                    description="演示版 Claude-3 模型",
                    type="chat"
                )
            ]
            return ModelsResponse(data=demo_models)
        
        # 验证API密钥
        if not config.api_key:
            raise HTTPException(status_code=400, detail="未配置API密钥")
        
        if config.provider == "openai":
            return await get_openai_models(config)
        elif config.provider == "anthropic":
            return await get_anthropic_models(config)
        else:  # custom provider（包括硅基流动等）
            return await get_custom_models(config)
            
    except HTTPException as e:
        print(f"获取模型列表HTTP异常: {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        error_msg = f"获取模型列表失败: {str(e)}"
        print(f"获取模型列表未知异常: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

def get_api_config(provider: str, api_config: Optional[dict] = None) -> dict:
    """获取API配置"""
    # 优先使用请求中传入的配置
    if api_config:
        return api_config
    
    # 其次使用存储的配置
    if provider in api_configs:
        return api_configs[provider]
    
    # 最后使用默认配置
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
        # 配置超时
        timeout = httpx.Timeout(60.0)
        
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
        # 配置超时
        timeout = httpx.Timeout(60.0)
        
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
        "Content-Type": "application/json",
        "User-Agent": "AI-Chat-App/1.0"
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
        
        print(f"正在请求API: {api_url}")
        print(f"请求头: {dict(headers)}")
        print(f"请求体模型: {payload['model']}")
        
        # 配置更宽松的超时和重试设置
        timeout = httpx.Timeout(
            connect=30.0,  # 连接超时
            read=120.0,    # 读取超时
            write=30.0,    # 写入超时
            pool=10.0      # 连接池超时
        )
        
        # 创建客户端时添加更多配置
        client_config = {
            "timeout": timeout,
            "verify": True,  # 验证SSL证书
            "follow_redirects": True,  # 跟随重定向
            "limits": httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
        }
        

        
        async with httpx.AsyncClient(**client_config) as client:
            print("开始发送HTTP请求...")
            response = await client.post(
                api_url,
                headers=headers,
                json=payload
            )
            print(f"收到响应，状态码: {response.status_code}")
        
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
        print(f"响应数据结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        
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
            print(f"无法识别的响应格式: {data}")
            raise HTTPException(status_code=500, detail="自定义API返回了无法识别的响应格式")
        
        if not message_content:
            raise HTTPException(status_code=500, detail="自定义API返回了空的响应内容")
        
        print(f"成功获取响应内容，长度: {len(message_content)}")
        
        return ChatResponse(
            message=ChatMessage(role="assistant", content=message_content),
            usage=data.get("usage")
        )
        
    except httpx.TimeoutException as e:
        error_msg = f"请求自定义API超时: {str(e)} - 请检查网络连接或尝试稍后再试"
        print(f"超时错误: {error_msg}")
        raise HTTPException(status_code=408, detail=error_msg)
    except httpx.ConnectError as e:
        error_msg = f"连接自定义API失败: {str(e)} - 请检查Base URL是否正确或网络连接"
        print(f"连接错误: {error_msg}")
        raise HTTPException(status_code=503, detail=error_msg)

# 流式API调用函数
async def call_openai_streaming_api(request: ChatRequest, config: dict) -> AsyncGenerator[dict, None]:
    """调用OpenAI流式API"""
    if not config.get('api_key'):
        yield {"error": True, "message": "未配置OpenAI API密钥"}
        return
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": request.model,
        "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "stream": True
    }
    
    try:
        timeout = httpx.Timeout(60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    error_detail = f"OpenAI API错误 (状态码: {response.status_code})"
                    yield {"error": True, "message": error_detail}
                    return
                
                content_buffer = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(data_str)
                            if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                                delta = chunk_data["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"] is not None:
                                    content = delta["content"]
                                    content_buffer += content
                                    yield {
                                        "type": "content",
                                        "content": content,
                                        "full_content": content_buffer
                                    }
                        except json.JSONDecodeError:
                            continue
                            
    except Exception as e:
        print(f"Debug: OpenAI streaming error: {e}")
        yield {"error": True, "message": f"请求OpenAI流式API失败: {str(e)}"}

async def call_anthropic_streaming_api(request: ChatRequest, config: dict) -> AsyncGenerator[dict, None]:
    """调用Anthropic流式API"""
    if not config.get('api_key'):
        yield {"error": True, "message": "未配置Anthropic API密钥"}
        return
    
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
        "messages": anthropic_messages,
        "stream": True
    }
    
    if system_message:
        payload["system"] = system_message
    
    try:
        timeout = httpx.Timeout(60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{config['base_url']}/v1/messages",
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    error_detail = f"Anthropic API错误 (状态码: {response.status_code})"
                    yield {"error": True, "message": error_detail}
                    return
                
                content_buffer = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(data_str)
                            if chunk_data.get("type") == "content_block_delta":
                                delta = chunk_data.get("delta", {})
                                if "text" in delta and delta["text"] is not None:
                                    content = delta["text"]
                                    content_buffer += content
                                    yield {
                                        "type": "content",
                                        "content": content,
                                        "full_content": content_buffer
                                    }
                        except json.JSONDecodeError:
                            continue
                            
    except Exception as e:
        yield {"error": True, "message": f"请求Anthropic流式API失败: {str(e)}"}

async def call_custom_streaming_api(request: ChatRequest, config: dict) -> AsyncGenerator[dict, None]:
    """调用自定义流式API（如硅基流动等）"""
    if not config.get('api_key'):
        yield {"error": True, "message": "未配置自定义API密钥"}
        return
    
    if not config.get('base_url'):
        yield {"error": True, "message": "未配置自定义API地址"}
        return
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
        "User-Agent": "AI-Chat-App/1.0"
    }
    
    payload = {
        "model": request.model,
        "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "stream": True
    }
    
    try:
        base_url = config['base_url'].rstrip('/')
        if not base_url.endswith('/chat/completions'):
            api_url = f"{base_url}/chat/completions"
        else:
            api_url = base_url
        
        print(f"正在请求流式API: {api_url}")
        
        timeout = httpx.Timeout(60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                api_url,
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    error_detail = f"自定义API错误 (状态码: {response.status_code})"
                    yield {"error": True, "message": error_detail}
                    return
                
                content_buffer = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(data_str)
                            if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                                delta = chunk_data["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"] is not None:
                                    content = delta["content"]
                                    content_buffer += content
                                    yield {
                                        "type": "content",
                                        "content": content,
                                        "full_content": content_buffer
                                    }
                        except json.JSONDecodeError:
                            continue
                            
    except Exception as e:
        print(f"Debug: Custom API streaming error: {e}")
        yield {"error": True, "message": f"请求自定义流式API失败: {str(e)}"}

async def call_demo_streaming_api(request: ChatRequest, config: dict) -> AsyncGenerator[dict, None]:
    """演示流式API - 模拟字符逐个输出"""
    import random
    
    # 获取用户最后一条消息
    user_message = request.messages[-1].content if request.messages else "你好"
    
    # 预定义一些模拟回复
    demo_responses = [
        f"你好！我是演示AI助手。我收到了你的消息：\"{user_message}\"。这是一个模拟的流式回复，用于测试应用功能。",
        f"非常感谢你的问题：\"{user_message}\"。作为演示模式，我可以告诉你，这个应用的流式聊天功能工作正常！要使用真实的AI，请配置真实的API密钥。",
        f"我正在演示模式下运行。你问了：\"{user_message}\"。如果这是真实的AI服务，我会给出更加智能和有用的回答。现在你可以体验应用的流式输出界面。"
    ]
    
    # 随机选择一个回复
    response_content = random.choice(demo_responses)
    
    # 模拟流式输出
    content_buffer = ""
    
    # 按字符逐个输出，模拟真实的流式体验
    for char in response_content:
        content_buffer += char
        yield {
            "type": "content",
            "content": char,
            "full_content": content_buffer
        }
        # 随机延迟，模拟网络传输
        await asyncio.sleep(random.uniform(0.01, 0.05))

# 模型列表获取函数
async def get_openai_models(config: APIConfig) -> ModelsResponse:
    """获取OpenAI模型列表"""
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        timeout = httpx.Timeout(30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                f"{config.base_url}/models",
                headers=headers
            )
        
        if response.status_code != 200:
            error_detail = f"OpenAI API错误 (状态码: {response.status_code})"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_detail = f"OpenAI API错误: {error_data['error'].get('message', '未知错误')}"
            except:
                pass
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
        data = response.json()
        models = []
        
        for model in data.get('data', []):
            # 只显示聊天模型（过滤掉embedding等其他模型）
            model_id = model.get('id', '')
            if any(keyword in model_id.lower() for keyword in ['gpt', 'chat', 'turbo']):
                models.append(ModelInfo(
                    id=model_id,
                    description=f"OpenAI {model_id}",
                    type="chat",
                    created=model.get('created', 0),
                    owned_by=model.get('owned_by', 'openai')
                ))
        
        return ModelsResponse(data=models)
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求OpenAI API失败: {str(e)}")

async def get_anthropic_models(config: APIConfig) -> ModelsResponse:
    """获取Anthropic模型列表"""
    # Anthropic没有公开的模型列表API，返回确定的模型
    models = [
        ModelInfo(
            id="claude-3-opus-20240229",
            description="Claude 3 Opus - 最先进的模型",
            type="chat",
            owned_by="anthropic"
        ),
        ModelInfo(
            id="claude-3-sonnet-20240229",
            description="Claude 3 Sonnet - 平衡性能和成本",
            type="chat",
            owned_by="anthropic"
        ),
        ModelInfo(
            id="claude-3-haiku-20240307",
            description="Claude 3 Haiku - 快速且经济",
            type="chat",
            owned_by="anthropic"
        ),
        ModelInfo(
            id="claude-2.1",
            description="Claude 2.1 - 上一代模型",
            type="chat",
            owned_by="anthropic"
        )
    ]
    
    return ModelsResponse(data=models)

async def get_custom_models(config: APIConfig) -> ModelsResponse:
    """获取自定API模型列表（支持硅基流动等）"""
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
        "User-Agent": "AI-Chat-App/1.0"
    }
    
    try:
        # 尝试使用标准的OpenAI兼容模型列表端点
        base_url = config.base_url.rstrip('/')
        if base_url.endswith('/chat/completions'):
            base_url = base_url.replace('/chat/completions', '')
        
        api_url = f"{base_url}/models"
        
        print(f"正在请求模型列表API: {api_url}")
        
        timeout = httpx.Timeout(30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                api_url,
                headers=headers
            )
        
        if response.status_code != 200:
            error_detail = f"自定API错误 (状态码: {response.status_code})"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_detail = f"自定API错误: {error_data['error'].get('message', '未知错误')}"
                elif 'detail' in error_data:
                    error_detail = f"自定API错误: {error_data['detail']}"
            except:
                pass
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
        data = response.json()
        models = []
        
        # 处理不同的响应格式
        model_list = []
        if 'data' in data and isinstance(data['data'], list):
            model_list = data['data']
        elif 'models' in data and isinstance(data['models'], list):
            model_list = data['models']
        elif isinstance(data, list):
            model_list = data
        
        for model in model_list:
            if isinstance(model, dict):
                model_id = model.get('id', model.get('name', model.get('model_name', '')))
                if model_id:
                    # 过滤聊天模型（排除图像、嵌入等模型）
                    model_type = model.get('type', model.get('object', 'chat'))
                    if (model_type in ['chat', 'text', 'model'] or 
                        any(keyword in model_id.lower() for keyword in 
                            ['chat', 'gpt', 'qwen', 'deepseek', 'glm', 'yi', 'llama', 
                             'mistral', 'claude', 'gemini', 'baichuan', 'chatglm'])):
                        
                        # 排除明显的非聊天模型
                        if not any(exclude in model_id.lower() for exclude in 
                                 ['embedding', 'whisper', 'tts', 'dall-e', 'diffusion', 
                                  'stable-diffusion', 'clip', 'rerank']):
                            models.append(ModelInfo(
                                id=model_id,
                                description=model.get('description', model_id),
                                type="chat",
                                created=model.get('created', 0),
                                owned_by=model.get('owned_by', model.get('provider', 'custom'))
                            ))
            elif isinstance(model, str):
                # 如果是字符串列表
                models.append(ModelInfo(
                    id=model,
                    description=model,
                    type="chat"
                ))
        
        if not models:
            # 如果没有找到模型，返回一些常见模型作为默认选项
            models = [
                ModelInfo(
                    id="gpt-3.5-turbo",
                    description="GPT-3.5 Turbo",
                    type="chat"
                ),
                ModelInfo(
                    id="gpt-4",
                    description="GPT-4",
                    type="chat"
                ),
                ModelInfo(
                    id="Qwen/Qwen2.5-72B-Instruct",
                    description="通义千问 2.5-72B",
                    type="chat"
                )
            ]
        
        print(f"成功获取到 {len(models)} 个模型")
        return ModelsResponse(data=models)
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求自定API失败: {str(e)}")
    except Exception as e:
        print(f"获取自定模型列表错误: {e}")
        raise HTTPException(status_code=500, detail=f"解析模型列表失败: {str(e)}")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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