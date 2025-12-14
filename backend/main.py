from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from database import engine, Base, test_connection, create_tables
from routers import auth, products, users, transactions, upload

# ----------------------------------------------------------------
# 【修正】先定义 app 实例，然后才能使用 @app.on_event
# ----------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="校园二手商品交易系统API"
)

# ----------------------------------------------------------------
# 测试数据库连接和创建表 (使用 FastAPI 的 startup 事件)
# ----------------------------------------------------------------
@app.on_event("startup")
def startup_db_init():
    print("正在连接数据库...")
    if not test_connection():
        print("数据库连接失败，请检查MySQL配置")
        # 推荐使用 HTTPException 或直接 raise RuntimeError
        raise RuntimeError("Database connection failed!") 

    print("正在创建数据库表...")
    create_tables()
    print("数据库初始化完成")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(products.router, prefix="/api/products", tags=["商品"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["交易"])
app.include_router(upload.router, prefix="/api", tags=["文件上传"])

@app.get("/")
async def root():
    return {"message": "校园二手商品交易系统API", "version": settings.VERSION}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run 在这里运行，并导入上面的 app 实例
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)