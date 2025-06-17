import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 邮件配置
def load_mail_config():
    """加载邮件配置"""
    try:
        from config import MAIL_CONFIG
        
        mail_server = MAIL_CONFIG.get("MAIL_SERVER")
        mail_port = int(MAIL_CONFIG.get("MAIL_PORT", 25))
        mail_username = MAIL_CONFIG.get("MAIL_USERNAME")
        mail_password = MAIL_CONFIG.get("MAIL_PASSWORD")
        mail_default_sender = MAIL_CONFIG.get("MAIL_DEFAULT_SENDER")
        mail_use_tls = MAIL_CONFIG.get("MAIL_USE_TLS", True)
        mail_use_ssl = MAIL_CONFIG.get("MAIL_USE_SSL", False)
        
        if not all([mail_server, mail_username, mail_password, mail_default_sender]):
            raise ValueError("邮件配置不完整")
        print("从配置文件读取邮件设置成功")
        
    except (ImportError, ValueError):
        # 从环境变量读取配置
        mail_server = os.environ.get("MAIL_SERVER")
        mail_port = int(os.environ.get("MAIL_PORT", 587))
        mail_username = os.environ.get("MAIL_USERNAME")
        mail_password = os.environ.get("MAIL_PASSWORD")
        mail_default_sender = os.environ.get("MAIL_DEFAULT_SENDER")
        mail_use_tls = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
        mail_use_ssl = os.environ.get("MAIL_USE_SSL", "False").lower() == "true"
        
        if not all([mail_server, mail_username, mail_password, mail_default_sender]):
            print("警告：邮件配置不完整，邮件功能将被禁用")
            return None
        else:
            print("从环境变量读取邮件设置成功")
    
    return {
        'server': mail_server,
        'port': mail_port,
        'username': mail_username,
        'password': mail_password,
        'default_sender': mail_default_sender,
        'use_tls': mail_use_tls,
        'use_ssl': mail_use_ssl
    }

# 全局邮件配置
MAIL_CONFIG_GLOBAL = load_mail_config()

def init_serializer(secret_key):
    """初始化序列化器"""
    return URLSafeTimedSerializer(secret_key)

def send_email_async(to, subject, template, mail_config=None):
    """异步发送邮件"""
    if mail_config is None:
        mail_config = MAIL_CONFIG_GLOBAL
    
    if not mail_config:
        print("邮件配置未设置，无法发送邮件")
        return False
    
    def send_mail_thread():
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = mail_config['default_sender']
            msg["To"] = to

            part = MIMEText(template, "html")
            msg.attach(part)

            if mail_config['use_ssl']:
                server = smtplib.SMTP_SSL(mail_config['server'], mail_config['port'])
            else:
                server = smtplib.SMTP(mail_config['server'], mail_config['port'])
                if mail_config['use_tls']:
                    server.starttls()

            if mail_config['username'] and mail_config['password']:
                server.login(mail_config['username'], mail_config['password'])

            server.sendmail(mail_config['default_sender'], to, msg.as_string())
            server.quit()
            print(f"邮件发送成功至: {to}")
            return True
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
            return False

    thread = threading.Thread(target=send_mail_thread)
    thread.start()
    print(f"开始异步发送邮件至: {to}")
    return True

def send_email(to, subject, template, mail_config=None):
    """发送邮件的简单封装"""
    return send_email_async(to, subject, template, mail_config)

def generate_confirmation_token(email, serializer):
    """生成确认令牌"""
    return serializer.dumps(email, salt="email-confirm-salt")

def confirm_token(token, serializer, expiration=3600):
    """验证确认令牌"""
    try:
        email = serializer.loads(token, salt="email-confirm-salt", max_age=expiration)
        return email
    except:
        return None

# 为了向后兼容，保留原有的全局函数
_global_serializer = None

def set_global_serializer(secret_key):
    """设置全局序列化器"""
    global _global_serializer
    _global_serializer = init_serializer(secret_key)

def generate_confirmation_token_global(email):
    """使用全局序列化器生成令牌"""
    if not _global_serializer:
        raise ValueError("序列化器未初始化，请先调用 set_global_serializer()")
    return generate_confirmation_token(email, _global_serializer)

def confirm_token_global(token, expiration=3600):
    """使用全局序列化器验证令牌"""
    if not _global_serializer:
        raise ValueError("序列化器未初始化，请先调用 set_global_serializer()")
    return confirm_token(token, _global_serializer, expiration)
