// 初始化功能
document.addEventListener('DOMContentLoaded', function() {
    initMobileSidebar();
    // 自动隐藏消息提示
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            if (document.body.contains(message)) {
                message.style.opacity = '0';
                setTimeout(() => {
                    if (document.body.contains(message)) {
                        document.body.removeChild(message);
                    }
                }, 300);
            }
        }, 5000);
    });

    // 表单验证增强
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#e74c3c';
                    
                    // 添加错误提示
                    if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('error-message')) {
                        const errorMessage = document.createElement('div');
                        errorMessage.className = 'error-message';
                        errorMessage.textContent = '此字段为必填项';
                        errorMessage.style.color = '#e74c3c';
                        errorMessage.style.fontSize = '12px';
                        errorMessage.style.marginTop = '4px';
                        input.parentNode.appendChild(errorMessage);
                    }
                } else {
                    input.style.borderColor = '#ecf0f1';
                    
                    // 移除错误提示
                    const errorMessage = input.nextElementSibling;
                    if (errorMessage && errorMessage.classList.contains('error-message')) {
                        errorMessage.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showMessage('请填写所有必填字段', 'error');
            }
        });
    });

    const joinClassForm = document.getElementById('join-class-form');
    if (joinClassForm) {
        joinClassForm.addEventListener('submit', function(e) {
            const classCodeInput = document.getElementById('class_code');
            if (!classCodeInput.value.trim()) {
                e.preventDefault();
                showMessage('请输入班级代码', 'error');
                classCodeInput.focus();
            }
        });
    }

    // 输入框实时验证
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.hasAttribute('required') && this.value.trim()) {
                this.style.borderColor = '#27ae60';
                
                // 移除错误提示
                const errorMessage = this.nextElementSibling;
                if (errorMessage && errorMessage.classList.contains('error-message')) {
                    errorMessage.remove();
                }
            }
        });
        
        input.addEventListener('blur', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.style.borderColor = '#e74c3c';
            } else {
                this.style.borderColor = '#ecf0f1';
            }
        });
    });
});

// 显示消息提示
function showMessage(message, type = 'success') {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;
    messageEl.innerHTML = `
        <div class="message-content">
            <i class="material-icons message-icon">${type === 'error' ? 'error' : 'check_circle'}</i>
            <span class="message-text">${message}</span>
        </div>
    `;
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
        if (document.body.contains(messageEl)) {
            messageEl.style.opacity = '0';
            setTimeout(() => {
                if (document.body.contains(messageEl)) {
                    document.body.removeChild(messageEl);
                }
            }, 300);
        }
    }, 5000);
}

// 复制文本到剪贴板
function copyToClipboard(text) {
    return navigator.clipboard.writeText(text)
        .then(() => {
            showMessage('已复制到剪贴板', 'success');
            return true;
        })
        .catch(err => {
            console.error('复制失败:', err);
            showMessage('复制失败', 'error');
            return false;
        });
}

// 格式化日期时间
function formatDateTime(date) {
    if (!date) return '';
    
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 确认对话框
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 加载状态指示器
function showLoading(container) {
    const loader = document.createElement('div');
    loader.className = 'loading';
    loader.innerHTML = `
        <div class="loading-spinner"></div>
        <span>加载中...</span>
    `;
    container.appendChild(loader);
    return loader;
}

function hideLoading(loader) {
    if (loader && loader.parentNode) {
        loader.parentNode.removeChild(loader);
    }
}

// 移动端侧边栏功能
function initMobileSidebar() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileSidebar = document.getElementById('mobileSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const sidebarClose = document.getElementById('sidebarClose');
    
    if (!mobileMenuBtn || !mobileSidebar) return;
    
    // 打开侧边栏
    function openSidebar() {
        mobileSidebar.classList.add('active');
        sidebarOverlay.classList.add('active');
        document.body.classList.add('sidebar-open');
    }
    
    // 关闭侧边栏
    function closeSidebar() {
        mobileSidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        document.body.classList.remove('sidebar-open');
    }
    
    // 绑定事件
    mobileMenuBtn.addEventListener('click', openSidebar);
    
    if (sidebarClose) {
        sidebarClose.addEventListener('click', closeSidebar);
    }
    
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
    
    // 点击侧边栏链接时自动关闭侧边栏
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', closeSidebar);
    });
    
    // ESC键关闭侧边栏
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileSidebar.classList.contains('active')) {
            closeSidebar();
        }
    });
    
    // 窗口大小变化时，如果从移动端切换到桌面端，自动关闭侧边栏
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && mobileSidebar.classList.contains('active')) {
            closeSidebar();
        }
    });
}