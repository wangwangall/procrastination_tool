# backend/app.py
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from backend.algorithm_core import get_risk_level, get_suggestions, calculate_score
import sqlite3
import os
import pickle
import bcrypt
import datetime
import uuid
import random
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 用于session加密
# 配置详细的CORS设置，解决跨域cookie问题
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:8080", "http://127.0.0.1:8080"],
        "supports_credentials": True,
        "allow_headers": ["Origin", "Content-Type", "Accept", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})
# 确保响应头包含正确的CORS信息
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 模型文件路径
model_path = 'model.pkl'
# 加载的模型
model = None

# 确保data目录存在
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 确保reports目录存在
reports_dir = os.path.join(data_dir, 'reports')
if not os.path.exists(reports_dir):
    os.makedirs(reports_dir)

# 数据库路径
db_path = os.path.join(data_dir, 'risk_records.db')

# 模型缓存，用于存储每个用户的模型
user_models = {}

# 获取当前用户ID或生成匿名ID
def get_current_user_id():
    """获取当前用户ID或生成匿名ID"""
    # 1. 优先从session获取登录用户ID
    if 'user_id' in session:
        return session['user_id']
    
    # 2. 如果未登录，生成或获取匿名ID
    # 从URL参数获取匿名ID
    anonymous_id = request.args.get('anonymous_id')
    
    # 如果URL参数中没有，从请求头获取
    if not anonymous_id:
        anonymous_id = request.headers.get('X-Anonymous-ID')
    
    # 如果请求头中没有，从cookie获取
    if not anonymous_id:
        anonymous_id = request.cookies.get('anonymous_id')
    
    # 如果所有地方都没有，生成新的匿名ID
    if not anonymous_id:
        anonymous_id = f'user_{uuid.uuid4().hex[:8]}'
    
    # 检查是否存在于数据库中
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM anonymous_users WHERE anonymous_id = ?', (anonymous_id,))
    user = cursor.fetchone()
    
    if not user:
        # 创建新匿名用户
        cursor.execute('INSERT INTO anonymous_users (anonymous_id) VALUES (?)', (anonymous_id,))
        conn.commit()
    
    conn.close()
    return anonymous_id

# 获取用户的自定义权重
def get_user_weights(user_id):
    """获取用户的自定义权重"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查是否为登录用户
    if user_id.startswith('user_') and len(user_id) > 5:
        # 登录用户，从weight_adjustments表获取最新权重
        cursor.execute('''
        SELECT w1, w2, w3 FROM weight_adjustments 
        WHERE user_id = ? 
        ORDER BY timestamp DESC LIMIT 1
        ''', (user_id,))
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return {
                'w1': result[0],
                'w2': result[1],
                'w3': result[2]
            }
    
    # 匿名用户或登录用户没有自定义权重，从anonymous_users表获取或返回默认值
    cursor.execute('SELECT w1, w2, w3 FROM anonymous_users WHERE anonymous_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'w1': result[0],
            'w2': result[1],
            'w3': result[2]
        }
    else:
        # 默认权重
        return {'w1': 0.4, 'w2': 0.3, 'w3': 0.3}

# 更新用户的自定义权重
def update_user_weights(user_id, w1, w2, w3):
    """更新用户的自定义权重"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查是否为登录用户
    if user_id.startswith('user_') and len(user_id) > 5:
        # 登录用户，插入新的权重调整记录
        cursor.execute('''
        INSERT INTO weight_adjustments (user_id, w1, w2, w3)
        VALUES (?, ?, ?, ?)
        ''', (user_id, w1, w2, w3))
    else:
        # 匿名用户，更新anonymous_users表
        cursor.execute('''
        UPDATE anonymous_users 
        SET w1 = ?, w2 = ?, w3 = ? 
        WHERE anonymous_id = ?
        ''', (w1, w2, w3, user_id))
    
    conn.commit()
    conn.close()

