# -*- coding: utf-8 -*-
"""
模型健康度检查测试脚本
用于验证模型健康度检查和自动启动功能
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conf_check import check_ollama_models, verify_model_exists, check_model_health

def test_model_health():
    """测试模型健康度检查功能"""
    print("=" * 60)
    print("🧪 模型健康度检查测试")
    print("=" * 60)
    print()
    
    # 测试1: 检查Ollama可用模型
    print("📋 测试1: 检查Ollama可用模型")
    print("-" * 60)
    models = check_ollama_models()
    if models:
        print(f"✅ 成功获取模型列表，共 {len(models)} 个模型:")
        for i, model in enumerate(models, 1):
            print(f"   {i}. {model}")
    else:
        print("❌ 无法获取模型列表")
    print()
    
    # 测试2: 验证指定模型
    print("📋 测试2: 验证模型存在性和健康度")
    print("-" * 60)
    model_name = "qwen3:14b-q4_K_M"
    result = verify_model_exists(model_name)
    if result:
        print(f"✅ 模型 {model_name} 验证通过且健康")
    else:
        print(f"❌ 模型 {model_name} 验证失败")
    print()
    
    print("=" * 60)
    print("🎉 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_model_health()
