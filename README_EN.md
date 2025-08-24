# AI Chat Desktop Application

A desktop AI chat application built with Vite + Vue3 + Electron + Python, supporting multiple AI model providers through API integration.

## Technology Stack

- **Frontend**: Vue 3 + Vite + TypeScript
- **Desktop Framework**: Electron
- **Backend**: Python (FastAPI/Flask)
- **Package Management**: 
  - Frontend: npm
  - Backend: uv (Python package manager)

## Environment Setup

### Prerequisites

- Node.js (v18.0.0 or higher)
- Python (v3.9 or higher)
- Git

### Network Configuration

For users in China or those needing faster downloads:

#### Mirror Registry
```bash
# Huawei npm mirror
npm config set registry https://repo.huaweicloud.com/repository/npm/

# Or Tsinghua npm mirror
npm config set registry https://registry.npmmirror.com/

# Tsinghua pip mirror
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Frontend Setup

#### 1. Install Node.js Dependencies Manager

```bash
# Check Node.js version
node --version
npm --version

# Optional: Install pnpm for faster package management
npm install -g pnpm
```

#### 2. Initialize Vue 3 + Vite Project

```bash
# Create Vue 3 project with Vite
npm create vue@latest frontend
# Select: TypeScript, Router, ESLint, Prettier

cd frontend
npm install
```

#### 3. Install Electron

```bash
# Install Electron as dev dependency
npm install --save-dev electron
npm install --save-dev electron-builder
npm install --save-dev concurrently
npm install --save-dev wait-on
```

#### 4. Install Additional Frontend Dependencies

```bash
# UI Framework (choose one)
npm install element-plus  # Element Plus UI
# or
npm install @arco-design/web-vue  # Arco Design Vue

# HTTP Client
npm install axios

# State Management
npm install pinia

# Utility Libraries
npm install lodash-es
npm install @types/lodash-es --save-dev

# Icons
npm install @element-plus/icons-vue
```

### Backend Setup

#### 1. Install UV (Python Package Manager)

```bash
# Install uv
pip install uv

# Or using pipx (recommended)
pipx install uv
```

#### 2. Initialize Python Backend

```bash
# Create backend directory
mkdir backend
cd backend

# Initialize Python project with uv
uv init

# Create virtual environment
uv venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

#### 3. Install Python Dependencies

```bash
# Web framework
uv add fastapi
uv add uvicorn[standard]

# HTTP client for AI API calls
uv add httpx
uv add aiohttp

# Environment management
uv add python-dotenv

# Data validation
uv add pydantic

# CORS middleware
uv add fastapi-cors

# Development dependencies
uv add --dev pytest
uv add --dev black
uv add --dev flake8
uv add --dev mypy
```

### Project Structure

```
AI_RAG/
├── README.md
├── frontend/                 # Vue 3 + Vite + Electron
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/          # Pinia stores
│   │   ├── services/        # API services
│   │   └── types/           # TypeScript types
│   ├── electron/            # Electron main process
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # Python FastAPI
│   ├── src/
│   │   ├── main.py         # FastAPI app
│   │   ├── models/         # Data models
│   │   ├── services/       # AI service integrations
│   │   └── config/         # Configuration
│   ├── pyproject.toml      # UV configuration
│   └── .env                # Environment variables
└── docs/                   # Documentation
```

### Environment Variables

#### Backend (.env file)

```bash
# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Custom Model Providers
CUSTOM_API_KEY=your_custom_api_key_here
CUSTOM_BASE_URL=https://your-custom-api.com/v1

# Server Configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
DEBUG=true

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Development Scripts

#### Frontend package.json scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "electron:dev": "concurrently \"npm run dev\" \"wait-on http://localhost:5173 && electron .\"",
    "electron:build": "npm run build && electron-builder",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mjs --fix --ignore-path .gitignore"
  }
}
```

#### Backend UV scripts

```bash
# Development
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Production
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

# Testing
uv run pytest

# Code formatting
uv run black src/
uv run flake8 src/
```

### Getting Started

1. **Clone and setup the project**:
   ```bash
   git clone <repository-url>
   cd AI_RAG
   ```

2. **Setup Backend**:
   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   uv sync
   cp .env.example .env  # Configure your API keys
   ```

3. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   ```

4. **Start Development**:
   ```bash
   # Terminal 1: Start backend
   cd backend
   uv run uvicorn src.main:app --reload
   
   # Terminal 2: Start frontend
   cd frontend
   npm run electron:dev
   ```

### Troubleshooting

#### Common Issues

1. **Network Issues**: If experiencing network issues, try switching between different mirror configurations
2. **Node Version**: Ensure Node.js version is 18+ for optimal Vite performance
3. **Python Version**: Ensure Python 3.9+ for UV compatibility
4. **Firewall**: Make sure ports 3000, 5173, and 8000 are accessible

#### Network Troubleshooting

```bash
# Reset npm configuration
npm config delete proxy
npm config delete https-proxy
npm config set registry https://registry.npmjs.org/

# Reset git proxy
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### Next Steps

1. Configure AI model provider APIs
2. Implement chat interface components
3. Set up Electron main process
4. Create Python API endpoints
5. Implement real-time communication (WebSocket)
6. Add conversation history storage
7. Package application for distribution

## Contributing

Please read the development guidelines before contributing to this project.

## License

This project is licensed under the MIT License.