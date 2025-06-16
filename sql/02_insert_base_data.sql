-- ====================================
-- 会议室管理系统 - 基础数据插入脚本
-- 创建时间: 2025年6月9日
-- 描述: 插入系统初始化数据
-- ====================================

USE test_meeting_rooms;

-- ====================================
-- 1. 插入用户数据
-- ====================================
INSERT INTO User (UserName, Password, Email, EmailVerified, Role) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', 'sifanlian@gmail.com', 1, 'admin'),  -- 密码：123456
('liansifan', 'e10adc3949ba59abbe56e057f20f883e', 'liamsifam@gmail.com', 1, 'admin'),  -- 密码：123456
('manager1', 'e10adc3949ba59abbe56e057f20f883e', 'manager1@example.com', 1, 'user'),  -- 密码：123456
('manager2', 'e10adc3949ba59abbe56e057f20f883e', 'manager2@example.com', 1, 'user'),  -- 密码：123456
('user1', 'e10adc3949ba59abbe56e057f20f883e', 'user1@example.com', 1, 'user'),  -- 密码：123456
('user2', 'e10adc3949ba59abbe56e057f20f883e', 'user2@example.com', 1, 'user'),  -- 密码：123456
('user3', 'e10adc3949ba59abbe56e057f20f883e', 'user3@example.com', 1, 'user');  -- 密码：123456

-- ====================================
-- 2. 插入会议室数据
-- ====================================
INSERT INTO MeetingRoom (RoomNumber, RoomName, Capacity, Equipment, Status, RoomType, Location, MeetingLink, Floor, Building, Description) VALUES
-- 线下会议室
('A101', '阳光会议室', 6, '投影仪,白板', 'Available', 'Offline', 'A区1楼101室', NULL, '1楼', 'A座', '小型会议室，适合团队讨论'),
('A102', '星空会议室', 8, '投影仪,电视', 'Available', 'Offline', 'A区1楼102室', NULL, '1楼', 'A座', '小型会议室，配备高清电视'),
('A201', '海景会议室', 12, '投影仪,音响系统,白板', 'Available', 'Offline', 'A区2楼201室', NULL, '2楼', 'A座', '中型会议室，设备齐全'),
('A202', '山景会议室', 10, '投影仪,电视', 'Available', 'Offline', 'A区2楼202室', NULL, '2楼', 'A座', '中型会议室，适合部门会议'),
('B301', '豪华会议厅', 50, '投影仪,音响系统,舞台灯光', 'Available', 'Offline', 'B区3楼301室', NULL, '3楼', 'B座', '大型会议厅，适合重要会议'),
('B302', '多功能厅', 30, '投影仪,音响系统,视频会议系统', 'Available', 'Offline', 'B区3楼302室', NULL, '3楼', 'B座', '多功能厅，支持线上线下结合'),
('C101', '创新讨论室', 4, '白板,投影仪', 'Available', 'Offline', 'C区1楼101室', NULL, '1楼', 'C座', '小型创新讨论室'),
('C102', '头脑风暴室', 6, '白板,便利贴墙', 'Available', 'Offline', 'C区1楼102室', NULL, '1楼', 'C座', '专为创意讨论设计'),
-- 线上会议室
('ONLINE01', '线上会议室1', 100, '视频会议系统', 'Available', 'Online', NULL, 'https://meeting.example.com/room1', NULL, '云端', '支持大型线上会议'),
('ONLINE02', '线上会议室2', 50, '视频会议系统,屏幕共享', 'Available', 'Online', NULL, 'https://meeting.example.com/room2', NULL, '云端', '支持屏幕共享的线上会议室');

-- ====================================
-- 3. 插入设备数据
-- ====================================
INSERT INTO Equipment (RoomID, EquipmentName, Quantity) VALUES
-- A101 阳光会议室设备
(1, '投影仪', 1),
(1, '音响系统', 1),
(1, '电子白板', 1),
-- A102 星空会议室设备
(2, '投影仪', 1),
(2, '音响系统', 1),
(2, '视频会议系统', 1),
-- A201 海景会议室设备
(3, '电子白板', 1),
(3, '音响系统', 1),
-- A202 山景会议室设备
(4, '电子白板', 1),
-- B301 豪华会议厅设备
(5, '投影仪', 1),
(5, '视频会议系统', 1),
-- B302 多功能厅设备
(6, '视频会议系统', 1),
-- 线上会议室设备
(9, '视频会议系统', 1),
(10, '视频会议系统', 1),
(10, '屏幕共享系统', 1);

