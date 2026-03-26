#!/usr/bin/env python3
# coding: utf-8

import sqlite3

# 数据库路径
db_path = 'd:/procrastination_tool/data/risk_records.db'

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== anonymous_users表 ===")
cursor.execute('SELECT * FROM anonymous_users')
anonymous_users = cursor.fetchall()
print("字段: id, anonymous_id, w1, w2, w3, created_at")
for user in anonymous_users:
    print(user)

print("\n=== core_function_results表 ===")
cursor.execute('SELECT * FROM core_function_results LIMIT 10')
core_results = cursor.fetchall()
print("字段: id, anonymous_id, task_aversion, result_value, self_control, w1, w2, w3, score, risk_level, user_notes, timestamp")
for result in core_results:
    print(result)

# 关闭数据库连接
conn.close()
