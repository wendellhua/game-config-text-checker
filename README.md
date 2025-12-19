# 🎮 Game Config Text Checker

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Required-orange.svg)](https://ollama.ai/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

**基于AI大模型的游戏配置文本智能审核工具**

[English](#english) | [中文](#简介)

</div>

---

## 简介

Game Config Text Checker 是一个专业的游戏配置文本审核工具，基于本地 Ollama AI 大模型，专门用于检查游戏配置文件（Excel）中的剧情对白、任务文本等内容。支持错别字检测、语病识别、敏感词过滤和内容合规审查。

### ✨ 核心特性

| 功能 | 描述 |
|------|------|
| 🔍 **智能检查** | 基于 AI 大模型进行错别字、语病、敏感词检测 |
| ⚡ **GPU 加速** | 强制使用 GPU 运行，检查速度提升 10-50 倍 |
| 🎯 **结果稳定** | 低温度配置确保相同输入产生相同输出 |
| 🏥 **健康检查** | 自动检测模型状态，未运行时自动启动 |
| 📊 **批量处理** | 支持大规模数据批量检查，自动分批处理 |
| 📝 **详细报告** | 生成 Excel 格式检查报告，包含原文、问题和建议 |
| 🛡️ **容错处理** | 完善的错误处理和 JSON 修复机制 |

### 🎯 检查能力

- ✍️ **错别字检测**：重点检查"的地得"用法、常见错别字
- 📝 **语病识别**：主语混乱、搭配不当、词性误用等
- 🚫 **敏感词过滤**：竞品相关词汇、政治敏感内容
- ✅ **内容合规**：黄赌毒、暴力色情等不当内容

---

## 📋 环境要求

- **Python**: 3.8+
- **Ollama**: [安装指南](https://ollama.ai/)
- **推荐模型**: `qwen3:14b-q4_K_M`
- **显存**: 建议 8GB+ (使用 14B 模型)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/wendellhua/game-config-text-checker.git
cd game-config-text-checker

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 配置 Ollama

```bash
# 启动 Ollama 服务
ollama serve

# 下载推荐模型
ollama pull qwen3:14b-q4_K_M
```

### 3. 运行检查

本工具支持两种使用方式，**推荐使用 AI SKILL 调用方式**：

#### 🌟 方式一：AI SKILL 调用（推荐）

通过 AI 助手（如 Claude）直接调用 SKILL，配合知识库使用效果更佳：

```
使用 SKILL 检查 F:\xxx\task.xlsx 的 xxx_CONF sheet，检查 text 列
```

**结合知识库使用**：

```
@剧情对白知识库 使用 SKILL 检查 F:\xxx\task.xlsx 的 xxx_CONF sheet，检查 text 列
```

> 💡 **优势**：AI 会自动从知识库中获取敏感词列表、文案规范、游戏角色名称等，检查更加智能和全面。

#### 方式二：命令行调用

```bash
# 基本用法
python scripts/conf_check.py "你的配置文件.xlsx" "Sheet名称" "列名"

# 示例
python scripts/conf_check.py "F:\config\task.xlsx" "TASK_CONF" "text"
```

### 4. 查看报告

检查完成后，报告将自动生成在当前目录，文件名格式：`{Sheet名}_{列名}_Check_Report_{日期}.xlsx`

---

## 📖 使用方法

### AI SKILL 调用语法

```
使用 SKILL 检查 <文件路径> 的 <Sheet名称> sheet，检查 <列名> 列
```

**示例**：

```
# 基本检查
使用 SKILL 检查 F:\task.xlsx 的 Sheet1 sheet，检查 对白内容 列

# 配合知识库（推荐）
@剧情对白知识库 使用 SKILL 检查 F:\导出全部对话.xlsx 的 全部对话 sheet，检查 对白内容 列
```

### 命令行参数

```bash
python scripts/conf_check.py <input_file> <sheet_name> <target_column> [options]

位置参数:
  input_file      Excel 配置文件路径
  sheet_name      Sheet 名称
  target_column   目标列名

可选参数:
  --batch-size    每批处理行数 (默认: 30)
  --model         Ollama 模型名称 (默认: qwen3:14b-q4_K_M)
  --column-index  列索引，当存在多个同名列时使用
```

### 命令行示例

```bash
# 基本检查
python scripts/conf_check.py "task.xlsx" "Sheet1" "对白内容"

# 自定义批次大小
python scripts/conf_check.py "task.xlsx" "Sheet1" "text" --batch-size 50

# 使用其他模型
python scripts/conf_check.py "task.xlsx" "Sheet1" "text" --model qwen3:7b

# 多列匹配时指定列索引
python scripts/conf_check.py "task.xlsx" "Sheet1" "text" --column-index 0
```

---

## 📁 项目结构

```
game-config-text-checker/
├── requirements.txt        # Python 依赖
├── LICENSE                 # MIT 许可证
├── README.md               # 项目说明（本文件）
├── CHANGELOG.md            # 更新日志
├── CONTRIBUTING.md         # 贡献指南
├── SKILL.md                # Claude SKILL 定义
├── pyproject.toml          # 项目配置
├── setup.cfg               # 工具配置
├── .gitignore              # Git 忽略规则
│
├── scripts/                # 脚本目录
│   ├── conf_check.py       # 核心检查脚本 ⭐
│   └── skill_executor.py   # SKILL 执行器
│
├── config/                 # 配置目录
│   └── check_config.yaml   # 检查配置文件
│
├── docs/                   # 文档目录
│   ├── USAGE.md            # 详细使用文档
│   ├── FAQ.md              # 常见问题
│   ├── GPU_CONFIG.md       # GPU 配置说明
│   └── MODEL_HEALTH_CHECK.md  # 模型健康检查
│
├── tests/                  # 测试目录
│   ├── __init__.py
│   └── test_conf_check.py  # 单元测试
│
├── examples/               # 示例目录
│   └── README.md           # 示例说明
│
└── reports/                # 报告输出目录
    └── .gitkeep
```

---

## ⚙️ 配置说明

### Ollama 配置

在 `scripts/conf_check.py` 中可以修改以下配置：

```python
# Ollama 服务地址
OLLAMA_URL = "http://localhost:11434/api/generate"

# 模型名称
MODEL_NAME = "qwen3:14b-q4_K_M"

# 批次大小
BATCH_SIZE = 30
```

### 模型推荐

| 模型 | 显存需求 | 速度 | 质量 | 推荐场景 |
|------|----------|------|------|----------|
| `qwen3:7b` | 4GB | ⚡⚡⚡ | ⭐⭐ | 快速检查 |
| `qwen3:14b-q4_K_M` | 8GB | ⚡⚡ | ⭐⭐⭐ | **推荐默认** |
| `qwen3:32b` | 16GB | ⚡ | ⭐⭐⭐⭐ | 精细检查 |

### GPU 优化配置

脚本默认启用 GPU 加速：

```python
"options": {
    "temperature": 0.1,    # 低温度保证结果确定性
    "num_ctx": 8192,       # 上下文窗口
    "num_gpu": 99,         # 使用所有可用 GPU
    "num_predict": 4096    # 最大生成长度
}
```

---

## 📊 检查报告格式

生成的 Excel 报告包含以下列：

| 列名 | 说明 | 示例 |
|------|------|------|
| 行号 | Excel 原始行号 | 260 |
| 配置原文 | 原始文本内容 | "你好，欢迎来到xxxx！" |
| 对白id | 第一列的 ID 值 | "123" |
| 问题说明 | 问题类型和具体描述 | "错别字：'的'应改为'地'" |
| 修改建议 | 具体的修改建议 | "将'的'改为'地'" |

---

## 🛠️ 故障排除

### 常见问题

<details>
<summary><b>模型不存在</b></summary>

```bash
# 查看可用模型
ollama list

# 下载模型
ollama pull qwen3:14b-q4_K_M
```

</details>

<details>
<summary><b>JSON 解析失败</b></summary>

- 减小批次大小：`--batch-size 20`
- 检查调试文件：`llm_debug_*.txt`
- 增大 `num_predict` 参数

</details>

<details>
<summary><b>文件被占用</b></summary>

- 关闭 Excel 中打开的报告文件
- 脚本会自动生成带时间戳的新文件

</details>

<details>
<summary><b>模型启动失败</b></summary>

```bash
# 检查 Ollama 服务状态
curl http://localhost:11434/api/tags

# 重启 Ollama 服务
ollama serve
```

</details>

更多问题请参阅 [FAQ.md](docs/FAQ.md)

---

## 🤝 贡献

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

### 贡献方式

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📝 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

### 最新版本 v2.5

- 📚 项目结构 GitHub 规范化
- 🌟 优先推荐 AI SKILL 调用方式
- 🏥 模型健康度检查和自动启动功能
- ⚡ GPU 加速优化
- 🛡️ 增强 JSON 解析容错处理
- 📊 改进报告格式

---

## 🙏 致谢

- [Ollama](https://ollama.ai/) - 本地 AI 模型运行平台
- [Qwen](https://github.com/QwenLM/Qwen) - 高质量中文 AI 模型
- [pandas](https://pandas.pydata.org/) - 数据处理库

---

## 📞 联系方式

- 提交 [Issue](https://github.com/wendellhua/game-config-text-checker/issues) 报告问题
- 提交 [Pull Request](https://github.com/wendellhua/game-config-text-checker/pulls) 贡献代码

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

</div>
