from repository import GenericRepository
from datetime import datetime

class OrderService:
    def __init__(self):
        self.order_repo = GenericRepository("orders")  # کالکشن سفارشات

    def create_order(self, user_id: int, cart: list):
        """ایجاد سفارش جدید (بدون پرداخت)"""
        if not cart:
            return "❌ سبد خرید شما خالی است! ابتدا محصولی به سبد اضافه کنید.", None
        
        order_data = {
            "user_id": user_id,
            "items": cart,
            "status": "منتظر پرداخت",
            "created_at": datetime.utcnow()
        }
        order_id = self.order_repo.insert(order_data)
        payment_link = self.generate_payment_link(str(order_id))

        return f"✅ سفارش شما ایجاد شد! لطفاً روی دکمه زیر کلیک کنید و پرداخت را انجام دهید.", payment_link

    def get_orders(self, user_id: int):
        """دریافت لیست سفارش‌های کاربر"""
        orders = self.order_repo.get_all()
        user_orders = [o for o in orders if o["user_id"] == user_id]
        if not user_orders:
            return "ℹ️ شما هیچ سفارشی ثبت نکرده‌اید."

        result = []
        for order in user_orders:
            order["_id"] = str(order["_id"])  # تبدیل ObjectId به رشته
            items = "\n".join([f"- {p['name']} ({p['price']} تومان)" for p in order["items"]])
            result.append(f"🆔 سفارش: {order['_id']}\n📦 وضعیت: {order['status']}\n🛒 محصولات:\n{items}")
        
        return "\n\n".join(result)

    def update_order_status(self, order_id: str, new_status: str) -> str:
        """بروزرسانی وضعیت سفارش"""
        if self.order_repo.update(order_id, {"status": new_status}):
            return f"✅ وضعیت سفارش {order_id} به '{new_status}' تغییر کرد."
        return "⚠️ خطا در تغییر وضعیت سفارش!"
    

    def generate_payment_link(self, order_id: str) -> str:
        """تولید لینک پرداخت (فعلاً به صورت تستی)"""
        return f"https://www.example.com/payment/{order_id}"  # در آینده این را به درگاه زرین‌پال متصل می‌کنیم