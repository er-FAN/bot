import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# فعال کردن لاگ‌ها برای دیباگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOKEN = "7652f002534:AAFaGS0gxvVp8woQj4sfgdfsT3zKZ7-pz28"

async def start(update: Update, context: CallbackContext) -> None:
    """ارسال پیام شروع"""
    await update.message.reply_text("سلام! من یک بات تلگرامی هستم.")

async def end(update: Update, context: CallbackContext) -> None:
    """ارسال پیام شروع"""
    await update.message.reply_text("خداحافظ.")

async def echo(update: Update, context: CallbackContext) -> None:
    """پیام‌های ورودی را ارسال کن"""
    await update.message.reply_text(f"تو گفتی: {update.message.text}")

def main():
    # ساخت ربات
    app = Application.builder().token(TOKEN).build()

    # اضافه کردن هندلرهای دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("end", end))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # شروع به دریافت پیام‌ها
    app.run_polling()

if __name__ == '__main__':
    main()
