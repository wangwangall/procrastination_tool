#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试登录和评估功能
1. 先测试登录
2. 获取认证信息后测试评估接口
"""

import requests
import json

# 基础URL
BASE_URL = "http://127.0.0.1:5001/api"

def test_login():
    """测试登录功能"""
    print("=== 测试登录功能 ===")
    
    # 使用测试账号登录
    login_data = {
        "username": "testuser",
        "password": "testpassword",
        "agreed_to_terms": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            print("登录成功！")
            print(f"返回结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 获取认证信息
            cookies = response.cookies
            print(f"获取到的Cookie: {dict(cookies)}")
            
            return cookies
        else:
            print(f"登录失败！HTTP状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"登录测试失败！发生错误: {e}")
        return None

def test_register():
    """测试注册功能"""
    print("=== 测试注册功能 ===")
    
    # 注册新用户
    register_data = {
        "username": "testuser",
        "password": "testpassword",
        "agreed_to_terms": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        
        if response.status_code == 200:
            result = response.json()
            print("注册成功！")
            print(f"返回结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"注册失败！HTTP状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"注册测试失败！发生错误: {e}")
        return False

def test_assess(cookies):
    """测试评估功能"""
    print("\n=== 测试评估功能 ===")
    
    # 测试数据
    assess_data = {
        "task_aversion": 80,
        "result_value": 40,
        "self_control": 50
    }
    
    try:
        response = requests.post(f"{BASE_URL}/assess", json=assess_data, cookies=cookies)
        
        if response.status_code == 200:
            result = response.json()
            print("评估成功！")
            print(f"返回结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 验证返回字段
            required_fields = ["risk_level", "score", "weights", "anonymous_id"]
            if all(field in result for field in required_fields):
                print("\n✅ 评估测试通过！返回结果包含所有必要字段")
                return True
            else:
                print("\n❌ 评估测试失败！返回结果缺少必要字段")
                print(f"缺少的字段: {set(required_fields) - set(result.keys())}")
                return False
        else:
            print(f"评估失败！HTTP状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"评估测试失败！发生错误: {e}")
        return False

def test_public_access():
    """测试不需要登录的公共接口"""
    print("\n=== 测试公共接口 ===")
    
    try:
        # 测试根路径
        response = requests.get("http://127.0.0.1:5001/")
        if response.status_code == 200:
            print("✅ 根路径访问成功！")
            return True
        else:
            print(f"❌ 根路径访问失败！HTTP状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"公共接口测试失败！发生错误: {e}")
        return False

if __name__ == "__main__":
    # 1. 测试公共访问
    test_public_access()
    
    # 2. 先尝试登录
    cookies = test_login()
    
    # 如果登录失败，尝试注册
    if not cookies:
        register_success = test_register()
        if register_success:
            cookies = test_login()
    
    # 3. 如果获取到cookies，测试评估功能
    if cookies:
        test_assess(cookies)
    else:
        print("\n❌ 无法获取认证信息，评估测试无法进行")
