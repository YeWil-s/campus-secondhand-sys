from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text
from typing import Optional, List
from database import get_db
from database.models import User, Product, Category, Transaction # 确保导入 Transaction
from schemas.product import ProductCreate, ProductResponse, ProductUpdate, ProductSearch, ProductListResponse
from utils.security import get_current_user
from utils.helpers import generate_product_id

router = APIRouter()

@router.post("/create", response_model=ProductResponse, summary="发布商品")
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布新商品"""
    
    try:
        # 检查分类是否存在
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="商品分类不存在"
            )
        
        # 创建商品
        product_id = generate_product_id()
        db_product = Product(
            product_id=product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            seller_id=current_user.user_id,
            category_id=product.category_id,
            image_path=product.image_path,
            status=1  # 正常状态
        )
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        # 关联查询返回完整信息
        result = db.query(
            Product.product_id,
            Product.name,
            Product.description,
            Product.price,
            Product.created_at,
            Product.status,
            Product.seller_id,
            Product.category_id,
            Product.image_path,
            User.username.label("seller_username"),
            User.phone.label("seller_phone"),
            Category.name.label("category_name")
        ).join(User, Product.seller_id == User.user_id)\
         .join(Category, Product.category_id == Category.id)\
         .filter(Product.product_id == product_id)\
         .first()
        
        return ProductResponse(**result._asdict())
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"创建商品失败: {e}")
        print(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建商品失败: {str(e)}"
        )


# ====================================================
# 2. 浏览可用商品 (GET /available)
# ====================================================
@router.get("/available", response_model=ProductListResponse, summary="浏览可用商品")
async def get_available_products(
        keyword: Optional[str] = Query(None, description="搜索关键词"),
        category_id: Optional[int] = Query(None, description="分类ID"),
        min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
        max_price: Optional[float] = Query(None, ge=0, description="最高价格"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
        sort_by: str = Query("newest", description="排序方式: newest/price_asc/price_desc"), 
        current_user: Optional[User] = Depends(get_current_user), 
        db: Session = Depends(get_db)
):
    """获取可购买的商品列表（只显示状态为1的商品，并排除当前用户自己发布的商品）"""
    min_price_fen = round(min_price * 100) if min_price is not None else None
    max_price_fen = round(max_price * 100) if max_price is not None else None

    sql_params = {
        "status": 1,
        "offset": (page - 1) * page_size,
        "limit": page_size
    }

    where_conditions = ["p.status = :status"]

    if current_user:
        where_conditions.append("p.seller_id != :exclude_seller_id")
        sql_params["exclude_seller_id"] = current_user.user_id 

    if keyword:
        where_conditions.append("p.name LIKE :keyword")
        sql_params["keyword"] = f"%{keyword}%"
    if category_id:
        where_conditions.append("p.category_id = :category_id")
        sql_params["category_id"] = category_id
    if min_price_fen is not None:
        where_conditions.append("p.price >= :min_price")
        sql_params["min_price"] = min_price_fen
    if max_price_fen is not None:
        where_conditions.append("p.price <= :max_price")
        sql_params["max_price"] = max_price_fen

    where_clause = ' AND '.join(where_conditions)
    
    order_by_clause = "p.created_at DESC" 
    if sort_by == "price_asc":
        order_by_clause = "p.price ASC, p.created_at DESC"
    elif sort_by == "price_desc":
        order_by_clause = "p.price DESC, p.created_at DESC"
    elif sort_by == "newest":
        order_by_clause = "p.created_at DESC"
        
    count_sql = f"""
        SELECT COUNT(p.product_id) 
        FROM products p
        WHERE {where_clause}
    """
    count_params = {k: v for k, v in sql_params.items() if k not in ['offset', 'limit']}
    total = db.execute(text(count_sql), count_params).scalar()
    
    sql = f"""
        SELECT 
            p.product_id,
            p.name,
            p.description,
            p.price,
            p.created_at,
            p.status,
            p.seller_id,
            p.category_id,
            p.image_path,
            u.username as seller_username,
            u.phone as seller_phone,
            c.name as category_name
        FROM products p
        JOIN users u ON p.seller_id = u.user_id
        JOIN categories c ON p.category_id = c.id
        WHERE {where_clause}
        ORDER BY {order_by_clause} 
        LIMIT :limit OFFSET :offset
    """
    
    products = db.execute(text(sql), sql_params).fetchall()

    product_list = []
    for product in products:
        product_dict = {
            "product_id": product.product_id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "created_at": product.created_at,
            "status": product.status, 
            "seller_id": product.seller_id,
            "category_id": product.category_id,
            "image_path": product.image_path,
            "seller_username": product.seller_username,
            "seller_phone": product.seller_phone,
            "category_name": product.category_name
        }
        product_list.append(ProductResponse(**product_dict))

    total_pages = (total + page_size - 1) // page_size if total else 0

    return ProductListResponse(
        products=product_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

# ====================================================
# 3. 我的商品 (GET /my)
# ====================================================
@router.get("/my", response_model=ProductListResponse, summary="我的商品")
async def get_my_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我发布的商品"""
    
    query = db.query(
        Product.product_id,
        Product.name,
        Product.description,
        Product.price,
        Product.created_at,
        Product.status,
        Product.seller_id,
        Product.category_id,
        Product.image_path,
        Category.name.label("category_name")
    ).join(Category, Product.category_id == Category.id)\
     .filter(Product.seller_id == current_user.user_id)\
     .order_by(Product.created_at.desc())\
     .offset((page - 1) * page_size)\
     .limit(page_size)
    
    products = query.all()
    
    # 获取总数
    total = db.query(Product).filter(Product.seller_id == current_user.user_id).count()
    
    product_list = []
    for product in products:
        product_dict = product._asdict()
        product_list.append(ProductResponse(**product_dict))
    
    total_pages = (total + page_size - 1) // page_size
    
    return ProductListResponse(
        products=product_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

# ====================================================
# 4. 商品详情 (GET /{product_id})
# ====================================================
@router.get("/{product_id}", response_model=ProductResponse, summary="商品详情")
async def get_product_detail(
    product_id: str,
    db: Session = Depends(get_db)
):
    """获取商品详情"""
    
    product = db.query(
        Product.product_id,
        Product.name,
        Product.description,
        Product.price,
        Product.created_at,
        Product.status,
        Product.seller_id,
        Product.category_id,
        Product.image_path,
        User.username.label("seller_username"),
        User.phone.label("seller_phone"),
        Category.name.label("category_name")
    ).join(User, Product.seller_id == User.user_id)\
     .join(Category, Product.category_id == Category.id)\
     .filter(Product.product_id == product_id)\
     .first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    product_dict = product._asdict()
    
    return ProductResponse(**product_dict)

# ====================================================
# 5. 更新商品 (PUT /{product_id})
# ====================================================
@router.put("/{product_id}", response_model=ProductResponse, summary="更新商品")
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新商品信息"""
    
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查权限
    if product.seller_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此商品"
        )
    
    # 更新商品信息
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    # 获取更新后的完整信息
    updated_product = db.query(
        Product.product_id,
        Product.name,
        Product.description,
        Product.price,
        Product.created_at,
        Product.status,
        Product.seller_id,
        Product.category_id,
        Product.image_path,
        User.username.label("seller_username"),
        User.phone.label("seller_phone"),
        Category.name.label("category_name")
    ).join(User, Product.seller_id == User.user_id)\
     .join(Category, Product.category_id == Category.id)\
     .filter(Product.product_id == product_id)\
     .first()
    
    product_dict = updated_product._asdict()
    
    return ProductResponse(**product_dict)

# ====================================================
# 6. 下架商品 (DELETE /{product_id})
# ====================================================
@router.delete("/{product_id}", summary="下架商品")
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下架商品"""
    
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查权限
    if product.seller_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此商品"
        )
    
    # 检查商品是否已被交易
    transaction = db.query(Transaction).filter(Transaction.product_id == product_id).first()
    if transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品已被交易，无法下架"
        )
    product.status = 3  # 设置为已下架
    db.commit()
    return {"message": "商品下架成功"}

# ====================================================
# 7. 获取分类列表 (GET /categories/list)
# ====================================================
@router.get("/categories/list", response_model=List[dict], summary="获取分类列表")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有商品分类"""
    
    categories = db.query(Category).all()
    
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description
        }
        for cat in categories
    ]