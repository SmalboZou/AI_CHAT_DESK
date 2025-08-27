import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ModelInfo } from '../services/api'

export interface APISettings {
  provider: string
  apiKey: string
  baseUrl: string
  modelName: string
  temperature: number
  maxTokens: number
  streamEnabled: boolean
}

export interface AppSettings {
  theme: 'light' | 'dark' | 'auto'
  language: string
  autoSave: boolean
}

export const useSettingsStore = defineStore('settings', () => {
  const apiSettings = ref<APISettings>({
    provider: 'openai',
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    modelName: 'gpt-3.5-turbo',
    temperature: 0.7,
    maxTokens: 2048,
    streamEnabled: true
  })

  const appSettings = ref<AppSettings>({
    theme: 'light',
    language: 'zh',
    autoSave: true
  })

  // 模型列表相关状态
  const availableModels = ref<ModelInfo[]>([])
  const modelsLoading = ref(false)
  const modelsError = ref<string | null>(null)

  const loadSettings = () => {
    try {
      const saved = localStorage.getItem('aiSettings')
      console.log('Loading settings from localStorage:', saved)
      
      if (saved && saved !== 'undefined' && saved !== 'null') {
        const parsedSettings = JSON.parse(saved)
        console.log('Parsed settings:', parsedSettings)
        // 验证解析的数据是否有效
        if (parsedSettings && typeof parsedSettings === 'object') {
          apiSettings.value = { ...apiSettings.value, ...parsedSettings }
          console.log('Final settings after merge:', apiSettings.value)
        }
      } else {
        console.log('No saved settings found, using defaults')
      }
    } catch (error) {
      console.warn('加载设置失败，使用默认设置:', error)
      // 清除无效的localStorage数据
      localStorage.removeItem('aiSettings')
    }
    
    // Load app settings
    try {
      const savedAppSettings = localStorage.getItem('appSettings')
      if (savedAppSettings && savedAppSettings !== 'undefined' && savedAppSettings !== 'null') {
        const parsedAppSettings = JSON.parse(savedAppSettings)
        if (parsedAppSettings && typeof parsedAppSettings === 'object') {
          appSettings.value = { ...appSettings.value, ...parsedAppSettings }
        }
      }
    } catch (error) {
      console.warn('加载应用设置失败，使用默认设置:', error)
      localStorage.removeItem('appSettings')
    }
  }

  const saveSettings = (settings: APISettings) => {
    try {
      apiSettings.value = { ...settings }
      localStorage.setItem('aiSettings', JSON.stringify(settings))
    } catch (error) {
      console.error('保存设置失败:', error)
      throw new Error('保存设置失败，请重试')
    }
  }

  const saveAppSettings = (settings: AppSettings) => {
    try {
      appSettings.value = { ...settings }
      localStorage.setItem('appSettings', JSON.stringify(settings))
    } catch (error) {
      console.error('保存应用设置失败:', error)
      throw new Error('保存应用设置失败，请重试')
    }
  }

  const isConfigured = () => {
    return !!apiSettings.value.apiKey && !!apiSettings.value.baseUrl
  }

  // 模型相关方法
  const setAvailableModels = (models: ModelInfo[]) => {
    availableModels.value = models
  }

  const setModelsLoading = (loading: boolean) => {
    modelsLoading.value = loading
  }

  const setModelsError = (error: string | null) => {
    modelsError.value = error
  }

  const clearModels = () => {
    availableModels.value = []
    modelsError.value = null
  }

  return {
    apiSettings,
    appSettings,
    availableModels,
    modelsLoading,
    modelsError,
    loadSettings,
    saveSettings,
    saveAppSettings,
    isConfigured,
    setAvailableModels,
    setModelsLoading,
    setModelsError,
    clearModels
  }
})