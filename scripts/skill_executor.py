# -*- coding: utf-8 -*-
"""
SKILL执行器 - 游戏配置文本检查
用于解析自然语言指令并调用核心检查脚本
"""
import sys
import os
import re
import subprocess
from pathlib import Path

def parse_skill_command(command):
    """
    解析SKILL命令
    
    支持的格式：
    1. "使用SKILL检查 <文件路径> 的 <Sheet名> sheet，检查 <列名> 列"
    2. "检查配置文件：<文件路径>，Sheet：<Sheet名>，列：<列名>"
    
    Args:
        command: 自然语言命令
    
    Returns:
        dict: 解析后的参数 {"file": "", "sheet": "", "column": ""}
    """
    # 模式1: 使用SKILL检查 ... 的 ... sheet，检查 ... 列
    pattern1 = r'使用SKILL检查\s+(.+?)\s+的\s+(.+?)\s+sheet[,，]\s*检查\s+(.+?)\s+列'
    match = re.search(pattern1, command, re.IGNORECASE)
    if match:
        return {
            "file": match.group(1).strip(),
            "sheet": match.group(2).strip(),
            "column": match.group(3).strip()
        }
    
    # 模式2: 检查配置文件：...，Sheet：...，列：...
    pattern2 = r'检查配置文件[：:]\s*(.+?)[,，]\s*Sheet[：:]\s*(.+?)[,，]\s*列[：:]\s*(.+?)(?:\s|$)'
    match = re.search(pattern2, command, re.IGNORECASE)
    if match:
        return {
            "file": match.group(1).strip(),
            "sheet": match.group(2).strip(),
            "column": match.group(3).strip()
        }
    
    # 模式3: 简化格式 <文件> <Sheet> <列>
    parts = command.split()
    if len(parts) >= 3:
        return {
            "file": parts[0],
            "sheet": parts[1],
            "column": parts[2]
        }
    
    return None

def validate_params(params):
    """
    验证参数
    
    Args:
        params: 参数字典
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not params:
        return False, "❌ 无法解析命令，请使用正确的格式"
    
    # 验证文件路径
    file_path = params["file"]
    if not os.path.exists(file_path):
        return False, f"❌ 文件不存在: {file_path}"
    
    if not file_path.endswith(('.xlsx', '.xls')):
        return False, f"❌ 不支持的文件格式: {file_path}（仅支持.xlsx和.xls）"
    
    # 验证Sheet名和列名
    if not params["sheet"]:
        return False, "❌ Sheet名称不能为空"
    
    if not params["column"]:
        return False, "❌ 列名不能为空"
    
    return True, ""

def execute_check(params):
    """
    执行检查任务（实时显示输出）
    
    Args:
        params: 参数字典
    
    Returns:
        int: 返回码（0表示成功）
    """
    # 获取脚本目录
    script_dir = Path(__file__).parent
    check_script = script_dir / "conf_check.py"
    
    if not check_script.exists():
        print(f"❌ 检查脚本不存在: {check_script}")
        return 1
    
    # 构造命令
    cmd = [
        sys.executable,
        str(check_script),
        params["file"],
        params["sheet"],
        params["column"]
    ]
    
    print("=" * 60)
    print("🚀 SKILL执行器 - 游戏配置文本检查")
    print("=" * 60)
    print(f"📋 执行参数:")
    print(f"   - 文件: {params['file']}")
    print(f"   - Sheet: {params['sheet']}")
    print(f"   - 列名: {params['column']}")
    print("-" * 60)
    print(f"🔧 调用命令: {' '.join(cmd)}")
    print("=" * 60)
    print()
    
    # 执行命令并实时显示输出
    try:
        # 使用Popen实现实时输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1,  # 行缓冲
            universal_newlines=True
        )
        
        # 实时读取并打印输出
        for line in process.stdout:
            print(line, end='', flush=True)
        
        # 等待进程结束
        process.wait()
        return process.returncode
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return 1

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("🚀 SKILL执行器 - 游戏配置文本检查")
        print("=" * 60)
        print()
        print("📖 使用方法:")
        print()
        print("方式1: 自然语言命令")
        print('  python skill_executor.py "使用SKILL检查 <文件路径> 的 <Sheet名> sheet，检查 <列名> 列"')
        print()
        print("方式2: 简化命令")
        print('  python skill_executor.py "检查配置文件：<文件路径>，Sheet：<Sheet名>，列：<列名>"')
        print()
        print("方式3: 直接参数")
        print('  python skill_executor.py <文件路径> <Sheet名> <列名>')
        print()
        print("=" * 60)
        print()
        print("📝 示例:")
        print('  python skill_executor.py "使用SKILL检查 F:\\task.xlsx 的 TASK_CONF sheet，检查 text 列"')
        print()
        return 1
    
    # 解析命令
    command = " ".join(sys.argv[1:])
    params = parse_skill_command(command)
    
    # 验证参数
    is_valid, error_msg = validate_params(params)
    if not is_valid:
        print(error_msg)
        print()
        print("💡 提示: 请检查命令格式和文件路径")
        return 1
    
    # 执行检查
    return execute_check(params)

if __name__ == "__main__":
    sys.exit(main())
