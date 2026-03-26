#!/usr/bin/env python3
"""
拖延风险评估工具启动脚本
功能：
1. 检查并安装依赖
2. 启动Flask服务器
3. 提供内网穿透选项，方便外部用户访问
4. 显示访问URL和使用说明
5. 支持后台运行和日志查看
"""

import os
import sys
import subprocess
import time
import webbrowser
import argparse
from pathlib import Path

def check_python_version():
    """检查Python版本是否符合要求"""
    if sys.version_info < (3, 8):
        print("❌ Python版本要求3.8或以上，请升级Python版本")
        sys.exit(1)
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")

def install_dependencies():
    """安装项目依赖"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ 找不到requirements.txt文件")
        sys.exit(1)
    
    print("📦 正在安装依赖...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt"
        ])
        print("✅ 依赖安装完成")
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败，请检查网络或权限")
        sys.exit(1)

def check_port_available(port):
    """检查端口是否可用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0

def get_local_ip():
    """获取本地IP地址"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def start_flask_server(port=5001, debug=False):
    """启动Flask服务器"""
    if not check_port_available(port):
        print(f"❌ 端口{port}已被占用，请使用其他端口")
        sys.exit(1)
    
    print(f"🚀 正在启动Flask服务器...")
    print(f"📡 服务器将运行在: http://localhost:{port}")
    print(f"🌐 本地网络访问: http://{get_local_ip()}:{port}")
    
    # 启动Flask应用
    env = os.environ.copy()
    env["FLASK_APP"] = "app.py"
    env["FLASK_RUN_PORT"] = str(port)
    
    if debug:
        cmd = [sys.executable, "-m", "flask", "run", "--debug"]
    else:
        cmd = [sys.executable, "app.py"]
    
    try:
        server_process = subprocess.Popen(cmd, env=env)
        return server_process
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

def install_ngrok():
    """安装ngrok内网穿透工具"""
    print("🔗 正在安装ngrok内网穿透工具...")
    try:
        if sys.platform.startswith("win32"):
            # Windows系统
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "pyngrok"
            ])
        else:
            # Linux/Mac系统
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "pyngrok"
            ])
        print("✅ ngrok安装完成")
    except subprocess.CalledProcessError:
        print("❌ ngrok安装失败，跳过内网穿透功能")
        return False
    return True

def start_ngrok(port):
    """启动ngrok内网穿透"""
    try:
        from pyngrok import ngrok
        
        # 检查ngrok是否已配置认证令牌
        try:
            tunnels = ngrok.get_tunnels()
        except:
            print("⚠️  ngrok未配置认证令牌，仅能使用临时隧道")
            print("📝 如需稳定隧道，请访问 https://dashboard.ngrok.com/get-started/your-authtoken 获取认证令牌")
            print("📝 然后运行: ngrok config add-authtoken YOUR_AUTHTOKEN")
        
        # 启动隧道
        http_tunnel = ngrok.connect(port, proto="http")
        print(f"🌍 内网穿透URL: {http_tunnel.public_url}")
        print(f"📱 手机用户可直接访问此URL使用工具")
        print(f"📊 所有访问数据将自动记录到本地数据库")
        return http_tunnel
    except ImportError:
        print("⚠️  pyngrok未安装，跳过内网穿透功能")
        return None
    except Exception as e:
        print(f"⚠️  内网穿透启动失败: {e}")
        return None

def open_browser(url):
    """打开浏览器"""
    try:
        webbrowser.open(url)
        print(f"🌐 浏览器已打开: {url}")
    except Exception as e:
        print(f"⚠️  浏览器打开失败: {e}")

def print_usage(local_url, lan_url, public_url=None):
    """打印使用说明"""
    print("\n" + "="*60)
    print("🎉 拖延风险评估工具已启动成功！")
    print("="*60)
    print(f"💻 本地访问地址: {local_url}")
    print(f"📡 局域网访问地址: {lan_url}")
    if public_url:
        print(f"🌍 公网访问地址: {public_url}")
    print("="*60)
    print("📱 使用说明:")
    print("1. 本地用户直接访问上述URL即可使用")
    print("2. 手机用户可扫描二维码或直接输入URL")
    print("3. 所有评估数据将自动保存到本地数据库")
    print("4. 按 Ctrl+C 停止服务")
    print("="*60)
    print("📊 数据收集说明:")
    print("- 系统会自动收集用户评估数据")
    print("- 数据保存在 data/risk_records.db 文件中")
    print("- 可通过 API 导出脱敏数据用于分析")
    print("="*60)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="拖延风险评估工具启动脚本")
    parser.add_argument("--port", type=int, default=5001, help="服务器端口")
    parser.add_argument("--no-deps", action="store_true", help="跳过依赖安装")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--debug", action="store_true", help="开启调试模式")
    parser.add_argument("--ngrok", action="store_true", help="启用ngrok内网穿透")
    args = parser.parse_args()
    
    print("🎯 拖延风险评估工具启动脚本")
    print("📅 " + time.strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    if not args.no_deps:
        install_dependencies()
    
    # 启动Flask服务器
    server_process = start_flask_server(args.port, args.debug)
    
    # 等待服务器启动
    time.sleep(2)
    
    # 构建访问URL
    local_url = f"http://localhost:{args.port}"
    lan_url = f"http://{get_local_ip()}:{args.port}"
    public_url = None
    
    # 启动内网穿透
    ngrok_tunnel = None
    if args.ngrok:
        if install_ngrok():
            ngrok_tunnel = start_ngrok(args.port)
            if ngrok_tunnel:
                public_url = ngrok_tunnel.public_url
    
    # 打开浏览器
    if not args.no_browser:
        open_browser(local_url)
    
    # 打印使用说明
    print_usage(local_url, lan_url, public_url)
    
    # 保持脚本运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        server_process.terminate()
        if ngrok_tunnel:
            from pyngrok import ngrok
            ngrok.disconnect(ngrok_tunnel.public_url)
        print("✅ 服务已停止")
        sys.exit(0)

if __name__ == "__main__":
    main()
