from telegram import Update
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext,CallbackQueryHandler
from bson import ObjectId
from user_service import UserService
from order_service import OrderService
from product_service import ProductService

TOKEN = "7652002534:AAFaGS0xvVp8woQj4shgMHDVT3zKZ7-pz28"

user_service = UserService()
order_service = OrderService()
product_service = ProductService(user_service)

async def handle_command(update: Update, context: CallbackContext, command: str) -> None:
    user = update.effective_user
    response = None

    if command == "get_users":
        response = user_service.get_all_users(user.id)

    elif command == "delete_user":
        response = user_service.delete_user(user.id)

    elif command == "add_to_cart":
        product = {"name": "گوشی موبایل", "price": 10_000_000}  # محصول نمونه
        response = user_service.add_to_cart(user.id, product)

    elif command == "get_cart":
        cart = user_service.get_user_cart(user.id)
        response = "\n".join([f"{p['name']} - {p['price']} تومان" for p in cart]) if cart else "🛒 سبد خرید شما خالی است!"

    if response:
        await update.message.reply_text(response)

async def start(update: Update, context: CallbackContext) -> None:
    """ثبت‌نام کاربر هنگام اجرای /start"""
    user = update.effective_user
    phone = "09123456789"  # در نسخه واقعی باید از ورودی کاربر دریافت شود
    response = user_service.register_user(user.id, user.username, phone)
    await update.message.reply_text(response)

async def place_order(update: Update, context: CallbackContext) -> None:
    """ثبت سفارش و ارسال دکمه پرداخت"""
    user = update.effective_user
    cart = user_service.get_user_cart(user.id)
    
    message, payment_link = order_service.create_order(user.id, cart)

    if payment_link:
        # دکمه "رفتن به درگاه پرداخت"
        keyboard = [[InlineKeyboardButton("💳 رفتن به درگاه پرداخت", url=payment_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message)

async def get_orders(update: Update, context: CallbackContext) -> None:
    """دریافت سفارشات ثبت‌شده"""
    user = update.effective_user
    response = order_service.get_orders(user.id)
    await update.message.reply_text(response)


async def add_product(update: Update, context: CallbackContext) -> None:
    
    
    # دریافت آرگومان‌ها از `context.args`
    args = context.args  
    if len(args) < 3:
        await update.message.reply_text("⚠️ لطفاً نام، قیمت و توضیح محصول را وارد کنید.\nمثال:\n/add_product گوشی 10000000 یک گوشی عالی")
        return

    name = args[0]
    try:
        price = int(args[1])  # بررسی اینکه قیمت عدد است
    except ValueError:
        await update.message.reply_text("❌ قیمت باید عدد باشد!")
        return

    description = " ".join(args[2:])  # ترکیب بقیه آرگومان‌ها به عنوان توضیحات
    response = product_service.add_product(name, price, description)
    await update.message.reply_text(response)





async def add_to_cart_callback(update: Update, context: CallbackContext) -> None:
    """مدیریت کلیک روی دکمه 'افزودن به سبد خرید'"""
    query = update.callback_query
    user = query.from_user

    product_id = query.data.replace("add_", "")  # استخراج آیدی محصول
    product = product_service.product_repo.get_by_id(ObjectId(product_id))

    if product:
        user_service.add_to_cart(user.id, product)
        await query.answer("✅ محصول به سبد خرید اضافه شد!", show_alert=True)
    else:
        await query.answer("❌ محصول یافت نشد!", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    #دستورات یوزر
    app.add_handler(CommandHandler("get_users", lambda u, c: handle_command(u, c, "get_users")))
    app.add_handler(CommandHandler("delete", lambda u, c: handle_command(u, c, "delete_user")))
    app.add_handler(CommandHandler("add_to_cart", lambda u, c: handle_command(u, c, "add_to_cart")))

    # دستورات سفارش
    app.add_handler(CommandHandler("place_order", place_order))
    app.add_handler(CommandHandler("get_orders", get_orders))


    app.add_handler(CommandHandler("add_product", add_product))
    app.add_handler(CommandHandler("show_products", product_service.show_products))
    app.add_handler(CommandHandler("get_cart", product_service.get_cart))
    app.add_handler(CallbackQueryHandler(add_to_cart_callback, pattern="^add_"))

    # مدیریت کلیک روی دکمه‌ها
    app.add_handler(CallbackQueryHandler(product_service.add_to_cart, pattern="^add_"))
    app.add_handler(CallbackQueryHandler(product_service.remove_from_cart, pattern="^remove_"))


    print("🤖 ربات در حال اجرا است...")
    app.run_polling()

if __name__ == '__main__':
    main()
