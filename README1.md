# 会议智控系统 - 数据库系统设计报告

## 📋 项目概述

**会议智控系统（Intelligent Conference Control System, ICCS）** 是一个基于Flask框架开发的现代化会议室管理平台，集成了完整的数据库管理系统、用户认证、预约管理、维护管理和API接口等功能。

### 🎯 系统特色
- **智能预约管理**：支持线上/线下会议室预约
- **用户权限管理**：多角色用户管理（管理员/普通用户）
- **邮件验证系统**：安全的用户注册验证
- **维护管理**：会议室维护计划和记录
- **文件管理**：会议资料上传和管理
- **系统日志**：完整的操作审计和日志记录
- **RESTful API**：支持第三方系统集成

---

## 🗄️ 数据库系统架构

### 数据库技术栈
- **数据库引擎**：MySQL 8.0+
- **ORM框架**：SQLAlchemy (Flask-SQLAlchemy)
- **连接驱动**：PyMySQL
- **数据库连接池**：SQLAlchemy连接池管理
- **字符集**：UTF-8 (支持中文)

### 数据库配置
```python
# 数据库连接配置
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 支持多环境配置
# - 本地开发环境：localhost
# - 云服务器环境：8.134.119.146
# - PythonAnywhere环境：pythonanywhere-services.com
```

---

## 📊 数据库表结构设计

### 1. 用户信息表 (User)
```sql
CREATE TABLE User (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    UserName VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(100) UNIQUE,
    EmailVerified BOOLEAN DEFAULT 0,
    VerificationToken VARCHAR(255),
    Role VARCHAR(50) NOT NULL,
    Avatar VARCHAR(255) NULL
);
```

**字段说明**：
- `UserID`：用户唯一标识符
- `UserName`：用户名（支持登录）
- `Password`：MD5加密密码
- `Email`：邮箱地址（支持邮箱登录）
- `EmailVerified`：邮箱验证状态
- `VerificationToken`：邮箱验证令牌
- `Role`：用户角色（admin/user）
- `Avatar`：用户头像路径

### 2. 会议室信息表 (MeetingRoom)
```sql
CREATE TABLE MeetingRoom (
    RoomID INT PRIMARY KEY AUTO_INCREMENT,
    RoomNumber VARCHAR(50) NOT NULL UNIQUE,
    RoomName VARCHAR(100) NOT NULL,
    Capacity INT NOT NULL,
    Equipment VARCHAR(255),
    Status VARCHAR(50) NOT NULL DEFAULT 'Available',
    RoomType ENUM('Offline', 'Online') NOT NULL DEFAULT 'Offline',
    Location VARCHAR(255),
    MeetingLink VARCHAR(1000),
    Floor VARCHAR(20),
    Building VARCHAR(50),
    Description TEXT
);
```

**特色功能**：
- 支持线上/线下会议室类型
- 灵活的设备配置管理
- 物理位置和虚拟链接并存

### 3. 预订信息表 (Booking)
```sql
CREATE TABLE Booking (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    RoomID INT NOT NULL,
    UserID INT NOT NULL,
    StartTime DATETIME NOT NULL,
    EndTime DATETIME NOT NULL,
    Status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    Title VARCHAR(100) NOT NULL,
    Purpose TEXT,
    Attendees INT NOT NULL DEFAULT 1,
    MeetingType ENUM('Offline', 'Online') NOT NULL DEFAULT 'Offline',
    MeetingPassword VARCHAR(255) NULL,
    FOREIGN KEY (RoomID) REFERENCES MeetingRoom(RoomID),
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);
```

**核心特性**：
- 支持预约状态管理（Pending/Confirmed/Cancelled）
- 参会人数验证
- 线上会议密码支持
- 完整的时间冲突检测

### 4. 设备信息表 (Equipment)
```sql
CREATE TABLE Equipment (
    EquipmentID INT PRIMARY KEY AUTO_INCREMENT,
    RoomID INT NOT NULL,
    EquipmentName VARCHAR(100) NOT NULL,
    Quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (RoomID) REFERENCES MeetingRoom(RoomID)
);
```

