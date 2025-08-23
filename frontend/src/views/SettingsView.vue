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
          
          <el-form :model="settings" label-width="120px" class="settings-form">
            <el-form-item label="模型提供商">
              <el-select v-model="settings.provider" placeholder="请选择模型提供商">
                <el-option label="OpenAI" value="openai" />
                <el-option label="Anthropic" value="anthropic" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="API 密钥">
              <el-input
                v-model="settings.apiKey"
                type="password"
                placeholder="请输入API密钥"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="API 基础URL">
              <el-input
                v-model="settings.baseUrl"
                placeholder="请输入API基础URL"
              />
            </el-form-item>
            
            <el-form-item label="模型名称">
              <el-input
                v-model="settings.modelName"
                placeholder="请输入模型名称"
              />
            </el-form-item>
            
            <el-form-item label="温度">
              <el-slider
                v-model="settings.temperature"
                :min="0"
                :max="2"
                :step="0.1"
                show-tooltip
                style="width: 200px;"
              />
            </el-form-item>
            
            <el-form-item label="最大令牌数">
              <el-input-number
                v-model="settings.maxTokens"
                :min="1"
                :max="4096"
                controls-position="right"
              />
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

interface Settings {
  provider: string
  apiKey: string
  baseUrl: string
  modelName: string
  temperature: number
  maxTokens: number
}

interface AppSettings {
  theme: string
  language: string
  autoSave: boolean
}

const settings = ref<Settings>({
  provider: 'openai',
  apiKey: '',
  baseUrl: 'https://api.openai.com/v1',
  modelName: 'gpt-3.5-turbo',
  temperature: 0.7,
  maxTokens: 2048
})

const appSettings = ref<AppSettings>({
  theme: 'light',
  language: 'zh',
  autoSave: true
})

const testing = ref(false)

const saveSettings = () => {
  // TODO: 保存到本地存储或后端
  localStorage.setItem('aiSettings', JSON.stringify(settings.value))
  ElMessage.success('设置已保存')
}

const saveAppSettings = () => {
  // TODO: 保存到本地存储
  localStorage.setItem('appSettings', JSON.stringify(appSettings.value))
  ElMessage.success('应用设置已保存')
}

const testConnection = async () => {
  testing.value = true
  try {
    // TODO: 测试API连接
    // 这里暂时模拟测试
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('连接测试成功')
  } catch (error) {
    console.error('连接测试失败:', error)
    ElMessage.error('连接测试失败')
  } finally {
    testing.value = false
  }
}

const loadSettings = () => {
  const savedSettings = localStorage.getItem('aiSettings')
  if (savedSettings) {
    settings.value = { ...settings.value, ...JSON.parse(savedSettings) }
  }
  
  const savedAppSettings = localStorage.getItem('appSettings')
  if (savedAppSettings) {
    appSettings.value = { ...appSettings.value, ...JSON.parse(savedAppSettings) }
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
</style>