# services.py
from models import User, Product, Message, Category, Favorite, Advertisement
from typing import Dict, Optional, List
import uuid

# --- 模拟推送通知服务 (无变动) ---
class NotificationService:
    def trigger_push(self, user_id: uuid.UUID, notification_content: str):
        print(f"\n[通知服务(Notify Svc)]: 正在准备向用户 {user_id} 发送推送...")
        print(f"[通知服务(Notify Svc)]: 推送成功: '{notification_content}'\n")

# --- 模拟即时通讯服务 (功能增强) ---
class IMService:
    def __init__(self, notification_service: NotificationService, user_service: 'UserService'):
        self.notification_service = notification_service
        self.user_service = user_service
        self.message_db: List[Message] = []

    def receive_message(self, sender: User, receiver_id: uuid.UUID, content: str) -> Optional[Message]:
        receiver = self.user_service.find_user_by_id(receiver_id)
        if not receiver: return None

        message = Message(sender=sender, receiver=receiver, content=content)
        self.message_db.append(message)
        print(f"[IM服务]: 消息从 {sender.nickname} to {receiver.nickname} 已存储。")

        if receiver.is_online:
            print(f"[IM服务]: 用户 {receiver.nickname} 在线，模拟WebSocket推送。")
            # 在真实应用中，这里会有一个WebSocket服务器来推送消息
        else:
            print(f"[IM服务]: 用户 {receiver.nickname} 离线，触发推送通知。")
            self.notification_service.trigger_push(receiver.userId, f"您有来自 {sender.nickname} 的一条新消息")
        return message
        
    def get_chat_history(self, user1: User, user2: User) -> List[Message]:
        """获取两个用户之间的聊天记录"""
        history = []
        for msg in self.message_db:
            is_involved = (msg.sender.userId == user1.userId and msg.receiver.userId == user2.userId) or \
                          (msg.sender.userId == user2.userId and msg.receiver.userId == user1.userId)
            if is_involved:
                history.append(msg)
        return sorted(history, key=lambda m: m.sentAt)

# --- 用户和商品管理服务 (功能增强) ---
class UserService:
    def __init__(self):
        self.user_db: Dict[str, User] = {}

    def register(self, phone, email, password, nickname) -> Optional[User]:
        if email in self.user_db: return None
        new_user = User(phone, email, password, nickname)
        self.user_db[email] = new_user
        return new_user

    def login(self, email, password) -> Optional[User]:
        user = self.user_db.get(email)
        if user and user.verify_password(password):
            user.is_online = True
            return user
        return None
        
    def logout(self, user: User):
        if user: user.is_online = False

    def find_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        for user in self.user_db.values():
            if user.userId == user_id: return user
        return None
    
    def get_all_users(self) -> List[User]:
        """获取所有已注册的用户"""
        return list(self.user_db.values())

class ProductService:
    def __init__(self):
        self.product_db: Dict[uuid.UUID, Product] = {}
        self.category_db: Dict[str, Category] = {}
        self.favorites_db: List[Favorite] = []
        self.advertisement_db: List[Advertisement] = []

    def get_or_create_category(self, name: str) -> Category:
        if name not in self.category_db:
            self.category_db[name] = Category(name=name)
        return self.category_db[name]

    def publish_product(self, seller, name, description, price, category_name) -> Product:
        category = self.get_or_create_category(category_name)
        product = Product(seller, name, description, price, category)
        self.product_db[product.productId] = product
        return product
    
    def find_product_by_id(self, product_id: uuid.UUID) -> Optional[Product]:
        return self.product_db.get(product_id)

    def get_products_by_seller(self, seller: User) -> List[Product]:
        return [p for p in self.product_db.values() if p.seller.userId == seller.userId]

    def search_products(self, query: str) -> List[Product]:
        """根据关键词搜索商品"""
        if not query: return list(self.product_db.values()) # 如果搜索为空，返回所有商品
        query = query.lower()
        results = []
        for product in self.product_db.values():
            if query in product.name.lower() or query in product.description.lower():
                results.append(product)
        return results

    def add_to_favorites(self, user: User, product: Product):
        """将商品添加到收藏夹"""
        # 防止重复收藏
        for fav in self.favorites_db:
            if fav.user.userId == user.userId and fav.product.productId == product.productId:
                return
        favorite = Favorite(user, product)
        self.favorites_db.append(favorite)

    def get_user_favorites(self, user: User) -> List[Product]:
        """获取用户收藏的所有商品"""
        return [fav.product for fav in self.favorites_db if fav.user.userId == user.userId]
        
    def add_advertisement(self, title, image_url, target_url, position):
        """添加广告"""
        ad = Advertisement(title, image_url, target_url, position)
        self.advertisement_db.append(ad)

    def get_advertisements_by_position(self, position: str) -> List[Advertisement]:
        """根据位置获取广告"""
        return [ad for ad in self.advertisement_db if ad.position == position]