### 5. 系统日志表 (Log)
```sql
CREATE TABLE Log (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    Action VARCHAR(100) NOT NULL,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Description TEXT,
    IPAddress VARCHAR(45),
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);
```

**审计功能**：
- 完整的用户操作记录
- IP地址追踪（支持IPv6）
- 操作时间戳记录
- 详细操作描述

### 6. 通知表 (Notification)
```sql
CREATE TABLE Notification (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    Status VARCHAR(50) NOT NULL DEFAULT 'Unread',
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Message TEXT NOT NULL,
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);
```

### 7. 维护记录表 (Maintenance)
```sql
CREATE TABLE Maintenance (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    RoomID INT NOT NULL,
    MaintenanceDate DATE NOT NULL,
    StartTime DATETIME NOT NULL,
    EndTime DATETIME NOT NULL,
    Description TEXT,
    Status VARCHAR(50) NOT NULL DEFAULT 'Scheduled',
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (RoomID) REFERENCES MeetingRoom(RoomID)
);
```

### 8. 会议资料表 (MeetingMaterials)
```sql
CREATE TABLE MeetingMaterials (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    BookingID INT NOT NULL,
    UserID INT NOT NULL,
    Title VARCHAR(200) NOT NULL,
    FilePath VARCHAR(500) NOT NULL,
    FileName VARCHAR(200) NOT NULL,
    FileSize INT NOT NULL,
    FileType VARCHAR(50) NOT NULL,
    UploadTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Status VARCHAR(20) NOT NULL DEFAULT 'Active',
    Description TEXT,
    FOREIGN KEY (BookingID) REFERENCES Booking(ID),
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);
```

---

## 🔧 ORM模型设计

### Flask-SQLAlchemy模型实现

#### 用户模型 (User)
```python
class User(UserMixin, db.Model):
    __tablename__ = 'User'
    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(100), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=True)
    EmailVerified = db.Column(db.Boolean, default=False)
    VerificationToken = db.Column(db.String(255), nullable=True)
    Role = db.Column(db.String(50), nullable=False)
    Avatar = db.Column(db.String(255), nullable=True)
    
    # 关系定义
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    # 安全方法
    def set_password(self, password):
        import hashlib
        self.Password = hashlib.md5(password.encode()).hexdigest()
    
    def check_password(self, password):
        import hashlib
        return self.Password == hashlib.md5(password.encode()).hexdigest()
```

#### 会议室模型 (Room)
```python
class Room(db.Model):
    __tablename__ = 'MeetingRoom'
    RoomID = db.Column(db.Integer, primary_key=True)
    RoomNumber = db.Column(db.String(50), nullable=False, unique=True)
    RoomName = db.Column(db.String(100), nullable=False)
    Capacity = db.Column(db.Integer, nullable=False)
    Equipment = db.Column(db.String(255))
    Status = db.Column(db.String(50), nullable=False, default='Available')
    RoomType = db.Column(db.String(20), nullable=False, default='Offline')
    Location = db.Column(db.String(255), nullable=True)
    MeetingLink = db.Column(db.String(1000), nullable=True)
    Floor = db.Column(db.String(20), nullable=True)
    Building = db.Column(db.String(50), nullable=True)
    Description = db.Column(db.Text, nullable=True)
    
    # 关系定义
    reservations = db.relationship('Reservation', backref='room', lazy=True)
```

#### 预订模型 (Reservation)
```python
class Reservation(db.Model):
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
```

---

## 🚀 核心功能实现

### 1. 用户认证系统

#### 多方式登录支持
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    username_or_email = request.form.get('username')
    password = request.form.get('password')
    
    # 支持用户名或邮箱登录
    user = User.query.filter(
        (User.UserName == username_or_email) | 
        (User.Email == username_or_email)
    ).first()
    
    if user and user.check_password(password):
        # 邮箱验证检查
        if user.Email and not user.EmailVerified:
            flash('请先验证您的邮箱')
            return render_template('shared/login.html')
        
        login_user(user)
        create_log('登录', f'用户 {user.UserName} 登录成功', user.UserID)
        return redirect(url_for('dashboard'))
