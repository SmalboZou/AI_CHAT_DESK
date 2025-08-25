import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface APISettings {
  provider: string
  apiKey: string
  baseUrl: string
  modelName: string
  temperature: number
  maxTokens: number
}

export const useSettingsStore = defineStore('settings', () => {
  const apiSettings = ref<APISettings>({
    provider: 'openai',
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    modelName: 'gpt-3.5-turbo',
    temperature: 0.7,
    maxTokens: 2048
  })

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

  const isConfigured = () => {
    return !!apiSettings.value.apiKey && !!apiSettings.value.baseUrl
  }

  return {
    apiSettings,
    loadSettings,
    saveSettings,
    isConfigured
  }
})