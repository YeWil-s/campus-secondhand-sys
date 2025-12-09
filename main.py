from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import mysql.connector
from mysql.connector import Error

# 1. 初始化FastAPI应用
app = FastAPI(title="校园二手商品交易系统", version="1.0")
# 配置前端模板路径（关联templates文件夹）
templates = Jinja2Templates(directory="templates")

# 2. 数据库配置（需替换为你的本地数据库实际信息）
DB_CONFIG = {
    "host": "localhost",       # 本地数据库地址（默认localhost）
    "user": "root",            # 数据库用户名（如root）
    "password": "123456",# 数据库密码（替换为你的实际密码，如123456）
    "port": "3306",            # 数据库端口（默认3306）
    "database": "campus_secondhand_trade"  # 已创建好的数据库名（匹配文档）
}

# 3. 数据库连接函数（验证连接有效性）
def test_db_connection():
    """测试数据库连接是否正常"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ 数据库连接成功！")
            print(f"当前数据库：{DB_CONFIG['database']}")
            return True
    except Error as e:
        print(f"❌ 数据库连接失败：{e}")
        print("请检查DB_CONFIG中的用户名、密码、数据库名是否正确！")
        return False
    finally:
        # 关闭连接（仅测试用，实际请求时按需创建连接）
        if connection and connection.is_connected():
            connection.close()

# 启动时自动测试数据库连接
test_db_connection()

# 4. 路由配置（页面跳转逻辑）
# 首页路由：默认跳转至登录页
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/login")  # 重定向到登录页

# 登录页面路由：返回登录UI
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",  # 关联login.html模板
        {"request": request, "title": "用户登录 - 校园二手交易系统"}  # 传递页面标题参数
    )

# 注册页面路由：返回注册UI
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",  # 关联register.html模板
        {"request": request, "title": "用户注册 - 校园二手交易系统"}
    )

# 主页面路由：登录/注册后跳转的目标页
@app.get("/index", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse(
        "index.html",  # 关联index.html模板
        {"request": request, "title": "校园二手商品交易系统 - 主页"}
    )

@app.post("/login/action")
async def login_action():
    # 303 See Other：强制用 GET 方法跳转
    return RedirectResponse(url="/index", status_code=303)

@app.post("/register/action")
async def register_action():
    return RedirectResponse(url="/index", status_code=303)