```

#### 邮件验证系统
```python
def send_email_async(to, subject, template):
    """异步邮件发送"""
    def send_mail_thread():
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = MAIL_DEFAULT_SENDER
        msg['To'] = to
        
        part = MIMEText(template, 'html')
        msg.attach(part)
        
        # 支持SSL/TLS配置
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            if MAIL_USE_TLS:
                server.starttls()
        
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_DEFAULT_SENDER, to, msg.as_string())
        server.quit()
    
    thread = threading.Thread(target=send_mail_thread)
    thread.start()
```

### 2. 预约管理系统

#### 时间冲突检测
```python
def check_room_availability(room_id, start_time, end_time, exclude_reservation_id=None):
    """检查会议室可用性"""
    query = Reservation.query.filter(
        Reservation.RoomID == room_id,
        Reservation.Status == 'Confirmed',
        Reservation.StartTime < end_time,
        Reservation.EndTime > start_time
    )
    
    if exclude_reservation_id:
        query = query.filter(Reservation.ID != exclude_reservation_id)
    
    conflicting_reservations = query.all()
    return len(conflicting_reservations) == 0
```

#### 自动清理过期预约
```python
def cleanup_expired_reservations():
    """定期清理过期预约"""
    try:
        expired_count = 0
        now = datetime.now()
        
        expired_reservations = Reservation.query.filter(
            Reservation.EndTime < now,
            Reservation.Status.in_(['Pending', 'Confirmed'])
        ).all()
        
        for reservation in expired_reservations:
            reservation.Status = 'Expired'
            expired_count += 1
        
        db.session.commit()
        print(f"清理了 {expired_count} 个过期预约")
        
    except Exception as e:
        db.session.rollback()
        print(f"清理过期预约时出错: {str(e)}")

# 使用APScheduler定期执行
scheduler.add_job(
    func=cleanup_expired_reservations,
    trigger="interval",
    hours=1,
    id='cleanup_expired_reservations'
)
```

### 3. 文件管理系统

#### 中文文件名支持
```python
def secure_filename(filename):
    """支持中文文件名的安全处理"""
    if not filename:
        return ""
    
    # Unicode规范化
    filename = unicodedata.normalize('NFKD', filename)
    # 移除非法字符
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # 替换空格为下划线
    filename = re.sub(r'\s+', '_', filename).strip('._')
    
    if not filename:
        return werkzeug_secure_filename(filename)
    return filename
```

#### 文件上传配置
```python
# 文件上传限制
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 上传目录
UPLOAD_FOLDER_MATERIALS = 'static/uploads/meeting_materials'
UPLOAD_FOLDER_AVATARS = 'static/uploads/avatars'
```

### 4. 系统日志记录

#### 智能IP地址获取
```python
def get_client_ip():
    """获取客户端真实IP地址"""
    headers_to_check = [
        'X-Forwarded-For',      # 代理服务器
        'X-Real-IP',            # Nginx代理
        'X-Forwarded',          # 标准代理头
        'X-Cluster-Client-IP',  # 集群代理
        'CF-Connecting-IP',     # Cloudflare
        'True-Client-IP',       # Akamai
    ]
    
    for header in headers_to_check:
        ip = request.headers.get(header)
        if ip:
            if ',' in ip:
                ip = ip.split(',')[0].strip()
            if ip and ip != 'unknown':
                return ip
    
    return request.environ.get('REMOTE_ADDR', 'unknown')
```

#### 统一日志记录
```python
def create_log(action, description, user_id=None):
    """创建系统操作日志"""
    try:
        if user_id is None:
            if current_user.is_authenticated:
                user_id = current_user.UserID
            else:
                user_id = 0  # 匿名用户
        
        log = Log(
            UserID=user_id,
            Action=action,
            Description=description,
            IPAddress=get_client_ip(),
            Timestamp=datetime.now()
        )
        
        db.session.add(log)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"创建日志失败: {str(e)}")
