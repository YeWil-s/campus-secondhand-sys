// 主应用逻辑
let currentPage = 1;
let currentProductPage = 1;
let currentTransactionPage = 1;
let currentCategoryId = '';

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadCategories();
    
    // 绑定表单事件
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('searchForm').addEventListener('submit', handleSearch);
    document.getElementById('transactionSearchForm').addEventListener('submit', handleTransactionSearch);
    document.getElementById('profileForm').addEventListener('submit', handleProfileUpdate);
});

// 检查用户认证状态
function checkAuth() {
    const token = getAuthToken();
    const user = getCurrentUser();
    
    if (token && user) {
        showAuthenticatedUI();
        if (document.getElementById('homePage').style.display !== 'none') {
            loadProducts();
        }
    } else {
        showUnauthenticatedUI();
    }
}

// 显示已认证的UI
function showAuthenticatedUI() {
    const user = getCurrentUser();
    document.getElementById('navLogin').style.display = 'none';
    document.getElementById('navRegister').style.display = 'none';
    document.getElementById('navUser').style.display = 'block';
    document.getElementById('navProducts').style.display = 'block';
    document.getElementById('navTransactions').style.display = 'block';
    document.getElementById('username').textContent = user.username;
}

// 显示未认证的UI
function showUnauthenticatedUI() {
    document.getElementById('navLogin').style.display = 'block';
    document.getElementById('navRegister').style.display = 'block';
    document.getElementById('navUser').style.display = 'none';
    document.getElementById('navProducts').style.display = 'none';
    document.getElementById('navTransactions').style.display = 'none';
}

// 修改页面切换函数中交易记录页面的处理逻辑
function showPage(pageName) {
    // 检查是否需要登录
    const requiresAuth = ['products', 'transactions', 'profile'];
    if (requiresAuth.includes(pageName) && !getAuthToken()) {
        showAlert('请先登录', 'warning');
        showPage('login');
        return;
    }

    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
        page.classList.remove('active');
    });


    // 显示指定页面
    const pageElement = document.getElementById(pageName + 'Page');
    if (pageElement) {
        pageElement.style.display = 'block';
        pageElement.classList.add('active');

        // 根据页面加载数据
        switch(pageName) {
            case 'home':
                loadProducts();
                break;
            case 'products':
                loadMyProducts();
                break;
            case 'transactions':
                // 重置交易记录相关缓存和DOM
                currentTransactionPage = 1; // 重置页码缓存
                const transactionList = document.getElementById('transactionList');
                const transactionPagination = document.getElementById('transactionPagination');
                if (transactionList) transactionList.innerHTML = ''; // 清空列表
                if (transactionPagination) transactionPagination.innerHTML = ''; // 清空分页
                loadTransactions(); // 重新加载数据
                break;
            case 'profile':
                loadProfile();
                break;
        }
    }
}
// 加载商品分类
async function loadCategories() {
    try {
        const categories = await productAPI.getCategories();
        
        // 【修改】: 移除对 searchCategorySelect 的处理
        const transactionCategorySelect = document.getElementById('transactionCategory');
        const productCategorySelect = document.getElementById('productCategory');
        
        [transactionCategorySelect, productCategorySelect].forEach(select => {
            if (select) {
                // 对于交易筛选，保留 "所有分类" 选项
                select.innerHTML = select.id === 'transactionCategory' ? '<option value="">所有分类</option>' : '<option value="">选择分类</option>';
                categories.forEach(category => {
                    select.innerHTML += `<option value="${category.id}">${category.name}</option>`;
                });
            }
        });
        
        // 生成左侧分类列表
        const categoryList = document.getElementById('categoryList');
        // 清除现有分类（保留"所有分类"）
        const allCategoryItem = categoryList.querySelector('.category-item[data-category=""]');
        categoryList.innerHTML = '';
        categoryList.appendChild(allCategoryItem);
        
        // 添加分类项
        categories.forEach(category => {
            const li = document.createElement('li');
            li.className = 'list-group-item category-item';
            li.dataset.category = category.id;
            li.textContent = category.name;
            
            // 添加点击事件
            li.addEventListener('click', function() {
                // 移除其他分类的激活状态
                document.querySelectorAll('.category-item').forEach(item => {
                    item.classList.remove('active');
                });
                // 设置当前分类为激活状态
                this.classList.add('active');
                
                // 【核心修复】: 更新全局分类ID
                currentCategoryId = this.dataset.category;
                
                // 重新加载商品列表
                currentPage = 1;
                loadProducts(1);
            });
            
            categoryList.appendChild(li);
        });
        
        // 为"所有分类"添加点击事件
        allCategoryItem.addEventListener('click', function() {
            document.querySelectorAll('.category-item').forEach(item => {
                item.classList.remove('active');
            });
            this.classList.add('active');
            
            // 【核心修复】: 重置全局分类ID
            currentCategoryId = '';
            currentPage = 1;
            loadProducts(1);
        });
        
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

// 处理用户登录
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const result = await authAPI.login({ username, password });
        setAuthToken(result.access_token);
        
        // 获取用户信息
        const user = await userAPI.getProfile();
        setCurrentUser(user);
        
        showAuthenticatedUI();
        showPage('home');
        showAlert('登录成功！', 'success');
    } catch (error) {
        showAlert(error.message);
    }
}

