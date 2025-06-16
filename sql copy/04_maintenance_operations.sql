-- ==============================================================================
-- 会议室管理系统 - 数据库维护脚本
-- 文件: 04_maintenance_operations.sql
-- 作用: 数据库日常维护、性能优化和数据清理
-- 创建时间: 2025年6月9日
-- ==============================================================================

USE test_meeting_rooms;

-- ==============================================================================
-- 1. 数据库健康检查
-- ==============================================================================

-- 检查表状态
SELECT 
    TABLE_NAME as '表名',
    TABLE_ROWS as '记录数',
    ROUND(DATA_LENGTH/1024/1024, 2) as '数据大小(MB)',
    ROUND(INDEX_LENGTH/1024/1024, 2) as '索引大小(MB)',
    TABLE_COLLATION as '字符集'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'test_meeting_rooms'
ORDER BY DATA_LENGTH DESC;

-- 检查索引使用情况
SELECT 
    TABLE_NAME as '表名',
    INDEX_NAME as '索引名',
    COLUMN_NAME as '列名',
    CARDINALITY as '基数'
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'test_meeting_rooms'
ORDER BY TABLE_NAME, INDEX_NAME;

-- ==============================================================================
-- 2. 数据清理操作
-- ==============================================================================

-- 清理过期的日志记录（保留最近6个月的日志）
-- 注意：正式环境使用前请根据实际需求调整时间范围
/*
DELETE FROM Log 
WHERE Timestamp < DATE_SUB(NOW(), INTERVAL 6 MONTH);
*/

-- 清理已读的旧通知（保留最近3个月的通知）
-- 注意：正式环境使用前请根据实际需求调整时间范围
/*
DELETE FROM Notification 
WHERE Status = 'Read' 
AND Timestamp < DATE_SUB(NOW(), INTERVAL 3 MONTH);
*/

-- 清理已完成的历史维护记录（保留最近1年的记录）
-- 注意：正式环境使用前请根据实际需求调整时间范围
/*
DELETE FROM Maintenance 
WHERE Status = 'Completed' 
AND CreatedAt < DATE_SUB(NOW(), INTERVAL 1 YEAR);
*/

-- ==============================================================================
-- 3. 性能优化操作
-- ==============================================================================

-- 优化表结构（重建索引）
-- 注意：这些操作可能耗时较长，建议在维护窗口期执行

-- 优化用户表
-- OPTIMIZE TABLE User;

-- 优化会议室表
-- OPTIMIZE TABLE MeetingRoom;

-- 优化预订表（通常是最大的表）
-- OPTIMIZE TABLE Booking;

-- 优化日志表
-- OPTIMIZE TABLE Log;

-- 优化通知表
-- OPTIMIZE TABLE Notification;

-- 优化维护表
-- OPTIMIZE TABLE Maintenance;

-- 优化会议资料表
-- OPTIMIZE TABLE MeetingMaterials;

-- 优化设备表
-- OPTIMIZE TABLE Equipment;

-- ==============================================================================
-- 4. 数据完整性检查
-- ==============================================================================

-- 检查孤立的预订记录（引用不存在的用户或会议室）
SELECT 
    'Booking表中的孤立记录' as 检查项目,
    COUNT(*) as 问题数量
FROM Booking b
LEFT JOIN User u ON b.UserID = u.UserID
LEFT JOIN MeetingRoom mr ON b.RoomID = mr.RoomID
WHERE u.UserID IS NULL OR mr.RoomID IS NULL;

-- 检查孤立的设备记录
SELECT 
    'Equipment表中的孤立记录' as 检查项目,
    COUNT(*) as 问题数量
FROM Equipment e
LEFT JOIN MeetingRoom mr ON e.RoomID = mr.RoomID
WHERE mr.RoomID IS NULL;

-- 检查孤立的维护记录
SELECT 
    'Maintenance表中的孤立记录' as 检查项目,
    COUNT(*) as 问题数量
FROM Maintenance m
LEFT JOIN MeetingRoom mr ON m.RoomID = mr.RoomID
WHERE mr.RoomID IS NULL;

-- 检查孤立的会议资料记录
SELECT 
    'MeetingMaterials表中的孤立记录' as 检查项目,
    COUNT(*) as 问题数量
FROM MeetingMaterials mm
LEFT JOIN Booking b ON mm.BookingID = b.ID
LEFT JOIN User u ON mm.UserID = u.UserID
WHERE b.ID IS NULL OR u.UserID IS NULL;

-- ==============================================================================
-- 5. 统计信息更新
-- ==============================================================================

-- 更新表统计信息（提高查询优化器性能）
ANALYZE TABLE User;
ANALYZE TABLE MeetingRoom;
ANALYZE TABLE Booking;
ANALYZE TABLE Equipment;
ANALYZE TABLE Log;
ANALYZE TABLE Notification;
ANALYZE TABLE Maintenance;
ANALYZE TABLE MeetingMaterials;

-- ==============================================================================
-- 6. 备份建议命令（注释形式提供）
-- ==============================================================================

/*
-- 完整数据库备份
mysqldump -u root -p --single-transaction --routines --triggers test_meeting_rooms > backup_$(date +%Y%m%d_%H%M%S).sql

-- 仅结构备份（不包含数据）
mysqldump -u root -p --no-data test_meeting_rooms > schema_backup_$(date +%Y%m%d_%H%M%S).sql

-- 仅数据备份（不包含结构）
mysqldump -u root -p --no-create-info test_meeting_rooms > data_backup_$(date +%Y%m%d_%H%M%S).sql
*/

-- ==============================================================================
-- 7. 监控查询
-- ==============================================================================

-- 活跃会议室使用情况
SELECT 
    mr.RoomName as '会议室名称',
    COUNT(b.ID) as '本月预订次数',
    ROUND(AVG(TIMESTAMPDIFF(HOUR, b.StartTime, b.EndTime)), 2) as '平均使用时长(小时)'
FROM MeetingRoom mr
LEFT JOIN Booking b ON mr.RoomID = b.RoomID 
    AND b.StartTime >= DATE_FORMAT(NOW(), '%Y-%m-01')
    AND b.Status = 'Confirmed'
GROUP BY mr.RoomID, mr.RoomName
ORDER BY COUNT(b.ID) DESC;

-- 用户活跃度统计
SELECT 
    u.UserName as '用户名',
    COUNT(b.ID) as '本月预订次数',
    u.Role as '角色'
FROM User u
LEFT JOIN Booking b ON u.UserID = b.UserID 
    AND b.StartTime >= DATE_FORMAT(NOW(), '%Y-%m-01')
GROUP BY u.UserID, u.UserName, u.Role
HAVING COUNT(b.ID) > 0
ORDER BY COUNT(b.ID) DESC;

-- 系统错误日志统计
SELECT 
    DATE(Timestamp) as '日期',
    COUNT(*) as '日志条数'
FROM Log 
WHERE Timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(Timestamp)
ORDER BY DATE(Timestamp) DESC;

-- ==============================================================================
-- 维护完成
-- ==============================================================================
SELECT 
    '🔧 数据库维护检查完成' as 状态,
    NOW() as 维护时间,
    '请根据检查结果执行相应的优化操作' as 建议;
