import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
  },
  {
    path: '/test',
    name: 'Test',
    component: () => import('@/views/TestView.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
  },
]

const router = createRouter({
  // 使用hash模式以支持Electron
  history: createWebHashHistory(),
  routes,
})

export default router