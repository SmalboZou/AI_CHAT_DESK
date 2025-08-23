# AI 聊天桌面应用程序

基于 Vite + Vue3 + Electron + Python 构建的桌面AI聊天应用，支持通过API集成多个AI模型提供商。

## 技术栈

- **前端**: Vue 3 + Vite + TypeScript
- **桌面框架**: Electron
- **后端**: Python (FastAPI/Flask)
- **包管理器**: 
  - 前端: npm
  - 后端: uv (Python 包管理器)

## 环境配置

### 前置要求

- Node.js (v18.0.0 或更高版本)
- Python (v3.9 或更高版本)
- Git

### 网络配置

针对中国用户或需要代理访问的用户：

#### 代理设置
```bash
# 为 npm 设置代理
npm config set proxy http://192.168.1.104:7890
npm config set https-proxy http://192.168.1.104:7890

# 为 git 设置代理
git config --global http.proxy http://192.168.1.104:7890
git config --global https.proxy http://192.168.1.104:7890

# 为 Python pip/uv 设置代理
export HTTP_PROXY=http://192.168.1.104:7890
export HTTPS_PROXY=http://192.168.1.104:7890
```

#### 镜像源配置（代理的替代方案）
```bash
# 华为 npm 镜像
npm config set registry https://repo.huaweicloud.com/repository/npm/

# 或者清华 npm 镜像
npm config set registry https://registry.npmmirror.com/

# 清华 pip 镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 前端环境配置

#### 1. 安装 Node.js 依赖管理器

```bash
# 检查 Node.js 版本
node --version
npm --version

# 可选：安装 pnpm 以获得更快的包管理
npm install -g pnpm
```

#### 2. 初始化 Vue 3 + Vite 项目

```bash
# 使用 Vite 创建 Vue 3 项目
npm create vue@latest frontend
# 选择：TypeScript, Router, ESLint, Prettier

cd frontend
npm install
```

#### 3. 安装 Electron

```bash
# 安装 Electron 作为开发依赖
npm install --save-dev electron
npm install --save-dev electron-builder
npm install --save-dev concurrently
npm install --save-dev wait-on
```

#### 4. 安装其他前端依赖

```bash
# UI 框架（选择其一）
npm install element-plus  # Element Plus UI
# 或者
npm install @arco-design/web-vue  # Arco Design Vue

# HTTP 客户端
npm install axios

# 状态管理
npm install pinia

# 工具库
npm install lodash-es
npm install @types/lodash-es --save-dev

# 图标
npm install @element-plus/icons-vue
```

### 后端环境配置

#### 1. 安装 UV（Python 包管理器）

```bash
# 安装 uv
pip install uv

# 或者使用 pipx（推荐）
pipx install uv
```

#### 2. 初始化 Python 后端

```bash
# 创建后端目录
mkdir backend
cd backend

# 使用 uv 初始化 Python 项目
uv init

# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

#### 3. 安装 Python 依赖

```bash
# Web 框架
uv add fastapi
uv add uvicorn[standard]

# 用于 AI API 调用的 HTTP 客户端
uv add httpx
uv add aiohttp

# 环境变量管理
uv add python-dotenv

# 数据验证
uv add pydantic

# CORS 中间件
uv add fastapi-cors

# 开发依赖
uv add --dev pytest
uv add --dev black
uv add --dev flake8
uv add --dev mypy
```

### 项目结构

```
AI_RAG/
├── README.md
├── frontend/                 # Vue 3 + Vite + Electron
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── services/        # API 服务
│   │   └── types/           # TypeScript 类型定义
│   ├── electron/            # Electron 主进程
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # Python FastAPI
│   ├── src/
│   │   ├── main.py         # FastAPI 应用
│   │   ├── models/         # 数据模型
│   │   ├── services/       # AI 服务集成
│   │   └── config/         # 配置文件
│   ├── pyproject.toml      # UV 配置
│   └── .env                # 环境变量
└── docs/                   # 文档
```

### 环境变量配置

#### 后端 (.env 文件)

```bash
# AI 模型配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com

# 自定义模型提供商
CUSTOM_API_KEY=your_custom_api_key_here
CUSTOM_BASE_URL=https://your-custom-api.com/v1

# 服务器配置
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
DEBUG=true

# CORS 配置
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 开发脚本

#### 前端 package.json 脚本

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "electron:dev": "concurrently \"npm run dev\" \"wait-on http://localhost:5173 && electron .\"",
    "electron:build": "npm run build && electron-builder",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore"
  }
}
```

#### 后端 UV 脚本

```bash
# 开发环境
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# 生产环境
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

# 测试
uv run pytest

# 代码格式化
uv run black src/
uv run flake8 src/
```

### 🚀 快速启动

#### 方法1: 标准开发命令（推荐）
```bash
cd frontend
npm run dev    # 启动Vite + Electron + 自动启动后端
```
> ℹ️ **说明**: 这个命令会自动启动后端Python服务，不需要手动启动后端

#### 方法2: 仅启动前端（不启动后端）
```bash
cd frontend
npm run dev:frontend-only    # 仅启动Vite + Electron，不启动后端
```
> ℹ️ **说明**: 如果您已经手动启动了后端，或者不需要后端服务

#### 方法3: 完整启动（双重后端）
```bash
cd frontend
npm run full:dev    # 同时启动两个后端实例（不推荐）
```

#### 方法4: 手动分别启动
```bash
# 终端1: 启动后端
cd backend
uv run python src/main.py

# 终端2: 启动前端（不启动后端）
cd frontend
npm run dev:frontend-only
```

#### 方法5: 单独组件启动
```bash
# 仅启动Vite开发服务器
cd frontend
npm run dev:vite

# 仅启动Electron（需要Vite已运行）
cd frontend
npm run dev:electron

# 启动后端API服务器
cd frontend  
npm run backend:start
```

### 故障排除

#### 常见问题

1. **代理问题**：如果遇到网络问题，尝试在代理和镜像配置之间切换
2. **Node 版本**：确保 Node.js 版本为 18+ 以获得最佳 Vite 性能
3. **Python 版本**：确保 Python 3.9+ 以兼容 UV
4. **防火墙**：确保端口 3000、5173 和 8000 可访问

#### 网络故障排除

```bash
# 测试代理连接
curl --proxy http://192.168.1.104:7890 https://www.google.com

# 重置 npm 配置
npm config delete proxy
npm config delete https-proxy
npm config set registry https://registry.npmjs.org/

# 重置 git 代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 后续步骤

1. 配置 AI 模型提供商 API
2. 实现聊天界面组件
3. 设置 Electron 主进程
4. 创建 Python API 端点
5. 实现实时通信（WebSocket）
6. 添加对话历史存储
7. 打包应用程序用于分发

## 贡献指南

在为此项目贡献代码之前，请阅读开发指南。

## 许可证

本项目采用 MIT 许可证。