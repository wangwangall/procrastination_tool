import sqlite3

# 连接数据库
conn = sqlite3.connect('data/risk_records.db')
cursor = conn.cursor()

# 查询user_id字段的分布情况
print('查询user_id字段的分布情况：')
cursor.execute('''
SELECT user_id, COUNT(*) as count
FROM risk_records
GROUP BY user_id
''')
user_id_stats = cursor.fetchall()

print('user_id | 记录数')
print('-' * 30)
for stat in user_id_stats:
    user_id = stat[0] if stat[0] is not None else 'NULL'
    print(f'{user_id:<7} | {stat[1]}')

# 查询user_id为1或NULL的记录
print('\n查询user_id为1或NULL的记录（前10条）：')
cursor.execute('''
SELECT task_aversion, result_value, self_control, actual_delay, user_id
FROM risk_records
WHERE user_id = ? OR user_id IS NULL
LIMIT 10
''', (1,))
user_1_records = cursor.fetchall()

print('task_aversion | result_value | self_control | actual_delay | user_id')
print('-' * 75)
for record in user_1_records:
    print(f'{record[0]:<13} | {record[1]:<13} | {record[2]:<13} | {record[3]:<13} | {record[4]}')

# 计算user_id为1或NULL的记录的平均值
print('\n计算user_id为1或NULL的记录的平均值：')
cursor.execute('''
SELECT 
    AVG(task_aversion) as avg_task_aversion,
    AVG(result_value) as avg_result_value,
    AVG(self_control) as avg_self_control
FROM risk_records
WHERE user_id = ? OR user_id IS NULL
''', (1,))
avg_stats = cursor.fetchone()

print(f'user_id为1或NULL的记录数量: {user_id_stats[0][1]}')
print(f'平均 task_aversion: {avg_stats[0]}')
print(f'平均 result_value: {avg_stats[1]}')
print(f'平均 self_control: {avg_stats[2]}')

# 关闭连接
conn.close()