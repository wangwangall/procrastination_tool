import requests

# 登录
login_response = requests.post('http://localhost:5001/api/login', json={
    'identifier': '15314244412',
    'password': 'wwall334133'
})

print(f"登录状态码: {login_response.status_code}")
cookies = login_response.cookies

# 测试提交反馈
feedback_response = requests.post('http://localhost:5001/api/feedback', json={
    'suggestion_id': 'suggestion_test_001',
    'suggestion_content': '立即行动：把任务拆分成最小可执行步骤',
    'risk_level': '高',
    'feedback_type': 'useful'
}, cookies=cookies)

print(f"\n反馈提交状态码: {feedback_response.status_code}")
print(f"反馈提交响应: {feedback_response.text}")

# 测试获取反馈统计
stats_response = requests.get('http://localhost:5001/api/feedback/stats', cookies=cookies)
print(f"\n反馈统计状态码: {stats_response.status_code}")
print(f"反馈统计响应: {stats_response.text}")
