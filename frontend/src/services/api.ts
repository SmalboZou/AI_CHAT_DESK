import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
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
}

export interface ChatResponse {
  message: ChatMessage
  usage?: any
}

export const chatAPI = {
  // 发送聊天消息
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    try {
      const response = await api.post('/api/chat', request)
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