```

---

## 🔄 数据库事务管理

### 1. 事务处理机制

系统采用SQLAlchemy的事务管理机制，确保数据的ACID特性（原子性、一致性、隔离性、持久性）。

#### 基本事务模式
```python
try:
    # 数据库操作
    db.session.add(object)
    db.session.commit()  # 提交事务
except Exception as e:
    db.session.rollback()  # 回滚事务
    print(f"操作失败: {str(e)}")
```

### 2. 复杂事务处理示例

#### 用户预约创建事务
```python
@app.route('/reservation/new', methods=['POST'])
@login_required
def new_reservation():
    try:
        # 1. 创建预约记录
        reservation = Reservation(
            RoomID=room_id,
            UserID=current_user.UserID,
            StartTime=start_time,
            EndTime=end_time,
            Title=title,
            Purpose=purpose,
            Attendees=attendees,
            Status='Pending'
        )
        db.session.add(reservation)
        
        # 2. 创建操作日志
        create_log('创建预订', f'用户 {current_user.UserName} 预订了会议室 {room.RoomName}')
        
        # 3. 提交所有更改
        db.session.commit()
        
        # 4. 后续异步操作（不影响事务）
        try:
            schedule_auto_confirmation(reservation.ID)  # 安排自动确认
            notify_all_admins(admin_message)  # 通知管理员
        except Exception as async_error:
            print(f"异步操作失败: {str(async_error)}")
        
        flash('预订成功')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()  # 回滚所有更改
        flash(f'预订失败: {str(e)}')
        return redirect(url_for('new_reservation'))
```

#### 用户删除事务（级联操作）
```python
@app.route('/admin/user/delete/<int:id>')
@login_required
def admin_delete_user(id):
    try:
        user = User.query.get_or_404(id)
        username = user.UserName
        
        # 1. 删除用户的所有预订（级联删除）
        Reservation.query.filter_by(UserID=id).delete()
        
        # 2. 删除用户的通知记录
        Notification.query.filter_by(UserID=id).delete()
        
        # 3. 转移日志记录到系统管理员账户
        system_admin_id = 1
        logs = Log.query.filter_by(UserID=id).all()
        for log in logs:
            log.Description = f"[原用户ID:{id}] {log.Description}"
            log.UserID = system_admin_id
        
        # 4. 记录删除操作日志
        create_log('管理员删除用户', f'管理员 {current_user.UserName} 删除了用户 {username}')
        
        # 5. 删除用户主记录
        db.session.delete(user)
        
        # 6. 提交所有更改
        db.session.commit()
        
        flash('用户删除成功')
        
    except Exception as e:
        db.session.rollback()  # 回滚所有更改
        flash(f'删除用户失败: {str(e)}')
        
    return redirect(url_for('admin_users'))
```

#### 邮箱验证事务
```python
@app.route('/verify/<token>')
def verify_email(token):
    try:
        # 1. 验证令牌有效性
        email = confirm_token(token)
        if not email:
            flash('无效的验证链接或链接已过期')
            return redirect(url_for('login'))
        
        # 2. 查找用户并更新状态
        user = User.query.filter_by(Email=email).first()
        if user:
            user.EmailVerified = True
            user.VerificationToken = None  # 清除令牌
            
            # 3. 记录验证操作
            create_log('邮箱验证', f'用户 {user.UserName} 完成邮箱验证')
            
            # 4. 提交事务
            db.session.commit()
            
            flash('邮箱验证成功！您现在可以正常使用系统。')
            
    except Exception as e:
        db.session.rollback()
        flash('验证过程中发生错误，请重试。')
        
    return redirect(url_for('login'))
