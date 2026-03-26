#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试三维度数据收集功能
1. 测试用户登录
2. 测试评估数据收集
3. 验证数据是否被正确存储
"""

import requests
import json

# 基础URL - 本地测试使用localhost
BASE_URL = "http://localhost:5001/api"

def test_data_collection():
    """测试三维度数据收集功能"""
    print("=== 测试三维度数据收集功能 ===")
    
    # 1. 登录获取认证
    login_data = {
        "identifier": "test@example.com",
        "password": "test123",
        "agree_to_terms": True
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/login", json=login_data)
        if login_response.status_code != 200:
            print(f"登录失败！HTTP状态码: {login_response.status_code}")
            print(f"错误信息: {login_response.text}")
            return False
        
        login_result = login_response.json()
        print("1. 登录成功！")
        print(f"   用户ID: {login_result.get('user_id')}")
        
        # 获取认证Cookie
        cookies = login_response.cookies
        
        # 2. 测试三维度数据收集
        assess_data = {
            "task_aversion": 75,
            "result_value": 45,
            "self_control": 60
        }
        
        assess_response = requests.post(f"{BASE_URL}/assess", json=assess_data, cookies=cookies)
        if assess_response.status_code != 200:
            print(f"评估失败！HTTP状态码: {assess_response.status_code}")
            print(f"错误信息: {assess_response.text}")
            return False
        
        assess_result = assess_response.json()
        print("2. 评估数据提交成功！")
        print(f"   风险等级: {assess_result.get('risk_level')}")
        print(f"   分数: {assess_result.get('score')}")
        
        # 验证返回的数据包含三维度信息
        if all(key in assess_result for key in ['task_aversion', 'result_value', 'self_control']):
            print("3. 评估结果包含三维度数据！")
            print(f"   任务厌恶度: {assess_result['task_aversion']}")
            print(f"   结果价值感: {assess_result['result_value']}")
            print(f"   自我控制能力: {assess_result['self_control']}")
        else:
            print("3. 评估结果缺少三维度数据！")
            return False
        
        # 3. 获取历史记录，验证数据是否被存储
        history_response = requests.get(f"{BASE_URL}/history", cookies=cookies)
        if history_response.status_code != 200:
            print(f"获取历史记录失败！HTTP状态码: {history_response.status_code}")
            print(f"错误信息: {history_response.text}")
            return False
        
        history_result = history_response.json()
        history = history_result.get('history', [])
        
        if history:
            latest_record = history[0]
            print("4. 历史记录获取成功！")
            print(f"   历史记录数量: {len(history)}")
            
            # 验证历史记录中包含三维度数据
            if all(key in latest_record for key in ['task_aversion', 'result_value', 'self_control']):
                print("5. 历史记录包含三维度数据！")
                print(f"   最新记录 - 任务厌恶度: {latest_record['task_aversion']}")
                print(f"   最新记录 - 结果价值感: {latest_record['result_value']}")
                print(f"   最新记录 - 自我控制能力: {latest_record['self_control']}")
                return True
            else:
                print("5. 历史记录缺少三维度数据！")
                print(f"   最新记录字段: {list(latest_record.keys())}")
                return False
        else:
            print("4. 历史记录为空！")
            return False
            
    except Exception as e:
        print(f"测试失败！发生错误: {e}")
        return False

if __name__ == "__main__":
    success = test_data_collection()
    if success:
        print("\n=== 三维度数据收集功能测试通过！ ===")
    else:
        print("\n=== 三维度数据收集功能测试失败！ ===")
