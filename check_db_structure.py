import sqlite3
import os

# 正确的数据库路径（与app.py中的设置一致）
data_dir = 'data'
db_path = os.path.join(data_dir, 'risk_records.db')

print(f"检查数据库文件: {db_path}")
print(f"文件存在: {os.path.exists(db_path)}")
if os.path.exists(db_path):
    print(f"文件大小: {os.path.getsize(db_path)} 字节")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n=== 检查数据库中的所有表 ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"数据库中的表数量: {len(tables)}")
for table in tables:
    table_name = table[0]
    print(f"\n=== 表: {table_name} ===")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for column in columns:
        print(f"列名: {column[1]}, 类型: {column[2]}, 是否为主键: {column[5]}")

# 检查core_function_results表中的数据
if any('core_function_results' in table for table in tables):
    print("\n=== core_function_results表中的记录数量 ===")
    cursor.execute('SELECT COUNT(*) FROM core_function_results')
    count = cursor.fetchone()[0]
    print(f"记录数量: {count}")
    
    # 查看前3条记录
    print("\n前3条记录:")
    cursor.execute('SELECT * FROM core_function_results LIMIT 3')
    records = cursor.fetchall()
    for record in records:
        print(record)

# 检查anonymous_users表
if any('anonymous_users' in table for table in tables):
    print("\n=== anonymous_users表中的记录 ===")
    cursor.execute('SELECT * FROM anonymous_users')
    users = cursor.fetchall()
    print(f"匿名用户数量: {len(users)}")
    for user in users:
        print(f"用户ID: {user[0]}, 匿名ID: {user[1]}, 权重: {user[2]}, {user[3]}, {user[4]}, 创建时间: {user[5]}")

conn.close()
