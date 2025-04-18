# AI Git Utils: 智能 Git Commit 助手 🚀

[![PyPI version](https://badge.fury.io/py/ai-git-utils.svg)](https://badge.fury.io/py/ai-git-utils) 

**AI Git Utils** 是一个利用 AI 技术增强您 Git 工作流程的智能化工具。它能够根据您的代码变更自动生成规范、清晰且富有表现力的 Commit Message，并智能推荐相关的 Emoji，显著提升版本控制的效率和体验。


![](https://raw.githubusercontent.com/twn39/aigit/main/screen.png)

---

## ✨ 核心特性

*   **🤖 AI 驱动的 Commit Message 生成:** 基于代码 `diff`，智能生成符合 [Conventional Commits](https://www.conventionalcommits.org/) 规范的提交信息（包含 `type`, `scope`, `subject`, `body`）。
*   **✍️ 交互式编辑:** 在 AI 生成建议后，提供便捷的交互式编辑界面，允许您轻松修改和确认最终的 Commit Message。
*   **😄 智能 Emoji 选择:** 根据 Commit 类型自动推荐合适的 Emoji，让您的提交记录更生动、直观。
*   **🔌 多模型支持与灵活配置:**
    *   支持接入多种兼容 OpenAI API 标准的大语言模型 (LLM)。
    *   通过简单的命令行指令即可添加、删除、切换和管理不同的 AI 模型配置。
*   **📜 增强的 Git Log:** 使用 `aigit log` 命令，以美观的表格形式展示提交历史，支持限制数量和时间范围过滤。

---

## 🛠️ 安装

确保您已安装 Python 3.8+。然后通过 pip 安装：

```bash
pip install ai-git-utils
```

---

## ⚙️ 配置 AI 模型

在使用 `aigit commit` 功能前，您需要至少配置一个 AI 模型。

1.  **添加模型配置:**
    运行 `aigit model add` 并根据提示输入模型信息：
    ```bash
    aigit model add
    # Name: my-gpt4o  (自定义模型名称)
    # Model: gpt-4o  (模型 ID)
    # Base Url: https://api.openai.com/v1 (模型服务 API 地址)
    # Temperature: 0.7 (模型温度参数)
    # Api Key: sk-xxxx (您的 API 密钥)
    ```
    添加的第一个模型会自动设为当前激活模型。

2.  **管理模型:**
    *   列出所有已配置模型: `aigit model list`
    *   查看当前激活模型的详细配置: `aigit model show`
    *   激活其他已配置模型: `aigit model active` (根据提示输入名称)
    *   删除指定模型配置: `aigit model remove` (根据提示输入名称)

---

## 🚀 使用指南

### 1. 生成 AI Commit Message (核心功能)

在您的 Git 仓库中，当您有暂存的更改 (staged changes) 时，运行：

```bash
# 默认使用英文生成
aigit commit

# 指定使用中文生成
aigit commit --lang Chinese

# 只针对特定文件的更改生成 commit message
aigit commit --file path/to/your/file.py
```


## 🤝 贡献

欢迎各种形式的贡献！如果您有任何建议、发现 Bug 或想改进功能，请随时：

1.  Fork 本仓库
2.  创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3.  提交您的更改 (`aigit commit` 😉)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  提交 Pull Request
