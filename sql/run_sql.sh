#!/bin/bash

# ==============================================================================
# 会议室管理系统 - SQL执行辅助脚本
# 文件: run_sql.sh
# 作用: 提供便捷的SQL脚本执行方式
# 创建时间: 2025年6月9日
# ==============================================================================

# 设置脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_DIR="$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}🗄️  会议室管理系统 - SQL执行工具${NC}"
    echo ""
    echo "用法: $0 [选项] [脚本名称]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -l, --list     列出所有可用的SQL脚本"
    echo "  -i, --install  执行完整安装"
    echo "  -t, --test     运行数据库测试"
    echo "  -m, --maintain 运行维护脚本"
    echo "  -s, --secure   运行安全加固"
    echo "  -r, --reset    重置数据库（危险操作）"
    echo ""
    echo "示例:"
    echo "  $0 --install                    # 一键安装"
    echo "  $0 --test                      # 运行测试"
    echo "  $0 01_create_tables.sql        # 执行指定脚本"
    echo ""
}

# 列出所有SQL脚本
list_scripts() {
    echo -e "${BLUE}📁 可用的SQL脚本:${NC}"
    echo ""
    for file in "$SQL_DIR"/*.sql; do
        if [[ -f "$file" ]]; then
            filename=$(basename "$file")
            case "$filename" in
                "00_"*) echo -e "${RED}  $filename${NC} - 数据库重置（谨慎使用）" ;;
                "01_"*) echo -e "${GREEN}  $filename${NC} - 创建表结构" ;;
                "02_"*) echo -e "${GREEN}  $filename${NC} - 插入基础数据" ;;
                "03_"*) echo -e "${GREEN}  $filename${NC} - 创建兼容性视图" ;;
                "04_"*) echo -e "${YELLOW}  $filename${NC} - 数据库维护" ;;
                "05_"*) echo -e "${YELLOW}  $filename${NC} - 安全加固" ;;
                "06_"*) echo -e "${BLUE}  $filename${NC} - 功能测试" ;;
                "99_"*) echo -e "${GREEN}  $filename${NC} - 一键完整安装" ;;
                *) echo -e "  $filename" ;;
            esac
        fi
    done
    echo ""
}

# 执行SQL脚本
execute_sql() {
    local sql_file="$1"
    local full_path
    
    # 检查文件是否存在
    if [[ -f "$SQL_DIR/$sql_file" ]]; then
        full_path="$SQL_DIR/$sql_file"
    elif [[ -f "$sql_file" ]]; then
        full_path="$sql_file"
    else
        echo -e "${RED}❌ 错误: 找不到文件 $sql_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🚀 执行SQL脚本: $(basename "$full_path")${NC}"
    echo ""
    
    # 提示用户输入MySQL密码
    read -s -p "请输入MySQL root 密码: " mysql_password
    echo ""
    
    # 执行SQL脚本
    if mysql -u root -p"$mysql_password" < "$full_path"; then
        echo ""
        echo -e "${GREEN}✅ 脚本执行成功!${NC}"
    else
        echo ""
        echo -e "${RED}❌ 脚本执行失败!${NC}"
        return 1
    fi
}

# 确认危险操作
confirm_dangerous_operation() {
    echo -e "${RED}⚠️  警告: 此操作将删除所有数据!${NC}"
    echo "请输入 'YES' 来确认执行重置操作:"
    read -r confirmation
    
    if [[ "$confirmation" != "YES" ]]; then
        echo -e "${YELLOW}操作已取消${NC}"
        return 1
    fi
    return 0
}

# 主逻辑
case "${1:-}" in
    -h|--help)
        show_help
        ;;
    -l|--list)
        list_scripts
        ;;
    -i|--install)
        echo -e "${GREEN}🔧 开始一键安装...${NC}"
        execute_sql "99_full_install.sql"
        ;;
    -t|--test)
        echo -e "${BLUE}🧪 开始运行数据库测试...${NC}"
        execute_sql "06_database_tests.sql"
        ;;
    -m|--maintain)
        echo -e "${YELLOW}🔧 开始运行维护脚本...${NC}"
        execute_sql "04_maintenance_operations.sql"
        ;;
    -s|--secure)
        echo -e "${YELLOW}🛡️  开始运行安全加固...${NC}"
        execute_sql "05_security_hardening.sql"
        ;;
    -r|--reset)
        if confirm_dangerous_operation; then
            echo -e "${RED}🗑️  开始重置数据库...${NC}"
            execute_sql "00_reset_database.sql"
        fi
        ;;
    "")
        show_help
        ;;
    *.sql)
        execute_sql "$1"
        ;;
    *)
        echo -e "${RED}❌ 未知选项: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
