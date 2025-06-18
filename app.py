"""会议智控系统
这个 Flask 应用程序实现了一个会议智控系统,允许用户注册、登录、预订会议室、编辑和取消预订。管理员可以管理用户和会议室。
模块:
- os: 提供与操作系统交互的功能
- flask_sqlalchemy: 提供 SQLAlchemy 数据库集成
- datetime: 提供日期和时间操作
- flask: 提供 Flask 框架的核心功能
- flask_login: 提供用户会话管理
配置:
- SECRET_KEY: Flask 应用程序的密钥
- SQLALCHEMY_DATABASE_URI: 数据库 URI
- SESSION_COOKIE_SECURE: 启用安全的会话 Cookie
- REMEMBER_COOKIE_SECURE: 启用安全的记住我 Cookie
- SESSION_COOKIE_HTTPONLY: 启用 HttpOnly 会话 Cookie
辅助函数:
- get_time_slots: 将时间段划分为固定时间槽
- check_room_availability: 检查会议室在指定时间段内的可用性
模型:
- User: 用户模型,包含用户名、密码、管理员标志和预订关系
- Room: 会议室模型,包含名称、容量、总槽位数、最大预订数、描述和预订关系
- Reservation: 预订模型,包含会议室 ID、用户 ID、标题、开始时间、结束时间、目的、创建时间和参会人数
- Equipment: 设备信息类,继承自db.Model
    属性：
        EquipmentID (int): 设备ID,主键
        RoomID (int): 关联的会议室ID
        EquipmentName (str): 设备名称
        Quantity (int): 设备数量
        room (relationship): 与会议室的关系
- Notification: 通知类,继承自db.Model
    属性：
        ID (int): 通知ID,主键
        UserID (int): 用户ID,外键关联到User表
        Status (str): 通知状态（'Unread'/'Read'）
        Timestamp (datetime): 通知时间
        Message (str): 通知内容
        user (relationship): 与用户的关系
- Maintenance: 会议室维护记录类,继承自db.Model
    属性：
        ID (int): 维护记录ID,主键
        RoomID (int): 会议室ID,外键关联到MeetingRoom表
        MaintenanceDate (date): 维护日期
        StartTime (datetime): 维护开始时间
        EndTime (datetime): 维护结束时间
        Description (text): 维护描述
        Status (str): 维护状态（Scheduled计划中/In Progress进行中/Completed已完成/Cancelled已取消）
        CreatedAt (datetime): 创建时间
        UpdatedAt (datetime): 更新时间
        room (relationship): 与会议室的关系
- MeetingMaterials: 会议资料类,继承自db.Model
    属性：
        ID (int): 资料ID,主键
        BookingID (int): 预订ID,外键关联到Booking表
        UserID (int): 上传用户ID,外键关联到User表
        Title (str): 资料标题
        FilePath (str): 文件路径
        FileName (str): 文件名称
        FileSize (int): 文件大小(bytes)
        FileType (str): 文件类型
        UploadTime (datetime): 上传时间
        Status (str): 状态（Active/Deleted）
        Description (text): 资料描述
    关联关系：
        booking (relationship): 与Booking表的关系
        user (relationship): 与User表的关系
路由:
- index: 首页
- login: 用户登录
- register: 用户注册
- dashboard: 用户仪表盘
- add_room: 添加会议室（管理员）
- edit_room: 编辑会议室（管理员）
- delete_room: 删除会议室（管理员）
- new_reservation: 创建新预订
- cancel_reservation: 取消预订
- edit_reservation: 编辑预订
- admin_reservations: 管理员查看所有预订
- delete_reservation: 管理员删除预订
- edit_reservation: 统一的编辑预订页面（支持管理员和普通用户）
- admin_users: 管理员查看所有用户
- admin_add_user: 管理员添加用户
- admin_edit_user: 管理员编辑用户
- admin_delete_user: 管理员删除用户
- available_rooms: 获取可用会议室
- about: 关于页面
- forgot_password: 忘记密码页面
- admin_rooms: 管理员查看所有会议室
- change_password: 用户修改密码
- logout: 用户登出
- statistics: 数据统计
- admin_logs: 管理员查看系统日志
其他功能:
- cleanup_expired_reservations: 清理过期的预订
- before_request: 每次请求前清理过期的预订
主程序:
- 初始化数据库表
- 运行 Flask 应用程序
"""
import os
import json
import threading
import re
import atexit
import config
from dotenv import load_dotenv
from file_utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

# 创建 Flask 应用实例
app = Flask(__name__)

# 加载配置
def load_config(app):
    """加载应用配置"""
    try:
        app.config.from_object(config)
        print("从 config.py 加载配置成功")
    except ImportError:
        print("config.py 不存在,从环境变量加载配置")
        load_dotenv()
        
        # 基础配置
        app.config["SECRET_KEY"] = os.environ.get(
            "SECRET_KEY", "default-secret-key-change-in-production"
        )
        
        # 数据库配置
        # 云服务器
        # DB_USERNAME = os.environ.get('DB_USERNAME', 'meetingroom')
        # DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Meeting-room0')
        # DB_HOST = os.environ.get('DB_HOST', '8.134.119.146')
        # DB_NAME = os.environ.get('DB_NAME', 'test_meeting_rooms')
        # 本地测试环境
        DB_USERNAME = os.environ.get("DB_USERNAME", "root")
        DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
        DB_HOST = os.environ.get("DB_HOST", "localhost")
        DB_NAME = os.environ.get("DB_NAME", "test_meeting_rooms")
        DB_PORT = os.environ.get("DB_PORT", "3306")
        # PythonAnywhere
        # DB_USERNAME = os.environ.get('DB_USERNAME', 'LianSifanTest')
        # DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Meeting-room0')
        # DB_HOST     = os.environ.get('DB_HOST', 'LianSifanTest.mysql.pythonanywhere-services.com')
        # DB_NAME     = os.environ.get('DB_NAME', 'LianSifanTest$ICCS ')
        # DB_PORT = int(os.environ.get('DB_PORT', 3306))

        if not DB_PASSWORD:
            print("警告: 数据库密码未设置,请设置 DB_PASSWORD 环境变量")
        
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        # 安全配置
        app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "True").lower() == "true"
        app.config["REMEMBER_COOKIE_SECURE"] = os.environ.get("REMEMBER_COOKIE_SECURE", "True").lower() == "true"
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        print("从环境变量加载配置完成")

load_config(app)
# 添加内置类型到模板全局变量
app.jinja_env.globals['int'] = int
app.jinja_env.globals['str'] = str
app.jinja_env.globals['float'] = float


# 初始化数据库实例
db = SQLAlchemy(app)
# 初始化 Flask-Login 管理器
login_manager = LoginManager(app)
# 设置登录视图的端点
login_manager.login_view = 'login'
# 从配置获取最大会议数量
MAX_TOTAL_MEETINGS = app.config.get('MAX_TOTAL_MEETINGS', 10000)
# 初始化后台调度器,配置支持多线程并发执行
executors = {
    # 最多支持的并发任务数
    'default': ThreadPoolExecutor(20), 
}
job_defaults = {
    'coalesce': False,        # 不合并任务
    'max_instances': 3,       # 每个任务最多实例数
    'misfire_grace_time': 30  # 超时宽限时间30秒
}
scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
scheduler.start()
# 确保在应用退出时关闭调度器
atexit.register(lambda: scheduler.shutdown())

# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化邮件服务
from send_email import init_email_service, send_email, send_email_async, generate_confirmation_token, confirm_token

# 初始化邮件服务
email_service = init_email_service(app.config['SECRET_KEY'])


# 辅助函数

## 时间槽
def get_time_slots(start_time, end_time, slot_minutes=15):
    """
    将时间段划分为固定时间槽,返回一个时间槽列表
    """
    slots = []
    current = start_time
    while current < end_time:
        slots.append(current)
        current += timedelta(minutes=slot_minutes)
    return slots

## 日志 获取客户端IP地址
def get_client_ip():
    """获取客户端真实IP地址,考虑代理服务器和负载均衡器的情况"""
    # 按优先级顺序检查各种头部
    headers_to_check = [
        'X-Forwarded-For',      
        'X-Real-IP',            
        'X-Forwarded',          
        'X-Cluster-Client-IP',  
        'CF-Connecting-IP',     
        'True-Client-IP',       
    ]
    
    for header in headers_to_check:
        ip = request.headers.get(header)
        if ip:
            # X-Forwarded-For 可能包含多个IP,取第一个
            if ',' in ip:
                ip = ip.split(',')[0].strip()
            # 验证IP格式
            if ip and ip != 'unknown':
                return ip
    
    # 如果没有找到代理头部,使用直接连接的IP
    return request.environ.get('REMOTE_ADDR', 'unknown')

