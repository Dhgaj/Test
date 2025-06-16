-- ====================================
-- 会议室管理系统 - 数据库表结构创建脚本
-- 创建时间: 2025年6月9日
-- 描述: 完整的数据库表结构定义
-- ====================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS test_meeting_rooms;
USE test_meeting_rooms;

-- ====================================
-- 1. 用户信息表 (User)
-- ====================================
CREATE TABLE User (
    UserID INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID，主键',
    UserName VARCHAR(100) NOT NULL COMMENT '用户名',
    Password VARCHAR(255) NOT NULL COMMENT '密码（MD5加密）',
    Email VARCHAR(100) UNIQUE COMMENT '邮箱地址，唯一',
    EmailVerified BOOLEAN DEFAULT 0 COMMENT '邮箱是否已验证',
    VerificationToken VARCHAR(255) COMMENT '邮箱验证令牌',
    Role VARCHAR(50) NOT NULL COMMENT '用户角色：admin/user',
    Avatar VARCHAR(255) NULL COMMENT '头像文件路径'
) COMMENT '用户信息表';

-- ====================================
-- 2. 会议室信息表 (MeetingRoom)
-- ====================================
CREATE TABLE MeetingRoom (
    RoomID INT PRIMARY KEY AUTO_INCREMENT COMMENT '会议室ID，主键',
    RoomNumber VARCHAR(50) NOT NULL UNIQUE COMMENT '会议室编号，唯一',
    RoomName VARCHAR(100) NOT NULL COMMENT '会议室名称',
    Capacity INT NOT NULL COMMENT '容纳人数',
    Equipment VARCHAR(255) COMMENT '设备列表（逗号分隔）',
    Status VARCHAR(50) NOT NULL DEFAULT 'Available' COMMENT '状态：Available/Unavailable/Maintenance',
    RoomType ENUM('Offline', 'Online') NOT NULL DEFAULT 'Offline' COMMENT '会议室类型：线下/线上',
    Location VARCHAR(255) COMMENT '物理位置（线下会议室）',
    MeetingLink VARCHAR(1000) COMMENT '会议链接（线上会议室）',
    Floor VARCHAR(20) COMMENT '楼层信息',
    Building VARCHAR(50) COMMENT '建筑信息',
    Description TEXT COMMENT '会议室详细描述'
) COMMENT '会议室信息表';

