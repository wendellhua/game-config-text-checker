# -*- coding: utf-8 -*-
import pandas as pd
import requests
import json
import re
import time
import os
import sys
import argparse
from tqdm import tqdm
from datetime import datetime
import math

# 修复Windows控制台编码问题（使用line_buffering确保实时输出）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

# 立即输出启动信息，确保脚本正在运行
print("🔄 正在初始化...", flush=True)
# ================= 配置区域 =================
# 1. 模型配置
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_API_URL = "http://localhost:11434/api"  # Ollama API基础URL
MODEL_NAME = "qwen3:14b-q4_K_M"  # 修改此处后保存文件，重新运行脚本即可生效

# 2. 文件路径配置
INPUT_FILE = "F:\\XXX.xlsx"  # 你的配置文件路径
SHEET_NAME = "XXX_CONF"           # 要检查的 Sheet 名称
TARGET_COLUMN = "XXX"   # 存中文文案的那一列的表头名称（第3行表头是"text"，会自动模糊匹配到"optional_string_text"）
TARGET_COLUMN_INDEX = None  # 可选：当存在多个同名列时，指定使用第几个（从0开始，None表示使用第一个匹配的列）
# 示例：如果有3个"text"列，TARGET_COLUMN_INDEX=0表示第1个，1表示第2个，2表示第3个

# 3. 表头配置（重要！）
HEADER_ROWS = [0, 1, 2]  # 使用第1、2、3行作为表头（对应Excel的第1-3行）
# 说明：
# - 第1行: optional, string, text 等类型定义
# - 第2行: string, bool, int64 等数据类型
# - 第3行: text, editor_name, id 等字段名
# - 第4行: 中文说明（"对白内容"等）会被跳过
# - 第5行: 数字行会被跳过
# - 第6行开始: 实际数据

# 4. 检查参数
BATCH_SIZE = 30  # 每次发给 AI 30 行数据，根据显存情况调整，太大容易幻觉
OUTPUT_FILE = f"{SHEET_NAME}_{TARGET_COLUMN}_Check_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"  # 文件名包含日期，避免覆盖
# ===========================================

def get_check_prompt(batch_data):
    """
    构造 Prompt，要求返回严格的 JSON 格式（整合洛克王国文案规范）
    """
    data_str = json.dumps(batch_data, ensure_ascii=False, indent=2)
    
    prompt = f"""你是洛克王国游戏文案审核专家。请严格按照以下规范检查剧情对白文本：

【必查项】
1. 错别字（重点：的地得用法、悉悉索索→窸窸窣窣）
2. 语病（主语混乱、缺少主语、搭配不当、词性误用、数量表达混乱）
3. 成语错用（负隅顽抗、娓娓道来、逡巡不前等贬义/褒义误用）
4. 多字/漏字
5. 内容合规:明确触及政治敏感、暴力色情、黄赌毒，不要过多扩展

【忽略项】
- 重复内容、非中文文本、标点符号、数字、NPC和精灵名字

数据:
{data_str}

输出要求:
1. 有问题输出JSON数组，无问题输出[]
2. 禁止```json标记，禁止任何解释文字
3. 格式:[{{"line_no":260,"issue":"问题类型：具体问题","suggestion":"修改建议"}}]
4. line_no必须是数字，字符串值用英文双引号
5. 必须以[开始]结束，确保完整

直接输出:"""
    return prompt

def check_ollama_models():
    """
    检查Ollama可用的模型列表
    
    Returns:
        list: 可用的模型名称列表，如果失败返回None
    """
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            models = [model['name'] for model in models_data.get('models', [])]
            return models
        else:
            print(f"⚠️ 获取模型列表失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ 无法连接到Ollama服务: {e}")
        return None

