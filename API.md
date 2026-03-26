# API 接口说明

## 接口概览
| 接口 | 方法 | 功能 |
|------|------|------|
| `/predict` | POST | 预测拖延概率并返回建议 |
| `/report` | POST | 收集评估数据并存储到数据库 |
| `/` | GET | 访问前端页面 |

## 1. `/predict` 接口

### 功能
基于用户输入的三个维度数据，预测拖延概率并返回个性化建议。

### 请求参数
- **方法**：POST
- **Content-Type**：application/json
- **请求体**：
  ```json
  {
    "task_aversion": 80,    // 任务厌恶度 (0-100)
    "result_value": 20,     // 结果价值 (0-100)
    "self_control": 30       // 自我控制 (0-100)
  }
  ```

### 响应格式
- **成功**：
  ```json
  {
    "拖延概率": 0.85,        // 拖延概率 (0-1)
    "建议": "您的拖延风险较高，建议分解任务并设置明确的时间节点"
  }
  ```
- **失败**：
  ```json
  {
    "error": "参数错误，请检查输入值"
  }
  ```

### 实现逻辑
1. 接收三个维度的输入数据
2. 尝试使用机器学习模型预测拖延概率
3. 如果模型加载失败或预测出错，回退到时间决策理论计算
4. 根据预测结果生成个性化建议
5. 返回预测结果和建议

## 2. `/report` 接口

### 功能
收集用户评估数据并存储到数据库，用于后续模型训练和分析。

### 请求参数
- **方法**：POST
- **Content-Type**：application/json
- **请求体**：
  ```json
  {
    "task_aversion": 80,    // 任务厌恶度 (0-100)
    "result_value": 20,     // 结果价值 (0-100)
    "self_control": 30,     // 自我控制 (0-100)
    "actual_delay": 1,      // 实际拖延情况 (0=未拖延, 1=拖延)
    "source": "web"         // 数据来源
  }
  ```

### 响应格式
- **成功**：
  ```json
  {
    "status": "success",
    "message": "数据保存成功"
  }
  ```
- **失败**：
  ```json
  {
    "status": "error",
    "message": "数据保存失败"
  }
  ```

### 实现逻辑
1. 接收用户评估数据
2. 连接数据库
3. 插入数据到 `risk_records` 表
4. 返回保存结果

## 3. `/` 接口

### 功能
访问前端页面，提供用户交互界面。

### 请求参数
- **方法**：GET

### 响应
- 返回 `frontend/index.html` 页面

## 数据模型

### risk_records 表结构
| 字段名 | 数据类型 | 描述 |
|--------|----------|------|
| id | INTEGER | 自增主键 |
| task_aversion | INTEGER | 任务厌恶度 (0-100) |
| result_value | INTEGER | 结果价值 (0-100) |
| self_control | INTEGER | 自我控制 (0-100) |
| actual_delay | INTEGER | 实际拖延情况 (0/1) |
| timestamp | TEXT | 记录时间戳 |
| source | TEXT | 数据来源 |

## 错误处理
- 所有接口均包含基本的错误处理
- 当模型加载失败时，会自动回退到时间决策理论
- 当数据库操作失败时，会返回错误信息

## 测试方法
使用 `test_predict.py` 脚本测试 `/predict` 接口：
```bash
python test_predict.py
```