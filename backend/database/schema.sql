-- 校园二手商品交易数据库系统
-- 创建数据库
CREATE DATABASE IF NOT EXISTS campus_second_hand DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE campus_second_hand;

-- 商品分类表
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '分类ID',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '分类名称',
    description VARCHAR(200) DEFAULT NULL COMMENT '分类描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(10) NOT NULL PRIMARY KEY COMMENT '用户ID，系统生成',
    username VARCHAR(20) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(64) NOT NULL COMMENT '密码，加密存储',
    phone VARCHAR(11) NOT NULL COMMENT '联系电话',
    campus_card VARCHAR(20) NOT NULL COMMENT '校园卡号/学号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 商品表
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(12) NOT NULL PRIMARY KEY COMMENT '商品ID，系统生成',
    name VARCHAR(20) NOT NULL COMMENT '商品名称',
    description TEXT DEFAULT NULL COMMENT '商品描述',
    price INT NOT NULL COMMENT '商品价格，单位：分',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '商品状态：0-不可选，1-正常状态，2-商品已售出，3-商品已送达',
    seller_id VARCHAR(10) NOT NULL COMMENT '卖家ID',
    category_id INT NOT NULL COMMENT '分类ID',
    image_path VARCHAR(255) DEFAULT NULL COMMENT '商品照片存储路径',
    INDEX idx_seller (seller_id),
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_name_price (name, price),
    FOREIGN KEY (seller_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 交易记录表
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(15) NOT NULL PRIMARY KEY COMMENT '交易ID，系统生成',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '交易时间',
    amount INT NOT NULL COMMENT '支付金额，单位：分',
    status TINYINT NOT NULL DEFAULT 0 COMMENT '交易状态：0-未完成支付，1-已成交',
    buyer_id VARCHAR(10) NOT NULL COMMENT '买家ID',
    seller_id VARCHAR(10) NOT NULL COMMENT '卖家ID',
    product_id VARCHAR(12) NOT NULL COMMENT '商品ID',
    INDEX idx_buyer_time (buyer_id, created_at DESC),
    INDEX idx_seller_time (seller_id, created_at DESC),
    INDEX idx_product (product_id),
    INDEX idx_status (status),
    FOREIGN KEY (buyer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易记录表';

-- 创建视图：商品浏览视图（只显示正常状态的商品）
CREATE OR REPLACE VIEW view_products_available AS
SELECT 
    p.product_id,
    p.name,
    p.description,
    p.price,
    p.created_at,
    p.image_path,
    u.username as seller_username,
    u.phone as seller_phone,
    c.name as category_name
FROM products p
JOIN users u ON p.seller_id = u.user_id
JOIN categories c ON p.category_id = c.id
WHERE p.status = 1
ORDER BY p.created_at DESC;

-- 创建视图：用户发布的商品视图
CREATE OR REPLACE VIEW view_user_products AS
SELECT 
    p.product_id,
    p.name,
    p.description,
    p.price,
    p.created_at,
    p.status,
    p.image_path,
    c.name as category_name,
    COUNT(t.transaction_id) as transaction_count
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.product_id, p.name, p.description, p.price, p.created_at, p.status, p.image_path, c.name;

-- 创建视图：用户交易记录视图
-- 注意：该视图为通用视图，实际使用时需要根据当前用户ID判断交易对象
CREATE OR REPLACE VIEW view_user_transactions AS
SELECT 
    t.transaction_id,
    t.created_at,
    t.amount,
    t.status,
    p.name as product_name,
    c.name as category_name,
    t.buyer_id,
    t.seller_id,
    t.product_id,
    u_buyer.username as buyer_username,
    u_seller.username as seller_username
FROM transactions t
JOIN users u_buyer ON t.buyer_id = u_buyer.user_id
JOIN users u_seller ON t.seller_id = u_seller.user_id
JOIN products p ON t.product_id = p.product_id
JOIN categories c ON p.category_id = c.id;

-- 插入默认商品分类
INSERT INTO categories (name, description) VALUES 
('电子产品', '手机、电脑、平板等电子设备'),
('书籍教材', '教材、参考书、课外读物等'),
('生活用品', '日常用品、宿舍用品等'),
('服装鞋包', '衣服、鞋子、包包等'),
('运动器材', '球类、健身器材等'),
('其他', '其他类型的商品');

-- 为用户表添加额外索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_campus_card ON users(campus_card);
CREATE INDEX idx_users_phone ON users(phone);