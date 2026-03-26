import requests

# 测试历史记录API
print("=== 测试历史记录API ===")
anonymous_id = 'test_user_123'
url = f'http://localhost:5001/history?anonymous_id={anonymous_id}'

print(f"请求URL: {url}")

try:
    response = requests.get(url)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {data}")
        if data.get('status') == 'success':
            history = data.get('history', [])
            print(f"返回的历史记录数量: {len(history)}")
            if history:
                print("第一条记录:")
                print(history[0])
    else:
        print(f"API调用失败，响应内容: {response.text}")
except Exception as e:
    print(f"API调用出错: {e}")