```

#### 自动确认预约事务
```python
def auto_confirm_reservation(reservation_id):
    """自动确认预约的后台任务"""
    try:
        # 1. 查找预约记录
        reservation = Reservation.query.get(reservation_id)
        if not reservation or reservation.Status != 'Pending':
            return
        
        # 2. 更新预约状态
        reservation.Status = 'Confirmed'
        
        # 3. 创建通知记录
        notification = Notification(
            UserID=reservation.UserID,
            Message=f'您的会议预约 "{reservation.Title}" 已自动确认',
            Status='Unread'
        )
        db.session.add(notification)
        
        # 4. 记录操作日志
        reservation_info = f'会议室: {reservation.room.RoomName}, 时间: {reservation.StartTime.strftime("%Y-%m-%d %H:%M")}'
        create_log('系统自动确认预订', f'预订 ({reservation_info}) 已自动确认', reservation.UserID)
        
        # 5. 提交所有更改
        db.session.commit()
        
        # 6. 发送邮件通知（异步操作）
        try:
            send_email_async(
                reservation.user.Email,
                '预约确认通知',
                render_template('email/confirm_booking.html', reservation=reservation)
            )
        except Exception as email_error:
            print(f"发送邮件失败: {str(email_error)}")
        
    except Exception as e:
        db.session.rollback()
        print(f"自动确认预订失败: {str(e)}")
```

---

## ⚠️ 事务处理问题分析与优化建议

### 🔍 当前代码中发现的问题

#### 1. **事务边界问题**
**问题**：在预约创建中，日志记录在同一个事务中
```python
# 当前代码（存在问题）
try:
    reservation = Reservation(...)
    db.session.add(reservation)
    
    # 问题：日志记录在同一事务中，如果日志失败会回滚整个预约
    create_log('创建预订', f'用户预订了会议室')  # 内部有独立的commit
    
    db.session.commit()  # 这里可能会出现重复提交
except Exception as e:
    db.session.rollback()
```

**优化方案**：
```python
# 优化后的代码
try:
    # 1. 核心业务操作（单一事务）
    reservation = Reservation(...)
    db.session.add(reservation)
    db.session.commit()
    
    # 2. 日志记录（独立事务，失败不影响业务）
    try:
        create_log('创建预订', f'用户预订了会议室', current_user.UserID)
    except Exception as log_error:
        print(f"日志记录失败: {log_error}")  # 不影响主业务
    
    # 3. 异步操作
    schedule_auto_confirmation(reservation.ID)
    notify_all_admins(message)
    
except Exception as e:
    db.session.rollback()
    flash(f'预订失败: {str(e)}')
```

#### 2. **日志函数的事务冲突**
**问题**：`create_log`函数有独立的事务处理
```python
def create_log(action, description, user_id=None):
    try:
        log_entry = Log(...)
        db.session.add(log_entry)
        db.session.commit()  # 独立提交，可能导致事务冲突
    except Exception as e:
        db.session.rollback()  # 可能回滚调用者的事务
```

**优化方案**：
```python
def create_log(action, description, user_id=None, auto_commit=True):
    """
    创建日志记录
    auto_commit: 是否自动提交，False时由调用者控制事务
    """
    try:
        if user_id is None:
            if current_user.is_authenticated:
                user_id = current_user.UserID
            else:
                return False
        
        log_entry = Log(
            UserID=user_id,
            Action=action,
            Description=description,
            IPAddress=get_client_ip(),
            Timestamp=datetime.now()
        )
        
        db.session.add(log_entry)
        
        if auto_commit:
            db.session.commit()
        
        return True
        
    except Exception as e:
        print(f"创建日志失败: {str(e)}")
        if auto_commit:
            try:
                db.session.rollback()
            except:
                pass
        return False

# 支持事务内调用
def create_log_in_transaction(action, description, user_id=None):
    """在已有事务中创建日志，不自动提交"""
    return create_log(action, description, user_id, auto_commit=False)
```

#### 3. **自动确认函数的事务处理问题**
**问题**：在事务中混合了多种操作
```python
def auto_confirm_reservation(reservation_id):
    try:
        reservation.Status = 'Confirmed'
        
        # 问题：通知和日志操作可能失败，但不应回滚状态更新
        send_notification(...)  # 可能失败
        create_log(...)  # 可能失败
        
        db.session.commit()  # 全部失败就全部回滚
    except Exception as e:
        db.session.rollback()
