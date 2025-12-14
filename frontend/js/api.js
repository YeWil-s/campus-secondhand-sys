// API配置和调用模块
const API_BASE_URL = 'http://localhost:8000/api';

// 获取认证token
function getAuthToken() {
    return localStorage.getItem('authToken');
}

// 设置认证token
function setAuthToken(token) {
    localStorage.setItem('authToken', token);
}

// 清除认证token
function clearAuthToken() {
    localStorage.removeItem('authToken');
}

// 获取当前用户信息
function getCurrentUser() {
    const userStr = localStorage.getItem('currentUser');
    return userStr ? JSON.parse(userStr) : null;
}

// 设置当前用户信息
function setCurrentUser(user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
}

// 清除当前用户信息
function clearCurrentUser() {
    localStorage.removeItem('currentUser');
}

// 通用API调用函数
async function apiCall(endpoint, options = {}) {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                // 认证失败，清除本地存储并跳转到登录页
                clearAuthToken();
                clearCurrentUser();
                showPage('login');
                throw new Error('认证失败，请重新登录');
            }
            throw new Error(data.detail || '请求失败');
        }

        return data;
    } catch (error) {
        console.error('API调用错误:', error);
        throw error;
    }
}

// 认证相关API
const authAPI = {
    // 用户注册
    register: (userData) => apiCall('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData)
    }),

    // 用户登录
    login: (credentials) => apiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials)
    })
};

// 用户相关API
const userAPI = {
    // 获取用户信息
    getProfile: () => apiCall('/users/profile'),

    // 更新用户信息
    updateProfile: (userData) => apiCall('/users/profile', {
        method: 'PUT',
        body: JSON.stringify(userData)
    })
};

