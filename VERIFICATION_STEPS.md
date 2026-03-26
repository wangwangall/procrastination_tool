# 验证服务状态和防火墙规则

## 1. 在服务器上执行以下命令

### 检查防火墙规则
```bash
firewall-cmd --list-ports
```

### 检查端口监听
```bash
netstat -tlnp | grep -E "(80|5001)"
```

### 检查Nginx状态
```bash
systemctl status nginx
```

### 检查应用服务状态
```bash
systemctl status procrastination-tool
```

## 2. 测试访问

### 电脑浏览器测试
```
http://8.148.7.83
```

### 手机浏览器测试
```
http://8.148.7.83
```

## 3. 预期结果

### 防火墙规则
- 应该显示：`80/tcp 5001/tcp`

### 端口监听
- 应该显示：
  - `0.0.0.0:80` (Nginx)
  - `0.0.0.0:5001` (Gunicorn)

### 服务状态
- Nginx：active (running)
- procrastination-tool：active (running)

## 4. 测试结果

请在以下表格中记录测试结果：

| 测试项 | 预期结果 | 实际结果 |
|--------|----------|----------|
| 电脑访问 http://8.148.7.83 | ✅ 正常打开 | |
| 手机访问 http://8.148.7.83 | ✅ 正常打开 | |
| 防火墙规则包含80端口 | ✅ 是 | |
| 防火墙规则包含5001端口 | ✅ 是 | |
| Nginx状态 | ✅ running | |
| 应用服务状态 | ✅ running | |

## 5. 如果测试失败

### 防火墙规则缺少端口
```bash
# 添加缺少的端口
firewall-cmd --zone=public --add-port=5001/tcp --permanent
firewall-cmd --reload
```

### 服务未运行
```bash
# 启动服务
systemctl start nginx
systemctl start procrastination-tool
```

### 端口未监听
```bash
# 检查服务日志
journalctl -u nginx -f
journalctl -u procrastination-tool -f
```