```

**优化方案**：
```python
def auto_confirm_reservation(reservation_id):
    """分层事务处理"""
    try:
        # 1. 核心状态更新（必须成功）
        reservation = db.session.get(Reservation, reservation_id)
        if not reservation or reservation.Status != 'Pending':
            return False
        
        reservation.Status = 'Confirmed'
        db.session.commit()
        
        # 2. 辅助操作（失败不影响核心业务）
        success_operations = []
        
        # 发送通知
        try:
            send_notification(reservation.UserID, f'预订已确认')
            success_operations.append('通知发送')
        except Exception as e:
            print(f"发送通知失败: {e}")
        
        # 记录日志
        try:
            create_log('系统自动确认预订', f'预订已自动确认', reservation.UserID)
            success_operations.append('日志记录')
        except Exception as e:
            print(f"日志记录失败: {e}")
        
        print(f"预订确认成功，完成操作: {', '.join(success_operations)}")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"自动确认失败: {e}")
        return False
```

### 🚀 事务优化最佳实践

#### 1. **使用事务上下文管理器**
```python
from contextlib import contextmanager

@contextmanager
def database_transaction():
    """数据库事务上下文管理器"""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

# 使用示例
def create_reservation_optimized(room_id, user_id, start_time, end_time, **kwargs):
    """优化的预约创建"""
    try:
        with database_transaction():
            # 1. 验证会议室可用性
            if not check_room_availability(room_id, start_time, end_time):
                raise ValueError("会议室在该时间段不可用")
            
            # 2. 创建预约记录
            reservation = Reservation(
                RoomID=room_id,
                UserID=user_id,
                StartTime=start_time,
                EndTime=end_time,
                Status='Pending',
                **kwargs
            )
            db.session.add(reservation)
            db.session.flush()  # 获取ID但不提交
            
            # 3. 在同一事务中记录核心日志
            create_log_in_transaction('创建预订', f'预订会议室 {room_id}', user_id)
            
            # 事务自动提交
        
        # 4. 事务外的异步操作
        schedule_auto_confirmation(reservation.ID)
        notify_admins_async(reservation)
        
        return reservation
        
    except Exception as e:
        print(f"创建预约失败: {e}")
        raise e
```

#### 2. **批量操作优化**
```python
def cleanup_expired_reservations_optimized():
    """优化的批量清理操作"""
    try:
        with database_transaction():
            # 1. 批量查询（使用索引）
            expired_reservations = db.session.query(Reservation).filter(
                Reservation.EndTime < datetime.now(),
                Reservation.Status.in_(['Pending', 'Confirmed'])
            ).with_for_update().all()  # 加锁防止并发修改
            
            if not expired_reservations:
                return 0
            
            # 2. 批量更新（单个SQL语句）
            reservation_ids = [r.ID for r in expired_reservations]
            db.session.query(Reservation).filter(
                Reservation.ID.in_(reservation_ids)
            ).update({
                'Status': 'Expired'
            }, synchronize_session=False)
            
            # 3. 记录清理日志
            create_log_in_transaction(
                '系统维护', 
                f'批量清理 {len(reservation_ids)} 个过期预约'
            )
            
            # 事务自动提交
            
        # 4. 异步通知用户
        notify_users_expired_reservations_async(reservation_ids)
        
        return len(reservation_ids)
        
    except Exception as e:
        print(f"清理过期预约失败: {e}")
        return 0
```

#### 3. **连接池和性能优化**
```python
# 数据库配置优化
from sqlalchemy import event
from sqlalchemy.pool import Pool

# 连接池配置
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,          # 连接池大小
    'pool_timeout': 20,       # 获取连接超时时间
    'pool_recycle': 3600,     # 连接回收时间（1小时）
    'pool_pre_ping': True,    # 连接前ping检查
    'max_overflow': 20        # 最大溢出连接数
}

