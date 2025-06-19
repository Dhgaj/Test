#!/usr/bin/env python3
"""
线上会议专用数据生成脚本
专门生成线上会议室和线上会议预订数据
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
    DATABASE_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'test_meeting_rooms',
        'charset': 'utf8mb4'
    }
    print("⚠️  使用默认数据库配置")

# 初始化Faker
fake = Faker(['zh_CN'])

# 线上会议室设备列表
ONLINE_EQUIPMENT_LIST = [
    '高清摄像头', '专业麦克风', '扬声器系统', '智能白板', 
    '屏幕共享设备', '录制设备', '网络增强器', '背景绿幕',
    '补光灯', '视频编码器', '音频处理器', '网络摄像头'
]

# 线上会议主题
ONLINE_MEETING_TITLES = [
    '线上项目启动会', '远程周例会', '在线产品讨论', '视频技术评审',
    '远程客户沟通', '线上培训会议', '视频年度总结', '在线季度规划',
    '远程需求评审', '线上设计评审', '视频代码评审', '在线测试总结',
    '远程发布计划', '线上风险评估', '视频团队建设', '在线技术分享',
    '远程头脑风暴', '线上用户调研', '视频产品演示', '在线客户培训'
]

# 线上会议目的
ONLINE_MEETING_PURPOSES = [
    '通过视频会议讨论项目进展和远程协作计划',
    '在线评估产品功能需求和用户体验反馈',
    '远程技术方案设计和架构评审讨论',
    '视频会议加强团队协作和远程沟通',
    '线上收集客户需求和处理远程反馈',
    '通过在线会议识别项目风险和应对策略',
    '视频讨论产品迭代计划和远程开发安排',
    '线上技术培训和远程知识分享',
    '远程工作总结和在线经验交流',
    '视频会议启动新项目和分配远程资源'
]

# 会议平台列表
MEETING_PLATFORMS = [
    'zoom.us', 'teams.microsoft.com', 'meet.google.com', 
    'webex.cisco.com', 'goto.webex.com', 'skype.com',
    'dingtalk.com', 'tencent-meeting.com', 'voovmeeting.com'
]

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DATABASE_CONFIG)
        return connection
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def generate_online_rooms(count=30):
    """生成线上会议室"""
    print(f"🌐 开始生成 {count} 个线上会议室...")
    
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        cursor = connection.cursor()
        created = 0
        
        for i in range(count):
            try:
                # 生成会议室数据
                room_number = f"ON{200 + i}"  # 线上会议室使用ON前缀
                room_name = f"线上会议室-{room_number}"
                capacity = random.choice([10, 20, 30, 50, 100, 200, 500])  # 线上会议室容量可以更大
                
                # 随机选择线上设备
                equipment_count = random.randint(3, 8)
                equipment = ','.join(random.sample(ONLINE_EQUIPMENT_LIST, equipment_count))
                
                status = 'Available'  # 线上会议室通常都是可用的
                room_type = 'Online'  # 固定为线上类型
                
                # 线上会议室特有属性
                platform = random.choice(MEETING_PLATFORMS)
                meeting_link = f"https://{platform}/room/{room_number.lower()}"
                
                # 线上会议室没有物理位置
                location = None
                floor = None
                building = None
                
                description = f"支持{capacity}人同时在线的视频会议室，配备{equipment_count}种专业设备"
                
                # 插入会议室
                sql = """
                INSERT INTO MeetingRoom (RoomNumber, RoomName, Capacity, Equipment, Status, 
                                       RoomType, Location, MeetingLink, Floor, Building, Description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (room_number, room_name, capacity, equipment, status,
                                    room_type, location, meeting_link, floor, building, description))
                created += 1
                
                if created % 10 == 0:
                    print(f"   已创建 {created} 个线上会议室")
                    
            except pymysql.IntegrityError:
                pass  # 跳过重复的房间号
        
        connection.commit()
        print(f"   ✅ 成功创建 {created} 个线上会议室")
        return created
        
    except Exception as e:
        print(f"❌ 生成线上会议室失败: {e}")
        connection.rollback()
        return 0
    finally:
        cursor.close()
        connection.close()

