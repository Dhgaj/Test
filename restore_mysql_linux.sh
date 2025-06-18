#!/bin/bash

# Linux服务器专用数据库恢复脚本
# 会议室智控系统 - 从最新备份中导入数据库

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 加载环境变量
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env 文件不存在！${NC}"
    exit 1
fi

source .env

# 配置
BACKUP_DIR="backups"
TEMP_DIR="/tmp"

# 检查备份目录是否存在
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ 备份目录不存在: $BACKUP_DIR${NC}"
    exit 1
fi

# 查找最新的备份文件（Linux版本）
echo -e "${BLUE}🔍 正在查找最新的备份文件...${NC}"
LATEST_BACKUP=$(find $BACKUP_DIR -name "meeting_room_backup_*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)

# 备用方法
if [ -z "$LATEST_BACKUP" ]; then
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/meeting_room_backup_*.sql.gz 2>/dev/null | head -1)
fi

if [ -z "$LATEST_BACKUP" ]; then
    echo -e "${RED}❌ 未找到任何备份文件！${NC}"
    echo -e "${YELLOW}请确保 $BACKUP_DIR 目录中存在 meeting_room_backup_*.sql.gz 文件${NC}"
    echo -e "${BLUE}当前目录内容:${NC}"
    ls -la $BACKUP_DIR/ 2>/dev/null || echo "目录为空或不存在"
    exit 1
fi

echo -e "${GREEN}✅ 找到最新备份文件: $LATEST_BACKUP${NC}"
echo -e "${BLUE}备份文件大小: $(du -h "$LATEST_BACKUP" | cut -f1)${NC}"
echo -e "${BLUE}备份创建时间: $(stat -c %y "$LATEST_BACKUP" 2>/dev/null)${NC}"

# 确认恢复操作
echo
echo -e "${YELLOW}⚠️  警告: 此操作将完全替换当前数据库的所有数据！${NC}"
echo -e "${YELLOW}   当前数据库: $DB_NAME${NC}"
echo -e "${YELLOW}   服务器: $DB_HOST${NC}"
echo
read -p "确认要从备份中恢复数据库吗？(输入 'YES' 继续): " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo -e "${YELLOW}❌ 操作已取消${NC}"
    exit 0
fi

# 解压备份文件到临时目录
TEMP_SQL_FILE="$TEMP_DIR/restore_$(basename "$LATEST_BACKUP" .gz)"
echo
echo -e "${BLUE}📦 正在解压备份文件...${NC}"
gunzip -c "$LATEST_BACKUP" > "$TEMP_SQL_FILE"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 解压备份文件失败！${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 备份文件解压成功${NC}"
echo -e "${BLUE}临时SQL文件: $TEMP_SQL_FILE${NC}"
echo -e "${BLUE}解压后大小: $(du -h "$TEMP_SQL_FILE" | cut -f1)${NC}"

# 测试数据库连接
echo
echo -e "${BLUE}🔌 测试数据库连接...${NC}"
mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD -e "SELECT 1;" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 无法连接到数据库！${NC}"
    echo -e "${YELLOW}请检查 .env 文件中的数据库配置${NC}"
    rm -f "$TEMP_SQL_FILE"
    exit 1
fi

echo -e "${GREEN}✅ 数据库连接正常${NC}"

# 创建恢复前的快速备份（可选）
echo
read -p "是否在恢复前创建当前数据库的快速备份？(y/N): " CREATE_BACKUP
if [[ $CREATE_BACKUP =~ ^[Yy]$ ]]; then
    QUICK_BACKUP_FILE="${BACKUP_DIR}/pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
    echo -e "${BLUE}📋 正在创建快速备份...${NC}"
    
    mysqldump -h $DB_HOST \
              -u $DB_USERNAME \
              -p$DB_PASSWORD \
              --skip-column-statistics \
              --single-transaction \
              --triggers \
              --complete-insert \
              $DB_NAME | gzip > "$QUICK_BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 快速备份创建成功: $QUICK_BACKUP_FILE${NC}"
    else
        echo -e "${YELLOW}⚠️  快速备份创建失败，但继续恢复操作${NC}"
    fi
fi

# 开始恢复数据库
echo
echo -e "${BLUE}🔄 开始恢复数据库...${NC}"
echo -e "${BLUE}恢复时间: $(date)${NC}"
echo "================================================================"

# 执行恢复
mysql -h $DB_HOST \
      -u $DB_USERNAME \
      -p$DB_PASSWORD \
      $DB_NAME < "$TEMP_SQL_FILE"

# 检查恢复是否成功
if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}✅ 数据库恢复成功！${NC}"
    
    # 验证恢复的数据
    echo -e "${BLUE}📊 验证恢复的数据...${NC}"
    
    # 检查用户表
    USER_COUNT=$(mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD -D $DB_NAME -se "SELECT COUNT(*) FROM User;" 2>/dev/null)
    echo -e "${BLUE}   用户数量: ${USER_COUNT:-'无法查询'}${NC}"
    
    # 检查会议室表
    ROOM_COUNT=$(mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD -D $DB_NAME -se "SELECT COUNT(*) FROM Room;" 2>/dev/null)
    echo -e "${BLUE}   会议室数量: ${ROOM_COUNT:-'无法查询'}${NC}"
    
    # 检查预订表
    RESERVATION_COUNT=$(mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD -D $DB_NAME -se "SELECT COUNT(*) FROM Reservation;" 2>/dev/null)
    echo -e "${BLUE}   预订记录数量: ${RESERVATION_COUNT:-'无法查询'}${NC}"
    
    echo
    echo -e "${GREEN}🎉 数据库恢复完成！${NC}"
    echo -e "${BLUE}恢复来源: $LATEST_BACKUP${NC}"
    echo -e "${BLUE}恢复时间: $(date)${NC}"
    
else
    echo
    echo -e "${RED}❌ 数据库恢复失败！${NC}"
    echo -e "${YELLOW}请检查错误信息并手动处理${NC}"
    
    # 清理临时文件
    rm -f "$TEMP_SQL_FILE"
    exit 1
fi

# 清理临时文件
echo
echo -e "${BLUE}🧹 清理临时文件...${NC}"
rm -f "$TEMP_SQL_FILE"
echo -e "${GREEN}✅ 临时文件已清理${NC}"

echo
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}恢复操作完成！请重启应用服务以确保所有缓存都已刷新。${NC}"
echo -e "${GREEN}================================================================${NC}"
