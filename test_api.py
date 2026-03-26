import requests

# 测试注册API
response = requests.post('http://localhost:5001/api/register', json={
    'phone': '13800138000',
    'username': 'testuser',
    'password': 'test123456'
})

print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")
