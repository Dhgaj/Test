-- ==============================================================================
-- 会议室管理系统 - 紧急修复脚本
-- 文件: hotfix_duplicate_columns.sql
-- 作用: 修复 Users 视图中的重复列问题
-- 创建时间: 2025年6月9日
-- 问题描述: Users 视图中同时包含 UserName as Username 和 UserName，导致列名冲突
-- ==============================================================================

USE test_meeting_rooms;

-- 显示修复信息
SELECT '🔧 正在修复 Users 视图中的重复列问题...' as 状态;

-- 删除有问题的视图
DROP VIEW IF EXISTS Users;

-- 重新创建正确的视图
CREATE VIEW Users AS 
SELECT 
    UserID,
    UserName as Username,         -- 提供兼容性别名
    Password,
    Email,
    EmailVerified,
    VerificationToken,
    Role,
    Avatar
FROM User;

-- 验证修复结果
SELECT '✅ Users 视图修复完成' as 状态;

-- 测试视图功能
SELECT 
    '视图测试结果' as 测试类型,
    COUNT(*) as 用户数量,
    '✅ 正常' as 状态
FROM Users;

-- 测试 Username 别名
SELECT 
    '别名测试结果' as 测试类型,
    Username as 用户名,
    UserID as 用户ID,
    '✅ 正常' as 状态
FROM Users 
LIMIT 1;

-- 显示视图结构
SELECT '📋 修复后的视图结构:' as 信息;
DESCRIBE Users;

SELECT '🎉 热修复完成！Users 视图现在可以正常使用了。' as 最终状态;
