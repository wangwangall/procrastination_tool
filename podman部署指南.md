# 🚀 拖延风险评估工具 - Podman部署指南

## 🌟 适用场景

当你的服务器上已安装了Podman（如阿里云官方镜像默认安装了podman-docker），但无法安装Docker或docker-compose时，可以使用本指南进行部署。

## 📋 问题分析

从你的操作日志可以看到：
- 服务器已安装了 `podman-docker`（Podman的Docker兼容层）
- 找不到 `docker-compose` 包
- 无法启动 `docker.service`（因为Podman不需要守护进程）
- 没有 `docker` 用户组

## 🛠️ 解决方案：使用Podman部署

### 步骤1：安装Podman Compose

```bash
# 安装Podman Compose
pip3 install podman-compose
```

### 步骤2：验证Podman和Podman Compose

```bash
# 验证Podman安装
podman --version

# 验证Podman Compose安装
podman-compose --version
```

### 步骤3：克隆项目

```bash
# 克隆项目到服务器
git clone https://github.com/你的用户名/procrastination-tool.git
cd procrastination-tool
```

### 步骤4：创建环境变量文件

```bash
# 创建.env文件
cat > .env << EOL
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 16)
DATABASE_URL=data/procrastination_notebook.db
HOST=0.0.0.0
PORT=5001
LOG_LEVEL=INFO
EOL
```

### 步骤5：配置阿里云安全组

（与原指南相同，需要开放5001端口）

### 步骤6：使用Podman Compose启动服务

```bash
# 使用Podman Compose启动服务
podman-compose up -d

# 查看服务状态
podman-compose ps

# 查看日志（可选）
podman-compose logs -f
```

### 步骤7：访问服务

1. 找到服务器的公网IP地址（在阿里云控制台查看）
2. 在浏览器中输入：`http://你的服务器IP:5001`
3. 看到拖延风险评估工具的登录页面，说明部署成功！

## 📋 备选方案：直接使用Docker引擎

如果需要使用真正的Docker引擎，可以按照以下步骤安装：

### 步骤1：卸载podman-docker（可选）

```bash
sudo dnf remove -y podman-docker
```

### 步骤2：安装Docker引擎

```bash
# 安装Docker引擎
sudo dnf install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo dnf install -y docker-compose-plugin
```

### 步骤3：继续使用原指南部署

安装完成后，可以按照原部署指南继续操作。

## 🚑 常见问题

### 1. Podman Compose安装失败

```bash
# 尝试使用pip安装
pip install podman-compose

# 或者使用pip3安装
pip3 install --user podman-compose
```

### 2. 服务启动失败

```bash
# 查看详细日志
podman-compose logs -f

# 检查端口是否被占用
podman-compose ps
```

### 3. 无法访问服务

- 检查阿里云安全组是否开放了5001端口
- 检查防火墙设置：`sudo firewall-cmd --list-ports`
- 如果防火墙未开放5001端口，执行：
  ```bash
  sudo firewall-cmd --add-port=5001/tcp --permanent
  sudo firewall-cmd --reload
  ```

## 🎉 恭喜！

你已经成功使用Podman部署了拖延风险评估工具！现在可以访问服务并开始使用了。