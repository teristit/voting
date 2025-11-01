"""
Telegram Bot для системы "Умная премия"

Основной модуль бота, обрабатывающий команды и взаимодействие с пользователями.
Интегрируется с Django через ORM и API.
"""

import logging
import asyncio
from typing import Dict, List, Optional

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    WebAppInfo,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from django.conf import settings
from django.contrib.auth import get_user_model
from apps.users.models import User
from apps.sessions.models import VotingSession
from apps.telegram_bot.models import TelegramUser, BotMessage
from apps.telegram_bot.services import (
    TelegramUserService,
    VotingNotificationService,
    WebAppAuthService
)
from apps.core.utils import get_logger

logger = get_logger(__name__)
User = get_user_model()


class SmartAwardBot:
    """
    Основной класс Telegram бота для системы "Умная премия"
    """
    
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.webapp_url = getattr(settings, 'TELEGRAM_WEBAPP_URL', 'https://your-domain.com/webapp')
        self.user_service = TelegramUserService()
        self.notification_service = VotingNotificationService()
        self.auth_service = WebAppAuthService()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обработчик команды /start
        """
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        try:
            # Регистрируем или обновляем пользователя
            telegram_user = await self.user_service.get_or_create_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                chat_id=chat_id
            )
            
            # Проверяем, есть ли пользователь в системе голосования
            system_user = await self.user_service.get_system_user(telegram_user)
            
            if system_user:
                welcome_text = (
                    f"👋 Добро пожаловать в систему \"Умная премия\", {user.first_name}!\n\n"
                    f"📊 Ваш статус: {system_user.get_role_display()}\n"
                    f"🎯 Активных сессий: {await self._get_active_sessions_count()}\n\n"
                    "Выберите действие:"
                )
            else:
                welcome_text = (
                    f"👋 Привет, {user.first_name}!\n\n"
                    "❌ Вы не зарегистрированы в системе \"Умная премия\".\n"
                    "📞 Обратитесь к администратору для получения доступа."
                )
            
            keyboard = await self._get_main_keyboard(system_user)
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            # Логируем взаимодействие
            await self._log_bot_interaction(
                telegram_user=telegram_user,
                action='start_command',
                details={'has_system_access': bool(system_user)}
            )
            
        except Exception as e:
            logger.error(f"Error in start_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Произошла ошибка. Попробуйте позже или обратитесь к администратору."
            )
    
    async def vote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обработчик команды /vote - открытие WebApp для голосования
        """
        user = update.effective_user
        
        try:
            telegram_user = await self.user_service.get_telegram_user(user.id)
            if not telegram_user:
                await update.message.reply_text(
                    "❌ Пользователь не найден. Выполните команду /start"
                )
                return
            
            system_user = await self.user_service.get_system_user(telegram_user)
            if not system_user or not system_user.active:
                await update.message.reply_text(
                    "❌ У вас нет доступа к системе голосования."
                )
                return
            
            # Получаем активную сессию
            active_session = await self._get_current_session()
            if not active_session:
                await update.message.reply_text(
                    "📅 В данный момент нет активных сессий голосования.\n"
                    "Ожидайте начала следующей сессии."
                )
                return
            
            # Проверяем, может ли пользователь голосовать
            can_vote = await self._can_user_vote(system_user, active_session)
            if not can_vote:
                await update.message.reply_text(
                    "⚠️ Вы не можете участвовать в текущем голосовании.\n"
                    "Возможные причины: отпуск, больничный или исключение из сессии."
                )
                return
            
            # Создаем кнопку для запуска WebApp
            webapp = WebAppInfo(url=f"{self.webapp_url}?session_id={active_session.id}")
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🗳️ Открыть голосование",
                    web_app=webapp
                )
            ]])
            
            session_info = (
                f"🗳️ **Сессия голосования #{active_session.id}**\n"
                f"📅 Период: {active_session.start_date.strftime('%d.%m.%Y')} - "
                f"{active_session.end_date.strftime('%d.%m.%Y')}\n"
                f"👥 Участников: {await self._get_session_participants_count(active_session)}\n"
                f"✅ Проголосовало: {await self._get_voted_count(active_session)}\n\n"
                "Нажмите кнопку ниже для открытия формы голосования:"
            )
            
            await update.message.reply_text(
                session_info,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in vote_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Произошла ошибка при открытии голосования. Попробуйте позже."
            )
    
    async def results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обработчик команды /results - показ результатов пользователя
        """
        user = update.effective_user
        
        try:
            telegram_user = await self.user_service.get_telegram_user(user.id)
            if not telegram_user:
                await update.message.reply_text(
                    "❌ Пользователь не найден. Выполните команду /start"
                )
                return
            
            system_user = await self.user_service.get_system_user(telegram_user)
            if not system_user:
                await update.message.reply_text(
                    "❌ У вас нет доступа к системе."
                )
                return
            
            # Получаем последние результаты пользователя
            user_results = await self._get_user_latest_results(system_user)
            
            if not user_results:
                await update.message.reply_text(
                    "📊 У вас пока нет результатов голосований.\n"
                    "Примите участие в голосовании, чтобы увидеть результаты."
                )
                return
            
            results_text = (
                f"📊 **Ваши результаты (сессия #{user_results.session.id})**\n\n"
                f"⭐ Средний балл: **{user_results.average_score:.2f}**\n"
                f"🏆 Место: **{user_results.rank}**\n"
                f"💰 Премия: **{user_results.total_bonus:.2f} ₽**\n"
                f"👥 Голосов получено: **{user_results.votes_received}**\n\n"
                f"📅 Период: {user_results.session.start_date.strftime('%d.%m.%Y')} - "
                f"{user_results.session.end_date.strftime('%d.%m.%Y')}"
            )
            
            # Добавляем кнопку для детального просмотра в WebApp
            webapp = WebAppInfo(url=f"{self.webapp_url}/results")
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "📈 Подробные результаты",
                    web_app=webapp
                )
            ]])
            
            await update.message.reply_text(
                results_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in results_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Произошла ошибка при получении результатов. Попробуйте позже."
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обработчик команды /help
        """
        help_text = (
            "🤖 **Бот системы \"Умная премия\"**\n\n"
            "**Доступные команды:**\n"
            "/start - Главное меню\n"
            "/vote - Открыть голосование\n"
            "/results - Посмотреть результаты\n"
            "/help - Справка\n\n"
            "**О системе:**\n"
            "Система \"Умная премия\" позволяет сотрудникам еженедельно "
            "оценивать работу коллег по шкале от 0 до 10 баллов. "
            "На основе полученных оценок автоматически рассчитывается "
            "размер индивидуальной премии для каждого участника.\n\n"
            "**Поддержка:**\n"
            "📧 admin@company.com\n"
            "📞 +7 (xxx) xxx-xx-xx"
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown'
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обработчик нажатий на inline кнопки
        """
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = query.from_user
        
        try:
            if data == 'current_session':
                await self._handle_current_session_callback(query, user)
            elif data == 'my_results':
                await self._handle_my_results_callback(query, user)
            elif data == 'help':
                await self._handle_help_callback(query)
            elif data.startswith('session_'):
                session_id = int(data.split('_')[1])
                await self._handle_session_details_callback(query, user, session_id)
                
        except Exception as e:
            logger.error(f"Error in button_callback: {e}", exc_info=True)
            await query.edit_message_text(
                "❌ Произошла ошибка. Попробуйте позже."
            )
    
    async def _get_main_keyboard(self, system_user: Optional[User]) -> InlineKeyboardMarkup:
        """
        Создает главную клавиатуру в зависимости от статуса пользователя
        """
        if not system_user:
            return InlineKeyboardMarkup([[
                InlineKeyboardButton("ℹ️ Справка", callback_data='help')
            ]])
        
        keyboard = []
        
        # Кнопка голосования для активных пользователей
        if system_user.active:
            active_session = await self._get_current_session()
            if active_session:
                can_vote = await self._can_user_vote(system_user, active_session)
                if can_vote:
                    webapp = WebAppInfo(url=f"{self.webapp_url}?session_id={active_session.id}")
                    keyboard.append([
                        InlineKeyboardButton("🗳️ Голосовать", web_app=webapp)
                    ])
        
        # Кнопки для всех пользователей системы
        keyboard.extend([
            [InlineKeyboardButton("📊 Текущая сессия", callback_data='current_session')],
            [InlineKeyboardButton("📈 Мои результаты", callback_data='my_results')],
            [InlineKeyboardButton("ℹ️ Справка", callback_data='help')]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    # Вспомогательные методы
    async def _get_active_sessions_count(self) -> int:
        """Получает количество активных сессий"""
        from apps.sessions.models import VotingSession
        return await VotingSession.objects.filter(active=True).acount()
    
    async def _get_current_session(self) -> Optional[VotingSession]:
        """Получает текущую активную сессию"""
        from apps.sessions.models import VotingSession
        from django.utils import timezone
        
        try:
            return await VotingSession.objects.filter(
                active=True,
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date()
            ).afirst()
        except VotingSession.DoesNotExist:
            return None
    
    async def _can_user_vote(self, user: User, session: VotingSession) -> bool:
        """Проверяет, может ли пользователь голосовать в сессии"""
        from apps.sessions.models import SessionParticipant
        
        try:
            participant = await SessionParticipant.objects.aget(
                session=session,
                user=user
            )
            return participant.can_vote and participant.status == 'active'
        except SessionParticipant.DoesNotExist:
            return False
    
    async def _get_session_participants_count(self, session: VotingSession) -> int:
        """Получает количество участников сессии"""
        return await session.participants.acount()
    
    async def _get_voted_count(self, session: VotingSession) -> int:
        """Получает количество проголосовавших в сессии"""
        from apps.voting.models import Vote
        
        return await Vote.objects.filter(
            session=session
        ).values('voter').distinct().acount()
    
    async def _get_user_latest_results(self, user: User):
        """Получает последние результаты пользователя"""
        from apps.results.models import SessionResult
        
        try:
            return await SessionResult.objects.select_related('session').filter(
                user=user
            ).order_by('-session__end_date').afirst()
        except SessionResult.DoesNotExist:
            return None
    
    async def _log_bot_interaction(self, telegram_user, action: str, details: Dict = None):
        """Логирует взаимодействие с ботом"""
        try:
            await BotMessage.objects.acreate(
                telegram_user=telegram_user,
                message_type='command',
                content=action,
                metadata=details or {}
            )
        except Exception as e:
            logger.error(f"Failed to log bot interaction: {e}")
    
    # Callback handlers
    async def _handle_current_session_callback(self, query, user):
        """Обработчик кнопки 'Текущая сессия'"""
        session = await self._get_current_session()
        if not session:
            await query.edit_message_text(
                "📅 В данный момент нет активных сессий голосования."
            )
            return
        
        participants_count = await self._get_session_participants_count(session)
        voted_count = await self._get_voted_count(session)
        participation_rate = (voted_count / participants_count * 100) if participants_count > 0 else 0
        
        session_text = (
            f"📊 **Текущая сессия #{session.id}**\n\n"
            f"📅 Период: {session.start_date.strftime('%d.%m.%Y')} - "
            f"{session.end_date.strftime('%d.%m.%Y')}\n"
            f"👥 Участников: {participants_count}\n"
            f"✅ Проголосовало: {voted_count}\n"
            f"📈 Участие: {participation_rate:.1f}%\n\n"
        )
        
        if session.active:
            webapp = WebAppInfo(url=f"{self.webapp_url}?session_id={session.id}")
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🗳️ Участвовать", web_app=webapp)
            ]])
        else:
            keyboard = None
        
        await query.edit_message_text(
            session_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _handle_my_results_callback(self, query, user):
        """Обработчик кнопки 'Мои результаты'"""
        telegram_user = await self.user_service.get_telegram_user(user.id)
        system_user = await self.user_service.get_system_user(telegram_user)
        
        if not system_user:
            await query.edit_message_text(
                "❌ У вас нет доступа к системе."
            )
            return
        
        results = await self._get_user_latest_results(system_user)
        if not results:
            await query.edit_message_text(
                "📊 У вас пока нет результатов голосований."
            )
            return
        
        results_text = (
            f"📊 **Ваши результаты**\n\n"
            f"⭐ Средний балл: **{results.average_score:.2f}**\n"
            f"🏆 Место: **{results.rank}**\n"
            f"💰 Премия: **{results.total_bonus:.2f} ₽**\n"
            f"👥 Голосов: **{results.votes_received}**"
        )
        
        webapp = WebAppInfo(url=f"{self.webapp_url}/results")
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📈 Подробнее", web_app=webapp)
        ]])
        
        await query.edit_message_text(
            results_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _handle_help_callback(self, query):
        """Обработчик кнопки 'Справка'"""
        help_text = (
            "🤖 **Справка по боту**\n\n"
            "Этот бот является частью системы \"Умная премия\" - "
            "внутренней системы для еженедельного взаимного оценивания "
            "сотрудников и автоматического расчета премий.\n\n"
            "**Как это работает:**\n"
            "1️⃣ Каждую неделю открывается сессия голосования\n"
            "2️⃣ Сотрудники оценивают коллег по шкале 0-10\n"
            "3️⃣ Система рассчитывает средние баллы и премии\n"
            "4️⃣ Результаты доступны после завершения сессии\n\n"
            "**Команды:**\n"
            "/start - Главное меню\n"
            "/vote - Голосование\n"
            "/results - Результаты\n"
            "/help - Эта справка"
        )
        
        await query.edit_message_text(
            help_text,
            parse_mode='Markdown'
        )


def create_bot_application() -> Application:
    """
    Создает и настраивает приложение Telegram бота
    """
    bot = SmartAwardBot()
    
    # Создаем приложение
    application = Application.builder().token(bot.token).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("vote", bot.vote_command))
    application.add_handler(CommandHandler("results", bot.results_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(bot.button_callback))
    
    # Обработчик неизвестных команд
    async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "❓ Неизвестная команда. Используйте /help для просмотра доступных команд."
        )
    
    application.add_handler(MessageHandler(
        filters.COMMAND & ~filters.COMMAND_REGEX(r"^/(start|vote|results|help)$"),
        unknown_command
    ))
    
    return application


async def set_bot_commands(application: Application):
    """
    Устанавливает команды бота в меню Telegram
    """
    commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("vote", "Открыть голосование"),
        BotCommand("results", "Посмотреть результаты"),
        BotCommand("help", "Справка")
    ]
    
    await application.bot.set_my_commands(commands)