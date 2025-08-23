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
    const saved = localStorage.getItem('aiSettings')
    if (saved) {
      const parsedSettings = JSON.parse(saved)
      apiSettings.value = { ...apiSettings.value, ...parsedSettings }
    }
  }

  const saveSettings = (settings: APISettings) => {
    apiSettings.value = { ...settings }
    localStorage.setItem('aiSettings', JSON.stringify(settings))
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