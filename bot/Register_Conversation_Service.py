from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
from user_service import UserService

# مراحل مکالمه
PHONE, PASSWORD, FULL_NAME, EMAIL, BIRTHDAY = range(5)

# سرویس کاربر
u_service = UserService()

# ذخیره اطلاعات ثبت‌نام
user_data = {}


class RegisterConversation:
    async def start_register(self, update: Update, context: CallbackContext) -> int:
        """شروع مکالمه و درخواست شماره تلفن"""
        reply_keyboard = [["📞 ارسال شماره تلفن"]]
        await update.message.reply_text(
            "🔹 لطفاً شماره تلفن خود را وارد کنید یا از دکمه زیر استفاده کنید:"
            + "\n"
            + "شما میتوانید در هر مرحله در صودت عدم تمایل به ثبت نام /cancel را ارسال کنید.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        user_data["user_id"] = update.effective_user.id
        return PHONE

    async def get_phone(self, update: Update, context: CallbackContext) -> int:
        """ذخیره شماره تلفن و درخواست رمز عبور"""
        phone = update.message.text

        # بررسی شماره تلفن معتبر
        if not phone.isdigit() or len(phone) < 10:
            await update.message.reply_text(
                "⚠️ شماره تلفن نامعتبر است! لطفاً مجدداً وارد کنید:"
            )
            return PHONE

        user_data["phone"] = phone
        await update.message.reply_text(
            "✅ شماره تلفن ثبت شد.\n🔹 لطفاً یک رمز عبور قوی انتخاب کنید:"
        )
        return PASSWORD

    async def get_password(self, update: Update, context: CallbackContext) -> int:
        """ذخیره رمز عبور و درخواست نام و نام خانوادگی"""
        password = update.message.text

        # بررسی حداقل طول رمز عبور
        if len(password) < 6:
            await update.message.reply_text(
                "⚠️ رمز عبور باید حداقل ۶ کاراکتر باشد! لطفاً مجدداً وارد کنید:"
            )
            return PASSWORD

        user_data["password"] = password
        await update.message.reply_text(
            "✅ رمز عبور ثبت شد.\n🔹 لطفاً نام و نام خانوادگی خود را وارد کنید:"
        )
        return FULL_NAME

    async def get_full_name(self, update: Update, context: CallbackContext) -> int:
        """ذخیره نام و نام خانوادگی و درخواست ایمیل"""
        user_data["full_name"] = update.message.text
        await update.message.reply_text(
            "✅ نام و نام خانوادگی ثبت شد.\n🔹 لطفاً ایمیل خود را وارد کنید (یا /skip بزنید):"
        )
        return EMAIL

    async def get_email(self, update: Update, context: CallbackContext) -> int:
        """ذخیره ایمیل و درخواست تاریخ تولد"""
        email = update.message.text

        # بررسی ایمیل معتبر
        if "@" not in email or "." not in email:
            await update.message.reply_text(
                "⚠️ ایمیل نامعتبر است! لطفاً مجدداً وارد کنید یا /skip را بزنید:"
            )
            return EMAIL

        user_data["email"] = email
        await update.message.reply_text(
            "✅ ایمیل ثبت شد.\n🔹 لطفاً تاریخ تولد خود را وارد کنید (مثلاً 1375/05/12) یا /skip بزنید:"
        )
        return BIRTHDAY

    async def skip_email(self, update: Update, context: CallbackContext) -> int:
        """رد کردن ایمیل و درخواست تاریخ تولد"""
        user_data["email"] = None
        await update.message.reply_text(
            "🔹 لطفاً تاریخ تولد خود را وارد کنید (مثلاً 1375/05/12) یا /skip بزنید:"
        )
        return BIRTHDAY

    async def get_birthday(self, update: Update, context: CallbackContext) -> int:
        """ذخیره تاریخ تولد و تکمیل ثبت‌نام"""
        user_data["birthday"] = update.message.text

        # دریافت نام کاربری تلگرام
        username = (
            update.message.from_user.username
            if update.message.from_user.username
            else "نامشخص"
        )

        # ذخیره اطلاعات در دیتابیس
        u_service.register_user(user_data)

        await update.message.reply_text(
            f"✅ ثبت‌نام شما تکمیل شد! 🎉\n📞 شماره: {user_data['phone']}\n🔒 رمز عبور: {'*' * len(user_data['password'])}\n👤 نام: {user_data['full_name']}\n📧 ایمیل: {user_data.get('email', 'ندارد')}\n🎂 تولد: {user_data.get('birthday', 'ندارد')}\n🆔 نام کاربری: @{username}"
        )

        user_data.clear()
        return ConversationHandler.END  # پایان مکالمه

    async def skip_birthday(self, update: Update, context: CallbackContext) -> int:
        """رد کردن تاریخ تولد و تکمیل ثبت‌نام"""
        user_data["birthday"] = None

        # دریافت نام کاربری تلگرام
        username = (
            update.message.from_user.username
            if update.message.from_user.username
            else "نامشخص"
        )

        # ذخیره اطلاعات در دیتابیس
        u_service.register_user(user_data)

        await update.message.reply_text(
            f"✅ ثبت‌نام شما تکمیل شد! 🎉\n📞 شماره: {user_data['phone']}\n🔒 رمز عبور: {'*' * len(user_data['password'])}\n👤 نام: {user_data['full_name']}\n📧 ایمیل: {user_data.get('email', 'ندارد')}\n🎂 تولد: ندارد\n🆔 نام کاربری: @{username}"
        )

        user_data.clear()
        return ConversationHandler.END

    async def cancel(self, update: Update, context: CallbackContext) -> int:
        """لغو مکالمه و پاک کردن اطلاعات موقت"""
        await update.message.reply_text(
            "❌ عملیات ثبت‌نام لغو شد.", reply_markup=ReplyKeyboardRemove()
        )
        user_data.clear()
        return ConversationHandler.END
