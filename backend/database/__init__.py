from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# 数据库引擎配置
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # 关闭SQL日志以减少输出
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False
    }
)

# 添加连接事件处理
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if 'mysql' in str(type(dbapi_connection)):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET sql_mode='STRICT_TRANS_TABLES'")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建数据库函数
def create_tables():
    Base.metadata.create_all(bind=engine)

# 测试数据库连接
def test_connection():
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False