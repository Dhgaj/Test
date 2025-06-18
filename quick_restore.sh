#!/bin/bash

# 快速数据库恢复脚本（紧急恢复用）
# 会议室智控系统

# 加载环境变量
source .env

# 查找最新备份（兼容macOS和Linux）
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LATEST_BACKUP=$(find backups -name "meeting_room_backup_*.sql.gz" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
else
    # Linux
    LATEST_BACKUP=$(find backups -name "meeting_room_backup_*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
fi

# 如果上面的方法失败，使用更通用的方法
if [ -z "$LATEST_BACKUP" ]; then
    LATEST_BACKUP=$(ls -t backups/meeting_room_backup_*.sql.gz 2>/dev/null | head -1)
fi

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ 未找到备份文件！"
    exit 1
fi

echo "📦 从最新备份恢复: $LATEST_BACKUP"

# 解压并恢复
gunzip -c "$LATEST_BACKUP" | mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD $DB_NAME

if [ $? -eq 0 ]; then
    echo "✅ 快速恢复完成！"
else
    echo "❌ 恢复失败！"
    exit 1
fi
