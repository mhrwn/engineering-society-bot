import logging
import os
import asyncio
import threading
from telegram.ext import Application, MessageHandler, filters
from main.handlers.start import register_start_handler
from main.handlers.registration import register_registration_handler
from main.handlers.messaging import register_messaging_handler
from main.handlers.profile import register_profile_handler, register_back_handler
from main.handlers.about import about_command
from main.handlers.events import events_command
from main.handlers.workshops import workshops_command
from main.handlers.contact import contact_command
from main.utils.keyboards import create_main_keyboard
from config import Config
import socks
import socket
from aiohttp import web

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

async def handle_text_messages(update, context):
    """Handle text messages for main menu buttons."""
    text = update.message.text
    commands = {
        "📖 درباره انجمن": about_command,
        "📅 رویدادها": events_command,
        "🎓 کارگاه‌ها": workshops_command,
        "📞 تماس با ما": contact_command,
    }
    if text in commands:
        await commands[text](update, context)
    else:
        await update.message.reply_text(
            "⚠️ لطفاً از دکمه‌های منو استفاده کنید.",
            reply_markup=create_main_keyboard()
        )

async def post_init(application):
    """Post-initialization setup for bot commands."""
    try:
        # Initialize the bot before setting commands
        await application.bot.initialize()
        
        commands = [
            ("start", "شروع کار با ربات"),
            ("cancel", "لغو عملیات جاری")
        ]
        await application.bot.set_my_commands(commands)
        logger.info("✅ Bot commands menu set successfully!")
    except Exception as e:
        logger.error(f"❌ Error setting bot commands: {e}")

def run_health_server():
    """Run health check server in a separate thread with its own event loop"""
    async def health_handler(request):
        return web.Response(text="OK")
    
    async def create_app():
        app = web.Application()
        app.router.add_get('/health', health_handler)
        app.router.add_get('/', health_handler)
        return app
    
    def start_server():
        """Start the health server in a separate event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_server():
            app = await create_app()
            port = int(os.getenv('PORT', 10000))
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            logger.info(f"🚀 Health check server running on port {port}")
            # Keep server running forever
            await asyncio.Future()
        
        try:
            loop.run_until_complete(run_server())
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()
    
    # Start the server in a daemon thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    return server_thread

def setup_bot():
    """Setup and return the bot application"""
    Config.validate()

    # Setup proxy if configured
    proxy_url = Config.PROXY_URL
    if proxy_url and proxy_url.startswith("socks5://"):
        proxy_url = proxy_url.replace("socks5://", "")
        host, port = proxy_url.split(":")
        socks.set_default_proxy(socks.SOCKS5, host, int(port))
        socket.socket = socks.socksocket
        logger.info(f"🔗 Proxy set: {host}:{port}")

    # Initialize application with connection pool size
    application = Application.builder()\
        .token(Config.MAIN_BOT_TOKEN)\
        .post_init(post_init)\
        .connection_pool_size(10)\
        .pool_timeout(30)\
        .build()

    # Register handlers
    register_start_handler(application)
    register_registration_handler(application)
    register_messaging_handler(application)
    register_profile_handler(application)
    register_back_handler(application)
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_text_messages
    ))

    return application

async def main():
    """Main function to run bot"""
    try:
        # Start health server in separate thread
        health_thread = run_health_server()
        logger.info("🩺 Health check server started in background thread")
        
        # Setup and start bot
        application = setup_bot()
        logger.info("🤖 Starting bot in polling mode...")
        
        # Run polling with specific settings for production
        await application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            close_loop=False  # Important: don't close the loop in production
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting main bot: {e}")
        raise

def run_bot():
    """Run the bot (for development without web server)"""
    try:
        application = setup_bot()
        logger.info("🤖 Starting bot in polling mode...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
    except Exception as e:
        logger.error(f"❌ Error starting main bot: {e}")
        raise

if __name__ == "__main__":
    # Check if we're in production (Render sets RENDER env var)
    if os.getenv('RENDER') or os.getenv('PORT'):
        # Use asyncio.run() for production
        asyncio.run(main())
    else:
        # Use simple run for development
        run_bot()