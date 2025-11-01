"""
Telegram Bot для системы "Smart Award" БЕЗ WebApp

Простой бот с командами для голосования через сообщения.
Никаких WebApp, только клавиатуры и текст.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.sessions.models import VotingSession, SessionParticipant
from apps.voting.models import Vote
from apps.results.models import SessionResult
from apps.core.utils import get_logger

logger = get_logger('telegram_bot')
User = get_user_model()

# Состояния для ConversationHandler
SELECTING_TARGET, ENTERING_SCORE = range(2)


class SmartAwardBot:
    """
    Основной класс Telegram бота без WebApp
    """
    
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Команда /start - регистрация/приветствие
        """
        user = update.effective_user
        
        try:
            # Получаем или создаём пользователя
            system_user = await self._get_or_register_user(user)
            
            if system_user and system_user.is_active:
                welcome_text = (
                    f"👋 Добро пожаловать, {system_user.get_display_name()}!\n\n"
                    f"🏆 Система \"Умная премия\"\n"
                    f"📋 Роль: {system_user.get_role_display()}\n"
                    f"🔄 Статус: {system_user.get_status_display()}\n\n"
                    "Используйте команды:"
                )
            else:
                welcome_text = (
                    f"👋 Привет, {user.first_name}!\n\n"
                    "❌ Вы не зарегистрированы в системе \"Умная премия\".\n"
                    f"🔑 Ваш Telegram ID: `{user.id}`\n\n"
                    "📞 Обратитесь к администратору для получения доступа."
                )
            
            keyboard = self._get_main_keyboard(system_user)
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in start_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Произошла ошибка. Попробуйте позже."
            )
    
    async def vote_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начало процесса голосования
        """
        user = update.effective_user
        
        try:
            system_user = await self._get_system_user(user.id)
            if not system_user or not system_user.is_voting_eligible():
                await update.message.reply_text(
                    "❌ У вас нет прав на голосование."
                )
                return ConversationHandler.END
            
            session = await self._get_current_session()
            if not session:
                await update.message.reply_text(
                    "📅 Сейчас нет активных сессий голосования."
                )
                return ConversationHandler.END
            
            # Получаем список доступных для голосования
            targets = await self._get_vote_targets(session, system_user)
            if not targets:
                await update.message.reply_text(
                    "❌ Нет доступных кандидатов для голосования."
                )
                return ConversationHandler.END
            
            # Сохраняем сессию и кандидатов
            context.user_data['session'] = session
            context.user_data['targets'] = targets
            context.user_data['current_votes'] = {}
            
            # Создаём клавиатуру с кандидатами
            keyboard = self._create_targets_keyboard(targets)
            
            await update.message.reply_text(
                f"🗳️ Голосование в сессии #{session.id}\n"
                f"📅 Период: {session.start_date} - {session.end_date}\n\n"
                "Выберите коллегу для оценки:",
                reply_markup=keyboard
            )
            
            return SELECTING_TARGET
            
        except Exception as e:
            logger.error(f"Error in vote_start: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Ошибка при запуске голосования."
            )
            return ConversationHandler.END
    
    async def target_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Пользователь выбрал коллегу для оценки
        """
        query = update.callback_query
        await query.answer()
        
        target_id = int(query.data.split('_')[1])
        targets = context.user_data.get('targets', [])
        
        # Находим выбранного кандидата
        selected_target = None
        for target in targets:
            if target.id == target_id:
                selected_target = target
                break
        
        if not selected_target:
            await query.edit_message_text(
                "❌ Кандидат не найден. Попробуйте снова: /vote"
            )
            return ConversationHandler.END
        
        context.user_data['selected_target'] = selected_target
        
        # Клавиатура для выбора оценки (0-10)
        keyboard = []
        for i in range(0, 11):
            if i % 5 == 0:  # Новая строка каждые 5 кнопок
                keyboard.append([])
            keyboard[-1].append(
                InlineKeyboardButton(str(i), callback_data=f"score_{i}")
            )
        
        # Кнопка отмены
        keyboard.append([InlineKeyboardButton("❌ Отменить", callback_data="cancel")])
        
        await query.edit_message_text(
            f"🎯 Оцените работу:\n"
            f"👤 **{selected_target.get_display_name()}**\n"
            f"🏢 {selected_target.position or 'Не указана'}\n\n"
            "🔢 Выберите оценку (0-10):",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        return ENTERING_SCORE
    
    async def score_entered(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Пользователь выбрал оценку
        """
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "cancel":
            await query.edit_message_text(
                "❌ Голосование отменено. Начните снова: /vote"
            )
            return ConversationHandler.END
        
        try:
            score = int(data.split('_')[1])
            session = context.user_data['session']
            target = context.user_data['selected_target']
            
            # Сохраняем голос
            system_user = await self._get_system_user(update.effective_user.id)
            vote_saved = await self._save_vote(session, system_user, target, score)
            
            if vote_saved:
                # Обновляем список текущих голосов
                context.user_data['current_votes'][target.id] = score
                
                # Показываем статус и предлагаем продолжить
                remaining_targets = [t for t in context.user_data['targets'] if t.id not in context.user_data['current_votes']]
                
                success_text = (
                    f"✅ Голос сохранён!\n"
                    f"👤 {target.get_display_name()}: **{score}** баллов\n\n"
                )
                
                if remaining_targets:
                    success_text += (
                        f"📋 Осталось оценить: {len(remaining_targets)} чел.\n"
                        "Продолжаем?"
                    )
                    
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("➡️ Продолжить", callback_data="continue_voting")],
                        [InlineKeyboardButton("✅ Завершить", callback_data="finish_voting")]
                    ])
                else:
                    success_text += "✅ Все голоса отданы!"
                    keyboard = None
                
                await query.edit_message_text(
                    success_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
                if not remaining_targets:
                    return ConversationHandler.END
                
            else:
                await query.edit_message_text(
                    "❌ Ошибка при сохранении голоса."
                )
                return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error saving vote: {e}", exc_info=True)
            await query.edit_message_text(
                "❌ Ошибка при сохранении голоса."
            )
            return ConversationHandler.END
        
        return SELECTING_TARGET
    
    async def continue_or_finish(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработка кнопок "Продолжить" и "Завершить"
        """
        query = update.callback_query
        await query.answer()
        
        if query.data == "continue_voting":
            # Показываем оставшихся кандидатов
            targets = context.user_data.get('targets', [])
            current_votes = context.user_data.get('current_votes', {})
            remaining_targets = [t for t in targets if t.id not in current_votes]
            
            if remaining_targets:
                keyboard = self._create_targets_keyboard(remaining_targets)
                await query.edit_message_text(
                    f"📋 Осталось оценить: {len(remaining_targets)}\n"
                    "Выберите следующего коллегу:",
                    reply_markup=keyboard
                )
                return SELECTING_TARGET
            else:
                await query.edit_message_text(
                    "✅ Все голоса отданы!"
                )
                return ConversationHandler.END
        
        elif query.data == "finish_voting":
            current_votes = context.user_data.get('current_votes', {})
            await query.edit_message_text(
                f"✅ Голосование завершено!\n"
                f"Вы оценили: **{len(current_votes)}** коллег\n\n"
                "Используйте /results для просмотра результатов.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        return ConversationHandler.END
    
    async def results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Команда /results - показ результатов
        """
        user = update.effective_user
        
        try:
            system_user = await self._get_system_user(user.id)
            if not system_user:
                await update.message.reply_text(
                    "❌ Вы не зарегистрированы в системе."
                )
                return
            
            # Получаем последние результаты
            latest_result = await self._get_user_latest_result(system_user)
            
            if not latest_result:
                await update.message.reply_text(
                    "📊 У вас пока нет результатов.\n"
                    "Примите участие в голосовании: /vote"
                )
                return
            
            results_text = (
                f"📊 **Ваши результаты**\n\n"
                f"📅 Сессия: {latest_result.session.start_date} - {latest_result.session.end_date}\n"
                f"⭐ Средний балл: **{latest_result.average_score:.2f}**\n"
                f"🏆 Место: **{latest_result.rank or 'Не рассчитано'}**\n"
                f"💰 Премия: **{latest_result.bonus_amount:.2f} ₽**\n"
                f"👥 Голосов: **{latest_result.votes_received}**\n\n"
            )
            
            # Показываем последние 5 результатов
            all_results = await self._get_user_results_history(system_user, limit=5)
            if len(all_results) > 1:
                results_text += "📈 **Последние результаты:**\n"
                for i, result in enumerate(all_results[:5], 1):
                    results_text += (
                        f"{i}. {result.session.start_date.strftime('%d.%m')}: "
                        f"{result.average_score:.1f} б. (место {result.rank or '?'})\n"
                    )
            
            await update.message.reply_text(
                results_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in results_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Ошибка при получении результатов."
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Команда /help - справка
        """
        help_text = (
            "🤖 **Бот системы \"Умная премия\"**\n\n"
            "📝 **Команды:**\n"
            "/start - Главное меню\n"
            "/vote - Начать голосование\n"
            "/results - Посмотреть результаты\n"
            "/status - Статус сессии\n"
            "/help - Эта справка\n\n"
            "🎯 **Как голосовать:**\n"
            "1. Напишите /vote\n"
            "2. Выберите коллегу\n"
            "3. Поставьте оценку 0-10\n"
            "4. Повторите для других\n\n"
            "📈 Премии рассчитываются автоматически после завершения сессии."
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Команда /status - статус сессии
        """
        user = update.effective_user
        
        try:
            system_user = await self._get_system_user(user.id)
            if not system_user:
                await update.message.reply_text(
                    "❌ Вы не зарегистрированы в системе."
                )
                return
            
            session = await self._get_current_session()
            
            if not session:
                await update.message.reply_text(
                    "📅 В данный момент нет активных сессий."
                )
                return
            
            participants_count = session.get_participants_count()
            voters_count = session.get_voters_count()
            user_voted = await self._has_user_voted(session, system_user)
            
            status_text = (
                f"📊 **Статус сессии #{session.id}**\n\n"
                f"📅 Период: {session.start_date} - {session.end_date}\n"
                f"👥 Участников: {participants_count}\n"
                f"✅ Проголосовало: {voters_count}\n"
                f"📈 Участие: {session.get_participation_rate():.1f}%\n\n"
                f"🔄 Ваш статус: {'\u2705 Проголосовали' if user_voted else '❌ Не голосовали'}\n\n"
            )
            
            if not user_voted and session.can_vote_today():
                status_text += "🗳️ Можно голосовать: /vote"
            elif session.closed_at:
                status_text += "🔒 Сессия завершена. Результаты: /results"
            else:
                status_text += "⏳ Ожидаем завершения сессии..."
            
            await update.message.reply_text(
                status_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in status_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Ошибка при получении статуса."
            )
    
    def cancel_voting(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Отмена голосования
        """
        update.message.reply_text(
            "❌ Голосование отменено."
        )
        return ConversationHandler.END
    
    # Вспомогательные методы
    
    async def _get_or_register_user(self, telegram_user):
        """Получает или создаёт пользователя по telegram_id"""
        try:
            user, created = await User.objects.aget_or_create(
                telegram_id=telegram_user.id,
                defaults={
                    'username': telegram_user.username or f'user_{telegram_user.id}',
                    'first_name': telegram_user.first_name or '',
                    'last_name': telegram_user.last_name or '',
                    'telegram_username': telegram_user.username or '',
                    'is_active': False,  # По умолчанию неактивен, пока не одобрит админ
                }
            )
            if created:
                logger.info(f"New user registered: {telegram_user.id} - {telegram_user.username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}", exc_info=True)
            return None
    
    async def _get_system_user(self, telegram_id: int):
        """Получает пользователя по telegram_id"""
        try:
            return await User.objects.aget(telegram_id=telegram_id)
        except User.DoesNotExist:
            return None
    
    async def _get_current_session(self):
        """Получает текущую активную сессию"""
        today = timezone.now().date()
        try:
            return await VotingSession.objects.filter(
                active=True,
                start_date__lte=today,
                end_date__gte=today
            ).afirst()
        except Exception:
            return None
    
    async def _get_vote_targets(self, session: VotingSession, voter: User):
        """Получает список кандидатов для голосования"""
        # Все участники, кроме самого голосующего
        participants = SessionParticipant.objects.filter(
            session=session,
            can_receive_votes=True,
            participant_status='active'
        ).select_related('user').exclude(user=voter)
        
        targets = []
        async for participant in participants:
            if participant.user.can_be_voted_for():
                targets.append(participant.user)
        
        return targets
    
    async def _save_vote(self, session, voter, target, score):
        """Сохраняет голос"""
        try:
            vote, created = await Vote.objects.aupdate_or_create(
                session=session,
                voter=voter,
                target=target,
                defaults={'score': score}
            )
            
            # Обновляем дату последнего голосования
            voter.last_vote_date = timezone.now()
            await voter.asave(update_fields=['last_vote_date'])
            
            logger.info(f"Vote saved: {voter.id} -> {target.id} = {score} (created: {created})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vote: {e}", exc_info=True)
            return False
    
    async def _has_user_voted(self, session, user):
        """Проверяет, голосовал ли пользователь"""
        return await Vote.objects.filter(session=session, voter=user).aexists()
    
    async def _get_user_latest_result(self, user):
        """Получает последние результаты пользователя"""
        try:
            return await SessionResult.objects.select_related('session').filter(
                user=user
            ).order_by('-session__end_date').afirst()
        except Exception:
            return None
    
    async def _get_user_results_history(self, user, limit=5):
        """Получает историю результатов"""
        results = []
        async for result in SessionResult.objects.select_related('session').filter(
            user=user
        ).order_by('-session__end_date')[:limit]:
            results.append(result)
        return results
    
    def _get_main_keyboard(self, system_user):
        """Создаёт основную клавиатуру"""
        if not system_user or not system_user.is_active:
            return None
        
        keyboard = [
            [KeyboardButton("🗳️ Голосовать"), KeyboardButton("📊 Статус")],
            [KeyboardButton("📈 Результаты"), KeyboardButton("❓ Помощь")]
        ]
        
        return ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )
    
    def _create_targets_keyboard(self, targets):
        """Создаёт клавиатуру с кандидатами"""
        keyboard = []
        
        for target in targets:
            display_name = target.get_display_name()
            if target.position:
                display_name += f" ({target.position})"
            
            keyboard.append([InlineKeyboardButton(
                display_name,
                callback_data=f"target_{target.id}"
            )])
        
        # Кнопка отмены
        keyboard.append([InlineKeyboardButton(
            "❌ Отменить",
            callback_data="cancel"
        )])
        
        return InlineKeyboardMarkup(keyboard)


def create_bot_application() -> Application:
    """
    Создаёт и настраивает Telegram бота
    """
    bot = SmartAwardBot()
    application = Application.builder().token(bot.token).build()
    
    # ConversationHandler для голосования
    vote_handler = ConversationHandler(
        entry_points=[
            CommandHandler('vote', bot.vote_start),
            MessageHandler(filters.Regex(r'^🗳️ Голосовать$'), bot.vote_start)
        ],
        states={
            SELECTING_TARGET: [
                CallbackQueryHandler(bot.target_selected, pattern=r'^target_\d+$')
            ],
            ENTERING_SCORE: [
                CallbackQueryHandler(bot.score_entered, pattern=r'^score_\d+$'),
                CallbackQueryHandler(bot.continue_or_finish, pattern=r'^(continue_voting|finish_voting)$')
            ],
        },
        fallbacks=[
            CommandHandler('cancel', bot.cancel_voting),
            CallbackQueryHandler(bot.cancel_voting, pattern='^cancel$')
        ]
    )
    
    # Регистрируем обработчики
    application.add_handler(vote_handler)
    application.add_handler(CommandHandler('start', bot.start_command))
    application.add_handler(CommandHandler('results', bot.results_command))
    application.add_handler(CommandHandler('status', bot.status_command))
    application.add_handler(CommandHandler('help', bot.help_command))
    
    # Обработчики кнопок клавиатуры
    application.add_handler(MessageHandler(
        filters.Regex(r'^📊 Статус$'), 
        bot.status_command
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^📈 Результаты$'), 
        bot.results_command
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^❓ Помощь$'), 
        bot.help_command
    ))
    
    # Обработчик неизвестных сообщений
    async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "❓ Непонятное сообщение.\n"
            "Используйте /help для просмотра команд."
        )
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        unknown_message
    ))
    
    return application


async def set_bot_commands(application: Application):
    """
    Устанавливает меню команд бота
    """
    commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("vote", "Начать голосование"),
        BotCommand("results", "Мои результаты"),
        BotCommand("status", "Статус сессии"),
        BotCommand("help", "Справка")
    ]
    
    await application.bot.set_my_commands(commands)