#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试三维度数据收集功能
"""

import requests
import json

def test_simple_data_collection():
    """简单测试三维度数据收集功能"""
    print("=== 简单测试三维度数据收集功能 ===")
    
    # 直接测试API路径
    api_url = "http://localhost:5001/api/user"
    
    try:
        # 测试API是否能正常响应
        response = requests.get(api_url)
        print(f"1. API响应状态码: {response.status_code}")
        print(f"2. API响应内容: {response.text}")
        
        # 解析JSON响应
        try:
            result = response.json()
            print("3. 响应内容是有效的JSON格式")
        except json.JSONDecodeError:
            print("3. 响应内容不是有效的JSON格式")
            return False
        
        # 测试评估接口
        assess_url = "http://localhost:5001/api/assess"
        test_data = {
            "task_aversion": 70,
            "result_value": 50,
            "self_control": 65
        }
        
        print(f"\n4. 测试评估数据: {test_data}")
        assess_response = requests.post(assess_url, json=test_data)
        print(f"5. 评估API响应状态码: {assess_response.status_code}")
        print(f"6. 评估API响应内容: {assess_response.text}")
        
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    test_simple_data_collection()