// 处理用户注册
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const phone = document.getElementById('registerPhone').value;
    const campusCard = document.getElementById('registerCampusCard').value;
    
    // 验证密码
    if (password !== confirmPassword) {
        showAlert('两次输入的密码不一致');
        return;
    }
    
    try {
        const user = await authAPI.register({
            username,
            password,
            phone,
            campus_card: campusCard
        });
        
        showAlert('注册成功！请登录', 'success');
        showPage('login');
    } catch (error) {
        showAlert(error.message);
    }
}

// 修改退出登录函数，确保退出后跳转到welcome.html
function logout() {
    // 清除本地存储的登录状态
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');

    // 退出后跳转到欢迎页
    window.location.href = 'welcome.html';
}

// 加载商品列表
async function loadProducts(page = 1) {
    // 显示加载状态
    const productList = document.getElementById('productList');
    const loading = document.getElementById('productLoading');
    productList.innerHTML = '';
    loading.style.display = 'block';
    try {
        const keyword = document.getElementById('searchKeyword').value;
        // 【核心修复】: 从新的排序字段中读取值
        const sortBy = document.getElementById('productSortBy').value;
        const minPrice = document.getElementById('minPrice').value;
        const maxPrice = document.getElementById('maxPrice').value;
        
        const params = {
            page,
            keyword,
            // 【核心修复】: 使用全局变量 currentCategoryId
            category_id: currentCategoryId, 
            min_price: minPrice,
            max_price: maxPrice,
            sort_by: sortBy,
            page_size: 10
        };
        
        const result = await productAPI.getAvailable(params);

        loading.style.display = 'none';
        currentPage = page;
        
        const productsToRender = result.products; 

        // 确保 productList 元素存在
        if (productList) {
            productList.innerHTML = productsToRender.map(product => generateProductCard(product)).join('');
        }
        
        // 渲染分页
        // 使用 generatePagination 函数，并传入所需的参数
        const pagination = document.getElementById('pagination');
        if (pagination) {
            pagination.innerHTML = generatePagination(result, 'loadProducts');
        }
        
        document.getElementById('productCount').textContent = `共 ${result.total} 件商品`;
    } catch (error) {
        console.error('加载商品失败:', error);
        showAlert('加载商品失败');
        loading.style.display = 'none';
    }
}

// 处理商品搜索
function handleSearch(event) {
    event.preventDefault();
    currentPage = 1;
    loadProducts(1);
}

