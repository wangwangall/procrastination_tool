import sqlite3

# 连接数据库
db_path = 'risk_records.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 检查数据库中的匿名用户 ===")
cursor.execute('SELECT anonymous_id, w1, w2, w3, created_at FROM anonymous_users')
anonymous_users = cursor.fetchall()
print(f"匿名用户数量: {len(anonymous_users)}")
for user in anonymous_users:
    print(f"匿名ID: {user[0]}, 权重: {user[1]}, {user[2]}, {user[3]}, 创建时间: {user[4]}")

print("\n=== 检查core_function_results表中的记录 ===")
cursor.execute('SELECT DISTINCT anonymous_id FROM core_function_results')
distinct_anonymous_ids = cursor.fetchall()
print(f"core_function_results表中的不同匿名ID数量: {len(distinct_anonymous_ids)}")
for anon_id in distinct_anonymous_ids:
    cursor.execute('SELECT COUNT(*) FROM core_function_results WHERE anonymous_id = ?', (anon_id[0],))
    count = cursor.fetchone()[0]
    print(f"匿名ID: {anon_id[0]}, 记录数量: {count}")

# 特别检查test_user_123
test_anon_id = 'test_user_123'
cursor.execute('SELECT COUNT(*) FROM core_function_results WHERE anonymous_id = ?', (test_anon_id,))
test_count = cursor.fetchone()[0]
print(f"\n'test_user_123'的记录数量: {test_count}")

# 如果没有test_user_123的记录，查看所有记录
if test_count == 0:
    print("\n=== 查看前5条core_function_results记录 ===")
    cursor.execute('SELECT anonymous_id, task_aversion, result_value, self_control, timestamp FROM core_function_results LIMIT 5')
    sample_records = cursor.fetchall()
    for record in sample_records:
        print(record)

conn.close()
