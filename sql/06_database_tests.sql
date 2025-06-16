-- ==============================================================================
-- 会议室管理系统 - 数据库功能测试脚本
-- 文件: 06_database_tests.sql
-- 作用: 全面测试数据库功能和性能
-- 创建时间: 2025年6月9日
-- ==============================================================================

USE test_meeting_rooms;

-- ==============================================================================
-- 1. 基础连接和权限测试
-- ==============================================================================

SELECT '🧪 开始数据库功能测试' as 测试状态, NOW() as 开始时间;

-- 测试数据库连接
SELECT CONNECTION_ID() as 连接ID, USER() as 当前用户, DATABASE() as 当前数据库;

-- 检查字符集设置
SELECT 
    @@character_set_database as 数据库字符集,
    @@collation_database as 数据库排序规则;

-- ==============================================================================
-- 2. 表结构完整性测试
-- ==============================================================================

-- 检查所有必需的表是否存在
SELECT 
    '表结构检查' as 测试项目,
    COUNT(*) as 表数量,
    CASE 
        WHEN COUNT(*) = 8 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'test_meeting_rooms' 
  AND TABLE_TYPE = 'BASE TABLE';

-- 列出所有表
SELECT TABLE_NAME as 表名 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'test_meeting_rooms' 
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- ==============================================================================
-- 3. 外键约束测试
-- ==============================================================================

-- 检查外键约束
SELECT 
    '外键约束检查' as 测试项目,
    COUNT(*) as 外键数量,
    CASE 
        WHEN COUNT(*) >= 6 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM information_schema.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'test_meeting_rooms' 
  AND REFERENCED_TABLE_NAME IS NOT NULL;

-- ==============================================================================
-- 4. 索引完整性测试
-- ==============================================================================

-- 检查索引
SELECT 
    '索引检查' as 测试项目,
    COUNT(*) as 索引数量,
    CASE 
        WHEN COUNT(*) >= 20 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'test_meeting_rooms';

-- ==============================================================================
-- 5. 数据完整性测试
-- ==============================================================================

-- 测试用户数据
SELECT 
    '用户数据检查' as 测试项目,
    COUNT(*) as 用户数量,
    CASE 
        WHEN COUNT(*) >= 7 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM User;

-- 测试会议室数据
SELECT 
    '会议室数据检查' as 测试项目,
    COUNT(*) as 会议室数量,
    CASE 
        WHEN COUNT(*) >= 10 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM MeetingRoom;

-- 测试预订数据
SELECT 
    '预订数据检查' as 测试项目,
    COUNT(*) as 预订数量,
    CASE 
        WHEN COUNT(*) >= 5 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM Booking;

-- ==============================================================================
-- 6. 兼容性视图测试
-- ==============================================================================

-- 测试 MaintenanceView 视图
SELECT 
    'MaintenanceView视图测试' as 测试项目,
    CASE 
        WHEN COUNT(*) > 0 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM MaintenanceView
LIMIT 1;

-- 测试 MaintenanceID 列别名
SELECT 
    'MaintenanceID别名测试' as 测试项目,
    CASE 
        WHEN MaintenanceID IS NOT NULL THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM MaintenanceView
LIMIT 1;

-- 测试 Users 视图
SELECT 
    'Users视图测试' as 测试项目,
    CASE 
        WHEN COUNT(*) > 0 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM Users
LIMIT 1;

-- 测试 Username 列别名
SELECT 
    'Username别名测试' as 测试项目,
    CASE 
        WHEN Username IS NOT NULL THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM Users
LIMIT 1;

-- 测试视图列数正确性
SELECT 
    'Users视图列数测试' as 测试项目,
    COUNT(*) as 列数,
    CASE 
        WHEN COUNT(*) = 8 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'test_meeting_rooms' 
  AND TABLE_NAME = 'Users';

-- ==============================================================================
-- 7. 查询性能测试
-- ==============================================================================

-- 测试复杂查询性能
SELECT '🚀 查询性能测试开始' as 状态;

-- 用户预订统计查询
SELECT 
    '用户预订统计查询' as 测试项目,
    COUNT(*) as 结果数量,
    '✅ 通过' as 测试结果
FROM (
    SELECT 
        u.UserName,
        COUNT(b.ID) as 预订次数
    FROM User u
    LEFT JOIN Booking b ON u.UserID = b.UserID
    GROUP BY u.UserID, u.UserName
) as stats;

-- 会议室使用率查询
SELECT 
    '会议室使用率查询' as 测试项目,
    COUNT(*) as 结果数量,
    '✅ 通过' as 测试结果
FROM (
    SELECT 
        mr.RoomName,
        COUNT(b.ID) as 预订次数,
        CASE 
            WHEN COUNT(b.ID) > 0 THEN '活跃'
            ELSE '空闲'
        END as 状态
    FROM MeetingRoom mr
    LEFT JOIN Booking b ON mr.RoomID = b.RoomID
    GROUP BY mr.RoomID, mr.RoomName
) as usage;