// 重置搜索条件
function resetSearch() {
    document.getElementById('searchForm').reset();
    
    // 【新增】: 重置排序
    const sortBySelect = document.getElementById('productSortBy');
    if (sortBySelect) {
        sortBySelect.value = 'newest';
    }
    
    // 【核心修复】: 重置全局分类ID
    currentCategoryId = '';

    // 移除其他分类的激活状态，并激活 "所有分类"
    document.querySelectorAll('.category-item').forEach(item => {
        item.classList.remove('active');
    });
    const allCategoryItem = document.querySelector('.category-item[data-category=""]');
    if (allCategoryItem) {
        allCategoryItem.classList.add('active');
    }
    
    currentPage = 1;
    loadProducts(1);
}

// 显示商品详情
async function showProductDetail(productId) {
    try {
        const product = await productAPI.getDetail(productId);
        const currentUser = getCurrentUser();

        const content = `
            <div class="row">
                <div class="col-md-6">
                    ${product.image_path ? 
                        `<img src="http://localhost:8000/api/uploads/${product.image_path}"  class="img-fluid rounded" alt="${product.name}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'400\' height=\'400\'%3E%3Crect fill=\'%23f0f0f0\' width=\'400\' height=\'400\'/%3E%3Ctext fill=\'%23999\' x=\'50%25\' y=\'50%25\' dominant-baseline=\'middle\' text-anchor=\'middle\'%3E暂无图片%3C/text%3E%3C/svg%3E'">` :
                        `<div class="bg-light p-5 text-center rounded">暂无图片</div>`
                    }
                </div>
                <div class="col-md-6">
                    <h5>${product.name}</h5>
                    <p><strong>价格：</strong><span class="product-price">¥${formatPrice(product.price)}</span></p>
                    <p><strong>分类：</strong>${product.category_name || '未分类'}</p>
                    <p><strong>状态：</strong><span class="status-badge ${getStatusClass(product.status)}">${getStatusText(product.status)}</span></p>
                    <p><strong>描述：</strong>${product.description || '暂无描述'}</p>
                    <hr>
                    <h6>卖家信息</h6>
                    <p><strong>用户名：</strong>${product.seller_username || '匿名用户'}</p>
                    <p><strong>联系方式：</strong>${product.seller_phone || '暂无'}</p>
                    <p><strong>发布时间：</strong>${formatDateTime(product.created_at)}</p>
                </div>
            </div>
        `;
        
        document.getElementById('productDetailContent').innerHTML = content;
        
        const buyBtn = document.getElementById('buyProductBtn');
        if (product.status === 1 && currentUser && product.seller_id !== currentUser.user_id) {
            buyBtn.style.display = 'block';
            buyBtn.onclick = () => buyProduct(productId);
        } else {
            buyBtn.style.display = 'none';
        }
        
        const modal = new bootstrap.Modal(document.getElementById('productDetailModal'));
        modal.show();
    } catch (error) {
        console.error('获取商品详情失败:', error);
        showAlert('获取商品详情失败');
    }
}

// 购买商品
async function buyProduct(productId) {
    if (!getAuthToken()) {
        showAlert('请先登录', 'warning');
        showPage('login');
        return;
    }
    
    try {
        const transaction = await transactionAPI.create({ product_id: productId });
        
        // 关闭商品详情模态框
        bootstrap.Modal.getInstance(document.getElementById('productDetailModal')).hide();
        
        showAlert('订单创建成功！请完成支付', 'success');
        
        // 显示确认对话框
        if (confirm(`订单创建成功！商品价格：¥${formatPrice(transaction.amount)}\n是否立即完成支付？`)) {
            await completePayment(transaction.transaction_id);
        }
    } catch (error) {
        showAlert(error.message);
    }
}

// 完成支付
async function completePayment(transactionId) {
    try {
        await transactionAPI.completePayment(transactionId);
        showAlert('支付成功！', 'success');
        
        // 刷新页面数据
        if (document.getElementById('homePage').style.display !== 'none') {
            loadProducts(currentPage);
        } else if (document.getElementById('transactionsPage').style.display !== 'none') {
            loadTransactions(currentTransactionPage);
        }
    } catch (error) {
        showAlert(error.message);
    }
}

