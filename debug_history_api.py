import requests
import json

# 调试历史记录API
def debug_history_api():
    print("=== 调试历史记录API ===")
    
    # 1. 直接查询core_function_results表的test_user_123记录
    print("\n1. 查询core_function_results表的test_user_123记录:")
    core_url = "http://localhost:5001/history?anonymous_id=test_user_123"
    response = requests.get(core_url)
    response.raise_for_status()
    core_data = response.json()
    print(f"   状态: {core_data['status']}")
    print(f"   历史记录数量: {len(core_data['history'])}")
    
    # 2. 查看返回的完整JSON数据
    print("\n2. 返回的完整JSON数据:")
    print(json.dumps(core_data, indent=2, ensure_ascii=False))
    
    # 3. 测试获取所有记录
    print("\n3. 测试获取所有记录 (使用新创建的用户):")
    # 先发送一个预测请求获取新的匿名ID
    predict_url = "http://localhost:5001/predict"
    payload = {
        "任务厌恶": 60,
        "结果价值": 70,
        "自我控制": 50
    }
    headers = {
        "Content-Type": "application/json"
    }
    predict_response = requests.post(predict_url, json=payload, headers=headers, cookies={}, allow_redirects=False)
    predict_response.raise_for_status()
    predict_data = predict_response.json()
    new_anonymous_id = predict_data['anonymous_id']
    print(f"   新生成的匿名ID: {new_anonymous_id}")
    
    # 使用新的匿名ID获取历史记录
    new_history_url = f"http://localhost:5001/history?anonymous_id={new_anonymous_id}"
    new_response = requests.get(new_history_url)
    new_response.raise_for_status()
    new_history_data = new_response.json()
    print(f"   新用户历史记录数量: {len(new_history_data['history'])}")
    
    print("\n=== 调试完成 ===")

if __name__ == "__main__":
    debug_history_api()
