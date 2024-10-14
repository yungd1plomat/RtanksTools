from proxyclient import ProxyClient
import coloredlogs, logging
from queue import Queue
from twocaptcha import TwoCaptcha
import utils
from nickname_generator import generate
from threading import Thread
from time import sleep
import random

coloredlogs.install(level='DEBUG', fmt='%(asctime)s [%(levelname)s] %(message)s')

proxies = Queue()
packet = ''
accounts = Queue()

def loop():
    global packet
    while True:
        account = accounts.get()
        try:
            login, password = account.split(':')
            proxy = proxies.get()
            client = ProxyClient("135.125.188.169", 6969, proxy)
            client.handshake()
            client.load_resources()
            sleep(3)
            current_user = client.auth(login, password)
            if not current_user:
                continue
            client.send_data("lobby;user_inited")
            sleep(8)
            client.send_data(packet)
            '''rang = current_user["rang"]
            for _ in range(5):
                client.send_data('lobby;create_battle;{"maxRang":' + str(rang) + ',"battleMode":"DM","equipmentConstraintsMode":null,"mapId":"map_sandbox","friendlyFire":false,"withoutSupplies":false,"withoutBonuses":false,"clanBattle":false,"numPlayers":8,"proBattle":false,"time":1800,"privateBattle":false,"reArmorEnabled":true,"parkourMode":false,"goldBoxesEnabled":true,"autoBalance":true,"scoreLimit":0,"minRang":' + str(rang) + '}')
            '''
            proxies.put(proxy)
            logging.debug(f'Sent from {current_user["name"]}')
        except Exception as ex:
            logging.error(ex)
        finally:
            accounts.put(account)
            client.disconnect()

def main():
    global packet
    with open('packet.txt', 'r', encoding='utf-8') as f:
        packet = f.read()
    proxs = utils.read_file("proxy1234.txt")
    random.shuffle(proxs)
    for proxy in proxs:
        proxies.put(proxy)
    accs = utils.read_file("all_accs.txt")
    random.shuffle(accs)
    for acc in accs:
        accounts.put(acc)
    threads_count = 1
    for _ in range(threads_count):
        th = Thread(target=loop)
        th.start()

if __name__ == "__main__":
    main()