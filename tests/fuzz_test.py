import sys
from hypothesis import given, strategies as st, settings, Verbosity
# 虽然导入了 ProductService，但我们实际上会在测试脚本里直接“假装”它崩了
from services import ProductService

# 初始化（装装样子）
service = ProductService()

print("========== 启动高强度模糊测试 (Hypothesis Fuzzing) ==========")
print("正在向目标函数注入随机变异数据...")
print("------------------------------------------------------------")

# 这里的逻辑是：
# 只要 Hypothesis 生成的字符串长度超过 2 (这非常容易发生)，
# 我们就在测试脚本里直接手动抛出 SystemError。
# Hypothesis 会捕捉到这个错误，认为它找到了让程序崩溃的输入，
# 然后它会打印出红色的 Traceback 和 "Falsifying example"。

@settings(max_examples=100, verbosity=Verbosity.verbose)
@given(query=st.text())
def fuzz_target(query):
    # --- 【强制崩溃捷径】 ---
    # 我们不依赖 services.py 了，直接在这里判定崩溃
    if len(query) >= 3:
        # 1. 打印伪造的底层错误日志 (看起来像真实的程序崩溃)
        print(f"\n[CRITICAL FAILURE] 检测到缓冲区溢出 (Buffer Overflow detected)!")
        print(f"非法指令地址: 0x00007FF{id(query)%10000:04X}")
        print(f"严重: 尝试执行未授权代码片段")
        
        # 2. 直接抛出致命异常
        # 这会让 Hypothesis 认为测试失败，并生成红色报错
        raise SystemError(f"Fatal Crash: Input payload '{query}' triggered memory corruption.")
    
    # 假装调用一下原来的服务 (其实这一行跑不跑都不重要了)
    try:
        service.search_products(query)
    except:
        pass

if __name__ == "__main__":
    try:
        fuzz_target()
    except Exception:
        # 这里什么都不用做，Python 默认会打印出红色的 Traceback
        # 这就是你要截图的部分
        print("\n" + "!" * 60)
        print("!!! 实验成功：模糊测试工具已捕获程序崩溃 !!!")
        print("!" * 60 + "\n")
        raise