-- ==============================================================================
-- 会议室管理系统 - 数据库安全加固脚本
-- 文件: 05_security_hardening.sql
-- 作用: 增强数据库安全性，创建专用用户和权限控制
-- 创建时间: 2025年6月9日
-- ==============================================================================

-- 注意：此脚本需要使用 root 用户执行

-- ==============================================================================
-- 1. 创建专用数据库用户
-- ==============================================================================

-- 创建应用程序专用用户（读写权限）
-- 注意：请将 'your_secure_password' 替换为强密码
/*
CREATE USER IF NOT EXISTS 'meeting_app'@'localhost' IDENTIFIED BY 'your_secure_password';
CREATE USER IF NOT EXISTS 'meeting_app'@'%' IDENTIFIED BY 'your_secure_password';
*/

-- 创建只读用户（用于报表和监控）
-- 注意：请将 'your_readonly_password' 替换为强密码
/*
CREATE USER IF NOT EXISTS 'meeting_readonly'@'localhost' IDENTIFIED BY 'your_readonly_password';
CREATE USER IF NOT EXISTS 'meeting_readonly'@'%' IDENTIFIED BY 'your_readonly_password';
*/

-- 创建备份专用用户
-- 注意：请将 'your_backup_password' 替换为强密码
/*
CREATE USER IF NOT EXISTS 'meeting_backup'@'localhost' IDENTIFIED BY 'your_backup_password';
*/

-- ==============================================================================
-- 2. 权限分配
-- ==============================================================================

-- 应用程序用户权限（完整的数据操作权限）
/*
GRANT SELECT, INSERT, UPDATE, DELETE ON test_meeting_rooms.* TO 'meeting_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON test_meeting_rooms.* TO 'meeting_app'@'%';
*/

-- 只读用户权限（仅查询权限）
/*
GRANT SELECT ON test_meeting_rooms.* TO 'meeting_readonly'@'localhost';
GRANT SELECT ON test_meeting_rooms.* TO 'meeting_readonly'@'%';
*/

-- 备份用户权限
/*
GRANT SELECT, LOCK TABLES ON test_meeting_rooms.* TO 'meeting_backup'@'localhost';
*/

-- 刷新权限
/*
FLUSH PRIVILEGES;
*/

-- ==============================================================================
-- 3. 默认用户密码更新提醒
-- ==============================================================================

USE test_meeting_rooms;

-- 添加密码更新提醒通知
INSERT INTO Notification (UserID, Status, Message) 
SELECT 
    UserID,
    'Unread',
    '🔒 安全提醒：请尽快修改默认密码以确保账户安全！'
FROM User 
WHERE UserName IN ('admin', 'liansifan')
AND NOT EXISTS (
    SELECT 1 FROM Notification n 
    WHERE n.UserID = User.UserID 
    AND n.Message LIKE '%修改默认密码%'
);

-- ==============================================================================
-- 4. 创建安全审计表
-- ==============================================================================

CREATE TABLE IF NOT EXISTS SecurityAudit (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    Action VARCHAR(100) NOT NULL COMMENT '操作类型',
    TableName VARCHAR(100) COMMENT '涉及的表名',
    RecordID INT COMMENT '涉及的记录ID',
    OldValues JSON COMMENT '修改前的值',
    NewValues JSON COMMENT '修改后的值',
    IPAddress VARCHAR(45) COMMENT 'IP地址',
    UserAgent TEXT COMMENT '用户代理',
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    INDEX idx_security_audit_user (UserID),
    INDEX idx_security_audit_action (Action),
    INDEX idx_security_audit_timestamp (Timestamp)
) COMMENT '安全审计日志表';

-- ==============================================================================
-- 5. 创建安全相关视图
-- ==============================================================================

-- 创建敏感操作监控视图
CREATE OR REPLACE VIEW SensitiveOperations AS
SELECT 
    l.ID,
    u.UserName,
    l.Action,
    l.Timestamp,
    l.Description,
    l.IPAddress
FROM Log l
JOIN User u ON l.UserID = u.UserID
WHERE l.Action IN ('登录失败', '密码修改', '用户删除', '权限变更', '数据导出')
ORDER BY l.Timestamp DESC;

-- 创建用户活动摘要视图
CREATE OR REPLACE VIEW UserActivitySummary AS
SELECT 
    u.UserID,
    u.UserName,
    u.Role,
    u.Email,
    COUNT(l.ID) as LoginCount,
    MAX(l.Timestamp) as LastLogin,
    COUNT(DISTINCT DATE(l.Timestamp)) as ActiveDays
FROM User u
LEFT JOIN Log l ON u.UserID = l.UserID AND l.Action = '登录'
WHERE l.Timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY u.UserID, u.UserName, u.Role, u.Email;

-- ==============================================================================
-- 6. 安全策略触发器
-- ==============================================================================

