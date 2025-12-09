from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text
from typing import Optional, List
from datetime import datetime
from database import get_db
from database.models import User, Product, Transaction, Category
from schemas.transaction import TransactionCreate, TransactionResponse, TransactionSearch, TransactionListResponse
from utils.security import get_current_user
from utils.helpers import generate_transaction_id

router = APIRouter()

@router.post("/", response_model=TransactionResponse, summary="创建交易订单")
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建交易订单（下单）"""
    
    # 检查商品是否存在
    product = db.query(Product).filter(Product.product_id == transaction.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查商品状态
    if product.status != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品不可购买"
        )
    
    # 检查是否是自己购买自己的商品
    if product.seller_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能购买自己的商品"
        )
    
    # 检查商品是否已被下单
    existing_transaction = db.query(Transaction).filter(
        Transaction.product_id == transaction.product_id,
        Transaction.status == 0
    ).first()
    
    if existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品已被下单，请等待卖家处理"
        )
    
    # 创建交易记录
    transaction_id = generate_transaction_id()
    db_transaction = Transaction(
        transaction_id=transaction_id,
        amount=product.price,
        status=0,  # 未完成支付
        buyer_id=current_user.user_id,
        seller_id=product.seller_id,
        product_id=transaction.product_id
    )
    
    db.add(db_transaction)
    
    # 锁定商品（更新状态为0-不可选）
    product.status = 0
    db.commit()
    db.refresh(db_transaction)
    
    # 获取交易详情
    result = db.execute(text("""
        SELECT 
            t.transaction_id,
            t.created_at,
            t.amount,
            t.status,
            t.buyer_id,
            t.seller_id,
            t.product_id,
            CASE 
                WHEN t.buyer_id = :user_id THEN u_seller.username
                WHEN t.seller_id = :user_id THEN u_buyer.username
                ELSE '未知用户'
            END as counterparty_username,
            CASE 
                WHEN t.buyer_id = :user_id THEN '卖家'
                WHEN t.seller_id = :user_id THEN '买家'
                ELSE '未知'
            END as counterparty_role,
            p.name as product_name,
            c.name as category_name
        FROM transactions t
        JOIN users u_buyer ON t.buyer_id = u_buyer.user_id
        JOIN users u_seller ON t.seller_id = u_seller.user_id
        JOIN products p ON t.product_id = p.product_id
        JOIN categories c ON p.category_id = c.id
        WHERE t.transaction_id = :transaction_id
    """), {"transaction_id": transaction_id, "user_id": current_user.user_id})
    
    transaction_data = result.first()
    transaction_dict = transaction_data._asdict()
    
    return TransactionResponse(**transaction_dict)

@router.put("/{transaction_id}/pay", response_model=TransactionResponse, summary="完成支付")
async def complete_payment(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """完成支付"""
    
    # 获取交易记录
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易记录不存在"
        )
    
    # 检查权限（只有买家可以支付）
    if transaction.buyer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此交易"
        )
    
    # 检查交易状态
    if transaction.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="交易状态不正确"
        )
    
    # 更新交易状态
    transaction.status = 1  # 已成交
    
    # 更新商品状态
    product = db.query(Product).filter(Product.product_id == transaction.product_id).first()
    if product:
        product.status = 2  # 商品已售出
    
    db.commit()
    db.refresh(transaction)
    
    # 获取更新后的交易详情
    result = db.execute(text("""
        SELECT 
            t.transaction_id,
            t.created_at,
            t.amount,
            t.status,
            t.buyer_id,
            t.seller_id,
            t.product_id,
            CASE 
                WHEN t.buyer_id = :user_id THEN u_seller.username
                WHEN t.seller_id = :user_id THEN u_buyer.username
                ELSE '未知用户'
            END as counterparty_username,
            CASE 
                WHEN t.buyer_id = :user_id THEN '卖家'
                WHEN t.seller_id = :user_id THEN '买家'
                ELSE '未知'
            END as counterparty_role,
            p.name as product_name,
            c.name as category_name
        FROM transactions t
        JOIN users u_buyer ON t.buyer_id = u_buyer.user_id
        JOIN users u_seller ON t.seller_id = u_seller.user_id
        JOIN products p ON t.product_id = p.product_id
        JOIN categories c ON p.category_id = c.id
        WHERE t.transaction_id = :transaction_id
    """), {"transaction_id": transaction_id, "user_id": current_user.user_id})
    
    transaction_data = result.first()
    transaction_dict = transaction_data._asdict()
    
    return TransactionResponse(**transaction_dict)


@router.get("/my", response_model=TransactionListResponse, summary="我的交易记录")
async def get_my_transactions(
        status: Optional[int] = Query(None, ge=0, le=1, description="交易状态"),
        category_id: Optional[int] = Query(None, gt=0, description="分类ID"),
        start_date: Optional[datetime] = Query(None, description="开始日期"),
        end_date: Optional[datetime] = Query(None, description="结束日期"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取当前用户的交易记录（包含商品图片URL）"""

    # 构建查询条件
    conditions = [
        or_(
            Transaction.buyer_id == current_user.user_id,
            Transaction.seller_id == current_user.user_id
        )
    ]

    if status is not None:
        conditions.append(Transaction.status == status)

    if start_date:
        conditions.append(Transaction.created_at >= start_date)

    if end_date:
        conditions.append(Transaction.created_at <= end_date)

    # 从products表获取image_path，构建完整图片URL
    query = db.execute(text("""
        SELECT SQL_CALC_FOUND_ROWS 
            t.transaction_id,
            t.created_at,
            t.amount,
            t.status,
            t.buyer_id,
            t.seller_id,
            t.product_id,
            CASE 
                WHEN u_buyer.user_id = :user_id AND u_buyer.user_id = t.buyer_id THEN u_seller.username
                WHEN u_seller.user_id = :user_id AND u_seller.user_id = t.seller_id THEN u_buyer.username
                ELSE '未知用户'
            END as counterparty_username,
            CASE 
                WHEN u_buyer.user_id = :user_id AND u_buyer.user_id = t.buyer_id THEN '卖家'
                WHEN u_seller.user_id = :user_id AND u_seller.user_id = t.seller_id THEN '买家'
                ELSE '未知'
            END as counterparty_role,
            p.name as product_name,
            c.name as category_name,
            p.image_path  -- 从products表获取图片路径
        FROM transactions t
        JOIN users u_buyer ON t.buyer_id = u_buyer.user_id
        JOIN users u_seller ON t.seller_id = u_seller.user_id
        JOIN products p ON t.product_id = p.product_id  -- 关联商品表
        JOIN categories c ON p.category_id = c.id
        WHERE (t.buyer_id = :user_id OR t.seller_id = :user_id)
    """ + (f" AND t.status = {status}" if status is not None else "") +
                            (f" AND t.created_at >= '{start_date}'" if start_date else "") +
                            (f" AND t.created_at <= '{end_date}'" if end_date else "") +
                            (f" AND c.id = {category_id}" if category_id else "") +
                            f" ORDER BY t.created_at DESC LIMIT {(page - 1) * page_size}, {page_size}"),
                       {"user_id": current_user.user_id})

    transactions = query.fetchall()

    # 获取总数
    total_query = db.execute(text("SELECT FOUND_ROWS()"))
    total = total_query.scalar()

    transaction_list = []
    # 图片基础URL（与前端访问路径保持一致）
    IMAGE_BASE_URL = "http://localhost:8000/api/uploads/"

    for transaction in transactions:
        # 拼接完整的商品图片URL
        product_image_url = None
        if transaction.image_path:  # 使用products表中的image_path字段
            product_image_url = f"{IMAGE_BASE_URL}{transaction.image_path}"

        transaction_dict = {
            "transaction_id": transaction.transaction_id,
            "created_at": transaction.created_at,
            "amount": transaction.amount,
            "status": transaction.status,
            "buyer_id": transaction.buyer_id,
            "seller_id": transaction.seller_id,
            "product_id": transaction.product_id,
            "counterparty_username": transaction.counterparty_username,
            "counterparty_role": transaction.counterparty_role,
            "product_name": transaction.product_name,
            "category_name": transaction.category_name,
            "product_image_url": product_image_url  # 包含完整图片URL
        }
        transaction_list.append(TransactionResponse(** transaction_dict))

    total_pages = (total + page_size - 1) // page_size

    return TransactionListResponse(
        transactions=transaction_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{transaction_id}", response_model=TransactionResponse, summary="交易详情")
async def get_transaction_detail(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取交易详情"""
    
    # 检查用户是否有权限查看此交易
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        or_(
            Transaction.buyer_id == current_user.user_id,
            Transaction.seller_id == current_user.user_id
        )
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易记录不存在或无权限查看"
        )
    
    # 获取交易详情
    result = db.execute(text("""
        SELECT 
            t.transaction_id,
            t.created_at,
            t.amount,
            t.status,
            t.buyer_id,
            t.seller_id,
            t.product_id,
            CASE 
                WHEN u_buyer.user_id = :user_id AND u_buyer.user_id = t.buyer_id THEN u_seller.username
                WHEN u_seller.user_id = :user_id AND u_seller.user_id = t.seller_id THEN u_buyer.username
                ELSE '未知用户'
            END as counterparty_username,
            CASE 
                WHEN u_buyer.user_id = :user_id AND u_buyer.user_id = t.buyer_id THEN '卖家'
                WHEN u_seller.user_id = :user_id AND u_seller.user_id = t.seller_id THEN '买家'
                ELSE '未知'
            END as counterparty_role,
            p.name as product_name,
            c.name as category_name
        FROM transactions t
        JOIN users u_buyer ON t.buyer_id = u_buyer.user_id
        JOIN users u_seller ON t.seller_id = u_seller.user_id
        JOIN products p ON t.product_id = p.product_id
        JOIN categories c ON p.category_id = c.id
        WHERE t.transaction_id = :transaction_id
    """), {"transaction_id": transaction_id, "user_id": current_user.user_id})
    
    transaction_data = result.first()
    if not transaction_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易记录不存在"
        )
    
    transaction_dict = transaction_data._asdict()
    
    return TransactionResponse(**transaction_dict)