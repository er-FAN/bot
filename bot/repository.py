from pymongo import MongoClient
from typing import TypeVar, Generic, Dict, Any, List

T = TypeVar('T')

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
        return self.collection.find_one({"_id": item_id})

    def get_all(self) -> List[Dict[str, Any]]:
        """دریافت تمام اسناد"""
        return list(self.collection.find())

    def update(self, item_id: Any, updated_item: Dict[str, Any]) -> bool:
        """بروزرسانی یک سند با آیدی"""
        result = self.collection.update_one({"_id": item_id}, {"$set": updated_item})
        return result.modified_count > 0

    def delete(self, item_id: Any) -> bool:
        """حذف یک سند با آیدی"""
        result = self.collection.delete_one({"_id": item_id})
        return result.deleted_count > 0

