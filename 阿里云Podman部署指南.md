# 阿里云轻量服务器Podman部署指南

## 一、环境说明

阿里云轻量服务器默认使用Podman作为容器引擎，而非Docker。本指南将详细说明如何在阿里云轻量服务器上使用Podman部署拖延探索笔记本应用。

## 二、准备工作

### 1. 登录阿里云服务器

使用SSH工具登录到你的阿里云轻量服务器：

```bash
ssh root@你的服务器IP
```

### 2. 安装必要依赖

确保服务器上已安装Podman和相关工具：

```bash
# 安装Podman和podman-compose
dnf install -y podman podman-compose

# 安装其他必要依赖
dnf install -y git curl gcc python3-devel libffi-devel

# 升级pip
python3 -m pip install --upgrade pip
```

### 3. 克隆代码仓库

将代码克隆到服务器上：

```bash
# 进入项目目录
cd /home/admin

# 克隆代码
git clone 你的GitHub仓库地址 procrastination_tool

# 进入项目目录
cd procrastination_tool
```

## 三、配置环境变量

### 1. 创建环境变量文件

根据模板创建环境变量文件：

```bash
# 复制示例环境变量文件
cp .env.production.example .env.production

# 编辑环境变量文件
vim .env.production
```

### 2. 配置环境变量

在.env.production文件中配置以下内容：

```
# Flask配置
FLASK_ENV=production
FLASK_APP=app.py
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5001

# 安全配置
SECRET_KEY=你的密钥（建议使用随机字符串）

# 数据库配置
DATABASE_URL=sqlite:///data/procrastination_notebook.db

# API配置
API_BASE=http://你的服务器IP:5001/api

# 日志配置
LOG_LEVEL=INFO

# Gunicorn配置
GUNICORN_WORKERS=3
GUNICORN_BIND=0.0.0.0:5001
```

## 四、部署应用

### 1. 使用podman-compose部署

使用我们提供的podman-compose.yml文件部署应用：

```bash
# 确保在项目根目录下
cd /home/admin/procrastination_tool

# 启动应用
podman-compose up -d

# 查看容器状态
podman-compose ps

# 查看日志
podman-compose logs -f
```

### 2. 直接使用Podman部署

如果你不使用podman-compose，也可以直接使用Podman命令部署：

```bash
# 构建镜像
podman build -t procrastination_tool .

# 运行容器
podman run -d \
  --name procrastination_tool \
  -p 5001:5001 \
  -v ./data:/app/data \
  -e SECRET_KEY=你的密钥 \
  -e FLASK_ENV=production \
  --restart unless-stopped \
  procrastination_tool

# 查看容器状态
podman ps

# 查看日志
podman logs -f procrastination_tool
```

## 五、验证部署

### 1. 检查容器状态

```bash
podman ps
```

你应该看到类似以下输出：

```
CONTAINER ID  IMAGE                           COMMAND               CREATED         STATUS             PORTS                   NAMES
1234567890ab  localhost/procrastination_tool  gunicorn --workers...  5 minutes ago   Up 5 minutes ago   0.0.0.0:5001->5001/tcp  procrastination_tool
```

### 2. 测试应用访问

在浏览器中访问以下地址：

```
http://你的服务器IP:5001
```

你应该能看到拖延探索笔记本的登录页面。

### 3. 测试API访问

使用curl测试API是否正常工作：

```bash
curl http://你的服务器IP:5001/api/user
```

你应该收到一个JSON格式的响应，提示未登录。

## 六、管理应用

### 1. 停止应用

```bash
# 使用podman-compose
podman-compose down

# 直接使用Podman
podman stop procrastination_tool
```

### 2. 重启应用

```bash
# 使用podman-compose
podman-compose restart

# 直接使用Podman
podman restart procrastination_tool
```

### 3. 更新应用

```bash
# 进入项目目录
cd /home/admin/procrastination_tool

# 拉取最新代码
git pull

# 重新构建并启动
podman-compose up -d --build
```

### 4. 查看应用日志

```bash
# 使用podman-compose
podman-compose logs -f

# 直接使用Podman
podman logs -f procrastination_tool
```

## 七、常见问题与解决方案

### 1. 端口被占用

如果端口5001已被占用，可以修改podman-compose.yml文件中的端口映射：

```yaml
ports:
  - "80:5001"  # 将80端口映射到容器的5001端口
```

### 2. 数据库连接问题

确保数据目录已正确挂载：

```yaml
volumes:
  - ./data:/app/data  # 检查该挂载配置是否正确
```

### 3. 应用启动失败

查看日志以定位问题：

```bash
podman-compose logs -f
```

### 4. 权限问题

确保数据目录有正确的权限：

```bash
chmod -R 755 data/
```

## 八、安全建议

1. **修改默认密钥**：在.env.production中修改SECRET_KEY
2. **配置防火墙**：只开放必要的端口（如5001）
3. **定期备份数据**：定期备份data目录
4. **更新依赖**：定期更新Python依赖和Podman镜像
5. **使用HTTPS**：建议在生产环境中配置HTTPS

## 九、技术支持

如果在部署过程中遇到任何问题，可以查看：

- 应用日志：`podman-compose logs -f`
- 服务器日志：`journalctl -u podman`
- 应用代码：查看app.py等核心文件

## 十、自动化部署

本项目已配置GitHub Actions CI/CD，可以实现代码推送后自动部署到阿里云服务器。如需使用自动化部署，请按照以下步骤配置：

1. 在GitHub仓库的Settings中添加以下Secrets：
   - `SERVER_SSH_KEY`：服务器的SSH私钥
   - `SERVER_IP`：服务器IP地址

2. 确保GitHub Actions工作流文件（.github/workflows/deploy.yml）已正确配置

3. 推送代码到main分支，触发自动部署

---

祝您部署顺利！