def generate_online_reservations(count=500):
    """生成线上会议预订"""
    print(f"📹 开始生成 {count} 个线上会议预订...")
    
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        cursor = connection.cursor()
        
        # 获取用户ID
        cursor.execute("SELECT UserID FROM User")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        # 获取线上会议室ID
        cursor.execute("SELECT RoomID FROM MeetingRoom WHERE RoomType = 'Online' AND Status = 'Available'")
        online_room_ids = [row[0] for row in cursor.fetchall()]
        
        if not user_ids:
            print("   ❌ 没有可用的用户数据")
            return 0
            
        if not online_room_ids:
            print("   ❌ 没有可用的线上会议室，请先生成线上会议室")
            return 0
        
        created = 0
        
        for i in range(count):
            try:
                room_id = random.choice(online_room_ids)
                user_id = random.choice(user_ids)
                
                # 生成时间（最近30天内的随机时间）
                start_date = datetime.now() - timedelta(days=random.randint(0, 30))
                start_time = start_date.replace(
                    hour=random.randint(8, 21),  # 线上会议时间更灵活，可以到晚上
                    minute=random.choice([0, 15, 30, 45]),
                    second=0,
                    microsecond=0
                )
                
                # 线上会议时长（0.5-3小时，通常比线下会议短一些）
                duration_hours = random.choices(
                    [0.5, 1, 1.5, 2, 2.5, 3],
                    weights=[15, 35, 25, 15, 8, 2]
                )[0]
                end_time = start_time + timedelta(hours=duration_hours)
                
                # 线上会议状态分布
                status = random.choices(
                    ['Pending', 'Confirmed', 'Cancelled'],
                    weights=[10, 80, 10]  # 线上会议确认率更高
                )[0]
                
                title = random.choice(ONLINE_MEETING_TITLES)
                purpose = random.choice(ONLINE_MEETING_PURPOSES)
                
                # 线上会议参与人数通常更多
                attendees = random.choice([3, 5, 8, 10, 15, 20, 25, 30, 50])
                
                # 固定为线上会议类型
                meeting_type = 'Online'
                
                # 生成会议密码（线上会议都有密码）
                meeting_password = str(random.randint(100000, 999999))
                
                # 插入预订
                sql = """
                INSERT INTO Booking (RoomID, UserID, StartTime, EndTime, Status, Title, 
                                   Purpose, Attendees, MeetingType, MeetingPassword)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (room_id, user_id, start_time, end_time, status,
                                    title, purpose, attendees, meeting_type, meeting_password))
                created += 1
                
                if created % 50 == 0:
                    print(f"   已创建 {created} 个线上预订")
                    
            except Exception:
                pass
        
        connection.commit()
        print(f"   ✅ 成功创建 {created} 个线上会议预订")
        return created
        
    except Exception as e:
        print(f"❌ 生成线上预订失败: {e}")
        connection.rollback()
        return 0
    finally:
        cursor.close()
        connection.close()

def show_meeting_statistics():
    """显示会议类型统计"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        print("\n📊 会议室统计:")
        print("-" * 40)
        
        # 会议室统计
        cursor.execute("SELECT RoomType, COUNT(*) FROM MeetingRoom GROUP BY RoomType")
        room_stats = cursor.fetchall()
        for room_type, count in room_stats:
            type_name = "线上会议室" if room_type == "Online" else "线下会议室"
            print(f"   {type_name}: {count} 个")
        
        print("\n📅 预订统计:")
        print("-" * 40)
        
        # 预订统计
        cursor.execute("SELECT MeetingType, COUNT(*) FROM Booking GROUP BY MeetingType")
        booking_stats = cursor.fetchall()
        for meeting_type, count in booking_stats:
            type_name = "线上会议" if meeting_type == "Online" else "线下会议"
            print(f"   {type_name}: {count} 个")
        
        # 预订状态统计
        print("\n📈 预订状态统计:")
        print("-" * 40)
        cursor.execute("""
            SELECT MeetingType, Status, COUNT(*) 
            FROM Booking 
            GROUP BY MeetingType, Status 
            ORDER BY MeetingType, Status
        """)
        status_stats = cursor.fetchall()
        for meeting_type, status, count in status_stats:
            type_name = "线上" if meeting_type == "Online" else "线下"
            status_name = {"Pending": "待确认", "Confirmed": "已确认", "Cancelled": "已取消"}.get(status, status)
            print(f"   {type_name}会议-{status_name}: {count} 个")
        
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")
    finally:
        cursor.close()
        connection.close()

def main():
    """主函数"""
    print("🌐 线上会议数据生成器")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # 命令行参数模式
        if sys.argv[1] == '--rooms-only':
            rooms_count = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            generate_online_rooms(rooms_count)
        elif sys.argv[1] == '--meetings-only':
            meetings_count = int(sys.argv[2]) if len(sys.argv) > 2 else 500
            generate_online_reservations(meetings_count)
        elif sys.argv[1] == '--stats':
            show_meeting_statistics()
        elif sys.argv[1] == '--all':
            rooms_count = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            meetings_count = int(sys.argv[3]) if len(sys.argv) > 3 else 500
            generate_online_rooms(rooms_count)
            generate_online_reservations(meetings_count)
            show_meeting_statistics()
        else:
            print("用法:")
            print("  python online_meeting_generator.py --rooms-only [数量]     # 只生成线上会议室")
            print("  python online_meeting_generator.py --meetings-only [数量]  # 只生成线上会议")
            print("  python online_meeting_generator.py --all [会议室数] [会议数] # 生成所有")
            print("  python online_meeting_generator.py --stats               # 显示统计")
    else:
        # 交互模式
        print("请选择操作：")
        print("1. 生成线上会议室")
        print("2. 生成线上会议预订")
        print("3. 生成所有线上数据")
        print("4. 查看统计信息")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-4): ").strip()
        
        if choice == '0':
            print("👋 退出程序")
        elif choice == '1':
            count = int(input("请输入要生成的线上会议室数量 (默认30): ") or "30")
            generate_online_rooms(count)
            show_meeting_statistics()
        elif choice == '2':
            count = int(input("请输入要生成的线上会议数量 (默认500): ") or "500")
            generate_online_reservations(count)
            show_meeting_statistics()
        elif choice == '3':
            rooms_count = int(input("请输入要生成的线上会议室数量 (默认30): ") or "30")
            meetings_count = int(input("请输入要生成的线上会议数量 (默认500): ") or "500")
            print(f"🔄 生成 {rooms_count} 个线上会议室和 {meetings_count} 个线上会议...")
            generate_online_rooms(rooms_count)
            generate_online_reservations(meetings_count)
            show_meeting_statistics()
        elif choice == '4':
            show_meeting_statistics()
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()
