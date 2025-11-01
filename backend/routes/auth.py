from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from extensions import db
from models.user import User
from models.auth import AuthSession, RevokedToken
from utils.telegram_auth import validate_telegram_init_data, extract_user_from_init_data
from services.audit_service import log_action
import hashlib

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/telegram", methods=["POST"])
def telegram_login():
    """
    Аутентификация через Telegram WebApp
    Обрабатывает POST /api/v1/auth/telegram
    """
    try:
        data = request.get_json() or {}
        init_data = data.get("init_data")
        
        if not init_data:
            return jsonify({
                "status": "error",
                "code": "MISSING_INIT_DATA",
                "message": "Отсутствуют данные аутентификации"
            }), 400
        
        # Проверяем подлинность данных Telegram
        bot_token = current_app.config.get("TELEGRAM_BOT_TOKEN")
        validated_data = validate_telegram_init_data(init_data, bot_token)
        
        if not validated_data:
            return jsonify({
                "status": "error",
                "code": "INVALID_TELEGRAM_DATA",
                "message": "Неверные данные Telegram"
            }), 401
        
        # Извлекаем информацию о пользователе
        user_info = extract_user_from_init_data(validated_data)
        
        if not user_info or not user_info.get('telegram_id'):
            return jsonify({
                "status": "error",
                "code": "INVALID_USER_DATA",
                "message": "Неверные данные пользователя"
            }), 401
        
        telegram_id = user_info['telegram_id']
        
        # Поиск или создание пользователя
        user = User.query.filter_by(telegram_id=telegram_id).first()
        
        if not user:
            # Создаем нового пользователя
            full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            if not full_name:
                full_name = user_info.get('username', f'User{telegram_id}')
                
            user = User(
                name=full_name,
                telegram_id=telegram_id,
                telegram_username=user_info.get('username'),
                role="user",
                active=True
            )
            
            db.session.add(user)
            db.session.commit()
            
            log_action(
                None, 
                "user_created", 
                {
                    "telegram_id": telegram_id,
                    "name": user.name,
                    "username": user.telegram_username
                }
            )
        else:
            # Обновляем данные пользователя
            full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            if full_name and full_name != user.name:
                user.name = full_name
                
            if user_info.get('username') and user_info['username'] != user.telegram_username:
                user.telegram_username = user_info['username']
                
            user.last_login = datetime.utcnow()
            db.session.commit()
        
        # Проверяем, что пользователь активен
        if not user.active:
            return jsonify({
                "status": "error",
                "code": "USER_DEACTIVATED",
                "message": "Пользователь деактивирован"
            }), 403
        
        # Создаем JWT токен
        access_token = create_access_token(
            identity=user.user_id,
            expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        )
        
        # Сохраняем сессию
        token_hash = hashlib.sha256(access_token.encode()).hexdigest()
        auth_session = AuthSession(
            user_id=user.user_id,
            token_hash=token_hash,
            device_info={
                "user_agent": request.headers.get("User-Agent"),
                "platform": "telegram_webapp"
            },
            ip_address=request.environ.get('REMOTE_ADDR'),
            expires_at=datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        )
        
        db.session.add(auth_session)
        db.session.commit()
        
        # Логируем вход
        log_action(
            user.user_id, 
            "user_login", 
            {
                "telegram_id": telegram_id,
                "platform": "telegram_webapp",
                "ip_address": request.environ.get('REMOTE_ADDR')
            }
        )
        
        return jsonify({
            "status": "success",
            "token": access_token,
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "role": user.role,
                "active": user.active,
                "telegram_username": user.telegram_username
            },
            "expires_in": int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in telegram_login: {str(e)}")
        return jsonify({
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": "Внутренняя ошибка сервера"
        }), 500


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Выход из системы
    Обрабатывает POST /api/v1/auth/logout
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Получаем токен из заголовка
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({
                "status": "error",
                "code": "INVALID_TOKEN_FORMAT",
                "message": "Неверный формат токена"
            }), 400
            
        token = auth_header.replace("Bearer ", "")
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Добавляем токен в черный список
        revoked_token = RevokedToken(
            token_hash=token_hash,
            user_id=current_user_id,
            reason="logout"
        )
        
        # Удаляем активную сессию
        auth_session = AuthSession.query.filter_by(
            user_id=current_user_id,
            token_hash=token_hash
        ).first()
        
        if auth_session:
            db.session.delete(auth_session)
        
        db.session.add(revoked_token)
        db.session.commit()
        
        # Логируем выход
        log_action(
            current_user_id, 
            "user_logout", 
            {
                "token_hash": token_hash[:16] + "...",  # Логируем только начало хэша
                "ip_address": request.environ.get('REMOTE_ADDR')
            }
        )
        
        return jsonify({
            "status": "success",
            "message": "Успешный выход из системы"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in logout: {str(e)}")
        return jsonify({
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": "Внутренняя ошибка сервера"
        }), 500


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    """
    Обновление токена доступа
    Обрабатывает POST /api/v1/auth/refresh
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Проверяем, что пользователь существует и активен
        user = User.query.filter_by(user_id=current_user_id, active=True).first()
        if not user:
            return jsonify({
                "status": "error",
                "code": "USER_NOT_FOUND",
                "message": "Пользователь не найден или неактивен"
            }), 401
        
        # Создаем новый токен
        new_access_token = create_access_token(
            identity=current_user_id,
            expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        )
        
        return jsonify({
            "status": "success",
            "token": new_access_token,
            "expires_in": int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in refresh_token: {str(e)}")
        return jsonify({
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": "Внутренняя ошибка сервера"
        }), 500
