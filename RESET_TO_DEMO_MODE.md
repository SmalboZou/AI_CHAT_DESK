# 重置为演示模式脚本

## 方法1: 在浏览器控制台中执行

打开应用后，按 F12 打开开发者工具，在控制台中执行以下代码：

```javascript
// 清除现有设置
localStorage.removeItem('aiSettings');

// 设置为演示模式
const demoSettings = {
  provider: 'demo',
  apiKey: 'demo_key',
  baseUrl: 'demo', 
  modelName: 'demo-model',
  temperature: 0.7,
  maxTokens: 2048
};

localStorage.setItem('aiSettings', JSON.stringify(demoSettings));

// 刷新页面
location.reload();
```

## 方法2: 手动在设置界面更改

1. 打开应用
2. 点击右上角"设置"按钮
3. 在"模型提供商"下拉菜单中选择"演示模式（无需API密钥）"
4. 点击"保存设置"
5. 返回聊天界面测试

## 方法3: 删除存储文件

如果是 Electron 应用，可以删除用户数据目录中的存储文件：

**Windows:**
```
%APPDATA%/AI Chat/Local Storage/
```

**macOS:**
```
~/Library/Application Support/AI Chat/Local Storage/
```

**Linux:**
```
~/.config/AI Chat/Local Storage/
```

删除这些文件后重启应用即可恢复默认的演示模式设置。