// 加载我的商品
// 加载我的商品列表
async function loadMyProducts(page = 1) {
    // 显示加载状态
    const productList = document.getElementById('myProductList');
    const loading = document.getElementById('myProductLoading');
    if (productList) productList.innerHTML = '';
    if (loading) loading.style.display = 'block';

    try {
        const result = await productAPI.getMyProducts({ page, page_size: 10 });
        loading.style.display = 'none';
        currentProductPage = page;

        const pagination = document.getElementById('myProductPagination');

        if (result.products.length === 0) {
            productList.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-box"></i>
                        <h5>暂无商品</h5>
                        <p>您还没有发布任何商品</p>
                    </div>
                </div>
            `;
            pagination.innerHTML = '';
        } else {
            // 使用与首页相同的商品卡片生成函数
            productList.innerHTML = result.products.map(product => generateProductCard(product)).join('');
            pagination.innerHTML = generatePagination(result, 'loadMyProducts');
        }

        document.getElementById('myProductCount').textContent = `共 ${result.total} 件商品`;
    } catch (error) {
        console.error('加载我的商品失败:', error);
        showAlert('加载我的商品失败');
        loading.style.display = 'none';
    }
}


// 显示编辑商品模态框
async function showEditProductModal(productId) {
    try {
        // 获取商品详情
        const product = await productAPI.getDetail(productId);

        // 填充表单数据
        document.getElementById('editProductId').value = product.product_id;
        document.getElementById('editProductName').value = product.name;
        document.getElementById('editProductDescription').value = product.description;
        document.getElementById('editProductPrice').value = product.price;
        document.getElementById('editProductStatus').value = product.status;

        // 加载分类并设置选中项
        const editCategorySelect = document.getElementById('editProductCategory');
        const categories = await productAPI.getCategories();
        editCategorySelect.innerHTML = '<option value="">选择分类</option>';
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            if (category.id === product.category_id) {
                option.selected = true;
            }
            editCategorySelect.appendChild(option);
        });

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('editProductModal'));
        modal.show();
    } catch (error) {
        console.error('加载商品详情失败:', error);
        showAlert('加载商品详情失败');
    }
}
// 提交编辑商品表单
async function submitEditProductForm() {
    const productId = document.getElementById('editProductId').value;
    const name = document.getElementById('editProductName').value;
    const description = document.getElementById('editProductDescription').value;
    const price = document.getElementById('editProductPrice').value;
    const categoryId = document.getElementById('editProductCategory').value;
    const status = document.getElementById('editProductStatus').value;
    const imageFile = document.getElementById('editProductImage').files[0];

    if (!name || !price || !categoryId || !status) {
        showAlert('请填写完整的商品信息');
        return;
    }

    try {
        let imagePath = null;

        // 如果有新图片，先上传
        if (imageFile) {
            const formData = new FormData();
            formData.append('file', imageFile);

            const uploadResponse = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`
                },
                body: formData
            });

            if (uploadResponse.ok) {
                const uploadData = await uploadResponse.json();
                imagePath = uploadData.filename;
            } else {
                showAlert('图片上传失败');
                return;
            }
        }

        // 准备更新数据
        const updateData = {
            name,
            description,
            price: parseFloat(price),
            category_id: parseInt(categoryId),
            status: parseInt(status)
        };

        // 只有上传了新图片才包含image_path字段
        if (imagePath) {
            updateData.image_path = imagePath;
        }

        // 调用API更新商品
        await productAPI.update(productId, updateData);

        // 关闭模态框并刷新列表
        bootstrap.Modal.getInstance(document.getElementById('editProductModal')).hide();
        showAlert('商品更新成功！', 'success');
        // 强制刷新图片（添加时间戳防止缓存）
        if (imagePath) {
            const imgElements = document.querySelectorAll(`img[src*="${productId}"]`);
            imgElements.forEach(img => {
                const src = img.src.split('?')[0];
                img.src = `${src}?t=${new Date().getTime()}`;
            });
        }
        loadMyProducts(currentProductPage);
    } catch (error) {
        showAlert(error.message);
    }
}
// 显示发布商品模态框
function showAddProductModal() {
    const modalElement = document.getElementById('addProductModal');
    // 检查元素是否存在
    if (!modalElement) {
        showAlert('发布商品功能初始化失败，请刷新页面重试', 'danger');
        return;
    }

    const modal = new bootstrap.Modal(modalElement);
    // 重置表单
    const form = document.getElementById('addProductForm');
    if (form) form.reset();
    // 显示模态框
    modal.show();
}

