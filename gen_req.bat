@echo off
REM 一键生成干净的 requirements.txt（不含本地路径）
echo ========================================
echo  正在激活虚拟环境 procrastinate_env ...
call conda activate procrastinate_env

echo 正在切换到项目目录 D:\procrastination_tool ...
d:
cd D:\procrastination_tool

echo 正在生成纯净的 requirements.txt ...
pip list --format=freeze > requirements.txt

echo 完成！requirements.txt 已生成在当前目录。
echo 请用记事本打开检查，确保没有 "@ file:///" 路径。
pause
