# -*- coding: utf-8 -*-

import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 导入现有模块
from check_proxy import check_proxy
import github_api
import proxyFetcher

class RealTimeProxyChecker:
    def __init__(self, token=""):
        self.token = token
        self.valid_proxies = []
        self.checked_count = 0
        self.total_count = 0
        self.start_time = None
        
    def print_status(self, message):
        """打印带时间戳的状态信息"""
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[{current_time}] {message}", flush=True)
        
    def get_proxy_list(self):
        """获取代理列表"""
        self.print_status("正在获取代理列表...")
        
        try:
            # 尝试从GitHub获取现有代理
            if self.token:
                self.print_status("从GitHub获取现有代理列表...")
                con = github_api.get_content("parserpp", "ip_ports", "/proxyinfo.txt", self.token)
                proxy_list = [proxy.strip() for proxy in con.split("\n") if proxy.strip()]
                self.print_status(f"从GitHub获取到 {len(proxy_list)} 个代理")
            else:
                proxy_list = []
        except Exception as e:
            self.print_status(f"从GitHub获取代理失败: {e}")
            proxy_list = []
            
        # 从本地文件获取（如果存在）
        if os.path.exists("proxyData.txt"):
            self.print_status("从本地文件获取代理...")
            with open("proxyData.txt", "r") as f:
                local_proxies = [line.strip() for line in f.readlines() if line.strip()]
                proxy_list.extend(local_proxies)
                self.print_status(f"从本地文件获取到 {len(local_proxies)} 个代理")
        
        # 去重
        proxy_list = list(set(proxy_list))
        self.print_status(f"去重后共有 {len(proxy_list)} 个代理待检查")
        
        return proxy_list
    
    def get_fresh_proxies(self):
        """获取新的代理（从各个代理网站抓取）"""
        self.print_status("正在从各个代理网站获取新代理...")
        fresh_proxies = []
        proxy_set = set()  # 使用set进行去重，提高效率
        
        # 获取新代理的函数列表
        proxy_functions = [
            proxyFetcher.freeProxy01,
            proxyFetcher.freeProxy02,
            proxyFetcher.freeProxy03,
            proxyFetcher.freeProxy04,
            proxyFetcher.freeProxy05,
            proxyFetcher.freeProxy06,
            proxyFetcher.freeProxy07,
            proxyFetcher.freeProxy08,
            proxyFetcher.freeProxy09,
            proxyFetcher.freeProxy10,
            proxyFetcher.freeProxy11,
            proxyFetcher.freeProxy12,
            proxyFetcher.freeProxy13,
            proxyFetcher.freeProxy14,
            proxyFetcher.freeProxy15,
        ]
        
        for func in proxy_functions:
            try:
                func_name = func.__name__
                self.print_status(f"正在获取 {func_name} 的代理...")
                count_before = len(proxy_set)
                for proxy in func():
                    if proxy and proxy not in proxy_set:
                        proxy_set.add(proxy)
                        fresh_proxies.append(proxy)
                        self.print_status(f"发现新代理: {proxy}")
                count_after = len(proxy_set)
                self.print_status(f"{func_name} 获取到 {count_after - count_before} 个新代理")
            except Exception as e:
                self.print_status(f"获取 {func.__name__} 代理时出错: {e}")
                
        self.print_status(f"去重后共获取到 {len(fresh_proxies)} 个新代理")
        return fresh_proxies
    
    def check_single_proxy(self, proxy):
        """检查单个代理"""
        try:
            if check_proxy(proxy):
                self.valid_proxies.append(proxy)
                self.print_status(f"✅ 可用代理: {proxy}")
                # 实时保存可用代理到文件
                with open("valid_proxies.txt", "a", encoding="utf-8") as f:
                    f.write(f"{proxy}\n")
                return True
            else:
                self.print_status(f"❌ 无效代理: {proxy}")
                return False
        except Exception as e:
            self.print_status(f"❌ 检查代理 {proxy} 时出错: {e}")
            return False
        finally:
            self.checked_count += 1
            # 显示进度
            if self.total_count > 0:
                progress = (self.checked_count / self.total_count) * 100
                elapsed = time.time() - self.start_time
                avg_time = elapsed / self.checked_count if self.checked_count > 0 else 0
                remaining = (self.total_count - self.checked_count) * avg_time
                
                self.print_status(f"进度: {self.checked_count}/{self.total_count} ({progress:.1f}%) | "
                               f"可用: {len(self.valid_proxies)} | "
                               f"预计剩余: {remaining/60:.1f}分钟")
    
    def check_proxies_batch(self, proxy_list, max_workers=50):
        """批量检查代理"""
        self.total_count = len(proxy_list)
        self.checked_count = 0
        self.valid_proxies = []
        self.start_time = time.time()
        
        # 清空之前的结果文件（旧代理清理机制）
        self.print_status("清理旧代理数据...")
        with open("valid_proxies.txt", "w", encoding="utf-8") as f:
            f.write("")  # 清空文件，移除所有旧代理
            
        self.print_status(f"开始检查 {self.total_count} 个代理，使用 {max_workers} 个线程...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_proxy = {executor.submit(self.check_single_proxy, proxy): proxy 
                             for proxy in proxy_list}
            
            # 等待完成
            for future in as_completed(future_to_proxy):
                pass
                
        elapsed = time.time() - self.start_time
        self.print_status(f"检查完成！耗时: {elapsed/60:.1f}分钟")
        self.print_status(f"总计检查: {self.checked_count} 个代理")
        self.print_status(f"可用代理: {len(self.valid_proxies)} 个")
        
        return self.valid_proxies
    
    def run_continuous_check(self):
        """持续运行模式：获取新代理并实时检查"""
        self.print_status("启动持续检查模式...")
        
        while True:
            try:
                # 获取新代理
                fresh_proxies = self.get_fresh_proxies()
                
                if fresh_proxies:
                    # 检查新获取的代理
                    self.check_proxies_batch(fresh_proxies, max_workers=30)
                else:
                    self.print_status("未获取到新代理，等待5分钟后重试...")
                    
                # 等待一段时间再获取新代理
                self.print_status("等待5分钟后获取新一批代理...")
                time.sleep(300)  # 5分钟
                
            except KeyboardInterrupt:
                self.print_status("用户中断，停止检查")
                break
            except Exception as e:
                self.print_status(f"运行时出错: {e}")
                time.sleep(60)  # 出错后等待1分钟

