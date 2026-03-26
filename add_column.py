import sqlite3

# 连接数据库
db_path = 'data/risk_records.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查表结构
print("当前表结构:")
cursor.execute("PRAGMA table_info(risk_records)")
columns = cursor.fetchall()
for column in columns:
    print(f"列名: {column[1]}, 类型: {column[2]}")

# 尝试添加task_aversion列
try:
    print("\n尝试添加task_aversion列...")
    cursor.execute("ALTER TABLE risk_records ADD COLUMN task_aversion INTEGER")
    print("task_aversion列添加成功!")
    conn.commit()
except Exception as e:
    print(f"添加列时出错: {e}")
    import traceback
    traceback.print_exc()

# 再次检查表结构
print("\n更新后的表结构:")
cursor.execute("PRAGMA table_info(risk_records)")
columns = cursor.fetchall()
for column in columns:
    print(f"列名: {column[1]}, 类型: {column[2]}")

# 关闭连接
conn.close()
