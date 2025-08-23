<template>
  <div class="chat-container">
    <el-container>
      <el-header height="60px" class="chat-header">
        <div class="header-content">
          <h2>AI 聊天助手</h2>
          <el-button type="primary" @click="$router.push('/settings')">
            <el-icon><Setting /></el-icon>
            设置
          </el-button>
        </div>
      </el-header>
      
      <el-main class="chat-main">
        <div class="messages-container" ref="messagesContainer">
          <div v-for="message in messages" :key="message.id" class="message-item">
            <div :class="['message', message.role]">
              <div class="message-avatar">
                <el-icon v-if="message.role === 'user'"><User /></el-icon>
                <el-icon v-else><ChatDotRound /></el-icon>
              </div>
              <div class="message-content">{{ message.content }}</div>
            </div>
          </div>
        </div>
      </el-main>
      
      <el-footer height="80px" class="chat-footer">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 3 }"
            placeholder="输入你的消息...按Ctrl+Enter发送"
            @keyup.enter.ctrl="sendMessage"
            class="message-input"
          />
          <el-button 
            type="primary" 
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isLoading"
            :loading="isLoading"
            class="send-button"
          >
            发送
          </el-button>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, ChatDotRound, Setting } from '@element-plus/icons-vue'
import { useSettingsStore } from '../stores/settings'
import { chatAPI } from '../services/api'
import type { ChatMessage } from '../services/api'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const settingsStore = useSettingsStore()
const messages = ref<Message[]>([
  {
    id: 1,
    role: 'assistant',
    content: '您好！我是AI助手。当前应用默认运行在演示模式下，您可以直接体验聊天功能。如需使用真实的AI模型，请在设置中配置相应的API密钥。',
    timestamp: new Date()
  }
])

const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  // 检查是否配置了API密钥
  if (!settingsStore.isConfigured()) {
    ElMessage.warning('请先在设置中配置API密钥')
    return
  }

  const userMessage: Message = {
    id: Date.now(),
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const userInput = inputMessage.value
  inputMessage.value = ''
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()

  isLoading.value = true

  try {
    // 准备发送给API的消息历史（只发送最近的10条消息避免上下文过长）
    const recentMessages = messages.value.slice(-10).map(msg => ({
      role: msg.role,
      content: msg.content
    })) as ChatMessage[]

    const response = await chatAPI.sendMessage({
      messages: recentMessages,
      provider: settingsStore.apiSettings.provider,
      model: settingsStore.apiSettings.modelName,
      temperature: settingsStore.apiSettings.temperature,
      max_tokens: settingsStore.apiSettings.maxTokens
    })

    const aiMessage: Message = {
      id: Date.now() + 1,
      role: 'assistant',
      content: response.message.content,
      timestamp: new Date()
    }
    
    messages.value.push(aiMessage)
    await nextTick()
    scrollToBottom()
    
  } catch (error: any) {
    console.error('发送消息失败:', error)
    
    // 显示详细错误信息
    let errorMessage = '发送消息失败'
    let suggestion = ''
    
    if (error.response?.status === 401) {
      errorMessage = 'API认证失败（401错误）'
      suggestion = '建议：1. 检查API密钥是否正确  2. 尝试使用演示模式进行测试'
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
      if (errorMessage.includes('API密钥')) {
        suggestion = '建议：在设置中选择"演示模式"可无需API密钥直接体验'
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error({
      message: errorMessage + (suggestion ? '\n' + suggestion : ''),
      duration: 5000,
      showClose: true
    })
    
    // 添加错误消息到聊天记录
    const errorMsg: Message = {
      id: Date.now() + 1,
      role: 'assistant',
      content: `抱歉，发生了错误：${errorMessage}\n\n${suggestion || '请检查您的API配置是否正确，或在设置中选择演示模式。'}`,
      timestamp: new Date()
    }
    messages.value.push(errorMsg)
    await nextTick()
    scrollToBottom()
  } finally {
    isLoading.value = false
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

onMounted(() => {
  // 加载设置
  settingsStore.loadSettings()
})
</script>

<style scoped>
.chat-container {
  height: 100vh;
  background: #f5f5f5;
}

.chat-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-content h2 {
  margin: 0;
  color: #303133;
}

.chat-main {
  padding: 20px;
  overflow: hidden;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
}

.message-item {
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #409eff;
  color: white;
}

.message.assistant .message-avatar {
  background: #67c23a;
  color: white;
}

.message-content {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  word-wrap: break-word;
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

.chat-footer {
  background: white;
  border-top: 1px solid #e4e7ed;
  padding: 12px 20px;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.send-button {
  flex-shrink: 0;
}
</style>