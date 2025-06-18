#!/usr/bin/env python3
"""
创建测试数据的脚本
用于测试控制面板的统计功能
"""

import os
import sys
from datetime import datetime, timedelta

# 添加应用根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Room, Reservation, MeetingMaterials

def create_test_data():
    """创建测试数据"""
    with app.app_context():
        try:
            # 检查是否有管理员用户
            admin_user = User.query.filter_by(Role='admin').first()
            if not admin_user:
                print("创建管理员用户...")
                admin_user = User(
                    UserName='admin',
                    Role='admin',
                    Email='admin@example.com',
                    EmailVerified=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("管理员用户创建成功")
            
            # 创建测试用户
            test_user = User.query.filter_by(UserName='testuser').first()
            if not test_user:
                print("创建测试用户...")
                test_user = User(
                    UserName='testuser',
                    Role='user',
                    Email='test@example.com',
                    EmailVerified=True
                )
                test_user.set_password('test123')
                db.session.add(test_user)
                db.session.commit()
                print("测试用户创建成功")
            
            # 检查是否有会议室
            rooms = Room.query.all()
            if not rooms:
                print("创建测试会议室...")
                room1 = Room(
                    RoomNumber='101',
                    RoomName='会议室A',
                    Capacity=10,
                    Equipment='投影仪,白板',
                    Status='Available',
                    RoomType='Offline',
                    Location='1楼',
                    Floor='1',
                    Building='主楼'
                )
                room2 = Room(
                    RoomNumber='102',
                    RoomName='会议室B',
                    Capacity=6,
                    Equipment='电视,白板',
                    Status='Available',
                    RoomType='Offline',
                    Location='1楼',
                    Floor='1',
                    Building='主楼'
                )
                db.session.add_all([room1, room2])
                db.session.commit()
                rooms = [room1, room2]
                print("测试会议室创建成功")
            
            # 创建不同状态的预订
            now = datetime.now()
            
            # 创建未来的待确认预订
            if not Reservation.query.filter_by(Status='Pending').first():
                print("创建待确认预订...")
                pending_reservation = Reservation(
                    RoomID=rooms[0].RoomID,
                    UserID=admin_user.UserID,
                    Title='待确认会议',
                    StartTime=now + timedelta(days=1, hours=2),
                    EndTime=now + timedelta(days=1, hours=4),
                    Purpose='这是一个待确认的会议',
                    Status='Pending',
                    Attendees=5,
                    MeetingType='Offline'
                )
                db.session.add(pending_reservation)
            
            # 创建已确认的预订
            if not Reservation.query.filter_by(Status='Confirmed').first():
                print("创建已确认预订...")
                confirmed_reservation = Reservation(
                    RoomID=rooms[1].RoomID,
                    UserID=admin_user.UserID,
                    Title='已确认会议',
                    StartTime=now + timedelta(days=2, hours=3),
                    EndTime=now + timedelta(days=2, hours=5),
                    Purpose='这是一个已确认的会议',
                    Status='Confirmed',
                    Attendees=8,
                    MeetingType='Offline'
                )
                db.session.add(confirmed_reservation)
            
            # 创建今日会议
            print("创建今日会议...")
            today_reservation = Reservation(
                RoomID=rooms[0].RoomID,
                UserID=admin_user.UserID,
                Title='今日重要会议',
                StartTime=now.replace(hour=14, minute=0, second=0),
                EndTime=now.replace(hour=16, minute=0, second=0),
                Purpose='今天的重要会议',
                Status='Confirmed',
                Attendees=6,
                MeetingType='Offline'
            )
            db.session.add(today_reservation)
            
            # 创建会议资料
            if not MeetingMaterials.query.filter_by(UserID=admin_user.UserID).first():
                print("创建会议资料...")
                material = MeetingMaterials(
                    BookingID=1,  # 假设存在ID为1的预订
                    UserID=admin_user.UserID,
                    Title='测试文档',
                    FilePath='static/uploads/meeting_materials/test.pdf',
                    FileName='test.pdf',
                    FileSize=1024,
                    FileType='pdf',
                    Status='Active',
                    Description='测试文档描述'
                )
                db.session.add(material)
            
            db.session.commit()
            print("测试数据创建完成！")
            
            # 显示统计信息
            total_users = User.query.count()
            total_rooms = Room.query.count()
            total_reservations = Reservation.query.count()
            pending_count = Reservation.query.filter_by(Status='Pending').count()
            confirmed_count = Reservation.query.filter_by(Status='Confirmed').count()
            
            print(f"\n=== 系统统计 ===")
            print(f"用户总数: {total_users}")
            print(f"会议室总数: {total_rooms}")
            print(f"预订总数: {total_reservations}")
            print(f"待确认预订: {pending_count}")
            print(f"已确认预订: {confirmed_count}")
            print(f"\n可以使用以下账户登录:")
            print(f"管理员: admin / admin123")
            print(f"普通用户: testuser / test123")
            
        except Exception as e:
            print(f"创建测试数据时出错: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_test_data()
