#!/usr/bin/env python3
"""
简化版测试数据生成脚本
快速生成测试数据，无需交互
"""

import os
import sys
import random
import hashlib
from datetime import datetime, timedelta
from faker import Faker
import pymysql

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
    print(f"✅ 已加载数据库配置: {config.DB_HOST}:{config.DB_NAME}")
except ImportError:
    # 如果没有config.py，使用默认配置
    DATABASE_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'test_meeting_rooms',
        'charset': 'utf8mb4'
    }
    print("⚠️  使用默认数据库配置")

# 初始化Faker，支持中文
fake = Faker(['zh_CN', 'en_US'])

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DATABASE_CONFIG)
        print("✅ 数据库连接成功")
        return connection
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def quick_generate_all():
    """快速生成所有测试数据"""
    print("🚀 开始生成测试数据...")
    print("=" * 50)
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # 1. 生成用户
        print("👥 生成用户数据...")
        users_created = 0
        for i in range(30):
            try:
                username = f"user_{i+1:03d}"
                email = f"user{i+1:03d}@test.com"
                password = hashlib.md5('123456'.encode()).hexdigest()
                role = 'admin' if i < 3 else 'user'  # 前3个为管理员
                
                sql = """
                INSERT INTO User (UserName, Password, Email, EmailVerified, Role)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (username, password, email, True, role))
                users_created += 1
            except Exception:
                pass  # 忽略重复用户
        
        print(f"   ✓ 创建了 {users_created} 个用户")
        
        # 2. 生成会议室
        print("🏢 生成会议室数据...")
        rooms_created = 0
        room_types = ['Offline', 'Online']
        buildings = ['A座', 'B座', 'C座', '主楼']
        
        for i in range(15):
            try:
                room_number = f"R{100 + i}"
                room_name = f"会议室-{room_number}"
                capacity = random.randint(4, 30)
                room_type = random.choice(room_types)
                
                if room_type == 'Offline':
                    location = f"{random.randint(1, 8)}楼{random.randint(1, 20)}号房间"
                    meeting_link = None
                    building = random.choice(buildings)
                    floor = str(random.randint(1, 8))
                else:
                    location = None
                    meeting_link = f"https://meeting.example.com/room/{room_number}"
                    building = None
                    floor = None
                
                sql = """
                INSERT INTO MeetingRoom (RoomNumber, RoomName, Capacity, Equipment, Status, 
                                       RoomType, Location, MeetingLink, Floor, Building, Description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (room_number, room_name, capacity, '投影仪,白板,音响', 'Available',
                                    room_type, location, meeting_link, floor, building, f"可容纳{capacity}人"))
                rooms_created += 1
            except Exception:
                pass
        
        print(f"   ✓ 创建了 {rooms_created} 个会议室")
        
        # 3. 获取用户和房间ID
        cursor.execute("SELECT UserID FROM User")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT RoomID FROM MeetingRoom")
        room_ids = [row[0] for row in cursor.fetchall()]
        
        # 4. 生成预订
        print("📅 生成预订数据...")
        reservations_created = 0
        meeting_titles = ['项目启动会', '周例会', '产品讨论', '技术评审', '客户沟通', '团队建设']
        
        for i in range(50):
            try:
                room_id = random.choice(room_ids)
                user_id = random.choice(user_ids)
                
                # 生成时间（最近15天内）
                start_date = datetime.now() - timedelta(days=random.randint(0, 15))
                start_time = start_date.replace(
                    hour=random.randint(9, 16),
                    minute=random.choice([0, 30]),
                    second=0,
                    microsecond=0
                )
                end_time = start_time + timedelta(hours=random.randint(1, 3))
                
                title = f"{random.choice(meeting_titles)}-{i+1:03d}"
                status = random.choice(['Confirmed', 'Pending', 'Cancelled'])
                attendees = random.randint(2, 15)
                
                sql = """
                INSERT INTO Booking (RoomID, UserID, StartTime, EndTime, Status, Title, 
                                   Purpose, Attendees, MeetingType)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (room_id, user_id, start_time, end_time, status,
                                    title, f"关于{title}的讨论", attendees, 'Offline'))
                reservations_created += 1
            except Exception:
                pass
        
        print(f"   ✓ 创建了 {reservations_created} 个预订")
        
        # 5. 生成通知
        print("📢 生成通知数据...")
        notifications_created = 0
        notification_messages = [
            '您的会议预订已确认',
            '会议提醒：您的会议将在30分钟后开始',
            '系统维护通知',
            '新功能上线通知'
        ]
        
        for i in range(40):
            try:
                user_id = random.choice(user_ids)
                message = random.choice(notification_messages)
                status = random.choice(['Unread', 'Read'])
                
                sql = """
                INSERT INTO Notification (UserID, Status, Message)
                VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (user_id, status, message))
                notifications_created += 1
            except Exception:
                pass
        
        print(f"   ✓ 创建了 {notifications_created} 个通知")
        
        # 6. 生成日志
        print("📝 生成日志数据...")
        logs_created = 0
        actions = ['登录', '登出', '创建预订', '修改预订', '取消预订']
        
        for i in range(80):
            try:
                user_id = random.choice(user_ids)
                action = random.choice(actions)
                timestamp = fake.date_time_between(start_date='-15d', end_date='now')
                
                sql = """
                INSERT INTO Log (UserID, Action, Timestamp, Description, IPAddress)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (user_id, action, timestamp, f"用户执行{action}操作", fake.ipv4()))
                logs_created += 1
            except Exception:
                pass
        
        print(f"   ✓ 创建了 {logs_created} 个日志记录")
        
        connection.commit()
        print("\n🎉 测试数据生成完成！")
        print("=" * 50)
        
        # 显示统计信息
        show_stats(cursor)
        
        return True
        
    except Exception as e:
        print(f"❌ 生成数据失败: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def show_stats(cursor):
    """显示数据统计"""
    print("📊 数据库统计:")
    
    tables = {
        'User': '用户',
        'MeetingRoom': '会议室', 
        'Booking': '预订',
        'Notification': '通知',
        'Log': '日志'
    }
    
    for table, name in tables.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {name}: {count} 条")
        except:
            print(f"   {name}: 查询失败")

def main():
    """主函数"""
    print("🚀 会议室管理系统 - 快速测试数据生成器")
    print("📝 默认管理员账户:")
    print("   用户名: user_001, user_002, user_003")
    print("   密码: 123456")
    print("📝 普通用户账户:")
    print("   用户名: user_004 ~ user_030")
    print("   密码: 123456")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # 自动模式，直接生成
        quick_generate_all()
    else:
        # 交互模式
        response = input("是否开始生成测试数据? (y/N): ").strip().lower()
        if response in ['y', 'yes', '是']:
            quick_generate_all()
        else:
            print("❌ 操作已取消")

if __name__ == "__main__":
    main()
