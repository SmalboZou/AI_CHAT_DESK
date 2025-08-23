const { app, BrowserWindow } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let mainWindow
let backendProcess

function createWindow() {
  console.log('创建Electron窗口...')
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    show: true, // 立即显示窗口
    titleBarStyle: 'default',
    autoHideMenuBar: false, // 开发时显示菜单栏
  })

  console.log('窗口创建完成，准备加载URL...')
  
  // 开发环境加载开发服务器，生产环境加载构建文件
  if (process.env.NODE_ENV === 'development') {
    // 动态检测Vite端口
    const devPort = process.env.VITE_DEV_PORT || '5173'
    const devUrl = `http://localhost:${devPort}`
    console.log(`加载开发服务器: ${devUrl}`)
    
    // 等待开发服务器启动
    const waitForServer = async (url, maxAttempts = 30) => {
      for (let i = 0; i < maxAttempts; i++) {
        try {
          const { net } = require('electron')
          const request = net.request(url)
          return new Promise((resolve, reject) => {
            request.on('response', () => resolve(true))
            request.on('error', () => reject(false))
            request.end()
          })
        } catch {
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      }
      return false
    }
    
    // 尝试连接开发服务器
    waitForServer(devUrl).then(() => {
      mainWindow.loadURL(devUrl)
    }).catch(() => {
      console.error('无法连接到开发服务器，尝试备用端口')
      // 尝试其他常见端口
      const alternativePorts = ['5173', '5174', '5175', '3000']
      let found = false
      
      alternativePorts.forEach(async (port) => {
        if (!found) {
          const altUrl = `http://localhost:${port}`
          try {
            if (await waitForServer(altUrl)) {
              console.log(`找到开发服务器在端口 ${port}`)
              mainWindow.loadURL(altUrl)
              found = true
            }
          } catch (e) {
            // 继续尝试下一个端口
          }
        }
      })
    })
    
    // 开发环境下打开开发者工具
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // 当页面准备好时显示窗口
  mainWindow.once('ready-to-show', () => {
    console.log('页面准备就绪，显示窗口')
    mainWindow.show()
  })

  // 当窗口关闭时
  mainWindow.on('closed', () => {
    console.log('窗口已关闭')
    mainWindow = null
  })

  // 添加页面加载错误处理
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error('页面加载失败:', errorCode, errorDescription, validatedURL)
  })

  mainWindow.webContents.on('did-finish-load', () => {
    console.log('页面加载完成')
  })

  // 监听渲染进程的控制台消息
  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`Console [${level}]: ${message}`)
  })

  // 监听JavaScript错误
  mainWindow.webContents.on('crashed', (event) => {
    console.error('渲染进程崩溃')
  })

  mainWindow.webContents.on('unresponsive', () => {
    console.error('渲染进程无响应')
  })
}

// 启动后端服务
function startBackend() {
  // 检查是否需要启动后端（可以通过环境变量控制）
  if (process.env.SKIP_BACKEND === 'true') {
    console.log('跳过后端启动（SKIP_BACKEND=true）')
    return
  }

  const backendPath = path.join(__dirname, '../../backend')
  const pythonPath = path.join(backendPath, '.venv', 'Scripts', 'python.exe')
  const mainPath = path.join(backendPath, 'src', 'main.py')
  
  console.log('正在启动后端服务...')
  
  // 启动Python后端服务
  backendProcess = spawn(pythonPath, [mainPath], {
    cwd: backendPath,
    stdio: process.env.NODE_ENV === 'development' ? 'inherit' : 'pipe', // 开发时显示输出，生产时隐藏
    windowsHide: true // 在Windows上隐藏控制台窗口
  })

  backendProcess.on('error', (err) => {
    console.error('启动后端服务失败:', err)
    console.log('提示：您可以手动启动后端服务：cd backend && uv run python src/main.py')
  })

  backendProcess.on('close', (code) => {
    console.log(`后端进程退出，代码: ${code}`)
  })

  // 监听后端输出（如果需要的话）
  if (backendProcess.stdout) {
    backendProcess.stdout.on('data', (data) => {
      console.log(`后端输出: ${data}`)
    })
  }

  if (backendProcess.stderr) {
    backendProcess.stderr.on('data', (data) => {
      console.error(`后端错误: ${data}`)
    })
  }
}

// 停止后端服务
function stopBackend() {
  if (backendProcess) {
    backendProcess.kill()
    backendProcess = null
  }
}

// 当 Electron 完成初始化并准备创建浏览器窗口时调用此方法
app.whenReady().then(() => {
  startBackend()
  createWindow()

  app.on('activate', () => {
    // 在 macOS 上，当点击 dock 图标并且没有其他窗口打开时，通常在应用程序中重新创建一个窗口
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// 当所有窗口都关闭时退出应用，除了在 macOS 上
app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') app.quit()
})

// 应用退出前清理
app.on('before-quit', () => {
  stopBackend()
})