import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from services import UserService, ProductService, IMService, NotificationService
from models import User, Product
from typing import Optional
import uuid

LARGE_FONT = ("Verdana", 12)
NORMAL_FONT = ("Verdana", 10)

class MarketplaceApp(tk.Tk):
    """主应用控制器"""
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("网络商场系统")
        self.geometry("800x600")

        self.user_service = UserService()
        self.product_service = ProductService()
        self.notification_service = NotificationService()
        self.im_service = IMService(self.notification_service, self.user_service)
        self.current_user: Optional[User] = None
        self._prepopulate_data()

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginRegisterPage, MainPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginRegisterPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if cont == MainPage and self.current_user:
             self.frames[MainPage].refresh()

    def _prepopulate_data(self):
        seller = self.user_service.register("13800138000", "seller@test.com", "123", "卖家小王")
        buyer = self.user_service.register("13900139000", "buyer@test.com", "123", "买家小李")
        self.product_service.publish_product(seller, "二手iPhone 15", "9成新，512GB，功能完好", 5000.0, "手机")
        self.product_service.publish_product(seller, "机械键盘", "青轴，带RGB灯效", 350.0, "电脑配件")
        self.product_service.publish_product(buyer, "闲置图书《代码大全》", "几乎全新，只翻过几次", 50.0, "图书")
        self.product_service.add_advertisement("双十一大促", "", "", "homepage_banner")

    def login(self, email, password):
        user = self.user_service.login(email, password)
        if user:
            self.current_user = user
            self.show_frame(MainPage)
        else:
            messagebox.showerror("登录失败", "邮箱或密码错误")
    
    def logout(self):
        self.user_service.logout(self.current_user)
        self.current_user = None
        self.show_frame(LoginRegisterPage)

class LoginRegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="欢迎来到网络商场", font=LARGE_FONT)
        label.pack(pady=20)

        login_frame = tk.Frame(self)
        tk.Label(login_frame, text="邮箱:", font=NORMAL_FONT).grid(row=0, column=0, padx=5, pady=5)
        self.login_email = tk.Entry(login_frame, font=NORMAL_FONT)
        self.login_email.grid(row=0, column=1, padx=5, pady=5)
        self.login_email.insert(0, "buyer@test.com") # 默认填充方便测试
        tk.Label(login_frame, text="密码:", font=NORMAL_FONT).grid(row=1, column=0, padx=5, pady=5)
        self.login_pass = tk.Entry(login_frame, show="*", font=NORMAL_FONT)
        self.login_pass.grid(row=1, column=1, padx=5, pady=5)
        self.login_pass.insert(0, "123") # 默认填充方便测试
        tk.Button(login_frame, text="登录", command=self.login, font=NORMAL_FONT).grid(row=2, columnspan=2, pady=10)
        login_frame.pack(pady=10)


    def login(self):
        email = self.login_email.get()
        password = self.login_pass.get()
        self.controller.login(email, password)

