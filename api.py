import jwt
from flask import Blueprint, jsonify, request
from functools import wraps
from flask_login import current_user
from datetime import datetime, timedelta
from app import app, db, User, Room, Reservation

# 创建API蓝图
api = Blueprint('api', __name__, url_prefix='/api')

# JWT密钥
JWT_SECRET = app.config['SECRET_KEY']

# JWT验证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头中获取token
        if 'Authorization' in request.headers:
            auth = request.headers['Authorization']
            if auth.startswith('Bearer '):
                token = auth.split(' ')[1]
        
        if not token:
            return jsonify({'message': '缺少认证令牌!'}), 401
        
        try:
            # 验证JWT令牌
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = User.query.filter_by(UserID=data['user_id']).first()
            if not current_user:
                return jsonify({'message': '无效的用户令牌!'}), 401
        except:
            return jsonify({'message': '令牌无效或已过期!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# 用户认证接口
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '请提供用户名和密码!'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter((User.UserName == username) | (User.Email == username)).first()
    
    if not user or not user.check_password(password):
        return jsonify({'message': '用户名或密码错误!'}), 401
    
    if user.Email and not user.EmailVerified:
        return jsonify({'message': '请先验证您的邮箱!'}), 401
    
    # 生成JWT令牌，有效期1天
    token = jwt.encode({
        'user_id': user.UserID,
        'username': user.UserName,
        'role': user.Role,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, JWT_SECRET, algorithm="HS256")
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.UserID,
            'username': user.UserName,
            'email': user.Email,
            'role': user.Role
        }
    }), 200

# 获取用户信息接口
@api.route('/user', methods=['GET'])
@token_required
def get_user_info(current_user):
    return jsonify({
        'user': {
            'id': current_user.UserID,
            'username': current_user.UserName,
            'email': current_user.Email,
            'phone': current_user.Phone,
            'role': current_user.Role
        }
    }), 200

# 获取所有会议室接口
@api.route('/rooms', methods=['GET'])
@token_required
def get_rooms(current_user):
    rooms = Room.query.all()
    result = []
    
    for room in rooms:
        result.append({
            'id': room.RoomID,
            'name': room.RoomName,
            'capacity': room.Capacity,
            'equipment': room.Equipment,
            'status': room.Status
        })
    
    return jsonify({'rooms': result}), 200

# 获取单个会议室详情
@api.route('/rooms/<int:room_id>', methods=['GET'])
@token_required
def get_room(current_user, room_id):
    room = db.get_or_404(Room, room_id)
    return jsonify({
        'room': {
            'id': room.RoomID,
            'name': room.RoomName,
            'capacity': room.Capacity,
            'equipment': room.Equipment,
            'status': room.Status
        }
    }), 200

# 获取当前用户的预订
@api.route('/my-reservations', methods=['GET'])
@token_required
def get_my_reservations(current_user):
    reservations = Reservation.query.filter_by(UserID=current_user.UserID)\
                   .order_by(Reservation.StartTime.desc()).all()
    result = []
    
    for res in reservations:
        room = db.session.get(Room, res.RoomID)
        result.append({
            'id': res.ID,
            'room': {
                'id': room.RoomID,
                'name': room.RoomName
            },
            'title': res.Title,
            'start_time': res.StartTime.strftime('%Y-%m-%d %H:%M'),
            'end_time': res.EndTime.strftime('%Y-%m-%d %H:%M'),
            'status': res.Status,
            'purpose': res.Purpose,
            'attendees': res.Attendees
        })
    
    return jsonify({'reservations': result}), 200

# 创建预订
@api.route('/reservations', methods=['POST'])
@token_required
def create_reservation(current_user):
    data = request.get_json()
    
    if not all(key in data for key in ['room_id', 'title', 'start_time', 'end_time']):
        return jsonify({'message': '缺少必要的参数!'}), 400
    
    room_id = data['room_id']
    title = data['title']
    start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M')
    end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M')
    purpose = data.get('purpose', '')
    attendees = data.get('attendees', 1)
    
    # 验证参数
    if start_time >= end_time:
        return jsonify({'message': '开始时间必须早于结束时间!'}), 400
    
    # 检查会议室是否存在
    room = db.session.get(Room, room_id)
    if not room:
        return jsonify({'message': '会议室不存在!'}), 404
    
    # 检查会议室容量
    if attendees > room.Capacity:
        return jsonify({
            'message': f'参会人数超过会议室容量（最大容量：{room.Capacity}人）!'
        }), 400
    
    # 检查会议室是否可用
    from app import check_room_availability
    is_available, message = check_room_availability(room_id, start_time, end_time)
    if not is_available:
        return jsonify({'message': message}), 400
    
    # 创建预订
    try:
        reservation = Reservation(
            RoomID=room_id,
            UserID=current_user.UserID,
            StartTime=start_time,
            EndTime=end_time,
            Status='Pending',
            Title=title,
            Purpose=purpose,
            Attendees=attendees
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'message': '预订成功!',
            'reservation': {
                'id': reservation.ID,
                'room_id': reservation.RoomID,
                'title': reservation.Title,
                'start_time': reservation.StartTime.strftime('%Y-%m-%d %H:%M'),
                'end_time': reservation.EndTime.strftime('%Y-%m-%d %H:%M'),
                'status': reservation.Status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'预订失败: {str(e)}!'}), 500

# 取消预订
@api.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@token_required
def cancel_reservation(current_user, reservation_id):
    reservation = db.get_or_404(Reservation, reservation_id)
    
    # 检查权限
    if reservation.UserID != current_user.UserID and current_user.Role != 'admin':
        return jsonify({'message': '无权取消此预订!'}), 403
    
    try:
        db.session.delete(reservation)
        db.session.commit()
        return jsonify({'message': '预订已取消!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'取消预订失败: {str(e)}!'}), 500

# 注册API蓝图
def register_api(app):
    app.register_blueprint(api)
