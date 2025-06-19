#!/usr/bin/env python3
"""
高级测试数据生成脚本
支持大量自定义选项和真实的测试数据生成
"""

import os
import sys
import random
import hashlib
import argparse
from datetime import datetime, timedelta, date
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
fake_en = Faker(['en_US'])

# 配置数据
class DataConfig:
    # 用户相关
    DEFAULT_PASSWORD = '123456'
    ADMIN_RATIO = 0.1  # 管理员比例
    EMAIL_DOMAINS = ['test.com', 'company.com', 'example.org', 'demo.net']
    
    # 会议室相关
    ROOM_TYPES = ['Offline', 'Online']
    ROOM_STATUSES = ['Available', 'Unavailable', 'Maintenance']
    BUILDINGS = ['A座', 'B座', 'C座', 'D座', '主楼', '技术楼', '行政楼']
    FLOORS = list(range(1, 20))
    EQUIPMENT_LIST = [
        '投影仪', '大屏幕', '音响设备', '白板', '电视屏幕', 
        '视频会议设备', '笔记本电脑', '无线话筒', '激光笔', 
        '翻页笔', '摄像头', '录音设备', '网络设备', '空调'
    ]
    
    # 会议相关
    MEETING_TITLES = [
        '项目启动会议', '周例会', '月度总结会', '季度规划会', '年度总结会',
        '产品讨论会', '技术评审会', '设计评审会', '代码评审会', '测试总结会',
        '客户沟通会', '需求评审会', '架构讨论会', '技术分享会', '培训会议',
        '团队建设活动', '发布计划会', '风险评估会', '预算讨论会', '人事会议'
    ]
    
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
        '新项目启动和资源分配',
        '预算规划和成本控制',
        '团队建设和文化交流'
    ]
    
    RESERVATION_STATUSES = ['Pending', 'Confirmed', 'Cancelled']
    
    # 维护相关
    MAINTENANCE_DESCRIPTIONS = [
        '空调系统检修维护', '投影设备定期保养', '网络设备升级更新',
        '桌椅维修和清洁', '灯光系统检查调试', '音响设备调试校准',
        '深度清洁消毒', '设备安全检查', '电路系统维护',
        '窗户清洁维护', '地毯清洁更换', '墙面维护粉刷'
    ]
    
    MAINTENANCE_STATUSES = ['Scheduled', 'InProgress', 'Completed', 'Cancelled']
    
    # 通知相关
    NOTIFICATION_TEMPLATES = [
        '您的会议预订已确认，请按时参加',
        '会议室维护通知：您预订的会议室将进行维护',
        '会议提醒：您的会议将在30分钟后开始',
        '预订变更通知：您的会议时间已调整',
        '系统维护通知：系统将在今晚22:00-02:00进行升级',
        '新功能上线通知：会议室预订系统新增了在线会议功能',
        '会议室使用规则更新：请查看最新的使用规范',
        '账户安全提醒：请定期更改您的登录密码',
        '会议取消通知：由于突发情况，您的会议已被取消',
        '设备故障通知：会议室设备正在维修中'
    ]
    
    # 日志相关
    LOG_ACTIONS = [
        '登录', '登出', '创建预订', '修改预订', '取消预订', 
        '查看会议室', '修改密码', '上传文件', '下载文件',
        '查看统计', '发送通知', '导出数据', '修改个人信息'
    ]

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DATABASE_CONFIG)
        return connection
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

