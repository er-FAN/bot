from bson import ObjectId
from pymongo import MongoClient
from typing import TypeVar, Generic, Dict, Any, List

T = TypeVar("T")


class GenericRepository(Generic[T]):
    def __init__(self, collection_name: str):
        client = MongoClient("mongodb://localhost:27017/")
        db = client["telegram_bot_db"]  # نام دیتابیس
        self.collection = db[collection_name]

    def insert(self, item: Dict[str, Any]) -> Any:
        """ایجاد یک سند جدید"""
        result = self.collection.insert_one(item)
        return result.inserted_id

    def get_by_id(self, item_id: Any) -> Dict[str, Any] | None:
        """دریافت یک سند با آیدی"""
        return self.collection.find_one({"_id": ObjectId(item_id)})

    def get_all(self, filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """دریافت تمام اسناد به‌صورت لیست"""
        if filter_dict is None:
            filter_dict = {}  # اگر هیچ فیلتری ارسال نشود، همه داده‌ها را برگردان

        return list(self.collection.find(filter_dict))

    def update(self, entity_id, update_fields):
        """بروزرسانی یک موجودیت بر اساس `entity_id`"""
        return self.collection.update_one(
            {"_id": ObjectId(entity_id)},  # جستجوی موجودیت بر اساس `_id`
            {"$set": update_fields},  # اعمال تغییرات
        )

    def delete(self, item_id: Any) -> bool:
        """حذف یک سند با آیدی"""
        result = self.collection.delete_one({"_id": item_id})
        return result.deleted_count > 0
