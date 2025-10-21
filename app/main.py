from app.core.events import create_app

# 创建应用实例
app = create_app()


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to FastAPI + TortoiseORM Demo",
        "docs": "/docs",
        "health": "/api/health"
    }