-- 密码修改记录触发器
DELIMITER //
CREATE TRIGGER tr_password_change_audit
AFTER UPDATE ON User
FOR EACH ROW
BEGIN
    IF OLD.Password != NEW.Password THEN
        INSERT INTO Log (UserID, Action, Description, IPAddress)
        VALUES (NEW.UserID, '密码修改', 
                CONCAT('用户 ', NEW.UserName, ' 修改了密码'), 
                '系统记录');
                
        INSERT INTO SecurityAudit (UserID, Action, TableName, RecordID, OldValues, NewValues)
        VALUES (NEW.UserID, '密码修改', 'User', NEW.UserID,
                JSON_OBJECT('password_hash', LEFT(OLD.Password, 10)),
                JSON_OBJECT('password_hash', LEFT(NEW.Password, 10)));
    END IF;
END//
DELIMITER ;

-- 用户删除记录触发器
DELIMITER //
CREATE TRIGGER tr_user_delete_audit
BEFORE DELETE ON User
FOR EACH ROW
BEGIN
    INSERT INTO Log (UserID, Action, Description, IPAddress)
    VALUES (OLD.UserID, '用户删除', 
            CONCAT('用户 ', OLD.UserName, ' 被删除'), 
            '系统记录');
            
    INSERT INTO SecurityAudit (UserID, Action, TableName, RecordID, OldValues)
    VALUES (OLD.UserID, '用户删除', 'User', OLD.UserID,
            JSON_OBJECT('username', OLD.UserName, 'email', OLD.Email, 'role', OLD.Role));
END//
DELIMITER ;

-- ==============================================================================
-- 7. 数据备份安全
-- ==============================================================================

-- 创建备份记录表
CREATE TABLE IF NOT EXISTS BackupHistory (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    BackupType ENUM('Full', 'Incremental', 'Schema', 'Data') NOT NULL,
    BackupPath VARCHAR(500),
    BackupSize BIGINT COMMENT '备份文件大小（字节）',
    StartTime DATETIME NOT NULL,
    EndTime DATETIME,
    Status ENUM('Running', 'Completed', 'Failed') DEFAULT 'Running',
    ErrorMessage TEXT,
    CreatedBy VARCHAR(100),
    INDEX idx_backup_time (StartTime),
    INDEX idx_backup_status (Status)
) COMMENT '备份历史记录表';

-- ==============================================================================
-- 8. 安全检查查询
-- ==============================================================================

-- 检查弱密码用户（密码长度过短或使用默认密码）
SELECT 
    '弱密码检查' as 检查项目,
    COUNT(*) as 问题数量,
    GROUP_CONCAT(UserName) as 问题用户
FROM User 
WHERE Password = 'e10adc3949ba59abbe56e057f20f883e'  -- 默认密码 123456
   OR LENGTH(Password) < 32;  -- 密码哈希长度过短

-- 检查未验证邮箱的用户
SELECT 
    '邮箱验证检查' as 检查项目,
    COUNT(*) as 未验证用户数量
FROM User 
WHERE EmailVerified = 0 AND Email IS NOT NULL;

-- 检查最近登录失败次数
SELECT 
    '登录安全检查' as 检查项目,
    COUNT(*) as 近24小时登录失败次数
FROM Log 
WHERE Action = '登录失败' 
  AND Timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR);

-- 检查异常IP访问
SELECT 
    '异常访问检查' as 检查项目,
    IPAddress,
    COUNT(*) as 访问次数
FROM Log 
WHERE Timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
  AND IPAddress NOT LIKE '192.168.%'  -- 排除内网IP
  AND IPAddress NOT LIKE '10.%'       -- 排除内网IP
  AND IPAddress != '127.0.0.1'        -- 排除本地IP
GROUP BY IPAddress
HAVING COUNT(*) > 100;  -- 访问次数异常高

-- ==============================================================================
-- 9. 生成安全报告
-- ==============================================================================

-- 系统安全概况
SELECT 
    '🔐 数据库安全加固完成' as 状态,
    NOW() as 加固时间,
    (SELECT COUNT(*) FROM User) as 总用户数,
    (SELECT COUNT(*) FROM User WHERE EmailVerified = 1) as 已验证用户数,
    (SELECT COUNT(*) FROM SecurityAudit WHERE Timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)) as 近24小时审计记录;

-- ==============================================================================
-- 10. 安全建议
-- ==============================================================================

SELECT '🛡️ 安全建议' as 类型, '定期更换数据库用户密码' as 建议
UNION ALL
SELECT '🛡️ 安全建议', '启用 MySQL 的 SSL 连接'
UNION ALL
SELECT '🛡️ 安全建议', '定期检查和清理日志文件'
UNION ALL
SELECT '🛡️ 安全建议', '监控异常登录活动'
UNION ALL
SELECT '🛡️ 安全建议', '实施数据库访问白名单'
UNION ALL
SELECT '🛡️ 安全建议', '定期备份数据并测试恢复';
