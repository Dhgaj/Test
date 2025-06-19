#!/bin/bash

# 会议室管理系统测试数据生成脚本
# 一键运行脚本，自动安装依赖并生成测试数据

echo "🚀 会议室管理系统 - 测试数据生成工具"
echo "================================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python3 环境检查通过"

# 检查pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip 未安装，请先安装pip"
    exit 1
fi

# 安装依赖
echo "📦 检查并安装依赖包..."
pip install -r requirements.txt -q

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，请检查网络连接"
    exit 1
fi

echo "✅ 依赖安装完成"

# 选择运行模式
echo ""
echo "请选择运行模式："
echo "1. 快速生成（基础数据，适合开发测试）"
echo "2. 自定义生成（高级选项，适合特定需求）"
echo "3. 大量数据生成（性能测试）"
echo "4. 查看数据库统计"
echo "5. 清理测试数据后重新生成"
echo ""

read -p "请输入选择 (1-5): " choice

case $choice in
    1)
        echo "🔄 运行快速数据生成..."
        python3 quick_test_data.py --auto
        ;;
    2)
        echo "🔄 启动自定义数据生成器..."
        echo "使用示例："
        echo "  python3 advanced_data_generator.py --users 100 --rooms 50"
        echo "  python3 advanced_data_generator.py --all"
        echo ""
        read -p "请输入自定义参数（或按回车使用默认）: " custom_args
        if [ -z "$custom_args" ]; then
            python3 advanced_data_generator.py --all
        else
            python3 advanced_data_generator.py $custom_args
        fi
        ;;
    3)
        echo "🔄 生成大量测试数据（适合性能测试）..."
        python3 advanced_data_generator.py --all --users 200 --rooms 80 --reservations 500 --logs 1000 --notifications 300
        ;;
    4)
        echo "📊 查看数据库统计信息..."
        python3 advanced_data_generator.py --stats
        ;;
    5)
        echo "⚠️  这将清理现有测试数据并重新生成"
        read -p "确认继续？(y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            echo "🔄 清理并重新生成数据..."
            python3 advanced_data_generator.py --all --clear
        else
            echo "❌ 操作已取消"
        fi
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 操作完成！"
echo ""
echo "📝 测试账户信息："
echo "   管理员账户: admin_001, admin_002, admin_003 (密码: 123456)"
echo "   普通用户: testuser_0001, testuser_0002... (密码: 123456)"
echo ""
echo "🌐 启动应用程序："
echo "   python3 app.py"
echo ""
