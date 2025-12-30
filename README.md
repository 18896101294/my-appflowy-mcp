# AppFlowy MCP Server

> Claude Code 扩展工具，用于将生成的富文本内容自动上传至 AppFlowy

## 📖 项目简介

本项目是一个 Claude Code 扩展工具（MCP Server），用于将生成的富文本内容自动上传至 AppFlowy。它支持 macOS 和 Windows，推荐使用 `uv` 进行环境管理。

## ✨ 功能特性

- 🚀 自动上传富文本内容到 AppFlowy
- 📝 支持 Markdown 语法解析（标题、列表、代码块、加粗、链接等）
- 🔒 安全的环境变量配置管理
- 🖥️ 跨平台支持（macOS、Linux、Windows）

## 🚀 快速开始

### 前置要求

1. **安装 uv**

   - **macOS / Linux**:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```

   - **Windows (PowerShell)**:
     ```powershell
     irm https://astral.sh/uv/install.ps1 | iex
     ```

2. **AppFlowy 账号**
   - 确保已注册 AppFlowy 账号
   - 获取 Workspace ID 和 Parent View ID（见下方说明）

### 获取 AppFlowy 配置信息

1. **Workspace ID**：登录 AppFlowy 后，在设置中可以找到工作空间 ID
2. **Parent View ID**：打开目标文档父级页面，从 URL 或页面设置中获取

## ⚙️ 配置方法

### 🍎 方案 A: macOS / Linux 配置

**配置文件路径**: `~/.claude/config.json`

**配置内容**:

```json
{
  "mcpServers": {
    "appflowy": {
      "command": "uv",
      "args": [
        "run",
        "/Users/xiangzheng/Codes/my-mcp/appflowy/appflowy_skill.py"
      ],
      "env": {
        "APPFLOWY_EMAIL": "your-email@example.com",
        "APPFLOWY_PASSWORD": "your-password",
        "APPFLOWY_WORKSPACE_ID": "your-workspace-id",
        "APPFLOWY_PARENT_VIEW_ID": "your-parent-view-id"
      }
    }
  }
}
```

> ⚠️ **注意**：请将路径 `/Users/xiangzheng/...` 替换为您实际的绝对路径。

### 🪟 方案 B: Windows 配置

**配置文件路径**:
- 通常位于: `%APPDATA%\Claude\config.json`
- 完整路径示例: `C:\Users\YourUserName\AppData\Roaming\Claude\config.json`

> 💡 **提示**: 您可以在文件资源管理器地址栏输入 `%APPDATA%\Claude` 直接跳转。

**配置内容** (注意路径转义):

> ⚠️ Windows 路径中的反斜杠 `\` 在 JSON 中必须写成双反斜杠 `\\`

```json
{
  "mcpServers": {
    "appflowy": {
      "command": "uv",
      "args": [
        "run",
        "C:\\Users\\YourUserName\\Codes\\my-mcp\\appflowy\\appflowy_skill.py"
      ],
      "env": {
        "APPFLOWY_EMAIL": "your-email@example.com",
        "APPFLOWY_PASSWORD": "your-password",
        "APPFLOWY_WORKSPACE_ID": "your-workspace-id",
        "APPFLOWY_PARENT_VIEW_ID": "your-parent-view-id"
      }
    }
  }
}
```

**Windows 特别说明**:

1. **uv 命令**: 确保已安装 `uv` 并添加到 PATH 环境变量。如果不确定，可以将 `"command": "uv"` 改为 `uv.exe` 的完整路径。
2. **路径格式**: 务必使用 `\\` 分隔符（如 `C:\\Users\\...`）。

## ✅ 验证与使用

### 1. 验证配置

配置保存后，需要完全重启 Claude Code：

```bash
# 退出当前 Claude Code 会话
exit

# 重新启动 Claude Code
claude code
```

检查 MCP Server 状态：

```bash
/mcp list
```

如果看到 `appflowy` 状态正常（绿色 ✓），表示配置成功！

### 2. 开始使用

向 Claude 发送指令，例如：

```
把这份代码说明写成文档上传到 AppFlowy，标题是《Windows配置说明》
```

Claude 会自动调用 AppFlowy MCP Server 将内容上传到您配置的 AppFlowy 工作空间。

## 📋 示例用法

- "将这段代码的使用说明整理成文档上传到 AppFlowy"
- "把刚才的分析报告上传到 AppFlowy，标题是《性能分析报告》"
- "创建一个 AppFlowy 文档，标题是《项目进度》，内容是今天完成的任务列表"

## 🔧 故障排查

### MCP Server 启动失败

1. **检查 uv 是否正确安装**:
   ```bash
   uv --version
   ```

2. **检查脚本路径是否正确**:
   - 确保 `appflowy_skill.py` 路径使用绝对路径
   - Windows 用户确保使用 `\\` 转义

3. **检查环境变量是否正确配置**:
   - 确认 `APPFLOWY_EMAIL`、`APPFLOWY_PASSWORD` 等都已填写
   - 确认 Workspace ID 和 Parent View ID 正确

### 上传失败

1. **检查网络连接**: 确保能够访问 AppFlowy 服务
2. **验证凭据**: 确认邮箱和密码正确
3. **检查权限**: 确认账号对目标工作空间有写入权限

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请在 GitHub Issues 中提出。
