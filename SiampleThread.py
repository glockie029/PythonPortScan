import threading
import queue
import requests

q = queue.Queue()


def thread_request():
    thread_name = threading.current_thread().name
    while True:
        url = q.get(block=True,timeout=1)
        res = requests.get(url)
def main():
