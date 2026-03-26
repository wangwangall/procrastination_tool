import requests
import json

# 测试历史记录API返回的建议是否正确
def test_suggestion():
    print("=== 测试历史记录API建议功能 ===")
    
    # 1. 发送评估请求获取匿名ID
    print("1. 发送评估请求...")
    predict_url = "http://localhost:5001/predict"
    payload = {
        "任务厌恶": 80,
        "结果价值": 40,
        "自我控制": 50
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(predict_url, json=payload, headers=headers, cookies={}, allow_redirects=False)
    response.raise_for_status()
    
    data = response.json()
    anonymous_id = data['anonymous_id']
    print(f"   评估成功，匿名ID: {anonymous_id}")
    
    # 2. 获取历史记录
    print("2. 获取历史记录...")
    history_url = f"http://localhost:5001/history?anonymous_id={anonymous_id}"
    history_response = requests.get(history_url)
    history_response.raise_for_status()
    
    history_data = history_response.json()
    print(f"   历史记录数量: {len(history_data['history'])}")
    
    # 3. 检查第一条记录的建议
    if history_data['history']:
        latest_record = history_data['history'][0]
        print(f"3. 最新记录详情:")
        print(f"   任务厌恶: {latest_record['task_aversion']}")
        print(f"   结果价值: {latest_record['result_value']}")
        print(f"   自我控制: {latest_record['self_control']}")
        print(f"   分数: {latest_record['score']}")
        print(f"   风险等级: {latest_record['risk_level']}")
        print(f"   建议: {latest_record['suggestion']}")
        
        # 验证建议是否正确
        if latest_record['risk_level'] == '高' and '立即采取行动' in latest_record['suggestion']:
            print("\n✅ 测试通过: 高风险记录返回了正确的建议")
        elif latest_record['risk_level'] == '中' and '制定合理的计划' in latest_record['suggestion']:
            print("\n✅ 测试通过: 中风险记录返回了正确的建议")
        elif latest_record['risk_level'] == '低' and '继续保持' in latest_record['suggestion']:
            print("\n✅ 测试通过: 低风险记录返回了正确的建议")
        else:
            print(f"\n❌ 测试失败: 建议与风险等级不匹配")
    else:
        print("\n❌ 测试失败: 没有历史记录")

if __name__ == "__main__":
    test_suggestion()