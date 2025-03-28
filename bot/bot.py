from telegram import Update
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from bson import ObjectId
from user_service import UserService
from order_service import OrderService
from product_service import ProductService
from userCart_Service import UserCartService
from add_product_conversation_service import (
    AddProductConversation,
    NAME,
    PRICE,
    CATEGORY,
    DESCRIPTION,
    PHOTO,
    CONFIRM_PRODUCT,
)

from Register_Conversation_Service import (
    RegisterConversation,
    PHONE,
    PASSWORD,
    FULL_NAME,
    EMAIL,
    BIRTHDAY,
)

from editProfile_conversation_service import (
    EditProfileConversation,
    EPASSWORD,
    EDIT_SELECTION,
    EDIT_PHONE,
    EDIT_FULL_NAME,
    EDIT_EMAIL,
    EDIT_BIRTHDAY,
)
from addToCart_Conversation_Service import AddToCartConversationService, SELECT_QUANTITY

TOKEN = "7652002534:AAFaGS0xvVp8woQj4shgMHDVT3zKZ7-pz28"

user_service = UserService()
cart_service = UserCartService()
order_service = OrderService()
product_service = ProductService()
addproduct_conversation = AddProductConversation()
register_conversation = RegisterConversation()
edit_profile_conversation = EditProfileConversation()
addToCart_conversation = AddToCartConversationService(user_service)

async def handle_command(
    update: Update, context: CallbackContext, command: str
) -> None:
    user = update.effective_user
    response = None

    if command == "get_users":
        response = user_service.get_all_users(user.id)

    elif command == "delete_user":
        response = user_service.delete_user(user.id)

    elif command == "add_to_cart":
        cart_service.add_to_cart(update, context)

    elif command == "get_cart":
        cart = user_service.get_user_cart(user.id)
        response = (
            "\n".join([f"{p['name']} - {p['price']} تومان" for p in cart])
            if cart
            else "🛒 سبد خرید شما خالی است!"
        )

    if response:
        await update.message.reply_text(response)


async def start(update: Update, context: CallbackContext) -> None:
    """ثبت‌نام کاربر هنگام اجرای /start"""
    user = update.effective_user
    if user_service.user_registered(user.id):
        await update.message.reply_text("خوش برگشتید :)")
    else:
        await update.message.reply_text(
            "سلام لطفا ابتدا با دستور /register ثبت نام کنید"
        )


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
    # دریافت سفارشات ثبت‌شده
    user = update.effective_user
    response = order_service.get_orders(user.id)
    await update.message.reply_text(response)


async def add_to_cart_callback(update: Update, context: CallbackContext) -> None:
    """مدیریت کلیک روی دکمه 'افزودن به سبد خرید' و شروع مکالمه انتخاب تعداد"""
    query = update.callback_query
    await query.answer()  # جلوگیری از خطای تایم‌اوت در بات تلگرام

    # هدایت کاربر به سرویس مکالمه انتخاب تعداد
    return await addToCart_conversation.add_to_cart(update, context)



def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # دستورات یوزر
    app.add_handler(
        CommandHandler("get_users", lambda u, c: handle_command(u, c, "get_users"))
    )
    app.add_handler(
        CommandHandler("delete", lambda u, c: handle_command(u, c, "delete_user"))
    )
    app.add_handler(
        CommandHandler("add_to_cart", lambda u, c: handle_command(u, c, "add_to_cart"))
    )

    # دستورات سفارش
    app.add_handler(CommandHandler("place_order", place_order))
    app.add_handler(CommandHandler("get_orders", get_orders))

    app.add_handler(CommandHandler("show_products", product_service.show_products))
    app.add_handler(CommandHandler("get_cart", cart_service.get_cart))
    app.add_handler(CommandHandler("categories", product_service.show_categories))
    app.add_handler(CommandHandler("search", product_service.search_products))
    app.add_handler(CallbackQueryHandler(add_to_cart_callback, pattern="^add_"))
    app.add_handler(
        CallbackQueryHandler(
            product_service.show_products_by_category, pattern="^category_"
        )
    )

    # مدیریت کلیک روی دکمه‌ها
    app.add_handler(CallbackQueryHandler(cart_service.add_to_cart, pattern="^add_"))
    app.add_handler(
        CallbackQueryHandler(product_service.show_product_info, pattern="^info_")
    )

    app.add_handler(
        CallbackQueryHandler(cart_service.remove_from_cart, pattern="^remove_")
    )

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("add_product", addproduct_conversation.start_add_product)
        ],
        states={
            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, addproduct_conversation.get_name
                )
            ],
            PRICE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, addproduct_conversation.get_price
                )
            ],
            CATEGORY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    addproduct_conversation.get_category,
                )
            ],
            DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    addproduct_conversation.get_description,
                )
            ],
            PHOTO: [MessageHandler(filters.PHOTO, addproduct_conversation.get_photo)],
            CONFIRM_PRODUCT: [
                CallbackQueryHandler(
                    addproduct_conversation.confirm_product, pattern="^confirm_product$"
                ),
                CallbackQueryHandler(
                    addproduct_conversation.cancel, pattern="^cancel$"
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", addproduct_conversation.cancel)],
    )
    app.add_handler(conv_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register_conversation.start_register)],
        states={
            PHONE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, register_conversation.get_phone
                )
            ],
            PASSWORD: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, register_conversation.get_password
                )
            ],
            FULL_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, register_conversation.get_full_name
                )
            ],
            EMAIL: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, register_conversation.get_email
                ),
                CommandHandler("skip", register_conversation.skip_email),
            ],
            BIRTHDAY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, register_conversation.get_birthday
                ),
                CommandHandler("skip", register_conversation.skip_birthday),
            ],
        },
        fallbacks=[CommandHandler("cancel", register_conversation.cancel)],
    )

    app.add_handler(conv_handler)

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("edit_profile", edit_profile_conversation.start_edit_profile)
        ],
        states={
            EPASSWORD: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    edit_profile_conversation.get_password,
                )
            ],
            EDIT_SELECTION: [
                CallbackQueryHandler(edit_profile_conversation.edit_selection)
            ],
            EDIT_PHONE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    edit_profile_conversation.update_phone,
                )
            ],
            EDIT_FULL_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    edit_profile_conversation.update_full_name,
                )
            ],
            EDIT_EMAIL: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    edit_profile_conversation.update_email,
                )
            ],
            EDIT_BIRTHDAY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    edit_profile_conversation.update_birthday,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", edit_profile_conversation.cancel)],
    )

    app.add_handler(conv_handler)

    

    conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(addToCart_conversation.add_to_cart, pattern="^add_")],
    states={
        SELECT_QUANTITY: [
            CallbackQueryHandler(addToCart_conversation.select_quantity, pattern="^qty_\d+$"),
            CallbackQueryHandler(addToCart_conversation.receive_custom_quantity, pattern="^custom_qty$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, addToCart_conversation.receive_custom_quantity),
            CallbackQueryHandler(addToCart_conversation.cancel_purchase, pattern="^cancel_purchase$")
        ]
    },
    fallbacks=[CallbackQueryHandler(addToCart_conversation.cancel_purchase, pattern="^cancel_purchase$")]
)

    app.add_handler(conv_handler)


    print("🤖 ربات در حال اجرا است...")
    app.run_polling()


if __name__ == "__main__":
    main()
