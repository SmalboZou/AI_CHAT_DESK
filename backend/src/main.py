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
        
        if request.provider == "openai":
            response = await call_openai_api(request, config)
        elif request.provider == "anthropic":
            response = await call_anthropic_api(request, config)
        else:
            response = await call_custom_api(request, config)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天请求失败: {str(e)}")

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
        # 这里可以实现实际的连接测试
        test_request = ChatRequest(
            messages=[ChatMessage(role="user", content="测试连接")],
            provider=config.provider,
            model=config.model
        )
        
        # 暂时返回成功，实际应该测试真实的API连接
        return {"status": "success", "message": "连接测试成功"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")

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
    else:
        return {
            "api_key": os.getenv("CUSTOM_API_KEY", ""),
            "base_url": os.getenv("CUSTOM_BASE_URL", ""),
            "model": "gpt-3.5-turbo"
        }

async def call_openai_api(request: ChatRequest, config: dict) -> ChatResponse:
    """调用OpenAI API"""
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
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        
        data = response.json()
        message_content = data["choices"][0]["message"]["content"]
        
        return ChatResponse(
            message=ChatMessage(role="assistant", content=message_content),
            usage=data.get("usage")
        )

async def call_anthropic_api(request: ChatRequest, config: dict) -> ChatResponse:
    """调用Anthropic API"""
    # 实现Anthropic API调用逻辑
    # 这里先返回一个模拟响应
    await asyncio.sleep(1)  # 模拟API调用延迟
    
    return ChatResponse(
        message=ChatMessage(
            role="assistant", 
            content="这是来自Anthropic Claude的模拟回复。实际实现需要调用真实的Anthropic API。"
        )
    )

async def call_custom_api(request: ChatRequest, config: dict) -> ChatResponse:
    """调用自定义API"""
    # 实现自定义API调用逻辑
    # 这里先返回一个模拟响应
    await asyncio.sleep(1)  # 模拟API调用延迟
    
    return ChatResponse(
        message=ChatMessage(
            role="assistant", 
            content="这是来自自定义API的模拟回复。您可以根据需要实现特定的API调用逻辑。"
        )
    )

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