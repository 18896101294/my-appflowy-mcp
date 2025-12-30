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

2. **Python 环境**
   - Python 3.12 或更高版本
   - 可以通过 `python --version` 检查版本

3. **AppFlowy 账号**
   - 确保已注册 AppFlowy 账号
   - 获取 Workspace ID 和 Parent View ID（见下方说明）

### 安装与构建

#### 1. 克隆仓库

```bash
git clone https://github.com/18896101294/my-appflowy-mcp.git
cd my-appflowy-mcp
```

#### 2. 安装依赖

使用 `uv` 自动安装项目依赖：

```bash
# uv 会自动创建虚拟环境并安装依赖
uv sync
```

这将会：
- 自动创建 Python 虚拟环境（如果不存在）
- 安装 `pyproject.toml` 中定义的所有依赖：
  - `mcp >= 1.25.0`
  - `requests >= 2.32.5`
- 生成或更新 `uv.lock` 锁定文件

#### 3. 验证安装

检查依赖是否安装成功：

```bash
# 查看已安装的包
uv pip list
```

你应该能看到 `mcp` 和 `requests` 包已成功安装。

#### 4. 获取项目绝对路径

配置 Claude Code 时需要使用项目的绝对路径：

- **macOS / Linux**:
  ```bash
  # 在项目目录下执行
  pwd
  # 输出示例: /Users/yourname/my-appflowy-mcp
  ```

- **Windows (PowerShell)**:
  ```powershell
  # 在项目目录下执行
  $PWD.Path
  # 输出示例: C:\Users\YourName\my-appflowy-mcp
  ```

记下这个路径，稍后配置时需要使用。

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
        "/path/to/your/my-appflowy-mcp/appflowy_skill.py"
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

> ⚠️ **注意**：
> - 将 `/path/to/your/my-appflowy-mcp/appflowy_skill.py` 替换为上一步获取的**绝对路径** + `/appflowy_skill.py`
> - 例如：如果 `pwd` 输出为 `/Users/john/my-appflowy-mcp`，则完整路径为 `/Users/john/my-appflowy-mcp/appflowy_skill.py`

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
        "C:\\path\\to\\your\\my-appflowy-mcp\\appflowy_skill.py"
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

**路径配置说明**:
> ⚠️ **重要**：
> - 将 `C:\\path\\to\\your\\my-appflowy-mcp\\appflowy_skill.py` 替换为实际路径
> - **必须使用双反斜杠** `\\` 分隔符
> - 例如：如果 `$PWD.Path` 输出为 `C:\Users\John\my-appflowy-mcp`，则配置中应写为：
>   ```
>   "C:\\Users\\John\\my-appflowy-mcp\\appflowy_skill.py"
>   ```

**Windows 特别说明**:

**uv 命令**: 确保已安装 `uv` 并添加到 PATH 环境变量。如果不确定，可以将 `"command": "uv"` 改为 `uv.exe` 的完整路径。

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

### 依赖安装问题

1. **Python 版本不兼容**:
   ```bash
   # 检查 Python 版本
   python --version
   # 或
   python3 --version
   ```
   确保版本 >= 3.12。如果版本过低，请升级 Python。

2. **uv sync 失败**:
   ```bash
   # 清理缓存并重新安装
   uv cache clean
   uv sync --refresh
   ```

3. **虚拟环境问题**:
   ```bash
   # 删除虚拟环境并重新创建
   rm -rf .venv  # macOS/Linux
   # 或
   Remove-Item -Recurse -Force .venv  # Windows PowerShell

   # 重新同步
   uv sync
   ```

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