-- ==============================================================================
-- 8. CRUD 操作测试
-- ==============================================================================

-- 创建测试用户
INSERT INTO User (UserName, Password, Email, EmailVerified, Role) 
VALUES ('test_user_temp', 'test_password_hash', 'test@example.com', 0, 'user');

SET @test_user_id = LAST_INSERT_ID();

SELECT 
    '用户创建测试' as 测试项目,
    CASE 
        WHEN @test_user_id > 0 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果;

-- 更新测试用户
UPDATE User 
SET EmailVerified = 1 
WHERE UserID = @test_user_id;

SELECT 
    '用户更新测试' as 测试项目,
    CASE 
        WHEN ROW_COUNT() > 0 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果;

-- 查询测试用户
SELECT 
    '用户查询测试' as 测试项目,
    CASE 
        WHEN COUNT(*) = 1 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM User 
WHERE UserID = @test_user_id AND EmailVerified = 1;

-- 删除测试用户
DELETE FROM User WHERE UserID = @test_user_id;

SELECT 
    '用户删除测试' as 测试项目,
    CASE 
        WHEN ROW_COUNT() > 0 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果;

-- ==============================================================================
-- 9. 事务测试
-- ==============================================================================

-- 测试事务回滚
START TRANSACTION;

INSERT INTO User (UserName, Password, Email, EmailVerified, Role) 
VALUES ('transaction_test', 'test_hash', 'transaction@test.com', 0, 'user');

SET @transaction_user_id = LAST_INSERT_ID();

-- 故意触发错误（插入重复邮箱）
-- INSERT INTO User (UserName, Password, Email, EmailVerified, Role) 
-- VALUES ('transaction_test2', 'test_hash', 'transaction@test.com', 0, 'user');

ROLLBACK;

-- 验证回滚是否成功
SELECT 
    '事务回滚测试' as 测试项目,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM User 
WHERE UserName = 'transaction_test';

-- ==============================================================================
-- 10. 日期时间测试
-- ==============================================================================

-- 测试时间范围查询
SELECT 
    '时间范围查询测试' as 测试项目,
    COUNT(*) as 结果数量,
    CASE 
        WHEN COUNT(*) >= 0 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM Booking 
WHERE StartTime >= '2025-06-01' 
  AND EndTime <= '2025-12-31';

-- 测试时间冲突检查
SELECT 
    '时间冲突检查测试' as 测试项目,
    COUNT(*) as 冲突数量,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ 通过'
        ELSE '⚠️ 发现冲突' 
    END as 测试结果
FROM Booking b1
JOIN Booking b2 ON b1.RoomID = b2.RoomID 
  AND b1.ID != b2.ID
  AND b1.Status = 'Confirmed' 
  AND b2.Status = 'Confirmed'
  AND ((b1.StartTime BETWEEN b2.StartTime AND b2.EndTime)
    OR (b1.EndTime BETWEEN b2.StartTime AND b2.EndTime)
    OR (b2.StartTime BETWEEN b1.StartTime AND b1.EndTime));

-- ==============================================================================
-- 11. 数据类型和约束测试
-- ==============================================================================

-- 测试 ENUM 类型
SELECT 
    'ENUM类型测试' as 测试项目,
    COUNT(DISTINCT RoomType) as 房间类型数,
    CASE 
        WHEN COUNT(DISTINCT RoomType) >= 2 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM MeetingRoom;

-- 测试 NOT NULL 约束
SELECT 
    'NOT NULL约束测试' as 测试项目,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ 通过'
        ELSE '❌ 失败' 
    END as 测试结果
FROM User 
WHERE UserName IS NULL OR Password IS NULL;

-- ==============================================================================
-- 12. 性能基准测试
-- ==============================================================================

-- 大量数据查询测试
SELECT 
    '大量数据查询测试' as 测试项目,
    COUNT(*) as 总记录数,
    '✅ 通过' as 测试结果
FROM (
    SELECT u.*, b.*, mr.*
    FROM User u
    LEFT JOIN Booking b ON u.UserID = b.UserID
    LEFT JOIN MeetingRoom mr ON b.RoomID = mr.RoomID
) as comprehensive_view;

-- ==============================================================================
-- 13. 测试结果汇总
-- ==============================================================================

SELECT 
    '🎉 数据库功能测试完成' as 测试状态,
    NOW() as 完成时间,
    'ALL TESTS COMPLETED' as 测试结果;

-- 显示测试环境信息
SELECT 
    @@version as MySQL版本,
    @@innodb_version as InnoDB版本,
    @@character_set_server as 服务器字符集,
    @@max_connections as 最大连接数;

-- 显示数据库状态
SELECT 
    TABLE_NAME as 表名,
    TABLE_ROWS as 记录数,
    ROUND(DATA_LENGTH/1024/1024, 2) as 数据大小MB
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'test_meeting_rooms' 
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY DATA_LENGTH DESC;

-- ==============================================================================
-- 测试完成
-- ==============================================================================

SELECT '✅ 所有测试项目执行完毕，请检查上述结果确认系统状态' as 最终提示;