## 日志
def create_log(action, description, user_id=None):
    """创建系统操作日志"""
    try:
        # 如果没有指定用户ID,尝试使用当前登录用户
        if user_id is None:
            from flask_login import current_user
            if current_user.is_authenticated:
                user_id = current_user.UserID
            else:
                # 如果没有当前用户,可能是系统操作或未登录操作
                # 这种情况下可以考虑创建一个系统用户或跳过日志记录
                return
        
        # 获取客户端IP地址
        ip_address = get_client_ip()
        
        # 创建日志记录
        log_entry = Log(
            UserID=user_id,
            Action=action,
            Description=description,
            IPAddress=ip_address,
            Timestamp=datetime.now()
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
    except Exception as e:
        # 日志记录失败不应该影响主要业务流程
        print(f"创建日志失败: {str(e)}")
        # 回滚数据库事务以确保数据一致性
        try:
            db.session.rollback()
        except:
            pass

## 会议室可用性检查
def check_room_availability(room_id, start_time, end_time, user_id=None, exclude_reservation_id=None):
    """检查会议室在指定时间段内的可用性"""
    # 检查会议室是否存在
    room = db.session.get(Room, room_id)
    if not room:
        return False, "会议室不存在"
    
    # 检查会议室状态
    if room.Status != 'Available':
        return False, f"会议室当前状态为{room.Status},不可用"

    # 检查是否在维护期间
    now = datetime.now()
    
    # 如果有过期的维护记录,先更新状态
    update_room_status_after_maintenance()
    
    maintenance = Maintenance.query.filter(
        Maintenance.RoomID == room_id,
        Maintenance.Status.in_(['Scheduled', 'In Progress']),
        # 检查维护时间是否与预订时间有重叠
        ((Maintenance.StartTime <= start_time) & (Maintenance.EndTime > start_time)) |
        ((Maintenance.StartTime < end_time) & (Maintenance.EndTime >= end_time)) |
        ((Maintenance.StartTime >= start_time) & (Maintenance.EndTime <= end_time))
    ).first()

    if maintenance:
        maintenance_period = f"{maintenance.StartTime.strftime('%Y-%m-%d %H:%M')} 至 {maintenance.EndTime.strftime('%Y-%m-%d %H:%M')}"
        return False, f"会议室在{maintenance_period}期间进行维护"

    # 检查时间段是否合理
    if start_time >= end_time:
        return False, "开始时间必须早于结束时间"

    # 检查是否被其他用户预订
    query = Reservation.query.filter(
        Reservation.RoomID == room_id,
        Reservation.EndTime > start_time,
        Reservation.StartTime < end_time,
        Reservation.Status.in_(['Confirmed', 'Pending'])
    )
    
    # 如果提供了user_id,排除该用户的预订
    if user_id:
        query = query.filter(Reservation.UserID != user_id)

    # 如果提供了exclude_reservation_id,排除该预订
    if exclude_reservation_id:
        query = query.filter(Reservation.ID != exclude_reservation_id)

    # 在个人会议室管理模式下,检查是否有重叠预订
    overlapping_reservations = query.count()
    
    # 在个人会议室管理模式下,每个会议室只能有一个预订
    if overlapping_reservations > 0:
        return False, "所选时间段该会议室已被预订"
    
    # 如果没有重叠预订,返回可用
    return True, "可用"

## 用户并发预订检查
def check_user_concurrent_reservations(user_id, start_time, end_time, max_concurrent=5, exclude_reservation_id=None):
    """检查用户在指定时间段内的并发预订数量"""
    # 检查用户在该时间段内的并发预订数量
    concurrent_reservations = Reservation.query.filter(
        Reservation.UserID == user_id,
        Reservation.EndTime > start_time,
        Reservation.StartTime < end_time,
        Reservation.Status.in_(['Confirmed', 'Pending'])
    )
    
    # 如果提供了exclude_reservation_id,排除该预订
    if exclude_reservation_id:
        concurrent_reservations = concurrent_reservations.filter(
            Reservation.ID != exclude_reservation_id
        )
    
    concurrent_count = concurrent_reservations.count()
    remaining = max_concurrent - concurrent_count
    
    # 检查是否超过了最大并发预订数量
    if concurrent_count >= max_concurrent:
        return False, f"您在该时间段内已有{concurrent_count}个预订,超过了最大限制({max_concurrent})"
    
    return True, f"当前已预订: {concurrent_count}个,还可预订: {remaining}个会议室"

## 自动确认预订
def auto_confirm_reservation(reservation_id):
    """自动确认预订函数,该函数在预订创建5分钟后被调度器调用,自动将状态从'Pending'更新为'Confirmed'"""
    print(f"====== 开始执行自动确认预订 ID: {reservation_id} ======")
    try:
        with app.app_context():
            # 获取预订记录
            reservation = db.session.get(Reservation, reservation_id)
            if not reservation:
                print(f"预订ID {reservation_id} 不存在,可能已被删除")
                return
            
            # 检查预订状态是否仍为Pending
            if reservation.Status != 'Pending':
                print(f"预订ID {reservation_id} 状态已变更为 {reservation.Status},无需自动确认")
                return
            
            # 更新状态为已确认
            reservation.Status = 'Confirmed'
            
            # 发送通知给预订用户
            try:
                send_notification(
                    reservation.UserID,
                    f'您预订的会议室 {reservation.room.RoomName} ({reservation.StartTime.strftime("%Y-%m-%d %H:%M")} - {reservation.EndTime.strftime("%H:%M")}) 已自动确认。'
                )
                print(f"已发送自动确认通知给用户 {reservation.UserID}")
            except Exception as notify_error:
                print(f"发送通知失败: {str(notify_error)}")
            
            # 记录自动确认操作日志
            try:
                reservation_info = f'会议室: {reservation.room.RoomName}, 时间: {reservation.StartTime.strftime("%Y-%m-%d %H:%M")}-{reservation.EndTime.strftime("%H:%M")}, 预订人: {reservation.user.UserName}'
                create_log('系统自动确认预订', f'预订 ({reservation_info}) 已自动确认', reservation.UserID)
                print(f"已记录自动确认操作日志")
            except Exception as log_error:
                print(f"记录日志失败: {str(log_error)}")
            
            # 提交数据库更改
            db.session.commit()
            print(f"预订ID {reservation_id} 已成功自动确认")
            
    except Exception as e:
        print(f"自动确认预订失败: {str(e)}")
        import traceback
        print(f"错误跟踪: {traceback.format_exc()}")
        try:
            db.session.rollback()
        except:
            pass

## 调度自动确认任务
def schedule_auto_confirmation(reservation_id):
    """调度自动确认任务,该函数为指定的预订安排5分钟后的自动确认任务"""
    try:
        # 计算5分钟后的时间
        confirm_time = datetime.now() + timedelta(minutes=5)
        
        # 添加调度任务
        job_id = f"auto_confirm_{reservation_id}"
        scheduler.add_job(
            func=auto_confirm_reservation,
            trigger='date',
            run_date=confirm_time,
            args=[reservation_id],
            id=job_id,
            replace_existing=True
        )
        
        print(f"已安排预订ID {reservation_id} 在 {confirm_time.strftime('%Y-%m-%d %H:%M:%S')} 自动确认")
        
    except Exception as e:
        print(f"调度自动确认任务失败: {str(e)}")
        import traceback
        print(f"错误跟踪: {traceback.format_exc()}")

## 取消自动确认任务
def cancel_auto_confirmation(reservation_id):
    """取消已调度的自动确认任务,该函数在手动确认或取消预订时被调用,用于移除待执行的自动确认任务"""
    try:
        job_id = f"auto_confirm_{reservation_id}"
        
        # 检查任务是否存在
        job = scheduler.get_job(job_id)
        if job:
            scheduler.remove_job(job_id)
            print(f"已取消预订ID {reservation_id} 的自动确认任务")
            return True
        else:
            print(f"预订ID {reservation_id} 的自动确认任务不存在或已执行")
            return False
            
    except Exception as e:
        print(f"取消自动确认任务失败: {str(e)}")
        import traceback
        print(f"错误跟踪: {traceback.format_exc()}")
        return False

## 获取待执行的自动确认任务
def get_pending_auto_confirmations():
    """
    获取所有待执行的自动确认任务信息
    返回包含任务信息的列表,用于监控和调试
    """
    try:
        pending_jobs = []
        for job in scheduler.get_jobs():
            if job.id.startswith('auto_confirm_'):
                reservation_id = job.id.replace('auto_confirm_', '')
                pending_jobs.append({
                    'reservation_id': reservation_id,
                    'scheduled_time': job.next_run_time,
                    'job_id': job.id
                })
        return pending_jobs
    except Exception as e:
        print(f"获取待执行任务失败: {str(e)}")
        return []

## 用户类
class User(UserMixin, db.Model):
    """
    用户类,继承自UserMixin和db.Model
    属性:
        UserID (int): 用户ID,主键
        UserName (str): 用户名,唯一且不能为空
        Password (str): 密码,不能为空
        Email (str): 电子邮箱,用于验证和找回密码
        EmailVerified (bool): 邮箱是否已验证
        VerificationToken (str): 邮箱验证令牌
        Role (str): 用户角色,管理员/经理/普通用户
        reservations (list): 用户的预订关系
    方法:
        set_password(password):
            设置用户密码,使用MD5加密
        check_password(password):
            检查用户密码是否正确,使用MD5加密比较
        generate_verification_token():
            生成邮箱验证令牌
    """
    __tablename__ = 'User'
    # 用户ID,主键
    UserID = db.Column(db.Integer, primary_key=True)
    # 用户名,唯一且不能为空
    UserName = db.Column(db.String(100), unique=True, nullable=False)
    # 密码,不能为空
    Password = db.Column(db.String(255), nullable=False)
    # 电子邮箱
    Email = db.Column(db.String(100), unique=True, nullable=True)
    # 邮箱验证状态
    EmailVerified = db.Column(db.Boolean, default=False)
    # 验证令牌
    VerificationToken = db.Column(db.String(255), nullable=True)
    # 用户角色
    Role = db.Column(db.String(50), nullable=False)
    # 头像路径
    Avatar = db.Column(db.String(255), nullable=True)
    # 用户的预订关系
    reservations = db.relationship('Reservation', backref='user', lazy=True, foreign_keys='Reservation.UserID')
    
    # 为了与Flask-Login兼容
    @property
    def id(self):
        return self.UserID
        
    @property
    def is_admin(self):
        return self.Role == 'admin'
        
    @property
    def username(self):
        return self.UserName

    def set_password(self, password):
        # 设置用户密码,使用MD5加密
        import hashlib
        self.Password = hashlib.md5(password.encode()).hexdigest()

    def check_password(self, password):
        # 检查用户密码是否正确,使用MD5加密比较
        import hashlib
        return self.Password == hashlib.md5(password.encode()).hexdigest()
        
    def generate_verification_token(self):
        # 生成邮箱验证令牌
        token = generate_confirmation_token(self.Email)
        self.VerificationToken = token
        return token

## 日志类
class Log(db.Model):
    """
    日志类,记录系统操作日志
    """
    __tablename__ = 'Log'
    ID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    Action = db.Column(db.String(100), nullable=False)
    Timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    Description = db.Column(db.Text)
    IPAddress = db.Column(db.String(45)) 
    # 建立与用户的关系
    user = db.relationship('User', backref=db.backref('logs', lazy=True))

## 会议室类
class Room(db.Model):
    """
    会议室类,继承自db.Model
    属性:
        RoomID (int): 会议室ID,主键
        RoomNumber (str): 房间号,唯一标识
        RoomName (str): 会议室名称,不能为空
        Capacity (int): 会议室容量,不能为空
        Equipment (str): 会议室设备
        Status (str): 会议室状态
        RoomType (str): 会议室类型（线上/线下）
        Location (str): 会议室位置（线下会议室）
        MeetingLink (str): 会议链接（线上会议室）
        Floor (str): 楼层信息
        Building (str): 建筑信息
        Description (str): 会议室详细描述
        reservations (list): 会议室的预订关系
    """
    __tablename__ = 'MeetingRoom'
    # 会议室ID,主键
    RoomID = db.Column(db.Integer, primary_key=True)
    # 房间号,唯一标识
    RoomNumber = db.Column(db.String(50), nullable=False, unique=True)
    # 会议室名称,不能为空
    RoomName = db.Column(db.String(100), nullable=False)
    # 会议室容量,不能为空
    Capacity = db.Column(db.Integer, nullable=False)
    # 会议室设备
    Equipment = db.Column(db.String(255))
    # 会议室状态
    Status = db.Column(db.String(50), nullable=False, default='Available')
    # 会议室类型（线上/线下）
    RoomType = db.Column(db.String(20), nullable=False, default='Offline')
    # 会议室位置（线下会议室）
    Location = db.Column(db.String(255), nullable=True)
    # 会议链接（线上会议室）
    MeetingLink = db.Column(db.String(1000), nullable=True)
    # 楼层信息
    Floor = db.Column(db.String(20), nullable=True)
    # 建筑信息
    Building = db.Column(db.String(50), nullable=True)
    # 会议室详细描述
    Description = db.Column(db.Text, nullable=True)
    # 会议室的预订关系 - 使用passive_deletes避免自动更新外键
    reservations = db.relationship('Reservation', backref='room', lazy=True, 
                                  foreign_keys='Reservation.RoomID', passive_deletes=True)
    
    # 兼容原有代码
    @property
    def id(self):
        return self.RoomID
    
    @property
    def room_number(self):
        return self.RoomNumber
        
    @property
    def name(self):
        return self.RoomName
        
    @property
    def capacity(self):
        return self.Capacity
    
    @property
    def room_type(self):
        return self.RoomType
    
    @property
    def location(self):
        return self.Location
    
    @property
    def meeting_link(self):
        return self.MeetingLink
    
    @property
    def floor(self):
        return self.Floor
    
    @property
    def building(self):
        return self.Building
    
    @property
    def description(self):
        return self.Description if self.Description else ''
    
    # 兼容属性,每个独立房间只能同时被一个会议预订
    @property
    def total_slots(self):
        """个别管理模式下,每个房间只能同时被一个会议预订"""
        return 1
    
    @total_slots.setter 
    def total_slots(self, value):
        """个别管理模式下忽略设置槽位数"""
        pass
    
    # 设置兼容属性
    max_reservations = 5  # 默认值


## 预订类
class Reservation(db.Model):
    """
    预订类,表示会议室预订信息。
    """
    __tablename__ = 'Booking'
    ID = db.Column(db.Integer, primary_key=True)
    RoomID = db.Column(db.Integer, db.ForeignKey('MeetingRoom.RoomID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    StartTime = db.Column(db.DateTime, nullable=False)
    EndTime = db.Column(db.DateTime, nullable=False)
    Status = db.Column(db.String(50), nullable=False, default='Pending')
    Title = db.Column(db.String(100), default='')
    Purpose = db.Column(db.Text, nullable=True)
    Attendees = db.Column(db.Integer, default=1)
    MeetingType = db.Column(db.String(20), nullable=False, default='Offline')
    MeetingPassword = db.Column(db.String(255), nullable=True)
    
    # 添加 id 属性的 getter 方法
    @property
    def id(self):
        return self.ID
        
    @property
    def title(self):
        return self.Title
        
    @title.setter
    def title(self, value):
        self.Title = value
        
    @property
    def room_id(self):
        return self.RoomID
        
    @room_id.setter
    def room_id(self, value):
        self.RoomID = value
        
    @property
    def user_id(self):
        return self.UserID
        
    @property
    def start_time(self):
        return self.StartTime
        
    @start_time.setter
    def start_time(self, value):
        self.StartTime = value
        
    @property
    def end_time(self):
        return self.EndTime
        
    @end_time.setter
    def end_time(self, value):
        self.EndTime = value
        
    @property
    def purpose(self):
        return self.Purpose
        
    @purpose.setter
    def purpose(self, value):
        self.Purpose = value
        
    @property
    def attendees(self):
        return self.Attendees
        
    @attendees.setter
    def attendees(self, value):
        self.Attendees = value
    
    # 其他兼容属性
    created_at = datetime.now()


@login_manager.user_loader
def load_user(user_id):
    """
    根据用户ID加载用户
    """
    return db.session.get(User, int(user_id))

# 路由定义

# 首页路由
@app.route('/')
def index():
    """
    渲染首页模板
    """
    return render_template('shared/index.html')

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录的路由。
    该函数执行以下操作：
    1. 如果请求方法为POST,获取并验证表单数据。
    2. 根据用户名或邮箱查询用户信息。
    3. 检查用户是否存在以及密码是否正确。
    4. 如果验证通过,登录用户并重定向到仪表盘。
    5. 如果验证失败,显示错误消息。
    返回:
        werkzeug.wrappers.Response: 渲染登录页面或重定向到仪表盘的响应对象。
    """
    # 添加调试信息
    print("====== 登录请求开始处理 ======")
    if request.method == 'POST':
        username_or_email = request.form.get('username')  # 现在可以是用户名或邮箱
        password = request.form.get('password')
        print(f"\u8bf7求数据: 用户名或邮箱={username_or_email}")
        
        # 尝试查询用户 - 同时支持用户名和邮箱登录
        user = User.query.filter((User.UserName == username_or_email) | 
                               (User.Email == username_or_email)).first()
        print(f"\u67e5询结果: 用户={'存在' if user else '不存在'}")
        
        if user:
            # 打印用户存在时的信息
            import hashlib
            input_password_hash = hashlib.md5(password.encode()).hexdigest()
            print(f"\u7528户ID: {user.UserID}")
            print(f"\u7528户角色: {user.Role}")
            print(f"\u8f93入密码哈希: {input_password_hash}")
            print(f"\u6570据库密码哈希: {user.Password}")
            print(f"\u5bc6码比较结果: {input_password_hash == user.Password}")
            print(f"\u90ae箱验证状态: {user.EmailVerified}")
        
        if user and user.check_password(password):
            # 检查邮箱验证状态
            if user.Email and not user.EmailVerified:
                flash('请先验证您的邮箱,验证链接已发送到您的邮箱。')
                return render_template('shared/login.html')
                
            print("\u8ba4证成功,正在登录用户...")
            login_user(user)
            
            # 记录登录日志
            create_log('登录', f'用户 {user.UserName} 登录成功', user.UserID)
            
            print("\u767b录成功,重定向到仪表盘")
            return redirect(url_for('dashboard'))
            
        print("\u8ba4证失败,显示错误消息")
        # 记录登录失败日志
        if user:
            create_log('登录失败', f'用户 {user.UserName} 登录失败：密码错误', user.UserID)
        flash('用户名/邮箱或密码错误')
    else:
        print("GET请求,展示登录页面")
    
    print("====== 登录请求处理结束 ======")
    return render_template('shared/login.html')

# 确认邮箱
@app.route('/confirm-email/<token>')
def confirm_email(token):
    """
    邮箱验证路由
    参数:
        token (str): 验证令牌
    返回:
        werkzeug.wrappers.Response: 重定向到登录页面或错误页面
    """
    try:
        # 解析令牌并获取邮箱
        print(f"开始验证令牌: {token}")
        email = confirm_token(token)
        print(f"令牌解析结果邮箱: {email}")
        
        if not email:
            print("令牌无效或已过期")
            flash('无效的验证链接或链接已过期。')
            return redirect(url_for('login'))
            
        # 使用解析出的邮箱查找用户
        user = User.query.filter_by(Email=email).first()
        
        if user:
            print(f"找到用户: {user.UserName}, 邮箱: {user.Email}")
            # 更新用户的邮箱验证状态
            user.EmailVerified = True
            user.VerificationToken = None  # 清除令牌
            db.session.commit()
            print("验证成功,用户邮箱已验证")
            flash('邮箱验证成功！您现在可以登录了。')
            return redirect(url_for('login'))
        else:
            print(f"未找到邮箱为 {email} 的用户")
            flash('找不到对应的用户账号。')
            return redirect(url_for('login'))
    except Exception as e:
        print(f"验证过程发生错误: {str(e)}")
        flash('验证邮箱时出错。请重试或联系管理员。')
        return redirect(url_for('login'))

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册的路由。
    该函数执行以下操作：
    1. 如果请求方法为POST,获取并验证表单数据。
    2. 检查用户名、密码和确认密码是否为空。
    3. 检查两次输入的密码是否一致。
    4. 检查用户名和邮箱是否已存在。
    5. 创建新用户并提交数据库会话。
    6. 发送邮箱验证邮件。
    7. 显示注册成功的消息并重定向到登录页面。
    返回:
        werkzeug.wrappers.Response: 渲染注册页面或重定向到登录页面的响应对象。
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 验证表单数据
        if not username or not password or not confirm_password or not email:
            flash('请填写所有必填字段')
            return render_template('shared/register.html')

        if password != confirm_password:
            flash('两次输入的密码不一致')
            return render_template('shared/register.html')

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(UserName=username).first()
        if existing_user:
            flash('用户名已存在,请选择其他用户名')
            return render_template('shared/register.html')
            
        # 检查邮箱是否已存在
        existing_email = User.query.filter_by(Email=email).first()
        if existing_email:
            flash('邮箱已被注册,请使用其他邮箱')
            return render_template('shared/register.html')

        # 创建新用户
        new_user = User(
            UserName=username,
            Password='',  # 先设置为空,然后使用set_password方法设置
            Email=email,
            EmailVerified=False,
            Role='user'
        )
        new_user.set_password(password)  # 使用set_password方法加密密码
        
        # 生成验证令牌
        token = new_user.generate_verification_token()
        
        # 保存用户
        db.session.add(new_user)
        db.session.commit()
        
        # 记录用户注册日志
        create_log('用户注册', f'新用户 {username} 注册成功', new_user.UserID)
        
        # 生成确认链接
        confirm_url = url_for('confirm_email', token=token, _external=True)
        
        # 发送确认邮件
        html = render_template('email/confirm_email.html', confirm_url=confirm_url, username=username)
        subject = "会议室预订系统 - 请验证您的邮箱"
        
        # 尝试发送邮件
        try:
            send_email(email, subject, html)
            flash('注册成功！请查看您的邮箱并点击验证链接。')
        except Exception as e:
            flash('注册成功,但发送验证邮件失败。请联系管理员。')
            print(f'发送验证邮件失败: {str(e)}')
            
        return redirect(url_for('login'))

    return render_template('shared/register.html')

# 仪表盘
@app.route('/dashboard')
@login_required
def dashboard():
    """
    仪表盘视图函数
    """
    try:
        # 获取当前用户的所有预订,按开始时间排序
        user_reservations = Reservation.query.filter_by(UserID=current_user.UserID)\
            .order_by(Reservation.StartTime.desc()).all()
        
        # 获取所有会议室
        rooms = Room.query.all()
        
        # 获取用户的会议资料数量和详细信息
        user_materials_count = MeetingMaterials.query.filter_by(
            UserID=current_user.UserID, 
            Status='Active'
        ).count()
        
        user_materials = MeetingMaterials.query.filter_by(
            UserID=current_user.UserID, 
            Status='Active'
        ).order_by(MeetingMaterials.UploadTime.desc()).all()
        
        return render_template('dashboard.html',
                           rooms=rooms,
                           user_reservations=user_reservations,
                           user_materials_count=user_materials_count,
                           user_materials=user_materials)
    except Exception as e:
        print(f"仪表盘视图出错: {str(e)}")
        flash(f'加载仪表盘时出错: {str(e)}')
        return render_template('shared/error.html', error=str(e))

# 添加会议室
@app.route('/room/add', methods=['GET', 'POST'])
@login_required
def add_room():
    """
    添加会议室的路由。
    该函数执行以下操作：
    1. 检查当前用户是否为管理员,如果不是则提示需要管理员权限。
    2. 如果请求方法为POST,获取并验证表单数据。
    3. 创建新会议室并提交数据库会话。
    4. 显示会议室添加成功的消息并重定向到仪表盘。
    返回:
        werkzeug.wrappers.Response: 渲染添加会议室页面或重定向到仪表盘的响应对象。
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        room_number = request.form.get('room_number')
        name = request.form.get('name')
        capacity = int(request.form.get('capacity'))
        description = request.form.get('description', '')
        room_type = request.form.get('room_type', 'Offline')
        location = request.form.get('location', '')
        meeting_link = request.form.get('meeting_link', '')
        floor = request.form.get('floor', '')
        building = request.form.get('building', '')
        equipment = request.form.get('equipment', '')

        # 验证必填字段
        if not room_number or not name:
            flash('房间号和会议室名称为必填项')
            return redirect(url_for('add_room'))

        # 检查房间号是否已存在
        existing_room = Room.query.filter_by(RoomNumber=room_number).first()
        if existing_room:
            flash('房间号已存在,请使用其他房间号')
            return redirect(url_for('add_room'))

        # 根据房间类型设置相应的字段
        if room_type == 'Offline':
            meeting_link = None
        else:  # room.RoomType == 'Online'
            location = None
            floor = None
            building = None

        room = Room(
            RoomNumber=room_number,
            RoomName=name,
            Capacity=capacity,
            Equipment=equipment,
            RoomType=room_type,
            Location=location,
            MeetingLink=meeting_link,
            Floor=floor,
            Building=building,
            Description=description
        )
        db.session.add(room)
        db.session.commit()
        
        # 记录管理员添加会议室的操作日志
        room_info = f'房间号: {room_number}, 名称: {name}, 容量: {capacity}人, 类型: {room_type}'
        create_log('管理员添加会议室', f'管理员 {current_user.UserName} 添加了会议室 ({room_info})', current_user.UserID)
        
        flash('会议室添加成功')
        return redirect(url_for('dashboard'))

    return render_template('admin_add_room.html')

# 编辑会议室
@app.route('/room/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_room(id):
    """
    编辑会议室信息的路由。
    该函数执行以下操作：
    1. 检查当前用户是否为管理员,如果不是则提示需要管理员权限。
    2. 根据会议室ID获取会议室信息,如果会议室不存在则返回404错误。
    3. 如果请求方法为GET,渲染编辑会议室页面并传递会议室信息。
    4. 如果请求方法为POST,获取并验证表单数据。
    5. 更新会议室信息并提交数据库会话。
    6. 显示会议室信息更新成功的消息并重定向到仪表盘。
    返回:
        werkzeug.wrappers.Response: 渲染编辑会议室页面或重定向到仪表盘的响应对象。
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    room = db.get_or_404(Room, id)

    if request.method == 'POST':
        # 更新房间号（如果提供的话）
        room_number = request.form.get('room_number')
        if room_number and room_number != room.RoomNumber:
            # 检查新房间号是否已存在
            existing_room = Room.query.filter_by(RoomNumber=room_number).first()
            if existing_room:
                flash('房间号已存在,请使用其他房间号')
                return redirect(url_for('edit_room', id=id))
            room.RoomNumber = room_number
        
        room.RoomName = request.form.get('name')
        room.Capacity = int(request.form.get('capacity'))
        room.Equipment = request.form.get('equipment', '')
        room.Description = request.form.get('description', '')
        
        # 处理会议室类型字段
        room.RoomType = request.form.get('room_type', 'Offline')
        
        # 根据会议室类型设置位置或链接
        if room.RoomType == 'Offline':
            room.Location = request.form.get('location', '')
            room.Floor = request.form.get('floor', '')
            room.Building = request.form.get('building', '')
            room.MeetingLink = None
        else:  # room.RoomType == 'Online'
            room.Location = None
            room.Floor = None
            room.Building = None
            room.MeetingLink = request.form.get('meeting_link', '')

        db.session.commit()
        
        # 记录管理员编辑会议室的操作日志
        room_info = f'房间号: {room.RoomNumber}, 名称: {room.RoomName}, 容量: {room.Capacity}人, 类型: {room.RoomType}'
        create_log('管理员编辑会议室', f'管理员 {current_user.UserName} 编辑了会议室信息 ({room_info})', current_user.UserID)
        
        flash('会议室信息已更新')
        return redirect(url_for('dashboard'))

    return render_template('edit_room.html', room=room)

# 删除会议室
@app.route('/room/delete/<int:id>')
@login_required
def delete_room(id):
    """
    删除会议室的路由。
    该函数执行以下操作：
    1. 检查当前用户是否为管理员,如果不是则提示需要管理员权限。
    2. 根据会议室ID获取会议室信息,如果会议室不存在则返回404错误。
    3. 检查是否有进行中的预订，如果有则阻止删除。
    4. 删除相关的设备、预订和维护记录。
    5. 删除会议室并提交数据库会话。
    6. 显示会议室删除成功的消息并重定向到仪表盘。
    返回:
        werkzeug.wrappers.Response: 重定向到仪表盘的响应对象。
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
    
    room = db.get_or_404(Room, id)
    
    # 检查是否有进行中的预订
    from datetime import datetime
    current_time = datetime.now()
    active_reservations = Reservation.query.filter(
        Reservation.RoomID == room.RoomID,
        Reservation.StartTime <= current_time,
        Reservation.EndTime > current_time,
        Reservation.Status.in_(['Confirmed', 'Pending'])
    ).first()
    
    if active_reservations:
        flash('无法删除会议室：该会议室目前有进行中的会议', 'error')
        return redirect(url_for('admin_rooms'))
    
    try:
        # 记录管理员删除会议室的操作日志
        room_info = f'名称: {room.RoomName}, 容量: {room.Capacity}人'
        create_log('管理员删除会议室', f'管理员 {current_user.UserName} 删除了会议室 ({room_info})', current_user.UserID)
        
        # 1. 先处理所有相关的预订记录 - 设置状态为已取消
        all_reservations = Reservation.query.filter_by(RoomID=room.RoomID).all()
        
        affected_users = set()
        future_reservations_count = 0
        
        for reservation in all_reservations:
            if reservation.Status not in ['Cancelled']:
                reservation.Status = 'Cancelled'
                affected_users.add(reservation.UserID)
                if reservation.StartTime > current_time:
                    future_reservations_count += 1
        
        # 2. 先提交预订状态的更改
        db.session.commit()
        
        # 3. 删除相关的设备
        Equipment.query.filter_by(RoomID=room.RoomID).delete()
        
        # 4. 删除相关的维护记录
        Maintenance.query.filter_by(RoomID=room.RoomID).delete()
        
        # 5. 删除会议室（现在预订记录已经是取消状态，不会触发外键更新）
        db.session.delete(room)
        
        # 6. 提交所有更改
        db.session.commit()
        
        # 提供详细的删除反馈
        if future_reservations_count > 0:
            flash(f'会议室已成功删除。已取消 {future_reservations_count} 个未来的预订，影响 {len(affected_users)} 位用户。', 'warning')
        else:
            flash('会议室已成功删除', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'删除会议室时发生错误: {str(e)}', 'error')
        return redirect(url_for('admin_rooms'))
    
    return redirect(url_for('admin_rooms'))

# 新预订
@app.route('/reservation/new', methods=['GET', 'POST'])
@login_required
def new_reservation():
    """
    创建新预订的路由。
    该函数执行以下操作：
    1. 如果请求方法为POST,获取并验证表单数据。
    2. 检查开始时间和结束时间的合理性。
    3. 检查会议总数限制。
    4. 检查会议室是否存在,参会人数是否超过会议室容量。
    5. 检查用户的预订数量限制。
    6. 检查会议室在指定时间段内是否可用。
    7. 创建新预订并提交数据库会话。
    8. 显示预订成功的消息并重定向到仪表盘。
    返回:
        werkzeug.wrappers.Response: 渲染新预订页面或重定向到仪表盘的响应对象。
    """
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        title = request.form.get('title')
        # 处理时间字段的兼容性
        start_datetime_str = request.form.get('start_datetime')
        end_datetime_str = request.form.get('end_datetime')
        
        if start_datetime_str and end_datetime_str:
            # 使用完整的datetime字段
            start_time = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
        else:
            # 兼容旧的date+time字段
            date_str = request.form.get('date')
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')
            
            if date_str and start_time_str and end_time_str:
                start_time = datetime.strptime(f"{date_str} {start_time_str}", '%Y-%m-%d %H:%M')
                end_time = datetime.strptime(f"{date_str} {end_time_str}", '%Y-%m-%d %H:%M')
            else:
                flash('请完整填写日期和时间信息')
                return redirect(url_for('new_reservation'))
        purpose = request.form.get('purpose', '') or request.form.get('description', '')
        attendees = request.form.get('attendees')
        attendees = int(attendees) if attendees else 1
        # 获取新的会议类型和密码字段
        meeting_type = request.form.get('meeting_type', 'Offline')
        meeting_password = request.form.get('password', '')

        # 基本验证
        if start_time >= end_time:
            flash('开始时间必须早于结束时间')
            return redirect(url_for('new_reservation'))

        current_time = datetime.now()
        if start_time < current_time - timedelta(minutes=2):
            flash('开始时间不能早于当前时间2分钟以上')
            return redirect(url_for('new_reservation'))
            
        # 验证在线会议密码
        if meeting_type == 'Online' and not meeting_password.strip():
            flash('在线会议必须设置会议密码')
            return redirect(url_for('new_reservation'))
            return redirect(url_for('new_reservation'))

        # 验证在线会议密码
        if meeting_type == 'Online' and not meeting_password:
            flash('在线会议必须设置会议密码')
            return redirect(url_for('new_reservation'))

        # 检查总会议数限制
        total_reservations = Reservation.query.count()
        if total_reservations >= MAX_TOTAL_MEETINGS:
            flash(f'已达到会议总数限制（{MAX_TOTAL_MEETINGS}个）。请稍后再试。')
            return redirect(url_for('new_reservation'))

        # 检查会议室容量
        room = db.session.get(Room, room_id)
        if not room:
            flash('会议室不存在')
            return redirect(url_for('new_reservation'))
        if attendees > room.capacity:
            flash(f'参会人数超过会议室容量（最大容量：{room.capacity}人）')
            return redirect(url_for('new_reservation'))

        # 检查用户在该时间段内的并发预订数量
        max_concurrent_reservations = 5
        can_reserve, message = check_user_concurrent_reservations(
            current_user.UserID, start_time, end_time, max_concurrent_reservations)
        if not can_reserve and not current_user.is_admin:
            flash(message)
            return redirect(url_for('new_reservation'))

        # 使用新的可用性检查函数
        is_available, message = check_room_availability(
            room_id, start_time, end_time, user_id=current_user.UserID)
        if not is_available:
            flash(message)
            return redirect(url_for('new_reservation'))

        # 创建预订（使用数据库事务确保原子性）
        try:
            print("====== 开始创建预订 ======")
            print(f"当前用户ID: {current_user.UserID}")
            print(f"会议室ID: {room_id}")
            print(f"开始时间: {start_time}")
            print(f"结束时间: {end_time}")
            
            # 创建预订对象
            reservation = Reservation(
                RoomID=room_id,
                UserID=current_user.UserID,
                StartTime=start_time,
                EndTime=end_time,
                Status='Pending',
                Title=title,
                Purpose=purpose,
                Attendees=attendees,
                MeetingType=meeting_type,
                MeetingPassword=meeting_password if meeting_password else None
            )
            print(f"预订对象创建成功: {reservation}")
            db.session.add(reservation)
            print("预订已添加到会话")
            
            # 记录预订日志
            create_log('创建预订', f'用户 {current_user.UserName} 预订了会议室 {room.RoomName}')
            print("日志已创建")
            
            print("正在提交数据库事务...")
            db.session.commit()
            print("数据库事务提交成功")
            
            # 安排5分钟后自动确认
            try:
                schedule_auto_confirmation(reservation.ID)
                print(f"已安排预订ID {reservation.ID} 的自动确认任务")
            except Exception as schedule_error:
                print(f"安排自动确认任务失败: {str(schedule_error)}")
                # 这里不影响预订创建,只是记录错误
            
            # 向所有管理员发送预订通知
            try:
                admin_message = f"新预订通知：用户 {current_user.UserName} 预订了会议室 {room.RoomName},时间：{start_time.strftime('%Y年%m月%d日 %H:%M')} - {end_time.strftime('%H:%M')},会议主题：{title}"
                notification_count = notify_all_admins(admin_message, exclude_user_id=current_user.UserID if current_user.is_admin else None)
                print(f"已向 {notification_count} 位管理员发送预订通知")
            except Exception as notify_error:
                print(f"发送管理员通知失败: {str(notify_error)}")
                # 这里不影响预订创建,只是记录错误
            
            flash('预订成功,将在5分钟后自动确认')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"====== 预订失败 ======")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误消息: {str(e)}")
            import traceback
            print(f"错误跟踪: {traceback.format_exc()}")
            flash(f'预订失败: {str(e)}')
            return redirect(url_for('new_reservation'))

    rooms = Room.query.all()
    return render_template('new_reservation.html', rooms=rooms)

# 取消预订
@app.route('/reservation/cancel/<int:id>')
@login_required
def cancel_reservation(id):
    """
    取消预订的路由。
    该函数执行以下操作：
    1. 根据预订ID获取预订信息,如果预订不存在则返回404错误。
    2. 检查当前用户是否有权限取消此预订（预订的用户或管理员）。
    3. 取消任何待执行的自动确认任务。
    4. 将预订状态更新为"Cancelled"而不是删除记录。
    5. 显示预订取消成功的消息并重定向到仪表盘。
    返回:
        werkzeug.wrappers.Response: 重定向到仪表盘的响应对象。
    """
    reservation = db.get_or_404(Reservation, id)
    if reservation.UserID == current_user.UserID or current_user.is_admin:
        try:
            # 取消自动确认任务（如果存在）
            cancel_auto_confirmation(reservation.ID)
            
            # 发送通知给预订用户（如果是管理员取消）
            if current_user.is_admin and reservation.UserID != current_user.UserID:
                send_notification(
                    reservation.UserID,
                    f'您预订的会议室 {reservation.room.RoomName} ({reservation.StartTime.strftime("%Y-%m-%d %H:%M")} - {reservation.EndTime.strftime("%H:%M")}) 已被管理员取消。'
                )
            
            # 更新预订状态为已取消,而不是删除记录
            reservation.Status = 'Cancelled'
            db.session.commit()
            flash('预订已成功取消')
        except Exception as e:
            db.session.rollback()
            flash('取消预订失败,请稍后重试')
            # 记录错误日志
            print(f"Error canceling reservation: {str(e)}")
    else:
        flash('您没有权限取消此预订')
    return redirect(url_for('dashboard'))

# 编辑预订
@app.route('/reservation/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_reservation(id):
    """
    统一的编辑预订路由（支持管理员和普通用户）。
    该函数执行以下操作：
    1. 根据预订ID获取预订信息,如果预订不存在则返回404错误。
    2. 检查当前用户是否有权限编辑此预订（预订的用户或管理员）。
    3. 根据用户角色确定返回页面和显示模式。
    4. 如果请求方法为GET,查询所有会议室信息并渲染编辑预订页面。
    5. 如果请求方法为POST,获取并验证表单数据。
    6. 检查会议室是否存在,参会人数是否超过会议室容量。
    7. 验证开始时间和结束时间的合理性。
    8. 检查会议室在指定时间段内是否可用（排除当前预订）。
    9. 更新预订信息并提交数据库会话。
    10. 根据用户角色重定向到相应页面。
    返回:
        werkzeug.wrappers.Response: 渲染编辑预订页面或重定向到相应页面的响应对象。
    """
    reservation = db.get_or_404(Reservation, id)

    # 检查当前用户是否有权限编辑此预订
    if not (reservation.UserID == current_user.UserID or current_user.is_admin):
        flash('您没有权限编辑此预订')
        return redirect(url_for('dashboard'))

    # 确定用户角色和返回路径
    is_admin_view = current_user.is_admin
    return_url = 'admin_reservations' if is_admin_view else 'dashboard'
    return_text = '返回列表' if is_admin_view else '返回控制面板'

    if request.method == 'GET':
        rooms = Room.query.all()
        return render_template('edit_reservation.html', 
                             reservation=reservation, 
                             rooms=rooms,
                             is_admin_view=is_admin_view,
                             return_url=return_url,
                             return_text=return_text)

    if request.method == 'POST':
        title = request.form.get('title')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        purpose = request.form.get('purpose', '')
        room_id = request.form.get('room_id')
        attendees = request.form.get('attendees')
        attendees = int(attendees) if attendees else 1

        # 验证必填字段
        if not all([title, start_time_str, end_time_str, room_id]):
            flash('请填写所有必填字段')
            return redirect(url_for('edit_reservation', id=id))

        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
        except (ValueError, TypeError) as e:
            flash('日期或时间格式错误,请重新填写')
            return redirect(url_for('edit_reservation', id=id))

        room = db.session.get(Room, room_id)
        if not room:
            flash('会议室不存在')
            return redirect(url_for('edit_reservation', id=id))

        if attendees > room.capacity:
            flash(f'参会人数超过会议室容量（最大容量：{room.capacity}人）')
            return redirect(url_for('edit_reservation', id=id))

        # 验证开始时间不能晚于结束时间
        if start_time >= end_time:
            flash('开始时间必须早于结束时间')
            return redirect(url_for('edit_reservation', id=id))

        # 管理员和普通用户的时间验证稍有不同
        current_time = datetime.now()
        time_buffer = timedelta(minutes=1) if is_admin_view else timedelta(minutes=2)
        if start_time < current_time - time_buffer:
            buffer_text = "1分钟" if is_admin_view else "2分钟"
            flash(f'开始时间不能早于当前时间{buffer_text}以上')
            return redirect(url_for('edit_reservation', id=id))

        # 使用统一的可用性检查函数（如果存在）或原有逻辑
        try:
            # 尝试使用新的可用性检查函数
            is_available, message = check_room_availability(
                room_id,
                start_time,
                end_time,
                exclude_reservation_id=id
            )
            if not is_available:
                flash(message)
                return redirect(url_for('edit_reservation', id=id))
        except:
            # 回退到原有逻辑
            buffer_minutes = 10
            check_start = start_time.replace(
                minute=start_time.minute - buffer_minutes)
            check_end = end_time.replace(minute=end_time.minute + buffer_minutes)

            existing_reservation = Reservation.query.filter(
                Reservation.ID != id,
                Reservation.RoomID == room_id,
                ((Reservation.StartTime <= check_start) & (Reservation.EndTime > check_start)) |
                ((Reservation.StartTime < check_end) & (Reservation.EndTime >= check_end)) |
                ((Reservation.StartTime >= check_start)
                 & (Reservation.EndTime <= check_end))
            ).first()

            if existing_reservation:
                flash('该时间段会议室已被预订（包含10分钟准备时间）,请选择其他时间段。')
                return redirect(url_for('edit_reservation', id=id))

        # 更新预订信息
        try:
            reservation.Title = title
            reservation.RoomID = room_id
            reservation.StartTime = start_time
            reservation.EndTime = end_time
            reservation.Purpose = purpose
            reservation.Attendees = attendees
            
            db.session.commit()
            
            # 如果是管理员编辑,记录操作日志
            if is_admin_view and hasattr(current_user, 'UserID'):
                try:
                    reservation_info = f'会议室: {room.RoomName}, 时间: {start_time.strftime("%Y-%m-%d %H:%M")}-{end_time.strftime("%H:%M")}, 预订人: {reservation.user.username}'
                    create_log('管理员编辑预订', f'管理员 {current_user.UserName} 编辑了预订 ({reservation_info})', current_user.UserID)
                except:
                    pass  # 日志记录失败不影响主要功能
            
            flash('预订已更新')
            return redirect(url_for(return_url))
            
        except Exception as e:
            db.session.rollback()
            flash('更新失败,请重试')
            return redirect(url_for('edit_reservation', id=id))

    return render_template('edit_reservation.html', 
                         reservation=reservation, 
                         rooms=rooms,
                         is_admin_view=is_admin_view,
                         return_url=return_url,
                         return_text=return_text)

# 管理员查看所有预订的路由。
@app.route('/admin/reservations')
@login_required
def admin_reservations():
    """
    管理员查看所有预订的路由。
    该函数执行以下操作：
    1. 检查当前用户是否为管理员,如果不是则提示需要管理员权限。
    2. 查询所有预订信息,支持分页显示。
    3. 渲染管理员预订管理页面,并传递预订信息和分页信息。
    返回:
        werkzeug.wrappers.Response: 渲染管理员预订管理页面的响应对象。
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 限制每页最大显示条数
    if per_page > 100:
        per_page = 100
    
    # 查询预订信息并分页
    reservations_pagination = Reservation.query.order_by(
        Reservation.StartTime.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    reservations = reservations_pagination.items
    
    # 获取今天的日期用于今日预订统计
    today = datetime.now().date()
    
    return render_template('admin_reservations.html', 
                         reservations=reservations, 
                         pagination=reservations_pagination,
                         admin_view=True, 
                         today=today,
                         current_per_page=per_page)

# 查看所有预订情况的路由。
@app.route('/all_reservations')
@login_required
def view_all_reservations():
    """
    用户查看预订情况的路由。
    该函数执行以下操作：
    1. 根据用户权限查询预订信息：
       - 管理员：查询所有预订信息
       - 普通用户：只查询自己的预订信息
    2. 查询所有会议室信息,并计算每个会议室的剩余预订数量。
    3. 渲染预订查看页面,并传递预订信息和会议室信息。
    返回:
        werkzeug.wrappers.Response: 渲染预订查看页面的响应对象。
    """
    # 根据用户权限查询预订信息
    if current_user.is_admin:
        # 管理员可以查看所有预订
        reservations = Reservation.query.order_by(Reservation.StartTime.desc()).all()
    else:
        # 普通用户只能查看自己的预订
        reservations = Reservation.query.filter_by(UserID=current_user.UserID).order_by(Reservation.StartTime.desc()).all()
    
    # 获取所有会议室信息
    rooms = Room.query.all()
    
    # 获取当前时间
    now = datetime.now()
    
    # 计算每个会议室的当前可用状态
    for room in rooms:
        # 检查当前是否有正在进行的预订
        current_reservations = Reservation.query.filter_by(RoomID=room.RoomID).filter(
            (Reservation.StartTime <= now) & (Reservation.EndTime > now)
        ).count()
        
        # 如果没有正在进行的预订,则可用；否则不可用
        room.available_slots = 1 if current_reservations == 0 else 0
    
    # 根据用户权限设置视图标志
    admin_view = current_user.is_admin
    
    return render_template('all_reservations.html', reservations=reservations, rooms=rooms, admin_view=admin_view)

# 管理员删除预订的路由。
@app.route('/admin/delete_reservation/<int:id>')
@login_required
def delete_reservation(id):
    """
    管理员删除预订的路由。
    该函数执行以下操作：
    1. 检查当前用户是否为管理员,如果不是则提示需要管理员权限。
    2. 根据预订ID获取预订信息,如果预订不存在则返回404错误。
    3. 删除预订相关的所有会议资料。
    4. 删除预订并提交数据库会话。
    5. 显示预订删除成功的消息并重定向到管理员预订页面。
    返回:
        werkzeug.wrappers.Response: 重定向到管理员预订页面的响应对象。
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    try:
        reservation = db.get_or_404(Reservation, id)
        
        # 删除相关的会议资料
        MeetingMaterials.query.filter_by(BookingID=id).delete()

        # 发送通知给预订用户
        if reservation.UserID != current_user.UserID:
            send_notification(
                reservation.UserID,
                f'您预订的会议室 {reservation.room.RoomName} ({reservation.StartTime.strftime("%Y-%m-%d %H:%M")} - {reservation.EndTime.strftime("%H:%M")}) 已被管理员删除。'
            )

        # 记录管理员删除预订的操作日志
        reservation_info = f'会议室: {reservation.room.RoomName}, 时间: {reservation.StartTime.strftime("%Y-%m-%d %H:%M")}-{reservation.EndTime.strftime("%H:%M")}, 预订人: {reservation.user.username}'
        create_log('管理员删除预订', f'管理员 {current_user.UserName} 删除了预订 ({reservation_info})', current_user.UserID)

        db.session.delete(reservation)
        db.session.commit()
        flash('预订已删除')
    except Exception as e:
        db.session.rollback()
        flash('删除预订失败,请稍后重试')
        # 记录错误日志
        print(f"Error deleting reservation: {str(e)}")
    
    return redirect(url_for('admin_reservations'))

# 管理员查看所有用户的路由。
@app.route('/admin/users')
@login_required
def admin_users():
    """
    管理员查看所有用户的路由。
    该函数执行以下操作：
    1. 检查当前用户是否为管理员,如果不是则提示需要管理员权限。
    2. 查询所有用户信息并支持分页。
    3. 渲染管理员用户管理页面,并传递用户信息和分页对象。
    返回:
        werkzeug.wrappers.Response: 渲染管理员用户管理页面的响应对象。
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 限制每页显示条数的范围
    if per_page not in [10, 20, 50, 100]:
        per_page = 10
    
    # 查询用户并分页
    users_pagination = User.query.paginate(
        page=page, 
        per_page=per_page,
        error_out=False
    )
    
    # 获取统计数据
    total_users = User.query.count()
    admin_users = User.query.filter(User.is_admin == True).count()
    normal_users = User.query.filter(User.is_admin == False).count()
    
    return render_template('admin_users.html', 
                         users=users_pagination.items,
                         pagination=users_pagination,
                         current_per_page=per_page,
                         total_users=total_users,
                         admin_users=admin_users,
                         normal_users=normal_users)

# 管理员添加用户的路由。
@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    """
    管理员添加用户的路由。
    该函数执行以下操作：
    1. 检查当前用户是否为管理员,如果不是则提示需要管理员权限。
    2. 如果请求方法为POST,获取并验证表单数据。
    3. 检查用户名和密码是否为空。
    4. 检查用户名是否已存在。
    5. 创建新用户并提交数据库会话。
    6. 显示用户添加成功的消息并重定向到用户管理页面。
    返回:
        werkzeug.wrappers.Response: 渲染添加用户页面或重定向到用户管理页面的响应对象。
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'

        if not username or not password:
            flash('请填写所有必填字段')
            return redirect(url_for('admin_users'))

        existing_user = User.query.filter_by(UserName=username).first()
        if existing_user:
            flash('用户名已存在')
            return redirect(url_for('admin_users'))

        new_user = User(
            UserName=username,
            Password='',
            Role='admin' if is_admin else 'user'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # 记录管理员添加用户的操作日志
        user_type = '管理员' if is_admin else '普通用户'
        create_log('管理员添加用户', f'管理员 {current_user.UserName} 添加了新用户 {username} ({user_type})', current_user.UserID)
        
        flash('用户添加成功')
        return redirect(url_for('admin_users'))

    return render_template('admin_add_user.html')


@app.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(id):
    """
    管理员编辑用户信息的路由。
    该函数执行以下操作：
    1. 检查当前用户是否为管理员,如果不是则提示需要管理员权限。
    2. 根据用户ID获取用户信息,如果用户不存在则返回404错误。
    3. 如果请求方法为POST,获取并验证表单数据。
    4. 检查用户名是否为空,是否已存在。
    5. 更新用户信息（用户名、密码、管理员权限）并提交数据库会话。
    6. 显示用户信息更新成功的消息并重定向到用户管理页面。
    返回:
        werkzeug.wrappers.Response: 渲染编辑用户页面或重定向到用户管理页面的响应对象。
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    user = db.get_or_404(User, id)
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            is_admin = request.form.get('is_admin') == 'on'

            if not username:
                flash('用户名不能为空')
                return redirect(url_for('admin_edit_user', id=id))

            # 检查用户名是否已被其他用户使用
            existing_user = User.query.filter(
                User.UserName == username, User.UserID != id).first()
            if existing_user:
                flash('用户名已存在')
                return redirect(url_for('admin_edit_user', id=id))

            # 检查邮箱是否已被其他用户使用（如果提供了邮箱）
            if email and email.strip():
                existing_email = User.query.filter(
                    User.Email == email, User.UserID != id).first()
                if existing_email:
                    flash('邮箱已被其他用户使用')
                    return redirect(url_for('admin_edit_user', id=id))

            # 更新用户信息
            user.UserName = username
            user.Email = email.strip() if email and email.strip() else None
            
            # 只有在提供了新密码时才更新密码
            if password and password.strip():
                user.set_password(password)
                
            user.Role = 'admin' if is_admin else 'user'
            
            db.session.commit()
            
            # 记录管理员编辑用户的操作日志
            user_type = '管理员' if is_admin else '普通用户'
            password_change_info = '(包含密码修改)' if password and password.strip() else ''
            email_info = f', 邮箱: {email}' if email and email.strip() else ''
            create_log('管理员编辑用户', f'管理员 {current_user.UserName} 编辑了用户 {username} 信息,角色: {user_type}{email_info} {password_change_info}', current_user.UserID)
            
            flash('用户信息更新成功')
            return redirect(url_for('admin_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新用户信息时出错: {str(e)}')
            return redirect(url_for('admin_edit_user', id=id))

    return render_template('admin_edit_user.html', user=user)


@app.route('/admin/upload_user_avatar/<int:user_id>', methods=['POST'])
@login_required
def admin_upload_user_avatar(user_id):
    """
    管理员为指定用户上传头像的路由
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    try:
        # 检查是否有文件上传
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'message': '未接收到文件'}), 400
            
        file = request.files['avatar']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400
            
        # 检查文件类型
        if not allowed_image_file(file.filename):
            return jsonify({'success': False, 'message': '不支持的文件格式'}), 400
            
        # 生成安全的文件名（使用用户ID和时间戳,避免文件名冲突）
        filename = f"avatar_{user.UserID}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(AVATAR_UPLOAD_FOLDER, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 更新用户头像路径
        avatar_url = f'/static/uploads/avatars/{filename}'
        user.Avatar = avatar_url
        db.session.commit()
        
        # 记录日志
        create_log('管理员为用户上传头像', f'管理员 {current_user.UserName} 为用户 {user.UserName} 上传了新的头像', current_user.UserID)
        
        return jsonify({
            'success': True,
            'message': '头像上传成功',
            'avatar_url': avatar_url
        })
        
    except Exception as e:
        # 记录错误
        app.logger.error(f'管理员上传用户头像失败: {str(e)}')
        return jsonify({'success': False, 'message': '服务器错误,上传失败'}), 500


@app.route('/admin/users/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_user(id):
    """
    管理员删除用户的路由。
    该函数执行以下操作：
    1. 检查当前用户是否为管理员,如果不是则提示需要管理员权限。
    2. 检查当前用户是否尝试删除自己,如果是则提示不能删除当前登录的用户。
    3. 根据用户ID获取用户信息,如果用户不存在则返回404错误。
    4. 检查是否尝试删除管理员账户,如果是则检查管理员数量,确保不能删除最后一个管理员账户。
    5. 删除用户的所有预订记录。
    6. 删除用户并提交数据库会话。
    7. 显示用户删除成功的消息并重定向到用户管理页面。
    返回:
        werkzeug.wrappers.Response: 重定向到用户管理页面的响应对象。
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    if current_user.UserID == id:
        flash('不能删除当前登录的用户')
        return redirect(url_for('admin_users'))

    user = db.get_or_404(User, id)
    if user.is_admin:
        admin_count = User.query.filter_by(Role='admin').count()
        if admin_count <= 1:
            flash('不能删除最后一个管理员账户')
            return redirect(url_for('admin_users'))

    # 保存被删用户的用户名,用于日志记录
    username = user.UserName
    
    try:
        # 获取用户的所有预订ID
        user_reservations = Reservation.query.filter_by(UserID=id).all()
        reservation_ids = [r.ID for r in user_reservations]
        
        # 先删除与用户预订相关的会议资料
        if reservation_ids:
            MeetingMaterials.query.filter(MeetingMaterials.BookingID.in_(reservation_ids)).delete(synchronize_session=False)
        
        # 删除用户直接上传的会议资料
        MeetingMaterials.query.filter_by(UserID=id).delete()
        
        # 然后删除用户的所有预订
        Reservation.query.filter_by(UserID=id).delete()
        
        # 删除用户的通知记录
        Notification.query.filter_by(UserID=id).delete()
        
        # 将用户相关的日志记录关联到管理员账户 (假设ID为1的用户为系统管理员)
        system_admin_id = 1
        # 记录原始操作者到日志描述中
        logs = Log.query.filter_by(UserID=id).all()
        for log in logs:
            log.Description = f"[原用户ID:{id}] {log.Description}"
            log.UserID = system_admin_id
        
        # 记录管理员删除用户的操作日志（使用当前管理员ID）
        create_log('管理员删除用户', f'管理员 {current_user.UserName} 删除了用户 {username}', current_user.UserID)
        
        # 删除用户并提交
        db.session.delete(user)
        db.session.commit()
        
        flash('用户删除成功')
        
    except Exception as e:
        db.session.rollback()
        flash(f'删除用户失败: {str(e)}')
        
    return redirect(url_for('admin_users'))


@app.route('/available_rooms')
@login_required
def available_rooms():
    """
    获取指定时间段内可用的会议室。
    该函数执行以下操作：
    1. 从请求参数中获取开始时间和结束时间,并将其转换为 datetime 对象。
    2. 查询所有会议室信息。
    3. 遍历每个会议室,检查在指定时间段内的预订数量。
    4. 如果预订数量小于会议室的总槽位数,则将会议室添加到可用列表中。
    5. 检查当前用户在该时间段内的并发预订数量,计算剩余可预订数量。
    6. 返回包含可用会议室信息和用户剩余预订数量的 JSON 响应。
    返回:
        flask.Response: 包含可用会议室信息的 JSON 响应对象。
    """
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    
    # 验证必填参数
    if not start_time_str or not end_time_str:
        return jsonify({'error': '缺少开始时间或结束时间参数'}), 400
    
    try:
        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
    except (ValueError, TypeError):
        return jsonify({'error': '日期时间格式错误'}), 400

    # 获取所有会议室
    all_rooms = Room.query.all()
    available_rooms = []
    
    # 获取当前用户在该时间段内的并发预订数量
    current_user_id = current_user.UserID
    user_concurrent_count = 0
    can_reserve_message = ""
    
    # 管理员无预订数量限制
    max_concurrent = 5
    if not current_user.is_admin:
        # check_user_concurrent_reservations返回的是一个元组(True/False, message)
        check_result = check_user_concurrent_reservations(current_user_id, start_time, end_time)
        can_reserve = check_result[0]  # 布尔值
        can_reserve_message = check_result[1]  # 消息
        
        # 从消息中提取并发预订数量
        # 假设消息格式为"当前已预订: X个,还可预订: Y个会议室"
        import re
        concurrent_match = re.search(r'当前已预订:\s*(\d+)', can_reserve_message)
        if concurrent_match:
            user_concurrent_count = int(concurrent_match.group(1))
        
    # 计算用户剩余可预订数量
    remaining_reservations = max_concurrent - user_concurrent_count
    
    for room in all_rooms:
        # 在个人会议室管理模式下,检查该时间段内是否已有预订
        overlapping_reservations = Reservation.query.filter_by(RoomID=room.RoomID).filter(
            ((Reservation.StartTime <= start_time) & (Reservation.EndTime > start_time)) |
            ((Reservation.StartTime < end_time) & (Reservation.EndTime >= end_time)) |
            ((Reservation.StartTime >= start_time)
             & (Reservation.EndTime <= end_time))
        ).count()

        # 在个人会议室管理模式下,如果没有预订冲突,则该会议室可用
        if overlapping_reservations == 0:
            available_rooms.append({
                'id': room.RoomID,
                'name': room.RoomName,
                'capacity': room.capacity,
                'available_slots': 1,  # 个人会议室管理模式下,每个会议室只有1个槽位
                'description': room.description,
                'RoomType': room.RoomType
            })

    return jsonify({
        'rooms': available_rooms,
        'user_concurrent_count': user_concurrent_count,
        'max_concurrent': max_concurrent,
        'remaining_reservations': remaining_reservations
    })


@app.route('/user/profile')
@login_required
def user_profile():
    """
    用户个人资料页面的路由。
    该函数执行以下操作：
    1. 确保用户已登录
    2. 渲染个人资料页面模板
    返回:
        werkzeug.wrappers.Response: 渲染用户个人资料页面的响应对象
    """
    return render_template('shared/user_profile.html')
    
# 创建头像上传目录
AVATAR_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), app.config.get('UPLOAD_FOLDER_AVATARS', 'static/uploads/avatars'))
os.makedirs(AVATAR_UPLOAD_FOLDER, exist_ok=True)

# 允许的图片类型
ALLOWED_IMAGE_EXTENSIONS = app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})

def allowed_image_file(filename):
    """检查文件是否为允许的图片格式"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    """
    上传用户头像的路由
    处理用户头像上传并保存到服务器
    """
    try:
        # 检查是否有文件上传
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'message': '未接收到文件'}), 400
            
        file = request.files['avatar']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400
            
        # 检查文件类型
        if not allowed_image_file(file.filename):
            return jsonify({'success': False, 'message': '不支持的文件格式'}), 400
            
        # 生成安全的文件名（使用用户ID和时间戳,避免文件名冲突）
        filename = f"avatar_{current_user.UserID}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(AVATAR_UPLOAD_FOLDER, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 更新用户头像路径
        avatar_url = f'/static/uploads/avatars/{filename}'
        current_user.Avatar = avatar_url
        db.session.commit()
        
        # 记录日志
        create_log('用户上传头像', f'用户 {current_user.UserName} 上传了新的头像')
        
        return jsonify({
            'success': True,
            'message': '头像上传成功',
            'avatar_url': avatar_url
        })
        
    except Exception as e:
        # 记录错误
        app.logger.error(f'头像上传失败: {str(e)}')
        return jsonify({'success': False, 'message': '服务器错误,上传失败'}), 500

@app.route('/about')
def about():
    """
    渲染关于页面的路由。
    该函数执行以下操作：
    1. 渲染关于页面模板。
    返回:
        werkzeug.wrappers.Response: 渲染关于页面的响应对象。
    """
    return render_template('shared/about.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    忘记密码页面的路由。
    如果是GET请求,返回忘记密码页面。
       如果是POST请求,发送重置密码邮件。
    返回:
        werkzeug.wrappers.Response: 渲染忘记密码页面的响应对象。
    """
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('请输入您的邮箱地址')
            return render_template('email/forgot_password.html')
            
        # 查找用户
        user = User.query.filter_by(Email=email).first()
        if not user:
            flash('该邮箱地址未注册')
            return render_template('email/forgot_password.html')
            
        # 生成密码重置令牌
        token = generate_confirmation_token(user.Email)
        
        # 生成重置链接
        reset_url = url_for('reset_password', token=token, _external=True)
        
        # 发送重置邮件
        html = render_template('email/reset_password.html', reset_url=reset_url, username=user.UserName)
        subject = "会议室预订系统 - 重置密码"
        
        try:
            send_email(user.Email, subject, html)
            flash('重置密码邮件已发送到您的邮箱,请查收并点击重置链接。')
        except Exception as e:
            flash('发送重置密码邮件失败,请重试或联系管理员。')
            print(f'发送重置密码邮件失败: {str(e)}')
            
        return redirect(url_for('login'))
        
    return render_template('email/forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    重置密码路由
    如果是GET请求,返回重置密码页面。
    如果是POST请求,处理密码重置。
    参数:
        token (str): 密码重置令牌
    返回:
        werkzeug.wrappers.Response: 渲染重置密码页面或重定向到登录页面
    """
    # 验证令牌
    email = confirm_token(token, expiration=3600)  # 令牌服务1小时
    
    if not email:
        flash('重置密码链接无效或已过期。请重新请求密码重置。')
        return redirect(url_for('forgot_password'))
    
    # 查找用户
    user = User.query.filter_by(Email=email).first()
    if not user:
        flash('用户不存在。')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('请填写所有必填字段')
            return render_template('reset_password.html', token=token)
            
        if password != confirm_password:
            flash('两次输入的密码不一致')
            return render_template('reset_password.html', token=token)

        # 设置新密码
        user.set_password(password)
        db.session.commit()
        
        # 记录密码重置日志
        create_log('密码重置', f'用户 {user.UserName} 通过邮件重置密码成功', user.UserID)
        
        flash('密码重置成功！请使用新密码登录。')
        return redirect(url_for('login'))
        
    return render_template('reset_password.html', token=token)


@app.route('/admin/rooms')
@login_required
def admin_rooms():
    """
    管理员查看所有会议室的路由。
    该函数执行以下操作：
    1. 查询所有会议室信息，支持分页和筛选。
    2. 渲染管理员会议室管理页面,并传递会议室信息。
    返回:
        werkzeug.wrappers.Response: 渲染管理员会议室管理页面的响应对象。
    """
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)  # 每页显示15个会议室
    
    # 获取筛选参数
    search = request.args.get('search', '').strip()
    room_type_filter = request.args.get('room_type', '')
    min_capacity = request.args.get('min_capacity', type=int)
    max_capacity = request.args.get('max_capacity', type=int)
    status_filter = request.args.get('status', '')
    
    # 构建查询
    query = Room.query
    
    # 应用搜索条件
    if search:
        query = query.filter(
            db.or_(
                Room.RoomName.contains(search),
                Room.RoomNumber.contains(search),
                Room.Location.contains(search),
                Room.Building.contains(search),
                Room.Floor.contains(search)
            )
        )
    
    # 应用筛选条件
    if room_type_filter and room_type_filter != 'all':
        query = query.filter(Room.RoomType == room_type_filter)
    
    if status_filter and status_filter != 'all':
        query = query.filter(Room.Status == status_filter)
    
    if min_capacity:
        query = query.filter(Room.Capacity >= min_capacity)
    
    if max_capacity:
        query = query.filter(Room.Capacity <= max_capacity)
    
    # 按会议室名称排序并分页
    rooms_pagination = query.order_by(Room.RoomName).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # 计算统计信息（基于所有会议室，不受分页影响）
    all_rooms = Room.query.all()
    total_rooms = len(all_rooms)
    online_rooms = len([r for r in all_rooms if r.RoomType == 'Online'])
    offline_rooms = len([r for r in all_rooms if r.RoomType == 'Offline'])
    
    return render_template('admin_rooms.html', 
                         rooms=rooms_pagination.items,
                         pagination=rooms_pagination,
                         current_per_page=per_page,
                         current_filters={
                             'search': search,
                             'room_type': room_type_filter,
                             'min_capacity': min_capacity,
                             'max_capacity': max_capacity,
                             'status': status_filter
                         },
                         stats={
                             'total_rooms': total_rooms,
                             'online_rooms': online_rooms,
                             'offline_rooms': offline_rooms
                         })


@app.route('/request_change_password', methods=['GET', 'POST'])
@login_required
def request_change_password():
    """
    请求修改密码并发送验证邮件
    """
    if current_user.is_admin:
        flash('管理员请在用户管理页面修改密码')
        return redirect(url_for('dashboard'))
    
    # 生成密码重置令牌
    token = generate_confirmation_token(current_user.Email)
    
    # 生成确认链接
    confirm_url = url_for('change_password', token=token, _external=True)
    
    # 发送确认邮件
    html = render_template('email/change_password.html', confirm_url=confirm_url, username=current_user.UserName)
    subject = "会议室预订系统 - 密码修改验证"
    
    # 异步发送邮件
    send_email(current_user.Email, subject, html)
    
    flash('密码修改验证邮件已发送到您的邮箱,请查收并点击链接完成修改。')
    return redirect(url_for('dashboard'))


@app.route('/change_password', methods=['GET', 'POST'])
@app.route('/change_password/<token>', methods=['GET', 'POST'])
def change_password(token=None):
    """
    处理用户修改密码的函数。
    该函数执行以下操作：
    1. 验证邮箱令牌
    2. 如果请求方法为POST,获取并验证新密码和确认密码。
    3. 如果新密码和确认密码不一致,提示用户两次输入的新密码不一致。
    4. 如果验证通过,更新用户密码并提交数据库会话。
    5. 显示密码修改成功的消息并重定向到登录页面。
    返回:
        werkzeug.wrappers.Response: 渲染修改密码页面或重定向到登录页面的响应对象。
    """
    # 如果没有令牌,重定向到请求修改密码页面
    if not token and current_user.is_authenticated:
        return redirect(url_for('request_change_password'))
    elif not token:
        flash('无效的密码修改请求')
        return redirect(url_for('login'))
    
    try:
        # 解析令牌并获取邮箱
        print(f"开始验证密码修改令牌: {token}")
        email = confirm_token(token)
        print(f"令牌解析结果邮箱: {email}")
        
        if not email:
            print("令牌无效或已过期")
            flash('无效的密码修改链接或链接已过期。')
            return redirect(url_for('login'))
            
        # 使用解析出的邮箱查找用户
        user = User.query.filter_by(Email=email).first()
        
        if not user:
            print(f"未找到邮箱为 {email} 的用户")
            flash('找不到对应的用户账号。')
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # 验证新密码
            if not new_password or not confirm_password:
                flash('请填写所有必填字段')
                return render_template('change_password.html', token=token)
                
            if new_password != confirm_password:
                flash('两次输入的新密码不一致')
                return render_template('change_password.html', token=token)

            # 更新密码
            user.set_password(new_password)
            db.session.commit()
            
            # 记录密码修改日志
            create_log('密码修改', f'用户 {user.UserName} 修改密码成功', user.UserID)
            
            # 如果用户已登录,则注销当前用户
            if current_user.is_authenticated:
                logout_user()
                
            flash('密码修改成功,请使用新密码登录')
            return redirect(url_for('login'))

        return render_template('change_password.html', token=token)
        
    except Exception as e:
        print(f"密码修改验证过程发生错误: {str(e)}")
        flash('验证过程出错。请重试或联系管理员。')
        return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    """
    处理用户登出操作的函数。
    该函数执行以下操作：
    1. 记录用户登出日志
    2. 调用 logout_user() 函数,注销当前用户。
    3. 使用 flash() 函数显示一条成功退出登录的消息。
    4. 重定向用户到主页。
    返回:
        werkzeug.wrappers.Response: 重定向到主页的响应对象。
    """
    # 记录登出日志（在logout_user()之前记录,因为之后current_user就不可用了）
    create_log('登出', f'用户 {current_user.UserName} 退出登录')
    
    logout_user()
    flash('您已成功退出登录')
    return redirect(url_for('index'))


def cleanup_expired_reservations():
    """
    清理过期的预订记录。
    该函数获取当前时间,并查询所有结束时间早于当前时间的预订记录。
    对于每一个过期的预订记录,都会从数据库中删除。
    最后提交数据库会话以保存更改。
    """
    current_time = datetime.now()
    expired_reservations = Reservation.query.filter(
        Reservation.EndTime < current_time).all()
    for reservation in expired_reservations:
        db.session.delete(reservation)
    db.session.commit()


def update_room_status_after_maintenance():
    """
    自动更新维护记录状态和会议室状态
    此函数检查所有维护记录并根据当前时间自动更新状态：
    - Scheduled -> In Progress (开始时间已到,但未结束)
    - Scheduled/In Progress -> Completed (结束时间已过)
    同时更新相应会议室的状态
    """
    now = datetime.now()
    
    # 查找所有需要更新状态的维护记录
    all_maintenances = Maintenance.query.filter(
        Maintenance.Status.in_(['Scheduled', 'In Progress'])
    ).all()
    
    for maintenance in all_maintenances:
        try:
            old_status = maintenance.Status
            new_status = None
            
            # 确定新状态
            if now >= maintenance.EndTime:
                new_status = 'Completed'
            elif now >= maintenance.StartTime:
                new_status = 'In Progress'
            else:
                new_status = 'Scheduled'
            
            # 如果状态需要更新
            if old_status != new_status:
                maintenance.Status = new_status
                
                # 更新会议室状态
                room = db.session.get(Room, maintenance.RoomID)
                if room:
                    if new_status == 'Completed':
                        # 检查是否还有其他进行中的维护
                        other_active = Maintenance.query.filter(
                            Maintenance.RoomID == maintenance.RoomID,
                            Maintenance.Status.in_(['Scheduled', 'In Progress']),
                            Maintenance.ID != maintenance.ID,
                            Maintenance.StartTime <= now,
                            Maintenance.EndTime > now
                        ).first()
                        
                        if not other_active:
                            room.Status = 'Available'
                            print(f"自动更新会议室 {room.RoomName} 状态为可用")
                    elif new_status == 'In Progress':
                        room.Status = 'Maintenance'
                        print(f"自动更新会议室 {room.RoomName} 状态为维护中")
                
                db.session.commit()
                print(f"维护记录ID {maintenance.ID} 状态更新: {old_status} -> {new_status}")
            
        except Exception as e:
            db.session.rollback()
            print(f"更新维护记录状态失败: {str(e)}")

@app.before_request
def before_request_handler():
    """
    在每个请求之前运行,用于执行一些自动维护任务
    """
    # 更新维护后的会议室状态
    update_room_status_after_maintenance()


class Equipment(db.Model):
    """
    "
    设备信息类,继承自db.Model
    属性：
        EquipmentID (int): 设备ID,主键
        RoomID (int): 关联的会议室ID
        EquipmentName (str): 设备名称
        Quantity (int): 设备数量
        room (relationship): 与会议室的关系
    """
    __tablename__ = 'Equipment'
    EquipmentID = db.Column(db.Integer, primary_key=True)
    RoomID = db.Column(db.Integer, db.ForeignKey('MeetingRoom.RoomID'), nullable=False)
    EquipmentName = db.Column(db.String(100), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False, default=1)
    # 建立与会议室的关系 - 使用passive_deletes避免自动更新外键
    room = db.relationship('Room', backref=db.backref('equipment', lazy=True, passive_deletes=True))


@app.route('/admin/equipment')
@login_required
def admin_equipment():
    """
    管理员查看所有设备的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
    
    # 获取所有设备信息,并关联会议室信息
    equipment_list = db.session.query(Equipment, Room).join(Room).all()
    return render_template('admin_equipment.html', equipment_list=equipment_list)

@app.route('/admin/equipment/add', methods=['GET', 'POST'])
@login_required
def add_equipment():
    """
    添加设备的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        room_id = request.form.get('room_id')
        equipment_name = request.form.get('equipment_name')
        quantity = request.form.get('quantity', type=int)

        if not all([room_id, equipment_name, quantity]):
            flash('请填写所有必填字段')
            return redirect(url_for('add_equipment'))

        # 检查会议室是否存在
        room = db.session.get(Room, room_id)
        if not room:
            flash('选择的会议室不存在')
            return redirect(url_for('add_equipment'))

        # 检查是否已存在相同的设备（防止重复提交）
        existing_equipment = Equipment.query.filter_by(
            RoomID=room_id,
            EquipmentName=equipment_name
        ).first()
        
        if existing_equipment:
            # 如果设备已存在,更新数量而不是重复添加
            existing_equipment.Quantity += quantity
            try:
                db.session.commit()
                equipment_info = f'会议室: {room.RoomName}, 设备名称: {equipment_name}, 新增数量: {quantity}'
                create_log('管理员更新设备数量', f'管理员 {current_user.UserName} 更新了设备数量 ({equipment_info})', current_user.UserID)
                flash(f'设备已存在,已将数量增加 {quantity} 台')
                return redirect(url_for('admin_equipment'))
            except Exception as e:
                db.session.rollback()
                flash(f'设备数量更新失败：{str(e)}')
                return redirect(url_for('add_equipment'))

        equipment = Equipment(
            RoomID=room_id,
            EquipmentName=equipment_name,
            Quantity=quantity
        )
        
        try:
            db.session.add(equipment)
            db.session.commit()
            
            # 记录管理员添加设备的操作日志
            equipment_info = f'会议室: {room.RoomName}, 设备名称: {equipment_name}, 数量: {quantity}'
            create_log('管理员添加设备', f'管理员 {current_user.UserName} 添加了设备 ({equipment_info})', current_user.UserID)
            
            flash('设备添加成功')
            return redirect(url_for('admin_equipment'))
        except Exception as e:
            db.session.rollback()
            flash(f'设备添加失败：{str(e)}')
            return redirect(url_for('add_equipment'))

    # GET请求,返回添加设备页面
    rooms = Room.query.all()
    return render_template('admin_add_equipment.html', rooms=rooms)

@app.route('/admin/equipment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_equipment(id):
    """
    编辑设备信息的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    equipment = db.get_or_404(Equipment, id)

    if request.method == 'POST':
        room_id = request.form.get('room_id')
        equipment_name = request.form.get('equipment_name')
        quantity = request.form.get('quantity', type=int)

        if not all([room_id, equipment_name, quantity]):
            flash('请填写所有必填字段')
            return redirect(url_for('edit_equipment', id=id))

        try:
            # 获取会议室信息用于日志
            room = db.session.get(Room, room_id)
            
            equipment.RoomID = room_id
            equipment.EquipmentName = equipment_name
            equipment.Quantity = quantity
            db.session.commit()
            
            # 记录管理员编辑设备的操作日志
            equipment_info = f'会议室: {room.RoomName}, 设备名称: {equipment_name}, 数量: {quantity}'
            create_log('管理员编辑设备', f'管理员 {current_user.UserName} 编辑了设备信息 ({equipment_info})', current_user.UserID)
            
            flash('设备信息更新成功')
            return redirect(url_for('admin_equipment'))
        except Exception as e:
            db.session.rollback()
            flash(f'设备信息更新失败：{str(e)}')
            return redirect(url_for('edit_equipment', id=id))

    rooms = Room.query.all()
    return render_template('admin_edit_equipment.html', equipment=equipment, rooms=rooms)

@app.route('/admin/equipment/delete/<int:id>')
@login_required
def delete_equipment(id):
    """
    删除设备的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    equipment = db.get_or_404(Equipment, id)
    try:
        # 获取设备和会议室信息用于日志
        room = db.session.get(Room, equipment.RoomID)
        equipment_info = f'会议室: {room.RoomName}, 设备名称: {equipment.EquipmentName}, 数量: {equipment.Quantity}'
        
        db.session.delete(equipment)
        db.session.commit()
        
        # 记录管理员删除设备的操作日志
        create_log('管理员删除设备', f'管理员 {current_user.UserName} 删除了设备 ({equipment_info})', current_user.UserID)
        
        flash('设备删除成功')
    except Exception as e:
        db.session.rollback()
        flash(f'设备删除失败：{str(e)}')
    
    return redirect(url_for('admin_equipment'))


class Notification(db.Model):
    """
    通知类,继承自db.Model
    属性：
        ID (int): 通知ID,主键
        UserID (int): 用户ID,外键关联到User表
        Status (str): 通知状态（'Unread'/'Read'）
        Timestamp (datetime): 通知时间
        Message (str): 通知内容
        user (relationship): 与用户的关系
    """
    __tablename__ = 'Notification'
    ID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    Status = db.Column(db.String(50), nullable=False, default='Unread')
    Timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    Message = db.Column(db.Text, nullable=False)
    # 建立与用户的关系
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

@app.route('/notifications')
@login_required
def view_notifications():
    """
    查看用户通知的路由
    """
    # 获取用户的所有通知,按时间倒序排列
    notifications = Notification.query.filter_by(UserID=current_user.UserID)\
        .order_by(Notification.Timestamp.desc()).all()
    
    # 获取未读通知数量
    unread_count = Notification.query.filter_by(
        UserID=current_user.UserID, Status='Unread').count()
    
    return render_template('shared/notifications.html', 
                         notifications=notifications,
                         unread_count=unread_count)

@app.route('/notifications/mark_read/<int:id>')
@login_required
def mark_notification_read(id):
    """
    标记通知为已读的路由
    """
    notification = db.get_or_404(Notification, id)
    
    # 检查是否是当前用户的通知
    if notification.UserID != current_user.UserID:
        flash('无权操作此通知')
        return redirect(url_for('view_notifications'))
    
    notification.Status = 'Read'
    db.session.commit()
    return redirect(url_for('view_notifications'))

@app.route('/notifications/mark_all_read')
@login_required
def mark_all_notifications_read():
    """
    标记所有通知为已读的路由
    """
    Notification.query.filter_by(UserID=current_user.UserID, Status='Unread')\
        .update({Notification.Status: 'Read'})
    db.session.commit()
    flash('所有通知已标记为已读')
    return redirect(url_for('view_notifications'))

@app.route('/notifications/delete/<int:id>')
@login_required
def delete_notification(id):
    """
    删除通知的路由
    """
    notification = db.get_or_404(Notification, id)
    
    # 检查是否是当前用户的通知
    if notification.UserID != current_user.UserID:
        flash('无权操作此通知')
        return redirect(url_for('view_notifications'))
    
    db.session.delete(notification)
    db.session.commit()
    flash('通知已删除')
    return redirect(url_for('view_notifications'))

def send_notification(user_id, message):
    """
    发送通知的辅助函数
    参数：
        user_id (int): 接收通知的用户ID
        message (str): 通知内容
    """
    notification = Notification(
        UserID=user_id,
        Message=message
    )
    db.session.add(notification)
    db.session.commit()

def notify_all_admins(message, exclude_user_id=None):
    """
    向所有管理员发送通知的辅助函数
    参数：
        message (str): 通知内容
        exclude_user_id (int, optional): 排除的用户ID（通常是当前操作用户）
    """
    try:
        # 查询所有管理员用户
        admin_users = User.query.filter(User.Role == 'admin').all()
        
        notification_count = 0
        for admin_user in admin_users:
            # 如果指定了排除用户ID,则跳过该用户
            if exclude_user_id and admin_user.UserID == exclude_user_id:
                continue
                
            # 发送通知给管理员
            send_notification(admin_user.UserID, message)
            notification_count += 1
            
        return notification_count
    except Exception as e:
        print(f"发送管理员通知失败: {str(e)}")
        return 0
# 在预订确认时发送通知
@app.route('/admin/confirm_reservation/<int:id>')
@login_required
def confirm_reservation(id):
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
        
    reservation = db.get_or_404(Reservation, id)
    
    # 取消自动确认任务（如果存在）
    cancel_auto_confirmation(reservation.ID)
    
    reservation.Status = 'Confirmed'
    
    # 发送通知给预订用户
    send_notification(
        reservation.UserID,
        f'您预订的会议室 {reservation.room.RoomName} ({reservation.StartTime.strftime("%Y-%m-%d %H:%M")} - {reservation.EndTime.strftime("%H:%M")}) 已被确认。'
    )
    
    # 记录管理员确认预订的操作日志
    reservation_info = f'会议室: {reservation.room.RoomName}, 时间: {reservation.StartTime.strftime("%Y-%m-%d %H:%M")}-{reservation.EndTime.strftime("%H:%M")}, 预订人: {reservation.user.username}'
    create_log('管理员确认预订', f'管理员 {current_user.UserName} 确认了预订 ({reservation_info})', current_user.UserID)
    
    db.session.commit()
    flash('预订已确认')
    return redirect(url_for('admin_reservations'))

class Maintenance(db.Model):
    """
    会议室维护记录类,继承自db.Model
    属性：
        ID (int): 维护记录ID,主键
        RoomID (int): 会议室ID,外键关联到MeetingRoom表
        MaintenanceDate (date): 维护日期
        StartTime (datetime): 维护开始时间
        EndTime (datetime): 维护结束时间
        Description (text): 维护描述
        Status (str): 维护状态（Scheduled计划中/In Progress进行中/Completed已完成/Cancelled已取消）
        CreatedAt (datetime): 创建时间
        UpdatedAt (datetime): 更新时间
        room (relationship): 与会议室的关系
    """
    __tablename__ = 'Maintenance'
    ID = db.Column(db.Integer, primary_key=True)
    RoomID = db.Column(db.Integer, db.ForeignKey('MeetingRoom.RoomID'), nullable=False)
    MaintenanceDate = db.Column(db.Date, nullable=False)
    StartTime = db.Column(db.DateTime, nullable=False)
    EndTime = db.Column(db.DateTime, nullable=False)
    Description = db.Column(db.Text)
    Status = db.Column(db.String(50), nullable=False, default='Scheduled')
    CreatedAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    UpdatedAt = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    # 建立与会议室的关系 - 使用passive_deletes避免自动更新外键
    room = db.relationship('Room', backref=db.backref('maintenance_records', lazy=True, passive_deletes=True))

@app.route('/admin/maintenance')
@login_required
def admin_maintenance():
    """
    管理员查看所有维护记录的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
    
    # 先更新已过期的维护记录状态
    update_room_status_after_maintenance()
    
    # 获取所有维护记录,并关联会议室信息
    maintenance_list = db.session.query(Maintenance, Room).join(Room)\
        .order_by(Maintenance.MaintenanceDate.desc()).all()
    return render_template('admin_maintenance.html', maintenance_list=maintenance_list)

@app.route('/admin/maintenance/add', methods=['GET', 'POST'])
@login_required
def add_maintenance():
    """
    添加维护记录的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        room_id = request.form.get('room_id')
        scheduled_date = request.form.get('scheduled_date')
        estimated_duration = request.form.get('estimated_duration', '60')  # 默认60分钟
        description = request.form.get('description')
        
        # 解析 datetime-local 格式的开始时间
        if scheduled_date:
            try:
                start_time = datetime.strptime(scheduled_date, '%Y-%m-%dT%H:%M')
                maintenance_date = start_time.date()
                # 计算结束时间
                duration_minutes = int(estimated_duration)
                end_time = start_time + timedelta(minutes=duration_minutes)
            except (ValueError, TypeError):
                flash('时间格式错误,请重新选择')
                return redirect(url_for('add_maintenance'))
        else:
            start_time = None
            end_time = None
            maintenance_date = None
        
        if not all([room_id, scheduled_date, description]):
            flash('请填写所有必填字段')
            return redirect(url_for('add_maintenance'))
            
        if not start_time or not end_time or not maintenance_date:
            flash('时间信息不完整,请重新填写')
            return redirect(url_for('add_maintenance'))

        if start_time >= end_time:
            flash('开始时间必须早于结束时间')
            return redirect(url_for('add_maintenance'))

        # 检查会议室是否存在
        room = db.session.get(Room, room_id)
        if not room:
            flash('选择的会议室不存在')
            return redirect(url_for('add_maintenance'))

        # 检查时间段是否有预订
        existing_reservations = Reservation.query.filter(
            Reservation.RoomID == room_id,
            Reservation.EndTime > start_time,
            Reservation.StartTime < end_time
        ).first()

        if existing_reservations:
            flash('该时间段内有会议室预订,请选择其他时间')
            return redirect(url_for('add_maintenance'))

        maintenance = Maintenance(
            RoomID=room_id,
            MaintenanceDate=maintenance_date,
            StartTime=start_time,
            EndTime=end_time,
            Description=description,
            Status='Scheduled'
        )
        
        try:
            # 更新会议室状态
            room.Status = 'Maintenance'
            db.session.add(maintenance)
            db.session.commit()
            
            # 发送通知给有预订的用户
            affected_reservations = Reservation.query.filter(
                Reservation.RoomID == room_id,
                Reservation.StartTime >= start_time
            ).all()
            
            for reservation in affected_reservations:
                send_notification(
                    reservation.UserID,
                    f'会议室 {room.RoomName} 将于 {maintenance_date} 进行维护,可能会影响您的预订使用。'
                )
            
            # 记录管理员添加维护计划的操作日志
            maintenance_info = f'会议室: {room.RoomName}, 日期: {maintenance_date}, 时间: {start_time.strftime("%H:%M")}-{end_time.strftime("%H:%M")}'
            create_log('管理员添加维护计划', f'管理员 {current_user.UserName} 添加了维护计划 ({maintenance_info})', current_user.UserID)
            
            flash('维护计划添加成功')
            return redirect(url_for('admin_maintenance'))
        except Exception as e:
            db.session.rollback()
            flash(f'维护计划添加失败：{str(e)}')
            return redirect(url_for('add_maintenance'))

    rooms = Room.query.all()
    users = User.query.all()
    return render_template('admin_add_maintenance.html', rooms=rooms, users=users)

@app.route('/admin/maintenance/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_maintenance(id):
    """
    编辑维护记录的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    maintenance = db.get_or_404(Maintenance, id)

    if request.method == 'POST':
        # 添加调试信息
        print(f"DEBUG: 编辑维护记录 ID {id}")
        print(f"DEBUG: 表单数据: {dict(request.form)}")
        
        room_id = request.form.get('room_id')
        start_datetime_str = request.form.get('start_datetime')
        end_datetime_str = request.form.get('end_datetime')
        description = request.form.get('description')
        status = request.form.get('status')
        
        print(f"DEBUG: 提取的数据 - room_id: {room_id}, status: {status}")
        print(f"DEBUG: 时间数据 - start: {start_datetime_str}, end: {end_datetime_str}")

        # 验证表单数据是否完整
        if not all([room_id, start_datetime_str, end_datetime_str, status]):
            flash('请填写所有必填字段')
            return redirect(url_for('edit_maintenance', id=id))

        try:
            start_time = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
            maintenance_date = start_time.date()
        except (ValueError, TypeError) as e:
            flash('日期或时间格式错误,请重新填写')
            return redirect(url_for('edit_maintenance', id=id))

        if start_time >= end_time:
            flash('开始时间必须早于结束时间')
            return redirect(url_for('edit_maintenance', id=id))

        try:
            maintenance.RoomID = room_id
            maintenance.MaintenanceDate = maintenance_date
            maintenance.StartTime = start_time
            maintenance.EndTime = end_time
            maintenance.Description = description
            maintenance.Status = status
            
            # 更新会议室状态
            room = db.session.get(Room, room_id)
            if status == 'Completed':
                room.Status = 'Available'
            elif status in ['Scheduled', 'In Progress']:
                room.Status = 'Maintenance'
            elif status == 'Cancelled':
                # 维护取消时,检查是否还有其他进行中的维护
                other_active = Maintenance.query.filter(
                    Maintenance.RoomID == room_id,
                    Maintenance.Status.in_(['Scheduled', 'In Progress']),
                    Maintenance.ID != id
                ).first()
                
                if not other_active:
                    room.Status = 'Available'
            
            db.session.commit()
            
            # 记录管理员编辑维护计划的操作日志
            maintenance_info = f'会议室: {room.RoomName}, 日期: {maintenance_date}, 时间: {start_time.strftime("%H:%M")}-{end_time.strftime("%H:%M")}, 状态: {status}'
            create_log('管理员编辑维护计划', f'管理员 {current_user.UserName} 编辑了维护计划 ({maintenance_info})', current_user.UserID)
            
            # 根据状态提供具体的反馈消息
            if status == 'Cancelled':
                flash('维护计划已成功取消,记录已保留在系统中')
            elif status == 'Completed':
                flash('维护计划已标记为完成')
            elif status == 'In Progress':
                flash('维护计划已标记为进行中')
            elif status == 'Scheduled':
                flash('维护计划已更新为计划中状态')
            else:
                flash('维护计划更新成功')
            
            return redirect(url_for('admin_maintenance'))
        except Exception as e:
            db.session.rollback()
            flash(f'维护计划更新失败：{str(e)}')
            return redirect(url_for('admin_edit_maintenance', id=id))

    rooms = Room.query.all()
    return render_template('admin_edit_maintenance.html', maintenance=maintenance, rooms=rooms)

@app.route('/admin/maintenance/delete/<int:id>')
@login_required
def delete_maintenance(id):
    """
    删除维护记录的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))

    maintenance = db.get_or_404(Maintenance, id)
    try:
        # 获取维护计划和会议室信息用于日志
        room = db.session.get(Room, maintenance.RoomID)
        maintenance_info = f'会议室: {room.RoomName}, 日期: {maintenance.MaintenanceDate}, 时间: {maintenance.StartTime.strftime("%H:%M")}-{maintenance.EndTime.strftime("%H:%M")}'
        
        # 如果维护计划是进行中的,将会议室状态改回可用
        if maintenance.Status in ['Scheduled', 'In Progress']:
            room.Status = 'Available'
        
        db.session.delete(maintenance)
        db.session.commit()
        
        # 记录管理员删除维护计划的操作日志
        create_log('管理员删除维护计划', f'管理员 {current_user.UserName} 删除了维护计划 ({maintenance_info})', current_user.UserID)
        
        flash('维护计划删除成功')
    except Exception as e:
        db.session.rollback()
        flash(f'维护计划删除失败：{str(e)}')
    
    return redirect(url_for('admin_maintenance'))

class MeetingMaterials(db.Model):
    """
    会议资料类,继承自db.Model
    """
    __tablename__ = 'MeetingMaterials'
    ID = db.Column(db.Integer, primary_key=True)
    BookingID = db.Column(db.Integer, db.ForeignKey('Booking.ID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    Title = db.Column(db.String(200), nullable=False)
    FilePath = db.Column(db.String(500), nullable=False)
    FileName = db.Column(db.String(200), nullable=False)
    FileSize = db.Column(db.Integer, nullable=False)
    FileType = db.Column(db.String(50), nullable=False)
    UploadTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    Status = db.Column(db.String(20), nullable=False, default='Active')
    Description = db.Column(db.Text)

    # 修改关系定义,使用正确的模型类名
    booking = db.relationship('Reservation', backref=db.backref('materials', lazy=True)) 
    user = db.relationship('User', backref=db.backref('uploaded_materials', lazy=True))

# 配置文件上传
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), app.config.get('UPLOAD_FOLDER_MATERIALS', 'static/uploads/meeting_materials'))
ALLOWED_EXTENSIONS = app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'})
# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/booking/<int:booking_id>/materials')
@login_required
def meeting_materials(booking_id):
    booking = db.get_or_404(Reservation, booking_id)  
    materials = MeetingMaterials.query.filter_by(BookingID=booking_id, Status='Active').all()
    return render_template('meeting_materials.html', booking=booking, materials=materials)

@app.route('/booking/<int:booking_id>/upload_material', methods=['GET', 'POST'])
@login_required
def upload_material(booking_id):
    booking = db.get_or_404(Reservation, booking_id)
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('没有选择文件')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('没有选择文件')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                # 获取原始文件名和扩展名
                # 保留原始文件名,但使用secure_filename处理特殊字符
                raw_filename = file.filename
                # 获取文件扩展名
                file_extension = raw_filename.rsplit('.', 1)[1].lower() if '.' in raw_filename else ''
                # 使用secure_filename处理文件名,避免安全问题
                original_filename = secure_filename(raw_filename)
                
                # 检查是否提供了自定义显示文件名
                display_filename_input = request.form.get('display_filename', '').strip()
                
                if display_filename_input:
                    # 如果提供了自定义显示文件名,使用它并确保它是安全的
                    display_filename = secure_filename(display_filename_input)
                    # 确保自定义文件名有正确的扩展名
                    if not display_filename.lower().endswith('.' + file_extension):
                        display_filename = f"{display_filename}.{file_extension}"
                else:
                    # 否则使用原始文件名
                    display_filename = original_filename
                
                # 获取文件命名方式
                filename_format = request.form.get('filename_format', 'timestamp_suffix')
                
                # 获取当前时间戳字符串
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                
                # 根据选择的命名方式生成存储文件名
                if filename_format == 'original':
                    # 使用原始文件名
                    storage_filename = secure_filename(display_filename)
                elif filename_format == 'title_prefix':
                    # 使用资料标题作为前缀
                    title = request.form.get('title', '').strip()
                    safe_title = secure_filename(title) if title else 'untitled'
                    storage_filename = f"{safe_title}_{secure_filename(display_filename)}"
                elif filename_format == 'booking_prefix':
                    # 使用会议标题作为前缀
                    safe_booking_title = secure_filename(booking.Title) if booking.Title else 'meeting'
                    storage_filename = f"{safe_booking_title}_{secure_filename(display_filename)}"
                elif filename_format == 'timestamp_suffix':
                    # 使用时间戳后缀
                    # 将文件名和扩展名分开
                    name_without_ext = secure_filename(display_filename)
                    if '.' in name_without_ext:
                        name_parts = name_without_ext.rsplit('.', 1)
                        storage_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                    else:
                        storage_filename = f"{name_without_ext}_{timestamp}"
                else:
                    # 默认使用时间戳前缀
                    storage_filename = f"{timestamp}_{secure_filename(display_filename)}"
                
                file_path = os.path.join(UPLOAD_FOLDER, storage_filename)
                
                # 打印调试信息
                print(f"保存文件到: {file_path}")
                
                # 确保上传目录存在
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # 保存文件
                file.save(file_path)
                
                # 检查文件是否成功保存
                if os.path.exists(file_path):
                    print(f"文件成功保存,大小: {os.path.getsize(file_path)} bytes")
                else:
                    print("文件保存失败")
                    raise Exception("文件保存失败")
                
                # 创建会议资料记录
                material = MeetingMaterials(
                    BookingID=booking_id,
                    UserID=current_user.UserID,
                    Title=request.form.get('title'),
                    FilePath=file_path,
                    FileName=display_filename,
                    FileSize=os.path.getsize(file_path),
                    FileType=file_extension,
                    Description=request.form.get('description')
                )
                db.session.add(material)
                db.session.commit()
                
                flash('文件上传成功')
                return redirect(url_for('meeting_materials', booking_id=booking_id))
            except Exception as e:
                print(f"文件上传失败: {str(e)}")
                flash(f'文件上传失败: {str(e)}')
                return redirect(request.url)
            
    return render_template('shared/upload_material.html', booking=booking)

@app.route('/material/<int:material_id>/download')
@login_required
def download_material(material_id):
    material = db.get_or_404(MeetingMaterials, material_id)
    return send_file(material.FilePath, 
                    download_name=material.FileName,
                    as_attachment=True)

@app.route('/material/<int:material_id>/delete')
@login_required
def delete_material(material_id):
    material = db.get_or_404(MeetingMaterials, material_id)
    if current_user.UserID == material.UserID or current_user.Role == 'admin':
        material.Status = 'Deleted'
        db.session.commit()
        flash('文件已删除')
    else:
        flash('您没有权限删除此文件')
    return redirect(url_for('meeting_materials', booking_id=material.BookingID))

# 添加到应用配置中
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 其他功能路由和初始化...

@app.route('/admin/send_notification', methods=['GET', 'POST'])
@login_required
def admin_send_notification():
    """
    管理员发送通知的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        title = request.form.get('title', '系统通知')
        message = request.form.get('message')
        recipient_type = request.form.get('recipient_type')
        
        try:
            sent_count = 0
            if recipient_type == 'all':
                # 发送给所有用户,除了当前管理员自己
                users = User.query.filter(User.UserID != current_user.UserID).all()
                for user in users:
                    send_notification(user.UserID, f"{title}: {message}")
                    sent_count += 1
                flash(f'已成功发送通知给 {sent_count} 位用户')
            elif recipient_type == 'admins':
                # 发送给所有管理员,除了当前管理员自己
                admin_users = User.query.filter(
                    User.UserID != current_user.UserID,
                    User.Role == 'admin'
                ).all()
                for user in admin_users:
                    send_notification(user.UserID, f"{title}: {message}")
                    sent_count += 1
                flash(f'已成功发送通知给 {sent_count} 位管理员')
            elif recipient_type == 'normal':
                # 发送给所有普通用户
                normal_users = User.query.filter(
                    User.UserID != current_user.UserID,
                    User.Role == 'user'
                ).all()
                for user in normal_users:
                    send_notification(user.UserID, f"{title}: {message}")
                    sent_count += 1
                flash(f'已成功发送通知给 {sent_count} 位普通用户')
            elif recipient_type == 'custom':
                # 发送给自定义选择的用户
                custom_recipients = request.form.getlist('custom_recipients[]')
                for user_id in custom_recipients:
                    user_id = int(user_id)
                    if user_id != current_user.UserID:
                        send_notification(user_id, f"{title}: {message}")
                        sent_count += 1
                flash(f'已成功发送通知给 {sent_count} 位用户')
                
            return redirect(url_for('admin_send_notification'))
            
        except Exception as e:
            flash(f'发送通知失败：{str(e)}')
            return redirect(url_for('admin_send_notification'))
    
    # GET 请求,显示发送通知表单
    # 获取除了当前管理员之外的所有用户
    users = User.query.filter(User.UserID != current_user.UserID).all()
    
    # 获取通知统计数据
    total_notifications = db.session.query(Notification).count()
    unread_notifications = db.session.query(Notification).filter(
        Notification.Status == 'Unread'
    ).count()
    read_notifications = db.session.query(Notification).filter(
        Notification.Status == 'Read'
    ).count()
    
    # 获取最近30天的发送统计
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_notifications = db.session.query(Notification).filter(
        Notification.Timestamp >= thirty_days_ago
    ).count()
    
    stats = {
        'total_sent': total_notifications,
        'total_read': read_notifications,
        'total_unread': unread_notifications,
        'recent_sent': recent_notifications
    }
    
    return render_template('admin_send_notification.html', users=users, stats=stats)

@app.route('/room/status')
@login_required
def view_room_status():
    """
    查看会议室状态的路由
    显示所有会议室的当前状态、设备情况和维护计划
    支持分页功能
    """
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)  # 每页显示12个会议室
    
    # 获取筛选参数
    status_filter = request.args.get('status', '')
    room_type_filter = request.args.get('room_type', '')
    
    current_time = datetime.now()
    
    # 自动更新过期的维护记录状态
    update_room_status_after_maintenance()
    
    # 构建查询
    query = Room.query
    
    # 应用筛选条件
    if status_filter and status_filter != 'all':
        query = query.filter(Room.Status == status_filter)
    
    if room_type_filter and room_type_filter != 'all':
        query = query.filter(Room.RoomType == room_type_filter)
    
    # 按会议室名称排序并分页
    rooms_pagination = query.order_by(Room.RoomName).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    room_status = []
    for room in rooms_pagination.items:
        # 获取当前正在进行的预订
        current_booking = Reservation.query.filter(
            Reservation.RoomID == room.RoomID,
            Reservation.StartTime <= current_time,
            Reservation.EndTime > current_time,
            Reservation.Status.in_(['Confirmed', 'Pending'])
        ).first()
        
        # 获取今天即将到来的预订（未来24小时内）
        upcoming_bookings = Reservation.query.filter(
            Reservation.RoomID == room.RoomID,
            Reservation.StartTime > current_time,
            Reservation.StartTime <= current_time + timedelta(hours=24),
            Reservation.Status.in_(['Confirmed', 'Pending'])
        ).order_by(Reservation.StartTime).all()
        
        # 获取设备信息
        equipment = Equipment.query.filter_by(RoomID=room.RoomID).all()
        
        # 获取维护计划
        maintenance = Maintenance.query.filter(
            Maintenance.RoomID == room.RoomID,
            Maintenance.Status.in_(['Scheduled', 'In Progress']),
            Maintenance.EndTime > current_time  # 只显示未结束的维护
        ).first()
        
        room_status.append({
            'room': room,
            'current_booking': current_booking,
            'upcoming_bookings': upcoming_bookings,
            'equipment': equipment,
            'maintenance': maintenance
        })
    
    return render_template('room_status.html', 
                         room_status=room_status,
                         pagination=rooms_pagination,
                         current_filters={
                             'status': status_filter,
                             'room_type': room_type_filter
                         })

@app.route('/my/materials')
@login_required
def my_materials():
    """
    查看我的会议资料的路由
    显示用户上传的所有会议资料,按会议分组
    """
    # 获取用户的会议资料
    materials = MeetingMaterials.query.filter_by(
        UserID=current_user.UserID,
        Status='Active'
    ).order_by(MeetingMaterials.UploadTime.desc()).all()
    
    # 按会议ID将资料分组
    materials_by_booking = {}
    for material in materials:
        if material.BookingID not in materials_by_booking:
            materials_by_booking[material.BookingID] = {
                'booking': material.booking,
                'materials': []
            }
        materials_by_booking[material.BookingID]['materials'].append(material)
    
    # 计算统计信息
    total_files = len(materials)
    total_size = sum(material.FileSize for material in materials)
    total_meetings = len(materials_by_booking)
    
    # 获取今日上传的文件数量
    today = datetime.now().date()
    today_uploads = sum(1 for material in materials 
                       if material.UploadTime.date() == today)
    
    # 获取用户的预订会议（当前日期以后的）
    current_datetime = datetime.now()
    bookings = Reservation.query.filter(
        Reservation.UserID == current_user.UserID,
        Reservation.Status.in_(['Pending', 'Confirmed']),
        Reservation.EndTime >= current_datetime
    ).order_by(Reservation.StartTime).all()
    
    return render_template('shared/my_materials.html', 
                         materials_by_booking=materials_by_booking, 
                         bookings=bookings,
                         total_files=total_files,
                         total_size=total_size,
                         total_meetings=total_meetings,
                         today_uploads=today_uploads)

@app.route('/statistics')
@login_required
def statistics():
    """
    数据统计页面的路由
    显示各种统计数据和图表
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
    # 1. 获取基本统计数据
    total_bookings = Reservation.query.count()
    active_users = db.session.query(db.func.count(db.distinct(Reservation.UserID))).scalar()
    total_rooms = Room.query.count()
    
    # 2. 计算平均预订时长（小时）
    avg_duration_result = db.session.query(
        db.func.avg(
            db.func.timestampdiff(db.text('HOUR'), Reservation.StartTime, Reservation.EndTime)
        )
    ).scalar()
    avg_duration = round(avg_duration_result, 1) if avg_duration_result else 0
    
    # 3. 获取会议室使用率数据
    rooms = Room.query.all()
    room_names = [room.RoomName for room in rooms]
    room_usage_data = []
    
    # 计算过去30天内每个会议室的使用率
    thirty_days_ago = datetime.now() - timedelta(days=30)
    working_hours_per_day = 10  # 假设每天工作10小时
    total_working_hours = 30 * working_hours_per_day
    
    for room in rooms:
        # 计算该会议室在过去30天内被预订的总小时数
        reservations = Reservation.query.filter(
            Reservation.RoomID == room.RoomID,
            Reservation.StartTime >= thirty_days_ago,
            Reservation.Status.in_(['Confirmed', 'Pending'])
        ).all()
        
        booked_hours = 0
        for res in reservations:
            # 确保只计算工作时间内的预订时间
            start = max(res.StartTime, thirty_days_ago)
            duration = (res.EndTime - start).total_seconds() / 3600  # 小时
            booked_hours += min(duration, 24)  # 每天最多计算24小时
        
        # 计算使用率百分比
        usage_rate = (booked_hours / total_working_hours) * 100
        room_usage_data.append(round(usage_rate, 1))
    
    # 4. 获取每日预订数据（显示未来7天的预订情况）
    date_labels = []
    daily_bookings_data = []
    
    # 准备未来7天的日期
    for i in range(0, 7):
        date = (datetime.now() + timedelta(days=i)).strftime('%m-%d')
        date_labels.append(date)
        
        # 获取当天的预订数量
        day_start = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = Reservation.query.filter(
            Reservation.StartTime >= day_start,
            Reservation.StartTime < day_end
        ).count()
        daily_bookings_data.append(count)
    
    # 5. 获取用户预订排名
    top_users_query = db.session.query(
        User.UserName.label('username'),
        db.func.count(Reservation.ID).label('booking_count')
    ).join(Reservation).group_by(User.UserID).order_by(
        db.func.count(Reservation.ID).desc()
    ).limit(10).all()
    
    top_users = [{'username': user.username, 'booking_count': user.booking_count} for user in top_users_query]
    
    # 6. 会议室容量利用率
    capacity_labels = ['小型会议室(≤8人)', '中型会议室(9-15人)', '大型会议室(≥16人)']
    small_rooms = Room.query.filter(Room.Capacity <= 8).count()
    medium_rooms = Room.query.filter(Room.Capacity > 8, Room.Capacity < 16).count()
    large_rooms = Room.query.filter(Room.Capacity >= 16).count()
    capacity_data = [small_rooms, medium_rooms, large_rooms]
    
    return render_template(
        'statistics.html',
        total_bookings=total_bookings,
        active_users=active_users,
        total_rooms=total_rooms,
        avg_duration=avg_duration,
        room_names=json.dumps(room_names),
        room_usage_data=json.dumps(room_usage_data),
        date_labels=json.dumps(date_labels),
        daily_bookings_data=json.dumps(daily_bookings_data),
        top_users=top_users,
        capacity_labels=json.dumps(capacity_labels),
        capacity_data=json.dumps(capacity_data)
    )


@app.route('/admin/auto_confirmation_status')
@login_required
def admin_auto_confirmation_status():
    """
    管理员查看自动确认任务状态的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
    
    # 获取所有待执行的自动确认任务
    pending_jobs = get_pending_auto_confirmations()
    
    # 获取相关的预订信息
    pending_reservations = []
    for job in pending_jobs:
        try:
            reservation_id = int(job['reservation_id'])
            reservation = Reservation.query.get(reservation_id)
            if reservation:
                pending_reservations.append({
                    'reservation': reservation,
                    'scheduled_time': job['scheduled_time'],
                    'job_id': job['job_id']
                })
        except (ValueError, AttributeError):
            continue
    
    # 获取统计数据
    total_pending = Reservation.query.filter_by(Status='Pending').count()
    total_confirmed = Reservation.query.filter_by(Status='Confirmed').count()
    
    return render_template('admin_auto_confirmation.html', 
                         pending_reservations=pending_reservations,
                         total_pending=total_pending,
                         total_confirmed=total_confirmed)


@app.route('/api/pending_auto_confirmations')
@login_required
def api_pending_auto_confirmations():
    """
    API端点：获取待自动确认的预订信息
    返回JSON格式的数据,包含预订ID、剩余时间等信息
    """
    if not current_user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    try:
        pending_jobs = get_pending_auto_confirmations()
        pending_data = []
        
        for job in pending_jobs:
            try:
                reservation_id = int(job['reservation_id'])
                reservation = Reservation.query.get(reservation_id)
                
                if reservation and reservation.Status == 'Pending':
                    # 计算剩余时间（秒）
                    now = datetime.now()
                    if job['scheduled_time'] > now:
                        remaining_seconds = int((job['scheduled_time'] - now).total_seconds())
                    else:
                        remaining_seconds = 0
                    
                    pending_data.append({
                        'id': reservation.ID,
                        'room_name': reservation.room.RoomName,
                        'user_name': reservation.user.UserName,
                        'title': reservation.Title,
                        'start_time': reservation.StartTime.isoformat(),
                        'end_time': reservation.EndTime.isoformat(),
                        'scheduled_time': job['scheduled_time'].isoformat(),
                        'remaining_seconds': remaining_seconds
                    })
            except (ValueError, AttributeError) as e:
                print(f"处理预订信息时出错: {e}")
                continue
        
        return jsonify(pending_data)
        
    except Exception as e:
        print(f"获取待确认预订API失败: {str(e)}")
        return jsonify({'error': '获取数据失败'}), 500


@app.route('/admin/logs')
@login_required
def admin_logs():
    """
    管理员查看系统日志的路由
    """
    if not current_user.is_admin:
        flash('需要管理员权限')
        return redirect(url_for('dashboard'))
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 每页显示20条记录
    
    # 获取过滤参数
    action_filter = request.args.get('action', '')
    user_filter = request.args.get('user', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # 构建查询
    query = db.session.query(Log, User).join(User, Log.UserID == User.UserID)
    
    # 应用过滤器
    if action_filter:
        query = query.filter(Log.Action.ilike(f'%{action_filter}%'))
    
    if user_filter:
        query = query.filter(User.UserName.ilike(f'%{user_filter}%'))
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Log.Timestamp >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            # 添加一天,使其包含整个日期
            to_date = to_date.replace(hour=23, minute=59, second=59)
            query = query.filter(Log.Timestamp <= to_date)
        except ValueError:
            pass
    
    # 按时间降序排列并分页
    logs = query.order_by(Log.Timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 获取所有唯一的操作类型用于过滤器
    # 首先从数据库获取现有的操作类型
    existing_actions = db.session.query(Log.Action).distinct().all()
    existing_action_list = [action[0] for action in existing_actions]
    
    # 定义系统中所有可能的操作类型（完整列表）
    all_possible_actions = [
        # 用户认证相关
        '登录', '登出', '登录失败',
        # 用户管理相关
        '用户注册', '密码修改', '密码重置', '上传头像',
        # 管理员用户管理操作
        '管理员添加用户', '管理员编辑用户', '管理员删除用户', '管理员为用户上传头像',
        # 会议室管理相关
        '管理员添加会议室', '管理员编辑会议室', '管理员删除会议室',
        # 预订管理相关
        '创建预订', '管理员编辑预订', '管理员删除预订', '系统自动确认预订',
        # 设备管理相关
        '管理员更新设备数量',
        # 系统操作相关
        '管理员添加会议室', '创建预订', '邮件发送', '系统通知',
        # 数据导出相关
        '数据导出', '报告生成',
        # 安全相关
        '权限变更', '用户删除', '异常登录'
    ]
    
    # 合并现有的和预定义的操作类型,去重并排序
    action_list = sorted(list(set(existing_action_list + all_possible_actions)))
    
    # 获取所有用户用于过滤器
    users = User.query.all()
    
    # 计算操作类型统计（基于所有日志,不仅仅是当前页）
    all_logs_query = db.session.query(Log).join(User, Log.UserID == User.UserID)
    
    # 对于统计,应用同样的过滤条件（除了分页）
    if action_filter:
        all_logs_query = all_logs_query.filter(Log.Action.ilike(f'%{action_filter}%'))
    
    if user_filter:
        all_logs_query = all_logs_query.filter(User.UserName.ilike(f'%{user_filter}%'))
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            all_logs_query = all_logs_query.filter(Log.Timestamp >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            to_date = to_date.replace(hour=23, minute=59, second=59)
            all_logs_query = all_logs_query.filter(Log.Timestamp <= to_date)
        except ValueError:
            pass
    
    # 获取所有符合条件的日志操作类型
    all_actions = [log.Action for log in all_logs_query.all()]
    
    # 计算各类型统计（基于实际数据库中的操作类型）
    auth_actions = ['登录', '登出', '用户注册', '密码修改', '登录失败', '修改个人信息', '用户上传头像']
    booking_actions = ['创建预订', '取消预订', '管理员确认预订', '管理员删除预订', '编辑预订', '管理员编辑预订', '查看个人预订', '查看会议室']
    admin_actions = ['会议室管理', '用户管理', '管理员添加设备', '管理员删除用户', '管理员添加用户', '管理员添加会议室', '管理员添加维护计划', '权限变更', '数据导出', '系统维护', '通知发送']
    error_actions = ['登录失败']
    
    action_stats = {
        'auth_count': len([action for action in all_actions if action in auth_actions]),
        'booking_count': len([action for action in all_actions if action in booking_actions]),
        'admin_count': len([action for action in all_actions if action in admin_actions]),
        'error_count': len([action for action in all_actions if action in error_actions])
    }
    
    return render_template('admin_logs.html', 
                         logs=logs, 
                         action_list=action_list,
                         users=users,
                         action_stats=action_stats,
                         current_filters={
                             'action': action_filter,
                             'user': user_filter,
                             'date_from': date_from,
                             'date_to': date_to
                         })


@app.route('/check_room_availability', methods=['POST'])
@login_required
def check_room_availability_route():
    """
    检查会议室可用性的API路由
    用于前端JavaScript调用
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        if not data or 'start_datetime' not in data or 'end_datetime' not in data:
            return jsonify({'error': '缺少必要参数'}), 400
        
        start_datetime_str = data['start_datetime']
        end_datetime_str = data['end_datetime']
        
        # 验证时间字符串不为空
        if not start_datetime_str or not end_datetime_str:
            return jsonify({'error': '时间参数不能为空'}), 400
        
        # 解析时间
        try:
            start_time = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
        except (ValueError, TypeError):
            return jsonify({'error': '时间格式错误'}), 400
        
        # 获取会议类型过滤参数
        meeting_type = data.get('meeting_type')
        
        # 获取参会人数参数
        attendees = data.get('attendees', 0)
        if attendees:
            attendees = int(attendees)
        
        # 获取所有会议室
        rooms_query = Room.query
        
        # 如果指定了会议类型,进行过滤
        if meeting_type:
            rooms_query = rooms_query.filter(Room.RoomType == meeting_type)
        
        # 如果指定了参会人数,进行容量过滤
        if attendees and attendees > 0:
            rooms_query = rooms_query.filter(Room.Capacity >= attendees)
        
        rooms = rooms_query.all()
        rooms_list = []
        
        for room in rooms:
            # 使用现有的可用性检查函数
            is_available, message = check_room_availability(
                room.RoomID, start_time, end_time, user_id=current_user.id
            )
            
            rooms_list.append({
                'id': room.RoomID,
                'name': room.RoomName,
                'capacity': room.Capacity,
                'description': room.Description or '',
                'equipment': room.Equipment or '',
                'RoomType': room.RoomType,
                'location': room.Location,
                'meeting_link': room.MeetingLink,
                'available': is_available,
                'message': message if not is_available else ''
            })
        
        return jsonify({
            'success': True,
            'rooms': rooms_list,
            'total_rooms': len(rooms_list),
            'available_count': len([r for r in rooms_list if r['available']]),
            'attendees_filter': attendees if attendees and attendees > 0 else None
        })
        
    except ValueError as e:
        return jsonify({'error': '时间格式错误'}), 400
    except Exception as e:
        print(f"检查会议室可用性时出错: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500


@app.template_filter('today')
def today_filter(reservations):
    """
    自定义过滤器：筛选今天的预订
    """
    today = datetime.now().date()
    return [r for r in reservations if r.StartTime.date() == today]


@app.template_filter('expired')
def expired_filter(reservations):
    """
    自定义过滤器：筛选过期的预订
    """
    now = datetime.now()
    return [r for r in reservations if r.EndTime < now]


@app.template_filter('days_since')
def days_since_filter(end_time):
    """
    自定义过滤器：计算距离结束时间的天数
    """
    now = datetime.now()
    if end_time < now:
        return (now - end_time).days
    else:
        return 0


@app.template_filter('active')
def active_filter(reservations):
    """
    Jinja2 自定义过滤器：筛选未过期的预订
    """
    now = datetime.now()
    return [r for r in reservations if r.EndTime >= now]


@app.route('/admin/debug_auto_confirmation')
@login_required
def debug_auto_confirmation():
    """
    调试自动确认功能,检查调度器状态和数据库状态的一致性
    """
    if not current_user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    debug_info = {
        'scheduler_jobs': [],
        'pending_reservations': [],
        'missing_jobs': [],
        'orphaned_jobs': []
    }
    
    try:
        # 1. 获取调度器中的所有自动确认任务
        scheduler_jobs = []
        for job in scheduler.get_jobs():
            if job.id.startswith('auto_confirm_'):
                reservation_id = job.id.replace('auto_confirm_', '')
                scheduler_jobs.append({
                    'job_id': job.id,
                    'reservation_id': reservation_id,
                    'scheduled_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'function': job.func.__name__
                })
        debug_info['scheduler_jobs'] = scheduler_jobs
        
        # 2. 获取数据库中的待确认预订
        pending_reservations = Reservation.query.filter_by(Status='Pending').all()
        pending_data = []
        for reservation in pending_reservations:
            pending_data.append({
                'id': reservation.ID,
                'room_name': reservation.room.RoomName,
                'user_name': reservation.user.UserName,
                'title': reservation.Title,
                'start_time': reservation.StartTime.isoformat(),
                'created_time': reservation.CreateTime.isoformat() if hasattr(reservation, 'CreateTime') else 'N/A'
            })
        debug_info['pending_reservations'] = pending_data
        
        # 3. 找出没有对应调度任务的待确认预订
        scheduler_reservation_ids = [job['reservation_id'] for job in scheduler_jobs]
        missing_jobs = []
        for reservation in pending_reservations:
            if str(reservation.ID) not in scheduler_reservation_ids:
                missing_jobs.append({
                    'reservation_id': reservation.ID,
                    'room_name': reservation.room.RoomName,
                    'user_name': reservation.user.UserName,
                    'title': reservation.Title
                })
        debug_info['missing_jobs'] = missing_jobs
        
        # 4. 找出没有对应预订的调度任务
        orphaned_jobs = []
        for job in scheduler_jobs:
            reservation = Reservation.query.get(int(job['reservation_id']))
            
            if not reservation or reservation.Status != 'Pending':
                orphaned_jobs.append({
                    'job_id': job['job_id'],
                    'reservation_id': job['reservation_id'],
                    'scheduled_time': job['scheduled_time'],
                    'status': reservation.Status if reservation else 'NOT_FOUND'
                })
        debug_info['orphaned_jobs'] = orphaned_jobs
        
        # 5. 汇总统计
        debug_info['summary'] = {
            'total_scheduler_jobs': len(scheduler_jobs),
            'total_pending_reservations': len(pending_reservations),
            'missing_jobs_count': len(missing_jobs),
            'orphaned_jobs_count': len(orphaned_jobs),
            'scheduler_running': scheduler.running
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': f'调试失败: {str(e)}',
            'debug_info': debug_info
        }), 500


@app.route('/admin/fix_auto_confirmation')
@login_required
def fix_auto_confirmation():
    """
    修复自动确认功能,为没有调度任务的待确认预订重新创建任务
    """
    if not current_user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    try:
        fixed_count = 0
        errors = []
        
        # 1. 获取调度器中的自动确认任务
        scheduler_reservation_ids = []
        for job in scheduler.get_jobs():
            if job.id.startswith('auto_confirm_'):
                reservation_id = job.id.replace('auto_confirm_', '')
                scheduler_reservation_ids.append(reservation_id)
        
        # 2. 获取数据库中的待确认预订
        pending_reservations = Reservation.query.filter_by(Status='Pending').all()
        
        # 3. 为没有调度任务的预订重新创建任务
        for reservation in pending_reservations:
            if str(reservation.ID) not in scheduler_reservation_ids:
                try:
                    # 重新安排自动确认任务
                    # 如果预订是很久之前创建的,立即确认；否则延迟1分钟
                    now = datetime.now()
                    if hasattr(reservation, 'CreateTime') and reservation.CreateTime:
                        time_since_creation = now - reservation.CreateTime
                        if time_since_creation > timedelta(minutes=5):
                            # 如果预订创建超过5分钟,立即确认
                            confirm_time = now + timedelta(seconds=10)
                        else:
                            # 否则按正常流程延迟确认
                            confirm_time = reservation.CreateTime + timedelta(minutes=5)
                            if confirm_time <= now:
                                confirm_time = now + timedelta(seconds=10)
                    else:
                        # 如果没有创建时间,延迟1分钟确认
                        confirm_time = now + timedelta(minutes=1)
                    
                    job_id = f"auto_confirm_{reservation.ID}"
                    scheduler.add_job(
                        func=auto_confirm_reservation,
                        trigger='date',
                        run_date=confirm_time,
                        args=[reservation.ID],
                        id=job_id,
                        replace_existing=True
                    )
                    
                    fixed_count += 1
                    print(f"已恢复预订ID {reservation.ID} 的自动确认任务,确认时间: {confirm_time}")
                    
                except Exception as e:
                    print(f"恢复预订ID {reservation.ID} 的自动确认任务失败: {str(e)}")
        
        # 4. 清理孤立的调度任务
        cleaned_count = 0
        for job in scheduler.get_jobs():
            if job.id.startswith('auto_confirm_'):
                reservation_id = job.id.replace('auto_confirm_', '')
                reservation = Reservation.query.get(int(reservation_id))
                
                if not reservation or reservation.Status != 'Pending':
                    try:
                        scheduler.remove_job(job.id)
                        cleaned_count += 1
                        print(f"已清理孤立的调度任务: {job.id}")
                    except Exception as e:
                        error_msg = f"清理任务 {job.id} 失败: {str(e)}"
                        errors.append(error_msg)
                        print(error_msg)
        
        return jsonify({
            'success': True,
            'message': f'修复完成！重新创建了 {fixed_count} 个任务,清理了 {cleaned_count} 个孤立任务',
            'fixed_count': fixed_count,
            'cleaned_count': cleaned_count,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'修复失败: {str(e)}'
        }), 500


def recover_lost_auto_confirmation_jobs():
    """
    应用启动时恢复丢失的自动确认任务
    该函数在应用启动时检查数据库中的待确认预订,
    为没有对应调度任务的预订重新创建自动确认任务
    """
    try:
        print("====== 开始恢复丢失的自动确认任务 ======")
        
        # 1. 获取调度器中现有的自动确认任务
        existing_job_ids = set()
        for job in scheduler.get_jobs():
            if job.id.startswith('auto_confirm_'):
                reservation_id = job.id.replace('auto_confirm_', '')
                existing_job_ids.add(reservation_id)
        
        print(f"调度器中现有自动确认任务数量: {len(existing_job_ids)}")
        
        # 2. 获取数据库中的待确认预订
        pending_reservations = Reservation.query.filter_by(Status='Pending').all()
        print(f"数据库中待确认预订数量: {len(pending_reservations)}")
        
        # 3. 为没有调度任务的预订重新创建任务
        recovered_count = 0
        for reservation in pending_reservations:
            if str(reservation.ID) not in existing_job_ids:
                try:
                    # 重新安排自动确认任务
                    # 如果预订是很久之前创建的,立即确认；否则延迟1分钟
                    now = datetime.now()
                    if hasattr(reservation, 'CreateTime') and reservation.CreateTime:
                        time_since_creation = now - reservation.CreateTime
                        if time_since_creation > timedelta(minutes=5):
                            # 如果预订创建超过5分钟,立即确认
                            confirm_time = now + timedelta(seconds=10)
                        else:
                            # 否则按正常流程延迟确认
                            confirm_time = reservation.CreateTime + timedelta(minutes=5)
                            if confirm_time <= now:
                                confirm_time = now + timedelta(seconds=10)
                    else:
                        # 如果没有创建时间,延迟1分钟确认
                        confirm_time = now + timedelta(minutes=1)
                    
                    job_id = f"auto_confirm_{reservation.ID}"
                    scheduler.add_job(
                        func=auto_confirm_reservation,
                        trigger='date',
                        run_date=confirm_time,
                        args=[reservation.ID],
                        id=job_id,
                        replace_existing=True
                    )
                    
                    recovered_count += 1
                    print(f"已恢复预订ID {reservation.ID} 的自动确认任务,确认时间: {confirm_time}")
                    
                except Exception as e:
                    print(f"恢复预订ID {reservation.ID} 的自动确认任务失败: {str(e)}")
        
        print(f"====== 自动确认任务恢复完成,共恢复 {recovered_count} 个任务 ======")
        
    except Exception as e:
        print(f"恢复自动确认任务时发生错误: {str(e)}")
        import traceback
        print(f"错误跟踪: {traceback.format_exc()}")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 恢复丢失的自动确认任务
        recover_lost_auto_confirmation_jobs()
    # 运行 Flask 应用程序,启用调试模式,端口为5000
    app.run(debug=True, port=5000)
