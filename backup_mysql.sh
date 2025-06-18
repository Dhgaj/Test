#!/bin/bash

# 云服务器MySQL数据库备份脚本
# 会议室智控系统

# 加载环境变量
source .env

# 备份配置
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/meeting_room_backup_${DATE}.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "🗄️  开始备份MySQL数据库..."
echo "备份时间: $(date)"
echo "备份文件: $BACKUP_FILE"
echo "=" * 50

# 执行备份


mysqldump -h $DB_HOST \
          -u $DB_USERNAME \
          -p$DB_PASSWORD \
          --skip-column-statistics \
          --single-transaction \
          --triggers \
          --complete-insert \
          --add-drop-table \
          --add-locks \
          --disable-keys \
          --extended-insert \
          --quick \
          --lock-tables=false \
          $DB_NAME > $BACKUP_FILE


# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "✅ 数据库备份成功！"
    echo "备份文件大小: $(du -h $BACKUP_FILE | cut -f1)"
    
    # 压缩备份文件
    gzip $BACKUP_FILE
    echo "✅ 备份文件已压缩: ${BACKUP_FILE}.gz"
    
    # 删除7天前的备份文件
    find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
    echo "🧹 已清理7天前的备份文件"
    
else
    echo "❌ 数据库备份失败！"
    rm -f $BACKUP_FILE
    exit 1
fi

echo "🎉 备份完成！"


