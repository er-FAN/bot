from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from bson import ObjectId
from repository import GenericRepository

SELECT_QUANTITY = range(1)


class AddToCartConversationService:
    def __init__(self, user_service):
        self.product_repo = GenericRepository("products")
        self.user_service = user_service

    async def add_to_cart(self, update: Update, context: CallbackContext):
        """مرحله اول: دریافت کلیک کاربر روی افزودن به سبد خرید و پرسیدن تعداد"""
        query = update.callback_query
        user = query.from_user
        product_id = query.data.replace("add_", "")

        # ذخیره اطلاعات موقت محصول در context.user_data
        context.user_data["selected_product_id"] = product_id

        product = self.product_repo.get_by_id(ObjectId(product_id))
        if not product:
            await query.answer("❌ محصول یافت نشد!", show_alert=True)
            return ConversationHandler.END

        keyboard = [
            [
                InlineKeyboardButton("1️⃣", callback_data="qty_1"),
                InlineKeyboardButton("2️⃣", callback_data="qty_2"),
                InlineKeyboardButton("3️⃣", callback_data="qty_3"),
            ],
            [InlineKeyboardButton("🔢 مقدار دلخواه", callback_data="custom_qty")],
            [
                InlineKeyboardButton(
                    "❌ انصراف از خرید", callback_data="cancel_purchase"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            f"🔢 لطفاً تعداد '{product['name']}' را انتخاب کنید:",
            reply_markup=reply_markup,
        )
        return SELECT_QUANTITY

    async def select_quantity(self, update: Update, context: CallbackContext):
        """مرحله دوم: دریافت تعداد انتخاب‌شده توسط کاربر"""
        query = update.callback_query
        await query.answer()

        selected_product_id = context.user_data.get("selected_product_id")
        if not selected_product_id:
            await query.message.reply_text("❌ مشکلی پیش آمد، لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END

        if query.data.startswith("qty_"):
            quantity = int(query.data.replace("qty_", ""))
        elif query.data == "custom_qty":
            await query.message.reply_text(
                "🔢 لطفاً تعداد موردنظر را به‌صورت عددی ارسال کنید:"
            )
            return SELECT_QUANTITY  # منتظر پیام متنی از کاربر
        else:
            return await self.cancel_purchase(update, context)  # انصراف از خرید

        return await self.finalize_purchase(
            update, context, selected_product_id, quantity
        )

    async def receive_custom_quantity(self, update: Update, context: CallbackContext):
        """دریافت مقدار دلخواه از کاربر"""
        try:
            quantity = int(update.message.text)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("⚠️ لطفاً یک عدد معتبر وارد کنید:")
            return SELECT_QUANTITY

        selected_product_id = context.user_data.get("selected_product_id")
        return await self.finalize_purchase(
            update, context, selected_product_id, quantity
        )

    async def finalize_purchase(
        self, update: Update, context: CallbackContext, product_id, quantity
    ):
        """نهایی کردن افزودن به سبد خرید"""
        user = update.effective_user
        product = self.product_repo.get_by_id(ObjectId(product_id))

        if not product:
            await update.message.reply_text("❌ محصول یافت نشد!")
            return ConversationHandler.END

        # اضافه کردن به سبد خرید همراه با تعداد
        self.user_service.add_to_cart(user.id, product, quantity)

        await update.message.reply_text(
            f"✅ {quantity} عدد از '{product['name']}' به سبد خرید اضافه شد!"
        )
        return ConversationHandler.END

    async def cancel_purchase(self, update: Update, context: CallbackContext):
        """لغو فرآیند خرید"""
        query = update.callback_query
        await query.answer()

        await query.message.reply_text("❌ عملیات خرید لغو شد.")
        return ConversationHandler.END
