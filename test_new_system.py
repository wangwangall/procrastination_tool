#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
拖延探索笔记本 - 功能测试脚本
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5001/api'

def test_register():
    """测试用户注册"""
    print("\n=== 测试用户注册 ===")
    
    timestamp = int(time.time())
    user_data = {
        'phone': f'1380013{timestamp % 10000}',
        'email': f'test{timestamp}@example.com',
        'username': f'测试用户{timestamp}',
        'password': 'test123456'
    }
    
    response = requests.post(f'{BASE_URL}/register', json=user_data)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print("✅ 注册成功")
            return user_data
        else:
            print(f"❌ 注册失败: {data['message']}")
            return None
    else:
        print("❌ 注册失败")
        return None

def test_login(user_data):
    """测试用户登录"""
    print("\n=== 测试用户登录 ===")
    
    login_data = {
        'identifier': user_data['phone'],
        'password': user_data['password']
    }
    
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print("✅ 登录成功")
            return response.cookies
        else:
            print(f"❌ 登录失败: {data['message']}")
            return None
    else:
        print("❌ 登录失败")
        return None

def test_get_user_info(cookies):
    """测试获取用户信息"""
    print("\n=== 测试获取用户信息 ===")
    
    response = requests.get(f'{BASE_URL}/user', cookies=cookies)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print("✅ 获取用户信息成功")
            print(f"用户名: {data['user']['username']}")
            print(f"权重: w1={data['user']['w1']}, w2={data['user']['w2']}, w3={data['user']['w3']}")
            return True
        else:
            print(f"❌ 获取用户信息失败: {data['message']}")
            return False
    else:
        print("❌ 获取用户信息失败")
        return False

def test_assess(cookies):
    """测试拖延评估"""
    print("\n=== 测试拖延评估 ===")
    
    assess_data = {
        'task_aversion': 70,
        'result_value': 50,
        'self_control': 30,
        'user_notes': '这是一个测试评估'
    }
    
    response = requests.post(f'{BASE_URL}/assess', json=assess_data, cookies=cookies)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print("✅ 评估成功")
            result = data['result']
            print(f"核心函数结果: {result['core_function']['risk_level']}风险, 分数{result['core_function']['score']}")
            print(f"模型预测结果: {result['model_prediction']['risk_level']}风险")
            print(f"是否匹配: {result['model_prediction']['match']}")
            print(f"建议: {result['suggestion']}")
            print(f"报告路径: {result['report_path']}")
            return True
        else:
            print(f"❌ 评估失败: {data['message']}")
            return False
    else:
        print(f"❌ 评估失败: {response.text}")
        return False

def test_get_history(cookies):
    """测试获取历史记录"""
    print("\n=== 测试获取历史记录 ===")
    
    response = requests.get(f'{BASE_URL}/history', cookies=cookies)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print("✅ 获取历史记录成功")
            print(f"历史记录数量: {len(data['history'])}")
            if len(data['history']) > 0:
                latest = data['history'][0]
                print(f"最新记录: {latest['risk_level']}风险, 分数{latest['score']}")
            return True
        else:
            print(f"❌ 获取历史记录失败: {data['message']}")
            return False
    else:
        print("❌ 获取历史记录失败")
        return False

def test_get_analytics(cookies):
    """测试获取数据分析"""
    print("\n=== 测试获取数据分析 ===")
    
    response = requests.get(f'{BASE_URL}/analytics', cookies=cookies)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print("✅ 获取数据分析成功")
            analytics = data['analytics']
            print(f"总评估次数: {analytics['total_count']}")
            print(f"高风险占比: {analytics['high_risk_ratio']}%")
            print(f"模型准确率: {analytics['model_accuracy']}%")
            print(f"平均分数: {analytics['avg_score']}")
            return True
        else:
            print(f"❌ 获取数据分析失败: {data['message']}")
            return False
    else:
        print("❌ 获取数据分析失败")
        return False

def test_update_weights(cookies):
    """测试更新权重"""
    print("\n=== 测试更新权重 ===")
    
    # 先获取当前权重
    response = requests.get(f'{BASE_URL}/weights', cookies=cookies)
    if response.status_code == 200:
        current_weights = response.json()['weights']
        print(f"当前权重: w1={current_weights['w1']}, w2={current_weights['w2']}, w3={current_weights['w3']}")
    
    # 更新权重
    new_weights = {
        'w1': 0.5,
        'w2': 0.3,
        'w3': 0.2
    }
    
    response = requests.post(f'{BASE_URL}/weights', json=new_weights, cookies=cookies)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print("✅ 更新权重成功")
            print(f"新权重: w1={new_weights['w1']}, w2={new_weights['w2']}, w3={new_weights['w3']}")
            return True
        else:
            print(f"❌ 更新权重失败: {data['message']}")
            return False
    else:
        print("❌ 更新权重失败")
        return False

def test_logout(cookies):
    """测试用户登出"""
    print("\n=== 测试用户登出 ===")
    
    response = requests.post(f'{BASE_URL}/logout', cookies=cookies)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print("✅ 登出成功")
            return True
        else:
            print(f"❌ 登出失败: {data['message']}")
            return False
    else:
        print("❌ 登出失败")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("拖延探索笔记本 - 功能测试")
    print("=" * 50)
    
    # 测试注册
    user_data = test_register()
    if not user_data:
        print("\n❌ 测试终止：注册失败")
        exit(1)
    
    # 测试登录
    cookies = test_login(user_data)
    if not cookies:
        print("\n❌ 测试终止：登录失败")
        exit(1)
    
    # 测试获取用户信息
    if not test_get_user_info(cookies):
        print("\n❌ 测试终止：获取用户信息失败")
        exit(1)
    
    # 测试评估（进行3次评估）
    for i in range(3):
        print(f"\n--- 第{i+1}次评估 ---")
        if not test_assess(cookies):
            print(f"\n❌ 第{i+1}次评估失败")
    
    # 测试获取历史记录
    if not test_get_history(cookies):
        print("\n❌ 获取历史记录失败")
    
    # 测试获取数据分析
    if not test_get_analytics(cookies):
        print("\n❌ 获取数据分析失败")
    
    # 测试更新权重
    if not test_update_weights(cookies):
        print("\n❌ 更新权重失败")
    
    # 再次评估（使用新权重）
    print("\n--- 使用新权重评估 ---")
    if not test_assess(cookies):
        print("\n❌ 新权重评估失败")
    
    # 测试登出
    if not test_logout(cookies):
        print("\n❌ 登出失败")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)
