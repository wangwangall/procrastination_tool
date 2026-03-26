import requests

# 登录
login_response = requests.post('http://localhost:5001/api/login', json={
    'identifier': '15314244412',
    'password': 'wwall334133'
}, cookies={})

print(f"登录状态码: {login_response.status_code}")
print(f"登录响应: {login_response.text}")

cookies = login_response.cookies

# 进行评估
assess_response = requests.post('http://localhost:5001/api/assess', json={
    'task_aversion': 60,
    'result_value': 70,
    'self_control': 50,
    'user_notes': '测试报告路径'
}, cookies=cookies)

print(f"\n评估状态码: {assess_response.status_code}")
assess_data = assess_response.json()
print(f"评估响应: {assess_data}")

if assess_data.get('status') == 'success':
    report_path = assess_data['result']['report_path']
    print(f"\n报告路径: {report_path}")
    
    # 测试访问报告
    # 提取相对路径
    path_parts = report_path.replace('\\', '/').split('/')
    relative_path = '/'.join(path_parts[-2:])
    print(f"相对路径: {relative_path}")
    
    report_url = f"http://localhost:5001/api/report/{relative_path}"
    print(f"报告URL: {report_url}")
    
    report_response = requests.get(report_url)
    print(f"报告访问状态码: {report_response.status_code}")
