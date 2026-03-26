#!/usr/bin/env python3
"""
测试所有功能的脚本
"""

import requests
import json
import time

# 测试服务器地址
BASE_URL = "http://localhost:5001"

# 测试用手机号和邮箱
TEST_PHONE = "13800138000"
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "测试用户"
TEST_PASSWORD = "password123"


def test_register():
    """测试用户注册功能"""
    print("=== 测试用户注册功能 ===")
    
    # 准备注册数据
    register_data = {
        "phone": TEST_PHONE,
        "email": TEST_EMAIL,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        # 发送注册请求
        response = requests.post(f"{BASE_URL}/register", json=register_data, cookies={})
        print(f"注册响应状态码: {response.status_code}")
        print(f"注册响应内容: {response.text}")
        
        # 检查响应
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("✅ 用户注册成功")
                return True, data.get("user_id")
        print("❌ 用户注册失败")
        return False, None
    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return False, None


def test_login():
    """测试用户登录功能"""
    print("\n=== 测试用户登录功能 ===")
    
    # 准备登录数据（使用邮箱登录）
    login_data = {
        "identifier": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        # 发送登录请求
        response = requests.post(f"{BASE_URL}/login", json=login_data, cookies={})
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        # 检查响应
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("✅ 用户登录成功")
                # 获取cookie
                cookies = response.cookies.get_dict()
                return True, cookies
        print("❌ 用户登录失败")
        return False, None
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return False, None


def test_predict(cookies):
    """测试风险评估功能"""
    print("\n=== 测试风险评估功能 ===")
    
    # 准备评估数据
    predict_data = {
        "task_aversion": 60,
        "result_value": 70,
        "self_control": 50
    }
    
    try:
        # 发送评估请求
        response = requests.post(f"{BASE_URL}/predict", json=predict_data, cookies=cookies)
        print(f"评估响应状态码: {response.status_code}")
        print(f"评估响应内容: {response.text}")
        
        # 检查响应
        if response.status_code == 200:
            data = response.json()
            if "core_function_result" in data:
                print("✅ 风险评估功能正常")
                return True
        print("❌ 风险评估功能异常")
        return False
    except Exception as e:
        print(f"❌ 评估请求失败: {e}")
        return False


def test_history(cookies):
    """测试历史记录功能"""
    print("\n=== 测试历史记录功能 ===")
    
    try:
        # 发送历史记录请求
        response = requests.get(f"{BASE_URL}/history", cookies=cookies)
        print(f"历史记录响应状态码: {response.status_code}")
        print(f"历史记录响应内容: {response.text}")
        
        # 检查响应
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                history = data.get("history", [])
                print(f"✅ 历史记录功能正常，共 {len(history)} 条记录")
                return True
        print("❌ 历史记录功能异常")
        return False
    except Exception as e:
        print(f"❌ 历史记录请求失败: {e}")
        return False


def test_analytics(cookies):
    """测试数据分析功能"""
    print("\n=== 测试数据分析功能 ===")
    
    try:
        # 发送数据分析请求
        response = requests.get(f"{BASE_URL}/analytics", cookies=cookies)
        print(f"数据分析响应状态码: {response.status_code}")
        print(f"数据分析响应内容: {response.text}")
        
        # 检查响应
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("✅ 数据分析功能正常")
                return True
        print("❌ 数据分析功能异常")
        return False
    except Exception as e:
        print(f"❌ 数据分析请求失败: {e}")
        return False


def test_logout(cookies):
    """测试用户登出功能"""
    print("\n=== 测试用户登出功能 ===")
    
    try:
        # 发送登出请求
        response = requests.post(f"{BASE_URL}/logout", cookies=cookies)
        print(f"登出响应状态码: {response.status_code}")
        print(f"登出响应内容: {response.text}")
        
        # 检查响应
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("✅ 用户登出成功")
                return True
        print("❌ 用户登出失败")
        return False
    except Exception as e:
        print(f"❌ 登出请求失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始测试所有功能...")
    
    # 测试注册
    register_success, user_id = test_register()
    if not register_success:
        print("注册失败，测试结束")
        return
    
    # 等待1秒
    time.sleep(1)
    
    # 测试登录
    login_success, cookies = test_login()
    if not login_success:
        print("登录失败，测试结束")
        return
    
    # 等待1秒
    time.sleep(1)
    
    # 测试风险评估
    predict_success = test_predict(cookies)
    
    # 等待1秒
    time.sleep(1)
    
    # 测试历史记录
    history_success = test_history(cookies)
    
    # 等待1秒
    time.sleep(1)
    
    # 测试数据分析
    analytics_success = test_analytics(cookies)
    
    # 等待1秒
    time.sleep(1)
    
    # 测试登出
    logout_success = test_logout(cookies)
    
    # 总结测试结果
    print("\n=== 测试结果总结 ===")
    print(f"用户注册: {'✅ 成功' if register_success else '❌ 失败'}")
    print(f"用户登录: {'✅ 成功' if login_success else '❌ 失败'}")
    print(f"风险评估: {'✅ 成功' if predict_success else '❌ 失败'}")
    print(f"历史记录: {'✅ 成功' if history_success else '❌ 失败'}")
    print(f"数据分析: {'✅ 成功' if analytics_success else '❌ 失败'}")
    print(f"用户登出: {'✅ 成功' if logout_success else '❌ 失败'}")
    
    # 计算通过率
    tests = [register_success, login_success, predict_success, history_success, analytics_success, logout_success]
    pass_rate = sum(tests) / len(tests) * 100
    print(f"\n整体通过率: {pass_rate:.1f}%")
    
    if pass_rate == 100:
        print("🎉 所有功能测试通过！")
    else:
        print("❌ 部分功能测试失败，请检查服务器日志和代码")


if __name__ == "__main__":
    main()
