@echo off
chcp 65001 >nul
echo.
echo =========================================
echo 🎯 拖延风险评估工具启动器
echo =========================================
echo.
echo 正在准备启动应用...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 未检测到Python，请先安装Python 3.8或以上版本
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查pip是否可用
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ pip不可用，请检查Python安装
    pause
    exit /b 1
)

:: 显示启动选项
echo =========================================
echo 🚀 启动选项
echo =========================================
echo 1. 本地模式（仅本地和局域网可访问）
echo 2. 公网模式（手机和外部用户均可访问，需要网络）
echo 3. 调试模式（开发人员使用）
echo =========================================
echo.
set /p choice=请选择启动模式 (1-3): 

:: 根据选择启动应用
if %choice% == 1 (
    echo.
    echo 📱 正在启动本地模式...
    echo 💡 提示：本地用户可直接在浏览器中使用
    echo 💡 手机用户需连接同一WiFi网络，使用局域网地址访问
    echo.
    python start_app.py
) else if %choice% == 2 (
    echo.
    echo 🌍 正在启动公网模式...
    echo 💡 提示：将生成公网URL，手机用户可直接访问
    echo 💡 所有访问数据将自动记录到本地数据库
    echo.
    python start_app.py --ngrok
) else if %choice% == 3 (
    echo.
    echo 🔧 正在启动调试模式...
    echo 💡 提示：仅开发人员使用，包含详细日志
    echo.
    python start_app.py --debug
) else (
    echo.
    echo ❌ 无效的选择，请重新运行
    pause
    exit /b 1
)

pause
