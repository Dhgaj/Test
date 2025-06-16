-- ====================================
-- 会议室管理系统 - 兼容性视图创建脚本
-- 创建时间: 2025年6月9日
-- 描述: 解决历史查询兼容性问题
-- ====================================

USE test_meeting_rooms;

-- ====================================
-- 问题描述
-- ====================================
-- 1. 某些查询使用 MaintenanceID 列名，但 Maintenance 表的主键是 ID
-- 2. 某些查询使用 Users 表名，但实际表名是 User
-- 3. 某些查询使用 Username 列名，但实际列名是 UserName

-- ====================================
-- 解决方案：创建兼容性视图
-- ====================================

-- 删除已存在的视图（如果有）
DROP VIEW IF EXISTS MaintenanceView;
DROP VIEW IF EXISTS Users;

-- ====================================
-- 1. MaintenanceView 视图
-- 解决 MaintenanceID 列名问题
-- ====================================
CREATE VIEW MaintenanceView AS 
SELECT 
    ID as MaintenanceID,          -- 将 ID 别名为 MaintenanceID
    ID,                           -- 保留原始 ID 列
    RoomID,
    MaintenanceDate,
    StartTime,
    EndTime,
    Description,
    Status,
    CreatedAt,
    UpdatedAt
FROM Maintenance;

-- ====================================
-- 2. Users 视图
-- 解决 Users 表名和 Username 列名问题
-- ====================================
CREATE VIEW Users AS 
SELECT 
    UserID,
    UserName as Username,         -- 将 UserName 别名为 Username（兼容性别名）
    Password,
    Email,
    EmailVerified,
    VerificationToken,
    Role,
    Avatar
FROM User;

-- 注意：这里只提供 Username 别名，不重复选择 UserName 列
-- 如果需要原始 UserName，可以直接查询 User 表

-- ====================================
-- 视图验证
-- ====================================

-- 验证 MaintenanceView 视图
SELECT 'MaintenanceView 视图验证' as 测试项目;
SELECT 
    MaintenanceID, 
    RoomID, 
    Description, 
    Status,
    MaintenanceDate
FROM MaintenanceView 
ORDER BY MaintenanceID 
LIMIT 3;

-- 验证 Users 视图
SELECT 'Users 视图验证' as 测试项目;
SELECT 
    UserID, 
    Username, 
    UserName,
    Email, 
    Role 
FROM Users 
LIMIT 5;

-- ====================================
-- 兼容性测试
-- ====================================

-- 测试之前会失败的查询1：MaintenanceID 查询
SELECT '测试原错误查询1' as 测试说明;
SELECT MaintenanceID, Description, RoomID, MaintenanceDate, StartTime, EndTime, Status 
FROM MaintenanceView 
ORDER BY MaintenanceID;

-- 测试之前会失败的查询2：Users 表查询
SELECT '测试原错误查询2' as 测试说明;
SELECT UserID, Username, Email 
FROM Users 
LIMIT 5;

-- ====================================
-- 统计信息
-- ====================================
SELECT 
    'MaintenanceView' as 视图名称,
    COUNT(*) as 记录数,
    'MaintenanceID 列可用' as 功能
FROM MaintenanceView

UNION ALL

SELECT 
    'Users' as 视图名称,
    COUNT(*) as 记录数,
    'Username 列可用' as 功能
FROM Users;

-- ====================================
-- 使用建议
-- ====================================
SELECT '✅ 兼容性视图创建完成' as 状态;
SELECT '建议' as 类型, '这些视图仅作为临时兼容性解决方案' as 说明
UNION ALL
SELECT '建议' as 类型, '长期应更新代码使用正确的表名和列名' as 说明
UNION ALL
SELECT '建议' as 类型, '完全修复后可删除这些兼容性视图' as 说明;
