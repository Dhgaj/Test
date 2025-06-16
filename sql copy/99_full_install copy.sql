-- ====================================
-- 会议室管理系统 - 完整安装脚本
-- 创建时间: 2025年6月9日
-- 描述: 一键安装整个数据库系统
-- ====================================

-- 此脚本按顺序执行所有必要的SQL文件
-- 适用于全新安装或重新安装

-- ====================================
-- 系统信息
-- ====================================
SELECT '会议室管理系统数据库安装' as 项目名称;
SELECT NOW() as 安装时间;
SELECT VERSION() as MySQL版本;

-- ====================================
-- 第一步:创建数据库和表结构
-- ====================================
SELECT '正在创建数据库和表结构...' as 进度;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS test_meeting_rooms;
USE test_meeting_rooms;

-- 用户信息表
CREATE TABLE User (
    UserID INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID,主键',
    UserName VARCHAR(100) NOT NULL COMMENT '用户名',
    Password VARCHAR(255) NOT NULL COMMENT '密码（MD5加密）',
    Email VARCHAR(100) UNIQUE COMMENT '邮箱地址,唯一',
    EmailVerified BOOLEAN DEFAULT 0 COMMENT '邮箱是否已验证',
    VerificationToken VARCHAR(255) COMMENT '邮箱验证令牌',
    Role VARCHAR(50) NOT NULL COMMENT '用户角色:admin/user',
    Avatar VARCHAR(255) NULL COMMENT '头像文件路径'
) COMMENT '用户信息表';

-- 会议室信息表
CREATE TABLE MeetingRoom (
    RoomID INT PRIMARY KEY AUTO_INCREMENT COMMENT '会议室ID,主键',
    RoomNumber VARCHAR(50) NOT NULL UNIQUE COMMENT '会议室编号,唯一',
    RoomName VARCHAR(100) NOT NULL COMMENT '会议室名称',
    Capacity INT NOT NULL COMMENT '容纳人数',
    Equipment VARCHAR(255) COMMENT '设备列表（逗号分隔）',
    Status VARCHAR(50) NOT NULL DEFAULT 'Available' COMMENT '状态:Available/Unavailable/Maintenance',
    RoomType ENUM('Offline', 'Online') NOT NULL DEFAULT 'Offline' COMMENT '会议室类型:线下/线上',
    Location VARCHAR(255) COMMENT '物理位置（线下会议室）',
    MeetingLink VARCHAR(1000) COMMENT '会议链接（线上会议室）',
    Floor VARCHAR(20) COMMENT '楼层信息',
    Building VARCHAR(50) COMMENT '建筑信息',
    Description TEXT COMMENT '会议室详细描述'
) COMMENT '会议室信息表';

