import sqlite3
import os

# 检查risk_records表的详细信息
def check_risk_records():
    print("=== 检查risk_records表的详细信息 ===")
    
    # 数据库路径
    data_dir = 'data'
    db_path = os.path.join(data_dir, 'risk_records.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看risk_records表的结构
    print("1. risk_records表结构:")
    cursor.execute("PRAGMA table_info(risk_records)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"   {col[1]}: {col[2]}")
    
    # 查看前10条记录
    print("\n2. risk_records表前10条记录:")
    cursor.execute("SELECT * FROM risk_records LIMIT 10")
    records = cursor.fetchall()
    for record in records:
        print(f"   {record}")
    
    # 查看record_id字段的最大值
    print("\n3. risk_records表记录统计:")
    cursor.execute("SELECT MAX(id) FROM risk_records")
    max_id = cursor.fetchone()[0]
    print(f"   最大ID: {max_id}")
    
    # 按user_id分组统计
    cursor.execute("SELECT user_id, COUNT(*) as count FROM risk_records GROUP BY user_id")
    user_counts = cursor.fetchall()
    print("   按user_id分组统计:")
    for user_id, count in user_counts:
        print(f"   - user_id={user_id}: {count}条")
    
    # 检查是否有task_aversion为NULL的记录
    cursor.execute("SELECT COUNT(*) FROM risk_records WHERE task_aversion IS NULL")
    null_task_aversion = cursor.fetchone()[0]
    print(f"   task_aversion为NULL的记录数: {null_task_aversion}")
    
    conn.close()
    
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    check_risk_records()
