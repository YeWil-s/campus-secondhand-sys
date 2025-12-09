# campus_second_trade
>>>>>>> 6af8660e057ec1952cab50f63da48f0d75ab9eab
# 校园二手商品交易系统

## 项目简介

本系统是一个基于 FastAPI + MySQL + Bootstrap 的校园二手商品交易平台，提供商品发布、浏览、搜索、购买及交易记录管理等功能。

## 技术栈

### 后端
- **FastAPI**: Web框架
- **SQLAlchemy**: ORM框架
- **PyMySQL**: MySQL数据库驱动
- **JWT**: 用户认证
- **Bcrypt**: 密码加密

### 前端
- **Bootstrap 5**: UI框架
- **原生JavaScript**: 业务逻辑
- **Bootstrap Icons**: 图标库

### 数据库
- **MySQL 8.0+**: 关系型数据库
- 使用视图保障数据安全性
- 合理创建索引优化查询性能

## 系统特点

1. **数据安全**: 用户只能查询视图数据，不能直接访问敏感信息
2. **价格处理**: 后端使用整数（分）存储价格，避免浮点数精度问题
3. **索引优化**: 针对常用查询场景创建复合索引
4. **RESTful API**: 符合REST规范的接口设计
5. **响应式设计**: 前端适配各种设备
6. **同步编程**: 使用同步数据库操作，便于理解和维护

## 环境要求

- Python 3.8+
- MySQL 8.0+
- 现代浏览器（Chrome、Firefox、Edge等）

## 数据库配置

系统默认使用以下数据库配置（可在 `backend/config.py` 修改）：

```python
DB_HOST: localhost
DB_PORT: 3306
DB_USER: root
DB_PASSWORD: 123456
DB_NAME: campus_second_hand
```

## 快速启动

### 方式一：使用虚拟环境（推荐）

**首次使用：**
```bash
# Windows用户双击运行
setup_env.bat

# 或者命令行运行
python -m venv venv
venv\Scripts\activate
cd backend
pip install -r requirements.txt
cd ..
```

**启动系统：**
```bash
# Windows用户双击运行
run_with_venv.bat

# 或者手动激活虚拟环境后运行
venv\Scripts\activate
python run.py
```

脚本会自动：
1. 激活虚拟环境
2. 检查并安装Python依赖
3. 检查MySQL连接
4. 创建数据库和表
5. 启动后端服务
6. 打开前端页面

### 方式二：不使用虚拟环境（不推荐）

```bash
# 直接运行启动脚本
python run.py
```

### 方式三：手动启动