# 连接池监控
@event.listens_for(Pool, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    print(f"新建数据库连接: {id(dbapi_connection)}")

@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    print(f"从连接池获取连接: {id(dbapi_connection)}")

@event.listens_for(Pool, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    print(f"连接返回连接池: {id(dbapi_connection)}")
```

#### 4. **死锁预防策略**
```python
def transfer_reservation_optimized(from_user_id, to_user_id, reservation_id):
    """预约转移（防死锁版本）"""
    try:
        with database_transaction():
            # 1. 按固定顺序获取锁（防死锁）
            user_ids = sorted([from_user_id, to_user_id])
            users = db.session.query(User).filter(
                User.UserID.in_(user_ids)
            ).with_for_update().order_by(User.UserID).all()
            
            # 2. 获取预约记录锁
            reservation = db.session.query(Reservation).filter(
                Reservation.ID == reservation_id,
                Reservation.UserID == from_user_id
            ).with_for_update().first()
            
            if not reservation:
                raise ValueError("预约不存在或无权限")
            
            # 3. 执行转移
            old_user = reservation.user.UserName
            reservation.UserID = to_user_id
            new_user = next(u for u in users if u.UserID == to_user_id).UserName
            
            # 4. 记录操作日志
            create_log_in_transaction(
                '预约转移', 
                f'预约从 {old_user} 转移给 {new_user}',
                from_user_id
            )
            
        return True
        
    except Exception as e:
        print(f"预约转移失败: {e}")
        return False
```

#### 5. **事务重试机制**
```python
import time
import random
from functools import wraps

def retry_on_deadlock(max_retries=3, base_delay=0.1):
    """死锁重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'deadlock' in error_msg or 'lock wait timeout' in error_msg:
                        if attempt < max_retries - 1:
                            # 指数退避 + 随机抖动
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                            print(f"检测到死锁，{delay:.2f}秒后重试 (尝试 {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            continue
                    raise e
            return None
        return wrapper
    return decorator

# 使用示例
@retry_on_deadlock(max_retries=3)
def create_reservation_with_retry(room_id, user_id, start_time, end_time):
    """带重试机制的预约创建"""
    return create_reservation_optimized(room_id, user_id, start_time, end_time)
```

#### 6. **事务监控和诊断**
```python
def get_transaction_statistics():
    """获取事务统计信息"""
    try:
        stats = db.session.execute(text("""
            SELECT 
                COUNT(*) as active_transactions,
                AVG(TIMESTAMPDIFF(SECOND, trx_started, NOW())) as avg_duration,
                MAX(TIMESTAMPDIFF(SECOND, trx_started, NOW())) as max_duration
            FROM information_schema.innodb_trx
        """)).fetchone()
        
        return {
            'active_transactions': stats.active_transactions or 0,
            'avg_duration': round(stats.avg_duration or 0, 2),
            'max_duration': stats.max_duration or 0
        }
    except Exception as e:
        print(f"获取事务统计失败: {e}")
        return None

def check_long_running_transactions(threshold_seconds=30):
    """检查长时间运行的事务"""
    try:
        long_trx = db.session.execute(text("""
            SELECT 
                trx_id,
                trx_started,
                trx_state,
                TIMESTAMPDIFF(SECOND, trx_started, NOW()) as duration
            FROM information_schema.innodb_trx 
            WHERE TIMESTAMPDIFF(SECOND, trx_started, NOW()) > :threshold
        """), {'threshold': threshold_seconds}).fetchall()
        
        if long_trx:
            print(f"发现 {len(long_trx)} 个长时间运行的事务:")
            for trx in long_trx:
                print(f"  事务ID: {trx.trx_id}, 持续时间: {trx.duration}秒")
        
        return long_trx
        
    except Exception as e:
        print(f"检查长事务失败: {e}")
        return []
```

### 📝 事务优化总结

#### ✅ 优化要点
1. **分离关注点**：核心业务、日志记录、通知发送应分别处理
2. **最小化事务范围**：只在事务中包含必要的数据库操作
3. **使用上下文管理器**：确保事务正确提交或回滚
4. **批量操作优化**：减少数据库往返次数
5. **死锁预防**：按固定顺序获取锁
6. **重试机制**：处理临时性的并发冲突
7. **连接池优化**：合理配置数据库连接参数
8. **监控和诊断**：及时发现和解决性能问题

#### 🎯 性能提升效果
- **事务冲突减少**：通过分层处理减少不必要的回滚
- **响应时间改善**：异步处理非关键操作
- **并发能力提升**：死锁预防和重试机制
- **系统稳定性**：更好的错误隔离和恢复
- **资源利用率**：优化的连接池配置
