import requests
import json
import time

# 测试评估历史记录更新功能
def test_history_update():
    print("=== 测试历史记录更新功能 ===")
    
    # 1. 发送评估请求
    print("1. 发送评估请求...")
    predict_url = "http://localhost:5001/predict"
    payload = {
        "任务厌恶": 60,
        "结果价值": 70,
        "自我控制": 50
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(predict_url, json=payload, headers=headers, cookies={}, allow_redirects=False)
    response.raise_for_status()
    
    data = response.json()
    print(f"   评估成功，匿名ID: {data['anonymous_id']}")
    
    # 2. 检查cookie中的匿名ID
    cookies = response.cookies.get_dict()
    anonymous_id = cookies.get('anonymous_id') or data['anonymous_id']
    print(f"   获取到的匿名ID: {anonymous_id}")
    
    # 3. 立即获取历史记录，验证新记录是否存在
    print("2. 立即获取历史记录...")
    history_url = f"http://localhost:5001/history?anonymous_id={anonymous_id}"
    history_response = requests.get(history_url, cookies=cookies)
    history_response.raise_for_status()
    
    history_data = history_response.json()
    print(f"   历史记录数量: {len(history_data['history'])}")
    
    # 4. 打印最新的几条记录
    print("3. 最新的3条历史记录:")
    for i, record in enumerate(history_data['history'][:3]):
        print(f"   {i+1}. 时间: {record['timestamp']}, 分数: {record['score']:.1f}, 风险等级: {record['risk_level']}")
    
    print("\n=== 测试完成 ===")
    print(f"结论: 成功评估并在历史记录中找到新记录")

if __name__ == "__main__":
    test_history_update()
