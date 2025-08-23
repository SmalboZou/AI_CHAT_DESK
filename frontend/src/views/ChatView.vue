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
            placeholder="输入你的消息..."
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
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { User, ChatDotRound, Setting } from '@element-plus/icons-vue'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const messages = ref<Message[]>([
  {
    id: 1,
    role: 'assistant',
    content: '您好！我是AI助手，有什么可以帮助您的吗？',
    timestamp: new Date()
  }
])

const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

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
    // TODO: 调用后端API
    // 这里暂时模拟AI回复
    setTimeout(() => {
      const aiMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `收到您的消息："${userInput}"。这是一个模拟回复，实际回复需要连接到AI服务。`,
        timestamp: new Date()
      }
      messages.value.push(aiMessage)
      isLoading.value = false
      nextTick(() => scrollToBottom())
    }, 1000)
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败，请重试')
    isLoading.value = false
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
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