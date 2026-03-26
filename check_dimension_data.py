import sqlite3

# 连接数据库
conn = sqlite3.connect('data/risk_records.db')
cursor = conn.cursor()

# 查询数据，查看各维度字段的实际值
print('查询risk_records表中的数据（前10条）：')
cursor.execute('''
SELECT task_aversion, result_value, self_control, actual_delay
FROM risk_records
LIMIT 10
''')
records = cursor.fetchall()

print('task_aversion | result_value | self_control | actual_delay')
print('-' * 60)
for record in records:
    print(f'{record[0]:<13} | {record[1]:<13} | {record[2]:<13} | {record[3]}')

# 统计NULL值情况
print('\n统计各字段的NULL值情况：')
cursor.execute('''
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN task_aversion IS NULL THEN 1 ELSE 0 END) as task_aversion_null,
    SUM(CASE WHEN result_value IS NULL THEN 1 ELSE 0 END) as result_value_null,
    SUM(CASE WHEN self_control IS NULL THEN 1 ELSE 0 END) as self_control_null,
    SUM(CASE WHEN actual_delay IS NULL THEN 1 ELSE 0 END) as actual_delay_null
FROM risk_records
''')
null_stats = cursor.fetchone()

print(f'总记录数: {null_stats[0]}')
print(f'task_aversion NULL值数量: {null_stats[1]}')
print(f'result_value NULL值数量: {null_stats[2]}')
print(f'self_control NULL值数量: {null_stats[3]}')
print(f'actual_delay NULL值数量: {null_stats[4]}')

# 计算实际平均值
print('\n计算各字段的实际平均值：')
cursor.execute('''
SELECT 
    AVG(task_aversion) as avg_task_aversion,
    AVG(result_value) as avg_result_value,
    AVG(self_control) as avg_self_control
FROM risk_records
''')
avg_stats = cursor.fetchone()

print(f'实际平均 task_aversion: {avg_stats[0]}')
print(f'实际平均 result_value: {avg_stats[1]}')
print(f'实际平均 self_control: {avg_stats[2]}')

# 关闭连接
conn.close()