def main():
    print("=== 实时代理检查器 ===", flush=True)
    
    # 获取token
    token = ""
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = os.getenv('GITHUB_TOKEN', "")
    
    checker = RealTimeProxyChecker(token)
    
    # 检查是否在CI/CD环境中（非交互式）
    if not sys.stdin.isatty():
        # 非交互环境，直接运行获取新代理并检查
        print("检测到非交互环境，自动运行代理获取和检查...", flush=True)
        fresh_proxies = checker.get_fresh_proxies()
        if fresh_proxies:
            checker.check_proxies_batch(fresh_proxies)
            print(f"成功检查了 {len(checker.valid_proxies)} 个有效代理", flush=True)
        else:
            print("未获取到新代理", flush=True)
        return
    
    # 交互式环境
    print("1. 检查现有代理列表")
    print("2. 获取并检查新代理")
    print("3. 持续模式（不断获取新代理并检查）")
    
    choice = input("请选择模式 (1/2/3): ").strip()
    
    if choice == "1":
        # 检查现有代理
        proxy_list = checker.get_proxy_list()
        if proxy_list:
            checker.check_proxies_batch(proxy_list)
        else:
            print("没有找到现有代理列表")
            
    elif choice == "2":
        # 获取新代理并检查
        fresh_proxies = checker.get_fresh_proxies()
        if fresh_proxies:
            checker.check_proxies_batch(fresh_proxies)
        else:
            print("未获取到新代理")
            
    elif choice == "3":
        # 持续模式
        checker.run_continuous_check()
    else:
        print("无效选择")

if __name__ == '__main__':
    main() 