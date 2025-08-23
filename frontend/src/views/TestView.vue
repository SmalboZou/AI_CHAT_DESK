<template>
  <div class="test-page">
    <h1>Vue + Element Plus 测试页面</h1>
    <p>如果你能看到这个页面，说明Vue正在正常工作。</p>
    
    <div class="test-buttons">
      <el-button @click="showAlert" type="primary">点击测试</el-button>
      <el-button @click="showMessage" type="success">显示消息</el-button>
      <el-button @click="goToChat" type="info">进入聊天页面</el-button>
    </div>
    
    <el-card class="test-card">
      <template #header>
        <span>Element Plus 组件测试</span>
      </template>
      <p>这是一个 Element Plus 卡片组件。</p>
      <el-tag type="success">正常工作</el-tag>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

const showAlert = () => {
  alert('Vue组件工作正常!')
}

const showMessage = () => {
  ElMessage.success('Element Plus 工作正常！')
}

const goToChat = () => {
  router.push('/chat')
}
</script>

<style scoped>
.test-page {
  padding: 20px;
  text-align: center;
  font-family: Arial, sans-serif;
  max-width: 600px;
  margin: 0 auto;
}

h1 {
  color: #42b883;
  margin-bottom: 20px;
}

p {
  margin-bottom: 20px;
  font-size: 16px;
}

.test-buttons {
  margin: 20px 0;
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.test-card {
  margin-top: 20px;
  text-align: left;
}
</style>