def check_model_health(model_name):
    """
    检查模型健康度，如果模型未运行则自动启动
    
    Args:
        model_name: 模型名称
    
    Returns:
        bool: 模型是否健康可用
    """
    print(f"🏥 正在检查模型健康度: {model_name}")
    
    # 1. 检查Ollama服务是否可访问
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags", timeout=5)
        if response.status_code != 200:
            print(f"❌ Ollama服务不可用 (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ 无法连接到Ollama服务: {e}")
        print(f"💡 请确保Ollama服务正在运行")
        return False
    
    # 2. 检查模型是否已加载（通过尝试生成来测试）
    print(f"🔍 测试模型响应...")
    test_payload = {
        "model": model_name,
        "prompt": "测试",
        "stream": False,
        "options": {
            "temperature": 0.1,  # 低温度保证结果确定性
            "num_ctx": 8192,     # 上下文窗口
            "num_gpu": 99,       # 使用所有可用GPU
            "num_predict": 1     # 测试只需要生成1个token
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=test_payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ 模型健康检查通过: {model_name}")
            return True
        elif response.status_code == 404:
            print(f"⚠️ 模型未加载，正在启动模型...")
            return start_model(model_name)
        else:
            print(f"⚠️ 模型响应异常 (HTTP {response.status_code})")
            return False
    except requests.exceptions.Timeout:
        print(f"⚠️ 模型响应超时，可能未加载，正在启动模型...")
        return start_model(model_name)
    except Exception as e:
        print(f"⚠️ 模型测试失败: {e}")
        return False

def start_model(model_name):
    """
    启动指定的Ollama模型
    
    Args:
        model_name: 模型名称
    
    Returns:
        bool: 启动是否成功
    """
    print(f"🚀 正在启动模型: {model_name}")
    print(f"📝 执行命令: ollama run {model_name}")
    
    try:
        import subprocess
        # 使用subprocess启动模型（后台运行）
        # 注意：ollama run 会加载模型到内存
        process = subprocess.Popen(
            ["ollama", "run", model_name, "--verbose"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )
        
        # 发送一个简单的测试输入并立即退出
        try:
            process.stdin.write("测试\n")
            process.stdin.write("/bye\n")
            process.stdin.flush()
        except:
            pass
        
        # 等待模型加载（大模型需要较长时间）
        print(f"⏳ 等待模型加载（约15-30秒）...")
        time.sleep(15)
        
        # 验证模型是否成功加载（多次尝试）
        test_payload = {
            "model": model_name,
            "prompt": "测试",
            "stream": False,
            "options": {
                "temperature": 0.1,  # 低温度保证结果确定性
                "num_ctx": 8192,     # 上下文窗口
                "num_gpu": 99,       # 使用所有可用GPU
                "num_predict": 1     # 测试只需要生成1个token
            }
        }
        
        max_retries = 3
        for i in range(max_retries):
            try:
                print(f"🔍 验证模型状态 ({i+1}/{max_retries})...")
                response = requests.post(OLLAMA_URL, json=test_payload, timeout=30)
                if response.status_code == 200:
                    print(f"✅ 模型启动成功: {model_name}")
                    return True
                else:
                    print(f"⚠️ 模型响应异常 (HTTP {response.status_code})")
                    if i < max_retries - 1:
                        print(f"⏳ 等待5秒后重试...")
                        time.sleep(5)
            except requests.exceptions.Timeout:
                print(f"⚠️ 验证超时")
                if i < max_retries - 1:
                    print(f"⏳ 等待5秒后重试...")
                    time.sleep(5)
            except Exception as e:
                print(f"⚠️ 验证出错: {e}")
                if i < max_retries - 1:
                    print(f"⏳ 等待5秒后重试...")
                    time.sleep(5)
        
        print(f"❌ 模型启动失败，已尝试 {max_retries} 次")
        return False
            
    except FileNotFoundError:
        print(f"❌ 错误: 找不到 ollama 命令")
        print(f"💡 请确保 Ollama 已正确安装并添加到系统 PATH")
        return False
    except Exception as e:
        print(f"❌ 启动模型时出错: {e}")
        return False

def verify_model_exists(model_name):
    """
    验证指定的模型是否存在，并检查健康度
    
    Args:
        model_name: 模型名称
    
    Returns:
        bool: 模型是否存在且健康
    """
    print(f"🔍 正在验证模型: {model_name}")
    models = check_ollama_models()
    
    if models is None:
        print(f"⚠️ 无法验证模型，将尝试直接使用")
        return True  # 无法验证时假设模型存在，让后续调用来处理错误
    
    if model_name in models:
        print(f"✅ 模型存在: {model_name}")
        # 进行健康度检查
        return check_model_health(model_name)
    else:
        print(f"❌ 错误: 模型 '{model_name}' 不存在！")
        print(f"📋 当前Ollama中可用的模型:")
        for i, model in enumerate(models, 1):
            print(f"   {i}. {model}")
        print(f"\n💡 解决方案:")
        print(f"   1. 修改脚本中的 MODEL_NAME 为上述模型之一")
        print(f"   2. 或者使用命令下载模型: ollama pull {model_name}")
        return False

def call_ollama(prompt):
    """
    调用本地 Ollama 接口
    
    Args:
        prompt: 提示词
    
    Returns:
        str: 模型响应文本，失败返回None
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1, # 低温度保证结果确定性
            "num_ctx": 8192,     # 上下文窗口（增大以支持更长的输入）
            "num_gpu": 99,    # 使用所有可用GPU
            "num_predict": 4096,  # 最大生成长度（从1024增加到4096，避免截断）
            "stop": ["\n\n\n", "【待检查数据】", "现在开始检查"] # 强制停止符
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(f"❌ Ollama API错误 (HTTP {response.status_code}): {response.text}")
            if response.status_code == 404:
                print(f"💡 提示: 模型 '{MODEL_NAME}' 可能不存在，请检查模型名称")
            return None
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时: 模型响应时间过长（>300秒）")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def parse_llm_response(response_text, batch_info=""):
    """
    尝试解析 LLM 返回的 JSON，支持多种格式和容错处理
    
    Args:
        response_text: LLM返回的原始文本
        batch_info: 批次信息（用于调试）
    
    Returns:
        list: 解析后的问题列表，解析失败返回空列表
    """
    if not response_text or not response_text.strip():
        print(f"⚠️ LLM返回了空响应 {batch_info}")
        return []
    
    try:
        # 步骤1: 清理Markdown标记和中文引号
        clean_text = response_text.strip()
        clean_text = clean_text.replace("```json", "").replace("```", "").strip()
        
        # 替换中文引号为英文引号（避免JSON解析错误）
        clean_text = clean_text.replace(""", '"').replace(""", '"')
        clean_text = clean_text.replace("'", "'").replace("'", "'")
        
        # 步骤2: 尝试找到JSON数组的边界
        start = clean_text.find("[")
        end = clean_text.rfind("]")
        
        if start == -1:
            print(f"❌ 未找到JSON数组开始符号 [ {batch_info}")
            print(f"📄 响应内容前200字符: {response_text[:200]}")
            return []
        
        if end == -1 or start >= end:
            # 可能是截断的JSON，尝试查找不完整的数组
            print(f"⚠️ JSON数组未正确闭合，尝试修复... {batch_info}")
            json_str = clean_text[start:]
            fixed_json = try_fix_truncated_json(json_str)
            if fixed_json:
                clean_text = fixed_json
                end = clean_text.rfind("]")
                if end == -1:
                    print(f"❌ 修复失败：仍然没有找到闭合符号 {batch_info}")
                    return []
            else:
                print(f"❌ 未找到任何完整的对象 {batch_info}")
                print(f"📄 响应内容前200字符: {response_text[:200]}")
                return []
        
        # 提取JSON字符串（包含完整的 [ ... ]）
        json_str = clean_text[start:end + 1]
        
        # 步骤3: 尝试直接解析
        try:
            result = json.loads(json_str)
            if isinstance(result, list):
                print(f"✅ 成功解析JSON，发现 {len(result)} 个问题 {batch_info}")
                return result
            else:
                print(f"⚠️ JSON格式错误：期望列表，实际为 {type(result)} {batch_info}")
                return []
        except json.JSONDecodeError as e:
            # 步骤4: 如果直接解析失败，尝试修复常见问题
            print(f"⚠️ JSON解析失败: {str(e)} {batch_info}")
            print(f"📍 错误位置: 第{e.lineno}行, 第{e.colno}列 (char {e.pos})")
            
            # 【新增】尝试更激进的清理策略（处理控制字符）
            print(f"🔧 尝试清理控制字符和特殊字符... {batch_info}")
            json_str_cleaned = clean_json_string(json_str)
            if json_str_cleaned != json_str:
                try:
                    result = json.loads(json_str_cleaned)
                    if isinstance(result, list):
                        print(f"✅ 清理后成功解析JSON，发现 {len(result)} 个问题 {batch_info}")
                        return result
                except json.JSONDecodeError as e2:
                    print(f"⚠️ 清理后仍然失败: {str(e2)} {batch_info}")
            
            # 尝试修复：处理截断的JSON
            print(f"🔧 尝试修复截断的JSON... {batch_info}")
            fixed_json = try_fix_truncated_json(json_str_cleaned if json_str_cleaned != json_str else json_str)
            if fixed_json:
                try:
                    result = json.loads(fixed_json)
                    if isinstance(result, list):
                        print(f"✅ 修复后成功解析JSON，发现 {len(result)} 个问题 {batch_info}")
                        return result
                except Exception as e3:
                    print(f"⚠️ 修复后解析失败: {str(e3)} {batch_info}")
            
            # 如果修复失败，保存原始响应用于调试
            import re
            # 清理batch_info，只保留数字和下划线
            safe_batch_info = re.sub(r'[^0-9_]', '', batch_info.replace(' ', '_').replace('批次', 'batch').replace('/', '_'))
            debug_file = f"llm_debug_{safe_batch_info}.txt"
            try:
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(f"=== 批次信息 ===\n")
                    f.write(f"{batch_info}\n\n")
                    f.write("=== 原始响应 ===\n")
                    f.write(response_text)
                    f.write("\n\n=== 清理后的JSON ===\n")
                    f.write(json_str)
                    f.write("\n\n=== 错误信息 ===\n")
                    f.write(f"错误: {str(e)}\n")
                    f.write(f"位置: 第{e.lineno}行, 第{e.colno}列\n")
                    if fixed_json:
                        f.write("\n\n=== 修复后的JSON ===\n")
                        f.write(fixed_json)
                print(f"💾 调试信息已保存: {debug_file}")
            except Exception as save_err:
                print(f"⚠️ 无法保存调试文件: {save_err}")
            
            print(f"❌ JSON解析失败 {batch_info}")
            print(f"📄 JSON前200字符: {json_str[:200]}")
            if len(json_str) > 500:
                print(f"📄 JSON后200字符: {json_str[-200:]}")
            
            return []
    
    except Exception as e:
        print(f"❌ 解析过程发生异常: {e}")
        return []

def clean_json_string(json_str):
    """
    清理JSON字符串中的问题字符（增强版）
    """
    import re
    
    # 1. 移除ASCII控制字符（0x00-0x1F）
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', json_str)
    
    # 2. 替换中文符号为英文符号
    cleaned = cleaned.replace('，', ',').replace('：', ':')
    cleaned = cleaned.replace('"', '"').replace('"', '"')
    cleaned = cleaned.replace(''', "'").replace(''', "'")
    
    # 3. 处理字符串值内的特殊字符
    def escape_special_chars(match):
        content = match.group(1)
        content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        return f'"{content}"'
    
    try:
        cleaned = re.sub(r'"([^"]*)"', escape_special_chars, cleaned)
    except Exception as e:
        print(f"⚠️ 字符转义失败: {e}")
    
    return cleaned

def try_fix_truncated_json(json_str):
    """
    尝试修复截断的JSON字符串（优化版）
    """
    try:
        # 先清理
        json_str = clean_json_string(json_str)
        
        # 空数组直接返回
        if json_str.strip() == "[]":
            return json_str
        
        # 查找数组边界
        start = json_str.find("[")
        end = json_str.rfind("]")
        
        if start == -1:
            return None
        
        # 未闭合的数组
        if end == -1 or start >= end:
            print(f"🔧 修复未闭合的数组...")
            
            # 找到最后一个完整对象
            last_brace = json_str.rfind("}")
            if last_brace == -1:
                print(f"⚠️ 未找到完整对象")
                return None
            
            # 从后往前查找括号匹配的位置
            positions = [i for i, c in enumerate(json_str) if c == '}']
            
            for pos in reversed(positions):
                before = json_str[:pos + 1]
                if before.count("{") == before.count("}"):
                    fixed = before + "]"  # 直接闭合，不加换行
                    print(f"✅ 保留 {before.count('}')} 个完整对象")
                    return fixed
            
            print(f"⚠️ 括号不匹配: {{ {json_str.count('{')} 个, }} {json_str.count('}')} 个")
            return None
        
        # 已闭合但可能有问题
        last_brace = json_str.rfind("}")
        if last_brace > -1:
            after = json_str[last_brace + 1:end].strip()
            if after in ["", ","]:
                return json_str
            # 移除多余内容
            return json_str[:last_brace + 1] + "]"
        
        return json_str
    
    except Exception as e:
        print(f"⚠️ 修复失败: {e}")
        return None

def load_excel_with_multirow_header(file_path, sheet_name, header_rows=None):
    """
    加载Excel文件，支持多行表头
    
    Args:
        file_path: Excel文件路径
        sheet_name: Sheet名称
        header_rows: 表头行配置
            - None: 自动检测（默认第一行）
            - int: 单行表头的行号（0-based）
            - list: 多行表头的行号列表，如 [0, 1, 2]
    
    Returns:
        df: DataFrame
        actual_header_rows: 实际使用的表头行数（用于计算Excel行号）
    """
    try:
        if header_rows is None:
            # 默认单行表头
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
            actual_header_rows = 1
            print(f"✅ 使用默认单行表头（第1行）")
        elif isinstance(header_rows, int):
            # 单行表头，指定行号
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_rows)
            actual_header_rows = header_rows + 1
            print(f"✅ 使用单行表头（第{header_rows + 1}行）")
        elif isinstance(header_rows, list):
            # 多行表头
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_rows)
            actual_header_rows = max(header_rows) + 1
            
            # 合并多行表头为单一列名
            # pandas会自动创建MultiIndex，我们需要将其展平
            if isinstance(df.columns, pd.MultiIndex):
                # 合并多层列名，用下划线连接，去除空值
                df.columns = [
                    '_'.join([str(c) for c in col if str(c) != 'nan' and str(c).strip() != ''])
                    for col in df.columns.values
                ]
                print(f"✅ 使用多行表头（第{min(header_rows)+1}-{max(header_rows)+1}行），已合并列名")
            else:
                print(f"✅ 使用多行表头（第{min(header_rows)+1}-{max(header_rows)+1}行）")
        else:
            raise ValueError(f"header_rows 参数格式错误: {header_rows}")
        
        return df, actual_header_rows
    
    except Exception as e:
        print(f"❌ 读取文件失败: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise

def find_target_column(df, target_column_name, column_index=None):
    """
    查找目标列，支持模糊匹配和多列选择
    
    Args:
        df: DataFrame
        target_column_name: 目标列名
        column_index: 可选，当存在多个匹配列时，指定使用第几个（从0开始）
    
    Returns:
        actual_column_name: 实际找到的列名，如果未找到返回None
    """
    matched_columns = []
    
    # 1. 精确匹配
    exact_matches = [col for col in df.columns if col == target_column_name]
    if exact_matches:
        matched_columns.extend(exact_matches)
    
    # 2. 模糊匹配（忽略大小写和空格）
    if not matched_columns:
        target_lower = target_column_name.lower().replace(' ', '')
        for col in df.columns:
            col_lower = str(col).lower().replace(' ', '')
            if target_lower in col_lower or col_lower in target_lower:
                matched_columns.append(col)
    
    # 3. 处理匹配结果
    if not matched_columns:
        # 未找到，列出所有列名供参考
        print(f"❌ 错误: 没找到列名 '{target_column_name}'")
        print(f"📋 当前表格的所有列名:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        print(f"\n💡 提示: 请修改脚本中的 TARGET_COLUMN 配置为上述列名之一")
        return None
    
    # 4. 如果找到多个匹配列
    if len(matched_columns) > 1:
        print(f"⚠️ 找到 {len(matched_columns)} 个匹配的列:")
        for i, col in enumerate(matched_columns):
            print(f"   [{i}] {col}")
        
        # 根据column_index选择
        if column_index is not None:
            if 0 <= column_index < len(matched_columns):
                selected_col = matched_columns[column_index]
                print(f"✅ 使用第 {column_index} 个匹配列: '{selected_col}'")
                return selected_col
            else:
                print(f"❌ 错误: TARGET_COLUMN_INDEX={column_index} 超出范围 (0-{len(matched_columns)-1})")
                return None
        else:
            # 默认使用第一个
            selected_col = matched_columns[0]
            print(f"✅ 默认使用第一个匹配列: '{selected_col}'")
            print(f"💡 提示: 如需使用其他列，请设置 TARGET_COLUMN_INDEX (0-{len(matched_columns)-1})")
            return selected_col
    
    # 5. 只找到一个匹配列
    selected_col = matched_columns[0]
    if selected_col == target_column_name:
        print(f"✅ 找到目标列（精确匹配）: '{selected_col}'")
    else:
        print(f"✅ 找到目标列（模糊匹配）: '{selected_col}' (配置中为: '{target_column_name}')")
    return selected_col

def main():
    # 解析命令行参数
    if len(sys.argv) >= 4:
        input_file = sys.argv[1]
        sheet_name = sys.argv[2]
        target_column = sys.argv[3]
    else:
        # 使用默认配置
        input_file = INPUT_FILE
        sheet_name = SHEET_NAME
        target_column = TARGET_COLUMN
    
    # 动态生成输出文件名
    output_file = f"{sheet_name}_{target_column}_Check_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    print("=" * 60, flush=True)
    print("🚀 配置文本检查工具 v2.3 (GPU加速版)", flush=True)
    print("=" * 60, flush=True)
    
    # 显示当前配置
    print(f"📋 当前配置:")
    print(f"   - 模型名称: {MODEL_NAME}")
    print(f"   - Ollama地址: {OLLAMA_URL}")
    print(f"   - 输入文件: {input_file}")
    print(f"   - Sheet名称: {sheet_name}")
    print(f"   - 目标列: {target_column}")
    print(f"   - 批次大小: {BATCH_SIZE} 行/批")
    print("-" * 60)
    
    # 验证模型是否存在
    if not verify_model_exists(MODEL_NAME):
        print("\n❌ 模型验证失败，程序终止")
        print("💡 请修改脚本中的 MODEL_NAME 配置或下载对应模型")
        return
    
    print("-" * 60)
    
    # 加载Excel文件（支持多行表头）
    try:
        df, header_row_count = load_excel_with_multirow_header(
            input_file, 
            sheet_name, 
            HEADER_ROWS
        )
    except Exception as e:
        return
    
    print(f"📊 数据行数: {len(df)} 行")
    print(f"📊 列数: {len(df.columns)} 列")
    print("-" * 60)
    
    # 查找目标列
    actual_column = find_target_column(df, target_column, TARGET_COLUMN_INDEX)
    if actual_column is None:
        return
    
    # 预处理：筛选出非空且包含中文的行（减少无效请求）
    # 这里假设我们只检查字符串类型的单元格
    df_to_check = df[df[actual_column].apply(lambda x: isinstance(x, str) and len(x) > 1)].copy()
    
    # 记录原始行号（Excel行号 = DataFrame的index + 表头行数 + 1）
    # 例如：3行表头，DataFrame第0行 = Excel第4行
    df_to_check['excel_row'] = df_to_check.index + header_row_count + 1
    
    total_rows = len(df_to_check)
    print(f"✅ 共发现 {total_rows} 行有效文本，开始分批检查...")
    print(f"📦 批次大小: {BATCH_SIZE} 行/批")
    print("-" * 60)

    all_issues = []

    # 分批处理
    batches = math.ceil(total_rows / BATCH_SIZE)
    failed_batches = []  # 记录失败的批次
    interrupted = False  # 标记是否被中断
    completed_batches = 0  # 已完成的批次数
    
    try:
        for i in tqdm(range(batches), desc="AI 检查进度"):
            start_idx = i * BATCH_SIZE
            end_idx = min((i + 1) * BATCH_SIZE, total_rows)
            batch_num = i + 1
            
            # 提取当前批次数据
            current_batch = df_to_check.iloc[start_idx:end_idx]
            
            # 构造发送给 LLM 的简化数据结构：{行号: 文本}
            batch_payload = {
                row['excel_row']: row[actual_column] 
                for _, row in current_batch.iterrows()
            }
            
            # 发送给 LLM
            prompt = get_check_prompt(batch_payload)
            response = call_ollama(prompt)
            
            if response:
                # 记录响应长度（用于调试）
                response_len = len(response)
                
                # 解析响应
                batch_info = f"(批次 {batch_num}/{batches})"
                issues = parse_llm_response(response, batch_info)
                
                if issues:
                    all_issues.extend(issues)
                    # 不在进度条中打印，避免干扰
                elif response_len > 10:
                    # 如果响应不为空但解析失败，记录失败的批次
                    failed_batches.append({
                        'batch': batch_num,
                        'rows': f"{list(batch_payload.keys())[0]}-{list(batch_payload.keys())[-1]}",
                        'response_len': response_len
                    })
            else:
                # API调用失败
                failed_batches.append({
                    'batch': batch_num,
                    'rows': f"{list(batch_payload.keys())[0]}-{list(batch_payload.keys())[-1]}",
                    'response_len': 0,
                    'error': 'API调用失败'
                })
            
            # 稍微休眠一下防止 GPU 过热或 Ollama 堵塞（可选）
            # time.sleep(0.1)
            completed_batches = i + 1
    except KeyboardInterrupt:
        interrupted = True
        print(f"\n\n⚠️ 用户中断！已完成 {completed_batches}/{batches} 批次", flush=True)
        print(f"💾 正在保存已检查的结果...", flush=True)
    
    # 处理完成后，显示失败的批次信息
    if failed_batches:
        print(f"\n⚠️ 有 {len(failed_batches)} 个批次处理失败或解析失败:")
        for fb in failed_batches:
            error_msg = fb.get('error', 'JSON解析失败')
            print(f"   - 批次 {fb['batch']} (行号 {fb['rows']}): {error_msg}, 响应长度: {fb['response_len']} 字符")
        print(f"💡 提示: 检查 llm_response_debug.txt 文件查看详细的响应内容")

    # 结果输出
    if all_issues:
        result_df = pd.DataFrame(all_issues)
        # 调整列顺序
        cols = ["line_no", "issue", "suggestion"]
        # 确保列存在（防止 LLM 返回的 key 不对）
        for c in cols:
            if c not in result_df.columns:
                result_df[c] = ""
        
        result_df = result_df[cols]
        result_df.columns = ["行号", "问题说明", "修改建议"]
        
        # 使用安全保存函数
        final_output_file = safe_save_excel(result_df, output_file)
        print(f"\n检查完成！共发现 {len(all_issues)} 处潜在问题。")
        print(f"结果已保存至: {final_output_file}")
        
        # 追加功能：插入原文内容
        print("-" * 60)
        print("📝 正在添加配置原文...")
        add_original_text_to_report(final_output_file, input_file, sheet_name, actual_column, header_row_count)
    else:
        print("\n检查完成！未发现明显问题（或者模型未能正确输出）。")

def safe_save_excel(df, file_path, max_retries=3):
    """
    安全保存Excel文件，处理文件被占用的情况
    
    Args:
        df: 要保存的DataFrame
        file_path: 目标文件路径
        max_retries: 最大重试次数
    
    Returns:
        str: 实际保存的文件路径
    """
    for attempt in range(max_retries):
        try:
            # 尝试保存文件
            df.to_excel(file_path, index=False)
            return file_path
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ 文件被占用，{2}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                # 最后一次尝试失败，生成新文件名
                print(f"❌ 文件 '{file_path}' 被占用（可能在Excel中打开）")
                
                # 生成带时间戳的新文件名
                base_name = os.path.splitext(file_path)[0]
                ext = os.path.splitext(file_path)[1]
                timestamp = datetime.now().strftime('%H%M%S')
                new_file_path = f"{base_name}_{timestamp}{ext}"
                
                try:
                    df.to_excel(new_file_path, index=False)
                    print(f"✅ 已保存为新文件: {new_file_path}")
                    print(f"💡 提示: 请关闭Excel中的文件后再运行脚本")
                    return new_file_path
                except Exception as e2:
                    print(f"❌ 保存失败: {e2}")
                    raise
        except Exception as e:
            print(f"❌ 保存文件时发生错误: {e}")
            raise
    
    return file_path

def add_original_text_to_report(output_file, input_file, sheet_name, target_column, header_row_count):
    """
    从输出报告中读取行号，从原始Excel文件中获取对应行的原文，
    并插入到报告的第一列之后
    
    Args:
        output_file: 输出报告文件路径
        input_file: 原始Excel文件路径
        sheet_name: Sheet名称
        target_column: 目标列名
        header_row_count: 表头行数
    """
    try:
        # 1. 读取输出报告
        report_df = pd.read_excel(output_file)
        print(f"✅ 读取报告文件: {len(report_df)} 行")
        
        # 2. 读取原始Excel文件
        original_df, _ = load_excel_with_multirow_header(input_file, sheet_name, HEADER_ROWS)
        print(f"✅ 读取原始文件: {len(original_df)} 行")
        
        # 3. 为每一行获取原文和第一列的id
        original_texts = []
        first_column_ids = []
        
        # 获取原始Excel的第一列列名
        first_column_name = original_df.columns[0]
        print(f"📋 第一列列名: {first_column_name}")
        
        for idx, row in report_df.iterrows():
            line_no = row['行号']
            try:
                # Excel行号转换为DataFrame索引
                # Excel行号 = DataFrame索引 + 表头行数 + 1
                # 所以 DataFrame索引 = Excel行号 - 表头行数 - 1
                df_index = int(line_no) - header_row_count - 1
                
                if 0 <= df_index < len(original_df):
                    # 获取原文
                    original_text = original_df.iloc[df_index][target_column]
                    # 处理NaN值
                    if pd.isna(original_text):
                        original_text = ""
                    original_texts.append(str(original_text))
                    
                    # 获取第一列的id
                    first_column_value = original_df.iloc[df_index][first_column_name]
                    if pd.isna(first_column_value):
                        first_column_value = ""
                    first_column_ids.append(str(first_column_value))
                else:
                    print(f"⚠️ 警告: 行号 {line_no} 超出范围")
                    original_texts.append("")
                    first_column_ids.append("")
            except Exception as e:
                print(f"⚠️ 警告: 无法获取行号 {line_no} 的数据: {e}")
                original_texts.append("")
                first_column_ids.append("")
        
        # 4. 在第一列之后插入"配置原文"列，在第二列位置插入"id"列
        report_df.insert(1, '配置原文', original_texts)
        report_df.insert(2, '对白id', first_column_ids)
        
        # 5. 保存更新后的报告（使用安全保存）
        final_file = safe_save_excel(report_df, output_file)
        print(f"✅ 已添加配置原文和id到报告文件")
        print(f"📊 最终报告: {len(report_df)} 行 × {len(report_df.columns)} 列")
        print(f"📋 列名: {', '.join(report_df.columns.tolist())}")
        if final_file != output_file:
            print(f"💡 注意: 原文件被占用，已保存为: {final_file}")
        
    except Exception as e:
        print(f"❌ 添加原文失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='游戏配置文本检查工具')
    parser.add_argument('input_file', nargs='?', default=INPUT_FILE, help='Excel配置文件路径')
    parser.add_argument('sheet_name', nargs='?', default=SHEET_NAME, help='Sheet名称')
    parser.add_argument('target_column', nargs='?', default=TARGET_COLUMN, help='目标列名')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE, help='批次大小')
    parser.add_argument('--model', default=MODEL_NAME, help='模型名称')
    parser.add_argument('--column-index', type=int, default=TARGET_COLUMN_INDEX, help='列索引')
    
    args = parser.parse_args()
    
    # 更新全局配置
    INPUT_FILE = args.input_file
    SHEET_NAME = args.sheet_name
    TARGET_COLUMN = args.target_column
    BATCH_SIZE = args.batch_size
    MODEL_NAME = args.model
    TARGET_COLUMN_INDEX = args.column_index
    OUTPUT_FILE = f"{SHEET_NAME}_{TARGET_COLUMN}_Check_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    main()