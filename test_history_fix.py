import requests
import json

# 测试数据
test_data = {
    "任务厌恶": 80,
    "结果价值": 50,
    "自我控制": 30
}

# 第一次测试：获取匿名ID
try:
    print("=== 第一次测试：获取匿名ID ===")
    response = requests.post(
        "http://127.0.0.1:5001/predict",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        anonymous_id = result['anonymous_id']
        print(f"✅ 第一次测试成功，匿名ID: {anonymous_id}")
        print(f"核心函数结果: {result['core_function_result']['风险等级']} (分数: {result['core_function_result']['分数']})")
        print(f"模型预测结果: {result['model_prediction']}")
    else:
        print(f"❌ 第一次测试失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        exit()
except Exception as e:
    print(f"❌ 第一次测试失败: {e}")
    exit()

# 第二次测试：使用相同的匿名ID进行测试
print("\n=== 第二次测试：使用相同的匿名ID进行测试 ===")
try:
    response = requests.post(
        "http://127.0.0.1:5001/predict",
        json=test_data,
        headers={
            "Content-Type": "application/json",
            "X-Anonymous-ID": anonymous_id
        },
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 第二次测试成功，返回的匿名ID: {result['anonymous_id']}")
        print(f"核心函数结果: {result['core_function_result']['风险等级']} (分数: {result['core_function_result']['分数']})")
        print(f"模型预测结果: {result['model_prediction']}")
    else:
        print(f"❌ 第二次测试失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        exit()
except Exception as e:
    print(f"❌ 第二次测试失败: {e}")
    exit()

# 第三次测试：获取历史记录
print("\n=== 第三次测试：获取历史记录 ===")
try:
    response = requests.get(
        f"http://127.0.0.1:5001/history?anonymous_id={anonymous_id}",
        headers={"X-Anonymous-ID": anonymous_id},
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        history_length = len(result['history'])
        print(f"✅ 第三次测试成功，历史记录数量: {history_length}")
        print(f"所有历史记录: {json.dumps(result['history'], indent=2, ensure_ascii=False)}")
        
        if history_length >= 2:
            print("\n🎉 测试成功！历史页面现在能显示所有记录了！")
        else:
            print("\n⚠️ 测试成功，但历史记录数量不足，可能需要多测试几次")
    else:
        print(f"❌ 第三次测试失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
except Exception as e:
    print(f"❌ 第三次测试失败: {e}")

# 第四次测试：获取数据分析
print("\n=== 第四次测试：获取数据分析 ===")
try:
    response = requests.get(
        "http://127.0.0.1:5001/analytics",
        headers={"X-Anonymous-ID": anonymous_id},
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        total_records = result['data']['total_records']
        print(f"✅ 第四次测试成功，总记录数: {total_records}")
        print(f"数据分析结果: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ 第四次测试失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
except Exception as e:
    print(f"❌ 第四次测试失败: {e}")