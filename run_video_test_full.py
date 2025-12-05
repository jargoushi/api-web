"""
视频生成服务完整测试运行脚本
"""
import sys
import os

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行完整测试
from app.test.test_video_generation import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
