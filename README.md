# 拖延风险评估工具

一个基于时间决策理论和机器学习的拖延风险评估工具，帮助用户识别拖延风险并提供个性化建议。

## 项目介绍

该工具通过分析用户的任务厌恶程度、结果价值感和自我控制能力，预测拖延概率并提供针对性建议。项目采用前后端分离架构，支持用户认证、历史记录管理、数据分析和反馈收集等功能。
注意：下文会出现“时间决策理论”名称，该时间决策理论只是代称，并无该理论，本工具是参考跨期决策、时间折扣模型与认知心理学方向对拖延有关研究的。

### 核心功能

- 📊 **拖延风险评估**：基于任务厌恶度、结果价值感和自我控制能力的综合评估
- 🤖 **双模型预测**：结合时间决策理论和机器学习模型，提供更准确的拖延概率预测（时间决策理论只是代称，并无该理论，而是参考跨期决策、时间折扣模型与认知心理学方向对拖延有关研究）
- 🔐 **用户认证**：支持用户注册、登录和个人信息管理
- 📝 **历史记录**：保存用户评估历史，支持查看和分析
- 📈 **数据分析**：提供用户拖延趋势分析和维度分析
- 💬 **反馈收集**：支持用户对建议的反馈，持续改进模型
- 📱 **响应式设计**：适配不同设备，支持移动端访问

## 技术栈

### 后端
- Python 3.9+
- Flask 2.0+
- SQLite 3
- scikit-learn（机器学习）
- Flask-CORS（跨域支持）

### 前端
- HTML5
- CSS3
- JavaScript (ES6+)

## 安装和运行

### 1. 环境准备

#### Windows系统

```bash
# 创建虚拟环境
python -m venv procrastinate_env

# 激活虚拟环境
procrastinate_env\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### Linux/macOS系统

```bash
# 创建虚拟环境
python3 -m venv procrastinate_env

# 激活虚拟环境
source procrastinate_env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行项目

```bash
# 启动Flask后端服务
python app.py

# 访问前端页面
# 在浏览器中打开 http://localhost:5001
```

## 项目结构

```
procrastination_tool/
├── app.py                # 主应用入口
├── backend/              # 后端核心代码
│   ├── __init__.py
│   └── algorithm_core.py # 算法核心模块
├── data/                 # 数据目录
│   └── risk_records.db   # SQLite数据库文件
├── frontend/             # 前端代码
│   ├── index.html        # 主页面
│   └── ...               # 其他前端资源
├── model.pkl             # 训练好的机器学习模型
├── requirements.txt      # 项目依赖
├── README.md             # 项目说明文档
├── LICENSE               # 开源许可证
├── CONTRIBUTING.md       # 贡献指南
└── .gitignore            # Git忽略文件
```

## API文档

### 1. 认证接口

#### 注册
```
POST /register
Content-Type: application/json

{
  "username": "用户名",
  "password": "密码"
}
```

#### 登录
```
POST /login
Content-Type: application/json

{
  "username": "用户名",
  "password": "密码"
}
```

#### 登出
```
POST /logout
```

#### 获取当前用户信息
```
GET /user
```

### 2. 评估接口

#### 预测拖延风险
```
POST /predict
Content-Type: application/json

{
  "任务厌恶": 80,         # 或 "task_aversion": 80
  "结果价值": 20,         # 或 "result_value": 20
  "自我控制": 30          # 或 "self_control": 30
}
```

返回示例：
```json
{
  "拖延概率": 0.85,
  "建议": "您的拖延风险较高，建议采用番茄工作法，将任务分解为25分钟的工作段..."
}
```

#### 上报评估数据
```
POST /report
Content-Type: application/json

{
  "task_aversion": 80,
  "result_value": 20,
  "self_control": 30,
  "timestamp": "2026-03-18T10:00:00Z",
  "source": "直接访问"
}
```

### 3. 历史记录接口

#### 获取评估历史
```
GET /history
```

### 4. 数据分析接口

#### 获取数据分析
```
GET /analytics
```

### 5. 反馈接口

#### 提交反馈
```
POST /feedback
Content-Type: application/json

{
  "feedback": 1,          # 1=有用, 2=部分有用, 0=没用
  "comments": "建议很实用！"
}
```

### 6. 用户行为接口

#### 创建用户行为记录
```
POST /user-behavior
Content-Type: application/json

{
  "task_type": "工作任务",
  "time_pressure": 8,
  "environment": 5,
  "age_group": "25-35",
  "occupation": "程序员"
}
```

#### 获取用户行为记录列表
```
GET /user-behavior
```

#### 获取单个用户行为记录
```
GET /user-behavior/<id>
```

#### 更新用户行为记录
```
PUT /user-behavior/<id>
Content-Type: application/json

{
  "task_type": "学习任务",
  "time_pressure": 6
}
```

#### 删除用户行为记录
```
DELETE /user-behavior/<id>
```

### 7. 使用统计接口

