from proxyclient import ProxyClient
import coloredlogs, logging
from queue import Queue
import utils
from threading import Thread, Lock

coloredlogs.install(level='DEBUG', fmt='%(asctime)s [%(levelname)s] %(message)s')

proxies = Queue()
output_file = "good_proxies.txt"
file_lock = Lock()

def save_good_proxy(proxy):
    with file_lock:
        with open(output_file, "a") as f:
            f.write(proxy + "\n")

def loop():
    global proxies
    while True:
        try:
            proxy = proxies.get()
        except:
            break
        client = ProxyClient("135.125.188.169", 6969, proxy)
        try:
            client.handshake()
            save_good_proxy(proxy)
            logging.info(f"[+] good {proxy}, remain {proxies.qsize()}")
        except:
            logging.error(f"[-] error {proxy}, remain {proxies.qsize()}")
        finally:
            client.disconnect()

def main():
    global proxies
    proxs = utils.read_file("proxy.txt")
    for proxy in proxs:
        proxies.put(proxy)
    threads_count = 40
    for _ in range(threads_count):
        th = Thread(target=loop)
        th.start()

if __name__ == "__main__":
    main()