# 智能控制助手 (Intelligent Control Assistant)

## 项目简介

智能控制助手是一个Windows系统命令行应用程序，通过与AI对话让API或本地模型协助用户操控计算机。该应用允许用户通过自然语言与AI交互，让AI帮助完成各种计算机操作任务。

## 功能特点

- 支持多种AI提供商：OpenAI、LM Studio、Ollama
- 提供丰富的系统操作工具：文件管理、系统命令执行、系统信息获取等
- 支持多种编程语言解释器：Python、Node.js等
- 提供友好的命令行界面
- 支持MCP (Model Context Protocol) 协议
- 具有完善的日志记录和错误处理机制

## 环境要求

- Python 3.8或更高版本
- Windows操作系统

## 安装与配置

1. 克隆或下载项目到本地
2. 安装依赖包：
   ```
   pip install -r requirements.txt
   ```
3. 配置AI提供商：
   - 编辑config.json文件，设置AI提供商和API密钥
   - 或者设置环境变量：
     - OPENAI_API_KEY: OpenAI API密钥
     - OPENAI_BASE_URL: OpenAI API基础URL（可选）
     - AI_MODEL: 使用的AI模型（可选）

## 使用方法

1. 直接运行run.bat文件启动程序
2. 或者在命令行中执行：
   ```
   python src/core/app.py
   ```

### 基本命令

- `help`: 显示可用命令列表
- `exit` 或 `quit`: 退出程序
- `clear`: 清除屏幕
- `ls` 或 `dir`: 列出当前目录文件
- `cd <目录名>`: 切换目录
- `pwd`: 显示当前工作目录
- `cat <文件名>`: 显示文件内容
- `echo <文本>`: 输出文本
- `sysinfo`: 显示系统信息

### AI相关命令

- `ai-list`: 列出可用的AI提供商
- `ai-set <提供商> [模型]`: 设置AI提供商和模型
- `ai-config`: 配置AI提供商参数

### 文件操作命令

- `create-dir <目录名>`: 创建目录
- `create-file <文件名> [内容]`: 创建文件
- `write-file <文件名> [内容]`: 写入文件内容
- `read-file <文件名>`: 读取文件内容
- `delete <文件或目录>`: 删除文件或目录

### 系统命令

- `exec <命令>`: 执行系统命令
- `run-as-admin <命令>`: 以管理员权限执行命令
- `process-list`: 列出进程
- `service-list`: 列出服务

### 编程语言执行

- `python <代码>`: 执行Python代码
- `node <代码>`: 执行Node.js代码

## 项目结构

```
IntelligentControl/
├── src/
│   ├── ai_interface/       # AI接口模块
│   ├── config/            # 配置管理
│   ├── core/              # 核心功能
│   ├── tools/             # 工具模块
│   ├── ui/                # 用户界面
│   └── utils/             # 工具函数
├── tests/                 # 测试模块
├── config.json            # 配置文件
├── requirements.txt       # 依赖项
└── run.bat               # 启动脚本
```

## 注意事项

- 首次使用前请确保已正确配置AI提供商
- 执行系统命令时请注意安全，避免执行危险命令
- 程序会记录操作日志，便于排查问题

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 许可证

[MIT License](LICENSE)