# 生成报告函数
def generate_report(anonymous_id, timestamp, task_aversion, result_value, self_control, w1, w2, w3, score, risk_level, model_prediction, comparison, suggestion, user_notes=None):
    """生成HTML报告"""
    # 格式化测算时间
    formatted_time = timestamp.replace('T', ' ').split('.')[0]
    
    # 处理模型预测结果的分数
    model_score = 0
    if model_prediction == '高':
        model_score = 85
    elif model_prediction == '中':
        model_score = 50
    elif model_prediction == '低':
        model_score = 15
    
    # 处理备注
    notes_html = ''
    if user_notes:
        notes_html = """
        <h2>备注</h2>
        <div class="notes-section">
            <h3>📝 您的备注</h3>
            <p>{user_notes}</p>
        </div>
        """
    
    # 生成HTML报告，使用format方法而不是f-string
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>拖延评估报告（{0}）</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                color: #333;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            h1 {{
                text-align: center;
                color: #4a6fa5;
                margin-bottom: 30px;
            }}
            
            h2 {{
                color: #4a6fa5;
                margin-top: 30px;
                margin-bottom: 20px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
            }}
            
            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            
            .info-table th, .info-table td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            
            .info-table th {{
                background-color: #f0f8ff;
                font-weight: bold;
                color: #4a6fa5;
            }}
            
            .info-table tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            
            .comparison-chart {{
                margin: 30px 0;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }}
            
            .chart-container {{
                display: flex;
                justify-content: space-around;
                align-items: end;
                height: 300px;
                margin-top: 20px;
            }}
            
            .chart-bar {{
                width: 100px;
                background-color: #4a6fa5;
                border-radius: 4px 4px 0 0;
                display: flex;
                justify-content: center;
                align-items: end;
                padding-bottom: 10px;
                color: white;
                font-weight: bold;
                position: relative;
                transition: all 0.3s ease;
            }}
            
            .chart-bar:hover {{
                transform: scaleY(1.05);
            }}
            
            .chart-bar.model-bar {{
                background-color: #5cb85c;
            }}
            
            .chart-label {{
                position: absolute;
                bottom: -30px;
                font-size: 14px;
                color: #666;
                white-space: nowrap;
            }}
            
            .suggestion-section {{
                margin: 30px 0;
                padding: 20px;
                background-color: #e7f3fe;
                border-radius: 8px;
                border-left: 4px solid #2196f3;
            }}
            
            .suggestion-section h3 {{
                color: #1976d2;
                margin-bottom: 15px;
            }}
            
            .suggestion-text {{
                font-size: 16px;
                line-height: 1.8;
            }}
            
            .notes-section {{
                margin: 30px 0;
                padding: 20px;
                background-color: #fff3cd;
                border-radius: 8px;
                border-left: 4px solid #ffc107;
            }}
            
            .notes-section h3 {{
                color: #856404;
                margin-bottom: 15px;
            }}
            
            .footer {{
                margin-top: 40px;
                text-align: center;
                color: #666;
                font-size: 14px;
                border-top: 1px solid #ddd;
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>拖延评估报告（{0}）</h1>
            
            <h2>核心信息</h2>
            <table class="info-table">
                <tr>
                    <th>评估维度</th>
                    <th>得分</th>
                </tr>
                <tr>
                    <td>任务厌恶程度</td>
                    <td>{1}</td>
                </tr>
                <tr>
                    <td>结果价值感</td>
                    <td>{2}</td>
                </tr>
                <tr>
                    <td>自我控制能力</td>
                    <td>{3}</td>
                </tr>
                <tr>
                    <th colspan="2">评估结果</th>
                </tr>
                <tr>
                    <td>核心函数计算式</td>
                    <td>{1}×{4}+(100-{2})×{5}+(100-{3})×{6}={7:.2f}</td>
                </tr>
                <tr>
                    <td>权重设置</td>
                    <td>w1={4}, w2={5}, w3={6}</td>
                </tr>
                <tr>
                    <td>核心函数结果</td>
                    <td>{8}（score={7:.2f}）</td>
                </tr>
                <tr>
                    <td>模型预测结果</td>
                    <td>{9}</td>
                </tr>
                <tr>
                    <td>结果对比</td>
                    <td>{10}</td>
                </tr>
            </table>
            
            <h2>双结果对比</h2>
            <div class="comparison-chart">
                <div class="chart-container">
                    <div class="chart-bar" style="height: {7}%;">
                        {7:.1f}%
                        <div class="chart-label">核心函数结果</div>
                    </div>
                    <div class="chart-bar model-bar" style="height: {11}%;">
                        {11}%
                        <div class="chart-label">模型预测结果</div>
                    </div>
                </div>
            </div>
            
            <h2>个性化建议</h2>
            <div class="suggestion-section">
                <h3>💡 针对您的建议</h3>
                <div class="suggestion-text">{12}</div>
            </div>
            
            {13}
            
            <div class="footer">
                <p>报告生成时间：{0}</p>
                <p>匿名ID：{14}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content.format(
        formatted_time,
        task_aversion,
        result_value,
        self_control,
        w1,
        w2,
        w3,
        score,
        risk_level,
        model_prediction,
        comparison,
        model_score,
        suggestion,
        notes_html,
        anonymous_id
    )

# 保存核心函数结果
def save_core_function_result(user_id, anonymous_id, task_aversion, result_value, self_control, w1, w2, w3, risk_level, score, model_prediction, comparison, suggestion, user_notes=None, report_path=None):
    """保存核心函数结果，包含完整评估信息"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO core_function_results (
        user_id, anonymous_id, task_aversion, result_value, self_control, 
        w1, w2, w3, score, risk_level, model_prediction, comparison, suggestion, user_notes, report_path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, anonymous_id, task_aversion, result_value, self_control, 
          w1, w2, w3, score, risk_level, model_prediction, comparison, suggestion, user_notes, report_path))
    conn.commit()
    conn.close()

# 保存模型预测结果
def save_model_prediction(user_id, anonymous_id, task_aversion, result_value, self_control, w1, w2, w3, predicted_level):
    """保存模型预测结果"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查model_predictions表结构
        cursor.execute("PRAGMA table_info(model_predictions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 简化SQL语句，只插入必填字段
        cursor.execute('''
        INSERT INTO model_predictions (
            task_aversion, result_value, self_control, 
            w1, w2, w3, predicted_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (task_aversion, result_value, self_control, 
              w1, w2, w3, predicted_level))
        conn.commit()
    except Exception as e:
        print(f"保存模型预测结果失败: {e}")
        # 记录详细错误信息
        print(f"参数: user_id={user_id}, anonymous_id={anonymous_id}, task_aversion={task_aversion}, result_value={result_value}, self_control={self_control}, w1={w1}, w2={w2}, w3={w3}, predicted_level={predicted_level}")
    finally:
        conn.close()

# 训练用户模型
def train_user_model(user_id):
    """训练用户模型"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取用户的核心函数结果
    cursor.execute('''
    SELECT task_aversion, result_value, self_control, risk_level 
    FROM core_function_results 
    WHERE user_id = ? OR anonymous_id = ?
    ''', (user_id, user_id))
    results = cursor.fetchall()
    
    # 如果核心函数结果不足，尝试从旧表risk_records获取数据
    if len(results) < 5:
        cursor.execute('''
        SELECT task_aversion, result_value, self_control 
        FROM risk_records 
        WHERE user_id = ? OR user_id IS NULL
        ''', (user_id,))
        old_results = cursor.fetchall()
        
        # 为旧数据生成风险等级
        level_mapping = {'低': 0, '中': 1, '高': 2}
        
        for old_result in old_results:
            task_aversion, result_value, self_control = old_result
            if task_aversion is None:
                continue
                
            # 使用默认权重计算风险等级
            time_decision_data = {
                "任务厌恶": task_aversion,
                "结果价值": result_value,
                "自我控制": self_control
            }
            risk_level, score = get_risk_level(time_decision_data, 0.4, 0.3, 0.3)
            results.append((task_aversion, result_value, self_control, risk_level))
    
    conn.close()
    
    if len(results) < 5:
        # 数据不足，返回None
        return None
    
    # 准备训练数据
    X = []
    y = []
    
    level_mapping = {'低': 0, '中': 1, '高': 2}
    
    for result in results:
        task_aversion, result_value, self_control, risk_level = result
        X.append([task_aversion, result_value, self_control])
        y.append(level_mapping[risk_level])
    
    # 训练模型
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression()
    model.fit(X_scaled, y)
    
    # 保存模型和缩放器
    user_model = {
        'model': model,
        'scaler': scaler,
        'level_mapping': level_mapping
    }
    
    return user_model

# 预测用户模型结果
def predict_with_user_model(user_id, task_aversion, result_value, self_control):
    """使用用户模型进行预测"""
    # 检查是否有缓存的模型
    if user_id not in user_models:
        # 训练模型
        user_model = train_user_model(user_id)
        if not user_model:
            # 如果个性化模型训练失败，使用全局预训练模型
            global model
            if model:
                try:
                    # 使用全局模型进行预测
                    # 注意：全局模型可能没有scaler，直接使用原始数据
                    X = np.array([[task_aversion, result_value, self_control]])
                    prediction = model.predict(X)[0]
                    # 假设全局模型的等级映射与系统一致
                    level_mapping = {'低': 0, '中': 1, '高': 2}
                    reverse_mapping = {v: k for k, v in level_mapping.items()}
                    return reverse_mapping[prediction]
                except Exception as e:
                    print(f"使用全局模型预测失败: {e}")
                    return None
            return None
        user_models[user_id] = user_model
    
    user_model = user_models[user_id]
    model = user_model['model']
    scaler = user_model['scaler']
    level_mapping = user_model['level_mapping']
    
    # 预测
    X = np.array([[task_aversion, result_value, self_control]])
    X_scaled = scaler.transform(X)
    prediction = model.predict(X_scaled)[0]
    
    # 反向映射等级
    reverse_mapping = {v: k for k, v in level_mapping.items()}
    return reverse_mapping[prediction]

# 密码加密
def hash_password(password):
    """
    对密码进行加密
    
    Args:
        password: 原始密码
        
    Returns:
        bytes: 加密后的密码哈希值
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

# 验证密码
def verify_password(plain_password, hashed_password):
    """
    验证密码是否匹配
    
    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码哈希值
        
    Returns:
        bool: 密码是否匹配
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# 验证用户
def verify_user(identifier, password):
    """
    验证用户登录
    
    Args:
        identifier: 手机号/邮箱
        password: 密码
        
    Returns:
        dict: 用户信息，如果验证失败返回None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查是手机号还是邮箱
    if '@' in identifier:
        # 邮箱登录
        cursor.execute('SELECT user_id, username, password_hash FROM users WHERE email = ?', (identifier,))
    else:
        # 手机号登录
        cursor.execute('SELECT user_id, username, password_hash FROM users WHERE phone = ?', (identifier,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2]):
        return {
            'user_id': user[0],
            'username': user[1]
        }
    return None

# 加载模型
def load_model():
    """
    加载训练好的模型
    
    Returns:
        model: 加载的模型，失败则返回None
    """
    global model
    try:
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            print("模型加载成功")
        else:
            print("模型文件不存在，将使用时间决策理论")
    except Exception as e:
        print(f"模型加载失败: {e}，将使用时间决策理论")
        model = None

def init_db():
    """初始化数据库，创建所有必要的表，使用ALTER TABLE避免删除历史数据"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建users表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        avatar TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建risk_records表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS risk_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_aversion INTEGER,
        result_value INTEGER NOT NULL,
        self_control INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        source TEXT NOT NULL,
        actual_delay INTEGER,
        delay_probability REAL
    )
    ''')
    
    # 为risk_records表添加user_id字段（如果不存在）
    cursor.execute("PRAGMA table_info(risk_records)")
    risk_fields = [field[1] for field in cursor.fetchall()]
    if 'user_id' not in risk_fields:
        cursor.execute("ALTER TABLE risk_records ADD COLUMN user_id TEXT")
    
    # 创建anonymous_users表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anonymous_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anonymous_id TEXT UNIQUE NOT NULL,
        w1 REAL DEFAULT 0.4,
        w2 REAL DEFAULT 0.3,
        w3 REAL DEFAULT 0.3,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建core_function_results表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_function_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_aversion INTEGER NOT NULL,
        result_value INTEGER NOT NULL,
        self_control INTEGER NOT NULL,
        w1 REAL NOT NULL,
        w2 REAL NOT NULL,
        w3 REAL NOT NULL,
        score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        comparison TEXT NOT NULL,
        suggestion TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        user_notes TEXT,
        report_path TEXT
    )
    ''')
    
    # 为core_function_results表添加缺失字段（如果不存在）
    cursor.execute("PRAGMA table_info(core_function_results)")
    core_fields = [field[1] for field in cursor.fetchall()]
    if 'user_id' not in core_fields:
        cursor.execute("ALTER TABLE core_function_results ADD COLUMN user_id TEXT")
    if 'anonymous_id' not in core_fields:
        cursor.execute("ALTER TABLE core_function_results ADD COLUMN anonymous_id TEXT")
    if 'model_prediction' not in core_fields:
        cursor.execute("ALTER TABLE core_function_results ADD COLUMN model_prediction TEXT")
    
    # 创建model_predictions表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS model_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_aversion INTEGER NOT NULL,
        result_value INTEGER NOT NULL,
        self_control INTEGER NOT NULL,
        w1 REAL NOT NULL,
        w2 REAL NOT NULL,
        w3 REAL NOT NULL,
        predicted_level TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 为model_predictions表添加缺失字段（如果不存在）
    cursor.execute("PRAGMA table_info(model_predictions)")
    model_fields = [field[1] for field in cursor.fetchall()]
    if 'user_id' not in model_fields:
        cursor.execute("ALTER TABLE model_predictions ADD COLUMN user_id TEXT")
    if 'anonymous_id' not in model_fields:
        cursor.execute("ALTER TABLE model_predictions ADD COLUMN anonymous_id TEXT")
    
    # 创建user_feedback表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER,
        feedback INTEGER,
        comments TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 为user_feedback表添加user_id字段（如果不存在）
    cursor.execute("PRAGMA table_info(user_feedback)")
    feedback_fields = [field[1] for field in cursor.fetchall()]
    if 'user_id' not in feedback_fields:
        cursor.execute("ALTER TABLE user_feedback ADD COLUMN user_id TEXT")
    
    # 创建user_behavior表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_behavior (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type TEXT,
        time_pressure INTEGER,
        environment INTEGER,
        age_group TEXT,
        occupation TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 为user_behavior表添加user_id字段（如果不存在）
    cursor.execute("PRAGMA table_info(user_behavior)")
    behavior_fields = [field[1] for field in cursor.fetchall()]
    if 'user_id' not in behavior_fields:
        cursor.execute("ALTER TABLE user_behavior ADD COLUMN user_id TEXT")
    
    # 创建usage_stats表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usage_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_duration INTEGER,
        actions_count INTEGER,
        feature_used TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 为usage_stats表添加user_id字段（如果不存在）
    cursor.execute("PRAGMA table_info(usage_stats)")
    usage_fields = [field[1] for field in cursor.fetchall()]
    if 'user_id' not in usage_fields:
        cursor.execute("ALTER TABLE usage_stats ADD COLUMN user_id TEXT")
    
    # 创建weight_adjustments表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weight_adjustments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        w1 REAL NOT NULL,
        w2 REAL NOT NULL,
        w3 REAL NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 为weight_adjustments表添加user_id字段（如果不存在）
    cursor.execute("PRAGMA table_info(weight_adjustments)")
    weight_fields = [field[1] for field in cursor.fetchall()]
    if 'user_id' not in weight_fields:
        cursor.execute("ALTER TABLE weight_adjustments ADD COLUMN user_id TEXT")
    
    conn.commit()
    conn.close()

# 数据脱敏处理

def desensitize_data(data, fields_to_desensitize=None):
    """
    对数据进行脱敏处理
    
    Args:
        data: 要脱敏的数据（字典或字典列表）
        fields_to_desensitize: 需要脱敏的字段列表
        
    Returns:
        脱敏后的数据
    """
    if fields_to_desensitize is None:
        fields_to_desensitize = ['username', 'occupation', 'age_group']
    
    def desensitize_value(value, field):
        """脱敏单个值"""
        if value is None:
            return None
        
        if field == 'username':
            # 用户名脱敏：只保留前2个字符
            if len(value) <= 2:
                return value
            return value[:2] + '*' * (len(value) - 2)
        elif field == 'occupation':
            # 职业脱敏：使用通用职业类别
            sensitive_occupations = ['医生', '律师', '教师', '工程师', '程序员']
            for occ in sensitive_occupations:
                if occ in value:
                    return occ + '（脱敏）'
            return value
        elif field == 'age_group':
            # 年龄段脱敏：只保留范围，不显示具体年龄
            return value + '（脱敏）'
        return value
    
    if isinstance(data, list):
        # 处理列表数据
        return [
            {
                key: desensitize_value(value, key) if key in fields_to_desensitize else value
                for key, value in item.items()
            }
            for item in data
        ]
    elif isinstance(data, dict):
        # 处理单个字典
        return {
            key: desensitize_value(value, key) if key in fields_to_desensitize else value
            for key, value in data.items()
        }
    return data

# 数据迁移功能
def migrate_anonymous_data_to_user(anonymous_id, user_id):
    """
    将匿名用户数据迁移到注册用户
    
    Args:
        anonymous_id: 匿名ID
        user_id: 注册用户ID
    
    Returns:
        bool: 迁移是否成功
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 更新core_function_results表
        cursor.execute('''
        UPDATE core_function_results 
        SET user_id = ? 
        WHERE anonymous_id = ? AND user_id IS NULL
        ''', (user_id, anonymous_id))
        
        # 更新model_predictions表
        cursor.execute('''
        UPDATE model_predictions 
        SET user_id = ? 
        WHERE anonymous_id = ? AND user_id IS NULL
        ''', (user_id, anonymous_id))
        
        # 更新risk_records表（如果有匹配的记录）
        # 由于risk_records表没有anonymous_id字段，这里暂时不处理
        
        # 更新user_feedback表
        cursor.execute('''
        UPDATE user_feedback 
        SET user_id = ? 
        WHERE user_id IS NULL
        ''', (user_id,))
        
        # 更新user_behavior表
        cursor.execute('''
        UPDATE user_behavior 
        SET user_id = ? 
        WHERE user_id IS NULL
        ''', (user_id,))
        
        # 更新usage_stats表
        cursor.execute('''
        UPDATE usage_stats 
        SET user_id = ? 
        WHERE user_id IS NULL
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"数据迁移失败: {e}")
        return False

# 数据迁移接口
@app.route('/migrate-data', methods=['POST'])
def migrate_data():
    """将匿名用户数据迁移到注册用户"""
    # 检查用户是否登录
    if 'user_id' not in session:
        return jsonify({"error": "未登录"}), 401
    
    data = request.json
    if not data or 'anonymous_id' not in data:
        return jsonify({"error": "缺少匿名ID"}), 400
    
    anonymous_id = data['anonymous_id']
    user_id = session['user_id']
    
    try:
        success = migrate_anonymous_data_to_user(anonymous_id, user_id)
        if success:
            return jsonify({"status": "success", "message": "数据迁移成功"}), 200
        else:
            return jsonify({"error": "数据迁移失败"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    # 校验输入
    # 支持两种输入格式：旧格式（中文键）和新格式（英文键）
    task_aversion = None
    result_value = None
    self_control = None
    user_notes = data.get('user_notes')
    
    if "任务厌恶" in data and "结果价值" in data and "自我控制" in data:
        # 旧格式
        task_aversion = data["任务厌恶"]
        result_value = data["结果价值"]
        self_control = data["自我控制"]
    elif "task_aversion" in data and "result_value" in data and "self_control" in data:
        # 新格式
        task_aversion = data["task_aversion"]
        result_value = data["result_value"]
        self_control = data["self_control"]
    else:
        return jsonify({"error": "缺少必要字段"}), 400
    
    # 获取当前用户ID或生成匿名ID
    current_user_id = get_current_user_id()
    
    # 确定user_id和anonymous_id
    user_id = session.get('user_id') if 'user_id' in session else None
    anonymous_id = current_user_id if not user_id else None
    
    # 获取用户权重
    weights = get_user_weights(current_user_id)
    w1 = weights['w1']
    w2 = weights['w2']
    w3 = weights['w3']
    
    # 1. 使用核心函数计算结果
    time_decision_data = {
        "任务厌恶": task_aversion,
        "结果价值": result_value,
        "自我控制": self_control
    }
    
    risk_level, score = get_risk_level(time_decision_data, w1, w2, w3)
    
    # 2. 使用用户模型进行预测
    model_prediction = predict_with_user_model(current_user_id, task_aversion, result_value, self_control)
    
    # 保存模型预测结果
    if model_prediction:
        save_model_prediction(user_id, anonymous_id, task_aversion, result_value, self_control, 
                            w1, w2, w3, model_prediction)
    
    # 3. 对比结果
    comparison = "一致" if model_prediction == risk_level else "不一致"
    
    # 获取建议
    tip = get_suggestions(risk_level)
    
    # 生成测算时间
    timestamp = datetime.datetime.now()
    formatted_time = timestamp.isoformat()
    # 生成报告文件名（YYYYMMDDHHMMSS格式）
    report_time = timestamp.strftime("%Y%m%d%H%M%S")
    
    # 按用户ID分文件夹存储报告
    if user_id:
        # 登录用户，创建用户专属报告文件夹
        user_report_dir = os.path.join(reports_dir, user_id)
        if not os.path.exists(user_report_dir):
            os.makedirs(user_report_dir)
        report_filename = f"report_{user_id}_{report_time}.html"
        report_path = os.path.join(user_report_dir, report_filename)
    else:
        # 匿名用户，使用原报告目录
        report_filename = f"report_{anonymous_id}_{report_time}.html"
        report_path = os.path.join(reports_dir, report_filename)
    
    # 生成HTML报告
    report_content = generate_report(
        current_user_id,
        formatted_time,
        task_aversion,
        result_value,
        self_control,
        w1,
        w2,
        w3,
        score,
        risk_level,
        model_prediction if model_prediction else "数据不足，无法预测",
        comparison,
        tip,
        user_notes
    )
    
    # 保存报告文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # 保存核心函数结果，包含完整评估信息和报告路径
    save_core_function_result(user_id, anonymous_id, task_aversion, result_value, self_control, 
                            w1, w2, w3, risk_level, score, model_prediction, comparison, tip, user_notes, report_path)
    
    # 构建响应
    response = {
        "user_id": user_id,
        "anonymous_id": anonymous_id,
        "core_function_result": {
            "风险等级": risk_level,
            "分数": round(score, 2),
            "权重": {
                "w1": w1,
                "w2": w2,
                "w3": w3
            }
        },
        "model_prediction": model_prediction if model_prediction else "数据不足，无法预测",
        "comparison": comparison,
        "建议": tip,
        "timestamp": formatted_time,
        "report_path": report_path
    }
    
    # 设置cookie
    resp = jsonify(response)
    if anonymous_id:
        resp.set_cookie('anonymous_id', anonymous_id, max_age=365*24*60*60)  # 1年有效期
    
    return resp

@app.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.json
    # 校验输入
    required_fields = ['password', 'username']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "缺少必要字段"}), 400
    
    # 检查是否提供了手机号或邮箱
    if 'phone' not in data and 'email' not in data:
        return jsonify({"error": "请提供手机号或邮箱"}), 400
    
    phone = data.get('phone')
    email = data.get('email')
    username = data['username']
    password = data['password']
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查手机号是否已存在
        if phone:
            cursor.execute('SELECT user_id FROM users WHERE phone = ?', (phone,))
            if cursor.fetchone():
                conn.close()
                return jsonify({"error": "手机号已被注册"}), 400
        
        # 检查邮箱是否已存在
        if email:
            cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return jsonify({"error": "邮箱已被注册"}), 400
        
        # 生成唯一用户ID
        user_id = f'user_{uuid.uuid4().hex[:8]}'
        
        # 插入新用户
        cursor.execute('''
        INSERT INTO users (user_id, phone, email, username, password_hash)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, phone, email, username, hash_password(password)))
        
        conn.commit()
        conn.close()
        
        # 设置session
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({"status": "success", "user_id": user_id, "username": username}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.json
    # 校验输入
    if not data or 'identifier' not in data or 'password' not in data:
        return jsonify({"error": "缺少登录标识或密码"}), 400
    
    identifier = data['identifier']
    password = data['password']
    
    # 验证用户
    user_info = verify_user(identifier, password)
    if not user_info:
        return jsonify({"error": "手机号/邮箱或密码错误"}), 401
    
    # 设置session
    session['user_id'] = user_info['user_id']
    session['username'] = user_info['username']
    
    return jsonify({"status": "success", "user_id": user_info['user_id'], "username": user_info['username']}), 200

@app.route('/logout', methods=['POST'])
def logout():
    """用户登出接口"""
    # 清除session
    session.clear()
    return jsonify({"status": "success"}), 200

@app.route('/user', methods=['GET'])
def get_user():
    """获取当前用户信息"""
    if 'user_id' in session:
        return jsonify({
            "status": "success",
            "user_id": session['user_id'],
            "username": session['username']
        }), 200
    else:
        return jsonify({"status": "error", "message": "未登录"}), 401

@app.route('/reset-password', methods=['POST'])
def reset_password_request():
    """请求重置密码"""
    data = request.json
    # 校验输入
    if not data or 'identifier' not in data:
        return jsonify({"error": "缺少手机号或邮箱"}), 400
    
    identifier = data['identifier']
    
    # TODO: 实现发送验证码/重置链接的功能
    # 这里简化处理，实际应该发送短信或邮箱验证码
    
    return jsonify({"status": "success", "message": "验证码已发送"}), 200

@app.route('/reset-password/confirm', methods=['POST'])
def reset_password_confirm():
    """确认重置密码"""
    data = request.json
    # 校验输入
    if not data or 'identifier' not in data or 'token' not in data or 'new_password' not in data:
        return jsonify({"error": "缺少必要字段"}), 400
    
    identifier = data['identifier']
    token = data['token']
    new_password = data['new_password']
    
    # TODO: 实现验证token并重置密码的功能
    # 这里简化处理，实际应该验证token的有效性
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 更新密码
        if '@' in identifier:
            # 邮箱
            cursor.execute('UPDATE users SET password_hash = ? WHERE email = ?', (hash_password(new_password), identifier))
        else:
            # 手机号
            cursor.execute('UPDATE users SET password_hash = ? WHERE phone = ?', (hash_password(new_password), identifier))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "密码重置成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report', methods=['POST'])
def report():
    """接收前端上报的数据并存储到数据库"""
    data = request.json
    # 校验输入
    required_keys = ["result_value", "self_control", "timestamp", "source"]
    if not all(k in data for k in required_keys):
        return jsonify({"error": "缺少必要字段"}), 400
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 插入数据，包含task_aversion和user_id字段
        task_aversion = data.get("task_aversion")  # 使用get方法，允许task_aversion为None
        actual_delay = data.get("actual_delay")  # 使用get方法，允许actual_delay为None
        delay_probability = data.get("delay_probability")  # 使用get方法，允许delay_probability为None
        cursor.execute('''
        INSERT INTO risk_records (task_aversion, result_value, self_control, timestamp, source, actual_delay, user_id, delay_probability)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_aversion, data["result_value"], data["self_control"], 
              data["timestamp"], data["source"], actual_delay, user_id, delay_probability))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """获取用户历史评估数据"""
    # 获取当前用户ID或生成匿名ID
    current_user_id = get_current_user_id()
    
    # 确定user_id和anonymous_id
    user_id = session.get('user_id') if 'user_id' in session else None
    anonymous_id = current_user_id if not user_id else None
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if user_id:
            # 登录用户，查询该用户的所有记录
            cursor.execute('''
            SELECT id, user_id, anonymous_id, task_aversion, result_value, self_control, 
                   w1, w2, w3, score, risk_level, model_prediction, comparison, suggestion, timestamp, user_notes, report_path
            FROM core_function_results 
            WHERE user_id = ?
            ORDER BY timestamp DESC
            ''', (user_id,))
        else:
            # 匿名用户，查询该匿名ID的记录
            cursor.execute('''
            SELECT id, user_id, anonymous_id, task_aversion, result_value, self_control, 
                   w1, w2, w3, score, risk_level, model_prediction, comparison, suggestion, timestamp, user_notes, report_path
            FROM core_function_results 
            WHERE anonymous_id = ?
            ORDER BY timestamp DESC
            ''', (anonymous_id,))
        
        core_records = cursor.fetchall()
        
        # 合并所有记录
        all_records = list(core_records)
        
        # 按时间戳排序，最新的在前
        all_records.sort(key=lambda x: x[14] if len(x) > 14 else x[13], reverse=True)
        
        # 格式化结果
        history = []
        for record in all_records:
            # 确保score是浮点数
            score = float(record[9])
            
            history.append({
                "id": record[0],
                "user_id": record[1],
                "anonymous_id": record[2],
                "task_aversion": record[3],
                "result_value": record[4],
                "self_control": record[5],
                "w1": record[6],
                "w2": record[7],
                "w3": record[8],
                "score": score,
                "risk_level": record[10],
                "model_prediction": record[11],
                "comparison": record[12],
                "suggestion": record[13],
                "timestamp": record[14] if len(record) > 14 else record[13],
                "user_notes": record[15] if len(record) > 15 else None,
                "report_path": record[16] if len(record) > 16 else None
            })
        
        resp = jsonify({"status": "success", "history": history})
        if anonymous_id:
            resp.set_cookie('anonymous_id', anonymous_id, max_age=365*24*60*60)  # 设置cookie，有效期1年
        return resp, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analytics', methods=['GET'])
