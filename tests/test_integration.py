import pytest
from services import UserService, ProductService, IMService, NotificationService

class TestIntegration:
    
    # --- 集成组 1: 用户发布商品全流程 (User + Product) ---
    def test_user_publish_flow(self):
        # 1. 初始化服务
        u_svc = UserService()
        p_svc = ProductService()
        
        # 2. 用户注册并登录
        seller = u_svc.register("138", "seller@i.com", "123", "Seller")
        buyer = u_svc.register("139", "buyer@i.com", "123", "Buyer")
        logged_in_buyer = u_svc.login("buyer@i.com", "123")
        
        # 3. 卖家发布商品
        product = p_svc.publish_product(seller, "Integration Item", "Desc", 99.0, "TestCat")
        
        # 4. 买家搜索该商品
        results = p_svc.search_products("Integration")
        
        # 5. 验证买家能搜到卖家发布的商品
        assert len(results) == 1
        assert results[0].seller.userId == seller.userId
        
        # 6. 买家收藏
        p_svc.add_to_favorites(logged_in_buyer, product)
        favs = p_svc.get_user_favorites(logged_in_buyer)
        assert product in favs

    # --- 集成组 2: 消息发送与通知 (User + IM + Notification) ---
    def test_im_notification_flow(self):
        # 1. 初始化服务
        u_svc = UserService()
        n_svc = NotificationService()
        im_svc = IMService(n_svc, u_svc) # 依赖注入
        
        # 2. 准备用户 (Receiver 处于离线状态)
        sender = u_svc.register("1", "s@i.com", "1", "Sender")
        receiver = u_svc.register("2", "r@i.com", "1", "Receiver")
        # receiver 不执行 login，所以 is_online 默认为 False
        
        # 3. 发送消息
        # 注意：这里会触发 NotificationService.trigger_push
        msg = im_svc.receive_message(sender, receiver.userId, "Hello Integration")
        
        # 4. 验证消息存储
        history = im_svc.get_chat_history(sender, receiver)
        assert len(history) == 1
        assert history[0].content == "Hello Integration"
        
        # 5. 验证副作用（查看是否生成了 notification.log 文件，验证资源泄露前的写操作）
        import os
        assert os.path.exists("notification.log")
        with open("notification.log", "r") as f:
            content = f.read()
            assert "Hello Integration" in content