import threading
import queue
import requests
import sys
from typing import List

q = queue.Queue()
url = "http://127.0.0.1:8000"
urls = [url] * 1000
ThreadCount = 50
print_lock = threading.Lock()
def thread_request():
    thread_name = threading.current_thread().name
    print_with_lock(f"[{thread_name} 启动!]")
    # print_with_lock()
    while True:
        task_url = None
        try:
            task_url = q.get(timeout=1,block=True)
        except queue.Empty:
            print_with_lock(f"[{thread_name}退出,任务队列已耗尽]")
            break
        try:
            res = requests.get(task_url,timeout=3)
            print_with_lock(f"[{thread_name}请求完成:url==>[{task_url}]]")
        except requests.exceptions.RequestException as e:
            print_with_lock(f"[{thread_name}错误],请求{task_url}失败:{e}")
        finally:
            if task_url:
                q.task_done()

def print_with_lock(msg:str):
    with print_lock:
        print(msg)
        sys.stdout.flush()


def main():
    print_with_lock(f"-----启动多线程域名请求任务-----")
    threads: List[threading.Thread] = []
    for i in range(ThreadCount):
        t = threading.Thread(target=thread_request,name=f"WOrker-{i+1}",daemon=True)
        threads.append(t)
        t.start()
    for url in urls:
        q.put(url)
    print_with_lock("已将所有url放入队列")
    try:
        q.join()
    except KeyboardInterrupt:
        print_with_lock("\n用户终端,正在尝试优雅退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()