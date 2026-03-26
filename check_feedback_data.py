import sqlite3

# 检查user_feedback表中的数据
def check_feedback_data():
    print("检查反馈数据...")
    
    try:
        conn = sqlite3.connect('data/risk_records.db')
        cursor = conn.cursor()
        
        # 检查user_feedback表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_feedback'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("user_feedback表不存在")
            return
        
        # 查询最近的5条反馈记录
        cursor.execute('SELECT * FROM user_feedback ORDER BY id DESC LIMIT 5')
        feedbacks = cursor.fetchall()
        
        print(f"找到 {len(feedbacks)} 条反馈记录")
        for feedback in feedbacks:
            print(f"ID: {feedback[0]}, 记录ID: {feedback[1]}, 用户ID: {feedback[2]}, 反馈: {feedback[3]}, 评论: {feedback[4]}, 时间: {feedback[5]}")
        
        conn.close()
    except Exception as e:
        print(f"检查反馈数据失败: {e}")

if __name__ == "__main__":
    check_feedback_data()
