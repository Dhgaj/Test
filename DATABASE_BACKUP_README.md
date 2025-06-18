# 数据库备份与恢复脚本

## 脚本说明

### 1. 备份脚本 - `backup_mysql.sh`
用于创建数据库备份，包含压缩和自动清理功能。

**使用方法：**
```bash
./backup_mysql.sh
```

**功能：**
- 创建完整的数据库备份
- 自动压缩备份文件
- 删除7天前的旧备份
- 包含表结构、数据、触发器等

### 2. 完整恢复脚本

#### `restore_mysql.sh` - 跨平台版本
安全的数据库恢复脚本，兼容macOS和Linux系统。

**使用方法：**
```bash
./restore_mysql.sh
```

#### `restore_mysql_linux.sh` - Linux服务器专用版本
专门为Linux服务器优化的恢复脚本，使用Linux特有的命令提高性能。

**使用方法：**
```bash
./restore_mysql_linux.sh
```

**推荐使用场景：**
- 本地开发（macOS）：使用 `restore_mysql.sh`
- 生产服务器（Linux）：使用 `restore_mysql_linux.sh`

**功能：**
- 自动查找最新的备份文件
- 显示备份文件信息
- 多重确认避免误操作
- 可选择在恢复前创建当前数据的快速备份
- 恢复后验证数据完整性
- 自动清理临时文件

**安全特性：**
- 恢复前需要输入 'YES' 确认
- 显示备份文件详细信息
- 测试数据库连接
- 可选的恢复前备份

### 3. 快速恢复脚本 - `quick_restore.sh`
紧急情况下的快速恢复脚本，省略所有确认步骤。

**使用方法：**
```bash
./quick_restore.sh
```

**⚠️ 注意：**
- 此脚本没有确认步骤，请谨慎使用
- 仅在紧急情况下使用
- 会立即覆盖当前数据库

## 使用场景

### 日常备份
```bash
# 创建定期备份
./backup_mysql.sh
```

### 系统维护恢复
```bash
# 安全恢复（推荐）
./restore_mysql.sh
```

### 紧急恢复
```bash
# 快速恢复（谨慎使用）
./quick_restore.sh
```

## 备份文件命名规则

备份文件格式：`meeting_room_backup_YYYYMMDD_HHMMSS.sql.gz`

例如：
- `meeting_room_backup_20250618_214834.sql.gz`
- `meeting_room_backup_20250613_093916.sql.gz`

## 环境要求

确保 `.env` 文件包含以下变量：
```bash
DB_HOST=你的数据库主机
DB_USERNAME=数据库用户名
DB_PASSWORD=数据库密码
DB_NAME=数据库名称
```

## 目录结构

```
项目根目录/
├── backup_mysql.sh           # 备份脚本
├── restore_mysql.sh          # 跨平台恢复脚本
├── restore_mysql_linux.sh    # Linux专用恢复脚本
├── quick_restore.sh          # 快速恢复脚本
├── .env                      # 环境变量文件
└── backups/                  # 备份文件目录
    ├── meeting_room_backup_20250618_214834.sql.gz
    └── meeting_room_backup_20250613_093916.sql.gz
```

## 故障排除

### 常见问题

1. **权限不足**
   ```bash
   chmod +x *.sh
   ```

2. **找不到备份文件**
   - 检查 `backups` 目录是否存在
   - 确认备份文件命名格式正确

3. **数据库连接失败**
   - 检查 `.env` 文件配置
   - 确认数据库服务正在运行
   - 验证网络连接

4. **恢复失败**
   - 检查备份文件是否损坏
   - 确认数据库权限足够
   - 查看错误日志

5. **find命令错误（macOS）**
   ```bash
   # 如果看到 "find: -printf: unknown primary or operator" 错误
   # 使用跨平台版本：
   ./restore_mysql.sh
   
   # 而不是Linux专用版本：
   ./restore_mysql_linux.sh
   ```

6. **备份文件权限问题**
   ```bash
   # 确保备份文件可读
   chmod 644 backups/*.sql.gz
   ```

### 测试连接
```bash
# 测试数据库连接
source .env
mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD -e "SELECT 1;"
```

## 自动化

### 设置定时备份（crontab）
```bash
# 编辑 crontab
crontab -e

# 添加每日凌晨2点备份
0 2 * * * /path/to/your/project/backup_mysql.sh
```

## 安全建议

1. **定期测试恢复流程**
2. **保留多个备份版本**
3. **备份文件异地存储**
4. **监控备份文件大小变化**
5. **恢复前总是创建当前数据备份**
