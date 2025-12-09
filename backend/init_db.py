#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库和初始化数据
"""

import pymysql
from config import settings

def create_database():
    """创建数据库"""
    try:
        # 连接MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✓ 数据库 '{settings.DB_NAME}' 创建成功")
        
        connection.commit()
        connection.close()
        
    except Exception as e:
        print(f"✗ 创建数据库失败：{e}")
        return False
    
    return True

def execute_schema():
    """执行数据库结构脚本"""
    try:
        # 连接到指定数据库
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset='utf8mb4'
        )
        
        # 读取并执行schema.sql文件
        import os
        schema_file = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        with connection.cursor() as cursor:
            # 执行SQL语句
            for sql_statement in sql_content.split(';'):
                if sql_statement.strip():
                    cursor.execute(sql_statement)
        
        connection.commit()
        connection.close()
        print("✓ 数据库表结构创建成功")
        
    except Exception as e:
        print(f"✗ 执行数据库脚本失败：{e}")
        return False
    
    return True

def check_data():
    """检查数据是否正确初始化"""
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 检查分类数量
            cursor.execute("SELECT COUNT(*) FROM categories")
            category_count = cursor.fetchone()[0]
            
            # 检查表是否存在
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
        
        connection.close()
        
        print(f"✓ 数据库检查完成")
        print(f"  - 商品分类数量：{category_count}")
        print(f"  - 数据表数量：{len(tables)}")
        print(f"  - 表列表：{', '.join(tables)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据检查失败：{e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("数据库初始化脚本")
    print("=" * 50)
    
    # 创建数据库
    print("\n1. 创建数据库")
    print("-" * 20)
    if not create_database():
        return
    
    # 执行数据库结构
    print("\n2. 创建表结构")
    print("-" * 20)
    if not execute_schema():
        return
    
    # 检查数据
    print("\n3. 数据检查")
    print("-" * 20)
    if not check_data():
        return
    
    print("\n" + "=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)
    print("\n数据库信息：")
    print(f"- 主机：{settings.DB_HOST}:{settings.DB_PORT}")
    print(f"- 数据库名：{settings.DB_NAME}")
    print(f"- 用户名：{settings.DB_USER}")
    print("\n现在可以启动后端服务了！")

if __name__ == "__main__":
    main()