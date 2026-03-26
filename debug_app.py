#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
拖延探索笔记本 - 调试启动脚本
"""

import sys
sys.path.insert(0, 'd:/procrastination_tool')

from app import app

# 打印所有路由
print("=" * 50)
print("Flask应用路由列表:")
print("=" * 50)
for rule in app.url_map.iter_rules():
    print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
print("=" * 50)

# 启动服务器
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
