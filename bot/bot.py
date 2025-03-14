from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# توکن بات را اینجا قرار بده
TOKEN = "YOUR_BOT_TOKEN"

# پاسخ به دستور /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("سلام! من یک بات تلگرامی هستم. با من صحبت کن.")

# پاسخ به پیام‌های متنی
async def echo(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    await update.message.reply_text(f"تو گفتی: {text}")

# تابع اصلی برای اجرای بات
def main():
    app = Application.builder().token(TOKEN).build()

    # اضافه کردن دستورات و فیلترها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # راه‌اندازی بات
    app.run_polling()

if __name__ == '__main__':
    main()
