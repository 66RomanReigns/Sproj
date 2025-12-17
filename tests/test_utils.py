import pytest
from services import UserService, ProductService, IMService, NotificationService
from models import User
import uuid

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

def test_logout_sets_user_offline(user_service):
    user_service.register("13800000000", "logout@test.com", "123456", "LogoutUser")
    user = user_service.login("logout@test.com", "123456")
    assert user is not None
    assert user.is_online is True
    user_service.logout(user)
    assert user.is_online is False

def test_get_all_users_and_find_user_not_found(user_service):
    user_service.register("1", "a@test.com", "1", "A")
    user_service.register("2", "b@test.com", "1", "B")
    users = user_service.get_all_users()
    assert len(users) == 2
    assert user_service.find_user_by_id(uuid.uuid4()) is None

def test_notification_service_writes_log(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = NotificationService()
    user_id = uuid.uuid4()
    svc.trigger_push(user_id, "Ping")
    log_path = tmp_path / "notification.log"
    assert log_path.exists()
    assert "Ping" in log_path.read_text(encoding="utf-8")

def test_im_offline_triggers_notification_and_history(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    u_svc = UserService()
    n_svc = NotificationService()
    im_svc = IMService(n_svc, u_svc)

    sender = u_svc.register("1", "im_s@test.com", "1", "Sender")
    receiver = u_svc.register("2", "im_r@test.com", "1", "Receiver")

    msg = im_svc.receive_message(sender, receiver.userId, "Hello IM")
    assert msg is not None
    assert msg.content == "Hello IM"

    history = im_svc.get_chat_history(sender, receiver)
    assert len(history) == 1
    assert history[0].content == "Hello IM"

    log_path = tmp_path / "notification.log"
    assert log_path.exists()
    assert "Hello IM" in log_path.read_text(encoding="utf-8")

def test_im_receiver_not_found_returns_none(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    u_svc = UserService()
    n_svc = NotificationService()
    im_svc = IMService(n_svc, u_svc)
    sender = u_svc.register("1", "im_s2@test.com", "1", "Sender")
    msg = im_svc.receive_message(sender, uuid.uuid4(), "X")
    assert msg is None

def test_im_online_does_not_create_notification_log(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    u_svc = UserService()
    n_svc = NotificationService()
    im_svc = IMService(n_svc, u_svc)

    sender = u_svc.register("1", "im_s3@test.com", "1", "Sender")
    receiver = u_svc.register("2", "im_r3@test.com", "1", "Receiver")
    u_svc.login("im_r3@test.com", "1")

    msg = im_svc.receive_message(sender, receiver.userId, "Hello Online")
    assert msg is not None
    assert not (tmp_path / "notification.log").exists()

def test_find_product_by_id_and_get_products_by_seller(product_service):
    seller1 = User("1", "seller1@test.com", "1", "S1")
    seller2 = User("2", "seller2@test.com", "1", "S2")
    p1 = product_service.publish_product(seller1, "P1", "D1", 1.0, "C1")
    p2 = product_service.publish_product(seller2, "P2", "D2", 2.0, "C2")

    assert product_service.find_product_by_id(p1.productId) == p1
    assert product_service.find_product_by_id(uuid.uuid4()) is None

    seller1_products = product_service.get_products_by_seller(seller1)
    assert p1 in seller1_products
    assert p2 not in seller1_products

def test_add_to_favorites_duplicate_does_not_add_twice(product_service):
    user = User("1", "favdup@test.com", "1", "U")
    prod = product_service.publish_product(user, "Dup", "D", 1.0, "C")
    product_service.add_to_favorites(user, prod)
    product_service.add_to_favorites(user, prod)
    favs = product_service.get_user_favorites(user)
    assert len(favs) == 1

def test_search_products_eval_exception_path(product_service):
    seller = User("1", "eval@test.com", "1", "U")
    product_service.publish_product(seller, "Alpha", "Beta", 1.0, "C")
    results = product_service.search_products("a'b")
    assert isinstance(results, list)

def test_advertisement_add_and_filter(product_service):
    product_service.add_advertisement("A1", "", "", "home")
    product_service.add_advertisement("A2", "", "", "home")
    product_service.add_advertisement("B1", "", "", "side")
    home_ads = product_service.get_advertisements_by_position("home")
    side_ads = product_service.get_advertisements_by_position("side")
    assert len(home_ads) == 2
    assert len(side_ads) == 1