1. **创建并激活虚拟环境**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# 或 source venv/bin/activate  # Linux/Mac
```

2. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

3. **初始化数据库**
```bash
cd backend
python init_db.py
cd ..
```

4. **启动后端**
```bash
cd backend
python main.py
# 或使用 uvicorn
uvicorn main:app --reload
```

5. **打开前端**

在浏览器中打开 `frontend/index.html`

## 功能说明

### 用户功能
- 用户注册与登录（JWT认证）
- 个人资料管理
- 发布商品
- 浏览和搜索商品
- 购买商品
- 查看交易记录

### 商品管理
- 发布商品（名称、描述、价格、分类）
- 编辑商品信息
- 删除商品（仅未售出商品）
- 商品状态管理（正常/锁定/已售出）

### 交易流程
1. 买家浏览商品
2. 创建订单（商品锁定）
3. 完成支付
4. 商品状态更新为已售出

## 数据库设计

### 核心表

1. **users** - 用户表
   - user_id: 用户ID（主键，10位）
   - username: 用户名（唯一）
   - password: 密码（加密）
   - phone: 手机号
   - campus_card: 校园卡号
   - created_at: 注册时间

2. **categories** - 商品分类表
   - id: 分类ID（主键，自增）
   - name: 分类名称（唯一）
   - description: 分类描述

3. **products** - 商品表
   - product_id: 商品ID（主键，12位）
   - name: 商品名称
   - description: 商品描述
   - price: 价格（整数，单位：分）
   - status: 状态（0-不可选，1-正常，2-已售出，3-已下架）
   - seller_id: 卖家ID（外键）
   - category_id: 分类ID（外键）
   - image_path: 图片路径
   - created_at: 发布时间

4. **transactions** - 交易记录表
   - transaction_id: 交易ID（主键，15位）
   - amount: 金额（整数，单位：分）
   - status: 状态（0-未支付，1-已成交）
   - buyer_id: 买家ID（外键）
   - seller_id: 卖家ID（外键）
   - product_id: 商品ID（外键）
   - created_at: 交易时间

### 视图设计

1. **view_products_available** - 可用商品视图
   - 仅显示状态为正常的商品
   - 包含卖家用户名和联系方式
   - 按发布时间降序排序

2. **view_user_products** - 用户商品视图
   - 显示用户发布的所有商品
   - 包含商品状态和交易次数

3. **view_user_transactions** - 用户交易视图
   - 显示用户的买卖交易记录
   - 智能显示交易对方信息

### 索引优化

1. **用户表索引**
   - idx_users_username: 用户名（唯一，优化登录）
   - idx_users_campus_card: 校园卡号（优化身份验证）
   - idx_users_phone: 手机号（优化信息核对）

2. **商品表索引**
   - idx_category: 分类ID（优化分类浏览）
   - idx_status: 商品状态（快速筛选）
   - idx_created_at: 发布时间降序（优化最新商品排序）
   - idx_name_price: 商品名称+价格（优化搜索）

3. **交易记录表索引**
   - idx_buyer_time: 买家ID+交易时间降序（优化买家记录查询）
   - idx_seller_time: 卖家ID+交易时间降序（优化卖家记录查询）
   - idx_product: 商品ID（优化商品交易查询）

## API文档

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

#### 认证接口
- POST `/api/auth/register` - 用户注册
- POST `/api/auth/login` - 用户登录

#### 用户接口
- GET `/api/users/profile` - 获取个人信息
- PUT `/api/users/profile` - 更新个人信息

#### 商品接口
- GET `/api/products/available` - 浏览可用商品
- GET `/api/products/my` - 我的商品
- POST `/api/products/` - 发布商品
- GET `/api/products/{product_id}` - 商品详情
- PUT `/api/products/{product_id}` - 更新商品
- DELETE `/api/products/{product_id}` - 删除商品
- GET `/api/products/categories/list` - 获取分类列表

#### 交易接口
- POST `/api/transactions/` - 创建订单
- PUT `/api/transactions/{transaction_id}/pay` - 完成支付
- GET `/api/transactions/my` - 我的交易记录
- GET `/api/transactions/{transaction_id}` - 交易详情

## 项目结构

```
sys/
├── backend/                 # 后端代码
│   ├── database/           # 数据库相关
│   │   ├── __init__.py    # 数据库连接
│   │   ├── models.py      # SQLAlchemy模型
│   │   └── schema.sql     # SQL建表脚本
│   ├── routers/            # 路由模块
│   │   ├── auth.py        # 认证路由
│   │   ├── products.py    # 商品路由
│   │   ├── transactions.py # 交易路由
│   │   └── users.py       # 用户路由
│   ├── schemas/            # Pydantic数据模型
│   │   ├── user.py
│   │   ├── product.py
│   │   └── transaction.py
│   ├── utils/              # 工具函数
│   │   ├── helpers.py     # 辅助函数
│   │   └── security.py    # 安全相关
│   ├── config.py           # 配置文件
│   ├── main.py             # FastAPI主程序
│   ├── init_db.py          # 数据库初始化
│   └── requirements.txt    # Python依赖
├── frontend/                # 前端代码
│   ├── css/
│   │   └── style.css      # 样式文件
│   ├── js/
│   │   ├── api.js         # API调用
│   │   └── app.js         # 应用逻辑
│   └── index.html          # 主页面
├── run.py                   # 启动脚本
└── README.md                # 项目说明
```

## 测试流程

1. **注册用户**
   - 注册用户A（卖家）
   - 注册用户B（买家）

2. **发布商品**
   - 用户A登录
   - 发布2-3个商品

3. **浏览购买**
   - 用户B登录
   - 搜索和浏览商品
   - 选择商品下单
   - 完成支付

4. **查看记录**
   - 用户A查看卖出记录
   - 用户B查看购买记录

## 注意事项

1. **价格处理**: 前端输入和显示使用元，后端存储使用分（整数）
2. **图片存储**: 当前版本图片存储在本地 `uploads` 文件夹
3. **数据安全**: 
   - 密码使用 bcrypt 加密
   - 用户只能查询视图数据
   - 实现了基本的权限控制
4. **索引使用**: 数据库查询已优化使用索引
5. **同步操作**: 数据库操作使用同步方式，便于理解

## 开发说明

### 添加新功能

1. 在 `database/models.py` 中定义模型
2. 在 `schemas/` 中定义请求/响应模型
3. 在 `routers/` 中实现业务逻辑
4. 在 `main.py` 中注册路由
5. 更新前端页面和API调用

### 数据库迁移

当模型变更时：
```python
# 删除旧数据库
DROP DATABASE campus_second_hand;

# 重新运行初始化
python init_db.py
```

## 许可证

MIT License

## 作者

校园二手交易系统开发组
=======
# campus_second_trade
>>>>>>> 6af8660e057ec1952cab50f63da48f0d75ab9eab
