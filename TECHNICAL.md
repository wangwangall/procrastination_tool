# 技术文档

## 系统架构

### 整体架构
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   前端页面       │────▶│   Flask后端     │────▶│   数据库/模型   │
│   (HTML/JS)     │◀────│   (app.py)      │◀────│   (SQLite/ML)   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 核心组件
1. **前端**：HTML + JavaScript 实现的用户界面
2. **后端**：Flask 框架实现的 API 服务
3. **数据库**：SQLite 数据库存储评估数据
4. **模型**：scikit-learn 实现的逻辑回归模型

## 数据流程

### 1. 数据收集流程
1. 用户在前端页面调整三个维度的滑动条
2. 前端发送 POST 请求到 `/predict` 接口
3. 后端接收请求，处理数据并预测拖延概率
4. 后端返回预测结果给前端
5. 前端展示预测结果
6. 用户反馈实际拖延情况
7. 前端发送 POST 请求到 `/report` 接口
8. 后端将数据存储到数据库

### 2. 模型训练流程
1. `seed_data.py` 生成种子数据并插入数据库
2. `train_model.py` 从数据库读取数据
3. 数据预处理和特征提取
4. 训练逻辑回归模型
5. 保存模型为 `model.pkl`
6. `app.py` 启动时加载模型

## 核心算法

### 1. 时间决策理论
```python
def get_risk_level(answers):
    w1, w2, w3 = 0.4, 0.3, 0.3
    score = (answers["任务厌恶"] * w1 + 
             (100 - answers["结果价值"]) * w2 + 
             (100 - answers["自我控制"]) * w3)
    if score < 30:
        return "低"
    elif score < 70:
        return "中"
    else:
        return "高"
```

### 2. 机器学习模型
- **算法**：逻辑回归（二分类）
- **输入特征**：task_aversion, result_value, self_control
- **输出**：拖延概率（0-1）
- **训练数据**：基于时间决策理论生成的50条种子数据
- **模型评估**：训练集准确率约90%

## 关键实现细节

### 1. 模型加载与预测
```python
try:
    # 加载模型
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    # 准备特征
    features = [[task_aversion, result_value, self_control]]
    # 预测概率
    probability = model.predict_proba(features)[0][1]
except Exception as e:
    # 模型加载失败，回退到时间决策理论
    score = (task_aversion * 0.4 + (100 - result_value) * 0.3 + (100 - self_control) * 0.3)
    probability = min(1.0, max(0.0, score / 100))
```

### 2. 数据库操作
```python
def init_db():
    conn = sqlite3.connect('data/risk_records.db')
    c = conn.cursor()
    # 创建表
    c.execute('''
    CREATE TABLE IF NOT EXISTS risk_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_aversion INTEGER,
        result_value INTEGER,
        self_control INTEGER,
        actual_delay INTEGER,
        timestamp TEXT,
        source TEXT
    )
    ''')
    conn.commit()
    conn.close()
```

### 3. 种子数据生成
- **场景设计**：6个典型场景（L1, L2, M1, M2, H1, H2）
- **数据分布**：每个场景生成一定比例的数据
- **随机性**：在场景范围内随机生成数据，确保数据多样性
- **验证**：确保生成的数据符合场景定义

## 技术栈选择理由

### 1. Flask
- **轻量级**：适合小型应用，部署简单
- **灵活性**：易于扩展和定制
- **内置开发服务器**：方便开发和测试
- **丰富的生态**：大量扩展和插件

### 2. SQLite
- **轻量级**：无需独立服务器，文件型数据库
- **易于部署**：单个文件即可，适合小型应用
- **功能完备**：支持基本的SQL操作
- **Python内置**：无需额外安装

### 3. scikit-learn
- **简单易用**：API设计清晰，学习曲线平缓
- **功能强大**：提供多种机器学习算法
- **性能稳定**：适合中小型数据集
- **文档丰富**：有详细的使用文档和示例

## 性能优化

### 1. 模型加载
- 模型在应用启动时加载，避免每次请求都加载
- 使用pickle序列化存储模型，提高加载速度

### 2. 数据库操作
- 使用参数化查询，防止SQL注入
- 批量插入数据，提高数据导入速度
- 适当创建索引，提高查询效率

### 3. 错误处理
- 实现完善的错误处理机制
- 当模型不可用时自动回退到时间决策理论
- 提供详细的错误信息，便于调试

## 安全性考虑

### 1. 输入验证
- 验证用户输入的取值范围（0-100）
- 防止恶意输入导致系统崩溃

### 2. 数据安全
- 数据库文件权限设置
- 避免存储敏感信息

### 3. API安全
- 实现基本的请求验证
- 防止恶意请求导致系统过载

## 部署建议

### 1. 开发环境
- Anaconda 虚拟环境
- 本地开发服务器

### 2. 生产环境
- 使用 WSGI 服务器（如 Gunicorn）
- 配置反向代理（如 Nginx）
- 设置环境变量管理敏感配置

### 3. 数据备份
- 定期备份数据库文件
- 考虑使用版本控制系统管理代码和配置

## 监控与维护

### 1. 日志记录
- 记录API请求和响应
- 记录模型加载和预测情况
- 记录数据库操作

### 2. 性能监控
- 监控API响应时间
- 监控数据库查询性能
- 监控模型预测性能

### 3. 定期维护
- 定期更新模型
- 定期清理和备份数据
- 定期检查系统状态