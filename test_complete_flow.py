import requests
import json
import time

# 测试服务器URL
BASE_URL = 'http://127.0.0.1:5001'

def test_predict_as_anonymous():
    """测试匿名用户的评估功能"""
    print("=== 测试匿名用户评估功能 ===")
    
    # 构造测试数据
    test_data = {
        "task_aversion": 60,
        "result_value": 70,
        "self_control": 50
    }
    
    # 发送POST请求
    response = requests.post(f'{BASE_URL}/predict', json=test_data)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 匿名用户评估功能测试成功")
        return True, response.json()
    else:
        print("❌ 匿名用户评估功能测试失败")
        return False, None

def test_register_and_login():
    """测试用户注册和登录功能"""
    print("\n=== 测试用户注册和登录功能 ===")
    
    # 生成随机手机号和用户名，避免重复
    timestamp = int(time.time())
    phone = f"1380013{timestamp % 10000}"
    username = f"test_user_{timestamp}"
    password = "test_password"
    
    print(f"使用测试账号: {phone}, 密码: {password}")
    
    # 1. 测试注册
    register_data = {
        "phone": phone,
        "username": username,
        "password": password
    }
    
    register_response = requests.post(f'{BASE_URL}/register', json=register_data)
    print(f"注册响应状态码: {register_response.status_code}")
    print(f"注册响应内容: {register_response.text}")
    
    if register_response.status_code != 200:
        print("❌ 用户注册失败")
        return False, None, None
    
    # 2. 测试登录
    login_data = {
        "identifier": phone,
        "password": password
    }
    
    login_response = requests.post(f'{BASE_URL}/login', json=login_data)
    print(f"登录响应状态码: {login_response.status_code}")
    print(f"登录响应内容: {login_response.text}")
    
    if login_response.status_code == 200:
        print("✅ 用户注册和登录功能测试成功")
        return True, login_response.cookies, login_response.json()
    else:
        print("❌ 用户登录失败")
        return False, None, None

def test_predict_as_logged_in_user(cookies, user_info):
    """测试登录用户的评估功能"""
    print("\n=== 测试登录用户评估功能 ===")
    
    # 构造测试数据
    test_data = {
        "task_aversion": 60,
        "result_value": 70,
        "self_control": 50
    }
    
    # 发送POST请求，包含登录cookie
    response = requests.post(f'{BASE_URL}/predict', json=test_data, cookies=cookies)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 登录用户评估功能测试成功")
        return True
    else:
        print("❌ 登录用户评估功能测试失败")
        return False

def test_get_history_as_logged_in_user(cookies):
    """测试登录用户获取历史记录功能"""
    print("\n=== 测试登录用户获取历史记录功能 ===")
    
    # 发送GET请求，包含登录cookie
    response = requests.get(f'{BASE_URL}/history', cookies=cookies)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 登录用户获取历史记录功能测试成功")
        return True
    else:
        print("❌ 登录用户获取历史记录功能测试失败")
        return False

def test_get_analytics_as_logged_in_user(cookies):
    """测试登录用户获取数据分析功能"""
    print("\n=== 测试登录用户获取数据分析功能 ===")
    
    # 发送GET请求，包含登录cookie
    response = requests.get(f'{BASE_URL}/analytics', cookies=cookies)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 登录用户获取数据分析功能测试成功")
        return True
    else:
        print("❌ 登录用户获取数据分析功能测试失败")
        return False

if __name__ == "__main__":
    print("开始完整流程测试...")
    
    # 测试1: 匿名用户评估
    anon_success, anon_result = test_predict_as_anonymous()
    
    # 测试2: 用户注册和登录
    register_success, cookies, user_info = test_register_and_login()
    
    # 测试3: 登录用户评估
    logged_in_predict_success = False
    if register_success and cookies:
        logged_in_predict_success = test_predict_as_logged_in_user(cookies, user_info)
    
    # 测试4: 登录用户获取历史记录
    history_success = False
    if register_success and cookies:
        history_success = test_get_history_as_logged_in_user(cookies)
    
    # 测试5: 登录用户获取数据分析
    analytics_success = False
    if register_success and cookies:
        analytics_success = test_get_analytics_as_logged_in_user(cookies)
    
    # 测试总结
    print("\n=== 测试结果总结 ===")
    print(f"匿名用户评估: {'✅ 成功' if anon_success else '❌ 失败'}")
    print(f"用户注册和登录: {'✅ 成功' if register_success else '❌ 失败'}")
    print(f"登录用户评估: {'✅ 成功' if logged_in_predict_success else '❌ 失败'}")
    print(f"登录用户获取历史记录: {'✅ 成功' if history_success else '❌ 失败'}")
    print(f"登录用户获取数据分析: {'✅ 成功' if analytics_success else '❌ 失败'}")
    
    # 计算通过率
    total_tests = 5
    passed_tests = sum([anon_success, register_success, logged_in_predict_success, history_success, analytics_success])
    print(f"\n整体通过率: {passed_tests/total_tests*100}%")
    
    if passed_tests == total_tests:
        print("✅ 所有测试都已通过，系统功能正常")
    else:
        print("❌ 部分测试失败，请检查系统功能")
