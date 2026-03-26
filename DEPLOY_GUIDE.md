# 直接部署指南（绕过GitHub Actions）

如果遇到GitHub访问问题，无法通过GitHub Actions自动部署，可以按照以下步骤直接在服务器上部署应用。

## 前置条件

1. 服务器已安装Docker和Docker Compose
2. 服务器已开放5001端口
3. 本地代码已修复完成

## 部署步骤

### 1. 连接到服务器

使用SSH连接到你的服务器：

```bash
ssh username@server_ip
```

### 2. 创建部署目录

```bash
mkdir -p /var/www/procrastination-tool
cd /var/www/procrastination-tool
```

### 3. 复制代码到服务器

将本地修复好的代码复制到服务器。可以使用`scp`命令：

```bash
# 在本地执行
tar -czf procrastination-tool.tar.gz .
scp procrastination-tool.tar.gz username@server_ip:/var/www/procrastination-tool/
```

### 4. 在服务器上解压代码

```bash
# 在服务器上执行
tar -xzf procrastination-tool.tar.gz
rm procrastination-tool.tar.gz
```

### 5. 构建并启动Docker容器

```bash
docker-compose up -d --build
```

### 6. 验证部署

检查容器状态：

```bash
docker-compose ps
```

查看日志：

```bash
docker-compose logs -f
```

### 7. 测试应用

在浏览器中访问：`http://server_ip:5001`

## 环境变量配置

如果需要修改环境变量，可以编辑`docker-compose.yml`文件中的`environment`部分：

```yaml
environment:
  - FLASK_ENV=production
  - SECRET_KEY=your-secret-key-here
```

修改后需要重启容器：

```bash
docker-compose down
docker-compose up -d
```

## 停止和重启应用

### 停止应用

```bash
docker-compose down
```

### 重启应用

```bash
docker-compose restart
```

## 数据库备份

数据库文件位于`./data/procrastination_notebook.db`，可以定期备份这个文件：

```bash
cp ./data/procrastination_notebook.db ./data/procrastination_notebook.db.backup
```

## 手动更新代码

如果需要更新代码，可以重复步骤3-5：

1. 复制新代码到服务器
2. 解压覆盖
3. 重启容器

## 常见问题排查

1. **端口被占用**：检查5001端口是否被其他进程占用
   ```bash
   netstat -tuln | grep 5001
   ```

2. **容器启动失败**：查看详细日志
   ```bash
   docker-compose logs
   ```

3. **数据库连接问题**：确保`./data`目录有正确的权限
   ```bash
   chmod -R 755 ./data
   ```

4. **登录失败**：检查前端`API_BASE`配置是否正确，应该指向服务器的IP地址

## 代码修复确认

确保以下修复已完成：

1. **前端API配置**：`frontend/index.html`中的`API_BASE`已设置为服务器IP
2. **CORS配置**：`app.py`中已添加`origins=['*']`
3. **依赖项**：`requirements.txt`已包含所有必要依赖
4. **GitHub Actions配置**：`.github/workflows/deploy.yml`已修复

## 测试登录功能

部署完成后，尝试注册一个新用户或使用已有账号登录，确保登录功能正常工作。

如果遇到登录问题，检查浏览器控制台是否有错误信息，常见问题包括：
- API URL配置错误
- 服务器端口未开放
- CORS配置问题
- 容器未正常运行

按照以上步骤操作，你可以绕过GitHub Actions直接在服务器上部署应用，确保应用正常运行。