from tkinter import SEL
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from repository import GenericRepository
from bson import ObjectId

# مراحل مختلف مکالمه
(
    NAME,
    PRICE,
    CATEGORY,
    DESCRIPTION,
    ATTRIBUTE_NAME,
    ATTRIBUTE_TYPE,
    ATTRIBUTE_VALUE,
    CONFIRM_PRODUCT,
) = range(8)


class ProductService:
    def __init__(self):
        self.product_repo = GenericRepository("products")
        # self.user_service = user_service

    def add_product(self, new_product):
        # """افزودن محصول جدید (فقط برای ادمین‌ها)"""
        # user = update.effective_user
        # if not user_service.is_admin(user.id):
        #     await update.message.reply_text("⛔ شما اجازه افزودن محصول را ندارید!")
        #     return

        # product_data = {
        # "name": name,
        # "price": price,
        # "category": category,  # دسته‌بندی محصول
        # "description": description,
        # "attributes": attributes
        # }
        self.product_repo.insert(new_product)
        return f"✅ محصول '{new_product['name']}' در دسته '{new_product['category']}' اضافه شد."

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

    async def show_products(self, update, context, products=None):
        """دریافت و نمایش لیست محصولات"""
        print("✅ متد show_products فراخوانی شد")  

        if products is None:
            products = list(self.product_repo.get_all())  # دریافت لیست محصولات

        if not products:
            if update.callback_query:  # اگر از طریق دکمه فراخوانی شده است
                await update.callback_query.message.reply_text("⚠️ هیچ محصولی یافت نشد!")
            else:  # اگر از طریق پیام متنی (`/show_products`) فراخوانی شده است
                await update.message.reply_text("⚠️ هیچ محصولی یافت نشد!")
            return

        for product in products:
            print(f"📦 محصول: {product['name']} - 📸 تصویر: {product.get('image_url', '❌ بدون تصویر')}")  

            text = f"🛍 {product['name']}\n💰 قیمت: {product['price']} تومان\nℹ️ {product.get('description', '')}"

            keyboard = [
                [
                    InlineKeyboardButton("➕ افزودن به سبد خرید", callback_data=f"add_{product['_id']}"),
                    InlineKeyboardButton("🔍 مشاهده اطلاعات محصول", callback_data=f"info_{product['_id']}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # بررسی ارسال از طریق پیام یا دکمه
            if update.callback_query:
                sender = update.callback_query.message  # از دکمه
            else:
                sender = update.message  # از پیام متنی

            if "image_url" in product and product["image_url"]:
                await sender.reply_photo(photo=product["image_url"], caption=text, reply_markup=reply_markup)
            else:
                await sender.reply_text(text, reply_markup=reply_markup)


    async def show_product_info(self, update, context):
        """نمایش اطلاعات کامل محصول"""
        query = update.callback_query
        await query.answer()

        product_id = query.data.replace("info_", "")  # استخراج ID محصول
        product = self.product_repo.get_by_id(product_id)  # دریافت اطلاعات محصول

        if not product:
            await query.message.reply_text("❌ محصول موردنظر یافت نشد!")
            return

        text = (
            f"🛍 نام محصول: {product['name']}\n"
            f"💰 قیمت: {product['price']} تومان\n"
            f"📂 دسته‌بندی: {product.get('category', 'نامشخص')}\n"
            f"ℹ توضیحات: {product.get('description', 'ندارد')}\n"
        )

        if "attributes" in product and product["attributes"]:
            text += "\n🔹 **ویژگی‌های محصول:**\n"
            for key, value in product["attributes"].items():
                text += f"• {key}: {value['value']} ({value['type']})\n"

        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ افزودن به سبد خرید", callback_data=f"add_{product_id}"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if "image_url" in product and product["image_url"]:
            await query.message.reply_photo(
                photo=product["image_url"], caption=text, reply_markup=reply_markup
            )
        else:
            await query.message.reply_text(text, reply_markup=reply_markup)

    async def show_categories(self, update, context):
        categories = self.product_repo.collection.distinct("category")

        if not categories:
            await update.message.reply_text("🚫 هیچ دسته‌ای یافت نشد!")
            return

        buttons = [
            [InlineKeyboardButton(cat, callback_data=f"category_{cat}")]
            for cat in categories
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(
            "📂 دسته‌بندی محصولات:", reply_markup=reply_markup
        )

    async def show_products_by_category(self, update, context):
        query = update.callback_query
        category = query.data.replace("category_", "")

        products = list(self.product_repo.get_all({"category": category}))
        await self.show_products(update, context, products)

    async def search_products(self, update, context):
        if len(context.args) < 1:
            await update.message.reply_text(
                "🔎 لطفاً نام محصول را وارد کنید.\nمثال:\n`/search گوشی`"
            )
            return

        search_text = " ".join(context.args)
        products = list(
            self.product_repo.get_all(
                {"name": {"$regex": search_text, "$options": "i"}}
            )
        )

        if not products:
            await update.message.reply_text(
                f"🚫 محصولی با نام '{search_text}' یافت نشد."
            )
            return

        for product in products:
            product_text = f"🛍 {product['name']}\n💰 قیمت: {product['price']} تومان\nℹ️ {product.get('description', '')}"

            # دکمه افزودن به سبد خرید
            keyboard = [
                [
                    InlineKeyboardButton(
                        "➕ افزودن به سبد خرید", callback_data=f"add_{product['_id']}"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(product_text, reply_markup=reply_markup)
