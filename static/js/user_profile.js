/**
 * 用户个人资料页面脚本
 * 实现头像上传和页面交互功能
 */
document.addEventListener('DOMContentLoaded', function() {
  // 头像上传处理
  const avatarUpload = document.getElementById('avatarUpload');
  const profileImage = document.getElementById('profileImage');
  
  if (avatarUpload) {
    avatarUpload.addEventListener('change', function() {
      const file = this.files[0];
      if (!file) return;
      
      // 检查文件类型
      if (!file.type.match('image.*')) {
        showAlert('请选择图片文件！', 'warning');
        return;
      }
      
      // 检查文件大小 (限制为 5MB)
      if (file.size > 5 * 1024 * 1024) {
        showAlert('图片文件过大，请选择小于 5MB 的文件！', 'warning');
        return;
      }
      
      // 预览头像
      const reader = new FileReader();
      reader.onload = function(e) {
        profileImage.src = e.target.result;
        
        // 准备上传头像
        uploadAvatar(file);
      };
      reader.readAsDataURL(file);
    });
  }
  
  /**
   * 上传头像到服务器
   * @param {File} file - 头像文件
   */
  function uploadAvatar(file) {
    const formData = new FormData();
    formData.append('avatar', file);
    
    // 设置加载状态
    profileImage.classList.add('uploading');
    profileImage.style.opacity = '0.6';
    
    // 获取CSRF令牌(如果你的应用使用Flask-WTF)
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    // 发送头像文件到服务器
    fetch('/upload_avatar', {
      method: 'POST',
      body: formData,
      headers: csrfToken ? {
        'X-CSRFToken': csrfToken
      } : {}
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('上传失败');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        showAlert('头像上传成功！', 'success');
      } else {
        showAlert(data.message || '头像上传失败，请重试！', 'danger');
      }
    })
    .catch(error => {
      console.error('上传头像出错:', error);
      showAlert('上传过程中发生错误，请重试！', 'danger');
    })
    .finally(() => {
      // 取消加载状态
      profileImage.classList.remove('uploading');
      profileImage.style.opacity = '1';
    });
  }
  
  /**
   * 显示提示消息
   * @param {string} message - 消息内容
   * @param {string} type - 消息类型 (success, danger, warning, info)
   */
  function showAlert(message, type = 'info') {
    // 创建消息元素
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="关闭"></button>
    `;
    
    // 添加到页面
    document.body.appendChild(alertDiv);
    
    // 3秒后自动关闭
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alertDiv);
      bsAlert.close();
    }, 3000);
  }
  
  // 标签切换事件监听
  const tabEls = document.querySelectorAll('button[data-bs-toggle="tab"]');
  tabEls.forEach(tabEl => {
    tabEl.addEventListener('shown.bs.tab', function(event) {
      // 可以在此处添加标签切换后的逻辑
    });
  });
  
  // 添加卡片悬停效果
  const cards = document.querySelectorAll('.card');
  cards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-5px)';
      card.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
      card.style.boxShadow = '';
    });
  });
});

// 添加头像上传相关的CSS
document.addEventListener('DOMContentLoaded', function() {
  const style = document.createElement('style');
  style.textContent = `
    .position-relative .position-absolute {
      transition: all 0.3s ease;
    }
    
    .position-relative:hover .position-absolute {
      transform: scale(1.1);
    }
    
    #profileImage {
      transition: all 0.3s ease;
      object-fit: cover;
    }
    
    #profileImage.uploading {
      filter: grayscale(50%);
    }
  `;
  document.head.appendChild(style);
});
