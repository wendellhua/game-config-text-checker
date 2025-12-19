#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Excel to Alpaca Format Converter
将Excel文件转换为Alpaca格式的训练数据

Author: AI Assistant
Date: 2025-11-29
"""

import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import pandas as pd
except ImportError:
    print("错误: 需要安装pandas库")
    print("请运行: pip install pandas openpyxl")
    sys.exit(1)


def read_excel_file(excel_path: str) -> pd.DataFrame:
    """
    Read Excel file and return DataFrame
    
    Args:
        excel_path: Path to Excel file
        
    Returns:
        DataFrame containing the Excel data
        
    Raises:
        FileNotFoundError: If Excel file doesn't exist
        ValueError: If required columns are missing
    """
    if not Path(excel_path).exists():
        raise FileNotFoundError(f"Excel文件不存在: {excel_path}")
    
    try:
        # Read Excel file, support both .xlsx and .xls
        df = pd.read_excel(excel_path, engine='openpyxl')
    except Exception as e:
        try:
            # Try with xlrd engine for older .xls files
            df = pd.read_excel(excel_path, engine='xlrd')
        except Exception:
            raise ValueError(f"无法读取Excel文件: {e}")
    
    # Check required columns
    required_columns = ['instruction', 'input', 'output']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(
            f"Excel文件缺少必需的列: {', '.join(missing_columns)}\n"
            f"当前列: {', '.join(df.columns)}\n"
            f"需要的列: {', '.join(required_columns)}"
        )
    
    return df


def convert_to_alpaca_format(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert DataFrame to Alpaca format
    
    Args:
        df: DataFrame with instruction, input, output columns
        
    Returns:
        List of dictionaries in Alpaca format
    """
    alpaca_data = []
    
    for idx, row in df.iterrows():
        # Handle NaN values and convert to string
        instruction = str(row['instruction']) if pd.notna(row['instruction']) else ""
        input_text = str(row['input']) if pd.notna(row['input']) else ""
        output_text = str(row['output']) if pd.notna(row['output']) else ""
        
        # Skip empty rows
        if not instruction and not input_text and not output_text:
            continue
        
        # Create Alpaca format entry
        entry = {
            "instruction": instruction.strip(),
            "input": input_text.strip(),
            "output": output_text.strip()
        }
        
        alpaca_data.append(entry)
    
    return alpaca_data


def save_to_json(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save data to JSON file with proper encoding
    
    Args:
        data: List of dictionaries to save
        output_path: Path to output JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,  # Keep Chinese characters
                indent=2,  # Pretty print with 2-space indentation
                sort_keys=False  # Keep original order
            )
        print(f"✓ 成功保存到: {output_path}")
        print(f"✓ 共转换 {len(data)} 条数据")
    except Exception as e:
        raise IOError(f"保存JSON文件失败: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='将Excel文件转换为Alpaca格式的训练数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python excel_to_alpaca.py input.xlsx
  python excel_to_alpaca.py input.xlsx -o output.json
  python excel_to_alpaca.py input.xlsx --output training_data.json

Excel文件要求:
  - 必须包含三列: instruction, input, output
  - 支持 .xlsx 和 .xls 格式
  - 支持中文和特殊字符
        """
    )
    
    parser.add_argument(
        'excel_file',
        type=str,
        help='输入的Excel文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='输出的JSON文件路径 (默认: 与输入文件同名的.json文件)'
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Use same name as input file but with .json extension
        input_path = Path(args.excel_file)
        output_path = input_path.with_suffix('.json')
    
    try:
        print(f"正在读取Excel文件: {args.excel_file}")
        df = read_excel_file(args.excel_file)
        print(f"✓ 成功读取 {len(df)} 行数据")
        
        print("正在转换为Alpaca格式...")
        alpaca_data = convert_to_alpaca_format(df)
        
        print(f"正在保存到: {output_path}")
        save_to_json(alpaca_data, str(output_path))
        
        # Show preview
        if alpaca_data:
            print("\n数据预览 (第一条):")
            print(json.dumps(alpaca_data[0], ensure_ascii=False, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
