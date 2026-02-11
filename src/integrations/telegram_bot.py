"""
Telegram Bot Integration - Control Pixie remotely via Telegram
"""
import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.ai_engine_operator import get_response_operator
from src.core.ai_engine_gemini import get_response

load_dotenv()


class PixieTelegramBot:
    """Telegram bot for controlling Pixie remotely"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not configured in .env")
        
        # Remove quotes if present
        self.token = self.token.strip('"').strip("'")
        
        self.app = Application.builder().token(self.token).build()
        self.authorized_users = self._load_authorized_users()
        self.setup_handlers()
        print("✓ Telegram bot initialized")
    
    def _load_authorized_users(self):
        """Load authorized user IDs from env"""
        users_str = os.getenv("TELEGRAM_AUTHORIZED_USERS", "")
        if users_str:
            return [int(uid.strip()) for uid in users_str.split(",")]
        return []
    
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        # If no users configured, allow all (for initial setup)
        if not self.authorized_users:
            return True
        return user_id in self.authorized_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text(
                "❌ Unauthorized. Your user ID: " + str(user_id)
            )
            return
        
        await update.message.reply_text(
            "🦊 **Pixie AI - Remote Control**\n\n"
            "I can help you control your computer remotely!\n\n"
            "**Commands:**\n"
            "/start - Show this message\n"
            "/status - Check Pixie status\n"
            "/operator - Toggle operator mode\n\n"
            "**Just send me a message to:**\n"
            "• Send WhatsApp messages\n"
            "• Open applications\n"
            "• Control your computer\n\n"
            "Example: `send whatsapp message to adith \"hello\"`"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        await update.message.reply_text(
            "✅ **Pixie Status**\n\n"
            "🟢 Online and ready\n"
            "🤖 Operator mode: Active\n"
            "💻 Computer: Connected"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text(
                f"❌ Unauthorized access attempt.\n"
                f"Your user ID: {user_id}\n\n"
                f"Add this ID to TELEGRAM_AUTHORIZED_USERS in .env to authorize."
            )
            return
        
        user_message = update.message.text
        print(f"\n📱 Telegram message from {update.effective_user.first_name}: {user_message}")
        
        # Send "typing" indicator
        await update.message.chat.send_action("typing")
        
        try:
            # Process message through Pixie operator
            response = get_response_operator(user_message)
            
            # Send response back to Telegram
            await update.message.reply_text(response, parse_mode="Markdown")
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"Error processing Telegram message: {e}")
            await update.message.reply_text(error_msg)
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def run(self):
        """Start the bot"""
        print("🤖 Starting Telegram bot...")
        print(f"📱 Bot is ready! Send messages to control Pixie remotely.")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def start_telegram_bot():
    """Start the Telegram bot"""
    try:
        bot = PixieTelegramBot()
        bot.run()
    except ValueError as e:
        print(f"❌ {e}")
        print("Please add TELEGRAM_BOT_TOKEN to your .env file")
    except Exception as e:
        print(f"❌ Failed to start Telegram bot: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    start_telegram_bot()