-- 预订信息表
CREATE TABLE Booking (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '预订ID,主键',
    RoomID INT NOT NULL COMMENT '会议室ID',
    UserID INT NOT NULL COMMENT '预订用户ID',
    StartTime DATETIME NOT NULL COMMENT '开始时间',
    EndTime DATETIME NOT NULL COMMENT '结束时间',
    Status VARCHAR(50) NOT NULL DEFAULT 'Pending' COMMENT '状态:Pending/Confirmed/Cancelled',
    Title VARCHAR(100) NOT NULL COMMENT '会议标题',
    Purpose TEXT COMMENT '会议目的',
    Attendees INT NOT NULL DEFAULT 1 COMMENT '参会人数',
    MeetingType ENUM('Offline', 'Online') NOT NULL DEFAULT 'Offline' COMMENT '会议类型:线下/线上',
    MeetingPassword VARCHAR(255) NULL COMMENT '会议密码（线上会议）',
    FOREIGN KEY (RoomID) REFERENCES MeetingRoom(RoomID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
) COMMENT '预订信息表';

-- 设备信息表
CREATE TABLE Equipment (
    EquipmentID INT PRIMARY KEY AUTO_INCREMENT COMMENT '设备ID,主键',
    RoomID INT NOT NULL COMMENT '所属会议室ID',
    EquipmentName VARCHAR(100) NOT NULL COMMENT '设备名称',
    Quantity INT NOT NULL DEFAULT 1 COMMENT '设备数量',
    FOREIGN KEY (RoomID) REFERENCES MeetingRoom(RoomID) ON DELETE CASCADE
) COMMENT '设备信息表';

-- 日志信息表
CREATE TABLE Log (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID,主键',
    UserID INT NOT NULL COMMENT '操作用户ID',
    Action VARCHAR(100) NOT NULL COMMENT '操作类型',
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    Description TEXT COMMENT '操作描述',
    IPAddress VARCHAR(45) COMMENT 'IP地址（支持IPv6）',
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
) COMMENT '操作日志表';

-- 通知表
CREATE TABLE Notification (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '通知ID,主键',
    UserID INT NOT NULL COMMENT '接收用户ID',
    Status VARCHAR(50) NOT NULL DEFAULT 'Unread' COMMENT '状态:Unread/Read',
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '通知时间',
    Message TEXT NOT NULL COMMENT '通知内容',
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
) COMMENT '通知表';

-- 会议室维护记录表
CREATE TABLE Maintenance (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '维护记录ID,主键',
    RoomID INT NOT NULL COMMENT '会议室ID',
    MaintenanceDate DATE NOT NULL COMMENT '维护日期',
    StartTime DATETIME NOT NULL COMMENT '维护开始时间',
    EndTime DATETIME NOT NULL COMMENT '维护结束时间',
    Description TEXT COMMENT '维护描述',
    Status VARCHAR(50) NOT NULL DEFAULT 'Scheduled' COMMENT '状态:Scheduled/InProgress/Completed',
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UpdatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (RoomID) REFERENCES MeetingRoom(RoomID) ON DELETE CASCADE
) COMMENT '会议室维护记录表';

-- 会议资料表
CREATE TABLE MeetingMaterials (
    ID INT PRIMARY KEY AUTO_INCREMENT COMMENT '资料ID,主键',
    BookingID INT NOT NULL COMMENT '关联预订ID',
    UserID INT NOT NULL COMMENT '上传用户ID',
    Title VARCHAR(200) NOT NULL COMMENT '资料标题',
    FilePath VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    FileName VARCHAR(200) NOT NULL COMMENT '原始文件名',
    FileSize INT NOT NULL COMMENT '文件大小（字节）',
    FileType VARCHAR(50) NOT NULL COMMENT '文件类型（MIME类型）',
    UploadTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    Status VARCHAR(20) NOT NULL DEFAULT 'Active' COMMENT '状态:Active/Deleted',
    Description TEXT COMMENT '资料描述',
    FOREIGN KEY (BookingID) REFERENCES Booking(ID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
) COMMENT '会议资料表';

SELECT '✅ 表结构创建完成' as 状态;

-- ====================================
-- 第二步:创建索引
-- ====================================
SELECT '正在创建索引...' as 进度;

-- 索引创建
CREATE INDEX idx_user_email ON User(Email);
CREATE INDEX idx_user_username ON User(UserName);
CREATE INDEX idx_room_number ON MeetingRoom(RoomNumber);
CREATE INDEX idx_room_status ON MeetingRoom(Status);
CREATE INDEX idx_room_type ON MeetingRoom(RoomType);
CREATE INDEX idx_booking_room_time ON Booking(RoomID, StartTime, EndTime);
CREATE INDEX idx_booking_user ON Booking(UserID);
CREATE INDEX idx_booking_status ON Booking(Status);
CREATE INDEX idx_booking_time ON Booking(StartTime, EndTime);
CREATE INDEX idx_maintenance_room ON Maintenance(RoomID);
CREATE INDEX idx_maintenance_date ON Maintenance(MaintenanceDate);
CREATE INDEX idx_maintenance_time ON Maintenance(StartTime, EndTime);
CREATE INDEX idx_log_user ON Log(UserID);
CREATE INDEX idx_log_timestamp ON Log(Timestamp);
CREATE INDEX idx_log_action ON Log(Action);
CREATE INDEX idx_notification_user ON Notification(UserID);
CREATE INDEX idx_notification_status ON Notification(Status);
CREATE INDEX idx_notification_timestamp ON Notification(Timestamp);
CREATE INDEX idx_materials_booking ON MeetingMaterials(BookingID);
CREATE INDEX idx_materials_user ON MeetingMaterials(UserID);
CREATE INDEX idx_materials_upload_time ON MeetingMaterials(UploadTime);

SELECT '✅ 索引创建完成' as 状态;

-- ====================================
-- 第三步:插入基础数据
-- ====================================
SELECT '正在插入基础数据...' as 进度;

-- 插入用户数据
INSERT INTO User (UserName, Password, Email, EmailVerified, Role) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', 'sifanlian@gmail.com', 1, 'admin'),
('liansifan', 'e10adc3949ba59abbe56e057f20f883e', 'liamsifam@gmail.com', 1, 'admin'),
('luwenhui', 'e10adc3949ba59abbe56e057f20f883e', 'luwenhui@gmail.com', 1, 'admin'),
('manager1', 'e10adc3949ba59abbe56e057f20f883e', 'manager1@example.com', 1, 'user'),
('manager2', 'e10adc3949ba59abbe56e057f20f883e', 'manager2@example.com', 1, 'user'),
('user1', 'e10adc3949ba59abbe56e057f20f883e', 'user1@example.com', 1, 'user'),
('user2', 'e10adc3949ba59abbe56e057f20f883e', 'user2@example.com', 1, 'user'),
('user3', 'e10adc3949ba59abbe56e057f20f883e', 'user3@example.com', 1, 'user'),
('randomuser1', 'e10adc3949ba59abbe56e057f20f883e', 'randomuser1@example.com', 0, 'user'),
('randomuser2', 'e10adc3949ba59abbe56e057f20f883e', 'randomuser2@example.com', 1, 'admin'),
('randomuser3', 'e10adc3949ba59abbe56e057f20f883e', 'randomuser3@example.com', 0, 'user'),
('randomuser4', 'e10adc3949ba59abbe56e057f20f883e', 'randomuser4@example.com', 1, 'user'),
('randomuser5', 'e10adc3949ba59abbe56e057f20f883e', 'randomuser5@example.com', 0, 'admin'),
('user1001', 'e10adc3949ba59abbe56e057f20f883e', 'user1001@example.com', 1, 'user'),
('user1002', 'e10adc3949ba59abbe56e057f20f883e', 'user1002@example.com', 0, 'admin'),
('user1003', 'e10adc3949ba59abbe56e057f20f883e', 'user1003@example.com', 1, 'user'),
('user1004', 'e10adc3949ba59abbe56e057f20f883e', 'user1004@example.com', 0, 'user'),
('user1005', 'e10adc3949ba59abbe56e057f20f883e', 'user1005@example.com', 1, 'admin'),
('user1006', 'e10adc3949ba59abbe56e057f20f883e', 'user1006@example.com', 0, 'user'),
('user1007', 'e10adc3949ba59abbe56e057f20f883e', 'user1007@example.com', 1, 'user'),
('user1008', 'e10adc3949ba59abbe56e057f20f883e', 'user1008@example.com', 0, 'admin'),
('user1009', 'e10adc3949ba59abbe56e057f20f883e', 'user1009@example.com', 1, 'user'),
('user1010', 'e10adc3949ba59abbe56e057f20f883e', 'user1010@example.com', 0, 'user'),
('user1011', 'e10adc3949ba59abbe56e057f20f883e', 'user1011@example.com', 1, 'user'),
('user1012', 'e10adc3949ba59abbe56e057f20f883e', 'user1012@example.com', 0, 'admin'),
('user1013', 'e10adc3949ba59abbe56e057f20f883e', 'user1013@example.com', 1, 'user'),
('user1014', 'e10adc3949ba59abbe56e057f20f883e', 'user1014@example.com', 0, 'user'),
('user1015', 'e10adc3949ba59abbe56e057f20f883e', 'user1015@example.com', 1, 'admin'),
('user1016', 'e10adc3949ba59abbe56e057f20f883e', 'user1016@example.com', 0, 'user'),
('user1017', 'e10adc3949ba59abbe56e057f20f883e', 'user1017@example.com', 1, 'user'),
('user1018', 'e10adc3949ba59abbe56e057f20f883e', 'user1018@example.com', 0, 'admin'),
('user1019', 'e10adc3949ba59abbe56e057f20f883e', 'user1019@example.com', 1, 'user'),
('user1020', 'e10adc3949ba59abbe56e057f20f883e', 'user1020@example.com', 0, 'user'),
('user1021', 'e10adc3949ba59abbe56e057f20f883e', 'user1021@example.com', 1, 'user'),
('user1022', 'e10adc3949ba59abbe56e057f20f883e', 'user1022@example.com', 0, 'admin'),
('user1023', 'e10adc3949ba59abbe56e057f20f883e', 'user1023@example.com', 1, 'user'),
('user1024', 'e10adc3949ba59abbe56e057f20f883e', 'user1024@example.com', 0, 'user'),
('user1025', 'e10adc3949ba59abbe56e057f20f883e', 'user1025@example.com', 1, 'admin'),
('user1026', 'e10adc3949ba59abbe56e057f20f883e', 'user1026@example.com', 0, 'user'),
('user1027', 'e10adc3949ba59abbe56e057f20f883e', 'user1027@example.com', 1, 'user'),
('user1028', 'e10adc3949ba59abbe56e057f20f883e', 'user1028@example.com', 0, 'admin'),
('user1029', 'e10adc3949ba59abbe56e057f20f883e', 'user1029@example.com', 1, 'user'),
('user1030', 'e10adc3949ba59abbe56e057f20f883e', 'user1030@example.com', 0, 'user'),
('user1031', 'e10adc3949ba59abbe56e057f20f883e', 'user1031@example.com', 1, 'user'),
('user1032', 'e10adc3949ba59abbe56e057f20f883e', 'user1032@example.com', 0, 'admin'),
('user1033', 'e10adc3949ba59abbe56e057f20f883e', 'user1033@example.com', 1, 'user'),
('user1034', 'e10adc3949ba59abbe56e057f20f883e', 'user1034@example.com', 0, 'user'),
('user1035', 'e10adc3949ba59abbe56e057f20f883e', 'user1035@example.com', 1, 'admin'),
('user1036', 'e10adc3949ba59abbe56e057f20f883e', 'user1036@example.com', 0, 'user'),
('user1037', 'e10adc3949ba59abbe56e057f20f883e', 'user1037@example.com', 1, 'user'),
('user1038', 'e10adc3949ba59abbe56e057f20f883e', 'user1038@example.com', 0, 'admin'),
('user1039', 'e10adc3949ba59abbe56e057f20f883e', 'user1039@example.com', 1, 'user'),
('user1040', 'e10adc3949ba59abbe56e057f20f883e', 'user1040@example.com', 0, 'user'),
('user1041', 'e10adc3949ba59abbe56e057f20f883e', 'user1041@example.com', 1, 'user'),
('user1042', 'e10adc3949ba59abbe56e057f20f883e', 'user1042@example.com', 0, 'admin'),
('user1043', 'e10adc3949ba59abbe56e057f20f883e', 'user1043@example.com', 1, 'user'),
('user1044', 'e10adc3949ba59abbe56e057f20f883e', 'user1044@example.com', 0, 'user'),
('user1045', 'e10adc3949ba59abbe56e057f20f883e', 'user1045@example.com', 1, 'admin'),
('user1046', 'e10adc3949ba59abbe56e057f20f883e', 'user1046@example.com', 0, 'user'),
('user1047', 'e10adc3949ba59abbe56e057f20f883e', 'user1047@example.com', 1, 'user'),
('user1048', 'e10adc3949ba59abbe56e057f20f883e', 'user1048@example.com', 0, 'admin'),
('user1049', 'e10adc3949ba59abbe56e057f20f883e', 'user1049@example.com', 1, 'user'),
('user1050', 'e10adc3949ba59abbe56e057f20f883e', 'user1050@example.com', 0, 'user'),
('user1051', 'e10adc3949ba59abbe56e057f20f883e', 'user1051@example.com', 1, 'user'),
('user1052', 'e10adc3949ba59abbe56e057f20f883e', 'user1052@example.com', 0, 'admin'),
('user1053', 'e10adc3949ba59abbe56e057f20f883e', 'user1053@example.com', 1, 'user'),
('user1054', 'e10adc3949ba59abbe56e057f20f883e', 'user1054@example.com', 0, 'user'),
('user1055', 'e10adc3949ba59abbe56e057f20f883e', 'user1055@example.com', 1, 'admin'),
('user1056', 'e10adc3949ba59abbe56e057f20f883e', 'user1056@example.com', 0, 'user'),
('user1057', 'e10adc3949ba59abbe56e057f20f883e', 'user1057@example.com', 1, 'user'),
('user1058', 'e10adc3949ba59abbe56e057f20f883e', 'user1058@example.com', 0, 'admin'),
('user1059', 'e10adc3949ba59abbe56e057f20f883e', 'user1059@example.com', 1, 'user'),
('user1060', 'e10adc3949ba59abbe56e057f20f883e', 'user1060@example.com', 0, 'user'),
('user1061', 'e10adc3949ba59abbe56e057f20f883e', 'user1061@example.com', 1, 'user'),
('user1062', 'e10adc3949ba59abbe56e057f20f883e', 'user1062@example.com', 0, 'admin'),
('user1063', 'e10adc3949ba59abbe56e057f20f883e', 'user1063@example.com', 1, 'user'),
('user1064', 'e10adc3949ba59abbe56e057f20f883e', 'user1064@example.com', 0, 'user'),
('user1065', 'e10adc3949ba59abbe56e057f20f883e', 'user1065@example.com', 1, 'admin'),
('user1066', 'e10adc3949ba59abbe56e057f20f883e', 'user1066@example.com', 0, 'user'),
('user1067', 'e10adc3949ba59abbe56e057f20f883e', 'user1067@example.com', 1, 'user'),
('user1068', 'e10adc3949ba59abbe56e057f20f883e', 'user1068@example.com', 0, 'admin'),
('user1069', 'e10adc3949ba59abbe56e057f20f883e', 'user1069@example.com', 1, 'user'),
('user1070', 'e10adc3949ba59abbe56e057f20f883e', 'user1070@example.com', 0, 'user'),
('user1071', 'e10adc3949ba59abbe56e057f20f883e', 'user1071@example.com', 1, 'user'),
('user1072', 'e10adc3949ba59abbe56e057f20f883e', 'user1072@example.com', 0, 'admin'),
('user1073', 'e10adc3949ba59abbe56e057f20f883e', 'user1073@example.com', 1, 'user'),
('user1074', 'e10adc3949ba59abbe56e057f20f883e', 'user1074@example.com', 0, 'user'),
('user1075', 'e10adc3949ba59abbe56e057f20f883e', 'user1075@example.com', 1, 'admin'),
('user1076', 'e10adc3949ba59abbe56e057f20f883e', 'user1076@example.com', 0, 'user'),
('user1077', 'e10adc3949ba59abbe56e057f20f883e', 'user1077@example.com', 1, 'user'),
('user1078', 'e10adc3949ba59abbe56e057f20f883e', 'user1078@example.com', 0, 'admin'),
('user1079', 'e10adc3949ba59abbe56e057f20f883e', 'user1079@example.com', 1, 'user'),
('user1080', 'e10adc3949ba59abbe56e057f20f883e', 'user1080@example.com', 0, 'user'),
('user1081', 'e10adc3949ba59abbe56e057f20f883e', 'user1081@example.com', 1, 'user'),
('user1082', 'e10adc3949ba59abbe56e057f20f883e', 'user1082@example.com', 0, 'admin'),
('user1083', 'e10adc3949ba59abbe56e057f20f883e', 'user1083@example.com', 1, 'user'),
('user1084', 'e10adc3949ba59abbe56e057f20f883e', 'user1084@example.com', 0, 'user'),
('user1085', 'e10adc3949ba59abbe56e057f20f883e', 'user1085@example.com', 1, 'admin'),
('user1086', 'e10adc3949ba59abbe56e057f20f883e', 'user1086@example.com', 0, 'user'),
('user1087', 'e10adc3949ba59abbe56e057f20f883e', 'user1087@example.com', 1, 'user'),
('user1088', 'e10adc3949ba59abbe56e057f20f883e', 'user1088@example.com', 0, 'admin'),
('user1089', 'e10adc3949ba59abbe56e057f20f883e', 'user1089@example.com', 1, 'user'),
('user1090', 'e10adc3949ba59abbe56e057f20f883e', 'user1090@example.com', 0, 'user'),
('user1091', 'e10adc3949ba59abbe56e057f20f883e', 'user1091@example.com', 1, 'user'),
('user1092', 'e10adc3949ba59abbe56e057f20f883e', 'user1092@example.com', 0, 'admin'),
('user1093', 'e10adc3949ba59abbe56e057f20f883e', 'user1093@example.com', 1, 'user'),
('user1094', 'e10adc3949ba59abbe56e057f20f883e', 'user1094@example.com', 0, 'user'),
('user1095', 'e10adc3949ba59abbe56e057f20f883e', 'user1095@example.com', 1, 'admin'),
('user1096', 'e10adc3949ba59abbe56e057f20f883e', 'user1096@example.com', 0, 'user'),
('user1097', 'e10adc3949ba59abbe56e057f20f883e', 'user1097@example.com', 1, 'user'),
('user1098', 'e10adc3949ba59abbe56e057f20f883e', 'user1098@example.com', 0, 'admin'),
('user1099', 'e10adc3949ba59abbe56e057f20f883e', 'user1099@example.com', 1, 'user'),
('user1100', 'e10adc3949ba59abbe56e057f20f883e', 'user1100@example.com', 0, 'user'),
('user1101', 'e10adc3949ba59abbe56e057f20f883e', 'user1101@example.com', 1, 'user'),
('user1102', 'e10adc3949ba59abbe56e057f20f883e', 'user1102@example.com', 0, 'admin'),
('user1103', 'e10adc3949ba59abbe56e057f20f883e', 'user1103@example.com', 1, 'user'),
('user1104', 'e10adc3949ba59abbe56e057f20f883e', 'user1104@example.com', 0, 'user'),
('user1105', 'e10adc3949ba59abbe56e057f20f883e', 'user1105@example.com', 1, 'admin'),
('user1106', 'e10adc3949ba59abbe56e057f20f883e', 'user1106@example.com', 0, 'user'),
('user1107', 'e10adc3949ba59abbe56e057f20f883e', 'user1107@example.com', 1, 'user'),
('user1108', 'e10adc3949ba59abbe56e057f20f883e', 'user1108@example.com', 0, 'admin'),
('user1109', 'e10adc3949ba59abbe56e057f20f883e', 'user1109@example.com', 1, 'user'),
('user1110', 'e10adc3949ba59abbe56e057f20f883e', 'user1110@example.com', 0, 'user'),
('user1111', 'e10adc3949ba59abbe56e057f20f883e', 'user1111@example.com', 1, 'user'),
('user1112', 'e10adc3949ba59abbe56e057f20f883e', 'user1112@example.com', 0, 'admin'),
('user1113', 'e10adc3949ba59abbe56e057f20f883e', 'user1113@example.com', 1, 'user'),
('user1114', 'e10adc3949ba59abbe56e057f20f883e', 'user1114@example.com', 0, 'user'),
('user1115', 'e10adc3949ba59abbe56e057f20f883e', 'user1115@example.com', 1, 'admin'),
('user1116', 'e10adc3949ba59abbe56e057f20f883e', 'user1116@example.com', 0, 'user'),
('user1117', 'e10adc3949ba59abbe56e057f20f883e', 'user1117@example.com', 1, 'user'),
('user1118', 'e10adc3949ba59abbe56e057f20f883e', 'user1118@example.com', 0, 'admin'),
('user1119', 'e10adc3949ba59abbe56e057f20f883e', 'user1119@example.com', 1, 'user'),
('user1120', 'e10adc3949ba59abbe56e057f20f883e', 'user1120@example.com', 0, 'user'),
('user1121', 'e10adc3949ba59abbe56e057f20f883e', 'user1121@example.com', 1, 'user'),
('user1122', 'e10adc3949ba59abbe56e057f20f883e', 'user1122@example.com', 0, 'admin'),
('user1123', 'e10adc3949ba59abbe56e057f20f883e', 'user1123@example.com', 1, 'user'),
('user1124', 'e10adc3949ba59abbe56e057f20f883e', 'user1124@example.com', 0, 'user'),
('user1125', 'e10adc3949ba59abbe56e057f20f883e', 'user1125@example.com', 1, 'admin'),
('user1126', 'e10adc3949ba59abbe56e057f20f883e', 'user1126@example.com', 0, 'user'),
('user1127', 'e10adc3949ba59abbe56e057f20f883e', 'user1127@example.com', 1, 'user'),
('user1128', 'e10adc3949ba59abbe56e057f20f883e', 'user1128@example.com', 0, 'admin'),
('user1129', 'e10adc3949ba59abbe56e057f20f883e', 'user1129@example.com', 1, 'user'),
('user1130', 'e10adc3949ba59abbe56e057f20f883e', 'user1130@example.com', 0, 'user'),
('user1131', 'e10adc3949ba59abbe56e057f20f883e', 'user1131@example.com', 1, 'user'),
('user1132', 'e10adc3949ba59abbe56e057f20f883e', 'user1132@example.com', 0, 'admin'),
('user1133', 'e10adc3949ba59abbe56e057f20f883e', 'user1133@example.com', 1, 'user'),
('user1134', 'e10adc3949ba59abbe56e057f20f883e', 'user1134@example.com', 0, 'user'),
('user1135', 'e10adc3949ba59abbe56e057f20f883e', 'user1135@example.com', 1, 'admin'),
('user1136', 'e10adc3949ba59abbe56e057f20f883e', 'user1136@example.com', 0, 'user'),
('user1137', 'e10adc3949ba59abbe56e057f20f883e', 'user1137@example.com', 1, 'user'),
('user1138', 'e10adc3949ba59abbe56e057f20f883e', 'user1138@example.com', 0, 'admin'),
('user1139', 'e10adc3949ba59abbe56e057f20f883e', 'user1139@example.com', 1, 'user'),
('user1140', 'e10adc3949ba59abbe56e057f20f883e', 'user1140@example.com', 0, 'user'),
('user1141', 'e10adc3949ba59abbe56e057f20f883e', 'user1141@example.com', 1, 'user'),
('user1142', 'e10adc3949ba59abbe56e057f20f883e', 'user1142@example.com', 0, 'admin'),
('user1143', 'e10adc3949ba59abbe56e057f20f883e', 'user1143@example.com', 1, 'user'),
('user1144', 'e10adc3949ba59abbe56e057f20f883e', 'user1144@example.com', 0, 'user'),
('user1145', 'e10adc3949ba59abbe56e057f20f883e', 'user1145@example.com', 1, 'admin'),
('user1146', 'e10adc3949ba59abbe56e057f20f883e', 'user1146@example.com', 0, 'user'),
('user1147', 'e10adc3949ba59abbe56e057f20f883e', 'user1147@example.com', 1, 'user'),
('user1148', 'e10adc3949ba59abbe56e057f20f883e', 'user1148@example.com', 0, 'admin'),
('user1149', 'e10adc3949ba59abbe56e057f20f883e', 'user1149@example.com', 1, 'user'),
('user1150', 'e10adc3949ba59abbe56e057f20f883e', 'user1150@example.com', 0, 'user'),
('user1151', 'e10adc3949ba59abbe56e057f20f883e', 'user1151@example.com', 1, 'user'),
('user1152', 'e10adc3949ba59abbe56e057f20f883e', 'user1152@example.com', 0, 'admin'),
('user1153', 'e10adc3949ba59abbe56e057f20f883e', 'user1153@example.com', 1, 'user'),
('user1154', 'e10adc3949ba59abbe56e057f20f883e', 'user1154@example.com', 0, 'user'),
('user1155', 'e10adc3949ba59abbe56e057f20f883e', 'user1155@example.com', 1, 'admin'),
('user1156', 'e10adc3949ba59abbe56e057f20f883e', 'user1156@example.com', 0, 'user'),
('user1157', 'e10adc3949ba59abbe56e057f20f883e', 'user1157@example.com', 1, 'user'),
('user1158', 'e10adc3949ba59abbe56e057f20f883e', 'user1158@example.com', 0, 'admin'),
('user1159', 'e10adc3949ba59abbe56e057f20f883e', 'user1159@example.com', 1, 'user'),
('user1160', 'e10adc3949ba59abbe56e057f20f883e', 'user1160@example.com', 0, 'user'),
('user1161', 'e10adc3949ba59abbe56e057f20f883e', 'user1161@example.com', 1, 'user'),
('user1162', 'e10adc3949ba59abbe56e057f20f883e', 'user1162@example.com', 0, 'admin'),
('user1163', 'e10adc3949ba59abbe56e057f20f883e', 'user1163@example.com', 1, 'user'),
('user1164', 'e10adc3949ba59abbe56e057f20f883e', 'user1164@example.com', 0, 'user'),
('user1165', 'e10adc3949ba59abbe56e057f20f883e', 'user1165@example.com', 1, 'admin'),
('user1166', 'e10adc3949ba59abbe56e057f20f883e', 'user1166@example.com', 0, 'user'),
('user1167', 'e10adc3949ba59abbe56e057f20f883e', 'user1167@example.com', 1, 'user'),
('user1168', 'e10adc3949ba59abbe56e057f20f883e', 'user1168@example.com', 0, 'admin'),
('user1169', 'e10adc3949ba59abbe56e057f20f883e', 'user1169@example.com', 1, 'user'),
('user1170', 'e10adc3949ba59abbe56e057f20f883e', 'user1170@example.com', 0, 'user'),
('user1171', 'e10adc3949ba59abbe56e057f20f883e', 'user1171@example.com', 1, 'user'),
('user1172', 'e10adc3949ba59abbe56e057f20f883e', 'user1172@example.com', 0, 'admin'),
('user1173', 'e10adc3949ba59abbe56e057f20f883e', 'user1173@example.com', 1, 'user'),
('user1174', 'e10adc3949ba59abbe56e057f20f883e', 'user1174@example.com', 0, 'user'),
('user1175', 'e10adc3949ba59abbe56e057f20f883e', 'user1175@example.com', 1, 'admin'),
('user1176', 'e10adc3949ba59abbe56e057f20f883e', 'user1176@example.com', 0, 'user'),
('user1177', 'e10adc3949ba59abbe56e057f20f883e', 'user1177@example.com', 1, 'user'),
('user1178', 'e10adc3949ba59abbe56e057f20f883e', 'user1178@example.com', 0, 'admin'),
('user1179', 'e10adc3949ba59abbe56e057f20f883e', 'user1179@example.com', 1, 'user'),
('user1180', 'e10adc3949ba59abbe56e057f20f883e', 'user1180@example.com', 0, 'user'),
('user1181', 'e10adc3949ba59abbe56e057f20f883e', 'user1181@example.com', 1, 'user'),
('user1182', 'e10adc3949ba59abbe56e057f20f883e', 'user1182@example.com', 0, 'admin'),
('user1183', 'e10adc3949ba59abbe56e057f20f883e', 'user1183@example.com', 1, 'user'),
('user1184', 'e10adc3949ba59abbe56e057f20f883e', 'user1184@example.com', 0, 'user'),
('user1185', 'e10adc3949ba59abbe56e057f20f883e', 'user1185@example.com', 1, 'admin'),
('user1186', 'e10adc3949ba59abbe56e057f20f883e', 'user1186@example.com', 0, 'user'),
('user1187', 'e10adc3949ba59abbe56e057f20f883e', 'user1187@example.com', 1, 'user'),
('user1188', 'e10adc3949ba59abbe56e057f20f883e', 'user1188@example.com', 0, 'admin'),
('user1189', 'e10adc3949ba59abbe56e057f20f883e', 'user1189@example.com', 1, 'user'),
('user1190', 'e10adc3949ba59abbe56e057f20f883e', 'user1190@example.com', 0, 'user'),
('user1191', 'e10adc3949ba59abbe56e057f20f883e', 'user1191@example.com', 1, 'user'),
('user1192', 'e10adc3949ba59abbe56e057f20f883e', 'user1192@example.com', 0, 'admin'),
('user1193', 'e10adc3949ba59abbe56e057f20f883e', 'user1193@example.com', 1, 'user'),
('user1194', 'e10adc3949ba59abbe56e057f20f883e', 'user1194@example.com', 0, 'user'),
('user1195', 'e10adc3949ba59abbe56e057f20f883e', 'user1195@example.com', 1, 'admin'),
('user1196', 'e10adc3949ba59abbe56e057f20f883e', 'user1196@example.com', 0, 'user'),
('user1197', 'e10adc3949ba59abbe56e057f20f883e', 'user1197@example.com', 1, 'user'),
('user1198', 'e10adc3949ba59abbe56e057f20f883e', 'user1198@example.com', 0, 'admin'),
('user1199', 'e10adc3949ba59abbe56e057f20f883e', 'user1199@example.com', 1, 'user'),
('user1200', 'e10adc3949ba59abbe56e057f20f883e', 'user1200@example.com', 0, 'user'),
('user1201', 'e10adc3949ba59abbe56e057f20f883e', 'user1201@example.com', 1, 'user'),
('user1202', 'e10adc3949ba59abbe56e057f20f883e', 'user1202@example.com', 0, 'admin'),
('user1203', 'e10adc3949ba59abbe56e057f20f883e', 'user1203@example.com', 1, 'user'),
('user1204', 'e10adc3949ba59abbe56e057f20f883e', 'user1204@example.com', 0, 'user'),
('user1205', 'e10adc3949ba59abbe56e057f20f883e', 'user1205@example.com', 1, 'admin'),
('user1206', 'e10adc3949ba59abbe56e057f20f883e', 'user1206@example.com', 0, 'user'),
('user1207', 'e10adc3949ba59abbe56e057f20f883e', 'user1207@example.com', 1, 'user'),
('user1208', 'e10adc3949ba59abbe56e057f20f883e', 'user1208@example.com', 0, 'admin'),
('user1209', 'e10adc3949ba59abbe56e057f20f883e', 'user1209@example.com', 1, 'user'),
('user1210', 'e10adc3949ba59abbe56e057f20f883e', 'user1210@example.com', 0, 'user'),
('user1211', 'e10adc3949ba59abbe56e057f20f883e', 'user1211@example.com', 1, 'user'),
('user1212', 'e10adc3949ba59abbe56e057f20f883e', 'user1212@example.com', 0, 'admin'),
('user1213', 'e10adc3949ba59abbe56e057f20f883e', 'user1213@example.com', 1, 'user'),
('user1214', 'e10adc3949ba59abbe56e057f20f883e', 'user1214@example.com', 0, 'user'),
('user1215', 'e10adc3949ba59abbe56e057f20f883e', 'user1215@example.com', 1, 'admin'),
('user1216', 'e10adc3949ba59abbe56e057f20f883e', 'user1216@example.com', 0, 'user'),
('user1217', 'e10adc3949ba59abbe56e057f20f883e', 'user1217@example.com', 1, 'user'),
('user1218', 'e10adc3949ba59abbe56e057f20f883e', 'user1218@example.com', 0, 'admin'),
('user1219', 'e10adc3949ba59abbe56e057f20f883e', 'user1219@example.com', 1, 'user'),
('user1220', 'e10adc3949ba59abbe56e057f20f883e', 'user1220@example.com', 0, 'user'),
('user1221', 'e10adc3949ba59abbe56e057f20f883e', 'user1221@example.com', 1, 'user'),
('user1222', 'e10adc3949ba59abbe56e057f20f883e', 'user1222@example.com', 0, 'admin'),
('user1223', 'e10adc3949ba59abbe56e057f20f883e', 'user1223@example.com', 1, 'user'),
('user1224', 'e10adc3949ba59abbe56e057f20f883e', 'user1224@example.com', 0, 'user'),
('user1225', 'e10adc3949ba59abbe56e057f20f883e', 'user1225@example.com', 1, 'admin'),
('user1226', 'e10adc3949ba59abbe56e057f20f883e', 'user1226@example.com', 0, 'user'),
('user1227', 'e10adc3949ba59abbe56e057f20f883e', 'user1227@example.com', 1, 'user'),
('user1228', 'e10adc3949ba59abbe56e057f20f883e', 'user1228@example.com', 0, 'admin'),
('user1229', 'e10adc3949ba59abbe56e057f20f883e', 'user1229@example.com', 1, 'user'),
('user1230', 'e10adc3949ba59abbe56e057f20f883e', 'user1230@example.com', 0, 'user'),
('user1231', 'e10adc3949ba59abbe56e057f20f883e', 'user1231@example.com', 1, 'user'),
('user1232', 'e10adc3949ba59abbe56e057f20f883e', 'user1232@example.com', 0, 'admin'),
('user1233', 'e10adc3949ba59abbe56e057f20f883e', 'user1233@example.com', 1, 'user'),
('user1234', 'e10adc3949ba59abbe56e057f20f883e', 'user1234@example.com', 0, 'user'),
('user1235', 'e10adc3949ba59abbe56e057f20f883e', 'user1235@example.com', 1, 'admin'),
('user1236', 'e10adc3949ba59abbe56e057f20f883e', 'user1236@example.com', 0, 'user'),
('user1237', 'e10adc3949ba59abbe56e057f20f883e', 'user1237@example.com', 1, 'user'),
('user1238', 'e10adc3949ba59abbe56e057f20f883e', 'user1238@example.com', 0, 'admin'),
('user1239', 'e10adc3949ba59abbe56e057f20f883e', 'user1239@example.com', 1, 'user'),
('user1240', 'e10adc3949ba59abbe56e057f20f883e', 'user1240@example.com', 0, 'user'),
('user1241', 'e10adc3949ba59abbe56e057f20f883e', 'user1241@example.com', 1, 'user'),
('user1242', 'e10adc3949ba59abbe56e057f20f883e', 'user1242@example.com', 0, 'admin'),
('user1243', 'e10adc3949ba59abbe56e057f20f883e', 'user1243@example.com', 1, 'user'),
('user1244', 'e10adc3949ba59abbe56e057f20f883e', 'user1244@example.com', 0, 'user'),
('user1245', 'e10adc3949ba59abbe56e057f20f883e', 'user1245@example.com', 1, 'admin'),
('user1246', 'e10adc3949ba59abbe56e057f20f883e', 'user1246@example.com', 0, 'user'),
('user1247', 'e10adc3949ba59abbe56e057f20f883e', 'user1247@example.com', 1, 'user'),
('user1248', 'e10adc3949ba59abbe56e057f20f883e', 'user1248@example.com', 0, 'admin'),
('user1249', 'e10adc3949ba59abbe56e057f20f883e', 'user1249@example.com', 1, 'user'),
('user1250', 'e10adc3949ba59abbe56e057f20f883e', 'user1250@example.com', 0, 'user'),
('user1251', 'e10adc3949ba59abbe56e057f20f883e', 'user1251@example.com', 1, 'user'),
('user1252', 'e10adc3949ba59abbe56e057f20f883e', 'user1252@example.com', 0, 'admin'),
('user1253', 'e10adc3949ba59abbe56e057f20f883e', 'user1253@example.com', 1, 'user'),
('user1254', 'e10adc3949ba59abbe56e057f20f883e', 'user1254@example.com', 0, 'user'),
('user1255', 'e10adc3949ba59abbe56e057f20f883e', 'user1255@example.com', 1, 'admin'),
('user1256', 'e10adc3949ba59abbe56e057f20f883e', 'user1256@example.com', 0, 'user'),
('user1257', 'e10adc3949ba59abbe56e057f20f883e', 'user1257@example.com', 1, 'user'),
('user1258', 'e10adc3949ba59abbe56e057f20f883e', 'user1258@example.com', 0, 'admin'),
('user1259', 'e10adc3949ba59abbe56e057f20f883e', 'user1259@example.com', 1, 'user'),
('user1260', 'e10adc3949ba59abbe56e057f20f883e', 'user1260@example.com', 0, 'user'),
('user1261', 'e10adc3949ba59abbe56e057f20f883e', 'user1261@example.com', 1, 'user'),
('user1262', 'e10adc3949ba59abbe56e057f20f883e', 'user1262@example.com', 0, 'admin'),
('user1263', 'e10adc3949ba59abbe56e057f20f883e', 'user1263@example.com', 1, 'user'),
('user1264', 'e10adc3949ba59abbe56e057f20f883e', 'user1264@example.com', 0, 'user'),
('user1265', 'e10adc3949ba59abbe56e057f20f883e', 'user1265@example.com', 1, 'admin'),
('user1266', 'e10adc3949ba59abbe56e057f20f883e', 'user1266@example.com', 0, 'user'),
('user1267', 'e10adc3949ba59abbe56e057f20f883e', 'user1267@example.com', 1, 'user'),
('user1268', 'e10adc3949ba59abbe56e057f20f883e', 'user1268@example.com', 0, 'admin'),
('user1269', 'e10adc3949ba59abbe56e057f20f883e', 'user1269@example.com', 1, 'user'),
('user1270', 'e10adc3949ba59abbe56e057f20f883e', 'user1270@example.com', 0, 'user'),
('user1271', 'e10adc3949ba59abbe56e057f20f883e', 'user1271@example.com', 1, 'user'),
('user1272', 'e10adc3949ba59abbe56e057f20f883e', 'user1272@example.com', 0, 'admin'),
('user1273', 'e10adc3949ba59abbe56e057f20f883e', 'user1273@example.com', 1, 'user'),
('user1274', 'e10adc3949ba59abbe56e057f20f883e', 'user1274@example.com', 0, 'user'),
('user1275', 'e10adc3949ba59abbe56e057f20f883e', 'user1275@example.com', 1, 'admin'),
('user1276', 'e10adc3949ba59abbe56e057f20f883e', 'user1276@example.com', 0, 'user'),
('user1277', 'e10adc3949ba59abbe56e057f20f883e', 'user1277@example.com', 1, 'user'),
('user1278', 'e10adc3949ba59abbe56e057f20f883e', 'user1278@example.com', 0, 'admin'),
('user1279', 'e10adc3949ba59abbe56e057f20f883e', 'user1279@example.com', 1, 'user'),
('user1280', 'e10adc3949ba59abbe56e057f20f883e', 'user1280@example.com', 0, 'user'),
('user1281', 'e10adc3949ba59abbe56e057f20f883e', 'user1281@example.com', 1, 'user'),
('user1282', 'e10adc3949ba59abbe56e057f20f883e', 'user1282@example.com', 0, 'admin'),
('user1283', 'e10adc3949ba59abbe56e057f20f883e', 'user1283@example.com', 1, 'user'),
('user1284', 'e10adc3949ba59abbe56e057f20f883e', 'user1284@example.com', 0, 'user'),
('user1285', 'e10adc3949ba59abbe56e057f20f883e', 'user1285@example.com', 1, 'admin'),
('user1286', 'e10adc3949ba59abbe56e057f20f883e', 'user1286@example.com', 0, 'user'),
('user1287', 'e10adc3949ba59abbe56e057f20f883e', 'user1287@example.com', 1, 'user'),
('user1288', 'e10adc3949ba59abbe56e057f20f883e', 'user1288@example.com', 0, 'admin'),
('user1289', 'e10adc3949ba59abbe56e057f20f883e', 'user1289@example.com', 1, 'user'),
('user1290', 'e10adc3949ba59abbe56e057f20f883e', 'user1290@example.com', 0, 'user'),
('user1291', 'e10adc3949ba59abbe56e057f20f883e', 'user1291@example.com', 1, 'user'),
('user1292', 'e10adc3949ba59abbe56e057f20f883e', 'user1292@example.com', 0, 'admin'),
('user1293', 'e10adc3949ba59abbe56e057f20f883e', 'user1293@example.com', 1, 'user'),
('user1294', 'e10adc3949ba59abbe56e057f20f883e', 'user1294@example.com', 0, 'user'),
('user1295', 'e10adc3949ba59abbe56e057f20f883e', 'user1295@example.com', 1, 'admin'),
('user1296', 'e10adc3949ba59abbe56e057f20f883e', 'user1296@example.com', 0, 'user'),
('user1297', 'e10adc3949ba59abbe56e057f20f883e', 'user1297@example.com', 1, 'user'),
('user1298', 'e10adc3949ba59abbe56e057f20f883e', 'user1298@example.com', 0, 'admin'),
('user1299', 'e10adc3949ba59abbe56e057f20f883e', 'user1299@example.com', 1, 'user'),
('user1300', 'e10adc3949ba59abbe56e057f20f883e', 'user1300@example.com', 0, 'user'),
('user1301', 'e10adc3949ba59abbe56e057f20f883e', 'user1301@example.com', 1, 'user'),
('user1302', 'e10adc3949ba59abbe56e057f20f883e', 'user1302@example.com', 0, 'admin'),
('user1303', 'e10adc3949ba59abbe56e057f20f883e', 'user1303@example.com', 1, 'user'),
('user1304', 'e10adc3949ba59abbe56e057f20f883e', 'user1304@example.com', 0, 'user'),
('user1305', 'e10adc3949ba59abbe56e057f20f883e', 'user1305@example.com', 1, 'admin'),
('user1306', 'e10adc3949ba59abbe56e057f20f883e', 'user1306@example.com', 0, 'user'),
('user1307', 'e10adc3949ba59abbe56e057f20f883e', 'user1307@example.com', 1, 'user'),
('user1308', 'e10adc3949ba59abbe56e057f20f883e', 'user1308@example.com', 0, 'admin'),
('user1309', 'e10adc3949ba59abbe56e057f20f883e', 'user1309@example.com', 1, 'user'),
('user1310', 'e10adc3949ba59abbe56e057f20f883e', 'user1310@example.com', 0, 'user'),
('user1311', 'e10adc3949ba59abbe56e057f20f883e', 'user1311@example.com', 1, 'user'),
('user1312', 'e10adc3949ba59abbe56e057f20f883e', 'user1312@example.com', 0, 'admin'),
('user1313', 'e10adc3949ba59abbe56e057f20f883e', 'user1313@example.com', 1, 'user'),
('user1314', 'e10adc3949ba59abbe56e057f20f883e', 'user1314@example.com', 0, 'user'),
('user1315', 'e10adc3949ba59abbe56e057f20f883e', 'user1315@example.com', 1, 'admin'),
('user1316', 'e10adc3949ba59abbe56e057f20f883e', 'user1316@example.com', 0, 'user'),
('user1317', 'e10adc3949ba59abbe56e057f20f883e', 'user1317@example.com', 1, 'user'),
('user1318', 'e10adc3949ba59abbe56e057f20f883e', 'user1318@example.com', 0, 'admin'),
('user1319', 'e10adc3949ba59abbe56e057f20f883e', 'user1319@example.com', 1, 'user'),
('user1320', 'e10adc3949ba59abbe56e057f20f883e', 'user1320@example.com', 0, 'user'),
('user1321', 'e10adc3949ba59abbe56e057f20f883e', 'user1321@example.com', 1, 'user'),
('user1322', 'e10adc3949ba59abbe56e057f20f883e', 'user1322@example.com', 0, 'admin'),
('user1323', 'e10adc3949ba59abbe56e057f20f883e', 'user1323@example.com', 1, 'user'),
('user1324', 'e10adc3949ba59abbe56e057f20f883e', 'user1324@example.com', 0, 'user'),
('user1325', 'e10adc3949ba59abbe56e057f20f883e', 'user1325@example.com', 1, 'admin'),
('user1326', 'e10adc3949ba59abbe56e057f20f883e', 'user1326@example.com', 0, 'user'),
('user1327', 'e10adc3949ba59abbe56e057f20f883e', 'user1327@example.com', 1, 'user'),
('user1328', 'e10adc3949ba59abbe56e057f20f883e', 'user1328@example.com', 0, 'admin'),
('user1329', 'e10adc3949ba59abbe56e057f20f883e', 'user1329@example.com', 1, 'user'),
('user1330', 'e10adc3949ba59abbe56e057f20f883e', 'user1330@example.com', 0, 'user'),
('user1331', 'e10adc3949ba59abbe56e057f20f883e', 'user1331@example.com', 1, 'user'),
('user1332', 'e10adc3949ba59abbe56e057f20f883e', 'user1332@example.com', 0, 'admin'),
('user1333', 'e10adc3949ba59abbe56e057f20f883e', 'user1333@example.com', 1, 'user'),
('user1334', 'e10adc3949ba59abbe56e057f20f883e', 'user1334@example.com', 0, 'user'),
('user1335', 'e10adc3949ba59abbe56e057f20f883e', 'user1335@example.com', 1, 'admin'),
('user1336', 'e10adc3949ba59abbe56e057f20f883e', 'user1336@example.com', 0, 'user'),
('user1337', 'e10adc3949ba59abbe56e057f20f883e', 'user1337@example.com', 1, 'user'),
('user1338', 'e10adc3949ba59abbe56e057f20f883e', 'user1338@example.com', 0, 'admin'),
('user1339', 'e10adc3949ba59abbe56e057f20f883e', 'user1339@example.com', 1, 'user'),
('user1340', 'e10adc3949ba59abbe56e057f20f883e', 'user1340@example.com', 0, 'user'),
('user1341', 'e10adc3949ba59abbe56e057f20f883e', 'user1341@example.com', 1, 'user'),
('user1342', 'e10adc3949ba59abbe56e057f20f883e', 'user1342@example.com', 0, 'admin'),
('user1343', 'e10adc3949ba59abbe56e057f20f883e', 'user1343@example.com', 1, 'user'),
('user1344', 'e10adc3949ba59abbe56e057f20f883e', 'user1344@example.com', 0, 'user'),
('user1345', 'e10adc3949ba59abbe56e057f20f883e', 'user1345@example.com', 1, 'admin'),
('user1346', 'e10adc3949ba59abbe56e057f20f883e', 'user1346@example.com', 0, 'user'),
('user1347', 'e10adc3949ba59abbe56e057f20f883e', 'user1347@example.com', 1, 'user'),
('user1348', 'e10adc3949ba59abbe56e057f20f883e', 'user1348@example.com', 0, 'admin'),
('user1349', 'e10adc3949ba59abbe56e057f20f883e', 'user1349@example.com', 1, 'user'),
('user1350', 'e10adc3949ba59abbe56e057f20f883e', 'user1350@example.com', 0, 'user'),
('user1351', 'e10adc3949ba59abbe56e057f20f883e', 'user1351@example.com', 1, 'user'),
('user1352', 'e10adc3949ba59abbe56e057f20f883e', 'user1352@example.com', 0, 'admin'),
('user1353', 'e10adc3949ba59abbe56e057f20f883e', 'user1353@example.com', 1, 'user'),
('user1354', 'e10adc3949ba59abbe56e057f20f883e', 'user1354@example.com', 0, 'user'),
('user1355', 'e10adc3949ba59abbe56e057f20f883e', 'user1355@example.com', 1, 'admin'),
('user1356', 'e10adc3949ba59abbe56e057f20f883e', 'user1356@example.com', 0, 'user'),
('user1357', 'e10adc3949ba59abbe56e057f20f883e', 'user1357@example.com', 1, 'user'),
('user1358', 'e10adc3949ba59abbe56e057f20f883e', 'user1358@example.com', 0, 'admin'),
('user1359', 'e10adc3949ba59abbe56e057f20f883e', 'user1359@example.com', 1, 'user'),
('user1360', 'e10adc3949ba59abbe56e057f20f883e', 'user1360@example.com', 0, 'user'),
('user1361', 'e10adc3949ba59abbe56e057f20f883e', 'user1361@example.com', 1, 'user'),
('user1362', 'e10adc3949ba59abbe56e057f20f883e', 'user1362@example.com', 0, 'admin'),
('user1363', 'e10adc3949ba59abbe56e057f20f883e', 'user1363@example.com', 1, 'user'),
('user1364', 'e10adc3949ba59abbe56e057f20f883e', 'user1364@example.com', 0, 'user'),
('user1365', 'e10adc3949ba59abbe56e057f20f883e', 'user1365@example.com', 1, 'admin'),
('user1366', 'e10adc3949ba59abbe56e057f20f883e', 'user1366@example.com', 0, 'user'),
('user1367', 'e10adc3949ba59abbe56e057f20f883e', 'user1367@example.com', 1, 'user'),
('user1368', 'e10adc3949ba59abbe56e057f20f883e', 'user1368@example.com', 0, 'admin'),
('user1369', 'e10adc3949ba59abbe56e057f20f883e', 'user1369@example.com', 1, 'user'),
('user1370', 'e10adc3949ba59abbe56e057f20f883e', 'user1370@example.com', 0, 'user'),
('user1371', 'e10adc3949ba59abbe56e057f20f883e', 'user1371@example.com', 1, 'user'),
('user1372', 'e10adc3949ba59abbe56e057f20f883e', 'user1372@example.com', 0, 'admin'),
('user1373', 'e10adc3949ba59abbe56e057f20f883e', 'user1373@example.com', 1, 'user'),
('user1374', 'e10adc3949ba59abbe56e057f20f883e', 'user1374@example.com', 0, 'user'),
('user1375', 'e10adc3949ba59abbe56e057f20f883e', 'user1375@example.com', 1, 'admin'),
('user1376', 'e10adc3949ba59abbe56e057f20f883e', 'user1376@example.com', 0, 'user'),
('user1377', 'e10adc3949ba59abbe56e057f20f883e', 'user1377@example.com', 1, 'user'),
('user1378', 'e10adc3949ba59abbe56e057f20f883e', 'user1378@example.com', 0, 'admin'),
('user1379', 'e10adc3949ba59abbe56e057f20f883e', 'user1379@example.com', 1, 'user'),
('user1380', 'e10adc3949ba59abbe56e057f20f883e', 'user1380@example.com', 0, 'user'),
('user1381', 'e10adc3949ba59abbe56e057f20f883e', 'user1381@example.com', 1, 'user'),
('user1382', 'e10adc3949ba59abbe56e057f20f883e', 'user1382@example.com', 0, 'admin'),
('user1383', 'e10adc3949ba59abbe56e057f20f883e', 'user1383@example.com', 1, 'user'),
('user1384', 'e10adc3949ba59abbe56e057f20f883e', 'user1384@example.com', 0, 'user'),
('user1385', 'e10adc3949ba59abbe56e057f20f883e', 'user1385@example.com', 1, 'admin'),
('user1386', 'e10adc3949ba59abbe56e057f20f883e', 'user1386@example.com', 0, 'user'),
('user1387', 'e10adc3949ba59abbe56e057f20f883e', 'user1387@example.com', 1, 'user'),
('user1388', 'e10adc3949ba59abbe56e057f20f883e', 'user1388@example.com', 0, 'admin'),
('user1389', 'e10adc3949ba59abbe56e057f20f883e', 'user1389@example.com', 1, 'user'),
('user1390', 'e10adc3949ba59abbe56e057f20f883e', 'user1390@example.com', 0, 'user'),
('user1391', 'e10adc3949ba59abbe56e057f20f883e', 'user1391@example.com', 1, 'user'),
('user1392', 'e10adc3949ba59abbe56e057f20f883e', 'user1392@example.com', 0, 'admin'),
('user1393', 'e10adc3949ba59abbe56e057f20f883e', 'user1393@example.com', 1, 'user'),
('user1394', 'e10adc3949ba59abbe56e057f20f883e', 'user1394@example.com', 0, 'user'),
('user1395', 'e10adc3949ba59abbe56e057f20f883e', 'user1395@example.com', 1, 'admin'),
('user1396', 'e10adc3949ba59abbe56e057f20f883e', 'user1396@example.com', 0, 'user'),
('user1397', 'e10adc3949ba59abbe56e057f20f883e', 'user1397@example.com', 1, 'user'),
('user1398', 'e10adc3949ba59abbe56e057f20f883e', 'user1398@example.com', 0, 'admin'),
('user1399', 'e10adc3949ba59abbe56e057f20f883e', 'user1399@example.com', 1, 'user'),
('user1400', 'e10adc3949ba59abbe56e057f20f883e', 'user1400@example.com', 0, 'user');

-- 插入会议室数据
INSERT INTO MeetingRoom (RoomNumber, RoomName, Capacity, Equipment, Status, RoomType, Location, MeetingLink, Floor, Building, Description) VALUES
('A101', '阳光会议室', 6, '投影仪,白板', 'Available', 'Offline', 'A区1楼101室', NULL, '1楼', 'A座', '小型会议室,适合团队讨论'),
('A102', '星空会议室', 8, '投影仪,电视', 'Available', 'Offline', 'A区1楼102室', NULL, '1楼', 'A座', '小型会议室,配备高清电视'),
('A201', '海景会议室', 12, '投影仪,音响系统,白板', 'Available', 'Offline', 'A区2楼201室', NULL, '2楼', 'A座', '中型会议室,设备齐全'),
('A202', '山景会议室', 10, '投影仪,电视', 'Available', 'Offline', 'A区2楼202室', NULL, '2楼', 'A座', '中型会议室,适合部门会议'),
('B301', '豪华会议厅', 50, '投影仪,音响系统,舞台灯光', 'Available', 'Offline', 'B区3楼301室', NULL, '3楼', 'B座', '大型会议厅,适合重要会议'),
('B302', '多功能厅', 30, '投影仪,音响系统,视频会议系统', 'Available', 'Offline', 'B区3楼302室', NULL, '3楼', 'B座', '多功能厅,支持线上线下结合'),
('C101', '创新讨论室', 4, '白板,投影仪', 'Available', 'Offline', 'C区1楼101室', NULL, '1楼', 'C座', '小型创新讨论室'),
('C102', '头脑风暴室', 6, '白板,便利贴墙', 'Available', 'Offline', 'C区1楼102室', NULL, '1楼', 'C座', '专为创意讨论设计'),
('ONLINE01', '线上会议室1', 100, '视频会议系统', 'Available', 'Online', NULL, 'https://meeting.example.com/room1', NULL, '云端', '支持大型线上会议'),
('ONLINE02', '线上会议室2', 50, '视频会议系统,屏幕共享', 'Available', 'Online', NULL, 'https://meeting.example.com/room2', NULL, '云端', '支持屏幕共享的线上会议室');

-- 插入设备数据
INSERT INTO Equipment (RoomID, EquipmentName, Quantity) VALUES
(1, '投影仪', 1), (1, '音响系统', 1), (1, '电子白板', 1),
(2, '投影仪', 1), (2, '音响系统', 1), (2, '视频会议系统', 1),
(3, '电子白板', 1), (3, '音响系统', 1),
(4, '电子白板', 1),
(5, '投影仪', 1), (5, '视频会议系统', 1),
(6, '视频会议系统', 1),
(9, '视频会议系统', 1),
(10, '视频会议系统', 1), (10, '屏幕共享系统', 1);

-- 插入预订数据
INSERT INTO Booking (RoomID, UserID, StartTime, EndTime, Status, Title, Purpose, Attendees) VALUES
(1, 4, '2025-06-11 14:00:00', '2025-06-11 16:00:00', 'Confirmed', '定期团队会议', '讨论当前项目进展和问题', 6),
(2, 5, '2025-06-12 09:00:00', '2025-06-12 12:00:00', 'Confirmed', '客户演示会议', '与重要客户展示新产品功能', 8),
(3, 6, '2025-06-11 10:00:00', '2025-06-11 11:30:00', 'Confirmed', '项目启动会', '新项目启动会议', 6),
(1, 5, '2025-06-13 14:00:00', '2025-06-13 17:00:00', 'Pending', '年中规划会议', '讨论下半年的工作安排', 6),
(4, 6, '2025-06-14 13:00:00', '2025-06-14 15:00:00', 'Confirmed', '部门内部会议', '讨论部门绩效评估', 4);

-- 插入维护记录数据
INSERT INTO Maintenance (RoomID, MaintenanceDate, StartTime, EndTime, Description, Status) VALUES
(1, '2025-06-10', '2025-06-11 09:00:00', '2025-06-11 12:00:00', '定期检查和维护', 'Scheduled'),
(2, '2025-06-15', '2025-06-16 14:00:00', '2025-06-16 17:00:00', '更换投影仪灯泡', 'Scheduled'),
(3, '2025-06-10', '2025-06-11 10:00:00', '2025-06-11 15:00:00', '更新视频会议系统软件', 'Scheduled');

-- 插入少量日志和通知数据
INSERT INTO Log (UserID, Action, Timestamp, Description, IPAddress) VALUES
(1, '登录', '2025-06-01 08:30:00', '管理员登录成功', '192.168.1.100'),
(1, '新增会议室', '2025-06-01 08:45:00', '添加会议室', '192.168.1.100');

INSERT INTO Notification (UserID, Status, Timestamp, Message) VALUES
(4, 'Unread', '2025-06-01 09:12:00', '您的会议室预订已确认'),
(5, 'Unread', '2025-06-01 09:22:00', '您的会议室预订已确认');

INSERT INTO MeetingMaterials (BookingID, UserID, Title, FilePath, FileName, FileSize, FileType, UploadTime, Status, Description) VALUES
(1, 4, '2025年Q2项目计划', '/files/meeting_materials/q2_project_plan.pdf', 'q2_project_plan.pdf', 1024000, 'application/pdf', '2025-06-01 13:30:00', 'Active', '2025年第二季度项目计划详情');

SELECT '✅ 基础数据插入完成' as 状态;

-- ====================================
-- 第四步:创建兼容性视图
-- ====================================
SELECT '正在创建兼容性视图...' as 进度;

DROP VIEW IF EXISTS MaintenanceView;
DROP VIEW IF EXISTS Users;

CREATE VIEW MaintenanceView AS 
SELECT 
    ID as MaintenanceID,
    ID,
    RoomID,
    MaintenanceDate,
    StartTime,
    EndTime,
    Description,
    Status,
    CreatedAt,
    UpdatedAt
FROM Maintenance;

CREATE VIEW Users AS 
SELECT 
    UserID,
    UserName as Username,
    Password,
    Email,
    EmailVerified,
    VerificationToken,
    Role,
    Avatar
FROM User;

SELECT '✅ 兼容性视图创建完成' as 状态;

-- ====================================
-- 第五步:验证安装
-- ====================================
SELECT '正在验证安装...' as 进度;

SELECT 
    '用户数据' as 表名, COUNT(*) as 记录数 FROM User
UNION ALL
SELECT '会议室数据' as 表名, COUNT(*) as 记录数 FROM MeetingRoom
UNION ALL
SELECT '设备数据' as 表名, COUNT(*) as 记录数 FROM Equipment
UNION ALL
SELECT '预订数据' as 表名, COUNT(*) as 记录数 FROM Booking
UNION ALL
SELECT '维护记录' as 表名, COUNT(*) as 记录数 FROM Maintenance
UNION ALL
SELECT '兼容性视图' as 表名, 2 as 记录数;

-- 测试兼容性查询
SELECT '测试兼容性查询' as 测试;
SELECT COUNT(*) as MaintenanceView记录数 FROM MaintenanceView;
SELECT COUNT(*) as Users视图记录数 FROM Users;

-- ====================================
-- 安装完成
-- ====================================
SELECT '🎉 会议室管理系统数据库安装完成！' as 状态;
SELECT '系统已就绪,可以启动应用程序' as 说明;
SELECT 'admin/123456' as 默认管理员账号;
SELECT 'liansifan/123456' as 默认管理员账号2;
