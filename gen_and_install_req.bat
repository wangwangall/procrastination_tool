@echo off
REM 一键生成纯净 requirements.txt 并安装依赖
echo ========================================
echo  正在激活虚拟环境 procrastinate_env ...
call conda activate procrastinate_env

echo 正在切换到项目目录 D:\procrastination_tool ...
d:
cd D:\procrastination_tool

echo 正在生成纯净的 requirements.txt ...
pip list --format=freeze > requirements.txt

echo 生成完成！正在安装 requirements.txt 中的依赖 ...
pip install -r requirements.txt

echo 全部完成！
pause
