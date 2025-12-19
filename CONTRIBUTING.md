# 贡献指南

感谢你对 Game Config Text Checker 项目的关注！我们欢迎各种形式的贡献。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [问题反馈](#问题反馈)

---

## 行为准则

请参与者遵循以下行为准则：

- 尊重所有贡献者
- 接受建设性批评
- 关注项目最佳利益
- 展现同理心和友善

---

## 如何贡献

### 贡献方式

1. **报告 Bug**：发现问题请提交 Issue
2. **建议功能**：有好的想法请提交 Feature Request
3. **改进文档**：完善文档和注释
4. **提交代码**：修复 Bug 或实现新功能

### 第一次贡献？

查看标记为 `good first issue` 的 Issue，这些是适合新手的入门任务。

---

## 开发环境设置

### 1. Fork 和克隆

```bash
# Fork 本仓库后克隆到本地
git clone https://github.com/your-username/game-config-text-checker.git
cd game-config-text-checker

# 添加上游仓库
git remote add upstream https://github.com/original-owner/game-config-text-checker.git
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 3. 配置 Ollama

```bash
# 安装 Ollama
# 参考: https://ollama.ai/

# 启动服务
ollama serve

# 下载测试模型
ollama pull qwen3:7b
```

### 4. 运行测试

```bash
# 运行单元测试
python -m pytest tests/

# 运行代码检查
flake8 conf_check.py
```

---

## 代码规范

本项目遵循 PEP 8 编码规范，并有以下额外要求：

### 基本规范

- 使用 4 个空格缩进
- 每行最多 120 个字符
- 使用 UTF-8 编码
- 文件末尾保留一个空行

### 导入规范

```python
# 标准库
import os
import sys

# 第三方库
import pandas as pd
import requests

# 本地模块
from utils import helper
```

### 命名规范

- 函数和变量：`lower_with_under`
- 类名：`CapWords`
- 常量：`CAPS_WITH_UNDER`
- 私有属性：`_single_leading_underscore`

### 文档字符串

```python
def function_name(param1, param2):
    """
    函数简短描述。

    详细描述（如果需要）。

    Args:
        param1: 参数1的描述
        param2: 参数2的描述

    Returns:
        返回值描述

    Raises:
        ValueError: 异常情况描述
    """
    pass
```

### 类型注解

```python
def process_data(data: list[dict]) -> pd.DataFrame:
    """处理数据并返回 DataFrame。"""
    pass
```

---

## 提交规范

### Commit Message 格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构（非新功能或 Bug 修复） |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建过程或辅助工具变动 |

### 示例

```bash
# 新功能
feat(check): add support for multi-column matching

# Bug 修复
fix(json): handle truncated JSON response

# 文档更新
docs(readme): add installation guide

# 重构
refactor(core): extract prompt generation to separate function
```

---

## Pull Request 流程

### 1. 创建分支

```bash
# 更新主分支
git checkout main
git pull upstream main

# 创建特性分支
git checkout -b feature/your-feature-name
```

### 2. 开发和测试

```bash
# 编写代码
# ...

# 运行测试
python -m pytest tests/

# 检查代码风格
flake8 conf_check.py
```

### 3. 提交更改

```bash
git add .
git commit -m "feat(scope): description"
```

### 4. 推送和创建 PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

### PR 检查清单

- [ ] 代码遵循项目代码规范
- [ ] 添加/更新了相关测试
- [ ] 更新了相关文档
- [ ] Commit message 符合规范
- [ ] 所有测试通过
- [ ] 代码已自我审查

---

## 问题反馈

### Bug 报告

提交 Bug 时请包含以下信息：

```markdown
**描述**
简要描述遇到的问题

**复现步骤**
1. 执行命令 '...'
2. 使用参数 '...'
3. 观察到 '...'

**预期行为**
描述你期望发生的事情

**实际行为**
描述实际发生的事情

**环境信息**
- 操作系统: [e.g., Windows 11]
- Python 版本: [e.g., 3.10.0]
- Ollama 版本: [e.g., 0.1.0]
- 模型: [e.g., qwen3:14b-q4_K_M]

**日志输出**
相关的错误日志或调试信息

**附加信息**
其他任何有助于理解问题的信息
```

### 功能建议

提交功能建议时请包含：

```markdown
**功能描述**
简要描述你想要的功能

**使用场景**
描述这个功能在什么场景下有用

**建议实现**
如果有想法，描述可能的实现方式

**替代方案**
描述你考虑过的其他解决方案
```

---

## 开发指南

### 项目结构

```
game-config-text-checker/
├── conf_check.py           # 主程序（核心逻辑）
├── scripts/
│   ├── conf_check.py       # 脚本副本
│   └── skill_executor.py   # SKILL 执行器
├── config/
│   └── check_config.yaml   # 配置文件
├── docs/                   # 文档
├── tests/                  # 测试文件
└── examples/               # 示例文件
```

### 核心模块说明

| 函数 | 说明 |
|------|------|
| `main()` | 主入口函数 |
| `check_model_health()` | 模型健康检查 |
| `call_ollama()` | 调用 Ollama API |
| `parse_llm_response()` | 解析 LLM 响应 |
| `get_check_prompt()` | 生成检查提示词 |
| `load_excel_with_multirow_header()` | 加载多行表头 Excel |
| `find_target_column()` | 查找目标列 |
| `safe_save_excel()` | 安全保存 Excel |

### 添加新的检查规则

修改 `get_check_prompt()` 函数中的提示词：

```python
def get_check_prompt(batch_data):
    prompt = f"""你是游戏文案审核专家。请按照以下规范检查：

【必查项】
1. 错别字
2. 语病
3. 你的新规则...  # 在这里添加

...
"""
    return prompt
```

---

## 许可

通过贡献代码，你同意你的贡献将按照项目的 MIT 许可证进行授权。

---

## 联系方式

如有问题，请通过以下方式联系：

- 提交 [Issue](https://github.com/your-username/game-config-text-checker/issues)
- 发送邮件至项目维护者

---

感谢你的贡献！🎉