class DataGenerator:
    def __init__(self):
        self.connection = get_db_connection()
        if not self.connection:
            raise Exception("无法连接到数据库")
        self.cursor = self.connection.cursor()

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()

    def generate_users(self, count=50, clear_existing=False):
        """生成用户数据"""
        print(f"👥 生成 {count} 个用户...")
        
        if clear_existing:
            self.cursor.execute("DELETE FROM User WHERE UserName LIKE 'testuser_%'")
            print("   已清理现有测试用户")
        
        admin_count = max(1, int(count * DataConfig.ADMIN_RATIO))
        created = 0
        
        for i in range(count):
            try:
                # 生成用户名
                if i < admin_count:
                    username = f"admin_{i+1:03d}"
                    role = 'admin'
                else:
                    username = f"testuser_{i+1:04d}"
                    role = 'user'
                
                # 生成邮箱
                domain = random.choice(DataConfig.EMAIL_DOMAINS)
                email = f"{username}@{domain}"
                
                # 密码哈希
                password = hashlib.md5(DataConfig.DEFAULT_PASSWORD.encode()).hexdigest()
                
                # 邮箱验证状态
                email_verified = random.choice([True, True, False])  # 大部分已验证
                
                sql = """
                INSERT INTO User (UserName, Password, Email, EmailVerified, Role)
                VALUES (%s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (username, password, email, email_verified, role))
                created += 1
                
                if created % 10 == 0:
                    print(f"   已创建 {created} 个用户")
                    
            except pymysql.IntegrityError:
                pass  # 跳过重复用户
                
        self.connection.commit()
        print(f"   ✅ 成功创建 {created} 个用户 (管理员: {min(admin_count, created)})")
        return created

    def generate_rooms(self, count=25, clear_existing=False):
        """生成会议室数据"""
        print(f"🏢 生成 {count} 个会议室...")
        
        if clear_existing:
            self.cursor.execute("DELETE FROM MeetingRoom WHERE RoomNumber LIKE 'TR%'")
            print("   已清理现有测试会议室")
        
        created = 0
        
        for i in range(count):
            try:
                room_number = f"TR{100 + i}"
                room_name = f"测试会议室-{room_number}"
                capacity = random.choice([4, 6, 8, 10, 12, 15, 20, 25, 30, 50])
                
                # 随机选择设备
                equipment_count = random.randint(2, 6)
                equipment = ','.join(random.sample(DataConfig.EQUIPMENT_LIST, equipment_count))
                
                status = random.choice(DataConfig.ROOM_STATUSES)
                room_type = random.choice(DataConfig.ROOM_TYPES)
                
                # 根据类型设置相关属性
                if room_type == 'Offline':
                    building = random.choice(DataConfig.BUILDINGS)
                    floor = str(random.choice(DataConfig.FLOORS))
                    location = f"{building} {floor}楼 {random.randint(1, 30):02d}号房间"
                    meeting_link = None
                else:
                    building = None
                    floor = None
                    location = None
                    meeting_link = f"https://meeting.company.com/room/{room_number.lower()}"
                
                description = f"可容纳{capacity}人的{room_type.lower()}会议室，配备{equipment_count}种设备"
                
                sql = """
                INSERT INTO MeetingRoom (RoomNumber, RoomName, Capacity, Equipment, Status, 
                                       RoomType, Location, MeetingLink, Floor, Building, Description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (room_number, room_name, capacity, equipment, status,
                                        room_type, location, meeting_link, floor, building, description))
                created += 1
                
                if created % 5 == 0:
                    print(f"   已创建 {created} 个会议室")
                    
            except pymysql.IntegrityError:
                pass
                
        self.connection.commit()
        print(f"   ✅ 成功创建 {created} 个会议室")
        return created

    def generate_reservations(self, count=100, days_range=30):
        """生成预订数据"""
        print(f"📅 生成 {count} 个预订（时间范围：{days_range}天）...")
        
        # 获取用户和会议室
        self.cursor.execute("SELECT UserID FROM User")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        self.cursor.execute("SELECT RoomID FROM MeetingRoom WHERE Status = 'Available'")
        room_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not user_ids or not room_ids:
            print("   ❌ 缺少用户或可用会议室数据")
            return 0
        
        created = 0
        
        for i in range(count):
            try:
                room_id = random.choice(room_ids)
                user_id = random.choice(user_ids)
                
                # 生成时间（过去和未来的时间）
                days_offset = random.randint(-days_range//2, days_range//2)
                base_date = datetime.now() + timedelta(days=days_offset)
                
                # 工作时间内的会议
                hour = random.choice([9, 10, 11, 13, 14, 15, 16, 17])
                minute = random.choice([0, 30])
                
                start_time = base_date.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
                
                # 会议时长
                duration_hours = random.choices(
                    [0.5, 1, 1.5, 2, 2.5, 3, 4],
                    weights=[10, 30, 20, 20, 10, 8, 2]
                )[0]
                
                end_time = start_time + timedelta(hours=duration_hours)
                
                # 会议信息
                title = random.choice(DataConfig.MEETING_TITLES)
                purpose = random.choice(DataConfig.MEETING_PURPOSES)
                attendees = random.randint(2, 20)
                status = random.choices(
                    DataConfig.RESERVATION_STATUSES,
                    weights=[15, 70, 15]  # 大部分已确认
                )[0]
                
                meeting_type = random.choice(['Offline', 'Online'])
                meeting_password = None
                if meeting_type == 'Online':
                    meeting_password = str(random.randint(100000, 999999))
                
                sql = """
                INSERT INTO Booking (RoomID, UserID, StartTime, EndTime, Status, Title, 
                                   Purpose, Attendees, MeetingType, MeetingPassword)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (room_id, user_id, start_time, end_time, status,
                                        title, purpose, attendees, meeting_type, meeting_password))
                created += 1
                
                if created % 20 == 0:
                    print(f"   已创建 {created} 个预订")
                    
            except Exception:
                pass
                
        self.connection.commit()
        print(f"   ✅ 成功创建 {created} 个预订")
        return created

    def generate_maintenance(self, count=20):
        """生成维护记录"""
        print(f"🔧 生成 {count} 个维护记录...")
        
        self.cursor.execute("SELECT RoomID FROM MeetingRoom")
        room_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not room_ids:
            print("   ❌ 没有可用的会议室")
            return 0
        
        created = 0
        
        for i in range(count):
            try:
                room_id = random.choice(room_ids)
                
                # 维护时间（通常在非工作时间）
                maintenance_date = fake.date_between(start_date='-30d', end_date='+30d')
                start_hour = random.choice([18, 19, 20, 21, 22, 6, 7])  # 晚上或早上
                start_time = datetime.combine(maintenance_date, datetime.min.time().replace(hour=start_hour))
                end_time = start_time + timedelta(hours=random.randint(1, 6))
                
                description = random.choice(DataConfig.MAINTENANCE_DESCRIPTIONS)
                status = random.choice(DataConfig.MAINTENANCE_STATUSES)
                
                sql = """
                INSERT INTO Maintenance (RoomID, MaintenanceDate, StartTime, EndTime, 
                                       Description, Status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (room_id, maintenance_date, start_time, end_time,
                                        description, status))
                created += 1
                
            except Exception:
                pass
                
        self.connection.commit()
        print(f"   ✅ 成功创建 {created} 个维护记录")
        return created

    def generate_notifications(self, count=100):
        """生成通知"""
        print(f"📢 生成 {count} 个通知...")
        
        self.cursor.execute("SELECT UserID FROM User")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not user_ids:
            print("   ❌ 没有可用的用户")
            return 0
        
        created = 0
        
        for i in range(count):
            try:
                user_id = random.choice(user_ids)
                message = random.choice(DataConfig.NOTIFICATION_TEMPLATES)
                status = random.choices(['Unread', 'Read'], weights=[30, 70])[0]
                timestamp = fake.date_time_between(start_date='-30d', end_date='now')
                
                sql = """
                INSERT INTO Notification (UserID, Status, Timestamp, Message)
                VALUES (%s, %s, %s, %s)
                """
                self.cursor.execute(sql, (user_id, status, timestamp, message))
                created += 1
                
            except Exception:
                pass
                
        self.connection.commit()
        print(f"   ✅ 成功创建 {created} 个通知")
        return created

    def generate_logs(self, count=200):
        """生成日志"""
        print(f"📝 生成 {count} 个日志记录...")
        
        self.cursor.execute("SELECT UserID FROM User")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not user_ids:
            print("   ❌ 没有可用的用户")
            return 0
        
        created = 0
        
        for i in range(count):
            try:
                user_id = random.choice(user_ids)
                action = random.choice(DataConfig.LOG_ACTIONS)
                timestamp = fake.date_time_between(start_date='-30d', end_date='now')
                description = f"用户执行{action}操作"
                ip_address = fake.ipv4()
                
                sql = """
                INSERT INTO Log (UserID, Action, Timestamp, Description, IPAddress)
                VALUES (%s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (user_id, action, timestamp, description, ip_address))
                created += 1
                
                if created % 50 == 0:
                    print(f"   已创建 {created} 个日志")
                    
            except Exception:
                pass
                
        self.connection.commit()
        print(f"   ✅ 成功创建 {created} 个日志记录")
        return created

    def show_statistics(self):
        """显示统计信息"""
        print("\n📊 数据库统计信息:")
        print("-" * 50)
        
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
        
        for table, name in tables.items():
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"   {name}: {count:>6} 条")
            except:
                print(f"   {name}: {'查询失败':>6}")
        
        print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description='会议室管理系统测试数据生成器')
    parser.add_argument('--users', type=int, default=50, help='生成用户数量 (默认: 50)')
    parser.add_argument('--rooms', type=int, default=25, help='生成会议室数量 (默认: 25)')
    parser.add_argument('--reservations', type=int, default=100, help='生成预订数量 (默认: 100)')
    parser.add_argument('--maintenance', type=int, default=20, help='生成维护记录数量 (默认: 20)')
    parser.add_argument('--notifications', type=int, default=100, help='生成通知数量 (默认: 100)')
    parser.add_argument('--logs', type=int, default=200, help='生成日志数量 (默认: 200)')
    parser.add_argument('--days', type=int, default=30, help='预订时间范围(天) (默认: 30)')
    parser.add_argument('--clear', action='store_true', help='清理现有测试数据')
    parser.add_argument('--all', action='store_true', help='生成所有类型的数据')
    parser.add_argument('--stats', action='store_true', help='只显示统计信息')
    
    args = parser.parse_args()
    
    print("🚀 会议室管理系统 - 高级测试数据生成器")
    print("=" * 60)
    
    try:
        generator = DataGenerator()
        
        if args.stats:
            generator.show_statistics()
            return
        
        if args.all:
            print("🔄 生成所有类型的测试数据...")
            generator.generate_users(args.users, args.clear)
            generator.generate_rooms(args.rooms, args.clear)
            generator.generate_reservations(args.reservations, args.days)
            generator.generate_maintenance(args.maintenance)
            generator.generate_notifications(args.notifications)
            generator.generate_logs(args.logs)
        else:
            # 根据参数选择性生成
            if args.users > 0:
                generator.generate_users(args.users, args.clear)
            if args.rooms > 0:
                generator.generate_rooms(args.rooms, args.clear)
            if args.reservations > 0:
                generator.generate_reservations(args.reservations, args.days)
            if args.maintenance > 0:
                generator.generate_maintenance(args.maintenance)
            if args.notifications > 0:
                generator.generate_notifications(args.notifications)
            if args.logs > 0:
                generator.generate_logs(args.logs)
        
        generator.show_statistics()
        print("\n🎉 数据生成完成！")
        print("\n📝 测试账户信息:")
        print("   管理员账户: admin_001, admin_002, admin_003...")
        print("   普通用户: testuser_0001, testuser_0002...")  
        print("   统一密码: 123456")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
