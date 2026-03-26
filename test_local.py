#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试本地服务器是否正常运行
"""

import requests
import json

def test_local_server():
    """测试本地服务器是否正常运行"""
    print("=== 测试本地服务器 ===")
    
    # 1. 测试根路径
    print("1. 测试根路径访问...")
    try:
        response = requests.get("http://localhost:5001/")
        if response.status_code == 200:
            print("根路径访问成功！")
            print(f"   响应长度: {len(response.text)} 字节")
            print(f"   响应内容类型: {response.headers.get('Content-Type')}")
        else:
            print(f"根路径访问失败！HTTP状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"根路径访问错误: {e}")
        return False
    
    # 2. 测试API路径
    print("\n2. 测试API路径访问...")
    try:
        response = requests.get("http://localhost:5001/api/user", cookies={})
        if response.status_code in [200, 401]:
            print("API路径访问成功！")
            print(f"   响应状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
        else:
            print(f"API路径访问失败！HTTP状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"API路径访问错误: {e}")
        return False
    
    print("\n=== 本地服务器测试通过！ ===")
    return True

if __name__ == "__main__":
    test_local_server()
