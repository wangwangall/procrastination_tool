# 阿里云轻量服务器 Docker Compose安装指南

## 问题分析
当使用 `sudo dnf install -y docker docker-compose` 命令时，提示 "No match for argument: docker-compose"，这是因为 docker-compose 不在默认的 dnf 仓库中。

## 解决方案

### 方法一：使用 pip 安装（推荐）

1. 首先确保已安装 Docker：
   ```bash
   sudo dnf install -y docker
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. 安装 pip：
   ```bash
   sudo dnf install -y python3-pip
   ```

3. 使用 pip 安装 docker-compose：
   ```bash
   sudo pip3 install docker-compose
   ```

4. 验证安装：
   ```bash
   docker-compose --version
   ```

### 方法二：使用官方二进制文件安装

1. 下载最新版本的 docker-compose：
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   ```

2. 赋予执行权限：
   ```bash
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. 验证安装：
   ```bash
   docker-compose --version
   ```

## 后续操作

安装完成后，您可以：

1. 检查 Docker 状态：
   ```bash
   sudo systemctl status docker
   ```

2. 创建 docker 用户组（可选，避免每次使用 sudo）：
   ```bash
   sudo usermod -aG docker $USER
   ```
   然后重新登录或执行 `newgrp docker` 使更改生效。

3. 开始使用 docker-compose：
   - 创建 `docker-compose.yml` 文件定义服务
   - 执行 `docker-compose up -d` 启动服务
   - 执行 `docker-compose ps` 查看服务状态

## 常见问题

- **权限问题**：如果执行 docker-compose 时提示权限不足，请使用 sudo 或将用户添加到 docker 组。
- **版本问题**：如果需要特定版本的 docker-compose，可以在下载 URL 中指定版本号，例如：
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  ```

祝您使用愉快！