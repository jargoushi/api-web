from app.core.events import create_app
from app.schemas.response import success_response

# 创建应用实例
app = create_app()


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return success_response(data="启动成功")
