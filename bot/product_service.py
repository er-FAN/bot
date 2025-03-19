# from repository import GenericRepository

# class ProductService:
#     def __init__(self):
#         self.product_repo = GenericRepository("products")

#     def add_product(self, name: str, price: int, description: str):
#         """افزودن محصول جدید به دیتابیس"""
#         product_data = {
#             "name": name,
#             "price": price,
#             "description": description
#         }
#         self.product_repo.insert(product_data)
#         return f"✅ محصول '{name}' اضافه شد."

#     def get_all_products(self):
#         """دریافت لیست محصولات"""
#         products = self.product_repo.get_all()
#         if not products:
#             return "هیچ محصولی یافت نشد!", None

#         product_list = []
#         for product in products:
#             product["_id"] = str(product["_id"])  # تبدیل ObjectId به str
#             product_list.append(product)
        
#         return None, product_list

from repository import GenericRepository
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from bson import ObjectId

class ProductService:
    def __init__(self, user_service):
        self.product_repo = GenericRepository("products")
        self.user_service = user_service

    def add_product(self, name: str, price: int, description: str = "توضیحی موجود نیست"):
        # """افزودن محصول جدید (فقط برای ادمین‌ها)"""
        # user = update.effective_user
        # if not user_service.is_admin(user.id):
        #     await update.message.reply_text("⛔ شما اجازه افزودن محصول را ندارید!")
        #     return

        product_data = {
            "name": name,
            "price": price,
            "description": description
        }
        self.product_repo.insert(product_data)
        return f"✅ محصول '{name}' اضافه شد."

    def get_all_products(self):
        """دریافت لیست محصولات"""
        products = self.product_repo.get_all()
        if not products:
            return "هیچ محصولی یافت نشد!", None

        product_list = []
        for product in products:
            product["_id"] = str(product["_id"])
            product_list.append(product)

        return None, product_list

    async def show_products(self, update, context):
        """نمایش لیست محصولات با دکمه 'افزودن به سبد خرید'"""
        message, products = self.get_all_products()
        
        if message:
            await update.message.reply_text(message)
            return

        for product in products:
            product_text = f"🛍 {product['name']}\n💰 قیمت: {product['price']} تومان\nℹ️ {product['description']}"
            keyboard = [[InlineKeyboardButton("➕ افزودن به سبد خرید", callback_data=f"add_{product['_id']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(product_text, reply_markup=reply_markup)

    async def add_to_cart(self, update, context):
        """افزودن محصول به سبد خرید"""
        query = update.callback_query
        user = query.from_user

        product_id = query.data.replace("add_", "")
        product = self.product_repo.get_by_id(ObjectId(product_id))

        if product:
            self.user_service.add_to_cart(user.id, product)
            await query.answer(f"✅ '{product['name']}' به سبد خرید اضافه شد!", show_alert=True)
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
            description = product.get('description', "توضیحی موجود نیست")
            product_text = f"🛍 {product['name']}\n💰 قیمت: {product['price']} تومان\nℹ️ {description}"
            keyboard = [[InlineKeyboardButton("❌ حذف از سبد", callback_data=f"remove_{index}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(product_text, reply_markup=reply_markup)

    async def remove_from_cart(self, update, context):
        """حذف محصول از سبد خرید"""
        query = update.callback_query
        user = query.from_user

        index = int(query.data.replace("remove_", ""))
        cart = self.user_service.get_user_cart(user.id)

        if cart and 0 <= index < len(cart):
            removed_item = cart.pop(index)
            self.user_service.user_repo.update(user.id, {"cart": cart})
            await query.answer(f"✅ '{removed_item['name']}' از سبد خرید حذف شد.", show_alert=True)
            await query.message.delete()
        else:
            await query.answer("❌ آیتم مورد نظر یافت نشد!", show_alert=True)


