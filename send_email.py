import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer

class EmailService:
    """邮件服务类"""
    
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.ts = URLSafeTimedSerializer(secret_key)
        self._load_mail_config()
    
    def _load_mail_config(self):
        """加载邮件配置"""
        # 发送邮件配置
        try:
            from config import MAIL_CONFIG
            self.mail_server = MAIL_CONFIG.get('MAIL_SERVER')
            self.mail_port = int(MAIL_CONFIG.get('MAIL_PORT', 25))
            self.mail_username = MAIL_CONFIG.get('MAIL_USERNAME')
            self.mail_password = MAIL_CONFIG.get('MAIL_PASSWORD')
            self.mail_default_sender = MAIL_CONFIG.get('MAIL_DEFAULT_SENDER')
            self.mail_use_tls = MAIL_CONFIG.get('MAIL_USE_TLS', True)
            self.mail_use_ssl = MAIL_CONFIG.get('MAIL_USE_SSL', False)
            # 验证必要的配置是否存在
            if not all([self.mail_server, self.mail_username, self.mail_password, self.mail_default_sender]):
                raise ValueError("邮件配置不完整")
            print("从配置文件读取邮件设置成功")
            self.mail_enabled = True
        except (ImportError, ValueError):
            # 如果没有配置文件或配置不完整,则从环境变量读取
            self.mail_server = os.environ.get('MAIL_SERVER')
            self.mail_port = int(os.environ.get('MAIL_PORT', 587))
            self.mail_username = os.environ.get('MAIL_USERNAME')
            self.mail_password = os.environ.get('MAIL_PASSWORD')
            self.mail_default_sender = os.environ.get('MAIL_DEFAULT_SENDER')
            self.mail_use_tls = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
            self.mail_use_ssl = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
            # 验证环境变量配置
            if not all([self.mail_server, self.mail_username, self.mail_password, self.mail_default_sender]):
                print("警告：邮件配置不完整,邮件功能将被禁用")
                self.mail_enabled = False
            else:
                self.mail_enabled = True
                print("从环境变量读取邮件设置成功")

    def send_email_async(self, to, subject, template):
        """异步发送邮件的函数"""
        def send_mail_thread():
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.mail_default_sender
                msg['To'] = to
                
                part = MIMEText(template, 'html')
                msg.attach(part)
                
                # 根据配置决定使用SSL还是TLS
                if self.mail_use_ssl:
                    server = smtplib.SMTP_SSL(self.mail_server, self.mail_port)
                else:
                    server = smtplib.SMTP(self.mail_server, self.mail_port)
                    if self.mail_use_tls:
                        server.starttls()
                
                # 如果提供了用户名和密码,则进行登录
                if self.mail_username and self.mail_password:
                    server.login(self.mail_username, self.mail_password)
                
                server.sendmail(self.mail_default_sender, to, msg.as_string())
                server.quit()
                print(f"邮件发送成功至: {to}")
            except Exception as e:
                print(f"邮件发送失败: {str(e)}")
        
        # 启动新线程发送邮件
        thread = threading.Thread(target=send_mail_thread)
        thread.start()
        print(f"开始异步发送邮件至: {to}")

    def send_email(self, to, subject, template):
        """发送邮件的辅助函数,现在调用异步版本"""
        if not self.mail_enabled:
            print("邮件功能已禁用，无法发送邮件")
            return False
        
        self.send_email_async(to, subject, template)
        return True

    def generate_confirmation_token(self, email):
        """生成邮箱确认令牌"""
        return self.ts.dumps(email, salt='email-confirm-salt')

    def confirm_token(self, token, expiration=3600):
        """验证令牌"""
        try:
            email = self.ts.loads(token, salt='email-confirm-salt', max_age=expiration)
            return email
        except:
            return None


_email_service = None

def init_email_service(secret_key):
    """初始化邮件服务"""
    global _email_service
    _email_service = EmailService(secret_key)
    return _email_service

def send_email_async(to, subject, template):
    """异步发送邮件的函数"""
    if _email_service:
        return _email_service.send_email_async(to, subject, template)
    else:
        print("邮件服务未初始化")

def send_email(to, subject, template):
    """发送邮件的辅助函数,现在调用异步版本"""
    if _email_service:
        return _email_service.send_email(to, subject, template)
    else:
        print("邮件服务未初始化")
        return False

def generate_confirmation_token(email):
    """生成邮箱确认令牌"""
    if _email_service:
        return _email_service.generate_confirmation_token(email)
    else:
        print("邮件服务未初始化")
        return None

def confirm_token(token, expiration=3600):
    """验证令牌"""
    if _email_service:
        return _email_service.confirm_token(token, expiration)
    else:
        print("邮件服务未初始化")
        return None
