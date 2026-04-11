#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
拖延探索笔记本 - 多人拖延自我探索平台
核心定位：让每个注册用户探索"自己的拖延本质"
"""

import os
import sqlite3
import json
import bcrypt
import jwt
import pickle
import csv
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, g, make_response
from flask_cors import CORS
from sklearn.linear_model import LogisticRegression
import numpy as np
from dotenv import load_dotenv

# 存储API请求频率的字典
request_counts = {}
RATE_LIMIT = 60  # 每分钟最多60个请求

# 加载环境变量
load_dotenv('.env.production')

app = Flask(__name__, static_folder='frontend')
# 配置CORS，允许所有来源，支持凭证
CORS(app, origins=['*'], supports_credentials=True)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'procrastination_exploration_notebook_2024')
app.config['DATABASE'] = 'data/procrastination_notebook.db'

# ==================== 核心函数（硬编码，不可改） ====================

def get_risk_level(task_aversion, result_value, self_control, w1=0.4, w2=0.3, w3=0.3):
    """
    核心函数：基于时间决策理论计算拖延风险等级
    输入：
        - task_aversion: 任务厌恶程度 (0-100)
        - result_value: 结果价值感 (0-100)
        - self_control: 自我控制能力 (0-100)
        - w1, w2, w3: 权重（默认0.4, 0.3, 0.3）
    输出：
        - risk_level: 风险等级 ("高"/"中"/"低")
        - score: 拖延风险分数
    """
    score = (
        task_aversion * w1 +
        (100 - result_value) * w2 +
        (100 - self_control) * w3
    )
    
    if score < 30:
        risk_level = "低"
    elif score < 70:
        risk_level = "中"
    else:
        risk_level = "高"
    
    return risk_level, score

# ==================== 个性化建议库 ====================

suggestion_db = {
    "高": [
        "立即行动：把任务拆分成最小可执行步骤，现在就做第一步",
        "降低门槛：告诉自己'只做5分钟'，开始后往往会继续下去",
        "消除干扰：关闭手机通知，创造专注环境",
        "寻求支持：找朋友监督，或加入学习小组",
        "设定奖励：完成任务后给自己一个小奖励"
    ],
    "中": [
        "番茄工作法：25分钟专注+5分钟休息",
        "设定截止时间：给自己设定明确的完成时间",
        "环境切换：换个环境工作，减少拖延触发",
        "进度可视化：用进度条或清单跟踪完成情况",
        "适度休息：保证充足睡眠，提升自控力"
    ],
    "低": [
        "保持习惯：维持当前的良好状态",
        "记录成功：记录自己的成功经验，增强信心",
        "帮助他人：分享自己的经验，帮助他人克服拖延",
        "持续优化：寻找进一步优化的空间",
        "预防复发：识别可能导致拖延的潜在风险"
    ]
}

def get_suggestion(risk_level):
    """根据风险等级获取个性化建议"""
    import random
    suggestions = suggestion_db.get(risk_level, suggestion_db["中"])
    return random.choice(suggestions)

# ==================== 数据库初始化 ====================

def init_db():
    """初始化数据库，创建所有必要的表"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        w1 REAL DEFAULT 0.4,
        w2 REAL DEFAULT 0.3,
        w3 REAL DEFAULT 0.3,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        agreed_to_terms INTEGER DEFAULT 0,
        terms_agreed_at TEXT
    )
    ''')
    
    # 核心函数结果表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_function_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        task_aversion INTEGER NOT NULL,
        result_value INTEGER NOT NULL,
        self_control INTEGER NOT NULL,
        w1 REAL NOT NULL,
        w2 REAL NOT NULL,
        w3 REAL NOT NULL,
        score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        user_notes TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    # 模型预测表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS model_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        task_aversion INTEGER NOT NULL,
        result_value INTEGER NOT NULL,
        self_control INTEGER NOT NULL,
        w1 REAL NOT NULL,
        w2 REAL NOT NULL,
        w3 REAL NOT NULL,
        predicted_level TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    # 风险记录表（包含报告路径）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS risk_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        task_aversion INTEGER NOT NULL,
        result_value INTEGER NOT NULL,
        self_control INTEGER NOT NULL,
        w1 REAL NOT NULL,
        w2 REAL NOT NULL,
        w3 REAL NOT NULL,
        score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        model_predicted_level TEXT,
        suggestion TEXT NOT NULL,
        user_notes TEXT,
        report_path TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    # 反馈表（用户对建议的评价）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        suggestion_id TEXT NOT NULL,
        suggestion_content TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        feedback_type TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# ==================== API请求频率限制装饰器 ====================

def rate_limit(f):
    """API请求频率限制装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        # 清理过期的请求记录
        if client_ip in request_counts:
            # 只保留最近60秒的请求
            request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < 60]
        else:
            request_counts[client_ip] = []
        
        # 检查请求频率
        if len(request_counts[client_ip]) >= RATE_LIMIT:
            return jsonify({'status': 'error', 'message': '请求过于频繁，请稍后再试'}), 429
        
        # 记录本次请求
        request_counts[client_ip].append(current_time)
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== 用户认证装饰器 ====================

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        
        if not token:
            # 尝试从Authorization header获取
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'status': 'error', 'message': '未登录'}), 401
        
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user_id = payload['user_id']
            g.username = payload['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'status': 'error', 'message': '登录已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'status': 'error', 'message': '无效的登录凭证'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== 用户认证API ====================

@app.route('/api/register', methods=['POST'])
@rate_limit
def register():
    """用户注册"""
    try:
        data = request.json or {}
        
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # 验证输入
        if not phone and not email:
            return jsonify({'status': 'error', 'message': '请提供手机号或邮箱'}), 400
        
        if not username:
            return jsonify({'status': 'error', 'message': '请提供用户名'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'status': 'error', 'message': '密码长度至少6位'}), 400
    
        # 生成用户ID
        user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}_{np.random.randint(1000, 9999)}"
        
        # 密码加密（增强哈希强度）
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        # 获取协议同意状态
        agree_to_terms = data.get('agree_to_terms', False)
        terms_agreed_at = datetime.now().isoformat() if agree_to_terms else None
        
        cursor.execute('''
            INSERT INTO users (user_id, phone, email, username, password_hash, agreed_to_terms, terms_agreed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, phone if phone else None, email if email else None, username, password_hash, agree_to_terms, terms_agreed_at))
        
        conn.commit()
        
        # 生成JWT token
        token = jwt.encode({
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow().timestamp() + 7 * 24 * 3600  # 7天有效期
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        response = jsonify({
            'status': 'success',
            'message': '注册成功',
            'user_id': user_id,
            'username': username
        })
        
        response.set_cookie('token', token, max_age=7*24*3600, httponly=True, samesite='Lax')
        
        conn.close()
        return response
        
    except sqlite3.IntegrityError as e:
        if conn:
            conn.close()
        error_msg = str(e)
        if 'phone' in error_msg:
            return jsonify({'status': 'error', 'message': '手机号已被注册'}), 400
        elif 'email' in error_msg:
            return jsonify({'status': 'error', 'message': '邮箱已被注册'}), 400
        else:
            return jsonify({'status': 'error', 'message': '注册失败，请重试'}), 400
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'status': 'error', 'message': f'注册失败: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
@rate_limit
def login():
    """用户登录"""
    try:
        data = request.json or {}
        
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        agree_to_terms = data.get('agree_to_terms', False)
        
        if not identifier or not password:
            return jsonify({'status': 'error', 'message': '请提供登录凭证和密码'}), 400
    
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        # 查找用户（支持手机号或邮箱登录）
        cursor.execute('''
            SELECT user_id, username, password_hash FROM users 
            WHERE phone = ? OR email = ?
        ''', (identifier, identifier))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'status': 'error', 'message': '用户不存在'}), 401
        
        user_id, username, password_hash = user
        
        # 验证密码
        if isinstance(password_hash, str):
            password_hash = password_hash.encode('utf-8')
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash):
            conn.close()
            return jsonify({'status': 'error', 'message': '密码错误'}), 401
        
        # 获取协议同意状态并更新
        if agree_to_terms:
            cursor.execute('''
                UPDATE users 
                SET agreed_to_terms = ?, terms_agreed_at = ? 
                WHERE user_id = ?
            ''', (1, datetime.now().isoformat(), user_id))
            conn.commit()
        
        conn.close()
        
        # 生成JWT token
        token = jwt.encode({
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow().timestamp() + 7 * 24 * 3600
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        response = jsonify({
            'status': 'success',
            'message': '登录成功',
            'user_id': user_id,
            'username': username
        })
        
        response.set_cookie('token', token, max_age=7*24*3600, httponly=True, samesite='Lax')
        
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'登录失败: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
@rate_limit
def logout():
    """用户登出"""
    response = jsonify({'status': 'success', 'message': '已登出'})
    response.delete_cookie('token')
    return response

@app.route('/api/user', methods=['GET'])
@login_required
@rate_limit
def get_user_info():
    """获取当前用户信息"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, username, phone, email, w1, w2, w3, created_at, agreed_to_terms, terms_agreed_at
        FROM users WHERE user_id = ?
    ''', (g.user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    return jsonify({
        'status': 'success',
        'user': {
            'user_id': user[0],
            'username': user[1],
            'phone': user[2],
            'email': user[3],
            'w1': user[4],
            'w2': user[5],
            'w3': user[6],
            'created_at': user[7],
            'agreed_to_terms': bool(user[8]) if len(user) > 8 else False,
            'terms_agreed_at': user[9] if len(user) > 9 else None
        }
    })

# ==================== 核心功能API ====================

@app.route('/api/assess', methods=['POST'])
@login_required
@rate_limit
def assess():
    """拖延风险评估（核心功能）"""
    data = request.json
    
    task_aversion = int(data.get('task_aversion', 50))
    result_value = int(data.get('result_value', 50))
    self_control = int(data.get('self_control', 50))
    user_notes = data.get('user_notes', '')
    
    # 获取用户权重
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('SELECT w1, w2, w3 FROM users WHERE user_id = ?', (g.user_id,))
    user_weights = cursor.fetchone()
    
    if not user_weights:
        conn.close()
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    w1, w2, w3 = user_weights
    
    # 1. 核心函数计算
    risk_level, score = get_risk_level(task_aversion, result_value, self_control, w1, w2, w3)
    
    # 2. 机器学习模型预测
    model_predicted_level = predict_with_model(g.user_id, task_aversion, result_value, self_control, w1, w2, w3)
    
    # 3. 生成个性化建议
    suggestion = get_suggestion(risk_level)
    
    # 4. 生成HTML报告
    timestamp_str = datetime.now().strftime('%Y%m%d%H%M%S')
    formatted_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    iso_timestamp = datetime.now().isoformat()
    report_filename = f"report_{g.user_id}_{timestamp_str}.html"
    report_path = generate_html_report(
        g.user_id, g.username, timestamp_str,
        task_aversion, result_value, self_control,
        w1, w2, w3, score, risk_level,
        model_predicted_level, suggestion, user_notes
    )
    
    # 5. 保存到数据库
    # 保存核心函数结果
    cursor.execute('''
        INSERT INTO core_function_results 
        (user_id, task_aversion, result_value, self_control, w1, w2, w3, score, risk_level, user_notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (g.user_id, task_aversion, result_value, self_control, w1, w2, w3, score, risk_level, user_notes, formatted_timestamp))
    
    # 保存模型预测
    cursor.execute('''
        INSERT INTO model_predictions 
        (user_id, task_aversion, result_value, self_control, w1, w2, w3, predicted_level, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (g.user_id, task_aversion, result_value, self_control, w1, w2, w3, model_predicted_level, formatted_timestamp))
    
    # 保存风险记录（包含报告路径）
    cursor.execute('''
        INSERT INTO risk_records 
        (user_id, task_aversion, result_value, self_control, w1, w2, w3, score, risk_level, 
         model_predicted_level, suggestion, user_notes, report_path, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (g.user_id, task_aversion, result_value, self_control, w1, w2, w3, score, risk_level,
          model_predicted_level, suggestion, user_notes, report_path, formatted_timestamp))
    
    conn.commit()
    conn.close()
    
    # 返回结果
    return jsonify({
        'status': 'success',
        'result': {
            'task_aversion': task_aversion,
            'result_value': result_value,
            'self_control': self_control,
            'weights': {'w1': w1, 'w2': w2, 'w3': w3},
            'core_function': {
                'score': round(score, 2),
                'risk_level': risk_level,
                'formula': f"{task_aversion}×{w1} + (100-{result_value})×{w2} + (100-{self_control})×{w3} = {round(score, 2)}"
            },
            'model_prediction': {
                'risk_level': model_predicted_level,
                'match': risk_level == model_predicted_level
            },
            'suggestion': suggestion,
            'report_path': report_path,
            'timestamp': iso_timestamp
        }
    })

# ==================== 机器学习模型 ====================

def predict_with_model(user_id, task_aversion, result_value, self_control, w1, w2, w3):
    """
    使用用户个人历史数据训练模型并预测
    如果历史数据不足，返回核心函数结果
    """
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # 获取用户历史数据
    cursor.execute('''
        SELECT task_aversion, result_value, self_control, risk_level 
        FROM core_function_results 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 100
    ''', (user_id,))
    
    history_data = cursor.fetchall()
    conn.close()
    
    # 如果历史数据少于5条，直接返回核心函数结果
    if len(history_data) < 5:
        risk_level, _ = get_risk_level(task_aversion, result_value, self_control, w1, w2, w3)
        return risk_level
    
    # 准备训练数据
    X = []
    y = []
    
    for row in history_data:
        X.append([row[0], row[1], row[2]])
        y.append(row[3])
    
    X = np.array(X)
    y = np.array(y)
    
    # 训练模型
    try:
        model = LogisticRegression(multi_class='multinomial', max_iter=1000)
        model.fit(X, y)
        
        # 预测
        prediction = model.predict([[task_aversion, result_value, self_control]])[0]
        return prediction
    except Exception as e:
        print(f"模型训练失败: {e}")
        risk_level, _ = get_risk_level(task_aversion, result_value, self_control, w1, w2, w3)
        return risk_level

# ==================== HTML报告生成 ====================

def generate_html_report(user_id, username, timestamp, task_aversion, result_value, self_control,
                        w1, w2, w3, score, risk_level, model_predicted_level, suggestion, user_notes):
    """生成HTML报告文件"""
    
    # 创建用户报告目录
    report_dir = f"data/reports/{user_id}"
    os.makedirs(report_dir, exist_ok=True)
    
    report_filename = f"report_{user_id}_{timestamp}.html"
    report_path = os.path.join(report_dir, report_filename)
    
    # 统一使用正斜杠，便于前端处理
    report_path_forward = report_path.replace('\\', '/')
    
    # 计算差异
    match_status = "一致：模型很准" if risk_level == model_predicted_level else f"不一致：差异需关注"
    
    # 格式化时间
    formatted_time = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[8:10]}:{timestamp[10:12]}:{timestamp[12:14]}"
    
    # 生成HTML内容
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>你的拖延评估报告 - {formatted_time}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4db6ac 0%, #00897b 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .card {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #4db6ac;
        }}
        
        .card h2 {{
            font-size: 18px;
            color: #00897b;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        
        .card h2::before {{
            content: "📊";
            margin-right: 10px;
        }}
        
        .dimension {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .dimension-label {{
            font-weight: 600;
            color: #555;
        }}
        
        .dimension-value {{
            font-size: 24px;
            font-weight: bold;
            color: #00897b;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4db6ac, #00897b);
            border-radius: 4px;
        }}
        
        .formula {{
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            font-family: "Courier New", monospace;
            font-size: 14px;
            color: #666;
            margin-top: 15px;
            border: 1px solid #e0e0e0;
        }}
        
        .risk-badge {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 18px;
            font-weight: bold;
            margin: 10px 5px;
        }}
        
        .risk-high {{
            background: #ffebee;
            color: #c62828;
        }}
        
        .risk-medium {{
            background: #fff3e0;
            color: #ef6c00;
        }}
        
        .risk-low {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        
        .comparison {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        
        .comparison-item {{
            text-align: center;
            flex: 1;
        }}
        
        .comparison-label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .suggestion-box {{
            background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #00897b;
            font-style: italic;
            color: #00695c;
        }}
        
        .notes-box {{
            background: #fff9c4;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 14px;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>你的拖延评估报告</h1>
            <div class="subtitle">{username} · {formatted_time}</div>
        </div>
        
        <div class="content">
            <div class="card">
                <h2>三维度分数</h2>
                
                <div class="dimension">
                    <span class="dimension-label">任务厌恶程度</span>
                    <span class="dimension-value">{task_aversion}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {task_aversion}%"></div>
                </div>
                
                <div class="dimension" style="margin-top: 20px;">
                    <span class="dimension-label">结果价值感</span>
                    <span class="dimension-value">{result_value}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {result_value}%"></div>
                </div>
                
                <div class="dimension" style="margin-top: 20px;">
                    <span class="dimension-label">自我控制能力</span>
                    <span class="dimension-value">{self_control}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {self_control}%"></div>
                </div>
            </div>
            
            <div class="card">
                <h2>双结果对比</h2>
                
                <div class="comparison">
                    <div class="comparison-item">
                        <div class="comparison-label">核心函数结果</div>
                        <span class="risk-badge risk-{risk_level.lower()}">{risk_level}风险</span>
                        <div style="margin-top: 10px; font-size: 14px; color: #666;">
                            分数: {round(score, 2)}
                        </div>
                    </div>
                    
                    <div class="comparison-item">
                        <div class="comparison-label">模型预测结果</div>
                        <span class="risk-badge risk-{model_predicted_level.lower()}">{model_predicted_level}风险</span>
                        <div style="margin-top: 10px; font-size: 14px; color: #666;">
                            {match_status}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>个性化建议</h2>
                <div class="suggestion-box">
                    "{suggestion}"
                </div>
            </div>
            
            {"<div class='notes-box'><strong>任务描述：</strong><br>" + user_notes + "</div>" if user_notes else ""}
        </div>
        
        <div class="footer">
            拖延探索笔记本 · 帮助你认清自己的拖延模式
        </div>
    </div>
</body>
</html>'''
    
    # 写入文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_path_forward

# ==================== 历史记录API ====================

@app.route('/api/history', methods=['GET'])
@login_required
@rate_limit
def get_history():
    """获取历史记录"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, task_aversion, result_value, self_control, w1, w2, w3, 
               score, risk_level, model_predicted_level, suggestion, 
               user_notes, report_path, timestamp
        FROM risk_records 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    ''', (g.user_id,))
    
    records = cursor.fetchall()
    conn.close()
    
    history = []
    for record in records:
        # 将数据库中的时间字符串转换为ISO格式
        db_timestamp = record[13]
        iso_timestamp = db_timestamp.replace(' ', 'T') + 'Z' if ' ' in db_timestamp else db_timestamp
        
        history.append({
            'id': record[0],
            'task_aversion': record[1],
            'result_value': record[2],
            'self_control': record[3],
            'weights': {'w1': record[4], 'w2': record[5], 'w3': record[6]},
            'score': round(record[7], 2),
            'risk_level': record[8],
            'model_predicted_level': record[9],
            'suggestion': record[10],
            'user_notes': record[11],
            'report_path': record[12],
            'timestamp': iso_timestamp,
            'match': record[8] == record[9]
        })
    
    return jsonify({
        'status': 'success',
        'history': history
    })

# ==================== 数据分析API ====================

@app.route('/api/analytics', methods=['GET'])
@login_required
@rate_limit
def get_analytics():
    """获取数据分析"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # 总评估次数
    cursor.execute('SELECT COUNT(*) FROM risk_records WHERE user_id = ?', (g.user_id,))
    total_count = cursor.fetchone()[0]
    
    # 各风险等级次数
    cursor.execute('''
        SELECT risk_level, COUNT(*) 
        FROM risk_records 
        WHERE user_id = ? 
        GROUP BY risk_level
    ''', (g.user_id,))
    
    level_counts = dict(cursor.fetchall())
    high_count = level_counts.get('高', 0)
    medium_count = level_counts.get('中', 0)
    low_count = level_counts.get('低', 0)
    
    # 平均分数
    cursor.execute('SELECT AVG(score) FROM risk_records WHERE user_id = ?', (g.user_id,))
    avg_score = cursor.fetchone()[0] or 0
    
    # 平均维度分数
    cursor.execute('''
        SELECT AVG(task_aversion), AVG(result_value), AVG(self_control)
        FROM risk_records 
        WHERE user_id = ?
    ''', (g.user_id,))
    
    avg_dimensions = cursor.fetchone()
    
    # 模型准确率
    cursor.execute('''
        SELECT COUNT(*) FROM risk_records 
        WHERE user_id = ? AND risk_level = model_predicted_level
    ''', (g.user_id,))
    
    match_count = cursor.fetchone()[0]
    model_accuracy = (match_count / total_count * 100) if total_count > 0 else 0
    
    conn.close()
    
    return jsonify({
        'status': 'success',
        'analytics': {
            'total_count': total_count,
            'level_distribution': {
                'high': high_count,
                'medium': medium_count,
                'low': low_count
            },
            'avg_score': round(avg_score, 2),
            'avg_dimensions': {
                'task_aversion': round(avg_dimensions[0], 2) if avg_dimensions[0] else 0,
                'result_value': round(avg_dimensions[1], 2) if avg_dimensions[1] else 0,
                'self_control': round(avg_dimensions[2], 2) if avg_dimensions[2] else 0
            },
            'model_accuracy': round(model_accuracy, 2),
            'high_risk_ratio': round(high_count / total_count * 100, 2) if total_count > 0 else 0
        }
    })

# ==================== 权重设置API ====================

@app.route('/api/weights', methods=['GET', 'POST'])
@login_required
@rate_limit
def handle_weights():
    """获取或设置权重"""
    if request.method == 'GET':
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('SELECT w1, w2, w3 FROM users WHERE user_id = ?', (g.user_id,))
        weights = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'weights': {
                'w1': weights[0],
                'w2': weights[1],
                'w3': weights[2]
            }
        })
    
    else:  # POST
        data = request.json
        w1 = float(data.get('w1', 0.4))
        w2 = float(data.get('w2', 0.3))
        w3 = float(data.get('w3', 0.3))
        
        # 验证权重总和为1
        if abs(w1 + w2 + w3 - 1.0) > 0.01:
            return jsonify({'status': 'error', 'message': '权重总和必须为1'}), 400
        
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET w1 = ?, w2 = ?, w3 = ? WHERE user_id = ?', 
                      (w1, w2, w3, g.user_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': '权重更新成功',
            'weights': {'w1': w1, 'w2': w2, 'w3': w3}
        })

# ==================== 反馈API ====================

@app.route('/api/feedback', methods=['POST'])
@login_required
@rate_limit
def submit_feedback():
    """提交用户对建议的反馈"""
    data = request.json
    
    suggestion_id = data.get('suggestion_id', '').strip()
    suggestion_content = data.get('suggestion_content', '').strip()
    risk_level = data.get('risk_level', '').strip()
    feedback_type = data.get('feedback_type', '').strip()
    
    # 验证输入
    if not suggestion_id or not suggestion_content:
        return jsonify({'status': 'error', 'message': '缺少建议信息'}), 400
    
    if risk_level not in ['高', '中', '低']:
        return jsonify({'status': 'error', 'message': '风险等级无效'}), 400
    
    if feedback_type not in ['useful', 'partially_useful', 'useless']:
        return jsonify({'status': 'error', 'message': '反馈类型无效'}), 400
    
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO feedbacks (user_id, suggestion_id, suggestion_content, risk_level, feedback_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (g.user_id, suggestion_id, suggestion_content, risk_level, feedback_type))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': '感谢你的反馈，我们会持续优化！'
        })
    except Exception as e:
        conn.close()
        return jsonify({'status': 'error', 'message': f'提交失败: {str(e)}'}), 500

@app.route('/api/feedback/stats', methods=['GET'])
@login_required
@rate_limit
def get_feedback_stats():
    """获取反馈统计数据（管理员功能）"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # 统计各类型反馈数量
    cursor.execute('''
        SELECT feedback_type, COUNT(*) 
        FROM feedbacks 
        WHERE user_id = ?
        GROUP BY feedback_type
    ''', (g.user_id,))
    
    feedback_counts = dict(cursor.fetchall())
    
    # 统计各风险等级的反馈
    cursor.execute('''
        SELECT risk_level, feedback_type, COUNT(*) 
        FROM feedbacks 
        WHERE user_id = ?
        GROUP BY risk_level, feedback_type
    ''', (g.user_id,))
    
    risk_feedback = {}
    for row in cursor.fetchall():
        risk_level, fb_type, count = row
        if risk_level not in risk_feedback:
            risk_feedback[risk_level] = {}
        risk_feedback[risk_level][fb_type] = count
    
    conn.close()
    
    return jsonify({
        'status': 'success',
        'stats': {
            'total_feedbacks': sum(feedback_counts.values()),
            'feedback_counts': feedback_counts,
            'risk_feedback': risk_feedback
        }
    })

@app.route('/api/admin/stats', methods=['GET'])
@login_required
@rate_limit
def get_admin_stats():
    """获取管理统计数据（管理员功能）"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # 获取总用户数
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # 获取活跃用户数（有行为记录）
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM risk_records')
    active_users = cursor.fetchone()[0]
    
    # 获取风险记录总数
    cursor.execute('SELECT COUNT(*) FROM risk_records')
    total_records = cursor.fetchone()[0]
    
    # 获取各风险等级分布
    cursor.execute('''
        SELECT risk_level, COUNT(*) 
        FROM risk_records 
        GROUP BY risk_level
    ''')
    risk_levels = dict(cursor.fetchone()) if total_records > 0 else {}
    
    # 获取平均分数
    cursor.execute('SELECT AVG(score) FROM risk_records')
    avg_score = cursor.fetchone()[0] or 0
    
    # 获取三维度平均分数
    cursor.execute('''
        SELECT AVG(task_aversion), AVG(result_value), AVG(self_control)
        FROM risk_records
    ''')
    avg_dimensions = cursor.fetchone()
    
    # 获取反馈统计
    cursor.execute('''
        SELECT feedback_type, COUNT(*) 
        FROM feedbacks 
        GROUP BY feedback_type
    ''')
    feedback_counts = dict(cursor.fetchall())
    
    conn.close()
    
    return jsonify({
        'status': 'success',
        'stats': {
            'total_users': total_users,
            'active_users': active_users,
            'total_records': total_records,
            'risk_levels': risk_levels,
            'avg_score': round(avg_score, 2),
            'avg_dimensions': {
                'task_aversion': round(avg_dimensions[0], 2) if avg_dimensions[0] else 0,
                'result_value': round(avg_dimensions[1], 2) if avg_dimensions[1] else 0,
                'self_control': round(avg_dimensions[2], 2) if avg_dimensions[2] else 0
            },
            'feedback_counts': feedback_counts
        }
    })

# ==================== 报告访问 ====================

@app.route('/api/report/<path:report_path>')
def get_report(report_path):
    """访问HTML报告"""
    return send_from_directory('data/reports', report_path)

# ==================== 数据导出API ====================

@app.route('/api/export', methods=['GET'])
@login_required
@rate_limit
def export_data():
    """导出用户数据为CSV格式"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # 获取用户历史记录
    cursor.execute('''
        SELECT id, task_aversion, result_value, self_control, w1, w2, w3, 
               score, risk_level, model_predicted_level, suggestion, 
               user_notes, timestamp
        FROM risk_records 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    ''', (g.user_id,))
    
    records = cursor.fetchall()
    conn.close()
    
    # 创建CSV响应
    response = make_response()
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=procrastination_data_{g.user_id}_{datetime.now().strftime("%Y%m%d")}.csv'
    
    # 写入CSV数据
    writer = csv.writer(response.stream)
    # 写入表头
    writer.writerow(['ID', '任务厌恶程度', '结果价值感', '自我控制能力', 
                    '权重1', '权重2', '权重3', '分数', '风险等级', 
                    '模型预测等级', '建议', '用户备注', '时间戳'])
    
    # 写入数据行
    for record in records:
        writer.writerow([
            record[0], record[1], record[2], record[3], 
            record[4], record[5], record[6], record[7], 
            record[8], record[9], record[10], record[11], record[12]
        ])
    
    return response

# ==================== 前端页面路由 ====================

@app.route('/')
def index():
    """主页面"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """静态文件服务"""
    return send_from_directory('frontend', path)

# ==================== 主函数 ====================

if __name__ == '__main__':
    print("正在启动拖延探索笔记本...")
    
    # 确保数据目录存在
    os.makedirs('data/reports', exist_ok=True)
    
    # 初始化数据库
    init_db()
    print("数据库初始化完成")
    
    # 启动Flask服务器
    print("启动服务器: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
