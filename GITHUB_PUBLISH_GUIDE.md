# GitHub开源发布详细指南

## 适合没有技术基础的小白

本指南将一步步教你如何将拖延风险评估工具发布到GitHub上，不需要任何技术基础，只需按照步骤操作即可。

## 目录

1. [步骤1：安装Git](#步骤1安装git)
2. [步骤2：创建GitHub账户](#步骤2创建github账户)
3. [步骤3：创建GitHub仓库](#步骤3创建github仓库)
4. [步骤4：配置Git](#步骤4配置git)
5. [步骤5：初始化本地仓库](#步骤5初始化本地仓库)
6. [步骤6：添加文件到仓库](#步骤6添加文件到仓库)
7. [步骤7：提交更改](#步骤7提交更改)
8. [步骤8：连接GitHub仓库](#步骤8连接github仓库)
9. [步骤9：推送代码到GitHub](#步骤9推送代码到github)
10. [步骤10：验证发布结果](#步骤10验证发布结果)
11. [常见问题解答](#常见问题解答)

## 步骤1：安装Git

Git是一个版本控制工具，用于管理代码的更改和发布。

### Windows系统安装步骤：

1. 打开浏览器，访问Git官网：https://git-scm.com/downloads
2. 点击页面上的"Windows"下载按钮
3. 下载完成后，双击安装文件开始安装
4. 在安装向导中，所有选项保持默认即可，一直点击"Next"按钮
5. 最后点击"Finish"完成安装

### 验证Git是否安装成功：

1. 按下键盘上的`Win + R`键，打开"运行"窗口
2. 输入`cmd`，然后按回车键，打开命令提示符
3. 在命令提示符中输入`git --version`，然后按回车键
4. 如果显示Git版本号，说明安装成功

## 步骤2：创建GitHub账户

GitHub是一个代码托管平台，用于存储和分享代码。

1. 打开浏览器，访问GitHub官网：https://github.com
2. 点击页面右上角的"Sign up"按钮
3. 输入你的邮箱地址，然后点击"Continue"
4. 创建一个用户名和密码，然后点击"Continue"
5. 选择一个计划，选择"Free"（免费）计划即可
6. 完成验证步骤（可能需要解决一个拼图或回答一些问题）
7. 登录你的邮箱，点击GitHub发送的验证邮件中的链接

## 步骤3：创建GitHub仓库

仓库（Repository）是用于存储代码的地方。

1. 登录GitHub账户
2. 点击页面右上角的"+"按钮，然后选择"New repository"
3. 在"Repository name"字段中输入仓库名称，例如：`procrastination-tool`
4. 在"Description"字段中输入仓库描述，例如：`一个基于时间决策理论和机器学习的拖延风险评估工具`
5. 选择仓库可见性：
   - 选择"Public"（公开），这样所有人都可以看到你的代码
   - 选择"Private"（私有），只有你和你邀请的人可以看到代码
6. 勾选"Initialize this repository with a README"（可选）
7. 点击"Create repository"按钮

## 步骤4：配置Git

在第一次使用Git之前，需要配置你的用户名和邮箱。

1. 按下键盘上的`Win + R`键，打开"运行"窗口
2. 输入`cmd`，然后按回车键，打开命令提示符
3. 在命令提示符中输入以下命令，将`your_name`替换为你的GitHub用户名：
   ```bash
   git config --global user.name "your_name"
   ```
4. 然后输入以下命令，将`your_email@example.com`替换为你注册GitHub时使用的邮箱：
   ```bash
   git config --global user.email "your_email@example.com"
   ```
5. 按回车键执行命令

## 步骤5：初始化本地仓库

1. 打开文件资源管理器，找到你的项目文件夹（`D:\procrastination_tool`）
2. 在文件夹空白处，按住`Shift`键，同时右键点击鼠标
3. 在弹出的菜单中，选择"Git Bash Here"，打开Git命令行窗口
4. 在Git命令行窗口中，输入以下命令，然后按回车键：
   ```bash
   git init
   ```
5. 看到"Initialized empty Git repository in D:/procrastination_tool/.git/"的提示，说明初始化成功

## 步骤6：添加文件到仓库

1. 在Git命令行窗口中，输入以下命令，将所有文件添加到仓库：
   ```bash
   git add .
   ```
2. 按回车键执行命令
3. 这个命令会将项目中的所有文件添加到Git的暂存区

## 步骤7：提交更改

1. 在Git命令行窗口中，输入以下命令，提交你的更改：
   ```bash
   git commit -m "Initial commit"
   ```
2. 按回车键执行命令
3. 这个命令会将暂存区的文件提交到本地仓库，"Initial commit"是提交信息，用于描述这次更改

## 步骤8：连接GitHub仓库

1. 登录GitHub，进入你刚创建的仓库页面
2. 点击"Code"按钮，然后复制显示的URL（以.git结尾）
3. 在Git命令行窗口中，输入以下命令，将`your_github_username`替换为你的GitHub用户名，`your_repository_name`替换为你的仓库名称：
   ```bash
   git remote add origin https://github.com/your_github_username/your_repository_name.git
   ```
4. 按回车键执行命令

## 步骤9：推送代码到GitHub

1. 在Git命令行窗口中，输入以下命令，将代码推送到GitHub：
   ```bash
   git push -u origin main
   ```
2. 按回车键执行命令
3. 此时会弹出一个GitHub登录窗口，输入你的GitHub用户名和密码，或者使用浏览器登录
4. 等待推送完成，看到类似"Writing objects: 100% (xx/xx), done."的提示，说明推送成功

## 步骤10：验证发布结果

1. 登录GitHub，进入你的仓库页面
2. 刷新页面，你应该能看到你的项目文件已经显示在仓库中
3. 恭喜！你已经成功将项目发布到GitHub上了

## 常见问题解答

### 问题1：安装Git时遇到问题怎么办？

- 确保下载的是适合你操作系统的Git版本
- 安装时所有选项保持默认即可
- 如果安装失败，可以尝试重新下载安装文件

### 问题2：忘记GitHub密码怎么办？

- 在GitHub登录页面，点击"Forgot password?"链接
- 按照提示重置密码

### 问题3：推送代码时提示权限错误怎么办？

- 确保你输入的GitHub用户名和密码正确
- 确保你有权限推送代码到该仓库
- 如果你使用的是GitHub SSH密钥，确保密钥已正确配置

### 问题4：推送代码时提示"fatal: remote origin already exists"怎么办？

- 这说明你已经添加过远程仓库
- 可以使用以下命令查看已添加的远程仓库：
  ```bash
  git remote -v
  ```
- 如果需要更改远程仓库，可以先删除旧的远程仓库，再添加新的：
  ```bash
  git remote remove origin
  git remote add origin https://github.com/your_github_username/your_repository_name.git
  ```

### 问题5：如何更新已发布的代码？

- 对项目文件进行更改后，重复以下步骤：
  ```bash
  git add .
  git commit -m "描述你的更改"
  git push origin main
  ```

## 后续操作建议

1. **添加项目README**：确保你的README.md文件包含项目介绍、安装说明和使用指南
2. **添加许可证**：在仓库中添加一个LICENSE文件，选择适合你的开源许可证（如MIT）
3. **邀请贡献者**：如果你希望其他人参与你的项目，可以邀请他们成为仓库的贡献者
4. **创建Issues**：用于跟踪项目中的问题和功能请求
5. **创建Pull Requests**：用于提交和审查代码更改

## 总结

通过以上步骤，你已经成功将拖延风险评估工具发布到GitHub上了！这是一个很好的开始，你可以继续学习更多关于Git和GitHub的知识，进一步完善你的项目。

如果你在操作过程中遇到任何问题，可以随时在GitHub上搜索相关解决方案，或者在项目的Issues中提问。

祝你开源之旅愉快！ 🚀