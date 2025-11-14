import threading
import queue
import time
import sys
from socket import socket
from typing import List, Tuple

#任务队列,用户线程间通信,分发端口
port_queue = queue.Queue()
#线程锁
print_lock = threading.Lock()

open_ports: List[int] = []
TARGET_IP = "127.0.0.1"  # 目标IP地址
PORT_RANGE = (1, 1024)   # 扫描的端口范围 (例如：1 到 1024)
THREAD_COUNT = 50        # 并发执行的线程数量
SCAN_TIMEOUT = 0.5       # Socket 连接超时时间（秒）
def port_scanner_worker():
    thread_name = threading.current_thread().name
    print_with_lock(f"[{thread_name}] Starting")

    while True:
        try:
            #从队列中获取一个端口,如果队列为空,阻塞端口
            port = port_queue.get(timeout=5,block=True)
        except queue.Empty:
            #如果在等待时间内队列仍为空,直接退出
            break
        except Exception as e:
            print_with_lock(f"[{thread_name}]发生异常{e}")
            break
        if scan_port(port):
            with print_lock:
                open_ports.append(port)
        port_queue.task_done()

def scan_port(port: int) -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((TARGET_IP, port))
        if result == 0:
            print_with_lock(f"[+] Port {port} is open")
            return True
        else:
            return False
    except socket.error as e:
        return False
    finally:
        if "s" in locals():
            s.close()

def print_with_lock(msg:str):
    with print_lock:
        print(msg)
        sys.stdout.flush()

def main():
    print_with_lock("[+] Starting")
    print_with_lock("[+] Scanning...")

    start_time = time.time()
    threads: List[threading.Thread] = []
    for i in range(THREAD_COUNT):
        t = threading.Thread(target=port_scanner_worker,name=f"Worker{i+1},",daemon=True)
        threads.append(t)
        t.start()
    print_with_lock(f"{THREAD_COUNT} threads started")
    #预留端口列表参数
    for port in range(PORT_RANGE[0], PORT_RANGE[1]+1):
        port_queue.put(port)
    print_with_lock(f"[+] 已将{port_queue.qsize()}个端口放入队列")
    try:
        port_queue.join()
    except KeyboardInterrupt:
        print_with_lock("\n用户终端,正常尝试优雅退出...")
        sys.exit(1)
    end_time = time.time()
    open_ports.sort()

    print_with_lock("\n" + "="*40)
    print_with_lock("扫描完成！")
    print_with_lock(f"总耗时: {end_time - start_time:.2f} 秒")
    print_with_lock(f"发现 {len(open_ports)} 个开放端口：{open_ports}")
    print_with_lock("="*40)

if __name__ == "__main__":
    main()