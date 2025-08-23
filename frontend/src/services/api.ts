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
    const response = await api.post('/api/chat', request)
    return response.data
  },

  // 测试连接
  testConnection: async (config: any): Promise<any> => {
    const response = await api.post('/api/test-connection', config)
    return response.data
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