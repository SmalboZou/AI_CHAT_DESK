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
    provider: 'demo',  // Default to demo mode
    apiKey: 'demo_key',
    baseUrl: 'demo',
    modelName: 'demo-model',
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
          // 检查是否是非演示模式但缺少API密钥的情况
          if (parsedSettings.provider !== 'demo' && (!parsedSettings.apiKey || parsedSettings.apiKey === '')) {
            console.warn('检测到非演示模式但缺少API密钥，自动设置为演示模式')
            // 自动转换为演示模式
            apiSettings.value = {
              provider: 'demo',
              apiKey: 'demo_key',
              baseUrl: 'demo',
              modelName: 'demo-model',
              temperature: parsedSettings.temperature || 0.7,
              maxTokens: parsedSettings.maxTokens || 2048
            }
            // 保存更新后的设置
            localStorage.setItem('aiSettings', JSON.stringify(apiSettings.value))
          } else {
            apiSettings.value = { ...apiSettings.value, ...parsedSettings }
          }
          console.log('Final settings after merge:', apiSettings.value)
        }
      } else {
        console.log('No saved settings found, using defaults (demo mode)')
      }
    } catch (error) {
      console.warn('加载设置失败，使用默认设置:', error)
      // 清除无效的localStorage数据
      localStorage.removeItem('aiSettings')
      // 确保使用演示模式作为默认
      apiSettings.value = {
        provider: 'demo',
        apiKey: 'demo_key',
        baseUrl: 'demo',
        modelName: 'demo-model',
        temperature: 0.7,
        maxTokens: 2048
      }
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
    // 演示模式不需要真实API密钥
    if (apiSettings.value.provider === 'demo') {
      return true
    }
    return !!apiSettings.value.apiKey && !!apiSettings.value.baseUrl
  }

  return {
    apiSettings,
    loadSettings,
    saveSettings,
    isConfigured
  }
})