// 生成分页HTML
function generatePagination(result, callbackName) {
    if (result.total <= result.page_size) {
        return '';
    }

    const totalPages = Math.ceil(result.total / result.page_size);
    let html = '<ul class="pagination">';

    // 上一页
    html += `<li class="page-item ${result.page === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="${callbackName}(${result.page - 1}); return false;">上一页</a>
    </li>`;

    // 页码
    for (let i = 1; i <= totalPages; i++) {
        // 只显示当前页附近的页码
        if (i === 1 || i === totalPages || Math.abs(i - result.page) <= 1) {
            html += `<li class="page-item ${result.page === i ? 'active' : ''}">
                <a class="page-link" href="#" onclick="${callbackName}(${i}); return false;">${i}</a>
            </li>`;
        } else if (i === result.page - 2 || i === result.page + 2) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }

    // 下一页
    html += `<li class="page-item ${result.page === totalPages ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="${callbackName}(${result.page + 1}); return false;">下一页</a>
    </li>`;

    html += '</ul>';
    return html;
}
// 图片预览
document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('productImage');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    showAlert('图片大小不能超过 5MB');
                    this.value = '';
                    return;
                }
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('previewImg').src = e.target.result;
                    document.getElementById('imagePreview').style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
});

// 发布商品
async function addProduct() {
    const name = document.getElementById('productName').value;
    const description = document.getElementById('productDescription').value;
    const price = document.getElementById('productPrice').value;
    const categoryId = document.getElementById('productCategory').value;
    const imageFile = document.getElementById('productImage').files[0];
    
    if (!name || !price || !categoryId) {
        showAlert('请填写完整的商品信息');
        return;
    }
    
    try {
        let imagePath = null;
        
        // 如果有图片，先上传图片
        if (imageFile) {
            const formData = new FormData();
            formData.append('file', imageFile);
            
            const uploadResponse = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`
                },
                body: formData
            });
            
            if (uploadResponse.ok) {
                const uploadData = await uploadResponse.json();
                imagePath = uploadData.filename;
            } else {
                showAlert('图片上传失败');
                return;
            }
        }
        
        await productAPI.create({
            name,
            description,
            price: parseFloat(price),
            category_id: parseInt(categoryId),
            image_path: imagePath
        });
        
        bootstrap.Modal.getInstance(document.getElementById('addProductModal')).hide();
        showAlert('商品发布成功！', 'success');
        loadMyProducts(currentProductPage);
    } catch (error) {
        showAlert(error.message);
    }
}

// 删除商品
async function deleteProduct(productId) {
    if (!confirm('确定要下架这个商品吗？下架后无法恢复！')) {
        return;
    }
    
    try {
        await productAPI.delete(productId);
        showAlert('商品下架成功', 'success');
        loadMyProducts(currentProductPage);
    } catch (error) {
        showAlert(error.message);
    }
}

// 更新商品状态（app.js）
async function setProductStatus(productId, status) {
    try {
        await productAPI.update(productId, { status });
        const statusText = getStatusText(status);
        showAlert(`商品已${statusText}`, 'success');
        loadMyProducts(currentProductPage);
    } catch (error) {
        showAlert(error.message);
    }
}

// 加载交易记录
async function loadTransactions(page = 1) {
    try {
        const status = document.getElementById('transactionStatus').value;
        const categoryId = document.getElementById('transactionCategory').value;
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        const params = {
            page,
            status: status || undefined,
            category_id: categoryId || undefined,
            start_date: startDate || undefined,
            end_date: endDate || undefined
        };
        
        const result = await transactionAPI.getMyTransactions(params);
        console.log("交易记录数据:", result.transactions);
        currentTransactionPage = page;
        
        const transactionList = document.getElementById('transactionList');
        const pagination = document.getElementById('transactionPagination');
        
        if (result.transactions.length === 0) {
            transactionList.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-receipt"></i>
                    <h5>暂无交易记录</h5>
                    <p>您还没有任何交易记录</p>
                </div>
            `;
            pagination.innerHTML = '';
        } else {
            transactionList.innerHTML = result.transactions.map(transaction => 
                generateTransactionItem(transaction)
            ).join('');
            
            pagination.innerHTML = generatePagination(result, 'loadTransactions');
        }
    } catch (error) {
        console.error('加载交易记录失败:', error);
        showAlert('加载交易记录失败');
    }
}

