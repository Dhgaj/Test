# 会议室管理系统 - SQL文件夹说明

## 📁 文件夹结构

```
sql/
├── 00_reset_database.sql          # 数据库重置脚本（谨慎使用）
├── 01_create_tables.sql           # 数据库表结构创建
├── 02_insert_base_data.sql        # 基础数据插入
├── 03_create_compatibility_views.sql # 兼容性视图（解决历史问题）
├── 04_maintenance_operations.sql  # 数据库维护和优化脚本
├── 05_security_hardening.sql      # 数据库安全加固脚本
├── 06_database_tests.sql          # 数据库功能测试脚本
├── 99_full_install.sql            # 一键完整安装脚本
├── hotfix_duplicate_columns.sql   # 热修复：重复列问题修复
├── run_sql.sh                     # SQL执行辅助脚本
└── README.md                      # 本说明文件
```

## 🚀 快速开始

### 方式一：使用执行脚本（推荐）
```bash
# 进入SQL目录
cd sql

# 查看帮助信息
./run_sql.sh --help

# 查看所有可用脚本
./run_sql.sh --list

# 一键安装
./run_sql.sh --install

# 运行测试
./run_sql.sh --test

# 运行维护
./run_sql.sh --maintain

# 安全加固
./run_sql.sh --secure
```

### 方式二：一键安装（传统方式）
```bash
mysql -u root -p < sql/99_full_install.sql
```

### 方式三：分步安装（传统方式）
```bash
# 1. 重置数据库（可选，仅在需要清空时使用）
mysql -u root -p < sql/00_reset_database.sql

# 2. 创建表结构
mysql -u root -p < sql/01_create_tables.sql

# 3. 插入基础数据
mysql -u root -p < sql/02_insert_base_data.sql

# 4. 创建兼容性视图（解决历史查询问题）
mysql -u root -p < sql/03_create_compatibility_views.sql

# 5. 运行数据库测试（可选）
mysql -u root -p < sql/06_database_tests.sql
```

### 方式四：高级维护操作
```bash
# 数据库维护和优化
mysql -u root -p < sql/04_maintenance_operations.sql

# 安全加固（生产环境推荐）
mysql -u root -p < sql/05_security_hardening.sql
```

## 📋 文件详细说明

### 00_reset_database.sql
- **作用**: 完全重置数据库，删除所有数据和表结构
- **警告**: ⚠️ 此操作不可逆，会删除所有数据！
- **使用场景**: 
  - 全新安装
  - 开发环境重置
  - 测试环境初始化

### 01_create_tables.sql
- **作用**: 创建完整的数据库表结构
- **包含表**:
  - User（用户信息）
  - MeetingRoom（会议室信息）
  - Booking（预订信息）
  - Equipment（设备信息）
  - Log（系统日志）
  - Notification（通知消息）
  - Maintenance（维护记录）
  - MeetingMaterials（会议资料）
- **特色**:
  - 完整的索引优化
  - 外键约束保证数据完整性
  - 详细的注释说明

### 02_insert_base_data.sql
- **作用**: 插入系统运行所需的基础数据
- **包含数据**:
  - 管理员账户（admin, liansifan）
  - 测试用户账户
  - 10个会议室（包含线上和线下）
  - 设备配置信息
  - 示例预订记录
  - 维护计划记录
  - 系统日志示例
  - 通知消息示例
- **修复内容**:
  - ✅ 修复了预订时间逻辑错误
  - ✅ 修正了参会人数与房间容量不符问题

### 03_create_compatibility_views.sql
- **作用**: 解决历史数据库查询兼容性问题
- **解决的问题**:
  1. 查询使用`MaintenanceID`但表使用`ID`作为主键
  2. 查询使用`Users`表名但实际表名是`User`
  3. 查询使用`Username`列名但实际列名是`UserName`
- **创建的视图**:
  - `MaintenanceView`: 将`ID`映射为`MaintenanceID`
  - `Users`: 将`User`表映射为`Users`视图，`UserName`映射为`Username`

### 04_maintenance_operations.sql
- **作用**: 数据库日常维护、性能优化和数据清理
- **包含功能**:
  - 数据库健康检查
  - 索引使用情况分析
  - 过期数据清理
  - 性能优化操作
  - 数据完整性检查
  - 统计信息更新
  - 监控查询和报告
- **使用场景**: 定期维护、性能优化

### 05_security_hardening.sql
- **作用**: 增强数据库安全性，创建专用用户和权限控制
- **包含功能**:
  - 创建专用数据库用户
  - 权限分配和管理
  - 安全审计表创建
  - 密码安全检查
  - 安全监控视图
  - 安全策略触发器
- **使用场景**: 生产环境部署、安全加固

### 06_database_tests.sql
- **作用**: 全面测试数据库功能和性能
- **包含测试**:
  - 基础连接和权限测试
  - 表结构完整性测试
  - 外键约束测试
  - 索引完整性测试
  - 数据完整性测试
  - 兼容性视图测试
  - 查询性能测试
  - CRUD操作测试
  - 事务测试
  - 性能基准测试
- **使用场景**: 系统验证、故障诊断

### 99_full_install.sql
- **作用**: 一键完整安装整个数据库系统
- **包含内容**: 
  - 所有上述脚本的完整合并版本
  - 安装进度提示
  - 系统信息显示
  - 错误处理机制

## 🛠️ 维护说明

### 数据库版本要求
- MySQL 5.7+
- MariaDB 10.2+

### 字符集设置
- 数据库字符集: `utf8mb4`
- 排序规则: `utf8mb4_unicode_ci`

### 性能优化
所有脚本已包含以下优化：
- 主键和外键索引
- 常用查询字段索引
- 适当的数据类型选择

### 安全考虑
- 默认管理员密码为MD5加密的`123456`
- 生产环境部署前请修改默认密码
- 建议启用SSL连接

## 🔧 故障排除

### 常见问题

1. **权限错误**
   ```bash
   # 确保MySQL用户有足够权限
   GRANT ALL PRIVILEGES ON test_meeting_rooms.* TO 'username'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. **字符集问题**
   ```sql
   # 检查字符集设置
   SHOW VARIABLES LIKE 'character_set%';
   ```

3. **兼容性视图问题**
   ```sql
   # 验证视图创建成功
   SHOW FULL TABLES WHERE Table_type = 'VIEW';
   ```

### 验证安装

安装完成后，可以运行以下查询验证：

```sql
-- 检查表结构
SHOW TABLES;

-- 检查数据
SELECT COUNT(*) FROM User;
SELECT COUNT(*) FROM MeetingRoom;
SELECT COUNT(*) FROM Booking;

-- 测试兼容性视图
SELECT MaintenanceID FROM MaintenanceView LIMIT 1;
SELECT Username FROM Users LIMIT 1;
```

## 📞 技术支持

如果遇到问题，请检查：
1. MySQL服务是否正常运行
2. 用户权限是否足够
3. 字符集设置是否正确
4. 磁盘空间是否充足

---

**创建时间**: 2025年6月9日  
**版本**: 1.0  
**维护者**: 会议室管理系统开发团队
