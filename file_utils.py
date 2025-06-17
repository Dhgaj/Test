"""
文件处理工具模块

提供安全的文件名处理和其他文件相关的工具函数
"""
import re
import unicodedata
from werkzeug.utils import secure_filename as werkzeug_secure_filename


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
