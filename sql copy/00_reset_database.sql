-- ====================================
-- 会议室管理系统 - 数据库重置脚本
-- 创建时间: 2025年6月9日
-- 描述: 完全重置数据库（谨慎使用）
-- ====================================

-- 警告：此脚本将删除所有数据！
-- 请确认您要执行完全重置操作

-- ====================================
-- 1. 删除所有视图
-- ====================================
USE test_meeting_rooms;

DROP VIEW IF EXISTS MaintenanceView;
DROP VIEW IF EXISTS Users;

-- ====================================
-- 2. 删除所有表（按依赖关系顺序）
-- ====================================

-- 删除有外键依赖的表
DROP TABLE IF EXISTS MeetingMaterials;
DROP TABLE IF EXISTS Notification;
DROP TABLE IF EXISTS Log;
DROP TABLE IF EXISTS Equipment;
DROP TABLE IF EXISTS Maintenance;
DROP TABLE IF EXISTS Booking;

-- 删除主表
DROP TABLE IF EXISTS MeetingRoom;
DROP TABLE IF EXISTS User;

-- ====================================
-- 3. 删除数据库（可选）
-- ====================================
-- 如果需要完全删除数据库，取消注释以下行：
-- DROP DATABASE IF EXISTS test_meeting_rooms;

-- ====================================
-- 重置完成提示
-- ====================================
SELECT '⚠️  数据库重置完成' as 状态, 
       '所有表和数据已删除' as 说明;

SELECT '下一步' as 操作, 
       '运行 01_create_tables.sql 重新创建表结构' as 建议;
