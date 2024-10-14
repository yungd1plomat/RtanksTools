from proxyclient import ProxyClient
import coloredlogs, logging
from queue import Queue
import base64
from twocaptcha import TwoCaptcha
import utils
from nickname_generator import generate
from threading import Thread
from time import sleep
import random

API_KEY = "8b05577f4418224a86a76ff3bd2b6474"

# c102b4fcaed58016e9fc39489ae89415 - 3$
# 8ad541582c76eca15bf84750aaf3ff7c - 2.9$


# Old keys
# 92449afaa253261e8a8743154f82f288 - 4$
# ab64599f9baded9ee06e9ba8d21c5e71 - 26$
# 725b33267e77fe2aa1ec45d2f6be8210 - 1.5$
# 8b05577f4418224a86a76ff3bd2b6474 - 2.8$
# 8e4d3a745d75dc4a4461b1f7d891c636 - 0.08$
# ffa52f3278dcca0d7505d0de8f1028cd - 10$


solver = TwoCaptcha(API_KEY)
proxies = Queue()
accounts = Queue()
stop = False
users = utils.read_file("online.txt")

coloredlogs.install(level='DEBUG', fmt='%(asctime)s [%(levelname)s] %(message)s')

def solve_captcha(captcha_packet: str):
    captcha_bytes = bytes(map(int, captcha_packet.split(';')[-1].split(',')))
    b64_image = base64.b64encode(captcha_bytes).decode()
    result = solver.normal(b64_image, case=True, minLen=4)
    print("Captcha solved with result:", result)
    return result

def loop_register():
    global proxies
    global accounts
    global stop
    while not stop:
        try:
            proxy = proxies.get()
        except:
            continue
        client = ProxyClient("135.125.188.169", 6969, proxy)
        try:
            client.handshake()
            client.receive_data("system;load_resources;")
            client.send_data("system;resources_loaded;1")
            client.receive_data("system;init_auth")
            client.send_data("registration;state")
            captcha = client.receive_data("auth;enable_captcha;REGISTER;")
            result = solve_captcha(captcha)
            nickname_not_exist = False
            nickname = ''
            while not nickname_not_exist:
                nickname = generate()
                nickname_not_exist = client.check_register_nickname(nickname)
            max_retries = 3
            retries = 0
            registered = False
            while retries < max_retries and not registered:
                retries += 1
                answer = result["code"]
                captcha_id = result["captchaId"]
                client.send_data(f"registration;{nickname};{nickname}123;{answer}")
                response = client.receive_data()
                if response.startswith("auth;wrong_captcha"):
                    solver.report(captcha_id, False)
                    logging.warning("Invalid captcha, retrying..")
                    captcha = client.receive_data("auth;update_captcha;REGISTER;")
                    result = solve_captcha(captcha)
                elif response.startswith("registration;info_done"):
                    logging.info(f"Registered {nickname}")
                    accounts.put(f"{nickname}:{nickname}123")
                    solver.report(captcha_id, True)
                    client.load_resources()
                    client.load_resources()
                    client.send_data('battle;get_init_data_local_tank')
                    sleep(3)
                    '''
                    client.send_data("battle;i_exit_from_battle")
                    client.send_data("lobby;user_inited")
                    sleep(3)
                    local = users.copy()
                    random.shuffle(local)
                    for user in local:
                        client.send_data(f"lobby;make_friend;{user}")
                        client.receive_data("lobby;add_to_outcoming;")
                        logging.debug(f"Added {user}")'''
                    client.send_data('battle;get_init_data_local_tank');
                    
                    registered = True
        except Exception as ex:
            logging.error(ex)
        client.disconnect()
        proxies.put(proxy)

def write_file_loop():
    global accounts
    global stop
    while not stop:
        try:
            account = accounts.get()
            with open("rtanksnovobranec.txt", '+a') as file:
                file.write(f"{account}\n")
        except:
            pass

def main():
    global proxies
    global stop
    proxs = utils.read_file("proxy.txt")
    random.shuffle(proxs)
    for proxy in proxs:
        proxies.put(proxy)
    threads_count = 40
    for _ in range(threads_count):
        th = Thread(target=loop_register)
        th.start()
    th = Thread(target=write_file_loop)
    th.start()
    input()
    stop = True

if __name__ == "__main__":
    main()