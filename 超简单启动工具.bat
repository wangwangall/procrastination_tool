@echo off
chcp 65001 >nul

REM 创建一个超简单的启动脚本，适合完全不懂技术的用户

:: 检查Python是否安装
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 未检测到Python
    echo 📥 正在为您打开Python下载页面...
    start https://www.python.org/downloads/
    echo.
    echo 📝 请下载并安装Python 3.8或以上版本，安装时务必勾选"Add Python to PATH"
    pause
    exit /b 1
)

:: 清理旧的运行窗口
if exist run_window.vbs del run_window.vbs

:: 创建VBS脚本，在后台运行Flask服务器
( echo Set WshShell = CreateObject("WScript.Shell")
  echo obj = WshShell.Run("cmd /c python app.py", 0, False)
  echo WScript.Sleep 3000
  echo WshShell.Run "start http://localhost:5001", 1, False
) > run_window.vbs

echo.
echo 🎯 拖延风险评估工具
setlocal enabledelayedexpansion
for /l %%i in (1,1,3) do (
    echo. 
    echo ⏳ 正在启动工具，请稍候...
    ping 127.0.0.1 -n 2 >nul
)

:: 运行VBS脚本
cscript //nologo run_window.vbs

echo.
echo 🎉 工具已成功启动！
echo 📱 电脑用户：浏览器已自动打开，可直接使用

echo.
echo 📡 手机访问指南：
echo 1. 确保手机和电脑连接同一WiFi网络

echo 2. 请查看电脑IP地址：
for /f "tokens=3 delims=: " %%i in ('netsh interface ip show address ^| findstr /i "ip地址" ^| findstr /v "127.0.0.1"') do (
    set IP=%%i
    echo    📍 您的电脑IP：!IP!
    echo 3. 手机浏览器输入：http://!IP!:5001
)

echo.
echo 🔒 安全说明：
echo - 本工具仅在您的本地网络内运行
- 数据保存在您的电脑本地，不会上传到公网
- 不需要任何账号密码
- 关闭工具后，数据将被安全保存

echo.
echo 💡 使用提示：
echo - 用完工具后，直接关闭浏览器即可
- 如需再次使用，重新双击本文件
- 数据保存在 data\risk_records.db 文件中

echo.
echo 📊 数据收集：
echo - 系统会自动收集评估数据用于优化模型
- 所有数据仅保存在您的电脑本地
- 数据完全隐私，不会泄露给任何人

echo.
echo 🎈 祝您使用愉快！
echo.
pause
