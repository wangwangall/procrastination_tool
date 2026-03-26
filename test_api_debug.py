import requests

# 登录
session = requests.Session()
login_response = session.post('http://localhost:5001/api/login', json={
    'identifier': '15314244412',
    'password': 'wwall334133'
})

print(f"登录状态: {login_response.status_code}")
print(f"登录响应: {login_response.json()}")

# 获取历史记录
history_response = session.get('http://localhost:5001/api/history')
print(f"\n历史记录状态: {history_response.status_code}")
print(f"历史记录数据: {history_response.json()}")

# 获取数据分析
analytics_response = session.get('http://localhost:5001/api/analytics')
print(f"\n数据分析状态: {analytics_response.status_code}")
print(f"数据分析数据: {analytics_response.json()}")
