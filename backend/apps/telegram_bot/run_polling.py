"""
Запуск Telegram-бота в режиме polling (без webhook)
"""

import asyncio
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_award.settings')
django.setup()

from .bot import create_bot_application, set_bot_commands  # noqa: E402


def main():
    application = create_bot_application()

    async def run():
        await set_bot_commands(application)
        await application.initialize()
        await application.start()
        try:
            await application.bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass
        await application.updater.start_polling(allowed_updates=application.bot.allowed_updates)
        await application.updater.idle()

    asyncio.run(run())


if __name__ == '__main__':
    main()