#!/usr/bin/env python3
"""
超简单启动工具 - 拖延风险评估工具
专为不懂技术的用户设计，双击即可使用
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_welcome():
    """打印欢迎信息"""
    print("\n" + "="*50)
    print("🎯 拖延风险评估工具")
    print("="*50)
    print("专为不懂技术的用户设计")
    print("双击即可使用，无需任何配置")
    print("="*50)

def check_python():
    """检查Python是否安装"""
    print("\n🔍 正在检查Python环境...")
    try:
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Python版本：{result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Python未正确安装")
        return False
    except FileNotFoundError:
        print("❌ 未检测到Python")
        return False

def install_dependencies():
    """安装依赖"""
    print("\n📦 正在安装必要的依赖...")
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("⚠️  找不到requirements.txt文件")
        print("📝 将尝试手动安装所需依赖...")
        dependencies = [
            "flask",
            "flask-cors",
            "scikit-learn",
            "numpy",
            "pandas"
        ]
        for dep in dependencies:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"✅ 已安装：{dep}")
            except subprocess.CalledProcessError:
                print(f"⚠️  安装{dep}失败，将尝试继续")
        return
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ 所有依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  依赖安装失败：{e.stderr[:100]}...")
        print("📝 将尝试继续运行...")

def start_server():
    """启动Flask服务器"""
    print("\n🚀 正在启动评估工具...")
    try:
        # 启动Flask服务器
        server_process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查服务器是否正在运行
        if server_process.poll() is not None:
            stderr = server_process.stderr.read()
            print(f"❌ 服务器启动失败：{stderr[:100]}...")
            return None
        
        print("✅ 服务器启动成功！")
        return server_process
    except Exception as e:
        print(f"❌ 启动服务器时出错：{e}")
        return None

def open_browser_window():
    """打开浏览器窗口"""
    url = "http://localhost:5001"
    print(f"\n🌐 正在打开浏览器：{url}")
    try:
        webbrowser.open(url)
        print("✅ 浏览器已打开")
        return url
    except Exception as e:
        print(f"⚠️  浏览器打开失败：{e}")
        print(f"📝 请手动在浏览器中输入：{url}")
        return url

def get_local_ip():
    """获取本地IP地址"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "无法获取IP地址"

def print_usage_guide(local_url):
    """打印使用指南"""
    print("\n" + "="*50)
    print("📖 使用指南")
    print("="*50)
    
    print("\n💻 电脑用户：")
    print(f"   浏览器已自动打开，可直接使用")
    print(f"   地址：{local_url}")
    
    print("\n📱 手机用户：")
    local_ip = get_local_ip()
    print(f"   1. 确保手机和电脑连接同一WiFi网络")
    print(f"   2. 您的电脑IP地址：{local_ip}")
    print(f"   3. 在手机浏览器中输入：http://{local_ip}:5001")
    print(f"   4. 即可在手机上使用评估工具")
    
    print("\n🔒 安全说明：")
    print("   ✅ 本工具仅在您的本地网络内运行")
    print("   ✅ 所有数据保存在您的电脑本地")
    print("   ✅ 不会上传任何数据到公网")
    print("   ✅ 不需要账号密码，完全隐私")
    
    print("\n💡 使用提示：")
    print("   ✅ 用完后直接关闭浏览器即可")
    print("   ✅ 数据自动保存在 data/risk_records.db 文件中")
    print("   ✅ 如需再次使用，重新双击本文件")
    print("   ✅ 关闭此窗口将停止服务器")
    
    print("\n📊 数据收集：")
    print("   ✅ 系统会自动收集评估数据")
    print("   ✅ 数据仅用于优化评估模型")
    print("   ✅ 所有数据仅保存在您的电脑上")
    print("   ✅ 数据完全隐私，不会泄露给任何人")
    
    print("\n" + "="*50)
    print("🎈 祝您使用愉快！")
    print("="*50)
    print("\n按任意键关闭此窗口（将停止服务器）...")

def main():
    """主函数"""
    print_welcome()
    
    # 检查Python
    if not check_python():
        print("\n📥 正在打开Python下载页面...")
        webbrowser.open("https://www.python.org/downloads/")
        print("\n📝 请下载并安装Python 3.8或以上版本")
        print("   安装时务必勾选\"Add Python to PATH\"")
        input("\n安装完成后，按任意键重新运行本程序...")
        return
    
    # 安装依赖
    install_dependencies()
    
    # 启动服务器
    server_process = start_server()
    if not server_process:
        input("\n按任意键退出...")
        return
    
    # 打开浏览器
    local_url = open_browser_window()
    
    # 显示使用指南
    print_usage_guide(local_url)
    
    # 等待用户输入，保持窗口打开
    try:
        input()
    except KeyboardInterrupt:
        pass
    
    # 停止服务器
    print("\n🛑 正在停止服务器...")
    server_process.terminate()
    print("✅ 服务器已停止")
    print("\n再见！")
    time.sleep(1)

if __name__ == "__main__":
    main()
