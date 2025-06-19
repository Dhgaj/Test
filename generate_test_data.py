#!/usr/bin/env python3
"""
测试数据生成脚本
随机创建用户、预订、维护记录等数据以充实数据库
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
except ImportError:
    # 如果没有config.py，使用默认配置
    DATABASE_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'test_meeting_rooms',
        'charset': 'utf8mb4'
    }

# 初始化Faker，支持中文
fake = Faker(['zh_CN', 'en_US'])

# 常量定义
ROLES = ['admin', 'user']
ROOM_TYPES = ['Offline', 'Online']
MEETING_TYPES = ['Offline', 'Online']
RESERVATION_STATUSES = ['Pending', 'Confirmed', 'Cancelled']
ROOM_STATUSES = ['Available', 'Unavailable', 'Maintenance']
MAINTENANCE_STATUSES = ['Scheduled', 'InProgress', 'Completed']

# 会议室设备列表
EQUIPMENT_LIST = [
    '投影仪', '音响设备', '白板', '电视屏幕', '视频会议设备',
    '笔记本电脑', '无线话筒', '激光笔', '翻页笔', '摄像头'
]

# 会议主题模板
MEETING_TITLES = [
    '项目启动会议', '周例会', '产品讨论会', '技术评审会', '客户沟通会',
    '团队建设活动', '培训会议', '年度总结会', '季度规划会', '需求评审会',
    '设计评审会', '代码评审会', '测试总结会', '发布计划会', '风险评估会'
]

# 会议目的模板
MEETING_PURPOSES = [
    '讨论项目进展和下一步计划',
    '评估产品功能需求和用户体验',
    '技术方案设计和架构评审',
    '团队协作和沟通改进',
    '客户需求收集和反馈处理',
    '项目风险识别和应对策略',
    '产品迭代计划和时间安排',
    '技术培训和知识分享',
    '工作总结和经验交流',
    '新项目启动和资源分配'
]

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DATABASE_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def generate_users(count=50):
    """生成随机用户数据"""
    print(f"开始生成 {count} 个用户...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        for i in range(count):
            # 生成用户数据
            username = fake.user_name() + str(random.randint(100, 999))
            email = fake.email()
            password = hashlib.md5('123456test'.encode()).hexdigest()  # 默认密码123456test
            role = random.choice(ROLES) if i > 5 else 'admin'  # 前几个设为管理员
            email_verified = random.choice([True, False]) if role == 'user' else True
            
            # 插入用户
            sql = """
            INSERT INTO User (UserName, Password, Email, EmailVerified, Role)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (username, password, email, email_verified, role))
            
            if (i + 1) % 10 == 0:
                print(f"已生成 {i + 1} 个用户")
        
        connection.commit()
        print(f"✅ 成功生成 {count} 个用户")
        
    except Exception as e:
        print(f"❌ 生成用户数据失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def generate_rooms(count=20):
    """生成随机会议室数据"""
    print(f"开始生成 {count} 个会议室...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        for i in range(count):
            # 生成会议室数据
            room_number = f"R{random.randint(100, 999)}"
            room_name = f"会议室-{room_number}"
            capacity = random.randint(4, 50)
            equipment = ','.join(random.sample(EQUIPMENT_LIST, random.randint(2, 5)))
            status = random.choice(ROOM_STATUSES)
            room_type = random.choice(ROOM_TYPES)
            
            # 根据类型生成相应信息
            if room_type == 'Offline':
                location = f"{random.randint(1, 10)}楼{random.randint(1, 20)}号房间"
                meeting_link = None
                floor = str(random.randint(1, 10))
                building = random.choice(['A座', 'B座', 'C座', '主楼'])
            else:
                location = None
                meeting_link = f"https://meeting.example.com/room/{room_number}"
                floor = None
                building = None
            
            description = f"可容纳{capacity}人的{room_type.lower()}会议室"
            
            # 插入会议室
            sql = """
            INSERT INTO MeetingRoom (RoomNumber, RoomName, Capacity, Equipment, Status, 
                                   RoomType, Location, MeetingLink, Floor, Building, Description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (room_number, room_name, capacity, equipment, status,
                                room_type, location, meeting_link, floor, building, description))
            
            if (i + 1) % 5 == 0:
                print(f"已生成 {i + 1} 个会议室")
        
        connection.commit()
        print(f"✅ 成功生成 {count} 个会议室")
        
    except Exception as e:
        print(f"❌ 生成会议室数据失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def generate_reservations(count=100):
    """生成随机预订数据"""
    print(f"开始生成 {count} 个预订...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 获取用户和会议室ID
        cursor.execute("SELECT UserID FROM User")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT RoomID FROM MeetingRoom WHERE Status = 'Available'")
        room_ids = [row[0] for row in cursor.fetchall()]
        
        if not user_ids or not room_ids:
            print("❌ 没有可用的用户或会议室数据")
            return
        
        for i in range(count):
            # 生成预订数据
            room_id = random.choice(room_ids)
            user_id = random.choice(user_ids)
            
            # 生成时间（最近30天内的随机时间）
            start_date = datetime.now() - timedelta(days=random.randint(0, 30))
            start_time = start_date.replace(
                hour=random.randint(8, 17),
                minute=random.choice([0, 15, 30, 45]),
                second=0,
                microsecond=0
            )
            
            # 会议时长（1-4小时）
            duration_hours = random.randint(1, 4)
            end_time = start_time + timedelta(hours=duration_hours)
            
            status = random.choice(RESERVATION_STATUSES)
            title = random.choice(MEETING_TITLES)
            purpose = random.choice(MEETING_PURPOSES)
            attendees = random.randint(2, 20)
            # 80% 概率生成线上会议，20% 概率生成线下会议
            meeting_type = 'Online' if random.random() < 0.8 else 'Offline'
            meeting_password = None
            
            if meeting_type == 'Online':
                meeting_password = str(random.randint(100000, 999999))
            
            # 插入预订
            sql = """
            INSERT INTO Booking (RoomID, UserID, StartTime, EndTime, Status, Title, 
                               Purpose, Attendees, MeetingType, MeetingPassword)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (room_id, user_id, start_time, end_time, status,
                                title, purpose, attendees, meeting_type, meeting_password))
            
            if (i + 1) % 20 == 0:
                print(f"已生成 {i + 1} 个预订")
        
        connection.commit()
        print(f"✅ 成功生成 {count} 个预订")
        
    except Exception as e:
        print(f"❌ 生成预订数据失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def generate_equipment(count=50):
    """生成随机设备数据"""
    print(f"开始生成 {count} 个设备记录...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 获取会议室ID
        cursor.execute("SELECT RoomID FROM MeetingRoom")
        room_ids = [row[0] for row in cursor.fetchall()]
        
        if not room_ids:
            print("❌ 没有可用的会议室数据")
            return
        
        for i in range(count):
            room_id = random.choice(room_ids)
            equipment_name = random.choice(EQUIPMENT_LIST)
            quantity = random.randint(1, 5)
            
            # 插入设备
            sql = """
            INSERT INTO Equipment (RoomID, EquipmentName, Quantity)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (room_id, equipment_name, quantity))
            
            if (i + 1) % 10 == 0:
                print(f"已生成 {i + 1} 个设备记录")
        
        connection.commit()
        print(f"✅ 成功生成 {count} 个设备记录")
        
    except Exception as e:
        print(f"❌ 生成设备数据失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def generate_maintenance_records(count=30):
    """生成随机维护记录"""
    print(f"开始生成 {count} 个维护记录...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 获取会议室ID
        cursor.execute("SELECT RoomID FROM MeetingRoom")
        room_ids = [row[0] for row in cursor.fetchall()]
        
        if not room_ids:
            print("❌ 没有可用的会议室数据")
            return
        
        for i in range(count):
            room_id = random.choice(room_ids)
            
            # 生成维护时间
            maintenance_date = fake.date_between(start_date='-60d', end_date='+30d')
            start_time = datetime.combine(maintenance_date, datetime.min.time().replace(
                hour=random.randint(18, 22),  # 下班后维护
                minute=0
            ))
            end_time = start_time + timedelta(hours=random.randint(1, 4))
            
            description = random.choice([
                '空调系统维护', '投影设备检修', '网络设备更新',
                '桌椅维修', '灯光系统检查', '音响设备调试',
                '清洁保养', '设备安全检查'
            ])
            status = random.choice(MAINTENANCE_STATUSES)
            
            # 插入维护记录
            sql = """
            INSERT INTO Maintenance (RoomID, MaintenanceDate, StartTime, EndTime, 
                                   Description, Status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (room_id, maintenance_date, start_time, end_time,
                                description, status))
            
            if (i + 1) % 10 == 0:
                print(f"已生成 {i + 1} 个维护记录")
        
        connection.commit()
        print(f"✅ 成功生成 {count} 个维护记录")
        
    except Exception as e:
        print(f"❌ 生成维护记录失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def generate_notifications(count=80):
    """生成随机通知数据"""
    print(f"开始生成 {count} 个通知...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 获取用户ID
        cursor.execute("SELECT UserID FROM User")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not user_ids:
            print("❌ 没有可用的用户数据")
            return
        
        notification_templates = [
            '您的会议预订已确认',
            '会议室维护通知：您预订的会议室将进行维护',
            '会议提醒：您的会议将在30分钟后开始',
            '预订变更通知：您的会议时间已调整',
            '系统维护通知：系统将在今晚进行升级',
            '新功能上线通知',
            '会议室使用规则更新',
            '账户安全提醒'
        ]
        
        for i in range(count):
            user_id = random.choice(user_ids)
            message = random.choice(notification_templates)
            status = random.choice(['Unread', 'Read'])
            timestamp = fake.date_time_between(start_date='-30d', end_date='now')
            
            # 插入通知
            sql = """
            INSERT INTO Notification (UserID, Status, Timestamp, Message)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, status, timestamp, message))
            
            if (i + 1) % 20 == 0:
                print(f"已生成 {i + 1} 个通知")
        
        connection.commit()
        print(f"✅ 成功生成 {count} 个通知")
        
    except Exception as e:
        print(f"❌ 生成通知数据失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def generate_logs(count=200):
    """生成随机日志数据"""
    print(f"开始生成 {count} 个日志记录...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 获取用户ID
        cursor.execute("SELECT UserID FROM User")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not user_ids:
            print("❌ 没有可用的用户数据")
            return
        
        actions = ['登录', '登出', '创建预订', '修改预订', '取消预订', '查看会议室', '修改密码', '上传文件']
        descriptions = [
            '用户登录系统',
            '用户退出系统',
            '用户创建新的会议预订',
            '用户修改会议预订信息',
            '用户取消会议预订',
            '用户查看会议室信息',
            '用户修改登录密码',
            '用户上传会议资料'
        ]
        
        for i in range(count):
            user_id = random.choice(user_ids)
            action = random.choice(actions)
            description = random.choice(descriptions)
            timestamp = fake.date_time_between(start_date='-30d', end_date='now')
            ip_address = fake.ipv4()
            
            # 插入日志
            sql = """
            INSERT INTO Log (UserID, Action, Timestamp, Description, IPAddress)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, action, timestamp, description, ip_address))
            
            if (i + 1) % 50 == 0:
                print(f"已生成 {i + 1} 个日志记录")
        
        connection.commit()
        print(f"✅ 成功生成 {count} 个日志记录")
        
    except Exception as e:
        print(f"❌ 生成日志数据失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def clear_all_data():
    """清空所有测试数据"""
    print("⚠️  警告：即将清空所有数据！")
    confirm = input("请输入 'YES' 确认清空所有数据: ")
    
    if confirm != 'YES':
        print("操作已取消")
        return
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 禁用外键约束检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 清空所有表
        tables = ['MeetingMaterials', 'Log', 'Notification', 'Maintenance', 
                 'Equipment', 'Booking', 'MeetingRoom', 'User']
        
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
            print(f"已清空表: {table}")
        
        # 重新启用外键约束检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        connection.commit()
        print("✅ 所有数据已清空")
        
    except Exception as e:
        print(f"❌ 清空数据失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def show_statistics():
    """显示数据库统计信息"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        tables = {
            'User': '用户',
            'MeetingRoom': '会议室',
            'Booking': '预订',
            'Equipment': '设备',
            'Maintenance': '维护记录',
            'Notification': '通知',
            'Log': '日志',
            'MeetingMaterials': '会议资料'
        }
        
        print("\n📊 数据库统计信息:")
        print("-" * 40)
        
        for table, name in tables.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{name}: {count} 条记录")
        
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")
    finally:
        cursor.close()
        connection.close()

def main():
    """主函数"""
    print("🚀 会议室管理系统测试数据生成器")
    print("=" * 50)
    
    while True:
        print("\n请选择操作：")
        print("1. 生成所有测试数据（推荐）")
        print("2. 生成用户数据")
        print("3. 生成会议室数据")
        print("4. 生成预订数据")
        print("5. 生成设备数据")
        print("6. 生成维护记录")
        print("7. 生成通知数据")
        print("8. 生成日志数据")
        print("9. 查看数据统计")
        print("10. 清空所有数据")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-10): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        elif choice == '1':
            print("🔄 开始生成所有测试数据...")
            generate_users(50)
            generate_rooms(20)
            generate_equipment(50)
            generate_reservations(100)
            generate_maintenance_records(30)
            generate_notifications(80)
            generate_logs(200)
            print("✅ 所有测试数据生成完成！")
            show_statistics()
        elif choice == '2':
            count = int(input("请输入要生成的用户数量 (默认50): ") or "50")
            generate_users(count)
        elif choice == '3':
            count = int(input("请输入要生成的会议室数量 (默认20): ") or "20")
            generate_rooms(count)
        elif choice == '4':
            count = int(input("请输入要生成的预订数量 (默认100): ") or "100")
            generate_reservations(count)
        elif choice == '5':
            count = int(input("请输入要生成的设备数量 (默认50): ") or "50")
            generate_equipment(count)
        elif choice == '6':
            count = int(input("请输入要生成的维护记录数量 (默认30): ") or "30")
            generate_maintenance_records(count)
        elif choice == '7':
            count = int(input("请输入要生成的通知数量 (默认80): ") or "80")
            generate_notifications(count)
        elif choice == '8':
            count = int(input("请输入要生成的日志数量 (默认200): ") or "200")
            generate_logs(count)
        elif choice == '9':
            show_statistics()
        elif choice == '10':
            clear_all_data()
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()
