import pytest
from services import UserService, ProductService
from models import User

# --- 子功能 1: UserService 测试 ---

@pytest.fixture
def user_service():
    return UserService()

def test_register_success(user_service):
    """测试正常注册"""
    user = user_service.register("13800000000", "test@test.com", "123456", "TestUser")
    assert user is not None
    assert user.email == "test@test.com"
    assert user.nickname == "TestUser"

def test_register_duplicate(user_service):
    """测试重复注册"""
    user_service.register("13800000000", "test@test.com", "123456", "TestUser")
    user2 = user_service.register("13900000000", "test@test.com", "654321", "User2")
    assert user2 is None  # 邮箱重复应返回 None

def test_login_success(user_service):
    """测试登录成功"""
    user_service.register("13800000000", "login@test.com", "123456", "LoginUser")
    user = user_service.login("login@test.com", "123456")
    assert user is not None
    assert user.is_online is True

def test_login_fail_password(user_service):
    """测试密码错误"""
    user_service.register("13800000000", "fail@test.com", "123456", "FailUser")
    user = user_service.login("fail@test.com", "wrongpass")
    assert user is None

def test_login_fail_user_not_found(user_service):
    """测试用户不存在"""
    user = user_service.login("unknown@test.com", "123456")
    assert user is None

def test_find_user_by_id(user_service):
    """测试ID查找"""
    u = user_service.register("1", "id@test.com", "1", "IDUser")
    found = user_service.find_user_by_id(u.userId)
    assert found == u

# --- 子功能 2: ProductService 测试 ---

@pytest.fixture
def product_service():
    return ProductService()

@pytest.fixture
def sample_user():
    return User("1", "seller@test.com", "1", "Seller")

def test_publish_product(product_service, sample_user):
    """测试发布商品"""
    prod = product_service.publish_product(sample_user, "Phone", "Old phone", 100.0, "Electronics")
    assert prod.name == "Phone"
    assert prod.price == 100.0
    assert prod.productId in product_service.product_db

def test_search_product_hit(product_service, sample_user):
    """测试搜索命中"""
    product_service.publish_product(sample_user, "iPhone 15", "New", 5000.0, "Mobile")
    results = product_service.search_products("iPhone")
    assert len(results) == 1
    assert results[0].name == "iPhone 15"

def test_search_product_miss(product_service, sample_user):
    """测试搜索未命中"""
    product_service.publish_product(sample_user, "MacBook", "Pro", 10000.0, "Laptop")
    results = product_service.search_products("Android")
    assert len(results) == 0

def test_search_empty(product_service, sample_user):
    """测试空搜索返回所有"""
    product_service.publish_product(sample_user, "A", "A", 1, "C")
    product_service.publish_product(sample_user, "B", "B", 1, "C")
    results = product_service.search_products("")
    assert len(results) == 2

def test_add_favorites(product_service, sample_user):
    """测试收藏功能"""
    prod = product_service.publish_product(sample_user, "FavItem", "Desc", 10.0, "Cat")
    product_service.add_to_favorites(sample_user, prod)
    favs = product_service.get_user_favorites(sample_user)
    assert len(favs) == 1
    assert favs[0] == prod