import requests
import json

# 测试数据
test_data = {
    "任务厌恶": 80,
    "结果价值": 50,
    "自我控制": 30
}

# 发送预测请求
try:
    response = requests.post(
        "http://127.0.0.1:5001/predict",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        print("预测成功!")
        print(f"核心函数结果: {result['core_function_result']['风险等级']} (分数: {result['core_function_result']['分数']})")
        print(f"模型预测结果: {result['model_prediction']}")
        print(f"结果对比: {result['comparison']}")
        print(f"建议: {result['建议']}")
        print(f"报告路径: {result['report_path']}")
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
except Exception as e:
    print(f"测试失败: {e}")
    print("请确保服务器正在运行 (python -m flask run --port=5001)")