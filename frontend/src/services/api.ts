import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000, // 增加超时时间到60秒，允许AI响应时间更长
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('响应错误:', error.response?.status, error.message)
    
    // 处理网络错误
    if (error.code === 'ECONNREFUSED' || error.message.includes('fetch')) {
      error.message = '无法连接到后端API服务，请检查服务是否正常启动'
    } else if (error.code === 'TIMEOUT_EXCEEDED') {
      error.message = '请求超时，请稍后重试'
    }
    
    return Promise.reject(error)
  }
)

// 聊天相关API
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  provider?: string
  model?: string
  temperature?: number
  max_tokens?: number
  stream?: boolean
  api_config?: any
}

export interface ChatResponse {
  message: ChatMessage
  usage?: any
}

export const chatAPI = {
  // 发送聊天消息（非流式）
  sendMessage: async (request: ChatRequest, signal?: AbortSignal): Promise<ChatResponse> => {
    try {
      const response = await api.post('/api/chat', request, {
        signal: signal
      })
      return response.data
    } catch (error: any) {
      // 提供更详细的错误信息
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      } else if (error.message) {
        throw error
      } else {
        throw new Error('发送消息失败，请稍后重试')
      }
    }
  },

  // 发送流式聊天消息
  sendStreamingMessage: async (
    request: ChatRequest,
    onChunk: (chunk: { type: string; content: string; full_content: string }) => void,
    onError: (error: string) => void,
    onComplete: () => void,
    signal?: AbortSignal
  ): Promise<void> => {
    try {
      // 确保启用流式模式
      const streamRequest = { ...request, stream: true }
      
      const response = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(streamRequest),
        signal: signal
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
        throw new Error(errorData.detail || `服务器错误: ${response.status}`)
      }

      if (!response.body) {
        throw new Error('响应体为空')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          // 将新数据添加到缓冲区
          buffer += decoder.decode(value, { stream: true })
          
          // 处理缓冲区中的完整行
          const lines = buffer.split('\n')
          // 保留最后一个可能不完整的行
          buffer = lines.pop() || ''
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim()
              
              if (dataStr === '[DONE]') {
                onComplete()
                return
              }
              
              try {
                const chunk = JSON.parse(dataStr)
                
                if (chunk.error) {
                  onError(chunk.message || '流式处理发生错误')
                  return
                }
                
                if (chunk.type === 'content') {
                  onChunk(chunk)
                }
              } catch (parseError) {
                console.warn('解析SSE数据失败:', dataStr, parseError)
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }
      
      onComplete()
      
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('流式请求被用户取消')
        return
      }
      
      console.error('流式请求失败:', error)
      onError(error.message || '流式请求失败，请稍后重试')
    }
  },

  // 测试连接
  testConnection: async (config: any): Promise<any> => {
    try {
      const response = await api.post('/api/test-connection', config)
      return response.data
    } catch (error: any) {
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      } else {
        throw new Error('连接测试失败')
      }
    }
  }
}

// 配置相关API
export interface APIConfig {
  provider: string
  api_key: string
  base_url: string
  model: string
}

// 模型信息接口
export interface ModelInfo {
  id: string
  object: string
  created: number
  owned_by: string
  description: string
  type: string
}

// 模型列表响应接口
export interface ModelsResponse {
  object: string
  data: ModelInfo[]
}

export const configAPI = {
  // 保存配置
  saveConfig: async (config: APIConfig): Promise<any> => {
    const response = await api.post('/api/config', config)
    return response.data
  },

  // 获取配置
  getConfig: async (provider: string): Promise<APIConfig> => {
    const response = await api.get(`/api/config/${provider}`)
    return response.data
  },

  // 获取模型列表
  getModels: async (config: APIConfig): Promise<ModelsResponse> => {
    try {
      const response = await api.post('/api/models', config)
      return response.data
    } catch (error: any) {
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      } else {
        throw new Error('获取模型列表失败')
      }
    }
  }
}

// 系统API
export const systemAPI = {
  // 健康检查
  healthCheck: async (): Promise<any> => {
    const response = await api.get('/health')
    return response.data
  },

  // 获取API信息
  getInfo: async (): Promise<any> => {
    const response = await api.get('/')
    return response.data
  }
}

export default api