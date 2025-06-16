import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Flask 应用配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'soYNJPrRb_S_PmkJqXYNo8qXZAvXepuQLBJ1JNCtqrYTOK-O_qeJN9ExCEY1aENhT4U')

# 远程数据库配置
# DB_USERNAME = os.environ.get('DB_USERNAME', 'LianSifanTest')
# DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Meeting-room0')
# DB_HOST     = os.environ.get('DB_HOST', 'LianSifanTest.mysql.pythonanywhere-services.com')
# DB_NAME     = os.environ.get('DB_NAME', 'LianSifanTest$ICCS')
# DB_PORT = int(os.environ.get('DB_PORT', 3306))

# DB_USERNAME = os.environ.get('DB_USERNAME', 'meetingroom')
# DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Meeting-room0')
# DB_HOST = os.environ.get('DB_HOST', '8.134.119.146')
# DB_NAME = os.environ.get('DB_NAME', 'test_meeting_rooms')

# 本地数据库配置
# 测试环境数据库配置
DB_USERNAME = os.environ.get('DB_USERNAME', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'test_meeting_rooms')


# 构建数据库URI
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 安全相关配置
SESSION_COOKIE_SECURE = True
REMEMBER_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# 应用配置
MAX_TOTAL_MEETINGS = 10000  # 允许的最大会议数量

# 文件上传配置
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制上传文件大小为16MB
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'}  # 允许的文件类型
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # 允许的图片类型

# 文件上传目录配置 (相对于应用根目录)
UPLOAD_FOLDER_MATERIALS = 'static/uploads/meeting_materials'
UPLOAD_FOLDER_AVATARS = 'static/uploads/avatars'


# gmail 邮件服务器配置
MAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',                    # 邮件服务器地址
    'MAIL_PORT': 587,                                   # 邮件服务器端口
    'MAIL_USERNAME': 'sifanlian@gmail.com',             # 邮箱用户名
    'MAIL_PASSWORD': 'vqkc zycl ufnk nngf',             # 邮箱密码或应用专用密码
    'MAIL_DEFAULT_SENDER': 'sifanlian@gmail.com',       # 默认发件人
    'MAIL_USE_TLS': True,                               # 使用TLS加密
    'MAIL_USE_SSL': False                               # 不使用SSL加密
}

# 163 mail 邮件服务器配置
# MAIL_CONFIG = {
#     'MAIL_SERVER': 'smtp.vip.163.com',                    # 邮件服务器地址
#     'MAIL_PORT': 25,                                   # 邮件服务器端口
#     'MAIL_USERNAME': '32306400017.gzhu@vip.163.com',             # 邮箱用户名
#     'MAIL_PASSWORD': 'WMs2Z3tefGTmbx8q',             # 邮箱密码或应用专用密码
#     'MAIL_DEFAULT_SENDER': '32306400017.gzhu@vip.163.com',       # 默认发件人
#     'MAIL_USE_TLS': True,                               # 使用TLS加密
#     'MAIL_USE_SSL': False                               # 不使用SSL加密
# }
