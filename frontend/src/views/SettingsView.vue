<template>
  <div class="settings-container">
    <el-container>
      <el-header height="60px" class="settings-header">
        <div class="header-content">
          <el-button @click="$router.push('/')" type="text">
            <el-icon><ArrowLeft /></el-icon>
            返回聊天
          </el-button>
          <h2>设置</h2>
        </div>
      </el-header>
      
      <el-main class="settings-main">
        <el-card class="settings-card">
          <template #header>
            <span>AI 模型配置</span>
          </template>
          
          <el-form :model="formSettings" label-width="120px" class="settings-form">
            <el-form-item label="模型提供商">
              <el-select v-model="formSettings.provider" placeholder="请选择模型提供商" @change="onProviderChange">
                <el-option label="OpenAI" value="openai" />
                <el-option label="Anthropic" value="anthropic" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="API 密钥">
              <el-input
                v-model="formSettings.apiKey"
                type="password"
                placeholder="请输入API密钥"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="API 基础URL">
              <el-input
                v-model="formSettings.baseUrl"
                placeholder="请输入API基础URL"
              />
            </el-form-item>
            
            <el-form-item label="模型名称">
              <el-input
                v-model="formSettings.modelName"
                placeholder="请输入模型名称"
              />
            </el-form-item>
            
            <el-form-item label="温度">
              <el-slider
                v-model="formSettings.temperature"
                :min="0"
                :max="2"
                :step="0.1"
                show-tooltip
                style="width: 200px;"
              />
            </el-form-item>
            
            <el-form-item label="最大令牌数">
              <el-input-number
                v-model="formSettings.maxTokens"
                :min="1"
                :max="4096"
                controls-position="right"
              />
            </el-form-item>
            
            <el-form-item label="流式输出">
              <el-switch 
                v-model="formSettings.streamEnabled"
                active-text="启用"
                inactive-text="禁用"
              />
              <div class="setting-description">
                启用后，AI响应将逐字显示，提供更好的用户体验
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存设置</el-button>
              <el-button @click="testConnection" :loading="testing">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card class="settings-card">
          <template #header>
            <span>应用设置</span>
          </template>
          
          <el-form label-width="120px" class="settings-form">
            <el-form-item label="主题">
              <el-select v-model="appSettings.theme" placeholder="请选择主题">
                <el-option label="浅色" value="light" />
                <el-option label="深色" value="dark" />
                <el-option label="自动" value="auto" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="语言">
              <el-select v-model="appSettings.language" placeholder="请选择语言">
                <el-option label="中文" value="zh" />
                <el-option label="English" value="en" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="自动保存对话">
              <el-switch v-model="appSettings.autoSave" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveAppSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useSettingsStore, type APISettings } from '../stores/settings'
import { configAPI, chatAPI } from '../services/api'
import type { ChatMessage } from '../services/api'

interface AppSettings {
  theme: string
  language: string
  autoSave: boolean
}

const settingsStore = useSettingsStore()

// Create local reactive form data
const formSettings = ref<APISettings>({
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

const testing = ref(false)

const saveSettings = async () => {
  try {
    // 保存到store和本地存储
    settingsStore.saveSettings(formSettings.value)
    
    // 同时保存到后端
    await configAPI.saveConfig({
      provider: formSettings.value.provider,
      api_key: formSettings.value.apiKey,
      base_url: formSettings.value.baseUrl,
      model: formSettings.value.modelName
    })
    
    ElMessage.success('设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  }
}

const saveAppSettings = () => {
  localStorage.setItem('appSettings', JSON.stringify(appSettings.value))
  ElMessage.success('应用设置已保存')
}

const testConnection = async () => {
  console.log('Testing connection with provider:', formSettings.value.provider)
  
  if (!formSettings.value.apiKey) {
    ElMessage.warning('请先输入API密钥')
    return
  }
  
  testing.value = true
  try {
    // Use the dedicated test connection API instead of sendMessage
    const response = await chatAPI.testConnection({
      provider: formSettings.value.provider,
      api_key: formSettings.value.apiKey,
      base_url: formSettings.value.baseUrl,
      model: formSettings.value.modelName
    })
    
    if (response && response.status === 'success') {
      ElMessage.success('连接测试成功！API响应正常')
    } else {
      ElMessage.error('连接测试失败：收到异常响应')
    }
  } catch (error: any) {
    console.error('连接测试失败:', error)
    let errorMsg = '连接测试失败'
    
    if (error.response?.status === 401) {
      errorMsg = 'API认证失败（401错误）'
    } else if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail
    } else if (error.message) {
      errorMsg = error.message
    }
    
    ElMessage.error({
      message: errorMsg,
      duration: 5000,
      showClose: true
    })
  } finally {
    testing.value = false
  }
}

const loadSettings = () => {
  // 从store加载设置
  settingsStore.loadSettings()
  
  console.log('Loaded settings from store:', settingsStore.apiSettings)
  
  // 同步到表单数据
  formSettings.value = { ...settingsStore.apiSettings }
  
  console.log('Final form settings:', formSettings.value)
  
  const savedAppSettings = localStorage.getItem('appSettings')
  if (savedAppSettings) {
    appSettings.value = { ...appSettings.value, ...JSON.parse(savedAppSettings) }
  }
}

// 当provider改变时，更新默认设置
const onProviderChange = () => {
  if (formSettings.value.provider === 'openai') {
    formSettings.value.baseUrl = 'https://api.openai.com/v1'
    formSettings.value.modelName = 'gpt-3.5-turbo'
    formSettings.value.apiKey = ''
  } else if (formSettings.value.provider === 'anthropic') {
    formSettings.value.baseUrl = 'https://api.anthropic.com'
    formSettings.value.modelName = 'claude-3-sonnet-20240229'
    formSettings.value.apiKey = ''
  } else if (formSettings.value.provider === 'custom') {
    formSettings.value.baseUrl = ''
    formSettings.value.modelName = 'gpt-3.5-turbo'
    formSettings.value.apiKey = ''
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-container {
  height: 100vh;
  background: #f5f5f5;
}

.settings-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.header-content h2 {
  margin: 0;
  color: #303133;
}

.settings-main {
  padding: 20px;
  overflow-y: auto;
}

.settings-card {
  margin-bottom: 20px;
  max-width: 600px;
}

.settings-form {
  max-width: 500px;
}

.setting-description {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}
</style>