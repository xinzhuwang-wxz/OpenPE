
# Vikingbot Console - Gradio 版本

使用 Gradio 实现的纯 Python 控制台界面。

## 运行

```bash
vikingbot gateway
```

这会自动在 http://localhost:18791 启动控制台 Web UI！

## 功能

### 1. Dashboard
- 显示系统状态
- 版本信息
- 配置路径和工作区路径

### 2. Config
- **Skills & Hooks**: 独立标签页
- **Agents / Providers / Channels / Gateway / Tools / Sandbox / Heartbeat**: 每个在自己的标签页中
  - Agents: 展开 AgentDefaults
  - Providers: 每个 provider 在自己的子标签页中
  - Sandbox: backends 在自己的子标签页中
  - Channels: JSON 编辑器（可配置多个 channel）
  - Enums: 使用下拉框（SandboxBackend, SandboxMode）

### 3. Sessions
- 刷新按钮：加载会话列表
- 会话选择：选择会话查看内容
- 会话内容显示：
  - 用户消息：绿色
  - 助手消息：红色
  - 其他消息：黑色

### 4. Workspace
- 使用 Gradio 的 FileExplorer 组件
- 显示工作区文件树
- 选择文件查看内容