class MainPage(tk.Frame):
    """应用主页面"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.nav_frame = tk.Frame(self, bg="#f0f0f0", width=150)
        self.nav_frame.pack(side="left", fill="y")
        
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def refresh(self):
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

        tk.Label(self.nav_frame, text=f"你好, {self.controller.current_user.nickname}", bg="#f0f0f0", font=LARGE_FONT).pack(pady=10, padx=10)
        
        ttk.Button(self.nav_frame, text="主页/搜索", command=self.show_home).pack(fill="x", padx=5, pady=5)
        ttk.Button(self.nav_frame, text="发布商品", command=self.show_publish).pack(fill="x", padx=5, pady=5)
        ttk.Button(self.nav_frame, text="我的商品", command=self.show_my_products).pack(fill="x", padx=5, pady=5)
        ttk.Button(self.nav_frame, text="我的收藏", command=self.show_my_favorites).pack(fill="x", padx=5, pady=5)
        ttk.Button(self.nav_frame, text="即时通讯", command=self.show_chat).pack(fill="x", padx=5, pady=5)
        ttk.Button(self.nav_frame, text="个人资料", command=self.show_profile).pack(fill="x", padx=5, pady=5)
        ttk.Button(self.nav_frame, text="登出", command=self.controller.logout).pack(fill="x", padx=5, pady=5, side="bottom")

        self.show_home() 

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_content()
        ad = self.controller.product_service.get_advertisements_by_position("homepage_banner")[0]
        tk.Label(self.content_frame, text=ad.title, font=LARGE_FONT, fg="red").pack(fill="x")
        
        search_frame = tk.Frame(self.content_frame)
        self.search_entry = tk.Entry(search_frame, font=NORMAL_FONT, width=50)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="搜索", command=self.perform_search).pack(side="left")
        search_frame.pack(pady=10)

        self.product_listbox = tk.Listbox(self.content_frame, font=NORMAL_FONT)
        self.product_listbox.pack(fill="both", expand=True)
        self.product_listbox.bind('<Double-1>', self.show_product_details)
        self.perform_search() 

    def perform_search(self):
        query = self.search_entry.get()
        results = self.controller.product_service.search_products(query)
        self.product_listbox.delete(0, tk.END)
        self.product_data = {} 
        for p in results:
            display_text = f"{p.name} - ¥{p.price:.2f} (卖家: {p.seller.nickname})"
            self.product_listbox.insert(tk.END, display_text)
            self.product_data[display_text] = p
            
    def show_product_details(self, event):
        selected_text = self.product_listbox.get(self.product_listbox.curselection())
        product = self.product_data[selected_text]

        if messagebox.askyesno("商品详情", f"名称: {product.name}\n描述: {product.description}\n\n是否收藏该商品?"):
            self.controller.product_service.add_to_favorites(self.controller.current_user, product)
            messagebox.showinfo("成功", "商品已添加到您的收藏夹!")

    def show_publish(self):
        self.clear_content()
        tk.Label(self.content_frame, text="发布新商品", font=LARGE_FONT).pack()
        
        fields = ["商品名称:", "商品描述:", "价格:", "分类:"]
        self.entries = {}
        for field in fields:
            row = tk.Frame(self.content_frame)
            lab = tk.Label(row, width=15, text=field, anchor='w')
            ent = tk.Entry(row)
            row.pack(fill='x', padx=5, pady=5)
            lab.pack(side='left')
            ent.pack(side='right', expand=True, fill='x')
            self.entries[field] = ent
        
        ttk.Button(self.content_frame, text="确认发布", command=self.do_publish).pack(pady=10)
        
    def do_publish(self):
        name = self.entries["商品名称:"].get()
        desc = self.entries["商品描述:"].get()
        price = float(self.entries["价格:"].get())
        cat = self.entries["分类:"].get()
        if name and desc and price and cat:
            self.controller.product_service.publish_product(
                self.controller.current_user, name, desc, price, cat
            )
            messagebox.showinfo("成功", "商品发布成功！")
            self.show_my_products() # 跳转到我的商品页面
        else:
            messagebox.showerror("错误", "所有字段均为必填项！")

    def show_my_products(self):
        self.clear_content()
        tk.Label(self.content_frame, text="我发布的商品", font=LARGE_FONT).pack()
        listbox = tk.Listbox(self.content_frame, font=NORMAL_FONT)
        products = self.controller.product_service.get_products_by_seller(self.controller.current_user)
        for p in products:
            listbox.insert(tk.END, f"{p.name} - ¥{p.price:.2f}")
        listbox.pack(fill="both", expand=True)

    def show_my_favorites(self):
        self.clear_content()
        tk.Label(self.content_frame, text="我的收藏", font=LARGE_FONT).pack()
        listbox = tk.Listbox(self.content_frame, font=NORMAL_FONT)
        products = self.controller.product_service.get_user_favorites(self.controller.current_user)
        for p in products:
            listbox.insert(tk.END, f"{p.name} - ¥{p.price:.2f} (来自: {p.seller.nickname})")
        listbox.pack(fill="both", expand=True)

    def show_chat(self):
        self.clear_content()
        tk.Label(self.content_frame, text="即时通讯", font=LARGE_FONT).pack()

        chat_frame = tk.Frame(self.content_frame)
        chat_frame.pack(fill="both", expand=True)

        user_list_frame = tk.Frame(chat_frame)
        tk.Label(user_list_frame, text="选择聊天对象:").pack()
        self.user_listbox = tk.Listbox(user_list_frame)
        all_users = self.controller.user_service.get_all_users()
        self.chat_user_data = {}
        for u in all_users:
            if u.userId != self.controller.current_user.userId:
                self.user_listbox.insert(tk.END, u.nickname)
                self.chat_user_data[u.nickname] = u
        self.user_listbox.bind("<<ListboxSelect>>", self.load_chat_history)
        self.user_listbox.pack(fill="y", expand=True)
        user_list_frame.pack(side="left", fill="y", padx=5)

        chat_window_frame = tk.Frame(chat_frame)
        self.chat_history = tk.Text(chat_window_frame, state='disabled', width=60, height=20)
        self.chat_history.pack(fill="both", expand=True)
        
        input_frame = tk.Frame(chat_window_frame)
        self.chat_input = tk.Entry(input_frame, width=50)
        self.chat_send_button = ttk.Button(input_frame, text="发送", command=self.send_message, state='disabled')
        self.chat_input.pack(side="left", fill="x", expand=True)
        self.chat_send_button.pack(side="right")
        input_frame.pack(fill="x")
        chat_window_frame.pack(side="left", fill="both", expand=True)
        
    def load_chat_history(self, event):
        selection = self.user_listbox.curselection()
        if not selection: return
        
        target_nickname = self.user_listbox.get(selection[0])
        target_user = self.chat_user_data[target_nickname]
        self.current_chat_partner = target_user 
        
        history = self.controller.im_service.get_chat_history(self.controller.current_user, target_user)
        
        self.chat_history.config(state='normal')
        self.chat_history.delete('1.0', tk.END)
        for msg in history:
            self.chat_history.insert(tk.END, f"{msg.sender.nickname} ({msg.sentAt.strftime('%H:%M:%S')}):\n{msg.content}\n\n")
        self.chat_history.config(state='disabled')
        self.chat_send_button.config(state='normal')
        
    def send_message(self):
        content = self.chat_input.get()
        if not content or not self.current_chat_partner: return
        
        msg = self.controller.im_service.receive_message(self.controller.current_user, self.current_chat_partner.userId, content)
        if msg:
            self.chat_history.config(state='normal')
            self.chat_history.insert(tk.END, f"{msg.sender.nickname} ({msg.sentAt.strftime('%H:%M:%S')}):\n{msg.content}\n\n")
            self.chat_history.config(state='disabled')
            self.chat_input.delete(0, tk.END)
    
    def show_profile(self):
        self.clear_content()
        tk.Label(self.content_frame, text="个人资料", font=LARGE_FONT).pack(pady=10)
        user = self.controller.current_user
        
        tk.Label(self.content_frame, text=f"邮箱: {user.email}", font=NORMAL_FONT).pack()
        tk.Label(self.content_frame, text=f"手机号: {user.phone}", font=NORMAL_FONT).pack()
        
        def update_nickname():
            new_name = simpledialog.askstring("修改昵称", "请输入新的昵称:", parent=self.content_frame)
            if new_name:
                user.update_profile(nickname=new_name)
                messagebox.showinfo("成功", "昵称已更新！")
                self.controller.frames[MainPage].refresh()

        ttk.Button(self.content_frame, text="修改昵称", command=update_nickname).pack(pady=20)

if __name__ == "__main__":
    app = MarketplaceApp()
    app.mainloop()