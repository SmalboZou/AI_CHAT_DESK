const { contextBridge, ipcRenderer } = require('electron')

// 向渲染进程暴露安全的API
contextBridge.exposeInMainWorld('electronAPI', {
  // 可以在这里添加需要的API方法
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // 系统信息
  getPlatform: () => process.platform,
  
  // 应用信息
  getVersion: () => ipcRenderer.invoke('get-version'),
})