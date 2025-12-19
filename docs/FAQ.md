# 常见问题解答（FAQ）

## 📋 目录
- [安装和环境](#安装和环境)
- [使用问题](#使用问题)
- [性能问题](#性能问题)
- [错误处理](#错误处理)
- [高级问题](#高级问题)

---

## 安装和环境

### Q1: 如何安装Ollama？

**A**: 
```bash
# Windows
# 访问 https://ollama.ai 下载安装包

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama
```

### Q2: 如何下载AI模型？

**A**:
```bash
# 下载推荐模型
ollama pull qwen3:14b-q4_K_M

# 查看已下载的模型
ollama list

# 删除不需要的模型
ollama rm model_name
```

### Q3: Python依赖安装失败怎么办？

**A**:
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者单独安装
pip install pandas openpyxl requests tqdm pyyaml psutil
```

### Q4: 如何检查Ollama服务是否运行？

**A**:
```bash
# 方法1: 使用curl
curl http://localhost:11434/api/tags

# 方法2: 使用浏览器
# 访问 http://localhost:11434

# 方法3: 检查进程
ps aux | grep ollama  # Linux/Mac
tasklist | findstr ollama  # Windows
```

---

## 使用问题

### Q5: 如何使用SKILL检查文件？

**A**: 有三种方式：

**方式1: 通过AI助手（最简单）**
```
使用SKILL检查 F:\task.xlsx 的 Sheet1 sheet，检查 text 列
```

**方式2: 使用SKILL执行器**
```bash
python scripts/skill_executor.py "使用SKILL检查 F:\task.xlsx 的 Sheet1 sheet，检查 text 列"
```

**方式3: 直接调用脚本**
```bash
python scripts/conf_check.py "F:\task.xlsx" "Sheet1" "text"
```

### Q6: 如何查看检查进度？

**A**: 
检查进度会在终端实时显示，包括：
- ✅ 环境验证进度
- 📊 数据加载进度
- 🤖 AI检查进度条（显示当前批次/总批次）
- 📝 问题发现实时提示
- ✨ 报告生成状态

无需额外工具，所有进度信息都会实时输出到终端。

### Q7: 检查报告保存在哪里？

**A**: 
报告保存在 `reports/` 目录下，文件名格式：
```
<Sheet名>_<列名>_Check_Report_<日期时间>.xlsx
```

例如：
```
TASK_CONF_text_Check_Report_20251217_093015.xlsx
```

### Q8: 如何指定使用哪个同名列？

**A**: 当有多个同名列时：

**方法1: 使用命令行参数**
```bash
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --column-index 0
```

**方法2: 修改配置文件**
```yaml
file:
  target_column_index: 0  # 0表示第1个，1表示第2个
```

### Q9: 如何处理多行表头？

**A**: 在配置文件中设置：

**单行表头**：
```yaml
file:
  header_rows: 0  # 使用第1行
```

**多行表头**：
```yaml
file:
  header_rows: [0, 1, 2]  # 使用第1、2、3行
```

### Q10: 如何批量检查多个文件？

**A**: 创建批处理脚本：

**Windows (batch_check.bat)**:
```batch
@echo off
python scripts/conf_check.py "F:\file1.xlsx" "Sheet1" "text"
python scripts/conf_check.py "F:\file2.xlsx" "Sheet1" "text"
python scripts/conf_check.py "F:\file3.xlsx" "Sheet1" "text"
```

**Linux/Mac (batch_check.sh)**:
```bash
#!/bin/bash
files=(
    "F:/file1.xlsx:Sheet1:text"
    "F:/file2.xlsx:Sheet1:text"
)

for item in "${files[@]}"; do
    IFS=':' read -r file sheet column <<< "$item"
    python scripts/conf_check.py "$file" "$sheet" "$column"
done
```

---

## 性能问题

### Q11: 检查速度太慢怎么办？

**A**: 优化方法：

1. **使用更快的模型**
```bash
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --model qwen3:7b
```

2. **增大批次大小**
```bash
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --batch-size 50
```

3. **使用GPU加速**
```yaml
# 在配置文件中
ollama:
  options:
    num_gpu: 99  # 使用所有GPU
```

### Q12: 如何提高检查准确度？

**A**: 优化方法：

1. **使用更好的模型**
```bash
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --model qwen3:32b
```

2. **减小批次大小**
```bash
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --batch-size 20
```

3. **降低温度**
```yaml
ollama:
  options:
    temperature: 0.05  # 更确定的输出
```

4. **引用知识库**
```
@剧情对白知识库 使用SKILL检查 ...
```

### Q13: 内存不足怎么办？

**A**:
1. 减小批次大小：`--batch-size 10`
2. 使用更小的模型：`--model qwen3:7b`
3. 减少上下文窗口：
```yaml
ollama:
  options:
    num_ctx: 4096  # 从8192减少
```

### Q14: GPU显存不足怎么办？

**A**:
1. 使用量化模型：`qwen3:14b-q4_K_M`（已量化）
2. 减少GPU使用：
```yaml
ollama:
  options:
    num_gpu: 1  # 只使用1个GPU
```
3. 使用CPU模式：
```yaml
ollama:
  options:
    num_gpu: 0  # 不使用GPU
```

---

## 错误处理

### Q15: "模型不存在"错误

**错误信息**:
```
❌ 错误: 模型 'qwen3:14b-q4_K_M' 不存在！
```

**解决方案**:
```bash
# 1. 查看可用模型
ollama list

# 2. 下载模型
ollama pull qwen3:14b-q4_K_M

# 3. 或修改配置使用其他模型
```

### Q16: "JSON解析失败"错误

**错误信息**:
```
⚠️ JSON解析失败: Expecting value: line 1 column 1
```

**原因**:
- 模型输出被截断
- 批次太大
- 模型返回非JSON格式

**解决方案**:
```bash
# 1. 减小批次大小
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --batch-size 20

# 2. 检查调试文件
cat llm_debug_*.txt

# 3. 增加生成长度（修改配置文件）
ollama:
  options:
    num_predict: 8192  # 从4096增加
```

### Q17: "文件被占用"错误

**错误信息**:
```
❌ 文件被占用: [Errno 13] Permission denied
```

**解决方案**:
1. 关闭Excel中打开的报告文件
2. 脚本会自动生成带时间戳的新文件
3. 或手动删除旧报告文件

### Q18: "列名找不到"错误

**错误信息**:
```
❌ 错误: 没找到列名 'text'
```

**解决方案**:
1. 查看脚本输出的所有列名
2. 使用正确的列名
3. 脚本支持模糊匹配，会自动匹配包含目标字符串的列名

### Q19: "Ollama连接失败"错误

**错误信息**:
```
⚠️ 无法连接到Ollama服务
```

**解决方案**:
```bash
# 1. 检查服务状态
curl http://localhost:11434/api/tags

# 2. 启动服务
ollama serve

# 3. 检查端口占用
netstat -ano | findstr 11434  # Windows
lsof -i :11434  # Linux/Mac

# 4. 检查防火墙设置
```

### Q20: 进度条卡住不动

**现象**: 进度条长时间不更新

**可能原因**:
- 模型推理时间长
- 批次数据量大
- GPU资源不足

**解决方案**:
1. 耐心等待（大批次可能需要几分钟）
2. 减小批次大小
3. 检查GPU使用情况：
```bash
nvidia-smi  # 查看GPU状态
```
4. 查看Ollama日志：
```bash
journalctl -u ollama -f  # Linux
```

---

## 高级问题

### Q21: 如何自定义检查规则？

**A**: 编辑 `scripts/conf_check.py` 中的 `get_check_prompt()` 函数：

```python
def get_check_prompt(batch_data):
    prompt = f"""你是游戏文案审核专家。请检查以下内容：
    
【必查项】
1. 错别字
2. 语病
3. 敏感词
4. 自定义规则1
5. 自定义规则2

【严禁词汇】
- 自定义敏感词1
- 自定义敏感词2

数据:
{data_str}

输出JSON格式...
"""
    return prompt
```

### Q22: 如何集成知识库？

**A**: 在使用SKILL时引用知识库：

```
@剧情对白知识库 使用SKILL检查 F:\task.xlsx 的 Sheet1 sheet，检查 text 列
```

AI会自动从知识库获取：
- 敏感词列表
- 文案规范
- 游戏角色名称
- 参考数据

### Q23: 如何调试JSON解析问题？

**A**: 
1. 查看调试文件：
```bash
cat llm_debug_batch_*.txt
```

2. 文件内容包括：
- 批次信息
- 原始响应
- 清理后的JSON
- 错误信息

3. 手动验证JSON：
```bash
# 提取JSON部分
cat llm_debug_*.txt | grep -A 100 "清理后的JSON"

# 使用在线工具验证
# https://jsonlint.com/
```

### Q24: 如何优化提示词？

**A**: 提示词优化技巧：

1. **明确输出格式**
```python
prompt = """
输出要求:
1. 有问题输出JSON数组，无问题输出[]
2. 禁止```json标记，禁止任何解释文字
3. 格式:[{"line_no":260,"issue":"问题","suggestion":"建议"}]
"""
```

2. **添加示例**
```python
prompt = """
示例输出:
[
  {"line_no": 100, "issue": "错别字：'的'应为'地'", "suggestion": "将'的'改为'地'"}
]
"""
```

3. **强调约束**
```python
prompt = """
严格要求:
- line_no必须是数字
- 字符串值用英文双引号
- 必须以[开始]结束
"""
```

### Q25: 如何处理大文件？

**A**: 大文件处理策略：

1. **分批检查**
```bash
# 检查前1000行
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --max-rows 1000

# 检查1000-2000行
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --start-row 1000 --max-rows 1000
```

2. **增加超时时间**
```yaml
check:
  timeout: 600  # 从300秒增加到600秒
```

3. **使用更快的模型**
```bash
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --model qwen3:7b
```

### Q26: 如何导出检查统计？

**A**: 使用Python脚本分析报告：

```python
import pandas as pd

# 读取报告
df = pd.read_excel("reports/report.xlsx")

# 统计问题类型
issue_types = df['问题说明'].str.extract(r'(错别字|语病|敏感词|合规)')[0].value_counts()
print(issue_types)

# 统计问题数量
print(f"总问题数: {len(df)}")
print(f"涉及行数: {df['行号'].nunique()}")
```

### Q27: 如何实现自动化检查？

**A**: 创建定时任务：

**Windows (任务计划程序)**:
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（每天、每周等）
4. 操作：运行程序
   - 程序：`python`
   - 参数：`scripts/conf_check.py "file.xlsx" "Sheet1" "text"`
   - 起始于：`f:\conf_check_tools`

**Linux (cron)**:
```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天凌晨2点执行）
0 2 * * * cd /path/to/conf_check_tools && python scripts/conf_check.py "file.xlsx" "Sheet1" "text"
```

### Q28: 如何备份和恢复配置？

**A**:
```bash
# 备份配置
cp config/check_config.yaml config/check_config.yaml.backup

# 恢复配置
cp config/check_config.yaml.backup config/check_config.yaml

# 版本控制（推荐）
git init
git add config/
git commit -m "保存配置"
```

### Q29: 如何升级模型？

**A**:
```bash
# 1. 查看当前模型
ollama list

# 2. 下载新模型
ollama pull qwen3:latest

# 3. 测试新模型
python scripts/conf_check.py "file.xlsx" "Sheet1" "text" --model qwen3:latest

# 4. 更新配置文件
# 修改 config/check_config.yaml 中的 model 字段

# 5. 删除旧模型（可选）
ollama rm qwen3:14b-q4_K_M
```

### Q30: 如何贡献代码？

**A**: 
1. Fork项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -m "Add new feature"`
4. 推送分支：`git push origin feature/new-feature`
5. 创建Pull Request

---

## 📞 获取帮助

如果以上FAQ没有解决你的问题：

1. 查看 [docs/USAGE.md](USAGE.md) 详细文档
2. 查看 [SKILL.md](../SKILL.md) 核心定义
3. 检查 `llm_debug_*.txt` 调试文件
4. 联系技术支持

---

**文档版本**: v2.0  
**最后更新**: 2025-12-17  
**维护者**: AI Assistant