def get_analytics():
    """获取用户数据分析"""
    # 获取当前用户ID
    user_id = session.get('user_id')
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询用户的历史记录
        if user_id:
            # 用户已登录，查询该用户的记录
            cursor.execute('''
            SELECT task_aversion, result_value, self_control, actual_delay, delay_probability
            FROM risk_records
            WHERE user_id = ?
            ''', (user_id,))
        else:
            # 用户未登录，返回空数据
            return jsonify({"status": "success", "data": {
                "total_records": 0,
                "average_probability": 0,
                "delay_rate": 0,
                "average_task_aversion": 0,
                "average_result_value": 0,
                "average_self_control": 0,
                "trend": []
            }}), 200
        
        records = cursor.fetchall()
        conn.close()
        
        if not records:
            return jsonify({"status": "success", "data": {
                "total_records": 0,
                "average_probability": 0,
                "delay_rate": 0,
                "average_task_aversion": 0,
                "average_result_value": 0,
                "average_self_control": 0,
                "trend": []
            }}), 200
        
        # 计算统计数据
        total_records = len(records)
        delay_count = sum(1 for record in records if record[3] == 1)
        delay_rate = delay_count / total_records if total_records > 0 else 0
        
        # 计算平均值
        task_aversion_sum = sum(record[0] or 50 for record in records)
        result_value_sum = sum(record[1] or 50 for record in records)
        self_control_sum = sum(record[2] or 50 for record in records)
        
        average_task_aversion = task_aversion_sum / total_records
        average_result_value = result_value_sum / total_records
        average_self_control = self_control_sum / total_records
        
        # 计算平均拖延概率
        total_probability = 0
        for record in records:
            task_aversion = record[0] or 50
            result_value = record[1] or 50
            self_control = record[2] or 50
            score = (task_aversion * 0.4 + (100 - result_value) * 0.3 + (100 - self_control) * 0.3)
            probability = min(1.0, max(0.0, score / 100))
            total_probability += probability
        
        average_probability = total_probability / total_records if total_records > 0 else 0
        
        # 简单的趋势分析（最近10条记录）
        trend = []
        recent_records = records[-10:]
        for i, record in enumerate(recent_records):
            # 优先使用保存的预测结果，没有则重新计算
            delay_probability = record[4] if len(record) > 4 else None
            
            if delay_probability is None:
                # 如果没有保存的预测结果，则重新计算
                task_aversion = record[0] or 50
                result_value = record[1] or 50
                self_control = record[2] or 50
                score = (task_aversion * 0.4 + (100 - result_value) * 0.3 + (100 - self_control) * 0.3)
                delay_probability = min(1.0, max(0.0, score / 100))
            
            trend.append({
                "index": i + 1,
                "probability": delay_probability
            })
        
        return jsonify({"status": "success", "data": {
            "total_records": total_records,
            "average_probability": average_probability,
            "delay_rate": delay_rate,
            "average_task_aversion": average_task_aversion,
            "average_result_value": average_result_value,
            "average_self_control": average_self_control,
            "trend": trend
        }}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """提交用户反馈"""
    data = request.json
    
    # 校验输入
    if not data or 'feedback' not in data:
        return jsonify({"error": "缺少必要字段"}), 400
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 插入反馈数据
        cursor.execute('''
        INSERT INTO user_feedback (user_id, feedback, comments, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (user_id, data['feedback'], data.get('comments'), datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# User Behavior CRUD Operations

@app.route('/user-behavior', methods=['POST'])
def create_user_behavior():
    """创建用户行为记录"""
    data = request.json
    
    # 校验输入
    required_fields = ['task_type', 'time_pressure', 'environment']
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"缺少必要字段: {', '.join(required_fields)}"}), 400
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 插入用户行为数据
        cursor.execute('''
        INSERT INTO user_behavior (user_id, task_type, time_pressure, environment, age_group, occupation)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, data['task_type'], data['time_pressure'], data['environment'],
              data.get('age_group'), data.get('occupation')))
        
        conn.commit()
        behavior_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"status": "success", "id": behavior_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user-behavior', methods=['GET'])
