import sqlite3
import os

# 正确的数据库路径
data_dir = 'data'
db_path = os.path.join(data_dir, 'risk_records.db')

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 检查test_user_123的记录 ===")

# 检查test_user_123在anonymous_users表中是否存在
cursor.execute('SELECT * FROM anonymous_users WHERE anonymous_id = ?', ('test_user_123',))
user = cursor.fetchone()
if user:
    print("test_user_123在anonymous_users表中存在")
    print(f"用户信息: {user}")
else:
    print("test_user_123在anonymous_users表中不存在")

# 检查test_user_123在core_function_results表中是否有记录
cursor.execute('SELECT COUNT(*) FROM core_function_results WHERE anonymous_id = ?', ('test_user_123',))
count = cursor.fetchone()[0]
print(f"\ntest_user_123在core_function_results表中的记录数量: {count}")

# 如果没有记录，创建一些测试数据
if count == 0:
    print("\n=== 为test_user_123创建测试记录 ===")
    
    # 插入3条测试记录
    test_records = [
        ('test_user_123', 80, 50, 30, 0.4, 0.3, 0.3, 68.0, '中', '中等', '一致', '-告诉家人/同事：‘接下来1小时我在忙任务，请勿打扰’，用外部边界保护你的时间。', '2026-03-19 14:00:00', ''),
        ('test_user_123', 60, 70, 50, 0.4, 0.3, 0.3, 53.0, '中', '中等', '一致', '找个朋友互相打卡：‘我今天完成了XX，你呢？’，社交监督比独自硬抗更有效。', '2026-03-19 15:00:00', ''),
        ('test_user_123', 30, 90, 80, 0.4, 0.3, 0.3, 31.0, '低', '低', '一致', '开启手机‘专注模式（关闭微信/抖音通知），或把手机锁机，告诉自己‘先专注25分钟再说’。', '2026-03-19 16:00:00', '')
    ]
    
    cursor.executemany('''
    INSERT INTO core_function_results (anonymous_id, task_aversion, result_value, self_control, 
                                      w1, w2, w3, score, risk_level, model_prediction, 
                                      comparison, suggestion, timestamp, user_notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_records)
    
    conn.commit()
    print(f"已为test_user_123创建了{len(test_records)}条测试记录")
    
    # 验证插入结果
    cursor.execute('SELECT COUNT(*) FROM core_function_results WHERE anonymous_id = ?', ('test_user_123',))
    new_count = cursor.fetchone()[0]
    print(f"插入后test_user_123的记录数量: {new_count}")
    
    # 查看插入的记录
    cursor.execute('SELECT * FROM core_function_results WHERE anonymous_id = ?', ('test_user_123',))
    inserted_records = cursor.fetchall()
    print("\n插入的记录:")
    for record in inserted_records:
        print(record)

conn.close()
