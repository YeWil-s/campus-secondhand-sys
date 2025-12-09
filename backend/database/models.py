from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, DateTime, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(10), primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    phone = Column(String(11), nullable=False)
    campus_card = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())
    
    # 关系
    products_sold = relationship("Product", foreign_keys="Product.seller_id", back_populates="seller")
    transactions_as_buyer = relationship("Transaction", foreign_keys="Transaction.buyer_id", back_populates="buyer")
    transactions_as_seller = relationship("Transaction", foreign_keys="Transaction.seller_id", back_populates="seller")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(200))
    created_at = Column(TIMESTAMP, default=func.now())
    
    # 关系
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(String(12), primary_key=True)
    name = Column(String(20), nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)  # 价格，单位：分
    created_at = Column(TIMESTAMP, default=func.now())
    status = Column(SmallInteger, nullable=False, default=1)  # 0-不可选，1-正常，2-已售出，3-已送达
    seller_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    image_path = Column(String(255))
    
    # 关系
    seller = relationship("User", foreign_keys=[seller_id], back_populates="products_sold")
    category = relationship("Category", back_populates="products")
    transactions = relationship("Transaction", back_populates="product")

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(String(15), primary_key=True)
    created_at = Column(TIMESTAMP, default=func.now())
    amount = Column(Integer, nullable=False)  # 支付金额，单位：分
    status = Column(SmallInteger, nullable=False, default=0)  # 0-未支付，1-已成交
    buyer_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    seller_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    product_id = Column(String(12), ForeignKey("products.product_id"), nullable=False)
    
    # 关系
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="transactions_as_buyer")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="transactions_as_seller")
    product = relationship("Product", back_populates="transactions")