#### 创建使用统计记录
```
POST /usage-stats
Content-Type: application/json

{
  "session_duration": 300,
  "actions_count": 10,
  "feature_used": "assessment"
}
```

#### 获取使用统计记录列表
```
GET /usage-stats
```

#### 获取单个使用统计记录
```
GET /usage-stats/<id>
```

#### 更新使用统计记录
```
PUT /usage-stats/<id>
Content-Type: application/json

{
  "session_duration": 450,
  "actions_count": 15
}
```

#### 删除使用统计记录
```
DELETE /usage-stats/<id>
```

### 8. 数据导出接口

#### 导出脱敏数据
```
GET /export-data
```

## 数据收集指南

### 数据收集目的

1. **改进模型准确性**：通过收集用户的评估数据和反馈，持续优化机器学习模型
2. **个性化建议**：基于用户历史数据提供更精准的个性化建议
3. **学术研究**：用于研究拖延行为的影响因素和干预方法
4. **产品优化**：了解用户使用习惯，优化产品功能和用户体验

### 数据收集范围

#### 1. 评估数据
- 任务厌恶程度（0-100）
- 结果价值感（0-100）
- 自我控制能力（0-100）
- 评估时间戳
- 访问来源

#### 2. 用户行为数据
- 任务类型
- 时间压力程度
- 环境干扰程度
- 年龄组
- 职业

#### 3. 使用统计数据
- 会话时长
- 操作次数
- 使用的功能模块

#### 4. 反馈数据
- 对建议的有用性评价
- 具体反馈内容

### 数据脱敏处理

为保护用户隐私，所有收集的数据都会经过脱敏处理：

1. **用户名**：只保留前2个字符，其余用*替换
2. **职业**：使用通用职业类别，不保留具体职位
3. **年龄组**：只保留年龄段范围，不显示具体年龄
4. **IP地址**：不收集用户IP地址
5. **设备信息**：仅收集设备类型，不收集具体型号

### 数据存储和安全

- 所有数据存储在本地SQLite数据库中，不进行云端存储
- 数据库文件采用权限控制，仅允许应用程序访问
- 用户密码采用SHA-256加密存储
- 定期清理过期数据，保留时间不超过12个月

### 用户权利

1. **知情权**：用户有权了解数据收集的目的、范围和使用方式
2. **选择权**：用户可以选择是否同意数据收集
3. **访问权**：用户有权访问自己的所有数据
4. **删除权**：用户可以随时请求删除自己的数据
5. **撤回权**：用户可以随时撤回数据收集同意

## 模型训练

### 训练数据

- 基于时间决策理论生成的种子数据
- 用户实际评估数据
- 人工标注的拖延行为数据

### 训练方法

1. **特征工程**：提取任务厌恶度、结果价值感和自我控制能力作为特征
2. **模型选择**：使用逻辑回归作为二分类模型
3. **训练过程**：
   - 数据划分：80%训练集，20%测试集
   - 模型训练：使用scikit-learn的LogisticRegression
   - 模型评估：使用准确率、精确率、召回率和F1-score进行评估
4. **模型更新**：定期使用新数据重新训练模型

### 模型文件

- 模型文件：`model.pkl`
- 训练脚本：`train_model.py`

## 开发指南

### 项目结构

```
backend/
├── __init__.py
└── algorithm_core.py     # 算法核心，包含时间决策理论和建议生成

data/                     # 数据目录
└── risk_records.db       # SQLite数据库

frontend/                 # 前端代码
└── index.html            # 主页面
```

### 算法核心

时间决策理论的核心公式：
```python
def get_risk_level(answers):
    w1, w2, w3 = 0.4, 0.3, 0.3  # 权重
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

### 添加新功能

1. **后端开发**：
   - 在`app.py`中添加新的路由和处理函数
   - 如果涉及数据库操作，更新`init_db()`函数
   - 确保添加适当的错误处理和输入验证

2. **前端开发**：
   - 修改`frontend/index.html`添加新的UI组件
   - 添加相应的JavaScript逻辑
   - 确保响应式设计适配不同设备

## 贡献指南

欢迎您为项目做出贡献！请遵循以下步骤：

1. Fork本仓库
2. 创建您的功能分支：`git checkout -b feature/AmazingFeature`
3. 提交您的更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 打开一个Pull Request

### 代码规范

- 遵循PEP 8代码规范
- 添加适当的注释和文档字符串
- 确保测试通过
- 保持代码简洁和可读性

## 许可证

本项目采用MIT许可证，详见[LICENSE](LICENSE)文件。

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 项目地址：https://github.com/yourusername/procrastination-tool
- 邮箱：your.email@example.com

## 更新日志

### v1.0.0 (2026-03-18)

- 初始版本发布
- 实现拖延风险评估核心功能
- 支持用户认证和历史记录
- 集成机器学习模型
- 实现数据收集和脱敏功能

## 致谢

感谢所有为项目做出贡献的开发者和用户！

---

**免责声明**：本工具仅供参考，不能替代专业的心理治疗。如果您有严重的拖延问题，建议咨询专业心理医生。
