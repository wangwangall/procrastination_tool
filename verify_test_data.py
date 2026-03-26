import sqlite3

# 连接到数据库
conn = sqlite3.connect('data/risk_records.db')
cursor = conn.cursor()

# 检查core_function_results表的记录数
cursor.execute('SELECT COUNT(*) FROM core_function_results')
count = cursor.fetchone()[0]
print(f'Number of records in core_function_results: {count}')

# 显示前10条记录
cursor.execute('SELECT id, anonymous_id, score, risk_level, timestamp FROM core_function_results ORDER BY timestamp DESC LIMIT 10')
records = cursor.fetchall()
print('\nLast 10 records:')
for record in records:
    print(f'ID: {record[0]}, User: {record[1]}, Score: {record[2]}, Risk: {record[3]}, Created: {record[4]}')

# 关闭连接
conn.close()