
import string
from repository import GenericRepository
import hashlib
import re


class UserService:
    def __init__(self):
        self.user_repo = GenericRepository("users")
        self.product_repo=GenericRepository("products")
        self.admins = [123456789, 987654321]  # لیست ادمین‌های مجاز

    def hash_data(self, data: str) -> str:
        # هش کردن داده‌های حساس (مثلاً شماره تلفن)
        return hashlib.sha256(data.encode()).hexdigest()

    def is_valid_username(self, username: str) -> bool:
        # اعتبارسنجی نام کاربری (نباید شامل کاراکترهای غیرمجاز باشد)
        return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username))

    def is_valid_phone(self, phone: str) -> bool:
        # اعتبارسنجی شماره تلفن (مثلاً فرمت ایران)
        return bool(re.match(r"^(\+98|0)?9\d{9}$", phone))

    def is_admin(self, user_id: int) -> bool:
        # بررسی اینکه آیا کاربر ادمین است یا نه
        return user_id in self.admins

    def register_user(self, user) -> str:
        """ثبت‌نام کاربر با اعتبارسنجی ورودی‌ها"""
        if not self.is_valid_phone(user["phone"]):
            return "⛔ شماره تلفن نامعتبر است!"

        if not self.user_registered(user["user_id"]):
            hashed_pass = self.hash_data(user["password"])
            # user_data = {"_id": user['user_id'], "username": user['username'], "phone": hashed_phone, "cart": []}
            user["password"] = hashed_pass
            self.user_repo.insert(user)
            return "✅ حساب شما با موفقیت ثبت شد."
        return "ℹ️ شما قبلاً ثبت‌نام کرده‌اید!"

    def check_password(self, password, user_id) -> bool:
        users = self.user_repo.get_all({"user_id": user_id})
        if users[0]:
            if users[0]["password"] == self.hash_data(password):
                return True
        return False

    def get_you(self, user_id):
        you = self.user_repo.get_all({"user_id": user_id})
        return you[0]

    def user_registered(self, user_id) -> bool:
        users = self.user_repo.get_all({"user_id": user_id})

        if users:
            return True
        return False

    def get_objectId_by_user_id(self, user_id) -> str:
        user = self.get_you(user_id)
        oid = str(user["_id"])
        return oid

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

    def update_user(self, user_data: dict) -> str:
        """بروزرسانی اطلاعات کاربر در دیتابیس"""
        user_id = self.get_objectId_by_user_id(user_data["user_id"])
        if not user_id:
            return "❌ کاربر یافت نشد!"

        update_fields = {
            key: value for key, value in user_data.items() if key != "_id"
        }  # حذف `_id` از بروزرسانی

        if not update_fields:
            return "⚠️ هیچ اطلاعات جدیدی برای بروزرسانی وارد نشده است!"

        result = self.user_repo.update(user_id, update_fields)

        if result.modified_count > 0:
            return "✅ اطلاعات کاربری با موفقیت بروزرسانی شد!"
        else:
            return "⚠️ هیچ تغییری در اطلاعات کاربری ایجاد نشد!"

    def delete_user(self, user_id):
        """حذف کاربر بر اساس user_id"""
        users = list(
            self.user_repo.get_all({"user_id": user_id})
        )  # تبدیل Cursor به لیست

        if not users:  # بررسی اینکه آیا نتیجه‌ای دارد؟
            return "⚠️ کاربر موردنظر یافت نشد!"

        o_id = users[0]["_id"]  # حالا مطمئنیم که لیست خالی نیست
        if self.user_repo.delete(o_id):
            return "✅ کاربر با موفقیت حذف شد!"
        return "⚠️ خطا در حذف حساب!"

    def get_user_cart(self, user_id: int):
        """دریافت سبد خرید کاربر"""
        user = self.user_repo.get_by_id(self.get_objectId_by_user_id(user_id))
        return user.get("cart", []) if user else None

    def add_to_cart(self, user_id: int, product: dict, qty: int) -> str:
        """افزودن محصول به سبد خرید"""
        user = self.user_repo.get_by_id(self.get_objectId_by_user_id(user_id))
        if user:
            cart = user.get("cart", [])
            if self.check_product_quantity:
                product["quantity"] = qty
                cart.append(product)
                self.user_repo.update(self.get_objectId_by_user_id(user_id), {"cart": cart})
                return f"🛒 محصول {product['name']} به سبد خرید اضافه شد!"
            else:
                return "تعداد بیش از موجودی!"
        return "⚠️ کاربر یافت نشد!"

    def check_product_quantity(self,product_id):
        return True