#!/usr/bin/env python3
"""
一个简单的Flask应用，用于测试服务器是否能正常启动
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    print("启动简单Flask服务器...")
    app.run(host='0.0.0.0', port=5001, debug=True)
