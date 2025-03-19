from repository import GenericRepository
import hashlib
import re

class UserService:
    def __init__(self):
        self.user_repo = GenericRepository("users")
        self.admins = [123456789, 987654321]  # لیست ادمین‌های مجاز

    def hash_data(self, data: str) -> str:
        #هش کردن داده‌های حساس (مثلاً شماره تلفن)
        return hashlib.sha256(data.encode()).hexdigest()

    def is_valid_username(self, username: str) -> bool:
        #اعتبارسنجی نام کاربری (نباید شامل کاراکترهای غیرمجاز باشد)
        return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username))

    def is_valid_phone(self, phone: str) -> bool:
        #اعتبارسنجی شماره تلفن (مثلاً فرمت ایران)
        return bool(re.match(r"^(\+98|0)?9\d{9}$", phone))

    def is_admin(self, user_id: int) -> bool:
        #بررسی اینکه آیا کاربر ادمین است یا نه
        return user_id in self.admins

    def register_user(self, user_id: int, username: str, phone: str) -> str:
        """ثبت‌نام کاربر با اعتبارسنجی ورودی‌ها"""
        if not self.is_valid_username(username):
            return "⛔ نام کاربری نامعتبر است! لطفاً فقط حروف، اعداد و آندرلاین استفاده کنید."
        if not self.is_valid_phone(phone):
            return "⛔ شماره تلفن نامعتبر است!"
        
        if not self.user_repo.get_by_id(user_id):
            hashed_phone = self.hash_data(phone)  # هش کردن شماره تلفن
            user_data = {"_id": user_id, "username": username, "phone": hashed_phone, "cart": []}
            self.user_repo.insert(user_data)
            return "✅ حساب شما با موفقیت ثبت شد."
        return "ℹ️ شما قبلاً ثبت‌نام کرده‌اید!"

    def get_all_users(self, user_id: int):
        """دریافت لیست تمام کاربران (فقط برای ادمین‌ها)"""
        if not self.is_admin(user_id):
            return "⛔ شما اجازه دسترسی به این اطلاعات را ندارید!"
        
        users = self.user_repo.get_all()

        # تبدیل ObjectId به رشته برای جلوگیری از خطای JSON
        result = []
        for user in users:
            user["_id"] = str(user["_id"])  # تبدیل ObjectId به str
            result.append(user)

        return result if result else "ℹ️ هیچ کاربری ثبت نشده است."


    def delete_user(self, user_id: int) -> str:
        """حذف کاربر از دیتابیس"""
        if self.user_repo.delete(user_id):
            return "✅ حساب شما حذف شد."
        return "⚠️ خطا در حذف حساب!"

    def get_user_cart(self, user_id: int):
        """دریافت سبد خرید کاربر"""
        user = self.user_repo.get_by_id(user_id)
        return user.get("cart", []) if user else None

    def add_to_cart(self, user_id: int, product: dict) -> str:
        """افزودن محصول به سبد خرید"""
        user = self.user_repo.get_by_id(user_id)
        if user:
            cart = user.get("cart", [])
            cart.append(product)
            self.user_repo.update(user_id, {"cart": cart})
            return f"🛒 محصول {product['name']} به سبد خرید اضافه شد!"
        return "⚠️ کاربر یافت نشد!"
