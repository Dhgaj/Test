"""
文件处理工具模块

提供安全的文件名处理和其他文件相关的工具函数
"""
import re
import os
import unicodedata
from datetime import datetime
from werkzeug.utils import secure_filename as werkzeug_secure_filename
import logging

# 尝试导入PIL，如果不存在则设置为None
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    PIL_AVAILABLE = False

# 配置日志
logger = logging.getLogger(__name__)


def secure_filename(filename):
    """
    对中文文件名的支持
    
    处理包含中文字符的文件名，确保文件名安全且符合系统要求

    """
    if not filename:
        return ""
    
    # 规范化Unicode字符串
    filename = unicodedata.normalize('NFKD', filename)
    
    # 移除文件名中的非法字符，保留中文字符、字母、数字、空格、点号和横线
    filename = re.sub(r'[^\w\s\u4e00-\u9fff.-]', '', filename)
    
    # 替换空格为下划线
    filename = re.sub(r'\s+', '_', filename).strip('._')
    
    # 如果处理后为空，则回退到werkzeug的原始实现
    if not filename:
        return werkzeug_secure_filename(filename)
        
    return filename


def get_file_extension(filename):
    """
    获取文件扩展名
    """
    if not filename or '.' not in filename:
        return ""
    return filename.rsplit('.', 1)[-1].lower()


def is_allowed_file(filename, allowed_extensions):
    """
    检查文件是否为允许的文件类型
    """
    if not filename:
        return False
    
    extension = get_file_extension(filename)
    return extension in allowed_extensions


def format_file_size(size_bytes):
    """
    格式化文件大小显示
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


class FileHandler:
    """
    文件处理类
    提供文件操作相关的静态方法和工具
    """
    
    # 常用的允许文件类型
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'}
    ALLOWED_ARCHIVE_EXTENSIONS = {'zip', 'rar', '7z', 'tar', 'gz'}
    
    @staticmethod
    def secure_filename(filename):
        """安全文件名处理的静态方法"""
        return secure_filename(filename)
    
    @staticmethod
    def is_image_file(filename):
        """检查是否为图片文件"""
        return is_allowed_file(filename, FileHandler.ALLOWED_IMAGE_EXTENSIONS)
    
    @staticmethod
    def is_document_file(filename):
        """检查是否为文档文件"""
        return is_allowed_file(filename, FileHandler.ALLOWED_DOCUMENT_EXTENSIONS)
    
    @staticmethod
    def is_archive_file(filename):
        """检查是否为压缩文件"""
        return is_allowed_file(filename, FileHandler.ALLOWED_ARCHIVE_EXTENSIONS)
    
    @staticmethod
    def validate_upload_file(file, max_size_mb=10, allowed_extensions=None):
        """
        验证上传文件
        """
        if not file or not file.filename:
            return False, "未选择文件"
        
        # 检查文件类型
        if allowed_extensions and not is_allowed_file(file.filename, allowed_extensions):
            return False, f"不支持的文件类型，允许的类型：{', '.join(allowed_extensions)}"
        
        # 检查文件大小
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"文件过大，最大允许 {max_size_mb}MB"
        
        return True, "文件验证通过"


class AvatarHandler:
    """
    头像处理类
    专门处理用户头像的上传、验证和保存
    """
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_SIZE_MB = 5  # 最大5MB
    DEFAULT_SIZE = (200, 200)  # 默认头像尺寸
    
    def __init__(self, upload_folder):
        """
        初始化头像处理器
        
        Args:
            upload_folder: 头像上传文件夹路径
        """
        self.upload_folder = upload_folder
        self.ensure_upload_folder()
    
    def ensure_upload_folder(self):
        """确保上传文件夹存在"""
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def validate_avatar_file(self, file):
        """
        验证头像文件
        
        Args:
            file: 上传的文件对象
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not file or file.filename == '':
            return False, '未选择文件'
        
        # 检查文件类型
        if not is_allowed_file(file.filename, self.ALLOWED_EXTENSIONS):
            return False, '不支持的文件格式，请上传 PNG、JPG、JPEG 或 GIF 格式的图片'
        
        # 检查文件大小
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        max_size_bytes = self.MAX_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f'文件过大，最大允许 {self.MAX_SIZE_MB}MB'
        
        return True, None
    
    def generate_avatar_filename(self, user_id, original_filename):
        """
        生成头像文件名
        
        Args:
            user_id: 用户ID
            original_filename: 原始文件名
            
        Returns:
            str: 生成的文件名
        """
        extension = get_file_extension(original_filename)
        timestamp = int(datetime.now().timestamp())
        return f"avatar_{user_id}_{timestamp}.{extension}"
    
    def save_avatar(self, file, user_id, resize_to=None):
        """
        保存头像文件
        
        Args:
            file: 上传的文件对象
            user_id: 用户ID
            resize_to: 调整到的尺寸，默认为 DEFAULT_SIZE
            
        Returns:
            tuple: (success: bool, filename: str, error_message: str)
        """
        try:
            # 验证文件
            is_valid, error_message = self.validate_avatar_file(file)
            if not is_valid:
                return False, None, error_message
            
            # 生成文件名
            filename = self.generate_avatar_filename(user_id, file.filename)
            file_path = os.path.join(self.upload_folder, filename)
            
            # 保存文件
            file.save(file_path)
            
            # 调整图片尺寸
            resize_size = resize_to or self.DEFAULT_SIZE
            self.resize_avatar(file_path, resize_size)
            
            logger.info(f"Avatar saved successfully for user {user_id}: {filename}")
            return True, filename, None
            
        except Exception as e:
            logger.error(f"Error saving avatar for user {user_id}: {str(e)}")
            return False, None, f'保存头像失败: {str(e)}'
    
    def resize_avatar(self, file_path, size):
        """
        调整头像尺寸
        
        Args:
            file_path: 图片文件路径
            size: 目标尺寸 (width, height)
        """
        if not PIL_AVAILABLE:
            logger.warning("PIL not available, skipping image resize")
            return
            
        try:
            with Image.open(file_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode in ('RGBA', 'LA'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 保持宽高比调整尺寸
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 如果需要，创建正方形图片（居中裁剪）
                if size[0] == size[1]:  # 正方形
                    # 创建正方形背景
                    square_img = Image.new('RGB', size, (255, 255, 255))
                    # 计算居中位置
                    x = (size[0] - img.width) // 2
                    y = (size[1] - img.height) // 2
                    square_img.paste(img, (x, y))
                    img = square_img
                
                # 保存优化后的图片
                img.save(file_path, 'JPEG', optimize=True, quality=85)
                logger.info(f"Avatar resized to {size}: {file_path}")
                
        except Exception as e:
            logger.error(f"Error resizing avatar {file_path}: {str(e)}")
    
    def delete_avatar(self, filename):
        """
        删除头像文件
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 删除是否成功
        """
        try:
            file_path = os.path.join(self.upload_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Avatar deleted: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting avatar {filename}: {str(e)}")
            return False
    
    def get_avatar_url(self, filename, url_prefix='/static/uploads/avatars/'):
        """
        获取头像URL
        
        Args:
            filename: 文件名
            url_prefix: URL前缀
            
        Returns:
            str: 头像URL
        """
        if filename:
            return f"{url_prefix}{filename}"
        return None