// 处理交易记录搜索
function handleTransactionSearch(event) {
    event.preventDefault();
    currentTransactionPage = 1;
    loadTransactions(1);
}

// 重置交易记录搜索
function resetTransactionSearch() {
    document.getElementById('transactionSearchForm').reset();
    currentTransactionPage = 1;
    loadTransactions(1);
}

// 显示交易详情
async function showTransactionDetail(transactionId) {
    try {
        const transaction = await transactionAPI.getDetail(transactionId);
        
        const content = `
            <div class="row">
                <div class="col-md-12">
                    <h6>商品信息</h6>
                    <p><strong>商品名称：</strong>${transaction.product_name}</p>
                    <p><strong>商品分类：</strong>${transaction.category_name || '未分类'}</p>
                    <hr>
                    <h6>交易信息</h6>
                    <p><strong>交易ID：</strong>${transaction.transaction_id}</p>
                    <p><strong>交易金额：</strong><span class="product-price">¥${formatPrice(transaction.amount)}</span></p>
                    <p><strong>交易状态：</strong><span class="status-badge ${getTransactionStatusClass(transaction.status)}">${getTransactionStatusText(transaction.status)}</span></p>
                    <p><strong>交易时间：</strong>${formatDateTime(transaction.created_at)}</p>
                    <hr>
                    <h6>交易对象</h6>
                    <p><strong>对方用户名：</strong>${transaction.counterparty_username}</p>
                    <p><strong>对方身份：</strong>${transaction.counterparty_role}</p>
                </div>
            </div>
        `;
        
        // 创建临时模态框显示详情
        const modalHtml = `
            <div class="modal fade" id="transactionDetailModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">交易详情</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">${content}</div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 移除现有的详情模态框
        const existingModal = document.getElementById('transactionDetailModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('transactionDetailModal'));
        modal.show();
        
        // 模态框关闭时移除DOM元素
        document.getElementById('transactionDetailModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    } catch (error) {
        console.error('获取交易详情失败:', error);
        showAlert('获取交易详情失败');
    }
}

// 加载个人资料
async function loadProfile() {
    try {
        const user = await userAPI.getProfile();
        
        document.getElementById('profileUserId').value = user.user_id;
        document.getElementById('profileUsername').value = user.username;
        document.getElementById('profilePhone').value = user.phone;
        document.getElementById('profileCampusCard').value = user.campus_card;
        document.getElementById('profileCreatedAt').value = formatDateTime(user.created_at);
    } catch (error) {
        console.error('加载个人资料失败:', error);
        showAlert('加载个人资料失败');
    }
}

// 处理个人资料更新
async function handleProfileUpdate(event) {
    event.preventDefault();
    
    const phone = document.getElementById('profilePhone').value;
    const campusCard = document.getElementById('profileCampusCard').value;
    
    try {
        const updatedUser = await userAPI.updateProfile({
            phone,
            campus_card: campusCard
        });
        
        setCurrentUser(updatedUser);
        showAlert('个人资料更新成功！', 'success');
    } catch (error) {
        showAlert(error.message);
    }
}