-- ====================================
-- 3. 预订信息表 (Booking)
-- ====================================
CREATE TABLE Booking (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '预订ID，主键',
    RoomID INT NOT NULL COMMENT '会议室ID',
    UserID INT NOT NULL COMMENT '预订用户ID',
    StartTime DATETIME NOT NULL COMMENT '开始时间',
    EndTime DATETIME NOT NULL COMMENT '结束时间',
    Status VARCHAR(50) NOT NULL DEFAULT 'Pending' COMMENT '状态：Pending/Confirmed/Cancelled',
    Title VARCHAR(100) NOT NULL COMMENT '会议标题',
    Purpose TEXT COMMENT '会议目的',
    Attendees INT NOT NULL DEFAULT 1 COMMENT '参会人数',
    MeetingType ENUM('Offline', 'Online') NOT NULL DEFAULT 'Offline' COMMENT '会议类型：线下/线上',
    MeetingPassword VARCHAR(255) NULL COMMENT '会议密码（线上会议）',
    FOREIGN KEY (RoomID) REFERENCES MeetingRoom(RoomID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
) COMMENT '预订信息表';

-- ====================================
-- 4. 设备信息表 (Equipment)
-- ====================================
CREATE TABLE Equipment (
    EquipmentID INT PRIMARY KEY AUTO_INCREMENT COMMENT '设备ID，主键',
    RoomID INT NOT NULL COMMENT '所属会议室ID',
    EquipmentName VARCHAR(100) NOT NULL COMMENT '设备名称',
    Quantity INT NOT NULL DEFAULT 1 COMMENT '设备数量',
    FOREIGN KEY (RoomID) REFERENCES MeetingRoom(RoomID) ON DELETE CASCADE
) COMMENT '设备信息表';

-- ====================================
-- 5. 日志信息表 (Log)
-- ====================================
CREATE TABLE Log (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID，主键',
    UserID INT NOT NULL COMMENT '操作用户ID',
    Action VARCHAR(100) NOT NULL COMMENT '操作类型',
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    Description TEXT COMMENT '操作描述',
    IPAddress VARCHAR(45) COMMENT 'IP地址（支持IPv6）',
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
) COMMENT '操作日志表';

-- ====================================
-- 6. 通知表 (Notification)
-- ====================================
CREATE TABLE Notification (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '通知ID，主键',
    UserID INT NOT NULL COMMENT '接收用户ID',
    Status VARCHAR(50) NOT NULL DEFAULT 'Unread' COMMENT '状态：Unread/Read',
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '通知时间',
    Message TEXT NOT NULL COMMENT '通知内容',
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
) COMMENT '通知表';

-- ====================================
-- 7. 会议室维护记录表 (Maintenance)
-- ====================================
CREATE TABLE Maintenance (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '维护记录ID，主键',
    RoomID INT NOT NULL COMMENT '会议室ID',
    MaintenanceDate DATE NOT NULL COMMENT '维护日期',
    StartTime DATETIME NOT NULL COMMENT '维护开始时间',
    EndTime DATETIME NOT NULL COMMENT '维护结束时间',
    Description TEXT COMMENT '维护描述',
    Status VARCHAR(50) NOT NULL DEFAULT 'Scheduled' COMMENT '状态：Scheduled/InProgress/Completed',
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UpdatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (RoomID) REFERENCES MeetingRoom(RoomID) ON DELETE CASCADE
) COMMENT '会议室维护记录表';

-- ====================================
-- 8. 会议资料表 (MeetingMaterials)
-- ====================================
CREATE TABLE MeetingMaterials (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '资料ID，主键',
    BookingID INT NOT NULL COMMENT '关联预订ID',
    UserID INT NOT NULL COMMENT '上传用户ID',
    Title VARCHAR(200) NOT NULL COMMENT '资料标题',
    FilePath VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    FileName VARCHAR(200) NOT NULL COMMENT '原始文件名',
    FileSize INT NOT NULL COMMENT '文件大小（字节）',
    FileType VARCHAR(50) NOT NULL COMMENT '文件类型（MIME类型）',
    UploadTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    Status VARCHAR(20) NOT NULL DEFAULT 'Active' COMMENT '状态：Active/Deleted',
    Description TEXT COMMENT '资料描述',
    FOREIGN KEY (BookingID) REFERENCES Booking(ID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
) COMMENT '会议资料表';

-- ====================================
-- 索引创建
-- ====================================

-- 用户表索引
CREATE INDEX idx_user_email ON User(Email);
CREATE INDEX idx_user_username ON User(UserName);

-- 会议室表索引
CREATE INDEX idx_room_number ON MeetingRoom(RoomNumber);
CREATE INDEX idx_room_status ON MeetingRoom(Status);
CREATE INDEX idx_room_type ON MeetingRoom(RoomType);

-- 预订表索引
CREATE INDEX idx_booking_room_time ON Booking(RoomID, StartTime, EndTime);
CREATE INDEX idx_booking_user ON Booking(UserID);
CREATE INDEX idx_booking_status ON Booking(Status);
CREATE INDEX idx_booking_time ON Booking(StartTime, EndTime);

-- 维护表索引
CREATE INDEX idx_maintenance_room ON Maintenance(RoomID);
CREATE INDEX idx_maintenance_date ON Maintenance(MaintenanceDate);
CREATE INDEX idx_maintenance_time ON Maintenance(StartTime, EndTime);

-- 日志表索引
CREATE INDEX idx_log_user ON Log(UserID);
CREATE INDEX idx_log_timestamp ON Log(Timestamp);
CREATE INDEX idx_log_action ON Log(Action);

-- 通知表索引
CREATE INDEX idx_notification_user ON Notification(UserID);
CREATE INDEX idx_notification_status ON Notification(Status);
CREATE INDEX idx_notification_timestamp ON Notification(Timestamp);

-- 会议资料表索引
CREATE INDEX idx_materials_booking ON MeetingMaterials(BookingID);
CREATE INDEX idx_materials_user ON MeetingMaterials(UserID);
CREATE INDEX idx_materials_upload_time ON MeetingMaterials(UploadTime);

-- ====================================
-- 表结构创建完成
-- ====================================
SELECT '✅ 数据库表结构创建完成' as 状态, 
       '共创建8个表和相关索引' as 说明;
