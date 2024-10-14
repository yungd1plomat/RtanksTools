from proxyclient import ProxyClient
from queue import Queue
import utils
import coloredlogs, logging
from threading import Thread
from time import sleep

coloredlogs.install(level='DEBUG', fmt='%(asctime)s [%(levelname)s] %(message)s')

proxies = Queue()
accounts = Queue()
clients = Queue()

def connect_loop():
    global proxies
    global accounts
    global clients
    while not accounts.empty() and not proxies.empty():
        try:
            account = accounts.get()
            login, password = account.split(':')
            proxy, count = proxies.get()
            if count == 2:
                accounts.put(account)
                continue
            client = ProxyClient("135.125.188.169", 6969, proxy)
            client.handshake()
            client.load_resources()
            sleep(3)
            current_user = client.auth(login, password)
            if current_user:
                clients.put(client)
                proxies.put((proxy, count + 1))
                logging.debug(f'Logged in as {current_user["name"]}')
        except Exception as ex:
            logging.error(ex)

def main():
    global proxies
    global accounts
    global clients
    users = utils.read_file("users.txt")
    file_proxies = utils.read_file("proxy.txt")
    for proxy in file_proxies:
        proxies.put((proxy, 0))
    accs = utils.read_file("accounts.txt")
    for acc in accs:
        accounts.put(acc)
    thread_count = 100
    threads = []
    for _ in range(thread_count):
        th = Thread(target=connect_loop)
        threads.append(th)
        th.start()
    for th in threads:
        th.join()
    print("Connected", clients.qsize(), "clients")
    for client in list(clients.queue):
        client: ProxyClient
        client.set_timeout(180)
    input()
    for user in users:
        for client in list(clients.queue):
            client: ProxyClient
            try:
                client.send_data("lobby;make_friend;" + user)
            except:
                pass
        logging.info("Sent")
        input()
    '''
    while True:
        data = input("Enter data: ")
        for client in list(clients.queue):
            client: ProxyClient
            client.send_data(data)
    '''
        

if __name__ == "__main__":
    main()

