#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dogeAgent 启动脚本
"""
import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("🐶 dogeAgent 启动检查中...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ Python 版本过低，需要 3.8+")
        return False
    
    # 检查必要依赖
    required = ['langchain', 'langchain_nvidia_ai_endpoints', 'dotenv', 'pydantic']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"❌ 缺少依赖：{', '.join(missing)}")
        print("请运行：pip install -r requirements.txt")
        return False
    
    print("✅ 依赖检查通过")
    return True

def check_env():
    """检查环境变量"""
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print("⚠️  .env 文件不存在，从示例创建...")
        example = Path(__file__).parent / '.env.example'
        if example.exists():
            import shutil
            shutil.copy(example, env_file)
            print("✅ 已创建 .env 文件，请编辑填入 API Key")
        else:
            print("❌ 找不到 .env.example")
            return False
    
    # 检查 NVIDIA API Key
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    if not os.getenv('NVIDIA_API_KEY'):
        print("⚠️  NVIDIA_API_KEY 未配置，部分功能可能不可用")
    
    return True

def start_electron():
    """启动 Electron"""
    print("🚀 启动 Electron 主程序...")
    
    project_dir = Path(__file__).parent
    package_file = project_dir / 'package.json'
    
    if not package_file.exists():
        print("❌ 找不到 package.json")
        return False
    
    # 检查 node_modules
    node_modules = project_dir / 'node_modules'
    if not node_modules.exists():
        print("📦 安装 Node.js 依赖...")
        try:
            subprocess.run(['npm', 'install'], cwd=project_dir, check=True)
        except FileNotFoundError:
            print("❌ 未找到 Node.js/npm，请先安装 Node.js")
            return False
        except subprocess.CalledProcessError as e:
            print(f"❌ npm install 失败：{e}")
            return False
    
    # 使用 npm.cmd 而不是 npm (Windows 特定)
    npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'
    
    # 启动 Electron
    print("🎉 启动 dogeAgent...")
    print("   (如果窗口未出现，请检查系统托盘)")
    
    try:
        # Windows 上使用 npm.cmd
        subprocess.run([npm_cmd, 'start'], cwd=project_dir, check=True)
    except FileNotFoundError:
        print(f"❌ 找不到 {npm_cmd}，请确认 Node.js 已安装")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败：{e}")
        return False
    
    return True

def main():
    """主函数"""
    print("""
    ██████╗  ██████╗  ██████╗ ██╗   ██╗███████╗
    ██╔══██╗██╔═══██╗██╔════╝ ██║   ██║██╔════╝
    ██████╔╝██║   ██║██║  ███╗██║   ██║█████╗  
    ██╔══██╗██║   ██║██║   ██║██║   ██║██╔══╝  
    ██████╔╝╚██████╔╝╚██████╔╝╚██████╔╝███████╗
    ╚═════╝  ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝
    """)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 检查环境
    if not check_env():
        return 1
    
    # 启动 Electron
    if not start_electron():
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
