"""
视频生成服务示例运行脚本
"""
import sys
import os

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行示例
from examples.video_generation_example import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
