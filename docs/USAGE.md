# 游戏配置文本检查 - 使用文档

## 📖 目录
- [快速开始](#快速开始)
- [详细使用](#详细使用)
- [配置说明](#配置说明)
- [高级功能](#高级功能)
- [故障排除](#故障排除)
- [最佳实践](#最佳实践)

---

## 快速开始

### 1. 环境准备

#### 安装依赖
```bash
pip install pandas openpyxl requests tqdm pyyaml psutil
```

#### 启动Ollama服务
```bash
# 确保Ollama服务运行
ollama serve

# 下载模型（如果还没有）
ollama pull qwen3:14b-q4_K_M
```

### 2. 基本使用

#### 方式1：通过AI助手（推荐）
直接告诉AI助手：
```
使用SKILL检查 F:\trunk_conf\ExcelDataConfig\task.xlsx 的 TASK_CONF sheet，检查 text 列
```

#### 方式2：命令行
```bash
# 进入项目目录
cd f:\conf_check_tools

# 执行检查
python scripts/skill_executor.py "使用SKILL检查 F:\task.xlsx 的 Sheet1 sheet，检查 text 列"
```

#### 方式3：直接调用脚本
```bash
python scripts/conf_check.py "F:\task.xlsx" "Sheet1" "text"
```

---

## 详细使用

### 命令格式

#### 格式1：自然语言（推荐）
```
使用SKILL检查 <文件路径> 的 <Sheet名> sheet，检查 <列名> 列
```

**示例**：
```
使用SKILL检查 F:\导出全部对话.xlsx 的 全部对话 sheet，检查 对白内容 列
```

#### 格式2：简化格式
```
检查配置文件：<文件路径>，Sheet：<Sheet名>，列：<列名>
```

#### 格式3：直接参数
```bash
python scripts/conf_check.py <文件路径> <Sheet名> <列名> [选项]
```

**可选参数**：
- `--batch-size N`: 批次大小（默认30）
- `--model NAME`: 模型名称（默认qwen3:14b-q4_K_M）
- `--column-index N`: 列索引（当有多个同名列时）

**示例**：
```bash
python scripts/conf_check.py "F:\task.xlsx" "TASK_CONF" "text" --batch-size 50 --model qwen3:7b
```

### 查看任务进度

检查进度会在终端实时显示：

```
============================================================
🚀 配置文本检查工具 v2.0
============================================================

📋 当前配置:
   - 模型名称: qwen3:14b-q4_K_M
   - 输入文件: F:\task.xlsx
   - Sheet名称: TASK_CONF
   - 目标列: text
   - 批次大小: 30 行/批

✅ 共发现 1003 行有效文本，开始分批检查...
📦 批次大小: 30 行/批

AI 检查进度: 100%|██████████| 34/34 [05:23<00:00]

   [1] task_TASK_CONF_text_检查报告_20251217_093015.xlsx
       大小: 45.23 KB
       修改时间: 2025-12-17 09:35:20
```

---

## 配置说明

### 配置文件位置
`config/check_config.yaml`

### 主要配置项

#### 1. Ollama配置
```yaml
ollama:
  url: "http://30.30.51.20:11434/api/generate"
  model: "qwen3:14b-q4_K_M"
  options:
    temperature: 0.1      # 温度（0-1，越低越确定）
    num_ctx: 8192        # 上下文窗口
    num_predict: 4096    # 最大生成长度
```

**模型选择建议**：
- `qwen3:7b` - 速度快，适合快速检查
- `qwen3:14b-q4_K_M` - 平衡推荐
- `qwen3:32b` - 质量高，适合精细检查

#### 2. 文件配置
```yaml
file:
  input_file: "F:\\trunk_conf\\ExcelDataConfig\\task.xlsx"
  sheet_name: "TASK_CONF"
  target_column: "text"
  header_rows: [0, 1, 2]  # 多行表头
```

**表头配置说明**：
- 单行表头：`header_rows: 0`
- 多行表头：`header_rows: [0, 1, 2]`（使用第1、2、3行）

#### 3. 检查参数
```yaml
check:
  batch_size: 30          # 每批处理行数
  timeout: 300            # 超时时间（秒）
```

**批次大小调整**：
- 小批次（10-20）：准确度高，速度慢
- 中批次（30-50）：平衡推荐
- 大批次（50-100）：速度快，可能产生幻觉

---

## 高级功能

### 1. 多列匹配

当Excel中有多个同名列时，可以指定使用第几个：

```bash
python scripts/conf_check.py "F:\task.xlsx" "Sheet1" "text" --column-index 0
```

或在配置文件中设置：
```yaml
file:
  target_column_index: 0  # 使用第1个text列（0-based）
```

### 2. 自定义检查规则

编辑 `scripts/conf_check.py` 中的 `get_check_prompt()` 函数：

```python
def get_check_prompt(batch_data):
    prompt = f"""你是游戏文案审核专家。请检查以下内容：
    
【必查项】
1. 错别字
2. 语病
3. 敏感词
4. 自定义规则...

数据:
{data_str}

输出JSON格式...
"""
    return prompt
```

### 3. 知识库集成

在使用SKILL时引用知识库：

```
@剧情对白知识库 使用SKILL检查 F:\task.xlsx 的 Sheet1 sheet，检查 text 列
```

AI会自动从知识库获取：
- 敏感词列表
- 文案规范
- 游戏角色名称
- 参考数据

### 4. 批量检查多个文件

创建批处理脚本 `batch_check.sh`：

```bash
#!/bin/bash
files=(
    "F:/conf1/task.xlsx:TASK_CONF:text"
    "F:/conf2/dialog.xlsx:DIALOG:content"
    "F:/conf3/story.xlsx:STORY:text"
)

for item in "${files[@]}"; do
    IFS=':' read -r file sheet column <<< "$item"
    echo "检查: $file - $sheet - $column"
    python scripts/conf_check.py "$file" "$sheet" "$column"
done
```

---

## 故障排除

### 问题1：模型不存在

**错误信息**：
```
❌ 错误: 模型 'qwen3:14b-q4_K_M' 不存在！
```

**解决方案**：
```bash
# 查看可用模型
ollama list

# 下载模型
ollama pull qwen3:14b-q4_K_M

# 或修改配置文件使用其他模型
```

### 问题2：JSON解析失败

**错误信息**：
```
⚠️ JSON解析失败: Expecting value: line 1 column 1 (char 0)
```

**原因**：
- 模型输出被截断
- 批次太大导致输出不完整
- 模型返回了非JSON格式

**解决方案**：
1. 减小批次大小：`--batch-size 20`
2. 增加生成长度：修改配置文件中的 `num_predict`
3. 检查调试文件：`llm_debug_*.txt`

### 问题3：文件被占用

**错误信息**：
```
❌ 文件被占用: [Errno 13] Permission denied
```

**解决方案**：
1. 关闭Excel中打开的报告文件
2. 脚本会自动生成带时间戳的新文件

### 问题4：列名找不到

**错误信息**：
```
❌ 错误: 没找到列名 'text'
```

**解决方案**：
1. 查看脚本输出的所有列名列表
2. 修改命令使用正确的列名
3. 脚本支持模糊匹配，会自动匹配包含目标字符串的列名

### 问题5：Ollama连接失败

**错误信息**：
```
⚠️ 无法连接到Ollama服务
```

**解决方案**：
```bash
# 检查Ollama服务状态
curl http://30.30.51.20:11434/api/tags

# 启动Ollama服务
ollama serve

# 检查防火墙设置
```

### 问题6：进度条卡住

**现象**：进度条长时间不动

**可能原因**：
- 模型推理时间长
- 批次数据量大
- GPU资源不足

**解决方案**：
1. 耐心等待（大批次可能需要几分钟）
2. 减小批次大小
3. 检查GPU使用情况：`nvidia-smi`

---

## 最佳实践

### 1. 检查前准备

✅ **环境检查清单**：
- [ ] Ollama服务运行正常
- [ ] 模型已下载
- [ ] Python依赖已安装
- [ ] Excel文件路径正确
- [ ] 关闭Excel中打开的文件

### 2. 参数调优

#### 根据数据量选择批次大小

| 数据量 | 推荐批次 | 预计时间 |
|--------|----------|----------|
| < 100行 | 30-50 | 1-2分钟 |
| 100-1000行 | 30 | 5-10分钟 |
| 1000-5000行 | 20-30 | 15-30分钟 |
| > 5000行 | 20 | 30分钟+ |

#### 根据需求选择模型

| 需求 | 推荐模型 | 特点 |
|------|----------|------|
| 快速检查 | qwen3:7b | 速度快，基本准确 |
| 日常检查 | qwen3:14b-q4_K_M | 平衡性能和质量 |
| 精细检查 | qwen3:32b | 质量高，速度慢 |

### 3. 检查流程

#### 标准检查流程：
1. **准备阶段**
   ```bash
   # 1. 备份原始文件
   cp original.xlsx original_backup.xlsx
   
   # 2. 检查环境
   ollama list
   python --version
   ```

2. **执行检查**
   ```bash
   # 3. 运行检查（进度会实时显示）
   python scripts/skill_executor.py "使用SKILL检查 ..."
   ```

3. **结果处理**
   ```bash
   # 5. 查看报告
   cd reports
   ls -lt | head -5
   
   # 6. 打开最新报告
   start "最新报告.xlsx"
   ```

4. **人工复核**
   - 仔细审阅AI的建议
   - 结合上下文判断
   - 不要盲目接受所有建议

5. **修改和验证**
   - 根据报告修改配置
   - 重新运行检查验证
   - 对比前后报告

### 4. 报告解读

#### 报告列说明

| 列名 | 含义 | 注意事项 |
|------|------|----------|
| 行号 | Excel原始行号 | 可直接定位到Excel |
| 配置原文 | 原始文本 | 用于对比 |
| 对白id | 第一列ID | 用于追溯 |
| 问题说明 | 问题类型和描述 | 重点关注 |
| 修改建议 | 具体修改方案 | 需人工判断 |

#### 问题优先级

**高优先级**（必须修改）：
- ❌ 敏感词（竞品相关）
- ❌ 明显错别字
- ❌ 内容合规问题

**中优先级**（建议修改）：
- ⚠️ 语病
- ⚠️ 成语错用
- ⚠️ 风格不符

**低优先级**（可选修改）：
- 💡 措辞优化建议
- 💡 标点符号建议

### 5. 性能优化

#### 提升检查速度

1. **使用更快的模型**
   ```yaml
   model: "qwen3:7b"  # 比14b快2倍
   ```

2. **增大批次大小**
   ```yaml
   batch_size: 50  # 从30增加到50
   ```

3. **使用多GPU**
   ```yaml
   num_gpu: 99  # 使用所有GPU
   ```

4. **减少上下文窗口**
   ```yaml
   num_ctx: 4096  # 从8192减少到4096
   ```

#### 提升检查质量

1. **使用更好的模型**
   ```yaml
   model: "qwen3:32b"
   ```

2. **减小批次大小**
   ```yaml
   batch_size: 20  # 减少幻觉
   ```

3. **降低温度**
   ```yaml
   temperature: 0.05  # 更确定的输出
   ```

4. **引用知识库**
   ```
   @剧情对白知识库 使用SKILL检查 ...
   ```

---

## 附录

### A. 完整命令参考

```bash
# 基本检查
python scripts/conf_check.py "file.xlsx" "Sheet1" "text"

# 自定义批次
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --batch-size 50

# 自定义模型
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --model qwen3:7b

# 指定列索引
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --column-index 0

# 组合参数
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" \
    --batch-size 50 \
    --model qwen3:7b \
    --column-index 0
```

### B. 配置文件模板

参考 `config/check_config.yaml`

### C. 常用脚本

#### 快速检查脚本
```bash
#!/bin/bash
# quick_check.sh
python scripts/skill_executor.py "使用SKILL检查 $1 的 $2 sheet，检查 $3 列"
```

使用：
```bash
./quick_check.sh "F:\task.xlsx" "Sheet1" "text"
```

#### 批量检查脚本
参考 [高级功能 - 批量检查](#4-批量检查多个文件)

---

## 技术支持

如遇到问题，请：
1. 查看本文档的[故障排除](#故障排除)章节
2. 检查 `llm_debug_*.txt` 调试文件
3. 查看Ollama服务日志
4. 联系技术支持

---

**文档版本**: v2.0  
**最后更新**: 2025-12-17  
**维护者**: AI Assistant
