from repository import GenericRepository
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from bson import ObjectId
from user_service import UserService


user_service = UserService()


class UserCartService:
    def __init__(self):
        self.userCart_repo = GenericRepository("users")
        self.user_service = user_service

    async def add_to_cart(self, update, context):
        """افزودن محصول به سبد خرید"""
        query = update.callback_query
        user = query.from_user

        product_id = query.data.replace("add_", "")
        product = self.product_repo.get_by_id(ObjectId(product_id))

        if product:
            self.user_service.add_to_cart(user.id, product)
            await query.answer(
                f"✅ '{product['name']}' به سبد خرید اضافه شد!", show_alert=True
            )
        else:
            await query.answer("❌ محصول یافت نشد!", show_alert=True)

    async def get_cart(self, update, context):
        user = update.effective_user
        cart = self.user_service.get_user_cart(user.id)

        if not cart:
            await update.message.reply_text("🛒 سبد خرید شما خالی است!")
            return

        for index, product in enumerate(cart):
            # اگر description موجود نباشد، مقدار پیش‌فرض بده
            description = product.get("description", "توضیحی موجود نیست")
            product_text = f"🛍 {product['name']}\n💰 قیمت: {product['price']} تومان\nℹ️ {description}"
            keyboard = [
                [InlineKeyboardButton("❌ حذف از سبد", callback_data=f"remove_{index}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if "image_url" in product and product["image_url"]:  # بررسی اینکه مقدار `image_url` وجود دارد
                await update.message.reply_photo(photo=product["image_url"], caption=product_text, reply_markup=reply_markup)
            else:
                await update.message.reply_text(product_text, reply_markup=reply_markup)

            # await update.message.reply_text(product_text, reply_markup=reply_markup)

    async def remove_from_cart(self, update, context):
        """حذف محصول از سبد خرید"""
        query = update.callback_query
        user = query.from_user

        index = int(query.data.replace("remove_", ""))
        cart = self.user_service.get_user_cart(user.id)

        if cart and 0 <= index < len(cart):
            removed_item = cart.pop(index)
            self.user_service.user_repo.update(user_service.get_objectId_by_user_id(user.id), {"cart": cart})
            await query.answer(
                f"✅ '{removed_item['name']}' از سبد خرید حذف شد.", show_alert=True
            )
            await query.message.delete()
        else:
            await query.answer("❌ آیتم مورد نظر یافت نشد!", show_alert=True)

    # def get_user_cart(self, user_id: int):
    #     """دریافت سبد خرید کاربر"""
    #     user = self.user_repo.get_by_id(user_id)
    #     return user.get("cart", []) if user else None

    # def add_to_cart(self, user_id: int, product: dict) -> str:
    #     """افزودن محصول به سبد خرید"""
    #     user = self.user_repo.get_by_id(user_id)
    #     if user:
    #         cart = user.get("cart", [])
    #         cart.append(product)
    #         self.user_repo.update(user_id, {"cart": cart})
    #         return f"🛒 محصول {product['name']} به سبد خرید اضافه شد!"
    #     return "⚠️ کاربر یافت نشد!"
