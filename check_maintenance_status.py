#!/usr/bin/env python3
"""
检查维护记录状态的脚本
"""

import pymysql
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
try:
    import config
    DATABASE_CONFIG = {
        'host': config.DB_HOST,
        'user': config.DB_USERNAME,
        'password': config.DB_PASSWORD,
        'database': config.DB_NAME,
        'charset': 'utf8mb4'
    }
except ImportError:
    DATABASE_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'test_meeting_rooms',
        'charset': 'utf8mb4'
    }

def check_maintenance_statuses():
    """检查维护记录的状态分布"""
    try:
        connection = pymysql.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()
        
        # 查询维护记录状态分布
        cursor.execute("""
            SELECT Status, COUNT(*) as count 
            FROM Maintenance 
            GROUP BY Status 
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        
        print("🔍 维护记录状态分布:")
        print("-" * 40)
        total = 0
        for status, count in results:
            print(f"   {status}: {count} 条")
            total += count
        print("-" * 40)
        print(f"   总计: {total} 条")
        
        # 查询最近的一些维护记录
        cursor.execute("""
            SELECT ID, Status, MaintenanceDate, StartTime, EndTime 
            FROM Maintenance 
            ORDER BY CreatedAt DESC 
            LIMIT 10
        """)
        
        recent_records = cursor.fetchall()
        
        print("\n📅 最近的维护记录:")
        print("-" * 80)
        print(f"{'ID':<5} {'状态':<15} {'日期':<12} {'开始时间':<16} {'结束时间':<16}")
        print("-" * 80)
        for record in recent_records:
            maintenance_id, status, date, start_time, end_time = record
            print(f"{maintenance_id:<5} {status:<15} {str(date):<12} {str(start_time):<16} {str(end_time):<16}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")

if __name__ == "__main__":
    check_maintenance_statuses()
