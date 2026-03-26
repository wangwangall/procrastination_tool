#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试/api/assess接口
模拟发送POST请求并验证返回结果
"""

import requests
import json

# 测试数据
test_data = {
    "task_aversion": 80,
    "result_value": 40,
    "self_control": 50
}

# API端点 - 当前正确的评估接口
url = "http://127.0.0.1:5001/api/assess"

# 发送请求
try:
    print("发送测试请求到/api/assess...")
    response = requests.post(url, json=test_data, cookies={})
    
    # 检查响应状态码
    if response.status_code == 200:
        # 解析响应
        result = response.json()
        print("响应结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证返回字段
        required_fields = ["risk_level", "score", "weights", "anonymous_id"]
        if all(field in result for field in required_fields):
            print("\n测试通过！返回结果包含所有必要字段")
        else:
            print("\n测试失败！返回结果缺少必要字段")
            print(f"缺少的字段: {set(required_fields) - set(result.keys())}")
    else:
        print(f"测试失败！HTTP状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        
except Exception as e:
    print(f"测试失败！发生错误: {e}")