-- ====================================
-- 4. 插入预订数据（修正时间逻辑错误）
-- ====================================
INSERT INTO Booking (RoomID, UserID, StartTime, EndTime, Status, Title, Purpose, Attendees) VALUES
-- 修正：原来的结束时间早于开始时间的错误
(1, 4, '2025-06-11 14:00:00', '2025-06-11 16:00:00', 'Confirmed', '定期团队会议', '讨论当前项目进展和问题', 6),
(2, 5, '2025-06-12 09:00:00', '2025-06-12 12:00:00', 'Confirmed', '客户演示会议', '与重要客户展示新产品功能', 8),
(3, 6, '2025-06-11 10:00:00', '2025-06-11 11:30:00', 'Confirmed', '项目启动会', '新项目启动会议', 6),
(1, 5, '2025-06-13 14:00:00', '2025-06-13 17:00:00', 'Pending', '年中规划会议', '讨论下半年的工作安排', 6),
(4, 6, '2025-06-14 13:00:00', '2025-06-14 15:00:00', 'Confirmed', '部门内部会议', '讨论部门绩效评估', 4);

-- ====================================
-- 5. 插入维护记录数据
-- ====================================
INSERT INTO Maintenance (RoomID, MaintenanceDate, StartTime, EndTime, Description, Status) VALUES
(1, '2025-06-10', '2025-06-11 09:00:00', '2025-06-11 12:00:00', '定期检查和维护', 'Scheduled'),
(2, '2025-06-15', '2025-06-16 14:00:00', '2025-06-16 17:00:00', '更换投影仪灯泡', 'Scheduled'),
(3, '2025-06-10', '2025-06-11 10:00:00', '2025-06-11 15:00:00', '更新视频会议系统软件', 'Scheduled');

-- ====================================
-- 6. 插入日志数据
-- ====================================
INSERT INTO Log (UserID, Action, Timestamp, Description, IPAddress) VALUES
(1, '登录', '2025-06-01 08:30:00', '管理员登录成功', '192.168.1.100'),
(1, '新增会议室', '2025-06-01 08:45:00', '添加会议室', '192.168.1.100'),
(4, '登录', '2025-06-01 09:00:00', '用户登录成功', '192.168.1.101'),
(4, '预订', '2025-06-01 09:10:00', '预订阳光会议室', '192.168.1.101'),
(5, '登录', '2025-06-01 09:15:00', '用户登录成功', '192.168.1.102'),
(5, '预订', '2025-06-01 09:20:00', '预订星空会议室', '192.168.1.102');

-- ====================================
-- 7. 插入通知数据
-- ====================================
INSERT INTO Notification (UserID, Status, Timestamp, Message) VALUES
(4, 'Unread', '2025-06-01 09:12:00', '您的会议室预订已确认'),
(5, 'Unread', '2025-06-01 09:22:00', '您的会议室预订已确认'),
(6, 'Unread', '2025-06-01 09:25:00', '您的会议室预订已确认'),
(5, 'Unread', '2025-06-01 09:30:00', '您的会议室预订正在审核中'),
(1, 'Read', '2025-06-01 08:50:00', '系统维护通知：部分会议室正在进行维护');

-- ====================================
-- 8. 插入会议资料数据
-- ====================================
INSERT INTO MeetingMaterials (BookingID, UserID, Title, FilePath, FileName, FileSize, FileType, UploadTime, Status, Description) VALUES
(1, 4, '2025年Q2项目计划', '/files/meeting_materials/q2_project_plan.pdf', 'q2_project_plan.pdf', 1024000, 'application/pdf', '2025-06-01 13:30:00', 'Active', '2025年第二季度项目计划详情'),
(2, 5, '产品设计说明', '/files/meeting_materials/product_design.docx', 'product_design.docx', 512000, 'application/msword', '2025-06-01 08:50:00', 'Active', '新产品设计说明文档'),
(3, 6, '周会议记录', '/files/meeting_materials/weekly_meeting_notes.pdf', 'weekly_meeting_notes.pdf', 256000, 'application/pdf', '2025-06-01 09:45:00', 'Active', '本周团队会议记录和决策事项');

-- ====================================
-- 数据验证
-- ====================================
SELECT '用户数据' as 表名, COUNT(*) as 记录数 FROM User
UNION ALL
SELECT '会议室数据' as 表名, COUNT(*) as 记录数 FROM MeetingRoom
UNION ALL
SELECT '设备数据' as 表名, COUNT(*) as 记录数 FROM Equipment
UNION ALL
SELECT '预订数据' as 表名, COUNT(*) as 记录数 FROM Booking
UNION ALL
SELECT '维护记录' as 表名, COUNT(*) as 记录数 FROM Maintenance
UNION ALL
SELECT '日志数据' as 表名, COUNT(*) as 记录数 FROM Log
UNION ALL
SELECT '通知数据' as 表名, COUNT(*) as 记录数 FROM Notification
UNION ALL
SELECT '会议资料' as 表名, COUNT(*) as 记录数 FROM MeetingMaterials;

-- ====================================
-- 基础数据插入完成
-- ====================================
SELECT '✅ 基础数据插入完成' as 状态, 
       '所有表已填入初始数据' as 说明;
