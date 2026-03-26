import requests
import json

# 测试test_user_123的历史记录
def test_test_user_history():
    print("=== 测试test_user_123的历史记录 ===")
    
    # 直接使用test_user_123作为匿名ID
    anonymous_id = 'test_user_123'
    history_url = f"http://localhost:5001/history?anonymous_id={anonymous_id}"
    
    try:
        # 获取历史记录
        response = requests.get(history_url)
        response.raise_for_status()
        
        history_data = response.json()
        
        print(f"1. 历史记录数量: {len(history_data['history'])}")
        
        # 打印前10条记录
        print("2. 最新的10条历史记录:")
        for i, record in enumerate(history_data['history'][:10]):
            score = record['score']
            # 确保分数是数字
            if isinstance(score, str):
                score = float(score)
            elif score is None:
                score = 0.0
            print(f"   {i+1}. 时间: {record['timestamp']}, 分数: {score:.1f}, 风险等级: {record['risk_level']}")
        
        print("\n=== 测试完成 ===")
        print(f"结论: test_user_123现在可以看到{len(history_data['history'])}条历史记录")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_test_user_history()
