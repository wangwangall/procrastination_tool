@echo off
REM 一键安装 requirements.txt 里的依赖
echo ========================================
echo  正在激活虚拟环境 procrastinate_env ...
call conda activate procrastinate_env

echo 正在切换到项目目录 D:\procrastination_tool ...
d:
cd D:\procrastination_tool

echo 正在安装 requirements.txt 中的依赖 ...
pip install -r requirements.txt

echo 安装完成！
pause