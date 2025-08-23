# 解决 401 认证错误指南

## 问题描述
当您看到以下错误时：
```
响应错误: 401 Request failed with status code 401
连接测试失败: Error: 自定义API错误 (状态码: 401)
```

这表示API认证失败，通常是由于API密钥配置问题导致的。

## 解决方案

### 方案1: 使用演示模式（推荐，无需API密钥）

1. 打开应用后，点击右上角的 **"设置"** 按钮
2. 在 **"模型提供商"** 下拉菜单中选择 **"演示模式（无需API密钥）"**
3. 点击 **"保存设置"** 按钮
4. 点击 **"测试连接"** 验证配置
5. 返回聊天界面，现在可以正常使用了！

### 方案2: 配置真实API密钥

如果您有有效的API密钥，请按以下步骤配置：

#### OpenAI 配置
1. 选择提供商: **OpenAI**
2. API密钥: `sk-xxxxxxxxxx` (从 https://platform.openai.com/api-keys 获取)
3. API基础URL: `https://api.openai.com/v1`
4. 模型名称: `gpt-3.5-turbo` 或 `gpt-4`

#### Anthropic 配置
1. 选择提供商: **Anthropic**
2. API密钥: `sk-ant-xxxxxxxxxx` (从 https://console.anthropic.com/ 获取)
3. API基础URL: `https://api.anthropic.com`
4. 模型名称: `claude-3-sonnet-20240229`

#### 自定义API配置
1. 选择提供商: **自定义**
2. 输入您的API密钥
3. 输入正确的API基础URL
4. 选择合适的模型名称

### 方案3: 使用环境变量配置

1. 复制 `backend/.env.template` 为 `backend/.env`
2. 在 `.env` 文件中填入您的API密钥：
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```
3. 重启应用

## 常见问题

### Q: 我已经输入了API密钥，为什么还是401错误？
A: 请检查：
- API密钥格式是否正确（OpenAI以`sk-`开头，Anthropic以`sk-ant-`开头）
- API密钥是否有效且有足够余额
- 网络连接是否正常
- 是否需要代理设置

### Q: 演示模式有什么限制？
A: 演示模式提供模拟的AI回复，用于测试应用功能。要获得真实的AI服务，需要配置真实的API密钥。

### Q: 如何获取API密钥？
A: 
- OpenAI: 访问 https://platform.openai.com/api-keys
- Anthropic: 访问 https://console.anthropic.com/

## 技术支持

如果以上方案都无法解决问题，请检查：
1. 后端服务是否正常运行在 http://127.0.0.1:8000
2. 浏览器控制台是否有其他错误信息
3. 网络连接和代理设置是否正确