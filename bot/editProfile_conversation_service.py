from telegram import (    Update,    InlineKeyboardMarkup,    InlineKeyboardButton,    ReplyKeyboardRemove,)
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    CallbackContext,
    filters,
)
from user_service import UserService

# مراحل مکالمه
EPASSWORD, EDIT_SELECTION, EDIT_PHONE, EDIT_FULL_NAME, EDIT_EMAIL, EDIT_BIRTHDAY = (
    range(6)
)

# سرویس کاربر
u_service = UserService()

# ذخیره اطلاعات ویرایش کاربر
user_data = {}


class EditProfileConversation:
    async def start_edit_profile(self, update: Update, context: CallbackContext) -> int:
        """شروع مکالمه و درخواست رمز عبور"""
        await update.message.reply_text("🔹 لطفاً رمز عبور خود را وارد کنید:")
        return EPASSWORD

    async def get_password(self, update: Update, context: CallbackContext) -> int:
        """دریافت رمز عبور و نمایش اطلاعات کاربری"""
        password = update.message.text

        # جستجو و تأیید کاربر در دیتابیس

        user = {}
        if not u_service.check_password(password, update.effective_user.id):
            await update.message.reply_text(
                "❌ رمز عبور اشتباه است! لطفاً دوباره وارد کنید یا /cancel را بفرستید:"
            )
            return EPASSWORD
        user = u_service.get_you(update.effective_user.id)
        user_data.update(user)  # ذخیره اطلاعات کاربر برای ویرایش

        # نمایش اطلاعات کاربر
        text = (
            f"📌 اطلاعات شما:\n"
            f"📞 شماره تلفن: {user['phone']}\n"
            f"👤 نام و نام خانوادگی: {user['full_name']}\n"
            f"📧 ایمیل: {user.get('email', 'ندارد')}\n"
            f"🎂 تاریخ تولد: {user.get('birthday', 'ندارد')}\n"
            "\n🔹 لطفاً اطلاعاتی که می‌خواهید ویرایش کنید را انتخاب کنید:"
        )

        keyboard = [
            [InlineKeyboardButton("📞 ویرایش شماره تلفن", callback_data="edit_phone")],
            [
                InlineKeyboardButton(
                    "👤 ویرایش نام و نام خانوادگی", callback_data="edit_full_name"
                )
            ],
            [InlineKeyboardButton("📧 ویرایش ایمیل", callback_data="edit_email")],
            [
                InlineKeyboardButton(
                    "🎂 ویرایش تاریخ تولد", callback_data="edit_birthday"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ پایان و ذخیره تغییرات", callback_data="save_changes"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(text, reply_markup=reply_markup)
        return EDIT_SELECTION

    async def edit_selection(self, update: Update, context: CallbackContext) -> int:
        """مدیریت انتخاب کاربر برای ویرایش و نمایش مجدد اطلاعات"""
        query = update.callback_query
        await query.answer()

        if query.data == "edit_phone":
            await query.message.reply_text("📞 لطفاً شماره تلفن جدید خود را وارد کنید:")
            return EDIT_PHONE
        elif query.data == "edit_full_name":
            await query.message.reply_text("👤 لطفاً نام و نام خانوادگی جدید خود را وارد کنید:")
            return EDIT_FULL_NAME
        elif query.data == "edit_email":
            await query.message.reply_text("📧 لطفاً ایمیل جدید خود را وارد کنید:")
            return EDIT_EMAIL
        elif query.data == "edit_birthday":
            await query.message.reply_text("🎂 لطفاً تاریخ تولد جدید خود را وارد کنید (مثلاً 1375/05/12):")
            return EDIT_BIRTHDAY
        elif query.data == "save_changes":
            return await self.save_changes(update, context)  # ذخیره تغییرات


    async def show_user_info(self, update: Update, context: CallbackContext):
        """نمایش مجدد اطلاعات کاربر بعد از ویرایش"""
        text = (
            f"📌 اطلاعات شما:\n"
            f"📞 شماره تلفن: {user_data['phone']}\n"
            f"👤 نام و نام خانوادگی: {user_data['full_name']}\n"
            f"📧 ایمیل: {user_data.get('email', 'ندارد')}\n"
            f"🎂 تاریخ تولد: {user_data.get('birthday', 'ندارد')}\n"
            "\n🔹 لطفاً اطلاعاتی که می‌خواهید ویرایش کنید را انتخاب کنید:"
        )

        keyboard = [
            [InlineKeyboardButton("📞 ویرایش شماره تلفن", callback_data="edit_phone")],
            [InlineKeyboardButton("👤 ویرایش نام و نام خانوادگی", callback_data="edit_full_name")],
            [InlineKeyboardButton("📧 ویرایش ایمیل", callback_data="edit_email")],
            [InlineKeyboardButton("🎂 ویرایش تاریخ تولد", callback_data="edit_birthday")],
            [InlineKeyboardButton("✅ پایان و ذخیره تغییرات", callback_data="save_changes")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(text, reply_markup=reply_markup)
        return EDIT_SELECTION



    async def update_phone(self, update: Update, context: CallbackContext) -> int:
        """ذخیره شماره تلفن جدید و نمایش مجدد اطلاعات"""
        user_data["phone"] = update.message.text
        await update.message.reply_text("✅ شماره تلفن جدید ثبت شد!")
        return await self.show_user_info(update, context)

    async def update_full_name(self, update: Update, context: CallbackContext) -> int:
        """ذخیره نام جدید و نمایش مجدد اطلاعات"""
        user_data["full_name"] = update.message.text
        await update.message.reply_text("✅ نام و نام خانوادگی جدید ثبت شد!")
        return await self.show_user_info(update, context)
    
    async def update_email(self, update: Update, context: CallbackContext) -> int:
        """ذخیره ایمیل جدید و نمایش مجدد اطلاعات"""
        user_data["email"] = update.message.text
        await update.message.reply_text("✅ ایمیل جدید ثبت شد!")
        return await self.show_user_info(update, context)
    
    async def update_birthday(self, update: Update, context: CallbackContext) -> int:
        """ذخیره تاریخ تولد جدید و نمایش مجدد اطلاعات"""
        user_data["birthday"] = update.message.text
        await update.message.reply_text("✅ تاریخ تولد جدید ثبت شد!")
        return await self.show_user_info(update, context)
    
    async def save_changes(self, update: Update, context: CallbackContext) -> int:
        """ذخیره تغییرات در دیتابیس و پایان مکالمه"""
        user_data["user_id"] = update.effective_user.id
        u_service.update_user(user_data)

        # await update.message.reply_text("✅ تغییرات شما با موفقیت ذخیره شد! 🎉")
        await update.callback_query.message.reply_text("✅ تغییرات شما با موفقیت ذخیره شد! 🎉")
        user_data.clear()
        return ConversationHandler.END

    async def cancel(self, update: Update, context: CallbackContext) -> int:
        """لغو مکالمه و پاک کردن اطلاعات موقت"""
        await update.message.reply_text(
            "❌ عملیات ویرایش لغو شد.", reply_markup=ReplyKeyboardRemove()
        )
        user_data.clear()
        return ConversationHandler.END
