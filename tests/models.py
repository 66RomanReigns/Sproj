# models.py
import uuid
from datetime import datetime
from enum import Enum

def simple_hash(password: str) -> str:
    return f"hashed_{password}"

class ProductStatus(Enum):
    ON_SALE = "ON_SALE"
    SOLD_OUT = "SOLD_OUT"
    REMOVED = "REMOVED"

class ContentType(Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"

class Permission:
    def __init__(self, permission_key: str):
        self.permissionId: uuid.UUID = uuid.uuid4()
        self.permissionKey: str = permission_key 

class Role:
    #植入点，可变默认参数，列表[]在函数定义的时候被创建一次，所有使用默认参数的Role实例将共享同一个permission列表
    def __init__(self, role_name: str, permissions=[]):
        self.roleId: uuid.UUID = uuid.uuid4()
        self.roleName: str = role_name 
        #self.permissions: list[Permission] = []
        self.permissions = permissions

    def add_permission(self, permission: Permission):
        if permission not in self.permissions:
            self.permissions.append(permission)

class User:
    def __init__(self, phone: str, email: str, password: str, nickname: str):
        self.userId: uuid.UUID = uuid.uuid4()
        self.phone: str = phone
        self.email: str = email
        self.passwordHash: str = simple_hash(password)
        self.nickname: str = nickname
        self.avatarUrl: str = "default_avatar.png"
        self.is_online: bool = False 

    def verify_password(self, password: str) -> bool:
        return self.passwordHash == simple_hash(password)

    def update_profile(self, nickname: str = None, avatar_url: str = None):
        if nickname:
            self.nickname = nickname
        if avatar_url:
            self.avatarUrl = avatar_url
        print(f"用户 {self.nickname} 的资料已更新。")

class AdminUser:
    def __init__(self, username: str, password: str):
        self.adminId: uuid.UUID = uuid.uuid4()
        self.username: str = username
        self.passwordHash: str = simple_hash(password)
        self.roles: list[Role] = []

    def assign_role(self, role: Role):
        if role not in self.roles:
            self.roles.append(role)

class Category:
    def __init__(self, name: str, parent_id: uuid.UUID = None):
        self.categoryId: uuid.UUID = uuid.uuid4()
        self.name: str = name
        self.parentId: uuid.UUID = parent_id 

class ProductImage:
    def __init__(self, image_url: str):
        self.imageId: uuid.UUID = uuid.uuid4()
        self.imageUrl: str = image_url

class Product:
    def __init__(self, seller: User, name: str, description: str, price: float, category: Category):
        self.productId: uuid.UUID = uuid.uuid4()
        self.seller: User = seller 
        self.name: str = name
        self.description: str = description
        self.price: float = price
        self.status: ProductStatus = ProductStatus.ON_SALE
        self.category: Category = category
        self.images: list[ProductImage] = []

    def add_image(self, image_url: str):
        image = ProductImage(image_url)
        self.images.append(image)

    def update(self, name: str = None, description: str = None, price: float = None):
        if name:
            self.name = name
        if description:
            self.description = description
        if price:
            self.price = price
        print(f"商品 '{self.name}' 信息已更新。")

class Favorite:
    def __init__(self, user: User, product: Product):
        self.user: User = user
        self.product: Product = product
        self.addedAt: datetime = datetime.now()

class Message:
    def __init__(self, sender: User, receiver: User, content: str, content_type: ContentType = ContentType.TEXT):
        self.messageId: uuid.UUID = uuid.uuid4()
        self.sender: User = sender
        self.receiver: User = receiver
        self.content: str = content
        self.sentAt: datetime = datetime.now()
        self.contentType: ContentType = content_type

class Advertisement:
    def __init__(self, title: str, image_url: str, target_url: str, position: str):
        self.adId: uuid.UUID = uuid.uuid4()
        self.title: str = title
        self.imageUrl: str = image_url
        self.targetUrl: str = target_url
        self.position: str = position 