from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    CallbackContext,
    filters,
)
from product_service import ProductService

# تعریف مراحل مکالمه
NAME, PRICE, CATEGORY, DESCRIPTION, PHOTO, CONFIRM_PRODUCT = range(6)

# سرویس محصول
p_service = ProductService()

# ذخیره اطلاعات محصول
new_product = {}


class AddProductConversation:
    async def start_add_product(self, update: Update, context: CallbackContext) -> int:
        """شروع مکالمه و درخواست نام محصول"""
        await update.message.reply_text("🔹 لطفاً نام محصول را وارد کنید:")
        return NAME

    async def get_name(self, update: Update, context: CallbackContext) -> int:
        """ذخیره نام محصول و درخواست قیمت"""
        new_product['name'] = update.message.text
        await update.message.reply_text(f"✅ نام محصول: {new_product['name']}\nلطفاً قیمت را وارد کنید:")
        return PRICE

    async def get_price(self, update: Update, context: CallbackContext) -> int:
        """ذخیره قیمت محصول و درخواست دسته‌بندی"""
        try:
            new_product['price'] = int(update.message.text)
            await update.message.reply_text(f"✅ قیمت محصول: {new_product['price']} تومان\nلطفاً دسته‌بندی را وارد کنید:")
            return CATEGORY
        except ValueError:
            await update.message.reply_text("⚠️ قیمت باید یک عدد باشد! لطفاً مجدداً وارد کنید:")
            return PRICE

    async def get_category(self, update: Update, context: CallbackContext) -> int:
        """ذخیره دسته‌بندی محصول و درخواست توضیحات"""
        new_product['category'] = update.message.text
        await update.message.reply_text(f"✅ دسته‌بندی: {new_product['category']}\nلطفاً توضیحات محصول را وارد کنید:")
        return DESCRIPTION

    async def get_description(self, update: Update, context: CallbackContext) -> int:
        """ذخیره توضیحات محصول و درخواست عکس"""
        new_product['description'] = update.message.text
        await update.message.reply_text(f"✅ توضیحات ثبت شد.\nلطفاً یک عکس از محصول ارسال کنید:")
        return PHOTO

    async def get_photo(self, update: Update, context: CallbackContext) -> int:
        """دریافت عکس و نمایش اطلاعات محصول برای تأیید"""
        photo = update.message.photo[-1]  # دریافت بهترین کیفیت عکس
        file_id = photo.file_id  # شناسه فایل تلگرام

        new_product["image_url"] = file_id  # ذخیره شناسه عکس در دیتابیس

        # نمایش اطلاعات محصول برای تأیید
        text = (
            f"🛍 نام: {new_product['name']}\n"
            f"💰 قیمت: {new_product['price']} تومان\n"
            f"📂 دسته‌بندی: {new_product['category']}\n"
            f"ℹ توضیحات: {new_product['description']}\n\n"
            "✅ آیا اطلاعات صحیح است؟"
        )

        keyboard = [
            [InlineKeyboardButton("✅ بله، ثبت شود", callback_data="confirm_product")],
            [InlineKeyboardButton("❌ لغو", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_photo(photo=file_id, caption=text, reply_markup=reply_markup)
        return CONFIRM_PRODUCT

    async def confirm_product(self, update: Update, context: CallbackContext) -> int:
        """ثبت محصول نهایی"""
        query = update.callback_query
        await query.answer()

        # ذخیره محصول در دیتابیس
        p_service.add_product(new_product)

        # ارسال پیام تأیید و پایان مکالمه
        await query.message.reply_text(f"✅ محصول '{new_product['name']}' با موفقیت اضافه شد! 🎉")

        new_product.clear()  # پاک کردن اطلاعات محصول
        return ConversationHandler.END  # پایان مکالمه

    async def cancel(self, update: Update, context: CallbackContext) -> int:
        """لغو مکالمه و پاک کردن اطلاعات موقت"""
        await update.message.reply_text("❌ عملیات لغو شد.", reply_markup=ReplyKeyboardRemove())
        new_product.clear()
        return ConversationHandler.END
