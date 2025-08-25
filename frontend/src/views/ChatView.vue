<template>
  <div class="chat-container">
    <el-header height="60px" class="chat-header">
      <div class="header-content">
        <h2>AI 聊天助手</h2>
        <el-button type="primary" @click="$router.push('/settings')">
          <el-icon><Setting /></el-icon>
          设置
        </el-button>
      </div>
    </el-header>
    
    <div class="chat-main">
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
        
        <!-- 显示正在流式输出的消息 -->
        <div v-if="currentStreamingMessage" class="message-item">
          <div class="message assistant">
            <div class="message-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="message-content streaming-content">
              {{ currentStreamingMessage.content }}
              <span class="streaming-cursor">|</span>
            </div>
          </div>
        </div>
        
        <!-- 显示载入指示器（仅在非流式模式或等待开始时显示） -->
        <div v-if="isLoading && !currentStreamingMessage" class="message-item">
          <div class="message assistant">
            <div class="message-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="message-content loading-content">
              <el-icon class="loading-icon"><Loading /></el-icon>
              AI正在思考中...
              <el-button type="text" size="small" @click="stopMessage" class="stop-thinking-btn">
                停止
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <el-footer height="auto" class="chat-footer">
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
          v-if="!isLoading"
          type="primary" 
          @click="sendMessage"
          :disabled="!inputMessage.trim()"
          class="send-button"
        >
          发送
        </el-button>
        <el-button 
          v-else
          type="danger" 
          @click="stopMessage"
          class="send-button"
        >
          <el-icon><CircleClose /></el-icon>
          停止
        </el-button>
      </div>
    </el-footer>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, ChatDotRound, Setting, CircleClose, Loading } from '@element-plus/icons-vue'
import { useSettingsStore } from '../stores/settings'
import { chatAPI } from '../services/api'
import type { ChatMessage } from '../services/api'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isStreaming?: boolean
}

const settingsStore = useSettingsStore()
const messages = ref<Message[]>([])

const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()
const abortController = ref<AbortController | null>(null)
const currentStreamingMessage = ref<Message | null>(null)

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
  
  // 创建新的 AbortController 用于取消请求
  abortController.value = new AbortController()

  try {
    // 准备发送给API的消息历史（只发送最近的10条消息避免上下文过长）
    const recentMessages = messages.value.slice(-10).map(msg => ({
      role: msg.role,
      content: msg.content
    })) as ChatMessage[]

    const requestData = {
      messages: recentMessages,
      provider: settingsStore.apiSettings.provider,
      model: settingsStore.apiSettings.modelName,
      temperature: settingsStore.apiSettings.temperature,
      max_tokens: settingsStore.apiSettings.maxTokens,
      api_config: {
        api_key: settingsStore.apiSettings.apiKey,
        base_url: settingsStore.apiSettings.baseUrl,
        model: settingsStore.apiSettings.modelName
      }
    }

    // 根据设置决定是否使用流式输出
    if (settingsStore.apiSettings.streamEnabled) {
      await handleStreamingResponse(requestData)
    } else {
      await handleNormalResponse(requestData)
    }
    
  } catch (error: any) {
    // 如果是用户主动取消的请求，不显示错误信息
    if (error.name === 'AbortError' || error.code === 'ECONNABORTED') {
      console.log('请求已被用户取消')
      ElMessage.info('消息发送已停止')
      return
    }
    
    console.error('发送消息失败:', error)
    
    // 显示详细错误信息
    let errorMessage = '发送消息失败'
    
    if (error.response?.status === 401) {
      errorMessage = 'API认证失败（401错误）'
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error({
      message: errorMessage,
      duration: 5000,
      showClose: true
    })
    
    // 添加错误消息到聊天记录
    const errorMsg: Message = {
      id: Date.now() + 1,
      role: 'assistant',
      content: `抱歉，发生了错误：${errorMessage}\n\n请检查您的API配置是否正确。`,
      timestamp: new Date()
    }
    messages.value.push(errorMsg)
    await nextTick()
    scrollToBottom()
  } finally {
    isLoading.value = false
    currentStreamingMessage.value = null
    abortController.value = null
  }
}

// 处理流式响应
const handleStreamingResponse = async (requestData: any) => {
  // 创建一个临时的流式消息
  const streamingMsg: Message = {
    id: Date.now() + 1,
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    isStreaming: true
  }
  
  currentStreamingMessage.value = streamingMsg
  
  await chatAPI.sendStreamingMessage(
    requestData,
    // onChunk 回调
    (chunk) => {
      if (currentStreamingMessage.value) {
        currentStreamingMessage.value.content = chunk.full_content
        // 自动滚动到底部
        nextTick(() => scrollToBottom())
      }
    },
    // onError 回调
    (error) => {
      console.error('流式响应错误:', error)
      ElMessage.error(`流式响应错误: ${error}`)
      
      // 如果已有部分内容，保存到消息列表
      if (currentStreamingMessage.value && currentStreamingMessage.value.content) {
        const finalMessage = { ...currentStreamingMessage.value, isStreaming: false }
        messages.value.push(finalMessage)
      }
      
      currentStreamingMessage.value = null
    },
    // onComplete 回调
    () => {
      if (currentStreamingMessage.value) {
        // 将流式消息添加到正式消息列表
        const finalMessage = { ...currentStreamingMessage.value, isStreaming: false }
        messages.value.push(finalMessage)
        currentStreamingMessage.value = null
        
        nextTick(() => scrollToBottom())
      }
    },
    abortController.value?.signal
  )
}

// 处理普通（非流式）响应
const handleNormalResponse = async (requestData: any) => {
  const response = await chatAPI.sendMessage(requestData, abortController.value?.signal)
  
  const aiMessage: Message = {
    id: Date.now() + 1,
    role: 'assistant',
    content: response.message.content,
    timestamp: new Date()
  }
  
  messages.value.push(aiMessage)
  await nextTick()
  scrollToBottom()
}

const stopMessage = () => {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
    isLoading.value = false
    
    // 如果有正在进行的流式消息，保存已有内容
    if (currentStreamingMessage.value && currentStreamingMessage.value.content) {
      const finalMessage = { ...currentStreamingMessage.value, isStreaming: false }
      messages.value.push(finalMessage)
      currentStreamingMessage.value = null
      ElMessage.info('已停止生成，保留了部分内容')
    } else {
      ElMessage.info('已停止发送消息')
    }
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    // 使用 requestAnimationFrame 确保在DOM更新后滚动
    requestAnimationFrame(() => {
      messagesContainer.value!.scrollTop = messagesContainer.value!.scrollHeight
    })
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
  display: flex;
  flex-direction: column;
}

.chat-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  flex-shrink: 0;
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
  flex: 1;
  padding: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  margin-bottom: 20px;
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
  flex-shrink: 0;
  position: sticky;
  bottom: 0;
  z-index: 10;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  max-width: 100%;
}

.message-input {
  flex: 1;
}

.send-button {
  flex-shrink: 0;
}

/* 加载指示器样式 */
.loading-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-style: italic;
}

.loading-icon {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.stop-thinking-btn {
  margin-left: auto;
  color: #f56c6c;
  font-size: 12px;
  padding: 2px 8px;
}

.stop-thinking-btn:hover {
  color: #f56c6c;
  background-color: #fef0f0;
}

/* 确保消息区域有足够的滚动空间 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 流式输出的样式 */
.streaming-content {
  position: relative;
}

.streaming-cursor {
  display: inline-block;
  animation: blink 1s infinite;
  color: #409eff;
  font-weight: bold;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}
</style>