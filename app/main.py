import sys
from pathlib import Path

# 确保从项目根目录导入模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from app.core.events import create_app
from app.schemas.common.response import success_response

# 创建应用实例
app = create_app()


@app.get("/")
async def root():
    """根路径"""
    return success_response(data="启动成功")


if __name__ == "__main__":
    """直接运行此文件启动服务"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
