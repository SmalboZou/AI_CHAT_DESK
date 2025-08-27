<template>
  <div id="app" :class="appThemeClass">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useSettingsStore } from './stores/settings'

const settingsStore = useSettingsStore()

// 计算当前主题类名
const appThemeClass = computed(() => {
  const theme = settingsStore.appSettings.theme
  
  if (theme === 'auto') {
    // 自动模式：根据系统偏好决定
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'theme-dark' : 'theme-light'
  }
  
  return theme === 'dark' ? 'theme-dark' : 'theme-light'
})

// 监听系统主题变化（仅在自动模式下）
const setupSystemThemeListener = () => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  
  const handleThemeChange = () => {
    // 强制触发重新计算
    if (settingsStore.appSettings.theme === 'auto') {
      // 通过更新DOM来触发重新渲染
      document.documentElement.className = mediaQuery.matches ? 'theme-dark' : 'theme-light'
    }
  }
  
  mediaQuery.addEventListener('change', handleThemeChange)
  
  // 返回清理函数
  return () => mediaQuery.removeEventListener('change', handleThemeChange)
}

// 监听主题设置变化
watch(
  () => settingsStore.appSettings.theme,
  (newTheme) => {
    console.log('主题变更为:', newTheme)
    // 同时更新document.documentElement的类名，以便全局样式生效
    if (newTheme === 'auto') {
      document.documentElement.className = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'theme-dark' : 'theme-light'
    } else {
      document.documentElement.className = newTheme === 'dark' ? 'theme-dark' : 'theme-light'
    }
  },
  { immediate: true }
)

onMounted(() => {
  // 加载设置
  settingsStore.loadSettings()
  
  // 设置系统主题监听器
  const cleanup = setupSystemThemeListener()
  
  // 组件卸载时清理监听器
  return cleanup
})
</script>

<style>
/* 基础样式 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  transition: background-color 0.3s ease, color 0.3s ease;
}

body {
  margin: 0;
  padding: 0;
}

* {
  box-sizing: border-box;
}

/* CSS 变量定义 */
:root {
  /* 浅色主题变量 */
  --bg-color: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-color: #303133;
  --text-secondary: #606266;
  --border-color: #e4e7ed;
  --shadow-color: rgba(0, 0, 0, 0.1);
}

/* 浅色主题 */
.theme-light {
  --bg-color: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-color: #303133;
  --text-secondary: #606266;
  --border-color: #e4e7ed;
  --shadow-color: rgba(0, 0, 0, 0.1);
}

/* 深色主题 */
.theme-dark {
  --bg-color: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --text-color: #e5e5e5;
  --text-secondary: #b0b0b0;
  --border-color: #404040;
  --shadow-color: rgba(0, 0, 0, 0.3);
}

/* 全局应用主题变量 */
.theme-light,
.theme-dark {
  background-color: var(--bg-color);
  color: var(--text-color);
}

/* Element Plus 深色主题覆盖 */
.theme-dark .el-card {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-card__header {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-form-item__label {
  color: var(--text-color) !important;
}

.theme-dark .el-input__inner {
  background-color: var(--bg-color) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-select .el-input__inner {
  background-color: var(--bg-color) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-textarea__inner {
  background-color: var(--bg-color) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-button {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-button:hover {
  background-color: var(--border-color) !important;
}

.theme-dark .el-header {
  background-color: var(--bg-color) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-main {
  background-color: var(--bg-secondary) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-footer {
  background-color: var(--bg-color) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-scrollbar__wrap {
  background-color: var(--bg-color) !important;
}

.theme-dark .el-message {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-switch__core {
  background-color: var(--border-color) !important;
}

.theme-dark .el-slider__runway {
  background-color: var(--border-color) !important;
}

.theme-dark .el-input-number {
  background-color: var(--bg-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-input-number .el-input__inner {
  background-color: var(--bg-color) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

/* Chat specific dark theme styles */
.theme-dark .chat-container {
  background: var(--bg-secondary) !important;
}

.theme-dark .chat-header {
  background: var(--bg-color) !important;
  border-bottom-color: var(--border-color) !important;
}

.theme-dark .chat-header h2 {
  color: var(--text-color) !important;
}

.theme-dark .chat-main {
  background: var(--bg-secondary) !important;
}

.theme-dark .chat-footer {
  background: var(--bg-color) !important;
  border-top-color: var(--border-color) !important;
}

.theme-dark .message-content {
  background: var(--bg-color) !important;
  color: var(--text-color) !important;
  box-shadow: 0 2px 4px var(--shadow-color) !important;
}

.theme-dark .message.user .message-content {
  background: #409eff !important;
  color: white !important;
}

.theme-dark .loading-content {
  color: var(--text-secondary) !important;
}

/* Settings specific dark theme styles */
.theme-dark .settings-container {
  background: var(--bg-secondary) !important;
}

.theme-dark .settings-header {
  background: var(--bg-color) !important;
  border-bottom-color: var(--border-color) !important;
}

.theme-dark .settings-header h2 {
  color: var(--text-color) !important;
}

.theme-dark .settings-main {
  background: var(--bg-secondary) !important;
}

.theme-dark .setting-description {
  color: var(--text-secondary) !important;
}

/* Scrollbar dark theme */
.theme-dark .messages-container::-webkit-scrollbar-track {
  background: var(--bg-secondary) !important;
}

.theme-dark .messages-container::-webkit-scrollbar-thumb {
  background: var(--border-color) !important;
}

.theme-dark .messages-container::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary) !important;
}

/* Element Plus dropdown and popover dark theme */
.theme-dark .el-select-dropdown {
  background-color: var(--bg-color) !important;
  border-color: var(--border-color) !important;
}

.theme-dark .el-option {
  background-color: var(--bg-color) !important;
  color: var(--text-color) !important;
}

.theme-dark .el-option:hover {
  background-color: var(--bg-secondary) !important;
}

.theme-dark .el-option.selected {
  background-color: var(--bg-secondary) !important;
  color: #409eff !important;
}

.theme-dark .el-popper {
  background-color: var(--bg-color) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}
</style>