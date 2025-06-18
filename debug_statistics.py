#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据统计调试脚本
用于检查数据库中的实际数据并验证统计计算的正确性
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import pymysql

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入应用配置
from config import Config
from app import app, db, User, Room, Reservation

def check_database_connection():
    """检查数据库连接"""
    try:
        with app.app_context():
            # 执行简单查询测试连接
            result = db.session.execute(text("SELECT 1")).fetchone()
            print("✓ 数据库连接正常")
            return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def check_basic_statistics():
    """检查基本统计数据"""
    print("\n=== 基本统计数据检查 ===")
    
    with app.app_context():
        # 1. 总预订数
        total_bookings = Reservation.query.count()
        print(f"总预订数: {total_bookings}")
        
        # 2. 活跃用户数（有预订记录的用户）
        active_users = db.session.query(db.func.count(
            db.func.distinct(Reservation.UserID))).scalar()
        print(f"活跃用户数: {active_users}")
        
        # 3. 总会议室数
        total_rooms = Room.query.count()
        print(f"总会议室数: {total_rooms}")
        
        # 4. 检查用户表总数
        total_users = User.query.count()
        print(f"总用户数: {total_users}")

def check_duration_calculation():
    """检查平均预订时长计算"""
    print("\n=== 平均预订时长检查 ===")
    
    with app.app_context():
        # 获取所有预订的时长
        reservations = Reservation.query.all()
        print(f"总预订记录数: {len(reservations)}")
        
        if reservations:
            total_hours = 0
            valid_count = 0
            
            for res in reservations:
                if res.StartTime and res.EndTime:
                    duration = (res.EndTime - res.StartTime).total_seconds() / 3600
                    total_hours += duration
                    valid_count += 1
                    
                    # 显示前5个预订的详情
                    if valid_count <= 5:
                        print(f"预订 {res.ID}: {res.StartTime} ~ {res.EndTime}, 时长: {duration:.1f}小时")
            
            if valid_count > 0:
                avg_duration = total_hours / valid_count
                print(f"平均预订时长: {avg_duration:.1f}小时")
                
                # 使用数据库函数计算
                avg_duration_db = db.session.query(
                    db.func.avg(
                        db.func.timestampdiff(
                            db.text('HOUR'), Reservation.StartTime, Reservation.EndTime)
                    )
                ).scalar()
                print(f"数据库函数计算结果: {avg_duration_db:.1f}小时" if avg_duration_db else "数据库函数计算失败")

def check_room_usage():
    """检查会议室使用率计算"""
    print("\n=== 会议室使用率检查 ===")
    
    with app.app_context():
        rooms = Room.query.all()
        print(f"会议室总数: {len(rooms)}")
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        print(f"计算时间范围: {thirty_days_ago.strftime('%Y-%m-%d')} 到现在")
        
        for i, room in enumerate(rooms[:3]):  # 只显示前3个会议室的详情
            print(f"\n会议室 {room.RoomName} (ID: {room.RoomID}):")
            
            # 获取该会议室的预订记录
            reservations = Reservation.query.filter(
                Reservation.RoomID == room.RoomID,
                Reservation.StartTime >= thirty_days_ago,
                Reservation.Status.in_(['Confirmed', 'Pending'])
            ).all()
            
            print(f"  - 30天内预订数: {len(reservations)}")
            
            booked_hours = 0
            for res in reservations:
                start = max(res.StartTime, thirty_days_ago)
                duration = (res.EndTime - start).total_seconds() / 3600
                booked_hours += min(duration, 24)
            
            working_hours_per_day = 10
            total_working_hours = 30 * working_hours_per_day
            usage_rate = (booked_hours / total_working_hours) * 100
            
            print(f"  - 总预订时长: {booked_hours:.1f}小时")
            print(f"  - 总工作时长: {total_working_hours}小时")
            print(f"  - 使用率: {usage_rate:.1f}%")

def check_daily_bookings():
    """检查每日预订数据"""
    print("\n=== 每日预订数据检查 ===")
    
    with app.app_context():
        print("未来7天预订情况:")
        
        for i in range(0, 7):
            date = datetime.now() + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # 获取当天的预订数量
            day_start = date.replace(hour=0, minute=0, second=0)
            day_end = day_start + timedelta(days=1)
            
            count = Reservation.query.filter(
                Reservation.StartTime >= day_start,
                Reservation.StartTime < day_end
            ).count()
            
            print(f"  {date_str}: {count}个预订")

def check_top_users():
    """检查用户预订排名"""
    print("\n=== 用户预订排名检查 ===")
    
    with app.app_context():
        top_users = db.session.query(
            User.UserName,
            db.func.count(Reservation.ID).label('booking_count')
        ).join(Reservation).group_by(User.UserID).order_by(
            db.func.count(Reservation.ID).desc()
        ).limit(10).all()
        
        print("前10名用户预订排名:")
        for i, user in enumerate(top_users, 1):
            print(f"  {i}. {user.UserName}: {user.booking_count}次预订")

def check_room_capacity():
    """检查会议室容量分布"""
    print("\n=== 会议室容量分布检查 ===")
    
    with app.app_context():
        rooms = Room.query.all()
        
        small_rooms = [r for r in rooms if r.Capacity <= 8]
        medium_rooms = [r for r in rooms if 8 < r.Capacity < 16]
        large_rooms = [r for r in rooms if r.Capacity >= 16]
        
        print(f"小型会议室(≤8人): {len(small_rooms)}个")
        print(f"中型会议室(9-15人): {len(medium_rooms)}个")
        print(f"大型会议室(≥16人): {len(large_rooms)}个")
        
        # 显示每个会议室的详情
        print("\n所有会议室容量详情:")
        for room in rooms:
            category = "小型" if room.Capacity <= 8 else ("中型" if room.Capacity < 16 else "大型")
            print(f"  {room.RoomName}: {room.Capacity}人 ({category})")

def main():
    print("开始数据统计调试...")
    
    if not check_database_connection():
        return
    
    check_basic_statistics()
    check_duration_calculation()
    check_room_usage()
    check_daily_bookings()
    check_top_users()
    check_room_capacity()
    
    print("\n调试完成！")

if __name__ == '__main__':
    main()