def get_user_behavior_list():
    """获取用户行为记录列表"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 查询用户行为记录
        cursor.execute('''
        SELECT id, user_id, task_type, time_pressure, environment, age_group, occupation, created_at
        FROM user_behavior
        WHERE user_id = ? OR user_id IS NULL
        ORDER BY created_at DESC
        ''', (user_id,))
        
        records = cursor.fetchall()
        conn.close()
        
        # 格式化结果
        behavior_list = []
        for record in records:
            behavior_list.append({
                "id": record[0],
                "user_id": record[1],
                "task_type": record[2],
                "time_pressure": record[3],
                "environment": record[4],
                "age_group": record[5],
                "occupation": record[6],
                "created_at": record[7]
            })
        
        # 数据脱敏
        desensitized_list = desensitize_data(behavior_list)
        
        return jsonify({"status": "success", "data": desensitized_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user-behavior/<int:behavior_id>', methods=['GET'])
def get_user_behavior(behavior_id):
    """获取单个用户行为记录"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询用户行为记录
        cursor.execute('''
        SELECT id, user_id, task_type, time_pressure, environment, age_group, occupation, created_at
        FROM user_behavior
        WHERE id = ?
        ''', (behavior_id,))
        
        record = cursor.fetchone()
        conn.close()
        
        if not record:
            return jsonify({"error": "记录不存在"}), 404
        
        # 格式化结果
        behavior_data = {
            "id": record[0],
            "user_id": record[1],
            "task_type": record[2],
            "time_pressure": record[3],
            "environment": record[4],
            "age_group": record[5],
            "occupation": record[6],
            "created_at": record[7]
        }
        
        # 数据脱敏
        desensitized_data = desensitize_data(behavior_data)
        
        return jsonify({"status": "success", "data": desensitized_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user-behavior/<int:behavior_id>', methods=['PUT'])
def update_user_behavior(behavior_id):
    """更新用户行为记录"""
    data = request.json
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 检查记录是否存在
        cursor.execute('''
        SELECT user_id FROM user_behavior WHERE id = ?
        ''', (behavior_id,))
        record = cursor.fetchone()
        
        if not record:
            conn.close()
            return jsonify({"error": "记录不存在"}), 404
        
        # 只允许更新自己的记录
        if record[0] is not None and record[0] != user_id:
            conn.close()
            return jsonify({"error": "无权限修改该记录"}), 403
        
        # 更新记录
        cursor.execute('''
        UPDATE user_behavior
        SET task_type = ?, time_pressure = ?, environment = ?, age_group = ?, occupation = ?
        WHERE id = ?
        ''', (data.get('task_type'), data.get('time_pressure'), data.get('environment'),
              data.get('age_group'), data.get('occupation'), behavior_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user-behavior/<int:behavior_id>', methods=['DELETE'])
def delete_user_behavior(behavior_id):
    """删除用户行为记录"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 检查记录是否存在
        cursor.execute('''
        SELECT user_id FROM user_behavior WHERE id = ?
        ''', (behavior_id,))
        record = cursor.fetchone()
        
        if not record:
            conn.close()
            return jsonify({"error": "记录不存在"}), 404
        
        # 只允许删除自己的记录
        if record[0] is not None and record[0] != user_id:
            conn.close()
            return jsonify({"error": "无权限删除该记录"}), 403
        
        # 删除记录
        cursor.execute('''
        DELETE FROM user_behavior WHERE id = ?
        ''', (behavior_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Usage Stats CRUD Operations

@app.route('/usage-stats', methods=['POST'])
def create_usage_stats():
    """创建使用统计数据"""
    data = request.json
    
    # 校验输入
    required_fields = ['session_duration', 'actions_count', 'feature_used']
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"缺少必要字段: {', '.join(required_fields)}"}), 400
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 插入使用统计数据
        cursor.execute('''
        INSERT INTO usage_stats (user_id, session_duration, actions_count, feature_used)
        VALUES (?, ?, ?, ?)
        ''', (user_id, data['session_duration'], data['actions_count'], data['feature_used']))
        
        conn.commit()
        stats_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"status": "success", "id": stats_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usage-stats', methods=['GET'])
def get_usage_stats_list():
    """获取使用统计数据列表"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 查询使用统计数据
        cursor.execute('''
        SELECT id, user_id, session_duration, actions_count, feature_used, timestamp
        FROM usage_stats
        WHERE user_id = ? OR user_id IS NULL
        ORDER BY timestamp DESC
        ''', (user_id,))
        
        records = cursor.fetchall()
        conn.close()
        
        # 格式化结果
        stats_list = []
        for record in records:
            stats_list.append({
                "id": record[0],
                "user_id": record[1],
                "session_duration": record[2],
                "actions_count": record[3],
                "feature_used": record[4],
                "timestamp": record[5]
            })
        
        return jsonify({"status": "success", "data": stats_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usage-stats/<int:stats_id>', methods=['GET'])
def get_usage_stats(stats_id):
    """获取单个使用统计数据"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询使用统计数据
        cursor.execute('''
        SELECT id, user_id, session_duration, actions_count, feature_used, timestamp
        FROM usage_stats
        WHERE id = ?
        ''', (stats_id,))
        
        record = cursor.fetchone()
        conn.close()
        
        if not record:
            return jsonify({"error": "记录不存在"}), 404
        
        # 格式化结果
        stats_data = {
            "id": record[0],
            "user_id": record[1],
            "session_duration": record[2],
            "actions_count": record[3],
            "feature_used": record[4],
            "timestamp": record[5]
        }
        
        return jsonify({"status": "success", "data": stats_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usage-stats/<int:stats_id>', methods=['PUT'])
def update_usage_stats(stats_id):
    """更新使用统计数据"""
    data = request.json
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 检查记录是否存在
        cursor.execute('''
        SELECT user_id FROM usage_stats WHERE id = ?
        ''', (stats_id,))
        record = cursor.fetchone()
        
        if not record:
            conn.close()
            return jsonify({"error": "记录不存在"}), 404
        
        # 只允许更新自己的记录
        if record[0] is not None and record[0] != user_id:
            conn.close()
            return jsonify({"error": "无权限修改该记录"}), 403
        
        # 更新记录
        cursor.execute('''
        UPDATE usage_stats
        SET session_duration = ?, actions_count = ?, feature_used = ?
        WHERE id = ?
        ''', (data.get('session_duration'), data.get('actions_count'), data.get('feature_used'), stats_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usage-stats/<int:stats_id>', methods=['DELETE'])
def delete_usage_stats(stats_id):
    """删除使用统计数据"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID（如果已登录）
        user_id = session.get('user_id')
        
        # 检查记录是否存在
        cursor.execute('''
        SELECT user_id FROM usage_stats WHERE id = ?
        ''', (stats_id,))
        record = cursor.fetchone()
        
        if not record:
            conn.close()
            return jsonify({"error": "记录不存在"}), 404
        
        # 只允许删除自己的记录
        if record[0] is not None and record[0] != user_id:
            conn.close()
            return jsonify({"error": "无权限删除该记录"}), 403
        
        # 删除记录
        cursor.execute('''
        DELETE FROM usage_stats WHERE id = ?
        ''', (stats_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取用户权重
@app.route('/user-weights', methods=['GET'])
def get_user_weights_route():
    """获取用户的自定义权重"""
    anonymous_id = get_or_create_anonymous_id()
    weights = get_user_weights(anonymous_id)
    
    resp = jsonify({"status": "success", "weights": weights})
    resp.set_cookie('anonymous_id', anonymous_id, max_age=365*24*60*60)
    return resp

# 更新用户权重
@app.route('/user-weights', methods=['POST'])
def update_user_weights_route():
    """更新用户的自定义权重"""
    data = request.json
    
    # 校验输入
    if not all(k in data for k in ['w1', 'w2', 'w3']):
        return jsonify({"error": "缺少必要字段"}), 400
    
    anonymous_id = get_or_create_anonymous_id()
    
    # 更新权重
    update_user_weights(anonymous_id, data['w1'], data['w2'], data['w3'])
    
    # 清除用户模型缓存
    if anonymous_id in user_models:
        del user_models[anonymous_id]
    
    resp = jsonify({"status": "success", "message": "权重更新成功"})
    resp.set_cookie('anonymous_id', anonymous_id, max_age=365*24*60*60)
    return resp

# 获取核心函数结果历史
@app.route('/core-results', methods=['GET'])
def get_core_results():
    """获取用户的核心函数结果历史"""
    anonymous_id = get_or_create_anonymous_id()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询用户的核心函数结果
    cursor.execute('''
    SELECT id, task_aversion, result_value, self_control, 
           w1, w2, w3, score, risk_level, timestamp, user_notes
    FROM core_function_results 
    WHERE anonymous_id = ?
    ORDER BY timestamp DESC
    ''', (anonymous_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    # 格式化结果
    formatted_results = []
    for result in results:
        formatted_results.append({
            "id": result[0],
            "task_aversion": result[1],
            "result_value": result[2],
            "self_control": result[3],
            "weights": {
                "w1": result[4],
                "w2": result[5],
                "w3": result[6]
            },
            "score": result[7],
            "risk_level": result[8],
            "timestamp": result[9],
            "user_notes": result[10]
        })
    
    resp = jsonify({"status": "success", "results": formatted_results})
    resp.set_cookie('anonymous_id', anonymous_id, max_age=365*24*60*60)
    return resp

# 获取模型预测结果历史
@app.route('/model-predictions', methods=['GET'])
def get_model_predictions():
    """获取用户的模型预测结果历史"""
    anonymous_id = get_or_create_anonymous_id()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询用户的模型预测结果
    cursor.execute('''
    SELECT id, task_aversion, result_value, self_control, 
           w1, w2, w3, predicted_level, timestamp
    FROM model_predictions 
    WHERE anonymous_id = ?
    ORDER BY timestamp DESC
    ''', (anonymous_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    # 格式化结果
    formatted_results = []
    for result in results:
        formatted_results.append({
            "id": result[0],
            "task_aversion": result[1],
            "result_value": result[2],
            "self_control": result[3],
            "weights": {
                "w1": result[4],
                "w2": result[5],
                "w3": result[6]
            },
            "predicted_level": result[7],
            "timestamp": result[8]
        })
    
    resp = jsonify({"status": "success", "results": formatted_results})
    resp.set_cookie('anonymous_id', anonymous_id, max_age=365*24*60*60)
    return resp

# 导出用户数据
@app.route('/export-user-data', methods=['GET'])
def export_user_data():
    """导出当前用户的所有数据"""
    anonymous_id = get_or_create_anonymous_id()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询核心函数结果
    cursor.execute('''
    SELECT id, task_aversion, result_value, self_control, 
           w1, w2, w3, score, risk_level, timestamp, user_notes
    FROM core_function_results 
    WHERE anonymous_id = ?
    ORDER BY timestamp
    ''', (anonymous_id,))
    core_results = cursor.fetchall()
    
    # 查询模型预测结果
    cursor.execute('''
    SELECT id, task_aversion, result_value, self_control, 
           w1, w2, w3, predicted_level, timestamp
    FROM model_predictions 
    WHERE anonymous_id = ?
    ORDER BY timestamp
    ''', (anonymous_id,))
    model_predictions = cursor.fetchall()
    
    conn.close()
    
    # 格式化结果
    export_data = {
        "anonymous_id": anonymous_id,
        "core_function_results": [],
        "model_predictions": []
    }
    
    for result in core_results:
        export_data["core_function_results"].append({
            "id": result[0],
            "task_aversion": result[1],
            "result_value": result[2],
            "self_control": result[3],
            "w1": result[4],
            "w2": result[5],
            "w3": result[6],
            "score": result[7],
            "risk_level": result[8],
            "timestamp": result[9],
            "user_notes": result[10]
        })
    
    for result in model_predictions:
        export_data["model_predictions"].append({
            "id": result[0],
            "task_aversion": result[1],
            "result_value": result[2],
            "self_control": result[3],
            "w1": result[4],
            "w2": result[5],
            "w3": result[6],
            "predicted_level": result[7],
            "timestamp": result[8]
        })
    
    resp = jsonify({"status": "success", "data": export_data})
    resp.set_cookie('anonymous_id', anonymous_id, max_age=365*24*60*60)
    return resp

# 导出所有用户数据（开发者使用）
@app.route('/export-all-data', methods=['GET'])
def export_all_data():
    """导出所有用户的数据（开发者使用）"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有核心函数结果
        cursor.execute('''
        SELECT anonymous_id, COUNT(*) as total_assessments,
               AVG(task_aversion) as avg_task_aversion,
               AVG(result_value) as avg_result_value,
               AVG(self_control) as avg_self_control,
               AVG(w1) as avg_w1,
               AVG(w2) as avg_w2,
               AVG(w3) as avg_w3
        FROM core_function_results
        GROUP BY anonymous_id
        ''')
        
        users_data = cursor.fetchall()
        
        # 格式化结果
        export_data = []
        for record in users_data:
            export_data.append({
                "anonymous_id": record[0],
                "total_assessments": record[1],
                "avg_task_aversion": record[2],
                "avg_result_value": record[3],
                "avg_self_control": record[4],
                "avg_w1": record[5],
                "avg_w2": record[6],
                "avg_w3": record[7]
            })
        
        conn.close()
        
        return jsonify({"status": "success", "data": export_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取用户模型状态
@app.route('/model-status', methods=['GET'])
def get_model_status():
    """获取用户模型的状态"""
    anonymous_id = get_or_create_anonymous_id()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询用户的核心函数结果数量
    cursor.execute('''
    SELECT COUNT(*) FROM core_function_results 
    WHERE anonymous_id = ?
    ''', (anonymous_id,))
    result_count = cursor.fetchone()[0]
    
    conn.close()
    
    # 检查是否有训练好的模型
    has_model = anonymous_id in user_models
    
    status = {
        "status": "success",
        "has_model": has_model,
        "data_count": result_count,
        "model_ready": result_count >= 5
    }
    
    resp = jsonify(status)
    resp.set_cookie('anonymous_id', anonymous_id, max_age=365*24*60*60)
    return resp

# 重新训练用户模型
@app.route('/retrain-model', methods=['POST'])
def retrain_model():
    """重新训练用户模型"""
    anonymous_id = get_or_create_anonymous_id()
    
    # 清除旧模型
    if anonymous_id in user_models:
        del user_models[anonymous_id]
    
    # 训练新模型
    user_model = train_user_model(anonymous_id)
    
    if user_model:
        user_models[anonymous_id] = user_model
        return jsonify({"status": "success", "message": "模型重新训练成功"})
    else:
        return jsonify({"status": "error", "message": "数据不足，无法训练模型"})

if __name__ == '__main__':
    import sys
    try:
        print("开始启动应用...")
        print("当前工作目录:", os.getcwd())
        print("Python路径:", sys.path)
        
        print("初始化数据库...")
        init_db()
        print("数据库初始化完成")
        
        print("加载模型...")
        load_model()
        print("模型加载完成")
        
        print("启动Flask服务器...")
        app.run(debug=True, port=5001, use_reloader=False)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
