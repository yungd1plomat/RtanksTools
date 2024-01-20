from proxyclient import ProxyClient
import socks

destination_ip = "135.125.188.169"
destination_port = 6969

def get_battle_max(user_info, battles_data):
    current_rank = user_info["rank"]
    max_count = -1
    battle = None
    for battle in battles_data["battles"]:
        if current_rank < battle["minRank"] or current_rank > battle["maxRank"]:
            continue
        count = battle["redPeople"] + battle["bluePeople"] + battle["countPeople"]
        if count > max_count and battle["maxPeople"] < count:
            count = max_count
            battle = battle
    return battle

if __name__ == '__main__':
    client = ProxyClient(destination_ip, destination_port)
    client.handshake()
    client.auth("tremor", "tremor123")
    user_info = client.get_user_info("tremor")
    battles_data = client.get_battles()
    print(get_battle_max(user_info, battles_data))
    input("Press enter to quit..")
    client.disconnect()
