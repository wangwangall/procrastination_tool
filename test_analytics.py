import requests

# 测试URL
BASE_URL = 'http://localhost:5001'

def test_analytics():
    print("=== 测试数据分析API ===")
    
    response = requests.get(f'{BASE_URL}/analytics')
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success' and data.get('data'):
            analytics_data = data['data']
            print(f"\n数据分析结果:")
            print(f"总评估次数: {analytics_data['total_records']}")
            print(f"平均拖延概率: {analytics_data['average_probability']:.4f}")
            print(f"拖延率: {analytics_data['delay_rate']:.4f}")
            print(f"平均任务厌恶度: {analytics_data['average_task_aversion']:.2f}")
            print(f"平均结果价值感: {analytics_data['average_result_value']:.2f}")
            print(f"平均自我控制能力: {analytics_data['average_self_control']:.2f}")
            print(f"趋势数据数量: {len(analytics_data['trend'])}")
            return True
    return False

if __name__ == "__main__":
    success = test_analytics()
    if success:
        print("\n测试通过！")
    else:
        print("\n测试失败！")