// 商品相关API
const productAPI = {
    // 获取可用商品列表
    getAvailable: (params = {}) => {
        const query = new URLSearchParams();
        if (params.keyword) query.append('keyword', params.keyword);
        if (params.category_id) query.append('category_id', params.category_id);
        if (params.min_price) query.append('min_price', params.min_price);
        if (params.max_price) query.append('max_price', params.max_price);
        if (params.sort_by) query.append('sort_by', params.sort_by);
        if (params.page) query.append('page', params.page);
        const pageSize = params.page_size || 10;
        query.append('page_size', pageSize);
        return apiCall(`/products/available?${query}`);
    },

    // 获取我的商品列表
    getMyProducts: (params = {}) => {
        const query = new URLSearchParams();
        if (params.page) query.append('page', params.page);
        const pageSize = params.page_size || 10; 
        query.append('page_size', pageSize);
        return apiCall(`/products/my?${query}`);
    },

 // 更新商品
    update: async function(productId, data) {
        const response = await fetch(`http://localhost:8000/api/products/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || '更新商品失败');
        }

        return result;
    },
    // 获取商品详情
    getDetail: (productId) => apiCall(`/products/${productId}`),

    // 创建商品
    create: (productData) => apiCall('/products/create', {
        method: 'POST',
        body: JSON.stringify(productData)
    }),

    // 更新商品
    update: (productId, productData) => apiCall(`/products/${productId}`, {
        method: 'PUT',
        body: JSON.stringify(productData)
    }),

    // 删除商品
    delete: (productId) => apiCall(`/products/${productId}`, {
        method: 'DELETE'
    }),

    // 获取分类列表
    getCategories: () => apiCall('/products/categories/list')
};

// 交易相关API
const transactionAPI = {
    // 创建交易订单
    create: (transactionData) => apiCall('/transactions/', {
        method: 'POST',
        body: JSON.stringify(transactionData)
    }),

    // 完成支付
    completePayment: (transactionId) => apiCall(`/transactions/${transactionId}/pay`, {
        method: 'PUT'
    }),

    // 获取我的交易记录
    getMyTransactions: (params = {}) => {
        const query = new URLSearchParams();
        if (params.status) query.append('status', params.status);
        if (params.category_id) query.append('category_id', params.category_id);
        if (params.start_date) query.append('start_date', params.start_date);
        if (params.end_date) query.append('end_date', params.end_date);
        if (params.page) query.append('page', params.page);
        if (params.page_size) query.append('page_size', params.page_size);
        
        return apiCall(`/transactions/my?${query}`);
    },

    // 获取交易详情
    getDetail: (transactionId) => apiCall(`/transactions/${transactionId}`)
};

// 工具函数
function showAlert(message, type = 'danger') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // 移除现有的alert
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // 添加新的alert到页面顶部
    const container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // 3秒后自动消失
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 3000);
    }
}

function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

function formatPrice(price) {
    if (typeof price !== 'number') {
        price = parseFloat(price);
    }
    return price.toFixed(2);
}

function getStatusText(status) {
    switch (status) {
        case 0: return '不可选';
        case 1: return '在售中';
        case 2: return '已售出';
        case 3: return '已下架';
        default: return '未知状态';
    }
}

function getStatusClass(status) {
    switch (status) {
        case 0: return 'status-locked';
        case 1: return 'status-available';
        case 2: return 'status-sold';
        case 3: return 'status-offline';
        default: return '';
    }
}

// 交易状态文本
function getTransactionStatusText(status) {
    switch (status) {
        case 0: return '未支付';
        case 1: return '已成交';
        default: return '未知状态';
    }
}

// 交易状态样式
function getTransactionStatusClass(status) {
    switch (status) {
        case 0: return 'status-pending';
        case 1: return 'status-completed';
        default: return '';
    }
}

// 生成商品卡片HTML（恢复操作按钮）
function generateProductCard(product) {
    const statusClass = getStatusClass(product.status);
    const statusText = getStatusText(product.status);
    // 判断是否是"我的商品"页面
    const isMyProductsPage = document.getElementById('productsPage').classList.contains('active');
    // 判断商品是否可操作（状态为1表示可售，2表示已售出，3表示下架）
    const isOperable = product.status === 1;

    // 操作按钮区域（仅在"我的商品"页面显示）
        const actionButtons = isMyProductsPage && isOperable ? `
        <div class="mt-2 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-sm btn-secondary"
                    onclick="event.stopPropagation();
                        if (${product.status} === 2) {
                            showAlert('已售出产品无法修改信息');
                        } else {
                            showEditProductModal('${product.product_id}');
                        }">
                <i class="bi bi-pencil"></i> 编辑
            </button>
            <button type="button" class="btn btn-sm btn-danger"
                    onclick="event.stopPropagation();
                        if (${product.status} === 2) {
                            showAlert('已售出产品无法下架');
                        } else if (confirm('确定要下架这个商品吗？下架后无法恢复！')) {
                            setProductStatus('${product.product_id}', 3);
                        }">
                <i class="bi bi-trash"></i> 下架
            </button>
        </div>
    ` : '';

    return `
        <div class="col-12 mb-3">
            <div class="card product-card" onclick="showProductDetail('${product.product_id}')" style="border-radius: 8px;">
                <div class="row g-0">
                    <!-- 左侧图片区域 -->
                    <div class="col-md-3 position-relative">
                        ${product.image_path ?
                            `<img src="http://localhost:8000/api/uploads/${product.image_path}?t=${new Date(product.updated_at || product.created_at).getTime()}"
                                 class="card-img product-img w-100"
                                 style="
                                     height: 100px;
                                     object-fit: contain;
                                     object-position: center;
                                     background-color: #f8f9fa;
                                 "
                                 alt="${product.name}"
                                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'100\'%3E%3Crect fill=\'%23f8f9fa\' width=\'200\' height=\'100\'/%3E%3Ctext fill=\'%23999\' x=\'50%25\' y=\'50%25\' dominant-baseline=\'middle\' text-anchor=\'middle\' font-size=\'12px\'%3E暂无图片%3C/text%3E%3C/svg%3E'">` :
                            `<div class="product-img bg-light d-flex align-items-center justify-content-center" style="height: 100px;">
                                <span class="text-muted" style="font-size: 12px;">暂无图片</span>
                            </div>`
                        }
                        <span class="product-status" style="top: 8px; right: 8px;">
                            <span class="status-badge ${statusClass}" style="font-size: 11px; padding: 2px 6px;">${statusText}</span>
                        </span>
                    </div>

                    <!-- 右侧信息区域 -->
                    <div class="col-md-9">
                        <div class="card-body d-flex flex-column p-2">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <h5 class="card-title" style="font-size: 15px; margin-bottom: 0;">${product.name}</h5>
                                <span class="product-price" style="font-size: 16px; font-weight: 600;">¥${formatPrice(product.price)}</span>
                            </div>
                            <p class="card-text text-truncate-2" style="font-size: 13px; color: #6c757d; margin-bottom: 0.5rem;">
                                ${product.description}
                            </p>
                            <div class="d-flex justify-content-between align-items-center mt-auto">
                                <small class="text-muted" style="font-size: 12px;">
                                    <i class="bi bi-clock"></i> ${formatDateTime(product.created_at)}
                                </small>
                                ${actionButtons}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 生成交易记录HTML
function generateTransactionItem(transaction) {
    // 确定当前用户角色
    const currentUser = getCurrentUser();
    const isBuyer = currentUser && transaction.buyer_id === currentUser.user_id;
    const isSeller = currentUser && transaction.seller_id === currentUser.user_id;
    
    // 根据交易状态和角色确定显示文本和样式
    let statusText, statusClass;
    if (transaction.status === 0) {
        // 未完成订单（灰色）
        statusText = '未完成';
        statusClass = 'bg-gray';
    } else {
        // 已完成订单（区分买家和卖家）
        if (isBuyer) {
            statusText = '已购买';
            statusClass = 'bg-blue';
        } else if (isSeller) {
            statusText = '已售出';
            statusClass = 'bg-red';
        } else {
            statusText = '已完成';
            statusClass = 'bg-green';
        }
    }
    
    return `
        <div class="transaction-item">
            <div class="row">
                <div class="col-md-8">
                    <div class="d-flex align-items-center mb-2">
                        <h6 class="mb-0">${transaction.product_name}</h6>
                        <span class="badge ${statusClass} ms-2">${statusText}</span>
                    </div>
                    <p class="mb-2">
                        <span class="badge bg-secondary">${transaction.category_name || '未分类'}</span>
                    </p>
                    <small class="text-muted">
                        <i class="bi bi-clock"></i> ${formatDateTime(transaction.created_at)}
                    </small>
                </div>
                <div class="col-md-4 text-end">
                    <h5 class="product-price">¥${formatPrice(transaction.amount)}</h5>
                    ${transaction.status === 0 && isBuyer ? 
                        `<button class="btn btn-success btn-sm mt-2" onclick="completePayment('${transaction.transaction_id}')">
                            <i class="bi bi-credit-card"></i> 完成支付
                        </button>` : ''
                    }
                    <button class="btn btn-outline-primary btn-sm mt-2" onclick="showTransactionDetail('${transaction.transaction_id}')">
                        <i class="bi bi-eye"></i> 查看详情
                    </button>
                </div>
            </div>
        </div>
    `;
}

// 生成分页HTML
function generatePagination(pagination, callback) {
    const { page, total_pages, total } = pagination;
    
    if (total_pages <= 1) return '';
    
    let html = '<nav><ul class="pagination justify-content-center">';
    
    // 上一页
    html += `<li class="page-item ${page === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="${callback}(${page - 1}); return false;">上一页</a>
    </li>`;
    
    // 页码
    const startPage = Math.max(1, page - 2);
    const endPage = Math.min(total_pages, page + 2);
    
    if (startPage > 1) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="${callback}(1); return false;">1</a></li>`;
        if (startPage > 2) {
            html += `<li class="page-item disabled"><a class="page-link" href="#">...</a></li>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `<li class="page-item ${i === page ? 'active' : ''}">
            <a class="page-link" href="#" onclick="${callback}(${i}); return false;">${i}</a>
        </li>`;
    }
    
    if (endPage < total_pages) {
        if (endPage < total_pages - 1) {
            html += `<li class="page-item disabled"><a class="page-link" href="#">...</a></li>`;
        }
        html += `<li class="page-item"><a class="page-link" href="#" onclick="${callback}(${total_pages}); return false;">${total_pages}</a></li>`;
    }
    
    // 下一页
    html += `<li class="page-item ${page === total_pages ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="${callback}(${page + 1}); return false;">下一页</a>
    </li>`;
    
    html += '</ul></nav>';
    
    // 添加统计信息
    html += `<div class="text-center text-muted mb-3">共 ${total} 条记录，第 ${page}/${total_pages} 页</div>`;
    
    return html;
}